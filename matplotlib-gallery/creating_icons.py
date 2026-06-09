import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np

# # 1. Ensure the output directory exists
# os.makedirs('icons', exist_ok=True)

# # 2. Fix dimensions: 5.3333 inches * 96 DPI = exactly 512 pixels
# fig, ax = plt.subplots(figsize=(5.3333, 5.3333), dpi=96)
# ax.set_xlim(0, 10)
# ax.set_ylim(0, 10)

# # 3. Remove default padding so the artwork fills out the icon boundaries
# fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
# ax.axis('off')

# # Draw a simple plot
# x = np.linspace(0, 10, 100)
# y = 5 + 2 * np.sin(x)
# ax.plot(x, y, color='#6366f1', linewidth=3)
# ax.fill_between(x, y, 5, alpha=0.3, color='#6366f1')

# # Add a bar chart
# ax.bar([1, 3, 5, 7, 9], [2, 4, 3, 5, 2], color='#ec4899', alpha=0.7, width=1)

# # 4. Save the base 512x512 icon accurately
# plt.savefig('icons/icon-512.png', transparent=True, dpi=96)
# plt.close()

# # 5. Scale down to other sizes using PIL
# img = Image.open('icons/icon-512.png')
# for size in [72, 96, 128, 144, 152, 192, 384]:
#     resized = img.resize((size, size), Image.Resampling.LANCZOS)
#     resized.save(f'icons/icon-{size}.png')

# from PIL import Image

# # Open current 511×511 icon
# img = Image.open('matplotlib-gallery\icons\icon-512.png')

# # Resize to exactly 512×512
# img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
# img_resized.save('matplotlib-gallery\icons\icon-512.png')
    
# print("Icon resized to 512x512")


# from PIL import Image, ImageDraw, ImageFont

# # Create desktop screenshot (1280x720)
# img_wide = Image.new('RGB', (1280, 720), color='#0f1117')
# draw = ImageDraw.Draw(img_wide)
# draw.text((640, 360), "MatplotGallery", fill='white', anchor='mm')
# img_wide.save('matplotlib-gallery\icons\screenshot-wide.png')

# # Create mobile screenshot (540x720)
# img_portrait = Image.new('RGB', (540, 720), color='#0f1117')
# draw = ImageDraw.Draw(img_portrait)
# draw.text((270, 360), "MatplotGallery", fill='white', anchor='mm')
# img_portrait.save('matplotlib-gallery\icons\screenshot-portrait.png')

# print("Screenshots created")
from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('icons', exist_ok=True)

# Create master 512x512 icon
base_size = 512
img = Image.new('RGB', (base_size, base_size), color='#0f1117')
draw = ImageDraw.Draw(img)

# Draw gradient circles (purple/indigo theme)
for i in range(base_size, 0, -20):
    # Math scaled to 156 max to ensure val + 99 never exceeds 255
    val = int(99 + (156 * (base_size - i) / base_size))
    color = f'#{val:02x}{102:02x}{241:02x}'
    draw.ellipse([(base_size//2 - i//2, base_size//2 - i//2), 
                 (base_size//2 + i//2, base_size//2 + i//2)], outline=color, width=2)

# Add "M" text for Matplotlib
try:
    font = ImageFont.truetype("arial.ttf", 300)
except IOError:
    font = ImageFont.load_default()

draw.text((base_size//2, base_size//2), "M", fill='white', font=font, anchor='mm')
img.save('icons/icon-512.png')
print('✓ icon-512.png (512x512)')

# Create all required sizes
for size in [72, 96, 128, 144, 152, 192, 384]:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(f'icons/icon-{size}.png')
    print(f'✓ icon-{size}.png ({size}x{size})')

# Desktop screenshot (1280x720)
ss_wide = Image.new('RGB', (1280, 720), color='#0f1117')
draw_w = ImageDraw.Draw(ss_wide)

try:
    font_lg = ImageFont.truetype("arial.ttf", 80)
except IOError:
    font_lg = ImageFont.load_default()

colors = ['#6366f1', '#ec4899', '#f59e0b', '#10b981']

for i, c in enumerate(colors):
    x = 150 + i * 250
    draw_w.rectangle([(x, 250), (x + 200, 550)], fill=c)

draw_w.text((640, 100), "MatplotGallery", fill='white', font=font_lg, anchor='mm')
ss_wide.save('icons/screenshot-wide.png')
print('✓ screenshot-wide.png (1280x720)')

# Mobile screenshot (540x720)
ss_port = Image.new('RGB', (540, 720), color='#0f1117')
draw_p = ImageDraw.Draw(ss_port)

try:
    font_sm = ImageFont.truetype("arial.ttf", 50)
except IOError:
    font_sm = ImageFont.load_default()

for i, c in enumerate(colors):
    x = 80 + i * 120
    draw_p.rectangle([(x, 200), (x + 100, 550)], fill=c)

draw_p.text((270, 100), "MatplotGallery", fill='white', font=font_sm, anchor='mm')
ss_port.save('icons/screenshot-portrait.png')
print('✓ screenshot-portrait.png (540x720)')

print('\n✅ All icons and screenshots created successfully!')
