import pygame
import enemy


# 颜色常量（RGB）
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --------------------------- 工具函数（抽离通用逻辑，减少重复代码）---------------------------
def init_pygame(BG_SIZE,title):
    """初始化Pygame（音频+窗口+标题）"""
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode(BG_SIZE)
   # pygame.display.set_caption()#
    pygame.display.set_caption(title)
    return screen


def load_sounds(SOUND_PATHS):
    """加载所有音效并设置音量，返回音效字典"""
    sounds = {}
    volume = 0.2  # 基础音量
    for key, path in SOUND_PATHS.items():
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(
                volume if key != "enemy3_down" else 0.5)  # 大型敌机爆炸音量特殊
            sounds[key] = sound
        except Exception as e:
            print(f"警告：加载音效 {key} 失败：{e}")
            sounds[key] = None  # 避免后续调用报错
    # 背景音乐单独处理
    try:
        pygame.mixer.music.load(SOUND_PATHS["game_music"])
        pygame.mixer.music.set_volume(volume)
    except Exception as e:
        print(f"警告：加载背景音乐失败：{e}")
    return sounds


def load_images(IMAGE_PATHS):
    """加载所有图片，返回图片字典"""
    images = {}
    for key, path in IMAGE_PATHS.items():
        try:
            # 背景用convert()优化，带透明通道的用convert_alpha()
            if key == "background":
                img = pygame.image.load(path).convert()
            else:
                img = pygame.image.load(path).convert_alpha()
            images[key] = img
        except Exception as e:
            print(f"警告：加载图片 {key} 失败：{e}")
            # 生成纯色占位图，避免游戏崩溃
            img = pygame.Surface((50, 50))
            img.fill(RED)
            images[key] = img
    return images


def add_enemies(BG_SIZE,small_group, mid_group, big_group, all_group, small_num=0, mid_num=0, big_num=0):
    """批量添加敌机到对应精灵组"""
    # 添加小型敌机
    for _ in range(small_num):
        e = enemy.SmallEnemy(BG_SIZE)
        small_group.add(e)
        all_group.add(e)
    # 添加中型敌机
    for _ in range(mid_num):
        e = enemy.MidEnemy(BG_SIZE)
        mid_group.add(e)
        all_group.add(e)
    # 添加大型敌机
    for _ in range(big_num):
        e = enemy.BigEnemy(BG_SIZE)
        big_group.add(e)
        all_group.add(e)


def increase_enemy_speed(target_group, speed_inc):
    """提升敌机速度"""
    for enemy_sprite in target_group:
        enemy_sprite.speed += speed_inc


def draw_health_bar(screen, enemy_sprite):
    """绘制敌机血条（通用函数，避免重复代码）"""
    # 血条背景（黑色边框）
    bar_x, bar_y = enemy_sprite.rect.left, enemy_sprite.rect.top - 5
    bar_width, bar_height = enemy_sprite.rect.width, 2
    pygame.draw.line(screen, BLACK, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y), bar_height)
    # 血条前景（根据剩余血量变色）
    if isinstance(enemy_sprite, enemy.BigEnemy):
        max_energy = enemy.BigEnemy.energy
    elif isinstance(enemy_sprite, enemy.MidEnemy):
        max_energy = enemy.MidEnemy.energy
    else:
        return  # 小型敌机无血条
    energy_ratio = enemy_sprite.energy / max_energy
    energy_color = GREEN if energy_ratio > 0.2 else RED
    pygame.draw.line(screen, energy_color, (bar_x, bar_y),
                     (bar_x + bar_width * energy_ratio, bar_y), bar_height)
