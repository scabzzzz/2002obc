#!/usr/bin/env python3
# BMW 2002 OBC – calculator UI (X11 via startx)

import os, sys, time, json, pygame
from datetime import datetime, timezone

# ----- CONFIG -----
LOG_W, LOG_H = 320, 240
AMBER=(224,122,0); BLACK=(0,0,0)
PROJECT=os.path.dirname(os.path.abspath(__file__))
SPLASH=os.path.join(PROJECT,"splash.png")
OIL_FILE=os.path.join(PROJECT,"oil.json")

RIGHT_BTN_W=110; MARGIN=6; GUTTER=6; HEADER_H=28

DEFAULT_TEMP_F=75
FAKE_VOLT="12.5 V"; FAKE_OILTMP="190 °F"; FAKE_COOL="182 °F"

# ----- STATE -----
class State:
    def __init__(self):
        self.page="HOME"
        self.temp_c=False
        self.speed_kmh=False
        self.idx=0
        self.brightness=100  # 0..100 (software dim)
        self.auto_night=True
        self.last_oil_ts=self.load_oil_ts()

    def load_oil_ts(self):
        try:
            with open(OIL_FILE,"r") as f: return json.load(f)["last_oil_ts"]
        except Exception:
            ts=int(time.time()); self.save_oil_ts(ts); return ts
    def save_oil_ts(self,ts):
        try: json.dump({"last_oil_ts":int(ts)}, open(OIL_FILE,"w"))
        except Exception: pass

STATE=State()

# ----- HELPERS -----
def font(sz): return pygame.font.Font(None, sz)
def text(surf,s,x,y,sz=18,color=AMBER): surf.blit(font(sz).render(s,True,color),(x,y))
def rect(surf,r,w=1,color=AMBER): pygame.draw.rect(surf,color,r,width=w)

def load_scaled(path, size):
    try:
        img=pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img,size)
    except Exception: return None

def scale_to_fit(img, phys):
    iw,ih=img.get_size(); pw,ph=phys
    k=min(pw/iw, ph/ih)
    new=(int(iw*k), int(ih*k))
    return pygame.transform.smoothscale(img,new)

def temp_display(f):
    if STATE.temp_c:
        c=round((f-32)*5/9); return f"{c}°C"
    return f"{f}°F"

def days_since(ts): return (int(time.time())-int(ts))//86400

def night_dim_factor():
    if not STATE.auto_night: return STATE.brightness/100.0
    # Simple schedule: dim from 20:00–06:30 local
    hhmm=int(time.strftime("%H%M"))
    base=0.6 if (hhmm>=2000 or hhmm<630) else 1.0
    return base*(STATE.brightness/100.0)

