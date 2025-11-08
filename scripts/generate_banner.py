#!/usr/bin/env python3
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

COLORS = {
    'bg': '#0F172A',
    'accent': '#0EA5E9',
    'muted': '#64748B',
    'muted2': '#94A3B8',
}

NAME = os.getenv('BANNER_NAME', 'Ajesh Krishnan')
TAGLINE = os.getenv('BANNER_TAGLINE', 'Professional Cybersecurity Analyst')
WIDTH = int(os.getenv('BANNER_WIDTH', '1200'))
HEIGHT = int(os.getenv('BANNER_HEIGHT', '220'))

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{NAME} — {TAGLINE}">
  <defs>
    <linearGradient id="metalText" x1="0%" y1="0%" x2="200%" y2="0%">
      <stop offset="0%" style="stop-color:#0EA5E9;stop-opacity:1">
        <animate attributeName="stop-color" values="#0EA5E9;#38BDF8;#0EA5E9" dur="3s" repeatCount="indefinite" />
      </stop>
      <stop offset="50%" style="stop-color:#38BDF8;stop-opacity:1">
        <animate attributeName="stop-color" values="#38BDF8;#0EA5E9;#38BDF8" dur="3s" repeatCount="indefinite" />
      </stop>
      <stop offset="100%" style="stop-color:#0EA5E9;stop-opacity:1">
        <animate attributeName="stop-color" values="#0EA5E9;#0284C7;#0EA5E9" dur="3s" repeatCount="indefinite" />
      </stop>
    </linearGradient>
    <linearGradient id="metalLine" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0EA5E9;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0284C7;stop-opacity:1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style>
      .name {{ font: 700 52px -apple-system,BlinkMacSystemFont,'Segoe UI','Inter','Roboto','Helvetica Neue',Arial,sans-serif; fill: url(#metalText); filter: url(#glow); }}
      .tagline {{ font: 400 18px -apple-system,BlinkMacSystemFont,'Segoe UI','Inter','Roboto','Helvetica Neue',Arial,sans-serif; fill: {COLORS['muted2']}; letter-spacing: 0.5px; }}
    </style>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{COLORS['bg']}" />
  <rect x="0" y="0" width="{WIDTH}" height="2" fill="url(#metalLine)" />
  <g transform="translate(50,0)">
    <text x="0" y="{HEIGHT//2 - 8}" class="name">{NAME}</text>
    <text x="0" y="{HEIGHT//2 + 30}" class="tagline">{TAGLINE}</text>
  </g>
</svg>
'''

os.makedirs('assets', exist_ok=True)
with open(os.path.join('assets', 'banner.svg'), 'w', encoding='utf-8') as f:
    f.write(svg)

def _load_font(size: int, bold: bool = False):
    try:
        # Ubuntu runners usually have DejaVu
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=size)
    except Exception:
        try:
            # Windows/Mac common fallbacks
            if bold:
                return ImageFont.truetype("arialbd.ttf", size=size)
            return ImageFont.truetype("arial.ttf", size=size)
        except Exception:
            return ImageFont.load_default()

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_metallic_gradient(width, height, color1, color2, color3):
    """Create a metallic gradient image"""
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        t = y / height
        if t < 0.5:
            # Blend color1 to color2
            blend = t * 2
            r = int(color1[0] * (1-blend) + color2[0] * blend)
            g = int(color1[1] * (1-blend) + color2[1] * blend)
            b = int(color1[2] * (1-blend) + color2[2] * blend)
        else:
            # Blend color2 to color3
            blend = (t - 0.5) * 2
            r = int(color2[0] * (1-blend) + color3[0] * blend)
            g = int(color2[1] * (1-blend) + color3[1] * blend)
            b = int(color2[2] * (1-blend) + color3[2] * blend)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img

def generate_gif(name: str, tagline: str, width: int, height: int, frames: int = 48, duration_ms: int = 120):
    bg_rgb = hex_to_rgb(COLORS['bg'])
    # Metallic gradient colors
    metal1 = hex_to_rgb('#38BDF8')  # Light cyan
    metal2 = hex_to_rgb('#0EA5E9')  # Accent
    metal3 = hex_to_rgb('#0284C7')  # Darker cyan
    muted2_rgb = hex_to_rgb(COLORS['muted2'])

    name_font = _load_font(52, bold=True)
    tagline_font = _load_font(18, bold=False)

    frames_out = []
    for i in range(frames):
        t = i / frames
        # Base image
        img = Image.new('RGB', (width, height), bg_rgb)
        draw = ImageDraw.Draw(img)
        
        # Static gradient top line (no shimmer)
        line_height = 2
        for x in range(width):
            ratio = x / width
            r = int(metal2[0] * (1-ratio) + metal3[0] * ratio)
            g = int(metal2[1] * (1-ratio) + metal3[1] * ratio)
            b = int(metal2[2] * (1-ratio) + metal3[2] * ratio)
            draw.rectangle([x, 0, x+1, line_height], fill=(r, g, b))
        
        # Get text bounding boxes
        temp_draw = ImageDraw.Draw(Image.new('RGBA', (width, height)))
        name_bbox = temp_draw.textbbox((50, height//2 - 8), name, font=name_font)
        name_w = name_bbox[2] - name_bbox[0]
        name_h = name_bbox[3] - name_bbox[1]
        
        # Animated metallic gradient for name text - shift colors through cycle
        cycle = (t * 3) % 1  # 3 cycles through animation
        if cycle < 0.33:
            c1, c2, c3 = metal2, metal1, metal2
        elif cycle < 0.66:
            c1, c2, c3 = metal1, metal2, metal3
        else:
            c1, c2, c3 = metal2, metal3, metal2
            
        metal_grad = create_metallic_gradient(name_w, name_h, c1, c2, c3)
        
        # Create text mask
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((50, height//2 - 8), name, fill=255, font=name_font)
        
        # Apply metallic gradient to text area
        img.paste(metal_grad, (50, height//2 - 8), mask.crop((50, height//2 - 8, 50 + name_w, height//2 - 8 + name_h)))
        
        # Add subtle glow to name
        glow_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        glow_draw.text((50, height//2 - 8), name, fill=(*metal1, 60), font=name_font)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=2))
        img = Image.alpha_composite(img.convert('RGBA'), glow_layer).convert('RGB')
        
        # Tagline (static)
        draw = ImageDraw.Draw(img)
        draw.text((50, height//2 + 30), tagline, fill=muted2_rgb, font=tagline_font)
        
        frames_out.append(img.convert('P', palette=Image.ADAPTIVE, colors=256))

    out_path = os.path.join('assets', 'banner.gif')
    frames_out[0].save(
        out_path,
        save_all=True,
        append_images=frames_out[1:],
        loop=0,
        duration=duration_ms,
        disposal=2,
        optimize=False,
    )

generate_gif(NAME, TAGLINE, WIDTH, HEIGHT, frames=60, duration_ms=100)

print('Wrote assets/banner.svg and assets/banner.gif')
