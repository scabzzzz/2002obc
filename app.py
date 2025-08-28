#!/usr/bin/env python3
"""
BMW OBC Prototype - HOME Screen
- Pi OS Lite + DSI (no desktop)
- Pixel font for 80s vibe
- Works headless over SSH with SDL_VIDEODRIVER=dummy
"""

import os, sys, time, pygame

# ---------- Config ----------
LOGICAL_W, LOGICAL_H = 320, 240
AMBER = (224,122,0); BLACK = (0,0,0)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SPLASH_PATH = os.path.join(PROJECT_DIR, "splash.png")
FONT_PATH   = os.path.join(PROJECT_DIR, "assets/fonts/PressStart2P-Regular.ttf")
FAKE_CITY="NASHVILLE"; FAKE_NOW="82°F CLOUDY"; FAKE_HILO="H88 L71 POP30%"

# ---------- Helpers ----------
def load_logo(sz):
    if not os.path.exists(SPLASH_PATH): return None
    try:
        img = pygame.image.load(SPLASH_PATH).convert_alpha()
        return pygame.transform.smoothscale(img,(sz,sz))
    except Exception: return None

def font(size): return pygame.font.Font(FONT_PATH if os.path.exists(FONT_PATH) else None, size)

def draw_label(surf, txt, x, y, size=16, color=AMBER):
    surf.blit(font(size).render(txt, True, color), (x,y))

def draw_home(surface, logo_small):
    surface.fill(BLACK)
    if logo_small: surface.blit(logo_small,(8,8))
    else: pygame.draw.circle(surface, AMBER, (32,32), 20)
    draw_label(surface,"BMW OBC",68,18,16); draw_label(surface,"-"*28,8,34,8)
    now_time=time.strftime("%H:%M"); now_date=time.strftime("%d %b %Y").upper()
    draw_label(surface,f"TIME  {now_time}",16,70,14)
    draw_label(surface,f"DATE  {now_date}",16,90,14)
    draw_label(surface,"WEATHER",16,120,12)
    draw_label(surface,f"{FAKE_CITY}",16,140,12)
    draw_label(surface,f"{FAKE_NOW}",16,160,12)
    draw_label(surface,f"{FAKE_HILO}",16,180,12)

# ---------- Video Init ----------
def init_video(fullscreen):
    pygame.font.init()
    drv = os.environ.get("SDL_VIDEODRIVER", "").lower()

    # Force headless if dummy explicitly requested
    if drv == "dummy":
        return pygame.Surface((800,480)), "dummy", True

    # Try candidate drivers
    for candidate in ([drv] if drv else []) + ["kmsdrm","fbcon","x11","directfb"]:
        try:
            os.environ["SDL_VIDEODRIVER"] = candidate
            pygame.display.init()
            flags = pygame.FULLSCREEN if fullscreen else 0
            size  = (0,0) if fullscreen else (800,480)
            screen = pygame.display.set_mode(size, flags)
            return screen, candidate, False
        except pygame.error:
            pygame.display.quit()

    # Last resort: dummy headless
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    return pygame.Surface((800,480)), "dummy", True

# ---------- Main ----------
def main():
    fullscreen = ("--fullscreen" in sys.argv) or ("-f" in sys.argv)
    screen, driver, headless = init_video(fullscreen)
    info = pygame.display.Info() if not headless else None
    physical = ((info.current_w, info.current_h) if info else (800,480))
    logical  = pygame.Surface((LOGICAL_W, LOGICAL_H))
    clock    = pygame.time.Clock()
    logo_small = load_logo(48)

    print(f"[OBC] driver={driver} headless={headless} physical={physical}")

    running=True
    while running:
        for e in pygame.event.get() if not headless else []:
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q):
                running=False

        draw_home(logical, logo_small)
        scaled = pygame.transform.scale(logical, physical)
        screen.blit(scaled,(0,0))
        if not headless: pygame.display.flip()
        clock.tick(30)

    if not headless: pygame.quit()

if __name__=="__main__":
    main()
