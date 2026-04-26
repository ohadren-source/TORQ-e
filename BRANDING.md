# TORQ-e Brand Guidelines

## Official Logo

**File**: `Teste Rosa/TdST.png` (Torque de Santa Tegra)

**Source**: Torque de Santa Tegra — Ancient Celtic neck ring from 1st century BC, discovered at Castro de Santa Trega, A Guarda, Spain. Open source artifact imagery from MASAT museum collection.

**Usage**: Primary logo for all TORQ-e materials (web, documents, presentations, communications).

---

## Logo Specifications

### Primary Logo (Full Color)
- **File**: TdST.png
- **Format**: PNG with transparency
- **Dimensions**: 512×512px (master)
- **Color**: Gold/bronze (as original artifact)
- **Background**: Transparent
- **Usage**: Website, dashboards, official documents

### Logo Variations

**Favicon (16×16px)**
- Use for browser tabs, bookmarks

**Header Logo (64×64px)**
- Use for website header/navigation

**Icon (32×32px)**
- Use for app icons, social media profiles

**Print Logo (300dpi)**
- Use for official printed materials

---

## Color Palette

| Element | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Primary Gold | #D4AF37 | (212, 175, 55) | Logo, headers, accents |
| Dark Bronze | #8B6914 | (139, 105, 20) | Text, borders on light backgrounds |
| State Blue | #003366 | (0, 51, 102) | Government/official elements |
| White | #FFFFFF | (255, 255, 255) | Background, text on dark |
| Light Gray | #F5F5F5 | (245, 245, 245) | Neutral background |

---

## Logo Placement

### Website Header
- Place logo in top-left corner
- Size: 48×48px
- Margin: 16px from edges
- Link to homepage

### Documents
- Place logo in document header (top-right or center)
- Size: 1 inch (96px at 96dpi)
- Document title beneath or beside logo

### Presentations
- Slide 1 (title slide): Full logo, 4×4 inches, centered
- Subsequent slides: Small logo (0.5×0.5 inches) in corner

### Email Signature
- Logo: 32×32px
- Placed left of name/title

---

## Typography

**Logotype**: TORQ-e (without additional text)

**Font Pairing**:
- Headlines: Sans-serif (Helvetica, Arial, or system sans-serif)
- Body: Sans-serif (same as headlines for consistency)
- Code/Technical: Monospace (Courier New, Monaco, or system monospace)

**Official Tagline** (optional):
"Unified Identity. Fraud Prevention. Program Integrity."

---

## Brand Voice

**Tone**: Professional, authoritative, accessible
**Audience**: State employees, healthcare providers, members, analysts
**Key Messages**:
- One identity, unified across all systems
- Real-time fraud detection protects the program
- Simple enrollment, fast claim processing
- Secure, transparent, accountable

---

## Logo Do's & Don'ts

### ✅ DO

- Use the official logo file (TdST.png)
- Maintain clear space around logo (min 16px)
- Use full color logo on white/light backgrounds
- Use white logo on dark backgrounds (with proper contrast)
- Resize proportionally (maintain aspect ratio)

### ❌ DON'T

- Distort, stretch, or skew the logo
- Change logo colors
- Add gradients or effects to logo
- Place logo on patterned or cluttered backgrounds without clear space
- Use low-resolution versions for large displays
- Rotate logo (except 90° increments if necessary)

---

## File Manifest

```
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\
├── Teste Rosa/
│   └── TdST.png (Master - 512×512px)
├── assets/
│   ├── logo-512.png (Full logo)
│   ├── logo-256.png (Web header)
│   ├── logo-64.png (Dashboard icon)
│   ├── favicon-32.png (Browser tab)
│   ├── favicon-16.png (Browser bookmark)
│   ├── favicon.ico (Windows favicon)
│   └── logo.svg (Vector version, if needed)
├── BRANDING.md (this file)
└── [Other documentation]
```

---

## Contact

For logo usage questions or brand guideline clarifications:
- Documentation: See ARCHITECTURE_BUSINESS_ANALYST.md or ARCHITECTURE_TECHNICAL.md
- Questions: Contact TORQ-e project lead


---

## Favicon Setup

> Source: `Teste Rosa/TdST.png` (512x512px master)

### Generate variants (Python + Pillow)
```python
from PIL import Image
src = "Teste Rosa/TdST.png"
img = Image.open(src)
for size, dest in [(512,"assets/logo-512.png"),(256,"assets/logo-256.png"),(64,"assets/logo-64.png"),(32,"assets/favicon-32.png"),(16,"assets/favicon-16.png")]:
    img.resize((size,size), Image.Resampling.LANCZOS).save(dest)
img.save("assets/favicon.ico", sizes=[(16,16),(32,32),(48,48),(64,64)])
```

### HTML head tags
```html
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png">
<link rel="icon" type="image/x-icon" href="/assets/favicon.ico">
<meta name="theme-color" content="#003366">
```

### Cache busting
```html
<link rel="icon" href="/assets/favicon-32.png?v=2">
```
