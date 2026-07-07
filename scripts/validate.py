#!/usr/bin/env python3
import os
import sys
import re

def print_err(msg):
    print(f"\033[91m[ERROR] {msg}\033[0m", file=sys.stderr)

def print_ok(msg):
    print(f"\033[92m[OK] {msg}\033[0m")

def parse_frontmatter(filepath):
    """
    Parses simple YAML frontmatter between the first two '---' lines.
    Returns a dict of parsed fields, and the remaining content.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match frontmatter using regex
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if not match:
        return None, content

    yaml_text = match.group(1)
    body = match.group(2)
    
    metadata = {}
    lines = yaml_text.split('\n')
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        if ':' not in line:
            continue
        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()
        
        # Handle list syntax like tags: [a, b]
        if val.startswith('[') and val.endswith(']'):
            val = [item.strip() for item in val[1:-1].split(',') if item.strip()]
        # Handle simple quotes
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
            
        metadata[key] = val
        
    return metadata, body

def check_code_blocks(filepath, content):
    """
    Verifies that all triple-backtick code blocks are properly paired.
    """
    lines = content.split('\n')
    open_block = False
    open_line = 0
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            if open_block:
                open_block = False
            else:
                open_block = True
                open_line = i
                
    if open_block:
        print_err(f"{os.path.basename(filepath)}: Unclosed code block starting at line {open_line}")
        return False
    return True

def check_reference_links(skill_dir, filepath, content):
    """
    Verifies that all local references mentioned in the text exist.
    Looks for paths like references/filename.md in code blocks, links, or text.
    """
    # Find all references matching references/*.md
    refs = re.findall(r'references/[\w\-]+\.md', content)
    
    # Also find standard markdown links to references directory
    md_links = re.findall(r'\]\((references/[\w\-]+\.md)\)', content)
    all_refs = set(refs + md_links)
    
    success = True
    for ref in all_refs:
        ref_path = os.path.join(skill_dir, ref)
        if not os.path.isfile(ref_path):
            print_err(f"{os.path.basename(filepath)}: Reference link '{ref}' points to non-existent file: {ref_path}")
            success = False
    return success

def validate_skill(skill_dir):
    """
    Validates a single skill folder.
    """
    skill_name = os.path.basename(skill_dir)
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    
    if not os.path.isfile(skill_md):
        print_err(f"Skill directory '{skill_name}' is missing required 'SKILL.md' file.")
        return False
        
    metadata, body = parse_frontmatter(skill_md)
    if metadata is None:
        print_err(f"'{skill_name}/SKILL.md' has invalid or missing YAML frontmatter.")
        return False
        
    # Validate required metadata fields
    required_fields = ['name', 'description', 'version', 'author', 'category', 'tags']
    missing_fields = [f for f in required_fields if f not in metadata]
    if missing_fields:
        print_err(f"'{skill_name}/SKILL.md' frontmatter is missing required fields: {', '.join(missing_fields)}")
        return False
        
    if metadata['name'] != skill_name:
        print_err(f"'{skill_name}/SKILL.md' name '{metadata['name']}' does not match directory name '{skill_name}'.")
        return False

    success = True
    
    # Check code blocks in SKILL.md
    if not check_code_blocks(skill_md, body):
        success = False
        
    # Check reference links in SKILL.md
    if not check_reference_links(skill_dir, skill_md, body):
        success = False
        
    # Check any files in references/ subfolder
    references_dir = os.path.join(skill_dir, 'references')
    if os.path.isdir(references_dir):
        for root, _, files in os.walk(references_dir):
            for file in files:
                if file.endswith('.md'):
                    ref_file_path = os.path.join(root, file)
                    with open(ref_file_path, 'r', encoding='utf-8') as f:
                        ref_content = f.read()
                    if not check_code_blocks(ref_file_path, ref_content):
                        success = False
                        
    return success

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(base_dir, 'skills')
    
    if not os.path.isdir(skills_dir):
        print_err(f"Skills directory not found at: {skills_dir}")
        sys.exit(1)
        
    skills = [os.path.join(skills_dir, d) for d in os.listdir(skills_dir) 
              if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith('.')]
              
    if not skills:
        print_err("No skills found in skills/ directory.")
        sys.exit(1)
        
    print(f"Found {len(skills)} skill(s) to validate.")
    all_ok = True
    
    for skill in sorted(skills):
        skill_name = os.path.basename(skill)
        print(f"Validating skill '{skill_name}'...")
        if validate_skill(skill):
            print_ok(f"Skill '{skill_name}' is valid.")
        else:
            all_ok = False
            
    if not all_ok:
        print_err("Validation failed for one or more skills.")
        sys.exit(1)
        
    print_ok("All skills validated successfully!")
    sys.exit(0)

if __name__ == '__main__':
    main()
