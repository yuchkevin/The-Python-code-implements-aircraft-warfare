import pygame


class Bullet1(pygame.sprite.Sprite):
        #继承自 pygame.sprite.Sprite（Pygame 精灵类，用于简化游戏元素的碰撞检测和批量处理）

    def __init__(self, position):#构造函数
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load("images/bullet1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.speed = 12 #速度
        self.active = False #这些子弹还没被发射，属于 “闲置状态”
        self.mask = pygame.mask.from_surface(self.image)
    
    def move(self):
        self.rect.top -= self.speed
        
        if self.rect.top < 0:
            self.active = False
    
    def reset(self, position): 
        self.rect.left, self.rect.top = position
        self.active = True  #置子弹的 self.active 设为 True，
        #并重置到发射位置（我方飞机枪口），让子弹变为 “有效状态”


class Bullet2(pygame.sprite.Sprite):
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load("images/bullet2.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.speed = 14
        self.active = False
        self.mask = pygame.mask.from_surface(self.image)
    
    def move(self):
        self.rect.top -= self.speed
        
        if self.rect.top < 0:
            self.active = False
    
    def reset(self, position):
        self.rect.left, self.rect.top = position
        self.active = True

