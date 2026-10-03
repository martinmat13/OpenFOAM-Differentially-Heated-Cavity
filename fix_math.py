import os
import re

def fix_github_math(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace block math \[ ... \] with $$ ... $$
    content = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', content, flags=re.DOTALL)
    
    # Replace inline math \( ... \) with $...$
    def inline_repl(match):
        inner = match.group(1).strip()
        return f"${inner}$"
    
    content = re.sub(r'\\\((.*?)\\\)', inline_repl, content)

    with open(filepath, 'w') as f:
        f.write(content)

for root, dirs, files in os.walk('.'):
    if '.git' in root:
        continue
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            fix_github_math(filepath)
            print(f"Fixed {filepath}")
