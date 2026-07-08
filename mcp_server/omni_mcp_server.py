#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-genai",
#   "mcp",
#   "httpx",
# ]
# ///
import os
import sys
import json
import time
import base64
import logging
from typing import Optional
import httpx
from google import genai
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("gemini-omni-mcp")

# Initialize FastMCP Server
mcp = FastMCP("Gemini Omni Video Server")

# Constants
OMNI_MODEL = "gemini-omni-flash-preview"
HOME_DIR = os.path.expanduser("~")
SESSION_FILE = os.path.join(HOME_DIR, ".gemini_omni_mcp_session.json")
OUTPUT_DIR = os.path.join(HOME_DIR, "gemini_omni_outputs")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

class SessionState:
    def __init__(self):
        self.last_interaction_id = None
        self.last_video_path = None
        self.turn_count = 0
        self.load()

    def load(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.last_interaction_id = data.get("last_interaction_id")
                    self.last_video_path = data.get("last_video_path")
                    self.turn_count = data.get("turn_count", 0)
            except Exception as e:
                logger.warning("Failed to load session state: %s", e)

    def save(self):
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "last_interaction_id": self.last_interaction_id,
                    "last_video_path": self.last_video_path,
                    "turn_count": self.turn_count
                }, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save session state: %s", e)

    def clear(self):
        self.last_interaction_id = None
        self.last_video_path = None
        self.turn_count = 0
        if os.path.exists(SESSION_FILE):
            try:
                os.remove(SESSION_FILE)
            except Exception:
                pass

# Global session state
state = SessionState()

