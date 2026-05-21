import sys

file_path = r'api_crawler.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix indentation: '        for raw in raw_items:' -> '    for raw in raw_items:'
content = content.replace('\n        for raw in raw_items:\n        #', '\n    for raw in raw_items:\n        #', 1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Indent fixed")
