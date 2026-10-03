import os
import re

def fix_markdown_math(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace block math $$ ... $$ with \[ ... \]
    content = re.sub(r'\$\$(.*?)\$\$', r'\\[\1\\]', content, flags=re.DOTALL)
    
    # Replace inline math $ ... $ with \( ... \)
    # We use a negative lookbehind and lookahead to avoid replacing $$
    content = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', r'\\(\1\\)', content)

    # Fix HTML tag issue with <
    content = content.replace('< 10^3', '&lt; 10^3').replace('> 10^8', '&gt; 10^8').replace('> 10^4', '&gt; 10^4').replace('> 10^7', '&gt; 10^7')

    with open(filepath, 'w') as f:
        f.write(content)

for root, dirs, files in os.walk('.'):
    if '.git' in root:
        continue
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            fix_markdown_math(filepath)
            print(f"Fixed {filepath}")