def _get_client() -> genai.Client:
    """Get the GenAI client initialized with GEMINI_API_KEY from environment."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is missing. "
            "Please configure the GEMINI_API_KEY variable in your environment."
        )
    return genai.Client(api_key=api_key)

def _decode_and_save_video(data, filepath):
    """Safely handles base64-encoded or raw binary video payload and saves to disk."""
    if isinstance(data, str):
        video_bytes = base64.b64decode(data)
    elif isinstance(data, bytes):
        # Base64-encoded MP4 files often start with 'AAAA' (null offset + ftyp).
        # Check if we should base64-decode the raw bytes.
        if data.startswith(b'AAAA') or b'ftyp' not in data[:20]:
            try:
                video_bytes = base64.b64decode(data)
            except Exception:
                video_bytes = data
        else:
            video_bytes = data
    else:
        raise ValueError("Invalid video data format")
        
    with open(filepath, "wb") as f:
        f.write(video_bytes)

def _poll_and_download_video(client, interaction, filepath) -> bool:
    """Polls the File API until the generated video is ACTIVE, then downloads and saves it."""
    video_output = getattr(interaction, "output_video", None)
    if not video_output:
        # Check raw steps content for direct REST response structures
        if hasattr(interaction, "content") and interaction.content:
            for part in interaction.content.parts or []:
                if hasattr(part, "inline_data") and part.inline_data:
                    if "video" in (part.inline_data.mime_type or ""):
                        _decode_and_save_video(part.inline_data.data, filepath)
                        return True
        return False

    uri = getattr(video_output, "uri", None)
    if not uri:
        # If uri is missing, try reading inline data directly
        data = getattr(video_output, "data", None)
        if data:
            _decode_and_save_video(data, filepath)
            return True
        return False

    # Extract file name/ID from the URI (e.g. files/abc-123)
    file_id = uri.split("/")[-1]
    if ":" in file_id:
        file_id = file_id.split(":")[0]
    if "?" in file_id:
        file_id = file_id.split("?")[0]
        
    file_name = f"files/{file_id}"
    logger.info("Polling status of generated video file: %s", file_name)

    # Polling loop
    start_time = time.time()
    timeout = 300 # 5 minutes max timeout
    while time.time() - start_time < timeout:
        try:
            f_info = client.files.get(name=file_name)
            status = f_info.state.name
            logger.info("Current video status: %s", status)
            
            if status == "ACTIVE":
                break
            elif status == "FAILED":
                raise RuntimeError("Video processing failed inside Gemini File API.")
        except Exception as e:
            logger.warning("Error fetching file status: %s. Retrying...", e)
            
        time.sleep(5)
    else:
        raise TimeoutError("Timed out waiting for video generation to become ACTIVE.")

    # Download bytes
    logger.info("Downloading finished video from: %s", uri)
    try:
        # Try SDK download first
        video_bytes = client.files.download(file=file_name)
        _decode_and_save_video(video_bytes, filepath)
        return True
    except Exception as sdk_err:
        logger.warning("SDK download failed (%s). Retrying via HTTP fallback...", sdk_err)
        
        # Fallback to HTTP download using api key headers
        api_key = os.environ.get("GEMINI_API_KEY")
        headers = {"x-goog-api-key": api_key} if api_key else {}
        resp = httpx.get(uri, headers=headers, follow_redirects=True, timeout=60.0)
        if resp.status_code == 200:
            _decode_and_save_video(resp.content, filepath)
            return True
            
    return False

@mcp.tool()
def generate_video(prompt: str, aspect_ratio: str = "16:9", image_path: Optional[str] = None) -> str:
    """
    Generate a new video from a structured 6-dimension prompt using Gemini Omni Flash.

    Args:
        prompt: Fully detailed 6-dimension prompt describing the shot framing, style, lighting, location, action, and text rendering.
        aspect_ratio: Frame aspect ratio. Use "16:9" for landscape or "9:16" for portrait.
        image_path: Optional absolute local path to an image to animate (Image-to-Video).
    """
    try:
        client = _get_client()
    except Exception as e:
        return f"[ERROR] {e}"

    logger.info("Running generate_video - prompt: %s (aspect_ratio=%s, image_path=%s)", prompt, aspect_ratio, image_path)

    # 1. Prepare input payload (supporting Image-to-Video/Subject Reference)
    input_payload = prompt
    task_name = "text_to_video"

    if image_path:
        if not os.path.exists(image_path):
            return f"[ERROR] Image reference path does not exist: {image_path}"
        try:
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            ext = os.path.splitext(image_path)[1].lower()
            mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
            b64_str = base64.b64encode(img_bytes).decode("utf-8")
            
            input_payload = [
                {"type": "image", "data": b64_str, "mime_type": mime},
                {"type": "text", "text": prompt}
            ]
            task_name = "image_to_video"
            logger.info("Loaded reference image for image_to_video task: %s", image_path)
        except Exception as e:
            return f"[ERROR] Failed to load reference image: {e}"

    # 2. Call Interactions API
    try:
        interaction = client.interactions.create(
            model=OMNI_MODEL,
            input=input_payload,
            background=False,
            store=True,
            stream=False,
            generation_config={
                "video_config": {
                    "task": task_name
                }
            },
            response_format={
                "type": "video",
                "aspect_ratio": aspect_ratio,
                "delivery": "uri"
            }
        )

        interaction_id = interaction.id
        output_filename = f"video_{interaction_id[:12]}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # 3. Poll and download generated file
        success = _poll_and_download_video(client, interaction, output_path)
        if not success:
            return f"[ERROR] Failed to extract or download video bytes from interaction: {interaction_id}"

        # 4. Save state
        state.last_interaction_id = interaction_id
        state.last_video_path = output_path
        state.turn_count = 1
        state.save()

        result_msg = (
            f"Success! Video generated successfully.\n"
            f"- Saved File Path: {output_path}\n"
            f"- Interaction ID: {interaction_id}\n"
            f"- Aspect Ratio: {aspect_ratio}\n"
            f"- Video Task: {task_name}\n"
            f"- Output Text: {interaction.output_text or 'N/A'}"
        )
        return result_msg

    except Exception as e:
        logger.error("generate_video failed", exc_info=True)
        return f"[ERROR] Video generation failed: {e}"

@mcp.tool()
def edit_video(edit_prompt: str) -> str:
    """
    Edit the last generated video using a targeted conversational instruction.

    Args:
        edit_prompt: Targeted instruction. The tool will automatically prefix it with preservation guardrails.
    """
    try:
        client = _get_client()
    except Exception as e:
        return f"[ERROR] {e}"

    previous_id = state.last_interaction_id
    if not previous_id:
        return "[ERROR] No active video session found. You must call generate_video first."

    # Enforce preservation guardrail
    if not edit_prompt.strip().lower().startswith("edit this keeping"):
        full_prompt = f"Edit this keeping everything else identical. {edit_prompt}"
    else:
        full_prompt = edit_prompt

    logger.info("Running edit_video - turn %d - previous_id: %s - prompt: %s", state.turn_count + 1, previous_id, full_prompt)

    try:
        interaction = client.interactions.create(
            model=OMNI_MODEL,
            input=full_prompt,
            previous_interaction_id=previous_id,
            background=False,
            store=True,
            stream=False,
            generation_config={
                "video_config": {
                    "task": "edit"
                }
            },
            response_format={
                "type": "video",
                "aspect_ratio": "16:9", # inherits/standardizes
                "delivery": "uri"
            }
        )

        new_id = interaction.id
        output_filename = f"video_{new_id[:12]}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Poll and download
        success = _poll_and_download_video(client, interaction, output_path)
        if not success:
            return f"[ERROR] Failed to download video bytes for edit turn: {new_id}"

        # Update state
        state.last_interaction_id = new_id
        state.last_video_path = output_path
        state.turn_count += 1
        state.save()

        warning_msg = ""
        if state.turn_count >= 4:
            warning_msg = (
                "\n\n[WARNING] Turn count is at or above 4. Visual quality, consistency, and "
                "character detail may start to drift. It is recommended to start a fresh "
                "session (generate_video) if structural drifts occur."
            )

        result_msg = (
            f"Success! Video edited successfully.\n"
            f"- Saved File Path: {output_path}\n"
            f"- Interaction ID: {new_id}\n"
            f"- Previous ID: {previous_id}\n"
            f"- Edit Turn Count: {state.turn_count}\n"
            f"- Output Text: {interaction.output_text or 'N/A'}"
            f"{warning_msg}"
        )
        return result_msg

    except Exception as e:
        logger.error("edit_video failed", exc_info=True)
        return f"[ERROR] Video editing failed: {e}"

@mcp.tool()
def get_last_video() -> str:
    """
    Get the details and local file path of the last generated video.
    """
    if not state.last_interaction_id:
        return "No active video session. No video has been generated yet."
        
    return (
        f"Last Video Details:\n"
        f"- Local Path: {state.last_video_path}\n"
        f"- Interaction ID: {state.last_interaction_id}\n"
        f"- Session Turn Count: {state.turn_count}"
    )

@mcp.tool()
def clear_session() -> str:
    """
    Clear the current video session state (discards the last interaction ID chaining).
    """
    state.clear()
    return "Session cleared successfully. Subsequent edits will require starting a new generation."

@mcp.prompt()
def create_omni_prompt(
    action: str,
    style: str,
    location: str,
    lighting: str,
    motion: str,
    text_overlay: Optional[str] = None
) -> str:
    """
    Builds a fully optimized 6-dimension prompt for Gemini Omni video creation.

    Args:
        action: The main action or subject behavior.
        style: Visual style (e.g. realistic film, claymation, bold outline anime).
        location: Environmental setting or background details.
        lighting: Light properties (e.g. golden hour volumetric rays, dimmed neon lights).
        motion: Camera motion and viewpoints (e.g. dolly zoom, handheld tracking shot).
        text_overlay: Optional exact text to render (e.g. street sign that says "Hello").
    """
    text_part = ""
    if text_overlay:
        text_part = f" Text rendering: {text_overlay}."
    
    return (
        f"Generate a video showing: {action}. "
        f"Visual style: {style}. "
        f"Camera and framing: {motion}. "
        f"Location/Environment: {location}. "
        f"Lighting/Volumetrics: {lighting}. "
        f"No cuts or scene transitions unless specified.{text_part}"
    )

@mcp.prompt()
def edit_omni_prompt(
    edit_instruction: str
) -> str:
    """
    Applies the turn-based preservation guardrails to edit an existing video.

    Args:
        edit_instruction: Exact modification instructions (e.g. 'Make the jacket red').
    """
    return f"Edit this keeping everything else identical. {edit_instruction}"

@mcp.prompt()
def rapid_fire_prompt(
    style: str,
    locations: str
) -> str:
    """
    Builds a prompt for a rapid-fire sequence of scenes/locations.

    Args:
        style: Cinematic style of the sequence (e.g. grainy analog film, risograph print).
        locations: Comma-separated list of locations (e.g. Paris, Tokyo, London).
    """
    return (
        f"In a rapid fire sequence, every half a second (12 frames at 24fps) change the scene to a new location. "
        f"Visual style: {style}. "
        f"List of locations: {locations}. "
        f"No dialogue. Keep transitions organic."
    )

@mcp.prompt()
def timecode_prompt(
    scene_0_3s: str,
    scene_3_6s: str,
    scene_6_10s: str
) -> str:
    """
    Builds a timecode-based prompt sequence to stage actions at exact times.

    Args:
        scene_0_3s: Description of action from 0 to 3 seconds.
        scene_3_6s: Description of action from 3 to 6 seconds.
        scene_6_10s: Description of action from 6 to 10 seconds.
    """
    return (
        f"[0-3s] {scene_0_3s}\n"
        f"[3-6s] {scene_3_6s}\n"
        f"[6-10s] {scene_6_10s}"
    )

if __name__ == "__main__":
    # Start standard stdio MCP Server transport
    mcp.run()
