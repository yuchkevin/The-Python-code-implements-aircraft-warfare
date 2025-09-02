import pygame 
import traceback
from pygame.locals import *
from  game   import Game
import myutils

# 窗口配置
WINDOW_WIDTH, WINDOW_HEIGHT = 480, 700
BG_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
# 音效/字体路径（统一管理，避免重复写路径）
SOUND_PATHS = {
    "game_music": "sound/game_music.ogg",
    "bullet": "sound/bullet.wav",
    "use_bomb": "sound/use_bomb.wav",
    "supply": "sound/supply.wav",
    "get_bomb": "sound/get_bomb.wav",
    "get_bullet": "sound/get_bullet.wav",
    "upgrade": "sound/upgrade.wav",
    "enemy3_fly": "sound/enemy3_flying.wav",
    "enemy1_down": "sound/enemy1_down.wav",
    "enemy2_down": "sound/enemy2_down.wav",
    "enemy3_down": "sound/enemy3_down.wav",
    "me_down": "sound/me_down.wav"
}

IMAGE_PATHS = {
    "background": "images/background.png",
    "pause_nor": "images/pause_nor.png",
    "pause_pressed": "images/pause_pressed.png",
    "resume_nor": "images/resume_nor.png",
    "resume_pressed": "images/resume_pressed.png",
    "bomb": "images/bomb.png",
    "life": "images/life.png",
    "again": "images/again.png",
    "gameover": "images/gameover.png"
}



 
 
# --------------------------- 主函数入口（确保代码可直接执行）---------------------------
def main():
    # 初始化游戏环境
    screen = myutils.init_pygame(BG_SIZE,"飞机大战 -- FishC Demo")
    sounds = myutils.load_sounds(SOUND_PATHS)
    images = myutils.load_images(IMAGE_PATHS)

    # 创建并运行游戏
    game = Game(screen, sounds, images,BG_SIZE)
    game.create_resource()
    game.run()


if __name__ == "__main__":
    try:
        main()  # 启动游戏
    except SystemExit:
        pass
    except Exception as e:
        traceback.print_exc()
        pygame.quit()
        input("按任意键退出...")
