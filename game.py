import pygame
import myutils 
import myplane 
import bullet
import sys
import supply
from random import choice
# --------------------------- 全局常量定义（统一管理，避免魔法值）---------------------------

# 颜色常量（RGB）
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
# 子弹配置
BULLET1_NUM = 4  # 普通子弹数量
BULLET2_NUM = 8  # 超级子弹数量
BULLET_FIRE_INTERVAL = 10  # 子弹发射间隔（帧）

# 动画配置
IMAGE_SWITCH_INTERVAL = 5  # 飞机图片切换间隔（帧）
EXPLOSION_INTERVAL = 3     # 爆炸动画更新间隔（帧）
DELAY_MAX = 100            # 延迟计数器最大值

# 游戏节奏配置
FPS_LIMIT = 60             # 帧率限制
SUPPLY_INTERVAL = 30 * 1000  # 补给包生成间隔（毫秒）
DOUBLE_BULLET_DURATION = 18 * 1000  # 超级子弹持续时间（毫秒）
INVINCIBLE_DURATION = 3 * 1000      # 无敌状态持续时间（毫秒）

# 难度配置（得分阈值：难度等级 -> (得分阈值, 新增敌机数量, 速度提升值)）
LEVEL_CONFIG = {
    1: (50000, (3, 2, 1), (1, 0, 0)),    # 1→2：得分>5万，加3小/2中/1大，小机速+1
    2: (300000, (5, 3, 2), (1, 1, 0)),   # 2→3：得分>30万，加5小/3中/2大，小+1/中+1
    3: (600000, (5, 3, 2), (1, 1, 0)),   # 3→4：得分>60万，同2→3
    4: (1000000, (5, 3, 2), (1, 1, 0))   # 4→5：得分>100万，同2→3
}
FONT_PATH = "font/font.ttf"

