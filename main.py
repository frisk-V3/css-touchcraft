#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_css_tui.py
Terminal-based CSS generator (no external libraries).
Features:
- Interactive TUI using only standard library
- Random theme generation
- Edit colors, font, sizes via prompts
- Save/load JSON configs
- Export CSS and simple preview HTML and open in default browser
Requirements: Python 3.9+
"""

import json
import os
import random
import sys
import webbrowser
from dataclasses import dataclass, asdict
from typing import Dict, Any

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".auto_css_tui")
os.makedirs(CONFIG_DIR, exist_ok=True)

def clamp(v: int, a: int = 0, b: int = 255) -> int:
    return max(a, min(b, int(v)))

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{clamp(r):02x}{clamp(g):02x}{clamp(b):02x}"

def random_color() -> str:
    return rgb_to_hex(random.randint(0,255), random.randint(0,255), random.randint(0,255))

def parse_hex(hex_str: str) -> str:
    s = hex_str.strip()
    if not s:
        raise ValueError("Empty color")
    if s.startswith("#"):
        s = s[1:]
    if len(s) == 3:
        s = "".join([c*2 for c in s])
    if len(s) != 6:
        raise ValueError("Hex must be 3 or 6 digits")
    int(s,16)  # validate
    return "#" + s.lower()

@dataclass
class Theme:
    primary: str = "#3498db"
    secondary: str = "#2ecc71"
    background: str = "#ffffff"
    text: str = "#333333"
    font_family: str = "Arial, sans-serif"
    base_font_size: int = 16
    border_radius: int = 6
    button_padding: str = "10px 16px"
    shadow: bool = True

    def to_dict(self) -> Dict[str,Any]:
        return asdict(self)

    @staticmethod
    def random_theme() -> "Theme":
        return Theme(
            primary=random_color(),
            secondary=random_color(),
            background=random_color(),
            text=random_color(),
            font_family=random.choice([
                "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
                "Georgia, 'Times New Roman', Times, serif",
                "Courier New, Courier, monospace",
                "Verdana, Geneva, sans-serif"
            ]),
            base_font_size=random.choice([14,15,16,17,18]),
            border_radius=random.choice([0,4,6,8,12]),
            button_padding=random.choice(["8px 12px","10px 16px","12px 20px"]),
            shadow=random.choice([True, False])
        )

class CSSGenerator:
    TEMPLATE = """/* Generated CSS */
:root {{
  --color-primary: {primary};
  --color-secondary: {secondary};
  --color-bg: {background};
  --color-text: {text};
  --font-family: {font_family};
  --base-font-size: {base_font_size}px;
  --border-radius: {border_radius}px;
}}

* {{
  box-sizing: border-box;
}}

body {{
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-family);
  font-size: var(--base-font-size);
  margin: 0;
  padding: 20px;
}}

.container {{
  max-width: 900px;
  margin: 0 auto;
}}

button {{
  background: var(--color-primary);
  color: #fff;
  padding: {button_padding};
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  {shadow_css}
}}

button.secondary {{
  background: var(--color-secondary);
}}

.card {{
  background: rgba(255,255,255,0.6);
  border-radius: var(--border-radius);
  padding: 16px;
  margin-bottom: 12px;
  {shadow_css}
}}

.header {{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom: 16px;
}}

.avatar {{
  width:48px;
  height:48px;
  border-radius:50%;
  background: var(--color-primary);
}}

.input, textarea {{
  width:100%;
  padding:8px 10px;
  border:1px solid rgba(0,0,0,0.08);
  border-radius:4px;
  font-size:14px;
}}

.footer {{
  margin-top:24px;
  text-align:center;
  color: rgba(0,0,0,0.5);
  font-size:13px;
}}
"""

    @staticmethod
    def generate(theme: Theme) -> str:
        shadow_css = "box-shadow: 0 4px 12px rgba(0,0,0,0.08);" if theme.shadow else "box-shadow: none;"
        return CSSGenerator.TEMPLATE.format(
            primary=theme.primary,
            secondary=theme.secondary,
            background=theme.background,
            text=theme.text,
            font_family=theme.font_family,
            base_font_size=theme.base_font_size,
            border_radius=theme.border_radius,
            button_padding=theme.button_padding,
            shadow_css=shadow_css
        )

    @staticmethod
    def preview_html(css: str) -> str:
        return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>CSS Preview</title>
<style>
{css}
</style>
</head>
<body>
<div class="container">
  <div class="header card">
    <div style="display:flex;gap:12px;align-items:center">
      <div class="avatar"></div>
      <div>
        <div style="font-weight:700">Preview Title</div>
        <div style="color:rgba(0,0,0,0.6)">Subtitle or description</div>
      </div>
    </div>
    <div><button>Primary</button> <button class="secondary">Secondary</button></div>
  </div>

  <div class="card">
    <h2>Card Heading</h2>
    <p>This is a sample paragraph to preview the generated theme. Edit settings in the TUI and export to see changes.</p>
    <input class="input" placeholder="Sample input"/>
  </div>

  <div class="card footer">Generated on export</div>
</div>
</body>
</html>
"""

def save_theme(theme: Theme, name: str) -> str:
    path = os.path.join(CONFIG_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
    return path

def load_theme(name: str) -> Theme:
    path = os.path.join(CONFIG_DIR, f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Theme(**data)

def list_saved() -> list:
    return [f[:-5] for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]

def prompt(prompt_text: str, default: str = "") -> str:
    try:
        res = input(f"{prompt_text} [{default}]: ").strip()
    except EOFError:
        res = ""
    return res if res else default

def show_menu():
    print("\nAuto CSS TUI — Menu")
    print("1) Edit theme values")
    print("2) Random theme")
    print("3) Save theme")
    print("4) Load theme")
    print("5) Export CSS to file")
    print("6) Preview in browser")
    print("7) List saved themes")
    print("0) Exit")

def edit_theme(theme: Theme) -> Theme:
    print("\nEditing theme values (leave blank to keep current)")
    for field in ["primary","secondary","background","text"]:
        cur = getattr(theme, field)
