# Weather page stub
from services import weather

def draw(surface, font, color):
    w = weather.get_weather()
    y = 10
    for k,v in w.items():
        surface.blit(font.render(f"{k}: {v}", True, color), (10, y))
        y += 20
