#!/usr/bin/env python3
# BMW 2002 OBC – calculator style UI, startx-friendly

import os, sys, time, pygame

# ------ CONFIG ------
LOG_W, LOG_H = 320, 240           # logical canvas (pixel look)
AMBER = (224,122,0); BLACK=(0,0,0)
PROJECT = os.path.dirname(os.path.abspath(__file__))
SPLASH  = os.path.join(PROJECT, "splash.png")

RIGHT_BTN_W = 110                  # right column width (logical px)
MARGIN = 6; GUTTER = 6
HEADER_H = 28

# Fake data defaults
DEFAULT_TEMP_F = 75
FAKE_VOLT   = "12.5 V"
FAKE_OILTMP = "190 °F"
FAKE_COOL   = "182 °F"

# ------ STATE ------
class State:
    def __init__(self):
        self.page = "HOME"
        self.temp_c = False  # False = °F, True = °C
        self.speed_kmh = False
        self.idx = 0         # generic index for NEXT/BACK cycling

STATE = State()

# ------ HELPERS ------
def font(sz): return pygame.font.Font(None, sz)
def text(surf, s, x, y, sz=18, color=AMBER): surf.blit(font(sz).render(s, True, color), (x,y))
def rect(surf, r, w=1, color=AMBER): pygame.draw.rect(surf, color, r, width=w)

