#!/usr/bin/env python3
import os, sys, time, pygame

# --------- CONFIG ---------
WIN_W, WIN_H = 800, 480         # window size
LOG_W, LOG_H = 320, 240         # low-res canvas for pixel vibe
AMBER = (224,122,0); BLACK=(0,0,0)
PROJECT = os.path.dirname(os.path.abspath(__file__))
SPLASH = os.path.join(PROJECT, "splash.png")

# --------- DRAW ---------
def load_logo(sz):
    try:
        img = pygame.image.load(SPLASH).convert_alpha()
        return pygame.transform.smoothscale(img, (sz, sz))
    except Exception:
        return None

def draw_text(surf, txt, x, y, size=18, color=AMBER):
    font = pygame.font.Font(None, size)
    surf.blit(font.render(txt, True, color), (x, y))

def draw_buttons(surf, labels):
    h = 28; y = LOG_H - h
    w = LOG_W // len(labels)
    rects=[]
    for i, lab in enumerate(labels):
        r = pygame.Rect(i*w+2, y+2, w-4, h-4)
        pygame.draw.rect(surf, AMBER, r, width=1)
        draw_text(surf, lab, r.x+6, r.y+6, 16)
        rects.append(r)
    return rects

def home_page(surf, logo):
    surf.fill(BLACK)
    if logo: surf.blit(logo, (10,10))
    draw_text(surf, "BMW OBC", 80, 12, 22)
    draw_text(surf, "-"*28, 8, 32, 14)
    draw_text(surf, f"TIME  {time.strftime('%H:%M')}", 16, 70, 22)
    draw_text(surf, f"DATE  {time.strftime('%d %b %Y').upper()}", 16, 98, 18)
    draw_text(surf, "WEATHER", 16, 132, 16)
    draw_text(surf, "NASHVILLE", 16, 152, 16)
    draw_text(surf, "82°F CLOUDY", 16, 170, 16)
    draw_text(surf, "H88 L71 POP30%", 16, 188, 16)
    return draw_buttons(surf, ["MENU"])

def menu_page(surf):
    surf.fill(BLACK)
    draw_text(surf, "MENU", 12, 12, 22)
    draw_text(surf, "-"*20, 8, 32, 14)
    draw_text(surf, "• HOME", 16, 70, 18)
    draw_text(surf, "• SETTINGS (stub)", 16, 92, 18)
    draw_text(surf, "• ABOUT (stub)", 16, 114, 18)
    return draw_buttons(surf, ["BACK", "HOME"])

# --------- APP ---------
def main():
    fullscreen = ("--fullscreen" in sys.argv) or ("-f" in sys.argv)
    pygame.init()
    flags = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((WIN_W, WIN_H), flags)
    pygame.display.set_caption("BMW OBC (minimal)")
    logical = pygame.Surface((LOG_W, LOG_H))
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    phys = (info.current_w, info.current_h)

    logo = load_logo(56)
    page = "HOME"
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q): running = False
                if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    page = "MENU" if page=="HOME" else "HOME"
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx,my = e.pos
                lx = int(mx * (LOG_W/phys[0])); ly = int(my * (LOG_H/phys[1]))
                for i, r in enumerate(btns):
                    if r.collidepoint((lx,ly)):
                        if page=="HOME" and i==0: page="MENU"
                        elif page=="MENU" and i==0: page="HOME"
                        elif page=="MENU" and i==1: page="HOME"

        if page=="HOME": btns = home_page(logical, logo)
        else:            btns = menu_page(logical)

        scaled = pygame.transform.scale(logical, (WIN_W, WIN_H))
        screen.blit(scaled, (0,0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
