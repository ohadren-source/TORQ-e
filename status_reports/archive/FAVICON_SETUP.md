# TORQ-e Favicon Setup Guide

## Overview

The Torque de Santa Tegra logo serves as the TORQ-e favicon. This guide explains how to generate favicon variants and integrate them into web applications.

---

## Generate Favicon Variants

### Source File
- **Master Image**: `Teste Rosa/TdST.png` (512×512px)
- **Tool**: Use online favicon generator or ImageMagick

### Using Online Tool (Recommended)
1. Go to https://favicon-generator.org/
2. Upload `TdST.png`
3. Download generated favicon package
4. Extract to `assets/` folder

### Using ImageMagick (CLI)
```bash
cd "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e"

# Create resized versions
magick Teste\ Rosa/TdST.png -resize 512x512 assets/logo-512.png
magick Teste\ Rosa/TdST.png -resize 256x256 assets/logo-256.png
magick Teste\ Rosa/TdST.png -resize 64x64 assets/logo-64.png
magick Teste\ Rosa/TdST.png -resize 32x32 assets/favicon-32.png
magick Teste\ Rosa/TdST.png -resize 16x16 assets/favicon-16.png

# Create .ico file (favicon for older browsers)
magick Teste\ Rosa/TdST.png -define icon:auto-resize=16,32,48 assets/favicon.ico
```

### Using Python + Pillow
```python
from PIL import Image
import os

src = "Teste Rosa/TdST.png"
img = Image.open(src)

sizes = [
    (512, "assets/logo-512.png"),
    (256, "assets/logo-256.png"),
    (64, "assets/logo-64.png"),
    (32, "assets/favicon-32.png"),
    (16, "assets/favicon-16.png"),
]

for size, dest in sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(dest)
    print(f"✓ Generated {dest}")

# Create .ico
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
img.save("assets/favicon.ico", sizes=ico_sizes)
print("✓ Generated assets/favicon.ico")
```

---

## Folder Structure

```
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\
├── Teste Rosa/
│   └── TdST.png (Master source - 512×512px)
├── assets/
│   ├── logo-512.png (Full resolution logo)
│   ├── logo-256.png (Medium resolution)
│   ├── logo-64.png (Dashboard/header)
│   ├── favicon-32.png (Modern browsers)
│   ├── favicon-16.png (Legacy browsers, bookmarks)
│   ├── favicon.ico (Windows/older browsers)
│   └── apple-touch-icon.png (Apple devices, optional)
├── BRANDING.md
└── FAVICON_SETUP.md (this file)
```

---

## Web Integration

### HTML (All Favicon Variants)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TORQ-e Medicaid Identity System</title>
    
    <!-- Favicon variants for different browsers/devices -->
    <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png">
    <link rel="icon" type="image/x-icon" href="/assets/favicon.ico">
    
    <!-- Apple touch icon (for home screen on iOS) -->
    <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
    
    <!-- Microsoft tile (for Windows Start menu) -->
    <meta name="msapplication-TileImage" content="/assets/logo-64.png">
    <meta name="msapplication-TileColor" content="#D4AF37">
    
    <!-- Android Chrome -->
    <link rel="icon" type="image/png" sizes="192x192" href="/assets/logo-256.png">
    <meta name="theme-color" content="#003366">
</head>
<body>
    <!-- Your content -->
</body>
</html>
```

### Flask/Python Web App

```python
from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        'assets',
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# Serve logo assets
@app.route('/assets/<path:filename>')
def serve_asset(filename):
    return send_from_directory('assets', filename)
```

### CSS (Logo in Header)

```css
header {
    display: flex;
    align-items: center;
    padding: 16px;
    background: white;
    border-bottom: 1px solid #E0E0E0;
}

.logo {
    width: 48px;
    height: 48px;
    margin-right: 24px;
    background-image: url('/assets/favicon-32.png');
    background-size: contain;
    background-repeat: no-repeat;
}

.logo:hover {
    opacity: 0.8;
    transition: opacity 0.2s ease;
}
```

### Next.js / React

```jsx
import Head from 'next/head';

export default function Layout() {
    return (
        <>
            <Head>
                <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png" />
                <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png" />
                <link rel="icon" type="image/x-icon" href="/assets/favicon.ico" />
                <meta name="theme-color" content="#003366" />
            </Head>
            <header>
                <img src="/assets/favicon-32.png" alt="TORQ-e Logo" className="logo" />
                <h1>TORQ-e Medicaid Identity System</h1>
            </header>
        </>
    );
}
```

---

## Favicon Specifications

### favicon.ico (Legacy)
- **Formats**: 16×16, 32×32, 48×48 pixels
- **Color Depth**: 32-bit (RGBA)
- **Usage**: Older browsers, bookmarks, address bar
- **Note**: Modern browsers prefer .png; keep for compatibility

### favicon-32.png (Modern)
- **Dimensions**: 32×32 pixels
- **Format**: PNG-32 with transparency
- **Usage**: Modern browser tabs, bookmarks
- **Recommended**: Primary favicon

### favicon-16.png (Legacy Fallback)
- **Dimensions**: 16×16 pixels
- **Format**: PNG-32 with transparency
- **Usage**: Very small displays, legacy systems
- **Note**: Usually browser will scale 32px down if this isn't available

### apple-touch-icon.png (Optional)
- **Dimensions**: 180×180 pixels
- **Format**: PNG
- **Usage**: iOS home screen icons
- **Background**: White background (iOS strips rounded corners)

---

## Browser Support

| Browser | Supported Formats | Preferred Size |
|---------|-------------------|-----------------|
| Chrome | PNG, ICO, SVG | 32×32px PNG |
| Firefox | PNG, ICO, SVG | 32×32px PNG |
| Safari | PNG, ICO | 32×32px PNG |
| Edge | PNG, ICO, SVG | 32×32px PNG |
| IE 11 | ICO only | favicon.ico |
| iOS Safari | PNG | 180×180px |
| Android Chrome | PNG | 192×192px |

---

## Testing

### Test Favicon Display

1. **Browser Tab**
   - Open website in browser
   - Check browser tab shows TORQ-e logo
   - Clear cache if not showing

2. **Bookmark**
   - Bookmark the page
   - Check favicon shows in bookmarks menu

3. **Mobile Home Screen**
   - Save website to home screen on iOS/Android
   - Check icon displays correctly

4. **DevTools**
   ```
   Right-click → Inspect
   Look for <link rel="icon"> tags in <head>
   Check all href paths are correct
   ```

### Cache Busting

If favicon doesn't update after changes:

```html
<!-- Add version parameter -->
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png?v=2">
```

Or clear browser cache:
- **Chrome**: Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)
- **Firefox**: Ctrl+Shift+Delete
- **Safari**: Develop → Empty Caches

---

## Deployment Checklist

- [ ] All favicon variants generated (ico, 16px, 32px, 64px, 256px, 512px)
- [ ] Files saved in `assets/` folder
- [ ] HTML head includes all favicon link tags
- [ ] CSS uses correct asset paths (`/assets/...`)
- [ ] Server configured to serve favicon (404 errors handled)
- [ ] Tested in multiple browsers
- [ ] Cache busting implemented if needed
- [ ] Mobile home screen icon tested
- [ ] Windows tile color set in meta tags

