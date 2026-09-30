from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).with_name("mojevychytavky-logo.png")
size = 1080
image = Image.new("RGB", (size, size), "#12392e")
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=240, fill="#12392e")
draw.ellipse((120, 120, 960, 960), outline="#8fe9c6", width=24)
font_path = "C:/Windows/Fonts/arialbd.ttf"
font = ImageFont.truetype(font_path, 500)
text = "M"
box = draw.textbbox((0, 0), text, font=font)
x = (size - (box[2] - box[0])) // 2
y = 265
# Simple white wordmark initial.
draw.text((x, y), text, font=font, fill="#f8fffa")
# Yellow spark.
cx, cy = 815, 260
points = [(cx, cy - 78), (cx + 20, cy - 20), (cx + 78, cy), (cx + 20, cy + 20), (cx, cy + 78), (cx - 20, cy + 20), (cx - 78, cy), (cx - 20, cy - 20)]
draw.polygon(points, fill="#ffdb66")
draw.line((250, 822, 830, 822), fill="#8fe9c6", width=24)
image.save(OUT, "PNG", optimize=True)
print(OUT, image.size)
