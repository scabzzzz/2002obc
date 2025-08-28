#!/usr/bin/env python3
# BMW 2002 OBC – calculator UI (X11 via startx)

import os, sys, time, json, pygame

# ---------- CONFIG ----------
LOG_W, LOG_H = 320, 240
AMBER = (224,122,0); BLACK=(0,0,0)
PROJECT = os.path.dirname(os.path.abspath(__file__))
SPLASH  = os.path.join(PROJECT, "splash.png")
OIL_FILE= os.path.join(PROJECT, "oil.json")

RIGHT_W = 110; MARGIN=6; GUTTER=6; HEADER_H=28
DEFAULT_TEMP_F = 75
FAKE_VOLT="12.5 V"; FAKE_OILTMP="190 °F"; FAKE_COOL="182 °F"

# ---------- STATE ----------
class State:
    def __init__(self):
        self.page="HOME"
        self.temp_c=False
        self.speed_kmh=False
        self.brightness=100      # 0..100 (software dim)
        self.auto_night=True
        self.last_oil_ts=self._load_oil_ts()
    def _load_oil_ts(self):
        try: return json.load(open(OIL_FILE))["last_oil_ts"]
        except Exception:
            ts=int(time.time()); self._save_oil_ts(ts); return ts
    def _save_oil_ts(self,ts):
        try: json.dump({"last_oil_ts":int(ts)}, open(OIL_FILE,"w"))
        except Exception: pass

STATE=State()

# ---------- HELPERS ----------
def font(sz): return pygame.font.Font(None, sz)
def text(surf,s,x,y,sz=18,color=AMBER): surf.blit(font(sz).render(s,True,color),(x,y))
def rect(surf,r,w=1,color=AMBER): pygame.draw.rect(surf,color,r,width=w)
def days_since(ts): return (int(time.time())-int(ts))//86400
def temp_display(f): return f"{round((f-32)*5/9)}°C" if STATE.temp_c else f"{f}°F"
def night_dim_factor():
    if not STATE.auto_night: return STATE.brightness/100
    hhmm=int(time.strftime("%H%M"))
    base=0.6 if (hhmm>=2000 or hhmm<630) else 1.0
    return base*(STATE.brightness/100)

def load_img(path):
    try: return pygame.image.load(path).convert_alpha()
    except Exception: return None

