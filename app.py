#!/usr/bin/env python3
# Main entry point for BMW OBC Kiosk (scaffold)

import os, time, pygame

AMBER = (224, 122, 0)
BLACK = (0, 0, 0)
LOGICAL_W, LOGICAL_H = 320, 240

def init_display():
    os.environ.setdefault("SDL_VIDEODRIVER", "kmsdrm")
    pygame.init()
    flags = pygame.FULLSCREEN
    screen = pygame.display.set_mode((0,0), flags)
    info = pygame.display.Info()
    physical = (info.current_w, info.current_h)
    logical = pygame.Surface((LOGICAL_W, LOGICAL_H))
    pygame.mouse.set_visible(False)
    return screen, logical, physical

def main():
    screen, logical, physical = init_display()
    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); return
        logical.fill(BLACK)
        font = pygame.font.Font(None, 24)
        txt = font.render("BMW OBC Scaffold", True, AMBER)
        logical.blit(txt, (40, 100))
        scaled = pygame.transform.scale(logical, physical)
        screen.blit(scaled, (0,0))
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
