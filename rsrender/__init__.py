from . import rsrender
from . import tiles

import pygame
from pygame.locals import *

def run_default_program():
    
    dsp = pygame.display.set_mode((720, 720))
    
    root = rsrender.RSRootObject(dsp, (16, 16))
    
    renderpanel = rsrender.RSRenderPanel(root, (1, 1, 14, 14))
    renderpanel.set_tile(tiles.BLACK)
    
    screenpanel = rsrender.RSLampScreen(renderpanel, (0, 0, 14, 10))
    
    inputpanel = rsrender.RSIOPanel(renderpanel, (1, 11, 12, 2))
    inputpanel.set_tile(tiles.LIME)
    
    lever_show = rsrender.RSIOTile(inputpanel, (0, 0), tiles.LEVER_TYPE)
    ad0 = rsrender.RSIOTile(inputpanel, (2, 0), tiles.LEVER_TYPE)
    ad1 = rsrender.RSIOTile(inputpanel, (4, 0), tiles.LEVER_TYPE)
    ad2 = rsrender.RSIOTile(inputpanel, (6, 0), tiles.LEVER_TYPE)
    
    def set_screen_data():
        screenpanel.set_data(int(ad0.get_state() | ad1.get_state()*2 | ad2.get_state()*4), 0, lever_show.get_state())
    
    lever_show.set_trigger(set_screen_data, (), {})
    ad0.set_trigger(set_screen_data, (), {})
    ad1.set_trigger(set_screen_data, (), {})
    ad2.set_trigger(set_screen_data, (), {})
    
    root.draw_all()
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONDOWN:
                root.handle_input()
        dsp.fill((0, 0, 0))
        root.draw_all()
        pygame.display.update()
        pygame.time.wait(10)
