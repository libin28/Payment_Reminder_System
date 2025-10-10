#!/usr/bin/env python3
"""
Fix the navigation section in app.py by removing problematic lines
"""

def fix_app_navigation():
    """Fix the navigation section in app.py"""
    
    # Read the current file
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the problematic section and fix it
    fixed_lines = []
    skip_lines = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Skip the problematic orphaned lines (361-368)
        if line_num >= 361 and line_num <= 368:
            continue
            
        # Also fix the user navigation section if it has similar issues
        if 'index=0 if st.session_state.page not in' in line:
            # Replace with simple selectbox
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(' ' * indent + '])\n')
            skip_lines = True
            continue
            
        if skip_lines and '].index(st.session_state.page))' in line:
            skip_lines = False
            continue
            
        if skip_lines:
            continue
            
        fixed_lines.append(line)
    
    # Write the fixed file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Fixed navigation section in app.py")
    print(f"📊 Removed problematic lines, total lines now: {len(fixed_lines)}")

if __name__ == "__main__":
    fix_app_navigation()
