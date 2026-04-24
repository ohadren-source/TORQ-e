#!/usr/bin/env python3
"""
Generate favicon variants from TdST.png master image
Run this once to create all favicon sizes needed for browser tabs, bookmarks, etc.
"""

from PIL import Image
import os

# Paths
SOURCE_IMAGE = "Teste Rosa/TdST.png"
ASSETS_FOLDER = "assets"

# Create assets folder if it doesn't exist
os.makedirs(ASSETS_FOLDER, exist_ok=True)

# Open master image
print(f"📖 Loading master image: {SOURCE_IMAGE}")
img = Image.open(SOURCE_IMAGE)
print(f"   Original size: {img.size}")

# Generate favicon variants
sizes = [
    (512, "logo-512.png", "Full resolution logo"),
    (256, "logo-256.png", "Medium resolution"),
    (64, "logo-64.png", "Dashboard/header icon"),
    (48, "favicon-48.png", "Windows tile"),
    (32, "favicon-32.png", "Modern browser tabs (PRIMARY)"),
    (16, "favicon-16.png", "Legacy bookmarks/tabs"),
]

print("\n✨ Generating favicon variants...\n")

for size, filename, description in sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    filepath = os.path.join(ASSETS_FOLDER, filename)
    resized.save(filepath)
    print(f"   ✅ {filename:25} ({size:3}×{size:3}px) - {description}")

# Create ICO file for older browsers
print("\n📌 Creating favicon.ico for legacy browser support...\n")
ico_path = os.path.join(ASSETS_FOLDER, "favicon.ico")
img.save(
    ico_path,
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
)
print(f"   ✅ favicon.ico - Multi-resolution ICO file")

print("\n" + "="*60)
print("✨ FAVICON GENERATION COMPLETE!")
print("="*60)
print(f"\n📁 All files saved to: {ASSETS_FOLDER}/")
print("\n📋 Files created:")
print("   - favicon-32.png (Use this one - modern browsers)")
print("   - favicon-16.png (Legacy fallback)")
print("   - favicon.ico (Old IE/Edge)")
print("   - logo-512.png, logo-256.png, logo-64.png (Various uses)")
print("\n🌐 Next: Add this to your HTML <head>:")
print("""
   <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
   <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png">
   <link rel="icon" type="image/x-icon" href="/assets/favicon.ico">
""")
print("\n✅ Done! Your TORQ-e logo will appear in browser tabs.")
