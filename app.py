#!/usr/bin/env python3
"""
BMW OBC Prototype - HOME Screen
- Pi OS Lite + DSI (no desktop)
- Forces KMS/DRM backend
- Pixel font for 80s vibe
"""

import os
import sys
import time
import pygame

# ---------- Force correct backend ----------
os.environ["SDL_VIDEODRIVER"] = "kmsdrm"

# ---------- Config ----------
LOGICAL_W, LOGICAL_H = 320, 240
AMBER = (224, 122, 0)
BLACK = (0, 0, 0)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SPLASH_PATH = os.path.join(PROJECT_DIR, "splash.png")
FONT_PATH   = os.path.join(PROJECT_DIR, "assets/fonts/PressStart2P-Regular.ttf")

FAKE_CITY = "NASHVILLE"
FAKE_NOW  = "82°F CLOUDY"
FAKE_HILO = "H88 L71 POP30%"

# ---------- Helpers ----------
def load_logo(target_size_px: int) -> pygame.Surface | None:
    if not os.path.exists(SPLASH_PATH):
        return None
    try:
        img = pygame.image.load(SPLASH_PATH).convert_alpha()
        return pygame.transform.smoothscale(img, (target_size_px, target_size_px))
    except Exception:
        return None

def draw_label(surf, text, x, y, size=16, color=AMBER):
    font = pygame.font.Font(FONT_PATH if os.path.exists(FONT_PATH) else None, size)
    surf.blit(font.render(text, True, color), (x, y))

def draw_home(surface, logo_small: pygame.Surface | None):
    surface.fill(BLACK)

    if logo_small:
        surface.blit(logo_small, (8, 8))
    else:
        pygame.draw.circle(surface, AMBER, (32, 32), 20)

    draw_label(surface, "BMW OBC", 68, 18, size=16)
    draw_label(surface, "-"*28, 8, 34, size=8)

    now_time = time.strftime("%H:%M")
    now_date = time.strftime("%d %b %Y").upper()
    draw_label(surface, f"TIME  {now_time}", 16, 70, size=14)
    draw_label(surface, f"DATE  {now_date}", 16, 90, size=14)

    draw_label(surface, "WEATHER", 16, 120, size=12)
    draw_label(surface, f"{FAKE_CITY}", 16, 140, size=12)
    draw_label(surface, f"{FAKE_NOW}", 16, 160, size=12)
    draw_label(surface, f"{FAKE_HILO}", 16, 180, size=12)

# ---------- Main ----------
def main():
    fullscreen = ("--fullscreen" in sys.argv) or ("-f" in sys.argv)

    pygame.init()

    if fullscreen:
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((800,480))
    pygame.display.set_caption("BMW OBC Prototype")

    info = pygame.display.Info()
    physical = (info.current_w, info.current_h)
    logical  = pygame.Surface((LOGICAL_W, LOGICAL_H))
    clock    = pygame.time.Clock()

    logo_small = load_logo(48)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            elif e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

        draw_home(logical, logo_small)
        scaled = pygame.transform.scale(logical, physical)
        screen.blit(scaled, (0,0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
