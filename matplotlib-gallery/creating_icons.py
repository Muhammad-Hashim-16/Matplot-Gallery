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


from PIL import Image, ImageDraw, ImageFont

# Create desktop screenshot (1280x720)
img_wide = Image.new('RGB', (1280, 720), color='#0f1117')
draw = ImageDraw.Draw(img_wide)
draw.text((640, 360), "MatplotGallery", fill='white', anchor='mm')
img_wide.save('matplotlib-gallery\icons\screenshot-wide.png')

# Create mobile screenshot (540x720)
img_portrait = Image.new('RGB', (540, 720), color='#0f1117')
draw = ImageDraw.Draw(img_portrait)
draw.text((270, 360), "MatplotGallery", fill='white', anchor='mm')
img_portrait.save('matplotlib-gallery\icons\screenshot-portrait.png')

print("Screenshots created")