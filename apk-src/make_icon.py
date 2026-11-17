#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""生成 APK 启动图标：深色底 + 金色命盘方格 + 朱红印章（纯几何，不依赖中文字体）。"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent / 'res'
DENSITIES = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}

BG = (11, 13, 18, 255)
GOLD = (216, 178, 99, 255)
GOLD2 = (169, 132, 53, 255)
GRID = (216, 178, 99, 62)
SEAL = (178, 59, 50, 255)


def render(size: int) -> Image.Image:
    S = size * 4  # 4x 超采样
    im = Image.new('RGBA', (S, S), BG)
    d = ImageDraw.Draw(im)

    # 外框（双线圆角）
    m = int(S * 0.085)
    d.rounded_rectangle([m, m, S - m, S - m], radius=int(S * 0.16),
                        outline=GOLD, width=max(2, int(S * 0.016)))
    m2 = m + int(S * 0.048)
    d.rounded_rectangle([m2, m2, S - m2, S - m2], radius=int(S * 0.11),
                        outline=GOLD2, width=max(1, int(S * 0.007)))

    # 4x4 命盘网格
    a, b = int(S * 0.295), int(S * 0.705)
    lw = max(1, int(S * 0.0035))
    for i in (1, 2, 3):
        x = a + (b - a) * i // 4
        d.line([(x, a), (x, b)], fill=GRID, width=lw)
        d.line([(a, x), (b, x)], fill=GRID, width=lw)
    d.rectangle([a, a, b, b], outline=GOLD2, width=lw)

    # 中央朱红菱形印章
    c, r = S // 2, int(S * 0.115)
    pts = [(c, c - r), (c + r, c), (c, c + r), (c - r, c)]
    d.polygon(pts, fill=SEAL)
    d.line(pts + [pts[0]], fill=GOLD, width=max(2, int(S * 0.009)), joint='curve')
    ir = int(r * 0.40)
    d.rectangle([c - ir, c - ir, c + ir, c + ir], outline=GOLD,
                width=max(1, int(S * 0.006)))

    # 四角星点
    for px, py in ((int(S * .19), int(S * .19)), (int(S * .81), int(S * .19)),
                   (int(S * .19), int(S * .81)), (int(S * .81), int(S * .81))):
        rr = int(S * 0.017)
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=GOLD)

    return im.resize((size, size), Image.LANCZOS)


def main():
    for name, size in DENSITIES.items():
        out = ROOT / f'mipmap-{name}' / 'ic_launcher.png'
        out.parent.mkdir(parents=True, exist_ok=True)
        render(size).save(out, 'PNG')
        print(f'  {out.relative_to(ROOT.parent)}  {size}x{size}')

    # Android 8+ 自适应图标（矢量，无需字体）
    v26 = ROOT / 'mipmap-anydpi-v26'
    v26.mkdir(parents=True, exist_ok=True)
    (v26 / 'ic_launcher.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
''', encoding='utf-8')

    dr = ROOT / 'drawable'
    dr.mkdir(parents=True, exist_ok=True)
    (dr / 'ic_launcher_background.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#0B0D12" android:pathData="M0,0 H108 V108 H0 Z" />
</vector>
''', encoding='utf-8')
    (dr / 'ic_launcher_foreground.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#D8B263"
        android:pathData="M54,26 L58,50 L82,54 L58,58 L54,82 L50,58 L26,54 L50,50 Z" />
    <path android:fillColor="#B23B32"
        android:pathData="M54,40 L68,54 L54,68 L40,54 Z" />
    <path android:strokeColor="#A98435" android:strokeWidth="1.6"
        android:fillColor="#00000000"
        android:pathData="M32,32 H76 V76 H32 Z" />
</vector>
''', encoding='utf-8')
    print('  自适应图标 XML 已生成')


if __name__ == '__main__':
    main()
