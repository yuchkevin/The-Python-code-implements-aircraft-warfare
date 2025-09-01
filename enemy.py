import pygame
from random import *
'''
敌机定义类，分为小型敌机（初始化的时候就是true）、中型敌机、大型敌机'''
#小型敌机（血量少、速度快）
class SmallEnemy(pygame.sprite.Sprite):
    #继承自 pygame.sprite.Sprite（Pygame 精灵类，用于简化游戏元素的碰撞检测和批量处理）
    def __init__(self, bg_size):
        #定义构造方法（初始化方法）
        pygame.sprite.Sprite.__init__(self) #父类的构造方法
    
    #加载小型敌机的正常状态图片
        self.image = pygame.image.load("images/enemy1.png").convert_alpha()
        self.destroy_images = []
        #初始化 self.destroy_images 为空列表，用于存储敌机被击落后的爆炸动画图片
        #这 4 张图片会在敌机被击落后按顺序播放，模拟爆炸效果。
        self.destroy_images.extend([ \
            pygame.image.load("images/enemy1_down1.png").convert_alpha(), \
            pygame.image.load("images/enemy1_down2.png").convert_alpha(), \
            pygame.image.load("images/enemy1_down3.png").convert_alpha(), \
            pygame.image.load("images/enemy1_down4.png").convert_alpha() \
            ])
        #获取图片的矩形区域（pygame.Rect 对象），用于碰撞检测
        self.rect = self.image.get_rect()
        self.width, self.height = bg_size[0], bg_size[1]
        self.speed = 2 #定义敌机的移动速度（垂直方向每秒移动 2 像素，小型敌机速度较快
        self.active = True #自定义的属性，定义敌机的存活状态：True 表示存活（正常显示和移动），False 表示被击落（播放爆炸动画）
        # 控制图片的左边界和上边界，初始位置随机
        self.rect.left, self.rect.top = \
            randint(0, self.width - self.rect.width), \
            randint( -5 * self.height,0)
        #创建碰撞掩码，精确的碰撞掩码
        #因为图片是方正的，但是飞机是不规则的，碰撞的时候要检测碰撞到飞机而不是图片
        #透明像素（背景部分）会被标记为 “碰撞无效”。
        #应该是传入这个就会检测生效
        self.mask = pygame.mask.from_surface(self.image)
    
    #用于更新敌机的位置，实现 “从屏幕上方飞入，
    # 向下移动” 的效果，当敌机飞出屏幕后会重置位置重新进入游戏
    def move(self):  
        if self.rect.top < self.height: # 如果敌机的top小于屏幕高度，则继续移动
            self.rect.top += self.speed # 向下移动 self.speed =2
        else:
            self.reset()
    
    #初始化
    def reset(self):
        self.active = True  #是存活的
        #位置是是随机的
        self.rect.left, self.rect.top = \
            randint(0, self.width - self.rect.width), \
            randint(-5 * self.height, 0)

#
class MidEnemy(pygame.sprite.Sprite):
    energy = 8 #敌机的血量属性的初始化值
    
    def __init__(self, bg_size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/enemy2.png").convert_alpha()
        self.image_hit = pygame.image.load("images/enemy2_hit.png").convert_alpha()
        self.destroy_images = []
        self.destroy_images.extend([ \
            pygame.image.load("images/enemy2_down1.png").convert_alpha(), \
            pygame.image.load("images/enemy2_down2.png").convert_alpha(), \
            pygame.image.load("images/enemy2_down3.png").convert_alpha(), \
            pygame.image.load("images/enemy2_down4.png").convert_alpha() \
            ])
        self.rect = self.image.get_rect()
        self.width, self.height = bg_size[0], bg_size[1]
        self.speed = 1 #中飞机飞的慢一点
        self.active = True
        self.rect.left, self.rect.top = \
            randint(0, self.width - self.rect.width), \
            randint(-10 * self.height, -self.height)
        self.mask = pygame.mask.from_surface(self.image)
        self.energy = MidEnemy.energy
        self.hit = False #被击中状态标记
    
    def move(self): #移动
        if self.rect.top < self.height:
            self.rect.top += self.speed
        else:
            self.reset()
    #初始化
    def reset(self): #重置
        self.active = True
        self.energy = MidEnemy.energy
        self.rect.left, self.rect.top = \
            randint(0, self.width - self.rect.width), \
            randint(-10 * self.height, -self.height)


class BigEnemy(pygame.sprite.Sprite):
    energy = 20
    
    def __init__(self, bg_size):
        pygame.sprite.Sprite.__init__(self)
        
        self.image1 = pygame.image.load("images/enemy3_n1.png").convert_alpha()
        self.image2 = pygame.image.load("images/enemy3_n2.png").convert_alpha()
        self.image_hit = pygame.image.load("images/enemy3_hit.png").convert_alpha()
        self.destroy_images = []
        self.destroy_images.extend([ \
            pygame.image.load("images/enemy3_down1.png").convert_alpha(), \
            pygame.image.load("images/enemy3_down2.png").convert_alpha(), \
            pygame.image.load("images/enemy3_down3.png").convert_alpha(), \
            pygame.image.load("images/enemy3_down4.png").convert_alpha(), \
            pygame.image.load("images/enemy3_down5.png").convert_alpha(), \
            pygame.image.load("images/enemy3_down6.png").convert_alpha() \
            ])
        self.rect = self.image1.get_rect()
        self.width, self.height = bg_size[0], bg_size[1]
        self.speed = 1
        self.active = True
        self.rect.left, self.rect.top = \
            randint(0, self.width - self.rect.width), \
            randint(-15 * self.height, -5 * self.height)
        self.mask = pygame.mask.from_surface(self.image1)
        self.energy = BigEnemy.energy
        self.hit = False
    
    def move(self):
        if self.rect.top < self.height:
            self.rect.top += self.speed
        else:
            self.reset()
    
    def reset(self):
        self.active = True
        self.energy = BigEnemy.energy
        self.rect.left, self.rect.top = \
            randint(0, self.width - self.rect.width), \
            randint(-15 * self.height, -5 * self.height)
