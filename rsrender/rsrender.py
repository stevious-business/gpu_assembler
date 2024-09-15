import pygame
from pygame.locals import *

from .tiles import *

class RSRenderObject:
    """Base object to be inherited from"""
    def __init__(self):
        self.children = []
        self.parent = None
        self.root = None
        self.true_xstart, self.true_ystart = (0, 0)
    
    def add_child(self, child):
        self.children.append(child)
    
    def update_all(self):
        self.update()
        for child in self.children:
            child.update_all()
    
    def update(self):
        pass
    
    def draw_all(self, dsp):
        self.draw(dsp)
        for child in self.children:
            child.draw_all(dsp)
    
    def draw(self, dsp):
        pass
    
    def handle_input(self, *arg):
        for child in self.children:
            child.handle_input(*arg)

class RSRootObject(RSRenderObject):
    def __init__(self, dsp, size):
        super().__init__()
        self.root = self
        self.dsp = dsp
        self.numxtiles, self.numytiles = size
        self.tile_size = (self.dsp.get_width()//self.numxtiles, self.dsp.get_height()//self.numytiles)
    
    def update_all(self):
        for child in self.children:
            child.update_all()
    
    def draw_all(self):
        for child in self.children:
            child.draw_all(self.dsp)

class RSRenderPanel(RSRenderObject):
    def __init__(self, parent, box, scale=1):
        super().__init__()
        parent.add_child(self)
        self.parent = parent
        self.root = parent.root
        self.box = box
        self.xstart, self.ystart, self.xtiles, self.ytiles = box
        self.true_xstart = self.parent.true_xstart+self.xstart
        self.true_ystart = self.parent.true_ystart+self.ystart
        self.tile = None
        self.tile_size = (
            self.parent.tile_size[0]*scale,
            self.parent.tile_size[1]*scale
        )
    
    def set_tile(self, tile):
        self.tile = pygame.image.load("rsrender\\resources\\"+tile+".png")
        self.tile = pygame.transform.scale(self.tile, self.tile_size)
    
    def draw_all(self, dsp):
        self.draw(dsp)
        for child in self.children:
            child.draw_all(dsp)
    
    def draw(self, dsp):
        if self.tile:
            for i in range(self.xtiles):
                for j in range(self.ytiles):
                    dsp.blit(self.tile,
                             (self.true_xstart*self.root.tile_size[0]+i*self.tile_size[0],
                              self.true_ystart*self.root.tile_size[1]+j*self.tile_size[1]))

class RSIOPanel(RSRenderPanel):
    def __init__(self, parent, box, *a, **kw):
        super().__init__(parent, box, *a, **kw)
    
    def handle_input(self, *arg):
        mouse_pos = pygame.mouse.get_pos()
        mouse_tile_pos = (mouse_pos[0]//self.root.tile_size[0],
                          mouse_pos[1]//self.root.tile_size[1])
        for child in self.children:
            child.handle_input(mouse_tile_pos)

class RSLampScreen(RSIOPanel):
    def __init__(self, parent, box, *a, **kw):
        super().__init__(parent, box, *a, **kw)
        self.tile_on = pygame.image.load("rsrender\\resources\\"+LAMP_ON+".png")
        self.tile_on = pygame.transform.scale(self.tile_on, self.tile_size)
        self.tile_off = pygame.image.load("rsrender\\resources\\"+LAMP_OFF+".png")
        self.tile_off = pygame.transform.scale(self.tile_off, self.tile_size)
        self.size = (box[2], box[3])
        self.initialize_data()
    
    def initialize_data(self):
        self.num_pixels = self.size[0]*self.size[1]
        self.data = [[False for j in range(self.size[1])] for i in range(self.size[0])]
    
    def set_data(self, x, y, val):
        if self.data[x][y] == 0 and bool(val) and self.num_pixels == 1:
            raise RuntimeError("Done!")
        if self.data[x][y] == 0:
            self.num_pixels -= 1
        self.data[x][y] = bool(val)
    
    def get_data(self, x, y):
        return self.data[x][y]
    
    def draw(self, dsp):
        for i in range(self.xtiles):
            for j in range(self.ytiles):
                if self.get_data(i, j):
                    self.tile = self.tile_on
                else:
                    self.tile = self.tile_off
                
                dsp.blit(self.tile,
                         (self.true_xstart*self.tile_size[0]+i*self.tile_size[0],
                          self.true_ystart*self.tile_size[1]+j*self.tile_size[1]))

class RSIOTile(RSIOPanel):
    def __init__(self, parent, xy, tile_type, *a, **kw):
        super().__init__(parent, (xy[0], xy[1], 1, 1), *a, **kw)
        def random_func(*arg, **kw): return
        self.trigger_func = random_func
        self.trigger_args = []
        self.trigger_kwargs = {}
        self.state = 0
        self.tile_type = tile_type
    
    def set_trigger(self, func, args, kwargs):
        self.trigger_func, self.trigger_args, self.trigger_kwargs = func, args, kwargs
    
    def get_state(self):
        return self.state
    
    def handle_input(self, mouse_tile_pos):
        size_in_tiles = (
            self.tile_size[0]//self.root.tile_size[0],
            self.tile_size[1]//self.root.tile_size[1]
        )
        if self.true_xstart <= mouse_tile_pos[0] < self.true_xstart+size_in_tiles[0] and self.true_ystart <= mouse_tile_pos[1] < self.true_ystart+size_in_tiles[1]: # clicked
            if self.tile_type in (BUTTON_TYPE, LEVER_TYPE):
                self.trigger()
    
    def trigger(self):
        if self.tile_type == LEVER_TYPE:
            self.state = int(not bool(self.state))
        self.trigger_func(*self.trigger_args, **self.trigger_kwargs)
    
    def draw(self, dsp):
        if self.tile_type == BUTTON_TYPE:
            self.tile = BUTTON
        elif self.tile_type == LEVER_TYPE:
            if self.get_state():
                self.tile = LEVER_ON
            else:
                self.tile = LEVER_OFF
        elif self.tile_type == LAMP_TYPE:
            if self.get_state():
                self.tile = LAMP_ON
            else:
                self.tile = LAMP_OFF
        
        self.tile = pygame.image.load("rsrender\\resources\\"+self.tile+".png")
        self.tile = pygame.transform.scale(self.tile, self.tile_size)
        
        dsp.blit(self.tile,
                 (self.true_xstart*self.root.tile_size[0],
                  self.true_ystart*self.root.tile_size[1]))
