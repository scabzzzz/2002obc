#!/usr/bin/env python3
# BMW 2002 OBC – wireframe home (clean calculator style)
# Runs best under X11 (startx). No driver forcing here.

import os, sys, time, pygame

# -------- CONFIG --------
LOG_W, LOG_H = 320, 240          # low-res canvas for pixel look
AMBER = (224,122,0); BLACK=(0,0,0)
PROJECT = os.path.dirname(os.path.abspath(__file__))
SPLASH  = os.path.join(PROJECT, "splash.png")  # your 911x911

# -------- HELPERS --------
def load_logo(sz):
    try:
        img = pygame.image.load(SPLASH).convert_alpha()
        return pygame.transform.smoothscale(img,(sz,sz))
    except Exception:
        return None

def font(size):  # swap to pixel TTF later if desired
    return pygame.font.Font(None, size)

def draw_text(surf, txt, xy, size=18, color=AMBER):
    surf.blit(font(size).render(txt, True, color), xy)

def rect(surf, r, w=1, color=AMBER):
    pygame.draw.rect(surf, color, r, width=w)

# -------- LAYOUT (logical coordinates) --------
def layout_home():
    # boxes per your sketch (all in LOG_W x LOG_H space)
    margin, gutter = 6, 6
    col_btn_w = 110
    header_h = 28
    right_x = LOG_W - margin - col_btn_w

    # regions
    logo_r   = pygame.Rect(margin, margin, 36, 36)
    title_y  = margin
    time_r   = pygame.Rect(margin, header_h+10, LOG_W - col_btn_w - 2*margin - gutter, 64)
    info_r   = pygame.Rect(margin, time_r.bottom + 18, time_r.w, 40)  # temp/date row

    # right buttons (4 stacked)
    btn_h = (LOG_H - header_h - 3*margin) // 4
    btns = []
    y = header_h + margin
    for _ in range(4):
        btns.append(pygame.Rect(right_x, y, col_btn_w, btn_h - gutter))
        y += btn_h

    # split info row into two boxes (TEMP, DATE)
    left_info  = pygame.Rect(info_r.x, info_r.y, info_r.w//2 - gutter//2, info_r.h)
    right_info = pygame.Rect(left_info.right + gutter, info_r.y, info_r.w - left_info.w - gutter, info_r.h)

    return logo_r, title_y, time_r, left_info, right_info, btns

# -------- PAGES --------
def draw_home(surf, logo_sm, tick):
    surf.fill(BLACK)
    logo_r, title_y, time_r, box_temp, box_date, btns = layout_home()

    # Header: small “roundel” + title centered
    if logo_sm:
        surf.blit(logo_sm, logo_r.topleft)
    else:
        # fallback roundel
        cx, cy = logo_r.center
        pygame.draw.circle(surf, AMBER, (cx,cy), 16, 2)
        pygame.draw.line(surf, AMBER, (cx-10,cy), (cx+10,cy), 2)
        pygame.draw.line(surf, AMBER, (cx,cy-10), (cx,cy+10), 2)

    title = "BMW 2002"
    title_s = font(18).render(title, True, AMBER)
    surf.blit(title_s, ((LOG_W - title_s.get_width())//2, title_y+4))

    # Big time
    t = time.strftime("%I:%M%p").lstrip("0")  # “9:56PM”
    draw_text(surf, t, (time_r.x+4, time_r.y+6), size=42)

    # Temp / Date boxes
    rect(surf, box_temp); rect(surf, box_date)
    draw_text(surf, f"{75 + (tick%3)}F", (box_temp.x+8, box_temp.y+8), size=24)  # fake temp
    draw_text(surf, time.strftime("%-m-%-d").upper(), (box_date.x+8, box_date.y+8), size=24)

    # Right column buttons
    labels = ["VOLT", "OIL", "TEMP", "DIAG"]
    for r, lab in zip(btns, labels):
        rect(surf, r)
        # center label inside each button
        s = font(22).render(lab, True, AMBER)
        surf.blit(s, (r.x + (r.w - s.get_width())//2, r.y + (r.h - s.get_height())//2))

    return btns, box_temp, box_date

# -------- APP --------
def main():
    fullscreen = ("--fullscreen" in sys.argv) or ("-f" in sys.argv)
    pygame.init()
    flags = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((800,480), flags)
    pygame.display.set_caption("BMW 2002 OBC (home)")
    logical = pygame.Surface((LOG_W, LOG_H))
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    phys = (info.current_w, info.current_h)
    logo_sm = load_logo(36)

    running, tick = True, 0
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running=False
            elif e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q): running=False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx,my = e.pos
                lx = int(mx * (LOG_W/phys[0])); ly = int(my * (LOG_H/phys[1]))
                # hit detection after draw (we re-use rects)
                if any(r.collidepoint((lx,ly)) for r in last_btns):
                    # stub: flash or print for now
                    print("BUTTON:", [ "VOLT","OIL","TEMP","DIAG" ][ [r.collidepoint((lx,ly)) for r in last_btns ].index(True) ])

        last_btns,_,_ = draw_home(logical, logo_sm, tick)
        tick += 1

        scaled = pygame.transform.scale(logical, (800,480))
        screen.blit(scaled,(0,0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