def fit_center(img, phys):
    iw,ih=img.get_size(); pw,ph=phys
    k=min(pw/iw, ph/ih); nw,nh=int(iw*k), int(ih*k)
    surf=pygame.Surface(phys, pygame.SRCALPHA); surf.fill(BLACK)
    surf.blit(pygame.transform.smoothscale(img,(nw,nh)), ((pw-nw)//2,(ph-nh)//2))
    return surf

def right_buttons(surf, labels):
    btns=[]; rx=LOG_W-MARGIN-RIGHT_W
    usable=LOG_H-HEADER_H-3*MARGIN
    h=max(28,(usable//len(labels)))
    y=HEADER_H+MARGIN
    for lab in labels:
        r=pygame.Rect(rx,y,RIGHT_W,h-GUTTER); rect(surf,r)
        s=font(20).render(lab,True,AMBER)
        surf.blit(s,(r.x+(r.w-s.get_width())//2, r.y+(r.h-s.get_height())//2))
        btns.append(r); y+=h
    return btns

# ---------- PAGES ----------
def draw_header(surf, title, logo_topright=False, logo_img=None):
    # title centered
    ts=font(18).render(title,True,AMBER)
    surf.blit(ts, ((LOG_W-RIGHT_W - GUTTER - ts.get_width())//2, MARGIN+4))
    if logo_topright and logo_img:
        surf.blit(logo_img, (LOG_W - MARGIN - RIGHT_W - GUTTER - logo_img.get_width(), MARGIN))

def draw_home(surf, logo_small):
    surf.fill(BLACK)
    # small roundel + "BMW"
    if logo_small: surf.blit(logo_small,(MARGIN,MARGIN))
    text(surf,"BMW", (LOG_W-RIGHT_W - GUTTER - font(18).size("BMW")[0])//2, MARGIN+4, sz=18)

    # time (reduced ~25% from prior huge)
    right_x=LOG_W-MARGIN-RIGHT_W
    time_w=right_x-(MARGIN+GUTTER)
    t=time.strftime("%I:%M%p").lstrip("0")
    text(surf,t, MARGIN+2, HEADER_H+2, sz=58)

    # TEMP | DATE row
    y = HEADER_H + 2 + 54 + 10
    tmp=temp_display(DEFAULT_TEMP_F); dt=time.strftime("%m-%d-%Y")
    text(surf, tmp, MARGIN+6, y, sz=24)
    pygame.draw.line(surf, AMBER, (LOG_W//2, y-2), (LOG_W//2, y+28), 1)
    text(surf, dt, LOG_W//2+8, y, sz=24)

    # OIL counter at very bottom-left
    od=days_since(STATE.last_oil_ts)
    text(surf, f"OIL {od} d", MARGIN+6, LOG_H-18, sz=16)

    labels=["VOLT","OIL","TEMP","MENU"]
    btns=right_buttons(surf, labels)
    return btns, labels

def draw_value_page(surf, title, kv, logo_tr):
    surf.fill(BLACK)
    draw_header(surf, title, logo_topright=True, logo_img=logo_tr)
    pygame.draw.line(surf, AMBER, (MARGIN, HEADER_H-2), (LOG_W-RIGHT_W-GUTTER, HEADER_H-2), 1)
    y=HEADER_H+12
    for k,v in kv:
        text(surf,k,MARGIN+8,y,18); y+=20
        text(surf,v,MARGIN+20,y,28); y+=28
    btns=right_buttons(surf, ["HOME","BACK","MENU"])
    return btns, ["HOME","BACK","MENU"]

def draw_volt(s,a): return draw_value_page(s,"VOLTAGE",[("BATTERY",FAKE_VOLT)],a)
def draw_oil(s,a):
    od=days_since(STATE.last_oil_ts)
    btns,labs=draw_value_page(s,"OIL",[("TEMP",FAKE_OILTMP),("CHANGE (days)",f"{od} d")],a)
    # reset button
    r=pygame.Rect(MARGIN+8, LOG_H-46, LOG_W-RIGHT_W-2*MARGIN-16, 28)
    rect(s,r); text(s,"RESET OIL TIMER", r.x+8, r.y+6, 18)
    return btns,labs,[("RESET",r)]
def draw_temp(s,a): return draw_value_page(s,"TEMPERATURE",[("COOLANT",FAKE_COOL),("AMBIENT",temp_display(DEFAULT_TEMP_F))],a)

def draw_menu(surf, logo_tr):
    surf.fill(BLACK); draw_header(surf,"MENU",logo_topright=True, logo_img=logo_tr)
    pygame.draw.line(surf, AMBER,(MARGIN,HEADER_H-2),(LOG_W-RIGHT_W-GUTTER,HEADER_H-2),1)
    boxes=[]; y=HEADER_H+14

    # temp units
    r1=pygame.Rect(MARGIN+6,y,LOG_W-RIGHT_W-2*MARGIN-8,26); rect(surf,r1)
    text(surf,"Temp Units",r1.x+8,r1.y+4,16); text(surf,"°C" if STATE.temp_c else "°F", r1.right-60,r1.y+4,16)
    boxes.append(("Temp Units",r1)); y+=34

    # speed units
    r2=pygame.Rect(MARGIN+6,y,LOG_W-RIGHT_W-2*MARGIN-8,26); rect(surf,r2)
    text(surf,"Speed Units",r2.x+8,r2.y+4,16); text(surf,"KMH" if STATE.speed_kmh else "MPH", r2.right-60,r2.y+4,16)
    boxes.append(("Speed Units",r2)); y+=34

    # auto night
    r3=pygame.Rect(MARGIN+6,y,LOG_W-RIGHT_W-2*MARGIN-8,26); rect(surf,r3)
    text(surf,"Auto Night",r3.x+8,r3.y+4,16); text(surf,"ON" if STATE.auto_night else "OFF", r3.right-60,r3.y+4,16)
    boxes.append(("Auto Night",r3)); y+=34

    # brightness → opens big slider page
    r4=pygame.Rect(MARGIN+6,y,LOG_W-RIGHT_W-2*MARGIN-8,26); rect(surf,r4)
    text(surf,"Brightness",r4.x+8,r4.y+4,16); text(surf,f"{STATE.brightness:3d}%", r4.right-60,r4.y+4,16)
    boxes.append(("Brightness",r4)); y+=34

    btns=right_buttons(surf, ["HOME","BACK","MENU"])
    return btns, ["HOME","BACK","MENU"], boxes

def draw_brightness(surf, logo_tr):
    surf.fill(BLACK); draw_header(surf,"BRIGHTNESS",logo_topright=True, logo_img=logo_tr)
    pygame.draw.line(surf, AMBER,(MARGIN,HEADER_H-2),(LOG_W-RIGHT_W-GUTTER,HEADER_H-2),1)

    # Large slider
    bar=pygame.Rect(MARGIN+10, HEADER_H+40, LOG_W-RIGHT_W-2*MARGIN-20, 18)
    rect(surf, bar, 1)
    fillw = int((STATE.brightness/100)*(bar.w-2))
    pygame.draw.rect(surf, AMBER, (bar.x+1, bar.y+1, fillw, bar.h-2))
    text(surf, f"{STATE.brightness:3d}%", bar.x, bar.y-26, 22)

    # tap anywhere on bar to set
    btns=right_buttons(surf, ["HOME","BACK","MENU"])
    return btns, ["HOME","BACK","MENU"], [("BAR",bar)]

# ---------- SPLASH ----------
def show_splash(screen, phys, img):
    if not img: return
    frame = fit_center(img, phys)
    # overlay bold "BMW"
    overlay = font(64).render("BMW", True, AMBER)
    frame.blit(overlay, ((phys[0]-overlay.get_width())//2, (phys[1]-overlay.get_height())//2))
    screen.blit(frame,(0,0)); pygame.display.flip(); pygame.time.wait(3000)

# ---------- MAIN ----------
def main():
    fullscreen = ("--fullscreen" in sys.argv) or ("-f" in sys.argv)
    pygame.init()
    flags = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((800,480), flags)
    pygame.display.set_caption("BMW 2002 OBC")
    info=pygame.display.Info(); phys=(info.current_w,info.current_h)
    logical=pygame.Surface((LOG_W,LOG_H)); clock=pygame.time.Clock()

    splash_img = load_img(SPLASH)
    show_splash(screen, phys, splash_img)

    logo_small = pygame.transform.smoothscale(splash_img,(36,36)) if splash_img else None
    logo_tr    = pygame.transform.smoothscale(splash_img,(28,28)) if splash_img else None

    last_btns=[]; last_labels=[]; menu_boxes=[]; oil_boxes=[]; bright_boxes=[]

    running=True
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.KEYDOWN and e.key in (pygame.K_ESCAPE,pygame.K_q): running=False
            elif e.type==pygame.MOUSEBUTTONDOWN:
                lx=int(e.pos[0]*(LOG_W/phys[0])); ly=int(e.pos[1]*(LOG_H/phys[1]))

                # menu toggles
                if STATE.page=="MENU" and menu_boxes:
                    for label,r in menu_boxes:
                        if r.collidepoint((lx,ly)):
                            if label=="Temp Units": STATE.temp_c=not STATE.temp_c
                            elif label=="Speed Units": STATE.speed_kmh=not STATE.speed_kmh
                            elif label=="Auto Night": STATE.auto_night=not STATE.auto_night
                            elif label=="Brightness": STATE.page="BRIGHTNESS"

                # bright page bar
                if STATE.page=="BRIGHTNESS" and bright_boxes:
                    for label,r in bright_boxes:
                        if label=="BAR" and r.collidepoint((lx,ly)):
                            rel=max(0,min(1,(lx-r.x)/max(1,r.w)))
                            STATE.brightness=int(rel*100)

                # oil reset
                if STATE.page=="OIL" and oil_boxes:
                    for label,r in oil_boxes:
                        if label=="RESET" and r.collidepoint((lx,ly)):
                            STATE.last_oil_ts=int(time.time()); STATE._save_oil_ts(STATE.last_oil_ts)

                # right-rail buttons
                for i,r in enumerate(last_btns):
                    if r.collidepoint((lx,ly)):
                        lab=last_labels[i]
                        if STATE.page=="HOME":
                            if lab in ("VOLT","OIL","TEMP","MENU"): STATE.page=lab
                        else:
                            if lab=="HOME": STATE.page="HOME"
                            elif lab=="BACK": STATE.page="HOME"
                            elif lab=="MENU": STATE.page="MENU"

        # draw
        if STATE.page=="HOME":
            last_btns,last_labels=draw_home(logical,logo_small); menu_boxes=[]; oil_boxes=[]; bright_boxes=[]
        elif STATE.page=="VOLT":
            last_btns,last_labels=draw_volt(logical,logo_tr); menu_boxes=[]; oil_boxes=[]; bright_boxes=[]
        elif STATE.page=="OIL":
            last_btns,last_labels,oil_boxes=draw_oil(logical,logo_tr); menu_boxes=[]; bright_boxes=[]
        elif STATE.page=="TEMP":
            last_btns,last_labels=draw_temp(logical,logo_tr); menu_boxes=[]; oil_boxes=[]; bright_boxes=[]
        elif STATE.page=="MENU":
            last_btns,last_labels,menu_boxes=draw_menu(logical,logo_tr); oil_boxes=[]; bright_boxes=[]
        elif STATE.page=="BRIGHTNESS":
            last_btns,last_labels,bright_boxes=draw_brightness(logical,logo_tr); menu_boxes=[]; oil_boxes=[]

        # present with software dim
        frame=pygame.transform.scale(logical,(800,480))
        dim=night_dim_factor()
        if dim<1.0:
            dark=pygame.Surface((800,480), pygame.SRCALPHA)
            dark.fill((0,0,0,int((1-dim)*255)))
            frame.blit(dark,(0,0))
        screen.blit(frame,(0,0)); pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__=="__main__":
    main()
