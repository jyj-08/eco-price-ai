import sys

file_path = r'backend/api_crawler.py'

with open(file_path, 'rb') as f:
    raw = f.read()

# Detect encoding
try:
    content = raw.decode('utf-8')
    enc = 'utf-8'
except UnicodeDecodeError:
    content = raw.decode('cp949')
    enc = 'cp949'

# Rewrite the blacklist line with the correct Korean keywords
old_start_marker = 'def parse_market_price_records('
func_idx = content.find(old_start_marker)
if func_idx == -1:
    print("ERROR: function not found")
    sys.exit(1)

# Find the blacklist line (first line after func def that has 'blacklist')
# We'll replace the entire block from the def line down to the 'for raw in raw_items' loop
block_start = content.find('\n', func_idx) + 1  # start after func def line
# Find first occurrence of 'for raw in raw_items'
for_idx = content.find('    for raw in raw_items:', func_idx)

old_block = content[func_idx:for_idx]

new_block = '''def parse_market_price_records(raw_items):
    parsed_records = []

    # 비식품(공산품) 키워드 블랙리스트
    blacklist = [
        '\uc138\uc81c', '\uc0f4\ud478', '\ub9b0\uc2a4', '\uce58\uc57d', '\uce6b\uc194',
        '\uba74\ub3c4\uae30', '\uac74\uc804\uc9c0', '\uace0\ubb34\uc7a5\uac11', '\ud654\uc7a5\uc9c0', '\ubb3c\ud2f0\uc288',
        '\ubd80\ud0c4\uac00\uc2a4', '\uc2b5\uae30\uc81c\uac70\uc81c', '\uc0b4\ucda9\uc81c', '\ub77d\uc2a4', '\ube44\ub204',
        '\uc2a4\ud0c0\ud0b9', '\uae30\uc800\uadc0'
    ]

    '''

content = content[:func_idx] + new_block + content[for_idx:]

with open(file_path, 'wb') as f:
    f.write(content.encode(enc))

print(f"Done. Encoding={enc}")
