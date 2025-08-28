def init_video(fullscreen):
    pygame.font.init()
    drv = os.environ.get("SDL_VIDEODRIVER", "").lower()

    # Force headless if dummy requested
    if drv == "dummy":
        return pygame.Surface((800,480)), "dummy", True

    # Try real backends in order
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

    # Last resort: headless
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    return pygame.Surface((800,480)), "dummy", True
