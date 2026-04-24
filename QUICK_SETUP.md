# TORQ-e Logo & Favicon - Quick Setup (5 minutes)

## Step 1: Generate Favicon Files (2 minutes)

```bash
cd C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e
python generate_favicon.py
```

**What it does**: Reads `Teste Rosa/TdST.png` and creates all favicon sizes in the `assets/` folder.

**Result**: 
```
assets/
├── favicon-32.png (🌟 Main one - browser tab)
├── favicon-16.png (Legacy)
├── favicon.ico (Old browsers)
├── logo-512.png
├── logo-256.png
└── logo-64.png
```

---

## Step 2: Add to Your HTML (1 minute)

Copy this into your `<head>` tag:

```html
<head>
    <title>TORQ-e Medicaid Identity System</title>
    
    <!-- TORQ-e Logo in Browser Tab -->
    <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png">
    <link rel="icon" type="image/x-icon" href="/assets/favicon.ico">
</head>
```

---

## Step 3: Verify (2 minutes)

1. Open your website in browser
2. Look at browser tab - you should see the **Torque de Santa Tegra logo** ✨
3. Done!

---

## Troubleshooting

**Logo not showing in tab?**
- Clear browser cache: `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
- Make sure file paths match your server (`/assets/favicon-32.png`)
- Refresh page: `Ctrl+F5` or `Cmd+Shift+R`

**File paths wrong?**
- If your assets folder is in different location, update the `href` paths
- Example: If assets are in `public/img/`, use `/public/img/favicon-32.png`

---

## What You Get

| Where | What | File |
|-------|------|------|
| Browser Tab | Small Torque logo | favicon-32.png |
| Bookmarks | Tiny Torque logo | favicon-16.png |
| Old Browsers | Torque icon | favicon.ico |
| Dashboards | Medium Torque logo | logo-64.png |
| Documents | Large Torque logo | logo-256.png |

---

## Done ✅

Your TORQ-e logo now appears in:
- ✅ Browser tabs
- ✅ Bookmarks
- ✅ Address bar
- ✅ Tab/window switcher
- ✅ Browser history

That's it. Simple as that.
