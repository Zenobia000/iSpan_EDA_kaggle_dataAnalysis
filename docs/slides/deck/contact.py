"""把 shots/<前綴>*.png 拼成一張縮圖總覽：uv run python contact.py <前綴> <輸出檔>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
prefix, out = sys.argv[1], sys.argv[2]
files = sorted(Path(__file__).parent.glob(f"shots/{prefix}*.png"))
W, H, cols = 960, 540, 3
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * W, rows * (H + 30)), "white")
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((W, H))
    x, y = (i % cols) * W, (i // cols) * (H + 30)
    sheet.paste(im, (x, y + 30))
    ImageDraw.Draw(sheet).text((x + 8, y + 8), f.stem, fill="black")
sheet.save(out)
print(out, len(files))