# ----- BUTTON RAIL -----
def draw_right_buttons(surf, labels):
    btns=[]
    right_x=LOG_W-MARGIN-RIGHT_BTN_W
    usable_h=LOG_H-HEADER_H-3*MARGIN
    btn_h=(usable_h//len(labels))
    y=HEADER_H+MARGIN
    for lab in labels:
        r=pygame.Rect(right_x,y,RIGHT_BTN_W,btn_h-GUTTER)
        rect(surf,r)
        s=font(20).render(lab,True,AMBER)
        surf.blit(s,(r.x+(r.w-s.get_width())//2, r.y+(r.h-s.get_height())//2))
        btns.append(r); y+=btn_h
    return btns

# ----- PAGES -----
def draw_home(surf, logo_sm):
    surf.fill(BLACK)
    # header
    if logo_sm: surf.blit(logo_sm,(MARGIN,MARGIN))
    title="BMW"; ts=font(18).render(title,True,AMBER)
    surf.blit(ts,((LOG_W-ts.get_width())//2,MARGIN+4))

    # big time (reduced ~25%)
    right_x=LOG_W-MARGIN-RIGHT_BTN_W
    time_w=right_x-(MARGIN+GUTTER)
    time_r=pygame.Rect(MARGIN,HEADER_H+8,time_w,60)
    t=time.strftime("%I:%M%p").lstrip("0")
    text(surf,t,time_r.x+2,time_r.y,sz=58)

    # TEMP | DATE (smaller so no overlap)
    row_y=time_r.bottom+16
    tmp=temp_display(DEFAULT_TEMP_F)
    dt=time.strftime("%m-%d-%Y")
    text(surf,tmp,MARGIN+6,row_y,sz=24)
    pygame.draw.line(surf,AMBER,(LOG_W//2,row_y-2),(LOG_W//2,row_y+28),1)
    text(surf,dt,LOG_W//2+8,row_y,sz=24)

    # small oil-days tag under date
    od=days_since(STATE.last_oil_ts)
    text(surf,f"OIL {od} d", LOG_W//2+8, row_y+24, sz=14)

    labels=["VOLT","OIL","TEMP","MENU"]
    btns=draw_right_buttons(surf,labels)
    return btns,labels

def draw_simple_value_page(surf,title,kv_pairs):
    surf.fill(BLACK)
    text(surf,title,(LOG_W-font(18).size(title)[0])//2,MARGIN+4,sz=18)
    pygame.draw.line(surf,AMBER,(MARGIN,HEADER_H-2),(LOG_W-RIGHT_BTN_W-GUTTER,HEADER_H-2),1)
    y=HEADER_H+12
    for label,value in kv_pairs:
        text(surf,label,MARGIN+8,y,sz=18); y+=20
        text(surf,value,MARGIN+20,y,sz=28); y+=28
    btns=draw_right_buttons(surf,["HOME","BACK","NEXT","MENU"])
    return btns,["HOME","BACK","NEXT","MENU"]

def draw_volt(surf): return draw_simple_value_page(surf,"VOLTAGE",[("BATTERY",FAKE_VOLT)])
def draw_oil(surf):
    od=days_since(STATE.last_oil_ts)
    btns,labs=draw_simple_value_page(surf,"OIL",[
        ("TEMP",FAKE_OILTMP),
        ("CHANGE (days since)",f"{od} d"),
    ])
    # Add a RESET button area
    r=pygame.Rect(MARGIN+8, LOG_H-46, LOG_W-RIGHT_BTN_W-2*MARGIN-16, 28)
    rect(surf,r); text(surf,"RESET OIL TIMER", r.x+8, r.y+6, sz=18)
    return btns,labs,[("RESET",r)]
def draw_temp(surf): return draw_simple_value_page(surf,"TEMPERATURE",[("COOLANT",FAKE_COOL),("AMBIENT",temp_display(DEFAULT_TEMP_F))])

def draw_menu(surf):
    surf.fill(BLACK)
    title="MENU"
    text(surf,title,(LOG_W-font(18).size(title)[0])//2,MARGIN+4,sz=18)
    pygame.draw.line(surf,AMBER,(MARGIN,HEADER_H-2),(LOG_W-RIGHT_BTN_W-GUTTER,HEADER_H-2),1)

    boxes=[]
    y=HEADER_H+14

    # Temp Units toggle
    r1=pygame.Rect(MARGIN+6,y,LOG_W-RIGHT_BTN_W-2*MARGIN-8,26); rect(surf,r1)
    text(surf,"Temp Units",r1.x+8,r1.y+4,16); text(surf,"°C" if STATE.temp_c else "°F", r1.right-60,r1.y+4,16)
    boxes.append(("Temp Units",r1)); y+=34

    # Speed Units toggle
    r2=pygame.Rect(MARGIN+6,y,LOG_W-RIGHT_BTN_W-2*MARGIN-8,26); rect(surf,r2)
    text(surf,"Speed Units",r2.x+8,r2.y+4,16); text(surf,"KMH" if STATE.speed_kmh else "MPH", r2.right-60,r2.y+4,16)
    boxes.append(("Speed Units",r2)); y+=34

    # Auto Night toggle
    r3=pygame.Rect(MARGIN+6,y,LOG_W-RIGHT_BTN_W-2*MARGIN-8,26); rect(surf,r3)
    text(surf,"Auto Night",r3.x+8,r3.y+4,16); text(surf,"ON" if STATE.auto_night else "OFF", r3.right-60,r3.y+4,16)
    boxes.append(("Auto Night",r3)); y+=34

    # Brightness slider (software dim)
    r4=pygame.Rect(MARGIN+6,y,LOG_W-RIGHT_BTN_W-2*MARGIN-8,26); rect(surf,r4)
    text(surf,"Brightness",r4.x+8,r4.y+4,16)
    # slider bar
    bar=pygame.Rect(r4.x+110,r4.y+10,r4.w-120,6); pygame.draw.rect(surf,AMBER,bar,1)
    fill_w=int((STATE.brightness/100.0)*(bar.w-2))
    pygame.draw.rect(surf,AMBER, (bar.x+1,bar.y+1,fill_w,bar.h-2))
    boxes.append(("Brightness", bar))
    y+=34

    btns=draw_right_buttons(surf,["HOME","BACK","NEXT","MENU"])
    return btns,["HOME","BACK","NEXT","MENU"],boxes

# ----- SPLASH -----
def show_splash(screen, phys):
    img=load_scaled(SPLASH, phys)
    if img:
        # keep aspect; center; no stretch
        iw,ih=img.get_size()
        if iw!=phys[0] or ih!=phys[1]:
            # rescale preserving AR
            orig=pygame.image.load(SPLASH).convert_alpha()
            fit=scale_to_fit(orig, phys)
            screen.fill(BLACK)
            screen.blit(fit, ((phys[0]-fit.get_width())//2, (phys[1]-fit.get_height())//2))
        else:
            screen.blit(img,(0,0))
        pygame.display.flip(); pygame.time.wait(3000)

# ----- APP LOOP -----
def main():
    fullscreen = ("--fullscreen" in sys.argv) or ("-f" in sys.argv)
    pygame.init()
    flags = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((800,480), flags)
    pygame.display.set_caption("BMW")
    info=pygame.display.Info(); phys=(info.current_w,info.current_h)
    logical=pygame.Surface((LOG_W,LOG_H)); clock=pygame.time.Clock()

    show_splash(screen, phys)
    logo_sm=load_scaled(SPLASH,(36,36))

    last_btns=[]; last_labels=[]; menu_boxes=[]; oil_boxes=[]

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
                        # Brightness drag/step
                        if label=="Brightness" and r.collidepoint((lx,ly)):
                            rel=(lx-r.x)/max(r.w,1); STATE.brightness=max(0,min(100,int(rel*100)))

                if STATE.page=="OIL" and oil_boxes:
                    for label,r in oil_boxes:
                        if label=="RESET" and r.collidepoint((lx,ly)):
                            STATE.last_oil_ts=int(time.time()); STATE.save_oil_ts(STATE.last_oil_ts)

                # right rail buttons
                for i,r in enumerate(last_btns):
                    if r.collidepoint((lx,ly)):
                        lab=last_labels[i]
                        if STATE.page=="HOME":
                            if lab in ("VOLT","OIL","TEMP","MENU"): STATE.page=lab
                        else:
                            if lab=="HOME": STATE.page="HOME"
                            elif lab=="BACK": STATE.page="HOME"
                            elif lab=="NEXT": STATE.idx=(STATE.idx+1)%3
                            elif lab=="MENU": STATE.page="MENU"

        # draw current page
        if STATE.page=="HOME":
            last_btns,last_labels=draw_home(logical,logo_sm); menu_boxes=[]; oil_boxes=[]
        elif STATE.page=="VOLT":
            last_btns,last_labels=draw_volt(logical); menu_boxes=[]; oil_boxes=[]
        elif STATE.page=="OIL":
            last_btns,last_labels,oil_boxes=draw_oil(logical); menu_boxes=[]
        elif STATE.page=="TEMP":
            last_btns,last_labels=draw_temp(logical); menu_boxes=[]; oil_boxes=[]
        elif STATE.page=="MENU":
            last_btns,last_labels,menu_boxes=draw_menu(logical); oil_boxes=[]

        # upscale and software dim
        frame=pygame.transform.scale(logical,(800,480))
        dim = night_dim_factor()
        if dim<1.0:
            # multiply by dim via a translucent black overlay
            dark=pygame.Surface((800,480), pygame.SRCALPHA)
            alpha=int((1.0-dim)*255)
            dark.fill((0,0,0,alpha))
            frame.blit(dark,(0,0))
        screen.blit(frame,(0,0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__=="__main__":
    main()
