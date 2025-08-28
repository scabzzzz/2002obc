#!/usr/bin/env python3
# BMW 2002 OBC – calc style, startx-friendly (Clock toggle: digital/analog)

import os, sys, time, json, math, pygame

# ---------- CONFIG ----------
LOG_W, LOG_H = 320, 240
AMBER=(224,122,0); BLACK=(0,0,0)
PROJECT=os.path.dirname(os.path.abspath(__file__))
SPLASH=os.path.join(PROJECT,"splash.png")
OIL_FILE=os.path.join(PROJECT,"oil.json")
CLOCK_FONT=os.path.join(PROJECT,"assets/fonts/PressStart2P-Regular.ttf")  # optional calc font

RIGHT_W=110; MARGIN=6; GUTTER=6; HEADER_H=28
DEFAULT_TEMP_F=75
FAKE_VOLT="12.5 V"; FAKE_OILTMP="190 °F"; FAKE_COOL="182 °F"

# ---------- STATE ----------
class State:
    def __init__(self):
        self.page="HOME"
        self.temp_c=False
        self.speed_kmh=False
        self.brightness=100
        self.auto_night=True
        self.clock_mode="digital"     # "digital" or "analog"
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
def font_calc(sz):
    try:
        return pygame.font.Font(CLOCK_FONT, sz) if os.path.exists(CLOCK_FONT) else pygame.font.Font(None, sz)
    except Exception:
        return pygame.font.Font(None, sz)
def text(surf,s,x,y,sz=18,color=AMBER,calc=False):
    f=font_calc(sz) if calc else font(sz); surf.blit(f.render(s,True,color),(x,y))
def rect(surf,r,w=1,color=AMBER): pygame.draw.rect(surf,color,r,width=w)
def days_since(ts): return (int(time.time())-int(ts))//86400
def temp_display(f): return f"{round((f-32)*5/9)}°C" if STATE.temp_c else f"{f}°F"
def night_dim_factor():
    if not STATE.auto_night: return STATE.brightness/100
    hhmm=int(time.strftime("%H%M")); base=0.6 if (hhmm>=2000 or hhmm<630) else 1.0
    return base*(STATE.brightness/100)
def load_img(path):
    try: return pygame.image.load(path).convert_alpha()
    except Exception: return None
