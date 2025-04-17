from setup import *
import pygame

class Rectangle():
    def __init__(self, size, position, color, image=None):
        self.image_path = image
        self.rotation = 0
        self.is_updating = True
        self.size = size
        self.position = position
        self.transparency = 255
        self.color = color
        
        if not image:
            self.original_rect = pygame.Surface(size)
            self.original_rect.fill(self.color)
            self.original_rect.set_alpha(self.transparency)
            self.rect = self.original_rect.copy()
            self.rect_rect = self.rect.get_rect(center=position)
        else:
            self.original_image = pygame.image.load(image).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, size)
            self.original_image.set_alpha(self.transparency)
            self.image = self.original_image.copy()
            self.image_rect = self.image.get_rect(center=position)
            self.image_rect.center = position
            mask = pygame.mask.from_surface(self.image)
            bounding_rects = mask.get_bounding_rects()
            if bounding_rects: 
                self.image = self.image.subsurface(bounding_rects[0])
        
    def update(self, surface):
        if self.is_updating:
            if self.image_path is not None:
                self.image_rect = self.image.get_rect(center=self.position)
                surface.blit(self.image, self.image_rect)
            else:
                self.rect_rect = self.rect.get_rect(center=self.position)
                surface.blit(self.rect, self.rect_rect)
        
    def set_transparency(self, transparency):
        self.transparency = transparency
        if self.image_path is not None:
            self.original_image.set_alpha(transparency)
            self.image.set_alpha(transparency)
        else:
            self.original_rect.set_alpha(transparency)
            self.rect.set_alpha(transparency)
            
    def set_image(self,image):
        self.original_image = pygame.image.load(image).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, self.size)
        self.original_image.set_alpha(self.transparency)
        self.image = self.original_image.copy()

    def set_position(self, xc, yc):
        self.position = (xc, yc)
        if self.image_path is not None:
            self.image_rect.center = self.position
            mask = pygame.mask.from_surface(self.image)
            bounding_rects = mask.get_bounding_rects()
            if bounding_rects: 
                self.image = self.image.subsurface(bounding_rects[0])
        else:
            self.rect_rect.center = self.position

    def change_position(self, xc, yc):
        self.position = (self.position[0] + xc, self.position[1] + yc)
        if self.image_path is not None:
            self.image_rect.center = self.position
            mask = pygame.mask.from_surface(self.image)
            bounding_rects = mask.get_bounding_rects()
            if bounding_rects: 
                self.image = self.image.subsurface(bounding_rects[0])
        else:
            self.rect_rect.center = self.position

    def kill(self):
        self.is_updating = False

    def change_rotation(self, rot):
        self.rotation += rot
        if self.image_path is not None:
            self.image = self.original_image
            self.image = pygame.transform.rotate(self.original_image, 0)
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            self.image_rect = self.image.get_rect(center=self.position)
            mask = pygame.mask.from_surface(self.image)
            bounding_rects = mask.get_bounding_rects()
            if bounding_rects: 
                self.image = self.image.subsurface(bounding_rects[0])
        else:
            self.rect = self.original_rect
            self.rect = pygame.transform.rotate(self.original_rect, 0)
            self.rect = pygame.transform.rotate(self.original_rect, self.rotation)
            self.rect_rect = self.rect.get_rect(center=self.position)

    def set_rotation(self,rot):
        self.rotation = rot
        if self.image_path is not None:
            self.image = self.original_image
            self.image = pygame.transform.rotate(self.original_image, 0)
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            mask = pygame.mask.from_surface(self.image)
            bounding_rects = mask.get_bounding_rects()
            if bounding_rects: 
                self.image = self.image.subsurface(bounding_rects[0])

        else:
            self.rect = self.original_rect
            self.rect = pygame.transform.rotate(self.original_rect, 0)
            self.rect = pygame.transform.rotate(self.original_rect, self.rotation)
            self.rect_rect = self.rect.get_rect(center=self.position)
            
    def get_pos(self):
        return self.position

    def get_point_collide(self, point):
        if self.image_path is not None:
            return self.image_rect.collidepoint(point)
        else:
            return self.rect_rect.collidepoint(point)
        
    def get_colliding_with(self, colrect):
        if self.image_path is not None:
            return self.image_rect.colliderect(colrect.image_rect if colrect.image_path is not None else colrect.rect_rect)
        else:
            return self.rect_rect.colliderect(colrect.rect_rect if colrect.image_path is None else colrect.image_rect)
        
    def return_perfect_colission(self,other_rectangle):
        my_mask = pygame.mask.from_surface(self.image)
        other_mask = pygame.mask.from_surface(other_rectangle.image)
        mp = self.image_rect.topleft
        op = other_rectangle.image_rect.topleft
        x_offset = op[0]-mp[0]
        y_offset = op[1]-mp[1]
        overlap = my_mask.overlap(other_mask,(x_offset,y_offset))
        return overlap != None
    
    def move_towards(self, steps,move=False):
        z = math.radians(-self.rotation+90)
        x = steps * math.cos(z)
        y = steps * math.sin(z)
        m = (-x, -y)
        if move:
            self.change_position(m[0],m[1])
        return m

    def dist_to(self,point):
        po = self.get_pos()
        xdist = point[0]-po[0]
        ydist = point[1]-po[1]
        dist = math.sqrt(xdist*xdist+ydist*ydist)
        return dist

    def point_towards(self,point):
        x0,y0 = self.position
        x1,y1 = point
        x = math.degrees(math.atan2(y1-y0, x1-x0))
        self.set_rotation(-x-90)