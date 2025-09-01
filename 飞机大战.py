# main.py
import pygame #引入的依赖库
import sys    #sys 是 Python 标准库中的一个模块，提供了与 Python 解释器及其环境交互的功能
import traceback
import myplane
import enemy
import bullet
import supply

from pygame.locals import *
from random import *

'''
是 Pygame 库的初始化函数
在使用 Pygame 开发任何程序时，必须首先调用该函数，
否则后续的 Pygame 功能（如创建窗口、加载图像、处理输入）都无法正常工作
重复调用无害
'''
pygame.init()
success, failure = pygame.init()
print(f"成功初始化 {success} 个模块，失败 {failure} 个模块")
pygame.mixer.init()
'''是 Pygame 中专门用于初始化音频混合器模块的函数，
负责启动 Pygame 的声音处理功能，包括背景音乐播放、音效处理等'''

bg_size = width, height = 480, 700
print(f"游戏窗口大小 {width} x {height}")
print(f"bg_size,{bg_size}") #(480, 700)
screen = pygame.display.set_mode(bg_size)  #初始化一个窗口
pygame.display.set_caption("飞机大战 -- FishC Demo") #设置游戏窗口标题

background = pygame.image.load("images/background.png").convert()  #加载背景图片

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 载入游戏音乐
pygame.mixer.music.load("sound/game_music.ogg")  #加载游戏背景音乐
pygame.mixer.music.set_volume(0.2)  #设置音量
bullet_sound = pygame.mixer.Sound("sound/bullet.wav") 
'''
加载一个音效文件
返回一个音效对象，后续可以控制这个音效的相关属性和行为 大小 播放和音量等等'''
bullet_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound("sound/use_bomb.wav")
bomb_sound.set_volume(0.2) #爆炸音效
supply_sound = pygame.mixer.Sound("sound/supply.wav") #补给包音效
supply_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav") #获得炸弹音效
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_bullet.wav") #
get_bullet_sound.set_volume(0.2)
upgrade_sound = pygame.mixer.Sound("sound/upgrade.wav")
upgrade_sound.set_volume(0.2)
enemy3_fly_sound = pygame.mixer.Sound("sound/enemy3_flying.wav")
enemy3_fly_sound.set_volume(0.2)
enemy1_down_sound = pygame.mixer.Sound("sound/enemy1_down.wav")
enemy1_down_sound.set_volume(0.2)
enemy2_down_sound = pygame.mixer.Sound("sound/enemy2_down.wav")
enemy2_down_sound.set_volume(0.2)
enemy3_down_sound = pygame.mixer.Sound("sound/enemy3_down.wav")
enemy3_down_sound.set_volume(0.5)
me_down_sound = pygame.mixer.Sound("sound/me_down.wav")
me_down_sound.set_volume(0.2)

#这个应该是添加小型敌机的函数，bg_size 全局变量直接用是吗？
def add_small_enemies(group1, group2, num):
    for i in range(num):
        #生成小飞机
        e1 = enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)

#这个应该是添加中型敌机的函数 
def add_mid_enemies(group1, group2, num):
    for i in range(num):
        e2 = enemy.MidEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)

#这个应该是添加大型敌机的函数
def add_big_enemies(group1, group2, num):
    for i in range(num):
        e3 = enemy.BigEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)

#加速度
def inc_speed(target, inc):
    for each in target:
        each.speed += inc

