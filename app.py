#!/usr/bin/env python3
"""
BMW OBC Prototype - Minimal HOME Screen
---------------------------------------
- Designed for Raspberry Pi 3 B+ with OS Lite + DSI display.
- Renders to a 320x240 logical surface for 80s pixel vibe, then upscales.
- Shows: splash.png as a logo (scaled), BMW title, time/date, fake weather.
- Run: python3 app.py --fullscreen
- Exit: press ESC or q
"""

import os
import sys
import time
import pygame

# ---------- Config ----------
LOGICAL_W, LOGICAL_H = 320, 240       # low-res logical surface
AMBER = (224, 122, 0)
BLACK = (0, 0, 0)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SPLASH_PATH = os.path.join(PROJECT_DIR, "splash.png")

# Fake weather (for now)
FAKE_CITY = "NASHVILLE"
FAKE_NOW  = "82°F  CLOUDY"
FAKE_HILO = "H 88°  L 71°  POP 30%"

# ---------- Helpers ----------
def load_logo(target_size_px: int) -> pygame.Surface | None:
    """Load splash.png and scale to a square size."""
    if not os.path.exists(SPLASH_PATH):
        return None
    try:
        img = pygame.image.load(SPLASH_PATH).convert_alpha()
        logo = pygame.transform.smoothscale(img, (target_size_px, target_size_px))
        return logo
    except Exception:
        return None

def draw_roundel_fallback(surf, x, y, scale=1):
    """Fallback orange/black concentric circles if no splash.png."""
    r_outer, r_mid, r_inner = 18*scale, 12*scale, 6*scale
    pygame.draw.circle(surf, AMBER, (x, y), r_outer)
    pygame.draw.circle(surf, BLACK, (x, y), r_mid)
    pygame.draw.circle(surf, AMBER, (x, y), r_inner)

def draw_label(surf, text, x, y, size=16, color=AMBER):
    font = pygame.font.Font(None, size)  # swap in pixel font later
    surf.blit(font.render(text, True, color), (x, y))

def draw_home(surface, logo_small: pygame.Surface | None):
    surface.fill(BLACK)

    # Header: logo (or fallback) + title
    if logo_small:
        surface.blit(logo_small, (8, 8))
    else:
        draw_roundel_fallback(surface, 8+24, 8+24, scale=1)

    draw_label(surface, "BMW OBC", 68, 12, size=24)
    draw_label(surface, "────────────────────────────", 8, 34, size=16)

    # Time & Date
    now_time = time.strftime("%H:%M")
    now_date = time.strftime("%d %b %Y").upper()
    draw_label(surface, f"TIME   {now_time}", 16, 60, size=26)
    draw_label(surface, f"DATE   {now_date}", 16, 90, size=22)

    # Weather
    draw_label(surface, "WEATHER", 16, 120, size=18)
    draw_label(surface, f"{FAKE_CITY}", 16, 138, size=18)
    draw_label(surface, f"{FAKE_NOW}", 16, 156, size=18)
    draw_label(surface, f"{FAKE_HILO}", 16, 174, size=18)

# ---------- Main ----------
def main():
    fullscreen = ("--fullscreen" in sys.argv) or ("-f" in sys.argv)

    # Force SDL to use KMS/DRM backend (works on Pi OS Lite, no desktop)
    os.environ["SDL_VIDEODRIVER"] = "kmsdrm"

    pygame.init()

    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption("BMW OBC Prototype")

    info = pygame.display.Info()
    physical = (info.current_w, info.current_h)
    logical = pygame.Surface((LOGICAL_W, LOGICAL_H))
    clock = pygame.time.Clock()

    logo_small = load_logo(48)  # scale splash.png down to ~48px square

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

        draw_home(logical, logo_small)

        # Upscale nearest-neighbor for chunky vibe
        scaled = pygame.transform.scale(logical, physical)
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
