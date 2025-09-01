import pygame
from random import *

'''
补给类：分为炸弹和子弹两种
1.'''

class Bullet_Supply(pygame.sprite.Sprite):
    def __init__(self, bg_size):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load("images/bullet_supply.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.width, self.height = bg_size[0], bg_size[1] # 背景大小
        self.rect.left, self.rect.bottom = \
            randint(0, self.width - self.rect.width), -100
        self.speed = 5 # 速度
        self.active = False # 补给是否激活，默认情况不激活没有下落
        self.mask = pygame.mask.from_surface(self.image) # 碰撞检测用
    
    def move(self):
        if self.rect.top < self.height:
            self.rect.top += self.speed
        else:
            self.active = False
    
    def reset(self):
        self.active = True  # 补给激活，激活之后才能下落 
        #初始化位置
        self.rect.left, self.rect.bottom = \
            randint(0, self.width - self.rect.width), -100

# 炸弹类
class Bomb_Supply(pygame.sprite.Sprite):
    def __init__(self, bg_size):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load("images/bomb_supply.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.width, self.height = bg_size[0], bg_size[1]
        # 炸弹位置
        self.rect.left, self.rect.bottom = \
            randint(0, self.width - self.rect.width), -100
        self.speed = 5  # 速度
        self.active = False  # 补给是否激活
        self.mask = pygame.mask.from_surface(self.image)
    
    #下落
    def move(self):
        if self.rect.top < self.height:
            self.rect.top += self.speed
        else:
    
            self.active = False
    # 重置补给，或者说激活补给
    def reset(self):
        self.active = True
        self.rect.left, self.rect.bottom = \
            randint(0, self.width - self.rect.width), -100