#主函数不会主动执行，还是需要手动调用
def main():
    # 播放背景音乐，-1 表示循环播放
    pygame.mixer.music.play(-1)

    # 生成我方飞机
    me = myplane.MyPlane(bg_size)
    
    # 3. 初始化敌机精灵组   是用来存放敌机的？?????x
    enemies = pygame.sprite.Group()
    
    # 这个是定义小飞机组
    small_enemies = pygame.sprite.Group()
    
    # 生成敌方小型飞机 ，放在小飞机组和飞机组
    add_small_enemies(small_enemies, enemies, 15)
    
    # 生成敌方中型飞机
    mid_enemies = pygame.sprite.Group()
    add_mid_enemies(mid_enemies, enemies, 4)
    
    # 生成敌方大型飞机
    big_enemies = pygame.sprite.Group()
    add_big_enemies(big_enemies, enemies, 2)
    
    # 生成普通子弹
    bullet1 = []
    bullet1_index = 0
    BULLET1_NUM = 4
    for i in range(BULLET1_NUM):
        bullet1.append(bullet.Bullet1(me.rect.midtop)) #子弹位置设为我方飞机位置的中上方
    
    # 生成超级子弹
    bullet2 = []
    bullet2_index = 0
    BULLET2_NUM = 8
    for i in range(BULLET2_NUM // 2): #// 整数除法，向下取整，类似于java的两个整数相除
        bullet2.append(bullet.Bullet2((me.rect.centerx - 33, me.rect.centery)))
        bullet2.append(bullet.Bullet2((me.rect.centerx + 30, me.rect.centery)))
        #一次循环是生成两个子弹对象 ，一个在左一个在右
    
    clock = pygame.time.Clock() #会创建一个 时钟对象，用于控制游戏的刷新频率
    
    # 中弹图片索引
    e1_destroy_index = 0
    e2_destroy_index = 0
    e3_destroy_index = 0
    me_destroy_index = 0
    
    # 统计得分
    score = 0
    score_font = pygame.font.Font("font/font.ttf", 36)   #加载字体
    
    
    paused = False# 标志是否暂停游戏
    pause_nor_image = pygame.image.load("images/pause_nor.png").convert_alpha() #暂停按钮
    pause_pressed_image = pygame.image.load("images/pause_pressed.png").convert_alpha()
    resume_nor_image = pygame.image.load("images/resume_nor.png").convert_alpha()
    resume_pressed_image = pygame.image.load("images/resume_pressed.png").convert_alpha()
    paused_rect = pause_nor_image.get_rect()  #暂停按钮矩形
    paused_rect.left, paused_rect.top = width - paused_rect.width - 10, 10 # 距离左边和上边各10个距离
    paused_image = pause_nor_image
    
    # 设置难度级别
    level = 1
    
    # 全屏炸弹 参数相关设置  参数相关设置
    bomb_image = pygame.image.load("images/bomb.png").convert_alpha()
    bomb_rect = bomb_image.get_rect()
    bomb_font = pygame.font.Font("font/font.ttf", 48)
    bomb_num = 3
    
    # 每30秒发放一个补给包
    bullet_supply = supply.Bullet_Supply(bg_size)
    bomb_supply = supply.Bomb_Supply(bg_size) #超级子弹补给包
    SUPPLY_TIME = USEREVENT   # SUPPLY_TIME = 24  主要是为了区分不同的事件类型
    #Pygame 中用于定时触发自定义事件的核心函数，在你的飞机大战代码中，它的作用是每 30 秒自动生成一个补给包
    pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
    
    # 超级子弹定时器
    DOUBLE_BULLET_TIME = USEREVENT + 1
    
    # 标志是否使用超级子弹
    is_double_bullet = False
    
    # 解除我方无敌状态定时器
    INVINCIBLE_TIME = USEREVENT + 2
    
    # 生命数量   初始3条生命
    life_image = pygame.image.load("images/life.png").convert_alpha()
    life_rect = life_image.get_rect()
    life_num = 3
    
    # 用于阻止重复打开记录文件
    recorded = False
    
    # 游戏结束画面
    gameover_font = pygame.font.Font("font/font.TTF", 48)
    again_image = pygame.image.load("images/again.png").convert_alpha()
    again_rect = again_image.get_rect()
    gameover_image = pygame.image.load("images/gameover.png").convert_alpha()
    gameover_rect = gameover_image.get_rect()
    
    # 用于切换图片
    switch_image = True
    
    # 用于延迟
    delay = 100
    
    running = True
    
    while running: #循环条件
        #是 Pygame 中处理用户输入和系统事件的核心循环结构，
        #用于捕获并处理游戏中发生的所有事件（如键盘按键、鼠标点击、窗口操作等）
        for event in pygame.event.get():
            #触发时机：用户点击窗口右上角的关闭按钮（×）
            if event.type == QUIT: #点击关闭按钮退出游戏
                pygame.quit()
                sys.exit()
            
            elif event.type == MOUSEBUTTONDOWN:
                #Pygame 中规定：1 代表鼠标左键，3 代表鼠标右键，2 代表滚轮点击，用户点击的是鼠标左键
                #并且 点击左键的位置在 暂停按钮矩形范围内
                #collidepoint() 是 Pygame 矩形对象的方法，用于判断一个点是否在矩形内部
                if event.button == 1 and paused_rect.collidepoint(event.pos):
                    #核心作用是反转 “暂停状态” 的布尔值
                    paused = not paused
                    if paused:
                        ## 暂停时：停止补给定时器、暂停背景音乐和所有音效
                        pygame.time.set_timer(SUPPLY_TIME, 0)
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                    else:
                        #这个意思是继续游戏，恢复补给定时器、恢复背景音乐和所有音效
                        pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()
            
            elif event.type == MOUSEMOTION: #鼠标移动事件
                if paused_rect.collidepoint(event.pos):  #切换暂停按钮的图片
                    if paused:
                        paused_image = resume_pressed_image
                    else:
                        paused_image = pause_pressed_image
                else:
                    if paused:
                        paused_image = resume_nor_image
                    else:
                        paused_image = pause_nor_image
            
            elif event.type == KEYDOWN: #键盘按键事件
                if event.key == K_SPACE: # 空格键
                    if bomb_num: #如果有炸弹
                        bomb_num -= 1
                        bomb_sound.play() #音效
                        for each in enemies: 
                            if each.rect.bottom > 0: #碰撞检测相关的条件判断，用于筛选出 “已经进入屏幕内” 的敌机，
                                #底部y轴>0，才会被击中
                                each.active = False
            
            elif event.type == SUPPLY_TIME: # 自定义事件 生成补给包
                supply_sound.play() 
                if choice([True, False]): #随机生成炸弹补给或子弹补给
                    bomb_supply.reset() #激活炸弹补给
                else:
                    bullet_supply.reset() #激活子弹补给
            
            elif event.type == DOUBLE_BULLET_TIME: #超级子弹定时器
                is_double_bullet = False # # 关闭超级子弹模式
                pygame.time.set_timer(DOUBLE_BULLET_TIME, 0) ## 停止该定时器
            
            elif event.type == INVINCIBLE_TIME: #解除我方无敌状态定时器
                me.invincible = False 
                pygame.time.set_timer(INVINCIBLE_TIME, 0)
        
        # 事件处理完成
        # 根据用户的得分增加难度
        if level == 1 and score > 50000:
            level = 2
            upgrade_sound.play()
            # 增加3架小型敌机、2架中型敌机和1架大型敌机
            add_small_enemies(small_enemies, enemies, 3)
            add_mid_enemies(mid_enemies, enemies, 2)
            add_big_enemies(big_enemies, enemies, 1)
            # 提升小型敌机的速度
            inc_speed(small_enemies, 1)
        elif level == 2 and score > 300000:
            level = 3
            upgrade_sound.play()
            # 增加5架小型敌机、3架中型敌机和2架大型敌机
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            # 提升小型敌机的速度
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
        elif level == 3 and score > 600000:
            level = 4
            upgrade_sound.play()
            # 增加5架小型敌机、3架中型敌机和2架大型敌机
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            # 提升小型敌机的速度
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
        elif level == 4 and score > 1000000:
            level = 5
            upgrade_sound.play()
            # 增加5架小型敌机、3架中型敌机和2架大型敌机
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            # 提升小型敌机的速度
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
        #是 Pygame 中用于绘制图像到游戏窗口的核心操作，作用是将背景图片显示在游戏窗口的指定位置。
        screen.blit(background, (0, 0))
        
        #如果还有声明 并且没有停止
        if life_num and not paused:
            # 检测用户的键盘操作
            key_pressed = pygame.key.get_pressed()
            #上下左右移动 飞机
            if key_pressed[K_w] or key_pressed[K_UP]:
                me.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                me.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                me.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                me.moveRight()
            
            # 绘制全屏炸弹补给并检测是否获得
            if bomb_supply.active: #这个已经在上面的事件里面激活了
                bomb_supply.move() #下落
                screen.blit(bomb_supply.image, bomb_supply.rect) #在屏幕上绘制补给包 
                if pygame.sprite.collide_mask(bomb_supply, me): #是 Pygame 提供的像素级精确碰撞检测方法
                    get_bomb_sound.play()
                    if bomb_num < 3:
                        bomb_num += 1
                    bomb_supply.active = False
            
            # 绘制超级子弹补给并检测是否获得
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply, me):
                    get_bullet_sound.play()#播放获取音效，提供听觉反馈
                    is_double_bullet = True  #激活超级子弹模式
                    pygame.time.set_timer(DOUBLE_BULLET_TIME, 18 * 1000) #设置18秒后自动关闭超级子弹模式的定时器
                    bullet_supply.active = False  #关闭补给包 以防下次循环生效
            
            # 发射子弹
            if not (delay % 10): # 整10触发一次发射子弹
                bullet_sound.play()
                if is_double_bullet: # 超级子弹模式
                    bullets = bullet2
                    bullets[bullet2_index].reset((me.rect.centerx - 33, me.rect.centery))
                    bullets[bullet2_index + 1].reset((me.rect.centerx + 30, me.rect.centery))
                    bullet2_index = (bullet2_index + 2) % BULLET2_NUM
                else:
                    bullets = bullet1
                    bullets[bullet1_index].reset(me.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM
            
            # 检测子弹是否击中敌机
            for b in bullets:
                if b.active:
                    b.move() # 移动子弹 
                    screen.blit(b.image, b.rect)
                    #检测单个精灵（这里是子弹 b）与精灵组（这里是所有敌机 enemies）的碰撞
                    enemy_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                    if enemy_hit: # 子弹击中敌机
                        b.active = False # 子弹消失
                        for e in enemy_hit:  
                            if e in mid_enemies or e in big_enemies: # 中型或大型敌机
                                e.hit = True # 标记敌机被击中
                                e.energy -= 1 # 减少敌机的血量
                                if e.energy == 0: # 敌机血量为0
                                    e.active = False
                            else:
                                e.active = False
            
            # 绘制大型敌机
            for each in big_enemies:
                if each.active:
                    each.move()
                    if each.hit:  # 若敌机被击中
                        screen.blit(each.image_hit, each.rect) # 绘制被击中效果
                        each.hit = False # 重置标记
                    else: #没有击中两张图片切换，造成一种飞机在运动的错觉
                        if switch_image: # 切换图片 为什么切换图片？？？？？
                            screen.blit(each.image1, each.rect)
                        else:
                            screen.blit(each.image2, each.rect)
                    
                    # 绘制血槽
                    pygame.draw.line(screen, BLACK, \
                                     (each.rect.left, each.rect.top - 5), \
                                     (each.rect.right, each.rect.top - 5), \
                                     2)
                    # 当生命大于20%显示绿色，否则显示红色
                    energy_remain = each.energy / enemy.BigEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color, \
                                     (each.rect.left, each.rect.top - 5), \
                                     (each.rect.left + each.rect.width * energy_remain, \
                                      each.rect.top - 5), 2)
                    
                    # 即将出现在画面中，播放音效
                    if each.rect.bottom == -50: 
                        enemy3_fly_sound.play(-1)
                else:
                    # 毁灭
                    if not (delay % 3):  # 每3帧更新一次爆炸动画
                        if e3_destroy_index == 0: # 首次进入销毁状态时播放爆炸音效 ？？？？？？？
                            enemy3_down_sound.play()
                            # 绘制当前帧的爆炸图片
                        screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                        e3_destroy_index = (e3_destroy_index + 1) % 6
                        if e3_destroy_index == 0:
                            enemy3_fly_sound.stop()
                            score += 10000
                            each.reset()  # 重置敌机（重新入场）  加分



            
            # 绘制中型敌机：
            for each in mid_enemies:
                if each.active:
                    each.move()
                    
                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        screen.blit(each.image, each.rect)
                    
                    # 绘制血槽
                    pygame.draw.line(screen, BLACK, \
                                     (each.rect.left, each.rect.top - 5), \
                                     (each.rect.right, each.rect.top - 5), \
                                     2)
                    # 当生命大于20%显示绿色，否则显示红色
                    energy_remain = each.energy / enemy.MidEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color, \
                                     (each.rect.left, each.rect.top - 5), \
                                     (each.rect.left + each.rect.width * energy_remain, \
                                      each.rect.top - 5), 2)
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e2_destroy_index == 0:
                            enemy2_down_sound.play()
                        screen.blit(each.destroy_images[e2_destroy_index], each.rect)
                        e2_destroy_index = (e2_destroy_index + 1) % 4
                        if e2_destroy_index == 0:
                            score += 6000
                            each.reset()
            
            # 绘制小型敌机：
            for each in small_enemies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e1_destroy_index == 0:
                            enemy1_down_sound.play()
                        screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                        e1_destroy_index = (e1_destroy_index + 1) % 4
                        if e1_destroy_index == 0:
                            score += 1000
                            each.reset()
            
            # 检测我方飞机是否被撞
            enemies_down = pygame.sprite.spritecollide(me, enemies, False, pygame.sprite.collide_mask)
            if enemies_down and not me.invincible:   # 我方飞机被击中并且不是无敌状态
                me.active = False
                for e in enemies_down:
                    e.active = False  # 敌机消失
            
            # 绘制我方飞机
            if me.active: #也是刷新吗？？？？？
                if switch_image:
                    screen.blit(me.image1, me.rect)
                else:
                    screen.blit(me.image2, me.rect)
            else:
                # 毁灭 ？？？？？？？？？？？？
                if not (delay % 3):
                    if me_destroy_index == 0:
                        me_down_sound.play()
                    screen.blit(me.destroy_images[me_destroy_index], me.rect)
                    me_destroy_index = (me_destroy_index + 1) % 4
                    if me_destroy_index == 0:
                        life_num -= 1
                        me.reset()
                        pygame.time.set_timer(INVINCIBLE_TIME, 3 * 1000)
            
            # 绘制全屏炸弹数量
            bomb_text = bomb_font.render("× %d" % bomb_num, True, WHITE)
            text_rect = bomb_text.get_rect()
            screen.blit(bomb_image, (10, height - 10 - bomb_rect.height)) #位置
            screen.blit(bomb_text, (20 + bomb_rect.width, height - 5 - text_rect.height)) #数量
            
            # 绘制剩余生命数量
            if life_num:
                for i in range(life_num):
                    screen.blit(life_image, \
                                (width - 10 - (i + 1) * life_rect.width, \
                                 height - 10 - life_rect.height))
            
            # 绘制得分
            score_text = score_font.render("Score : %s" % str(score), True, WHITE)
            screen.blit(score_text, (10, 5))
        
        # 绘制游戏结束画面
        elif life_num == 0:
            # 背景音乐停止
            pygame.mixer.music.stop()
            
            # 停止全部音效
            pygame.mixer.stop()
            
            # 停止发放补给
            pygame.time.set_timer(SUPPLY_TIME, 0)
            
            if not recorded:
                recorded = True
                # 读取历史最高得分
                with open("record.txt", "r") as f:
                    record_score = int(f.read())
                
                # 如果玩家得分高于历史最高得分，则存档
                if score > record_score:
                    with open("record.txt", "w") as f:
                        f.write(str(score))
            
            # 绘制结束画面
            record_score_text = score_font.render("Best : %d" % record_score, True, (255, 255, 255))
            screen.blit(record_score_text, (50, 50))
            
            gameover_text1 = gameover_font.render("Your Score", True, (255, 255, 255))
            gameover_text1_rect = gameover_text1.get_rect()
            gameover_text1_rect.left, gameover_text1_rect.top = \
                (width - gameover_text1_rect.width) // 2, height // 3
            screen.blit(gameover_text1, gameover_text1_rect)
            
            gameover_text2 = gameover_font.render(str(score), True, (255, 255, 255))
            gameover_text2_rect = gameover_text2.get_rect()
            gameover_text2_rect.left, gameover_text2_rect.top = \
                (width - gameover_text2_rect.width) // 2, \
                gameover_text1_rect.bottom + 10
            screen.blit(gameover_text2, gameover_text2_rect)
            
            again_rect.left, again_rect.top = \
                (width - again_rect.width) // 2, \
                gameover_text2_rect.bottom + 50
            screen.blit(again_image, again_rect)
            
            gameover_rect.left, gameover_rect.top = \
                (width - again_rect.width) // 2, \
                again_rect.bottom + 10
            screen.blit(gameover_image, gameover_rect)
            
            # 检测用户的鼠标操作
            # 如果用户按下鼠标左键
            if pygame.mouse.get_pressed()[0]:
                # 获取鼠标坐标
                pos = pygame.mouse.get_pos()
                # 如果用户点击“重新开始”
                if again_rect.left < pos[0] < again_rect.right and \
                        again_rect.top < pos[1] < again_rect.bottom:
                    # 调用main函数，重新开始游戏
                    main()
                # 如果用户点击“结束游戏”
                elif gameover_rect.left < pos[0] < gameover_rect.right and \
                        gameover_rect.top < pos[1] < gameover_rect.bottom:
                    # 退出游戏
                    pygame.quit()
                    sys.exit()
                    
                    # 绘制暂停按钮
        screen.blit(paused_image, paused_rect)
        
        # 切换图片
        if not (delay % 5):  # 每5帧切换一次图片
            switch_image = not switch_image
        
        delay -= 1
        if not delay: #delay`=0时，刷新delay=100
            delay = 100
        ## 4. 刷新屏幕，显示所有绘制内容 
        #如果没有这行代码，所有绘制操作只会停留在内存中，屏幕会一直显示初始画面，玩家看不到任何更新
        pygame.display.flip()
        #是 Pygame 中用于控制游戏帧率的核心代码，作用是确保游戏每秒最多刷新 60 次
        clock.tick(60)

#不是一个函数，而是 Python 中的一个条件判断语句，
# #它的作用是判断当前脚本是否被直接运行，从而决定是否执行其内部的代码块
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
