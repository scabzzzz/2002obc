#!/usr/bin/env python3
"""
Minimal HOME screen for BMW OBC prototype.
- No kiosk, just a normal window (fullscreen optional via CLI).
- Shows: roundel-like image from splash.png (scaled), BMW label fallback,
         time, date, and fake weather.
- Renders to a small logical canvas (320x240) for chunky 80s vibe, then upscales.
"""

import os
import sys
import time
import pygame

# ---------- Config ----------
# Logical canvas (low-res look)
LOGICAL_W, LOGICAL_H = 320, 240
BOTTOM_BAR_H = 0  # not using buttons yet

# Colors (80s amber)
AMBER = (224, 122, 0)
BLACK = (0, 0, 0)

# Fake weather (for now)
FAKE_CITY = "NASHVILLE"
FAKE_NOW  = "82°F  CLOUDY"
FAKE_HILO = "H 88°  L 71°  POP 30%"

# Where to find splash.png (your 911x911 image)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SPLASH_PATH = os.path.join(PROJECT_DIR, "splash.png")

# ---------- Helpers ----------
def load_and_scale_logo(target_size_px: int) -> pygame.Surface | None:
    """
    Load splash.png and scale it to a square of target_size_px.
    Returns a Surface or None if not found/failed.
    """
    if not os.path.exists(SPLASH_PATH):
        return None
    try:
        img = pygame.image.load(SPLASH_PATH).convert_alpha()
        # Scale to square, preserve aspect by fitting smallest dimension
        logo = pygame.transform.smoothscale(img, (target_size_px, target_size_px))
        return logo
    except Exception:
        return None

def draw_roundel_fallback(surf, x, y, scale=1):
    """
    Simple orange/black concentric circles in case splash.png is missing.
    """
    r_outer, r_mid, r_inner = 18*scale, 12*scale, 6*scale
    pygame.draw.circle(surf, AMBER, (x, y), r_outer)
    pygame.draw.circle(surf, BLACK, (x, y), r_mid)
    pygame.draw.circle(surf, AMBER, (x, y), r_inner)

def draw_label(surf, text, x, y, size=16, color=AMBER):
    font = pygame.font.Font(None, size)  # swap in a pixel TTF later
    surf.blit(font.render(text, True, color), (x, y))

def draw_home(surface, logo_small: pygame.Surface | None):
    surface.fill(BLACK)

    # Header area: logo (or fallback) + title
    # Reserve ~48px square for logo
    if logo_small:
        surface.blit(logo_small, (8, 8))
    else:
        draw_roundel_fallback(surface, 8 + 24, 8 + 24, scale=1)

    # If you want "BMW" text too, add it next to the logo:
    draw_label(surface, "BMW OBC", 68, 12, size=24)

    # Divider (fake pixel line)
    draw_label(surface, "────────────────────────────", 8, 34, size=16)

    # Time/Date (bigger)
    now_time = time.strftime("%H:%M")
    now_date = time.strftime("%d %b %Y").upper()
    draw_label(surface, f"TIME        {now_time}", 16, 60, size=22)
    draw_label(surface, f"DATE        {now_date}", 16, 86, size=22)

    # Fake weather block
    draw_label(surface, "WEATHER", 16, 118, size=18)
    draw_label(surface, f"{FAKE_CITY}", 16, 138, size=18)
    draw_label(surface, f"{FAKE_NOW}", 16, 156, size=18)
    draw_label(surface, f"{FAKE_HILO}", 16, 174, size=18)

def main():
    # Parse a simple --fullscreen flag (optional)
    fullscreen = ("--fullscreen" in sys.argv) or ("-f" in sys.argv)

    pygame.init()

    # Create the physical window
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        # Windowed for development (fits most Pi screens). Adjust if you want.
        screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption("BMW OBC Prototype")

    # Detect physical size to scale our logical canvas
    info = pygame.display.Info()
    physical = (info.current_w, info.current_h)
    logical = pygame.Surface((LOGICAL_W, LOGICAL_H))
    clock = pygame.time.Clock()

    # Load logo derived from splash.png and scale to ~48 px square on the logical canvas
    # (Looks good next to 24px title text)
    logo_small = load_and_scale_logo(48)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                # quick exits for dev
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

        # Draw HOME each frame (for now)
        draw_home(logical, logo_small)

        # Nearest-neighbor upscale for chunky 80s look
        scaled = pygame.transform.scale(logical, physical)
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