def load_scaled(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        return None

def logical_to_phys(p, phys):  # map logical coords hit-test
    lx, ly = p
    return int(lx * (phys[0]/LOG_W)), int(ly * (phys[1]/LOG_H))

def draw_right_buttons(surf, labels):
    btns = []
    right_x = LOG_W - MARGIN - RIGHT_BTN_W
    usable_h = LOG_H - HEADER_H - 3*MARGIN
    btn_h = (usable_h // len(labels))
    y = HEADER_H + MARGIN
    for lab in labels:
        r = pygame.Rect(right_x, y, RIGHT_BTN_W, btn_h - GUTTER)
        rect(surf, r)
        s = font(20).render(lab, True, AMBER)
        surf.blit(s, (r.x + (r.w - s.get_width())//2, r.y + (r.h - s.get_height())//2))
        btns.append(r)
        y += btn_h
    return btns

def temp_display(f):
    if STATE.temp_c:
        c = round((f-32)*5/9)
        return f"{c}°C"
    return f"{f}°F"

# ------ LAYOUTS ------
def home_layout():
    right_x = LOG_W - MARGIN - RIGHT_BTN_W
    time_w  = right_x - (MARGIN + GUTTER)
    time_r  = pygame.Rect(MARGIN, HEADER_H + 8, time_w, 72)   # BIG time
    row_y   = time_r.bottom + 18
    return time_r, row_y

# ------ PAGES ------
def draw_home(surf, logo_sm):
    surf.fill(BLACK)

    # header
    if logo_sm: surf.blit(logo_sm, (MARGIN, MARGIN))
    title = "BMW"
    ts = font(18).render(title, True, AMBER)
    surf.blit(ts, ((LOG_W - ts.get_width())//2, MARGIN+4))

    # big time (2× bigger than before)
    time_r, row_y = home_layout()
    t = time.strftime("%I:%M%p").lstrip("0")
    text(surf, t, time_r.x+2, time_r.y, sz=78)  # giant

    # TEMP | DATE
    # no boxes; use a vertical pipe separator
    tmp = temp_display(DEFAULT_TEMP_F)
    dt  = time.strftime("%m-%d-%Y")
    # left side value
    text(surf, tmp, MARGIN+6, row_y, sz=32)
    # pipe
    pygame.draw.line(surf, AMBER, (LOG_W//2, row_y-2), (LOG_W//2, row_y+36), 1)
    # right side value
    text(surf, dt, LOG_W//2 + 8, row_y, sz=32)

    # right buttons → pages
    labels = ["VOLT","OIL","TEMP","MENU"]
    btns = draw_right_buttons(surf, labels)
    return btns, labels

def draw_simple_value_page(surf, title, kv_pairs):
    surf.fill(BLACK)
    # header
    text(surf, title, (LOG_W - font(18).size(title)[0])//2, MARGIN+4, sz=18)
    pygame.draw.line(surf, AMBER, (MARGIN, HEADER_H-2), (LOG_W - RIGHT_BTN_W - GUTTER, HEADER_H-2), 1)

    y = HEADER_H + 12
    for label, value in kv_pairs:
        text(surf, label, MARGIN+8, y, sz=18); y += 20
        text(surf, value, MARGIN+20, y, sz=28); y += 28

    # nav rail on right for subpages
    btns = draw_right_buttons(surf, ["HOME","BACK","NEXT","MENU"])
    return btns, ["HOME","BACK","NEXT","MENU"]

def draw_volt(surf):
    return draw_simple_value_page(surf, "VOLTAGE", [("BATTERY", FAKE_VOLT)])

def draw_oil(surf):
    return draw_simple_value_page(surf, "OIL", [("TEMP", FAKE_OILTMP), ("PRESS", "— bar")])

def draw_temp(surf):
    return draw_simple_value_page(surf, "TEMPERATURE", [("COOLANT", FAKE_COOL), ("AMBIENT", temp_display(DEFAULT_TEMP_F))])

def draw_menu(surf):
    surf.fill(BLACK)
    title = "MENU"
    text(surf, title, (LOG_W - font(18).size(title)[0])//2, MARGIN+4, sz=18)
    pygame.draw.line(surf, AMBER, (MARGIN, HEADER_H-2), (LOG_W - RIGHT_BTN_W - GUTTER, HEADER_H-2), 1)

    # simple options (tap to toggle)
    options = [
        ("Temp Units", "°C" if STATE.temp_c else "°F"),
        ("Speed Units", "KMH" if STATE.speed_kmh else "MPH"),
        ("Brightness", "—"),  # stub
    ]
    boxes = []
    y = HEADER_H + 14
    for label, val in options:
        r = pygame.Rect(MARGIN+6, y, LOG_W - RIGHT_BTN_W - 2*MARGIN - 8, 26)
        rect(surf, r)
        text(surf, f"{label}", r.x+8, r.y+4, sz=16)
        text(surf, f"{val}",   r.right-64, r.y+4, sz=16)
        boxes.append((label, r))
        y += 34

    btns = draw_right_buttons(surf, ["HOME","BACK","NEXT","MENU"])
    return btns, ["HOME","BACK","NEXT","MENU"], boxes

# ------ SPLASH ------
def show_splash(screen, phys):
    img = load_scaled(SPLASH, phys)
    if img:
        screen.blit(img, (0,0)); pygame.display.flip(); pygame.time.wait(3000)

# ------ APP LOOP ------
def main():
    fullscreen = ("--fullscreen" in sys.argv) or ("-f" in sys.argv)
    pygame.init()
    flags = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((800,480), flags)
    pygame.display.set_caption("BMW 2002 OBC")
    info = pygame.display.Info(); phys = (info.current_w, info.current_h)
    logical = pygame.Surface((LOG_W, LOG_H))
    clock = pygame.time.Clock()

    # splash (3s), then proceed
    show_splash(screen, phys)

    logo_sm = load_scaled(SPLASH, (36,36))
    last_btns = []; last_labels = []; menu_boxes = []

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running=False
            elif e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q): running=False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                # map click to logical and hit-test
                lx = int(e.pos[0] * (LOG_W/phys[0])); ly = int(e.pos[1] * (LOG_H/phys[1]))
                # menu option toggles
                if STATE.page == "MENU" and menu_boxes:
                    for label, r in menu_boxes:
                        if r.collidepoint((lx,ly)):
                            if label == "Temp Units": STATE.temp_c = not STATE.temp_c
                            elif label == "Speed Units": STATE.speed_kmh = not STATE.speed_kmh
                # right-rail buttons
                for i, r in enumerate(last_btns):
                    if r.collidepoint((lx,ly)):
                        lab = last_labels[i]
                        if STATE.page == "HOME":
                            if lab in ("VOLT","OIL","TEMP","MENU"): STATE.page = lab
                        else:
                            if lab == "HOME": STATE.page = "HOME"
                            elif lab == "BACK": STATE.page = "HOME"  # simple for now
                            elif lab == "NEXT": STATE.idx = (STATE.idx + 1) % 3  # placeholder
                            elif lab == "MENU": STATE.page = "MENU"

        # draw current page
        if STATE.page == "HOME":
            last_btns, last_labels = draw_home(logical, logo_sm)
            menu_boxes = []
        elif STATE.page == "VOLT":
            last_btns, last_labels = draw_volt(logical)
            menu_boxes = []
        elif STATE.page == "OIL":
            last_btns, last_labels = draw_oil(logical)
            menu_boxes = []
        elif STATE.page == "TEMP":
            last_btns, last_labels = draw_temp(logical)
            menu_boxes = []
        elif STATE.page == "MENU":
            last_btns, last_labels, menu_boxes = draw_menu(logical)

        # upscale + present
        screen.blit(pygame.transform.scale(logical, (800,480)), (0,0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
