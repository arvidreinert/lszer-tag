from operator import index
from screeninfo import get_monitors
import pygame, sys,random, math

#initialyse the module:
ip = input("address: ")
pygame.init()
pygame.joystick.init()
my_screens = get_monitors()
width,height = (my_screens[0].width-100,my_screens[0].height-100)
SW,SH = width/1720,height/1000
screen = pygame.display.set_mode((width,height))
#, pygame.SRCALPHA
surface = pygame.Surface((width, height), pygame.SRCALPHA)
clock = pygame.time.Clock()

#a class for handling sprite sheets:
class SpriteSheet:

    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()
        print("initialysed")

    def image_at(self, rectangle, colorkey=None):
        rect = pygame.Rect(rectangle)
        #,pygame.SRCALPHA
        image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image


    def images_load(self, rects, colorkey = None):
        return [self.image_at(rect, colorkey) for rect in rects]