class Game:
    def __init__(self, screen, sounds, images,BG_SIZE):
        self.screen = screen
        self.sounds = sounds
        self.images = images
        self.bg_size= BG_SIZE

        # 精灵组初始化
        self.small_enemies = pygame.sprite.Group()
        self.mid_enemies = pygame.sprite.Group()
        self.big_enemies = pygame.sprite.Group()
        self.all_enemies = pygame.sprite.Group()

        # 子弹初始化（空列表，后续在create_resource中填充）
        self.bullet1 = []
        self.bullet2 = []

        # 游戏状态初始化
        self.clock = pygame.time.Clock()
        self.score = 0
        self.level = 1
        self.bomb_num = 3
        self.life_num = 3
        self.paused = False
        self.recorded = False
        self.is_double_bullet = False
        self.switch_image = True
        self.delay = DELAY_MAX
        # 子弹索引（关键修复：改为实例属性，确保索引能持续累加）
        self.bullet1_index = 0
        self.bullet2_index = 0

        # 动画索引初始化
        self.explosion_indexes = {
            "small": 0, "mid": 0, "big": 0, "me": 0
        }

        # 补给包初始化
        self.bullet_supply = supply.Bullet_Supply(self.bg_size)
        self.bomb_supply = supply.Bomb_Supply(self.bg_size)

        # 定时器初始化（自定义事件）
        self.SUPPLY_EVENT = pygame.USEREVENT
        self.DOUBLE_BULLET_EVENT = pygame.USEREVENT + 1
        self.INVINCIBLE_EVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.SUPPLY_EVENT, SUPPLY_INTERVAL)

        # 字体初始化（避免重复创建）
        self.score_font = pygame.font.Font(FONT_PATH, 36)
        self.bomb_font = pygame.font.Font(FONT_PATH, 48)
        self.gameover_font = pygame.font.Font(FONT_PATH, 48)

        # 暂停按钮配置
        self.pause_rect = self.images["pause_nor"].get_rect()
        self.pause_rect.topleft = (
            self.bg_size[0] - self.pause_rect.width - 10, 10)
        self.pause_image = self.images["pause_nor"]

    def create_resource(self):
        """创建游戏资源：敌机、子弹、背景音乐"""
        # 播放背景音乐   -1 一直播放
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

        # 初始化敌机（初始数量：15小/4中/2大）
        myutils.add_enemies(self.bg_size,
            self.small_enemies, self.mid_enemies, self.big_enemies, self.all_enemies,
            small_num=15, mid_num=4, big_num=2
        )

        # 初始化普通子弹
        self.me = myplane.MyPlane(self.bg_size)  # 我方飞机（需先创建，用于定位子弹）
        for _ in range(BULLET1_NUM):
            self.bullet1.append(bullet.Bullet1(self.me.rect.midtop))

        # 初始化超级子弹（每次循环生成2个，左右各1）
        for _ in range(BULLET2_NUM // 2):
            left_pos = (self.me.rect.centerx - 33, self.me.rect.centery)
            right_pos = (self.me.rect.centerx + 30, self.me.rect.centery)
            self.bullet2.append(bullet.Bullet2(left_pos))
            self.bullet2.append(bullet.Bullet2(right_pos))

    def update_level(self):
        """根据得分更新难度（读取LEVEL_CONFIG，避免多层if-else）"""
        if self.level not in LEVEL_CONFIG:
            return  # 最高难度后不再升级

        score_threshold, add_nums, speed_incs = LEVEL_CONFIG[self.level]
        if self.score > score_threshold:
            self.level += 1
            if self.sounds["upgrade"]:
                self.sounds["upgrade"].play()

            # 新增敌机（add_nums：(小机数量, 中机数量, 大机数量)）
            myutils.add_enemies(self.bg_size,
                self.small_enemies, self.mid_enemies, self.big_enemies, self.all_enemies,
                small_num=add_nums[0], mid_num=add_nums[1], big_num=add_nums[2]
            )

            # 提升敌机速度（speed_incs：(小机增速, 中机增速, 大机增速)）
            myutils.increase_enemy_speed(self.small_enemies, speed_incs[0])
            myutils.increase_enemy_speed(self.mid_enemies, speed_incs[1])
            myutils.increase_enemy_speed(self.big_enemies, speed_incs[2])

    def handle_events(self):
        """事件处理（统一管理键盘/鼠标/定时器事件）"""
        for event in pygame.event.get():
            # 关闭窗口
            if event.type == pygame.QUIT:
                self.quit_game()

            # 鼠标点击（暂停/继续）
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pause_rect.collidepoint(event.pos):
                    self.paused = not self.paused
                    if self.paused:
                        # 暂停：停止定时器+音频
                        pygame.time.set_timer(self.SUPPLY_EVENT, 0)
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                    else:
                        # 继续：恢复定时器+音频
                        pygame.time.set_timer(
                            self.SUPPLY_EVENT, SUPPLY_INTERVAL)
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()

            # 鼠标移动（暂停按钮图片切换）
            elif event.type == pygame.MOUSEMOTION:
                if self.pause_rect.collidepoint(event.pos):
                    self.pause_image = self.images["resume_pressed"] if self.paused else self.images["pause_pressed"]
                else:
                    self.pause_image = self.images["resume_nor"] if self.paused else self.images["pause_nor"]

            # 键盘按键（放炸弹）
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.bomb_num > 0 and not self.paused:
                    self.bomb_num -= 1
                    if self.sounds["use_bomb"]:
                        self.sounds["use_bomb"].play()
                    # 引爆所有屏幕内敌机
                    for enemy_sprite in self.all_enemies:
                        if enemy_sprite.rect.bottom > 0:
                            enemy_sprite.active = False

            # 补给包生成
            elif event.type == self.SUPPLY_EVENT:
                if self.sounds["supply"]:
                    self.sounds["supply"].play()
                # 随机激活炸弹/子弹补给
                if choice([True, False]):
                    self.bomb_supply.reset()
                else:
                    self.bullet_supply.reset()

            # 超级子弹结束
            elif event.type == self.DOUBLE_BULLET_EVENT:
                self.is_double_bullet = False
                pygame.time.set_timer(self.DOUBLE_BULLET_EVENT, 0)

            # 无敌状态结束
            elif event.type == self.INVINCIBLE_EVENT:
                self.me.invincible = False
                pygame.time.set_timer(self.INVINCIBLE_EVENT, 0)

    def fire_bullets(self):
        """发射子弹（统一处理普通/超级子弹，避免重复逻辑）"""
        # 用局部索引避免全局变量冲突，每次调用重置索引（通过取模保证循环）

        if not (self.delay % BULLET_FIRE_INTERVAL):
            if self.sounds["bullet"]:
                self.sounds["bullet"].play()

            if self.is_double_bullet:
                # 超级子弹：每次发射2个
                self.bullet2[self.bullet2_index].reset(
                    (self.me.rect.centerx - 33, self.me.rect.centery))
                self.bullet2[self.bullet2_index +
                             1].reset((self.me.rect.centerx + 30, self.me.rect.centery))
                self.bullet2_index = (self.bullet2_index + 2) % BULLET2_NUM

            else:
                # 普通子弹：每次发射1个
                self.bullet1[self.bullet1_index].reset(self.me.rect.midtop)
                self.bullet1_index = (self.bullet1_index + 1) % BULLET1_NUM

        """更新子弹位置"""

    def update_bullets(self, bullets):
        for b in bullets:
            if b.active:
                b.move()

    def draw_bullets(self, bullets):
        for b in bullets:
            if b.active:
                self.screen.blit(b.image, b.rect)

    def check_bullet_hits(self, bullets):
        for b in bullets:
            if b.active:
                # 碰撞检测
                hit_enemies = pygame.sprite.spritecollide(
                    b, self.all_enemies, False, pygame.sprite.collide_mask
                )
                if hit_enemies:
                    b.active = False  # 子弹击中后消失
                    for enemy_sprite in hit_enemies:
                        if enemy_sprite in self.mid_enemies or enemy_sprite in self.big_enemies:
                            enemy_sprite.hit = True
                            enemy_sprite.energy -= 1
                            if enemy_sprite.energy <= 0:
                                enemy_sprite.active = False
                        else:
                            enemy_sprite.active = False  # 小型敌机直接销毁

    def draw_enemies(self):
        """绘制所有敌机及爆炸效果"""
        # 绘制大型敌机
        for enemy_sprite in self.big_enemies:
            if enemy_sprite.active:
                enemy_sprite.move()
                if enemy_sprite.hit:
                    self.screen.blit(enemy_sprite.image_hit, enemy_sprite.rect)
                    enemy_sprite.hit = False
                else:
                    # 切换图片实现动画效果
                    self.screen.blit(
                        enemy_sprite.image1 if self.switch_image else enemy_sprite.image2, enemy_sprite.rect)
                myutils.draw_health_bar(self.screen, enemy_sprite)
                # 大型敌机入场音效
                if enemy_sprite.rect.bottom == -50 and self.sounds["enemy3_fly"]:
                    self.sounds["enemy3_fly"].play(-1)
            else:
                # 爆炸动画
                if not (self.delay % EXPLOSION_INTERVAL):
                    if self.explosion_indexes["big"] == 0 and self.sounds["enemy3_down"]:
                        self.sounds["enemy3_down"].play()
                    self.screen.blit(
                        enemy_sprite.destroy_images[self.explosion_indexes["big"]], enemy_sprite.rect)
                    self.explosion_indexes["big"] = (
                        self.explosion_indexes["big"] + 1) % 6
                    if self.explosion_indexes["big"] == 0:
                        self.sounds["enemy3_fly"].stop()
                        self.score += 10000
                        enemy_sprite.reset()

        # 绘制中型敌机
        for enemy_sprite in self.mid_enemies:
            if enemy_sprite.active:
                enemy_sprite.move()
                if enemy_sprite.hit:
                    self.screen.blit(enemy_sprite.image_hit, enemy_sprite.rect)
                    enemy_sprite.hit = False
                else:
                    self.screen.blit(enemy_sprite.image, enemy_sprite.rect)
                myutils.draw_health_bar(self.screen, enemy_sprite)
            else:
                if not (self.delay % EXPLOSION_INTERVAL):
                    if self.explosion_indexes["mid"] == 0 and self.sounds["enemy2_down"]:
                        self.sounds["enemy2_down"].play()
                    self.screen.blit(
                        enemy_sprite.destroy_images[self.explosion_indexes["mid"]], enemy_sprite.rect)
                    self.explosion_indexes["mid"] = (
                        self.explosion_indexes["mid"] + 1) % 4
                    if self.explosion_indexes["mid"] == 0:
                        self.score += 6000
                        enemy_sprite.reset()

        # 绘制小型敌机
        for enemy_sprite in self.small_enemies:
            if enemy_sprite.active:
                enemy_sprite.move()
                self.screen.blit(enemy_sprite.image, enemy_sprite.rect)
            else:
                if not (self.delay % EXPLOSION_INTERVAL):
                    if self.explosion_indexes["small"] == 0 and self.sounds["enemy1_down"]:
                        self.sounds["enemy1_down"].play()
                    self.screen.blit(
                        enemy_sprite.destroy_images[self.explosion_indexes["small"]], enemy_sprite.rect)
                    self.explosion_indexes["small"] = (
                        self.explosion_indexes["small"] + 1) % 4
                    if self.explosion_indexes["small"] == 0:
                        self.score += 1000
                        enemy_sprite.reset()

    def draw_my_plane(self):
        """绘制我方飞机及碰撞检测"""
        # 检测我方飞机与敌机碰撞
        if not self.me.invincible:
            collisions = pygame.sprite.spritecollide(
                self.me, self.all_enemies, False, pygame.sprite.collide_mask)
            if collisions:
                self.me.active = False
                for enemy_sprite in collisions:
                    enemy_sprite.active = False

        # 绘制我方飞机（正常状态/爆炸状态）
        if self.me.active:
            if self.switch_image:
                self.screen.blit(self.me.image1, self.me.rect)
            else:
                self.screen.blit(self.me.image2, self.me.rect)
        else:
            if not (self.delay % EXPLOSION_INTERVAL):
                if self.explosion_indexes["me"] == 0 and self.sounds["me_down"]:
                    self.sounds["me_down"].play()
                self.screen.blit(
                    self.me.destroy_images[self.explosion_indexes["me"]], self.me.rect)
                self.explosion_indexes["me"] = (
                    self.explosion_indexes["me"] + 1) % 4
                if self.explosion_indexes["me"] == 0:
                    self.life_num -= 1
                    self.me.reset()
                    pygame.time.set_timer(
                        self.INVINCIBLE_EVENT, INVINCIBLE_DURATION)

    def draw_ui(self):
        """绘制游戏UI（分数、炸弹数量、生命值）"""
        # 绘制炸弹数量
        bomb_text = self.bomb_font.render(f"× {self.bomb_num}", True, WHITE)
        text_rect = bomb_text.get_rect()
        self.screen.blit(
            self.images["bomb"], (10, self.bg_size[1] - 10 - self.images["bomb"].get_height()))
        self.screen.blit(
            bomb_text, (20 + self.images["bomb"].get_width(), self.bg_size[1] - 5 - text_rect.height))

        # 绘制剩余生命值
        if self.life_num:
            for i in range(self.life_num):
                pos_x = self.bg_size[0] - 10 - \
                    (i + 1) * self.images["life"].get_width()
                pos_y = self.bg_size[1] - 10 - self.images["life"].get_height()
                self.screen.blit(self.images["life"], (pos_x, pos_y))

        # 绘制得分
        score_text = self.score_font.render(
            f"Score : {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 5))

    def draw_game_over(self):
        """绘制游戏结束界面"""
        # 停止所有音频和定时器
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        pygame.time.set_timer(self.SUPPLY_EVENT, 0)

        # 读取并更新最高记录
        if not self.recorded:
            self.recorded = True
            try:
                with open("record.txt", "r") as f:
                    self.record_score = int(f.read())
            except (FileNotFoundError, ValueError):
                self.record_score = 0  # 首次运行或文件异常时默认0

            if self.score > self.record_score:
                with open("record.txt", "w") as f:
                    f.write(str(self.score))
                self.record_score = self.score

        # 绘制结束界面元素
        record_text = self.score_font.render(
            f"Best : {self.record_score}", True, WHITE)
        self.screen.blit(record_text, (50, 50))

        # 绘制玩家得分
        gameover_text1 = self.gameover_font.render("Your Score", True, WHITE)
        text1_rect = gameover_text1.get_rect(
            centerx=self.bg_size[0]//2, top=self.bg_size[1]//3)
        self.screen.blit(gameover_text1, text1_rect)

        gameover_text2 = self.gameover_font.render(
            str(self.score), True, WHITE)
        text2_rect = gameover_text2.get_rect(
            centerx=self.bg_size[0]//2, top=text1_rect.bottom + 10)
        self.screen.blit(gameover_text2, text2_rect)

        # 绘制重新开始/结束按钮
        again_rect = self.images["again"].get_rect(
            centerx=self.bg_size[0]//2, top=text2_rect.bottom + 50)
        gameover_rect = self.images["gameover"].get_rect(
            centerx=self.bg_size[0]//2, top=again_rect.bottom + 10)
        self.screen.blit(self.images["again"], again_rect)
        self.screen.blit(self.images["gameover"], gameover_rect)

        # 检测按钮点击
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if again_rect.collidepoint(pos):
                # 重新开始游戏（重置当前实例）
                self.__init__(self.screen, self.sounds, self.images)
                self.create_resource()
            elif gameover_rect.collidepoint(pos):
                self.quit_game()

    def run(self):
        """游戏主循环"""
        while True:
            self.handle_events()  # 处理事件

            # 绘制背景
            self.screen.blit(self.images["background"], (0, 0))

            if self.life_num > 0 and not self.paused:
                # 游戏进行中
                self.update_level()  # 更新难度

                # 处理玩家移动
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    self.me.moveUp()
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    self.me.moveDown()
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self.me.moveLeft()
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self.me.moveRight()

                # 处理子弹补给
                if self.bullet_supply.active:
                    self.bullet_supply.move()
                    self.screen.blit(self.bullet_supply.image,
                                     self.bullet_supply.rect)
                    if pygame.sprite.collide_mask(self.bullet_supply, self.me):
                        if self.sounds["get_bullet"]:
                            self.sounds["get_bullet"].play()
                        self.is_double_bullet = True
                        pygame.time.set_timer(
                            self.DOUBLE_BULLET_EVENT, DOUBLE_BULLET_DURATION)
                        self.bullet_supply.active = False

                # 处理炸弹补给
                if self.bomb_supply.active:
                    self.bomb_supply.move()
                    self.screen.blit(self.bomb_supply.image,
                                     self.bomb_supply.rect)
                    if pygame.sprite.collide_mask(self.bomb_supply, self.me):
                        if self.sounds["get_bomb"]:
                            self.sounds["get_bomb"].play()
                        if self.bomb_num < 3:
                            self.bomb_num += 1
                        self.bomb_supply.active = False

                bullets = self.fire_bullets()          # 生成子弹
                if self.is_double_bullet:
                    bullets = self.bullet2
                else:
                    bullets = self.bullet1
                self.update_bullets(bullets)  # 更新子弹位置
                self.check_bullet_hits(bullets)  # 碰撞检测
                self.draw_bullets(bullets)      # 绘制子弹

                # 绘制敌机
                self.draw_enemies()

                # 绘制我方飞机,并且检测我方飞机是否被撞
                self.draw_my_plane()

                # 绘制UI
                self.draw_ui()

            elif self.life_num == 0:
                # 游戏结束
                self.draw_game_over()

            # 绘制暂停按钮
            self.screen.blit(self.pause_image, self.pause_rect)

            # 控制动画切换频率
            if not (self.delay % IMAGE_SWITCH_INTERVAL):
                self.switch_image = not self.switch_image

            # 更新延迟计数器
            self.delay -= 1
            if self.delay <= 0:
                self.delay = DELAY_MAX

            # 刷新屏幕
            pygame.display.flip()
            self.clock.tick(FPS_LIMIT)

    def quit_game(self):
        """退出游戏"""
        pygame.quit()
        sys.exit()

