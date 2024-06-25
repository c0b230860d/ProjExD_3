import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の数 
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)] #クラス(birdと同じ)
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)

 
class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        self.img = pg.image.load(f"fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery
        self.rct.left = bird.rct.right
        self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct) 
        

class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """
    スコアに関するクラス
    """
    sum = 0
    def __init__(self):
        """
        フォントを生成する
        """
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.img = self.fonto.render(f"スコア：{Score.sum}", 0,(0, 0, 255))
        self.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        """
        スコアを表示する
        引数 screen：画面Surface
        """
        self.img = self.fonto.render(f"スコア：{Score.sum}", 0,(0, 0, 255))
        screen.blit(self.img, self.center)


class Explosion:
    """
    爆発に関するクラス
    """
    def __init__(self, bombs:"Bomb"):
        """
        爆発エフェクトを生成する
        引数 bombs：ビーム
        """
        img1 = pg.image.load(f"fig/explosion.gif")
        img2 = pg.transform.flip(img1, True, True)
        self.img_lst = [img1, img2]
        for i in self.img_lst:
            self.rct = i.get_rect()
        self.rct.center = bombs.rct.center
        self.life = 10

    def update(self, screen: pg.Surface):
        """
        爆発を表示する
        引数 screen：画面Surface
        """
        self.life -= 1
        if self.life > 0:
            if 0 <= self.life % 10 <= 5:
                screen.blit(self.img_lst[0], self.rct.center)
            else:
                screen.blit(self.img_lst[1], self.rct.center)
                

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    # こうかとんに関する変数
    bird = Bird((300, 200))
    # ビームに関する変数
    beams = []
    # スコアに関する変数
    score = Score()
    # 爆弾に関する変数
    bombs = [Bomb((255, 0, 0), 10) for i in range(NUM_OF_BOMBS)]
    # 爆発に関する変数
    explosions = []
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースキー押下でBeamクラスのインスタンス生成
                # beam = Beam(bird)   
                beams.append(Beam(bird))         
        screen.blit(bg_img, [0, 0])

        #ゲームオーバー
        for bm in range(len(bombs)):
            if bombs[bm] is not None:
                if bird.rct.colliderect(bombs[bm].rct):
                    font = pg.font.Font(None, 80)
                    txt = font.render("Game Over", True, (255, 0, 0))
                    screen.blit(txt, [WIDTH/2-150, HEIGHT/2])
                    pg.display.update()
                    time.sleep(5)
                    return

        # うち落とし    
        for bm in range(len(bombs)):
            for bem in range(len(beams)):
                if beams[bem] is not None and bombs[bm] is not None:
                    if beams[bem].rct.colliderect(bombs[bm].rct):
                        # うち落とし時に、こうかとん画像を切り替え
                        bird.change_img(6, screen)
                        pg.display.update()
                        Score.sum += 1
                        explosions.append(Explosion(bombs[bm]))  # 爆発のインスタンスをリストに追加 
                        beams[bem] = None
                        bombs[bm] = None

        # それぞれのリストの削減
        bombs = [bm for bm in bombs if bm is not None]
        beams = [bem for bem in beams if bem is not None]
        explosions = [eps for eps in explosions if eps.life > 0]

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        # ビームの更新
        for bem in range(len(beams)):
            beams[bem].update(screen)

        # 爆弾の更新
        for i in range(len(bombs)):
            bombs[i].update(screen)
        
        # スコアの更新
        score.update(screen)

        # ビーム範囲外に出たら削除
        for i, bem in enumerate(beams):
            if check_bound(bem.rct) != (True, True):
                del beams[i]

        # 爆発を更新
        for i, eps in enumerate(explosions):
            explosions[i].update(screen )
        
                
        pg.display.update()
        tmr += 1 
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