def fit_center_percent(img, phys, percent=0.70):
    iw,ih=img.get_size(); pw,ph=phys
    k=min(pw/iw, ph/ih)*percent; nw,nh=int(iw*k), int(ih*k)
    surf=pygame.Surface(phys, pygame.SRCALPHA); surf.fill(BLACK)
    surf.blit(pygame.transform.smoothscale(img,(nw,nh)), ((pw-nw)//2,(ph-nh)//2)); return surf
def right_buttons(surf, labels):
    btns=[]; rx=LOG_W-MARGIN-RIGHT_W; usable=LOG_H-HEADER_H-3*MARGIN
    h=max(28,(usable//len(labels))); y=HEADER_H+MARGIN
    for lab in labels:
        r=pygame.Rect(rx,y,RIGHT_W,h-GUTTER); rect(surf,r)
        s=font(20).render(lab,True,AMBER)
        surf.blit(s,(r.x+(r.w-s.get_width())//2, r.y+(r.h-s.get_height())//2))
        btns.append(r); y+=h
    return btns

# ---------- ANALOG CLOCK ----------
def draw_analog_clock(surf, cx, cy, r):
    # ticks
    for i in range(60):
        ang = math.radians(i*6 - 90)
        inner = r-6 if i % 5 else r-10
        x1 = cx + int(math.cos(ang)*inner)
        y1 = cy + int(math.sin(ang)*inner)
        x2 = cx + int(math.cos(ang)*r)
        y2 = cy + int(math.sin(ang)*r)
        pygame.draw.line(surf, AMBER, (x1,y1), (x2,y2), 1 if i%5 else 2)
    # hands
    t = time.localtime()
    sec = t.tm_sec
    minute = t.tm_min + sec/60.0
    hour = (t.tm_hour%12) + minute/60.0
    def hand(angle_deg, length, width):
        a = math.radians(angle_deg - 90)
        x = cx + int(math.cos(a)*length)
        y = cy + int(math.sin(a)*length)
        pygame.draw.line(surf, AMBER, (cx,cy), (x,y), width)
    hand(hour*30,   int(r*0.55), 3)
    hand(minute*6,  int(r*0.75), 2)
    hand(sec*6,     int(r*0.85), 1)

# ---------- HEADERS ----------
def draw_header_center_logo(surf, title, logo_img):
    content_w=LOG_W-RIGHT_W-GUTTER-2*MARGIN; content_x=MARGIN
    if logo_img:
        lx=content_x+(content_w-logo_img.get_width())//2; surf.blit(logo_img,(lx,MARGIN))
    ts=font(16).render(title,True,AMBER)
    tx=content_x+(content_w-ts.get_width())//2
    surf.blit(ts,(tx, MARGIN+(logo_img.get_height()+2 if logo_img else 4)))
    pygame.draw.line(surf,AMBER,(MARGIN,HEADER_H-2),(LOG_W-RIGHT_W-GUTTER,HEADER_H-2),1)

# ---------- PAGES ----------
def draw_home(surf, logo_small):
    surf.fill(BLACK)
    if logo_small: surf.blit(logo_small,(MARGIN,MARGIN))
    text(surf,"BMW",(LOG_W-RIGHT_W - GUTTER - font(18).size("BMW")[0])//2, MARGIN+4, sz=18)

    # Clock area (left)
    if STATE.clock_mode == "analog":
        avail_w = LOG_W - RIGHT_W - GUTTER - 2*MARGIN
        cx = MARGIN + avail_w//2
        cy = LOG_H//2 - 8
        r  = min(avail_w, LOG_H//2) // 2
        draw_analog_clock(surf, cx, cy, r)
        y_base = cy + r + 6
    else:
        # digital (compact, left-aligned)
        t_str = time.strftime("%I:%M%p").lstrip("0")
        time_sz = 18
        time_x  = MARGIN + 2
        time_y  = LOG_H//2 - 15
        text(surf, t_str, time_x, time_y, sz=time_sz, calc=True)
        y_base = time_y + time_sz + 6

    # TEMP | DATE (no year), near the clock
    tmp = temp_display(DEFAULT_TEMP_F)
    f24 = font(24); tmp_w = f24.size(tmp)[0]
    text(surf, tmp, MARGIN+6, y_base, sz=24)
    px = MARGIN+6 + tmp_w + 10
    pygame.draw.line(surf, AMBER, (px, y_base-2), (px, y_base+28), 1)
    dt = time.strftime("%m-%d")
    text(surf, dt, px+8, y_base, sz=24)

    # OIL counter bottom-left
    od=days_since(STATE.last_oil_ts); text(surf,f"OIL {od} d",MARGIN+6,LOG_H-18,sz=16)

    labels=["VOLT","OIL","TEMP","MENU"]; btns=right_buttons(surf,labels)
    return btns, labels

def draw_value_page(surf, title, kv, logo_center):
    surf.fill(BLACK); draw_header_center_logo(surf,title,logo_center)
    y=HEADER_H+12
    for k,v in kv:
        text(surf,k,MARGIN+8,y,18); y+=20
        text(surf,v,MARGIN+20,y,28); y+=28
    btns=right_buttons(surf,["HOME","BACK","MENU"])
    return btns,["HOME","BACK","MENU"]

def draw_volt(s,a): return draw_value_page(s,"VOLTAGE",[("BATTERY",FAKE_VOLT)],a)
def draw_oil(s,a):
    od=days_since(STATE.last_oil_ts)
    btns,labs=draw_value_page(s,"OIL",[("TEMP",FAKE_OILTMP),("CHANGE (days)",f"{od} d")],a)
    r=pygame.Rect(MARGIN+8,LOG_H-46,LOG_W-RIGHT_W-2*MARGIN-16,28)
    rect(s,r); text(s,"RESET OIL TIMER",r.x+8,r.y+6,18)
    return btns,labs,[("RESET",r)]
def draw_temp(s,a): return draw_value_page(s,"TEMPERATURE",[("COOLANT",FAKE_COOL),("AMBIENT",temp_display(DEFAULT_TEMP_F))],a)

def draw_menu(surf, logo_center):
    surf.fill(BLACK); draw_header_center_logo(surf,"MENU",logo_center)
    boxes=[]; y=HEADER_H+14
    def opt(label,value):
        nonlocal y
        r=pygame.Rect(MARGIN+6,y,LOG_W-RIGHT_W-2*MARGIN-8,26); rect(surf,r)
        text(surf,label,r.x+8,r.y+4,16); text(surf,value,r.right-72,r.y+4,16)
        boxes.append((label,r)); y+=34
    opt("Temp Units","°C" if STATE.temp_c else "°F")
    opt("Speed Units","KMH" if STATE.speed_kmh else "MPH")
    opt("Auto Night","ON" if STATE.auto_night else "OFF")
    opt("Clock Style","ANALOG" if STATE.clock_mode=="analog" else "DIGITAL")
    opt("Brightness",f"{STATE.brightness:3d}%")  # opens big slider page
    btns=right_buttons(surf,["HOME","BACK","MENU"])
    return btns,["HOME","BACK","MENU"],boxes

def draw_brightness(surf, logo_center):
    surf.fill(BLACK); draw_header_center_logo(surf,"BRIGHTNESS",logo_center)
    bar=pygame.Rect(MARGIN+10,HEADER_H+40,LOG_W-RIGHT_W-2*MARGIN-20,18)
    rect(surf,bar,1); fillw=int((STATE.brightness/100)*(bar.w-2))
    pygame.draw.rect(surf,AMBER,(bar.x+1,bar.y+1,fillw,bar.h-2))
    text(surf,f"{STATE.brightness:3d}%",bar.x,bar.y-26,22)
    btns=right_buttons(surf,["HOME","BACK","MENU"])
    return btns,["HOME","BACK","MENU"],[("BAR",bar)]

# ---------- SPLASH ----------
def show_splash(screen, phys, img):
    if not img: return
    frame=fit_center_percent(img,phys,percent=0.70)
    lbl=font_calc(48).render("BMW",True,AMBER)
    frame.blit(lbl,((phys[0]-lbl.get_width())//2,phys[1]-lbl.get_height()-20))
    screen.blit(frame,(0,0)); pygame.display.flip(); pygame.time.wait(3000)

# ---------- MAIN ----------
def main():
    fullscreen=("--fullscreen" in sys.argv) or ("-f" in sys.argv)
    pygame.init(); flags=pygame.FULLSCREEN if fullscreen else 0
    screen=pygame.display.set_mode((800,480),flags); pygame.display.set_caption("BMW 2002 OBC")
    info=pygame.display.Info(); phys=(info.current_w,info.current_h)
    logical=pygame.Surface((LOG_W,LOG_H)); clock=pygame.time.Clock()

    splash_img=load_img(SPLASH); show_splash(screen,phys,splash_img)
    logo_small=pygame.transform.smoothscale(splash_img,(36,36)) if splash_img else None
    logo_center=pygame.transform.smoothscale(splash_img,(24,24)) if splash_img else None

    last_btns=[]; last_labels=[]; menu_boxes=[]; oil_boxes=[]; bright_boxes=[]

    running=True
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.KEYDOWN and e.key in (pygame.K_ESCAPE,pygame.K_q): running=False
            elif e.type==pygame.MOUSEBUTTONDOWN:
                lx=int(e.pos[0]*(LOG_W/phys[0])); ly=int(e.pos[1]*(LOG_H/phys[1]))

                if STATE.page=="MENU" and menu_boxes:
                    for label,r in menu_boxes:
                        if r.collidepoint((lx,ly)):
                            if label=="Temp Units": STATE.temp_c=not STATE.temp_c
                            elif label=="Speed Units": STATE.speed_kmh=not STATE.speed_kmh
                            elif label=="Auto Night": STATE.auto_night=not STATE.auto_night
                            elif label=="Clock Style": STATE.clock_mode = ("digital" if STATE.clock_mode=="analog" else "analog")
                            elif label=="Brightness": STATE.page="BRIGHTNESS"

                if STATE.page=="BRIGHTNESS" and bright_boxes:
                    for _,r in bright_boxes:
                        if r.collidepoint((lx,ly)):
                            rel=max(0,min(1,(lx-r.x)/max(1,r.w))); STATE.brightness=int(rel*100)

                if STATE.page=="OIL" and oil_boxes:
                    for label,r in oil_boxes:
                        if label=="RESET" and r.collidepoint((lx,ly)):
                            STATE.last_oil_ts=int(time.time()); STATE._save_oil_ts(STATE.last_oil_ts)

                for i,r in enumerate(last_btns):
                    if r.collidepoint((lx,ly)):
                        lab=last_labels[i]
                        if STATE.page=="HOME":
                            if lab in ("VOLT","OIL","TEMP","MENU"): STATE.page=lab
                        else:
                            if lab=="HOME": STATE.page="HOME"
                            elif lab=="BACK": STATE.page = "MENU" if STATE.page=="BRIGHTNESS" else "HOME"
                            elif lab=="MENU": STATE.page="MENU"

        if STATE.page=="HOME":
            last_btns,last_labels=draw_home(logical,logo_small); menu_boxes=[]; oil_boxes=[]; bright_boxes=[]
        elif STATE.page=="VOLT":
            last_btns,last_labels=draw_volt(logical,logo_center); menu_boxes=[]; oil_boxes=[]; bright_boxes=[]
        elif STATE.page=="OIL":
            last_btns,last_labels,oil_boxes=draw_oil(logical,logo_center); menu_boxes=[]; bright_boxes=[]
        elif STATE.page=="TEMP":
            last_btns,last_labels=draw_temp(logical,logo_center); menu_boxes=[]; oil_boxes=[]; bright_boxes=[]
        elif STATE.page=="MENU":
            last_btns,last_labels,menu_boxes=draw_menu(logical,logo_center); oil_boxes=[]; bright_boxes=[]
        elif STATE.page=="BRIGHTNESS":
            last_btns,last_labels,bright_boxes=draw_brightness(logical,logo_center); menu_boxes=[]; oil_boxes=[]

        frame=pygame.transform.scale(logical,(800,480))
        dim=night_dim_factor()
        if dim<1.0:
            dark=pygame.Surface((800,480), pygame.SRCALPHA)
            dark.fill((0,0,0,int((1-dim)*255))); frame.blit(dark,(0,0))
        screen.blit(frame,(0,0)); pygame.display.flip(); clock.tick(30)

    pygame.quit()

if __name__=="__main__":
    main()
