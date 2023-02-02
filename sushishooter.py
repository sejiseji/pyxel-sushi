# -*- coding: utf-8 -*-
import pyxel
import math
import webbrowser
from pyquaternion import Quaternion

#-----------------------------------------------
# BGM
MUSIC_NO = 0
# GAME状態
SCENE_TITLE = 0
SCENE_PLAY = 1
SCENE_GAMEOVER = 2
INVINCIBLE_MODE = 1
NORMAL_MODE = 2
HARD_MODE = 3
POST_TWEET_MODE = 4
TEXT_COLOR = 7
# 星
NUM_STARS = 100
STAR_COLOR_HIGH = 11
STAR_COLOR_LOW = 3
# 寿司衛星の周回半径
SATELLITE_RADIUS = 20
# 寿司衛星の3D回転
FLG_SATELITE_3D_ROTATE = True
# 寿司衛星の3D回転時の軸設定
## 回転更新に用いる回転軸
AXIS_3D_X = -1
AXIS_3D_Y = 1
AXIS_3D_Z = -1
## 初期位置の平面→3次元平面への座標セットに用いる回転軸
AXIS_3D_X_INIT = -1
AXIS_3D_Y_INIT = 1
AXIS_3D_Z_INIT = -1
# miku
MIKU_WIDTH  = 16
MIKU_SPEED = 5
MIKU_HP = 3
AFTER_DAMAGE_FRAME = 24
# 寿司ネタ敵
ITEM_WIDTH   = 16
ITEM_HEIGHT  = 16
ITEM_SPEED   = 2
# 寿司ネタ敵
ENEMY_WIDTH   = 16
ENEMY_HEIGHT  = 16
ENEMY_SPEED   = 3
# シャリ弾
BULLET_WIDTH  = 8
BULLET_HEIGHT = 8
BULLET_SPEED  = 4
# 星弾
STAR_BULLET_WIDTH  = 16
STAR_BULLET_HEIGHT = 16
STAR_BULLET_SPEED  = 5
# レーザー弾
LASER_SPEED  = 8
# レーザー弾着弾時の衝撃アニメ表示フレーム数
KIRAKIRA2_CNT = 8
# 着弾時衝撃
BLAST_START_RADIUS = 1
BLAST_END_RADIUS   = 8
BLAST_COLOR_IN     = 10
BLAST_COLOR_OUT    = 14
# 醤油敵
SHOYU_WIDTH   = 16
SHOYU_HEIGHT  = 16
SHOYU_SPEED   = 5
# 醤油弾
SHOYU_BULLET_WIDTH  = 8
SHOYU_BULLET_HEIGHT = 8
SHOYU_BULLET_SPEED  = 4
# 敵レーザー弾

# 7つ寿司を揃えた時のキラキラ表示frame_count
KIRAKIRA_CNT = 24
# 得点単価のセット
# 0:まぐろ 1:はまち 2:たまご 3:とろ軍艦 4:サーモン 5:えび 6:さんま
SCORE_0 = 4
SCORE_1 = 5
SCORE_2 = 2
SCORE_3 = 8
SCORE_4 = 10
SCORE_5 = 6
SCORE_6 = 7
SCORE_SUSHIALL = 200
SCORE_HEART = 100
SCORE_SHOYU = 40
# 加速アイテムを取得した際の有効時間（frame数）
ACCELERATED_TIME = 100
# 加速アイテム取得による増分
ACCELERATED_SPEED = 3

#-----------------------------------------------
# >> オブジェクト種別毎の配列
# アイテム
items = []
# ネタ
sushineta = []
# シャリ弾
shari_bullets = []
# 衝撃波
blasts = []
# 醤油
shoyu = []
# 醬油弾
shoyu_bullets = []
# 星弾
star_bullets = []
# レーザー弾
lasers = []
lasers_enemy = []
#-----------------------------------------------
# 敵homing用の自機の座標
miku_xy = []
#-----------------------------------------------


def update_list(list):
    for elem in list:
        elem.update()

def draw_list(list):
    for elem in list:
        elem.draw()

def cleanup_list(list):
    i = 0
    while i < len(list):
        elem = list[i]
        if not elem.is_alive:
            list.pop(i)
        else:
            i += 1

class Background:
    def __init__(self):
        self.stars = []
        for i in range(NUM_STARS):
            self.stars.append(
                (
                    pyxel.rndi(0, pyxel.width - 1),
                    pyxel.rndi(0, pyxel.height - 1),
                    pyxel.rndf(1, 2.5),
                )
            )

    def update(self):
        for i, (x, y, speed) in enumerate(self.stars):
            x += speed
            if x >= 0:
                x += pyxel.width
            self.stars[i] = (x, y, speed)

    def draw(self):
        for (x, y, speed) in self.stars:
            pyxel.pset(x, y, STAR_COLOR_HIGH if speed > 2.1 else STAR_COLOR_LOW)


# ゲームオブジェクト
class GameObject:
	def __init__(self):
        # パラメタ初期化（存在フラグ、機体座標、移動時座標増分、機体サイズ、機体体力）
		self.exists = False
		self.x = 0
		self.y = 0
		self.vx = 0
		self.vy = 0
		self.size = 16
	def init(self, x, y, deg, speed):
        # インスタンス生成時の引数に基づく初期化
        # 座標
		self.x, self.y = x, y
        # 角度パラメタを極座標redへ変換
		rad = math.radians(deg)
        # 速度の指定
		self.setSpeed(rad, speed)
	def move(self):
        # 増分パラメタに基づいて位置座標を更新する
		self.x += self.vx
		self.y += self.vy
	def setSpeed(self, rad, speed):
        # 移動時のx,y軸増分を計算（速度とラジアンによる極座標から直交座標へ） 
		self.vx, self.vy = speed * math.cos(rad), speed * -math.sin(rad)
	def isOutSide(self):
        # 画面外判定
		r2 = self.size/2
        # （更新後座標の）Ｘ座標が機体サイズ半分のマイナスより小さくなる（＝画面内左上隅より左にある）とき、
        # （更新後座標の）Ｙ座標が機体サイズ半分のマイナスより小さくなる（＝画面内左上隅より上にある）とき、
        # （更新後座標の）Ⅹ座標が画面幅を超えるとき、
        # （更新後座標の）Ｙ座標が画面高さを超えるとき
		return self.x < -r2 or self.y < -r2 or self.x > pyxel.width+r2 or self.y > pyxel.height+r2
	def clipScreen(self):
		r2 = self.size/2
        # 座標が自機サイズ半分未満の位置Ａにあるとき自機サイズ半分の位置を座標とし、そうでないときは変化させない
		self.x = r2 if self.x < r2 else self.x
		self.y = r2 if self.y < r2 else self.y
        # 座標が画面幅・高さから自機サイズ半分を差し引いた値より大きい位置ＢにあるときはＢの位置とし、そうでないときは変化させない
		self.x = pyxel.width-r2 if self.x > pyxel.width-r2 else self.x
		self.y = pyxel.height-r2 if self.y > pyxel.height-r2 else self.y
	def update(self):
        # 移動計算をしたのち、画面外判定
		self.move()
		if self.isOutSide():
			self.exists = False


# ゲームオブジェクト管理
class GameObjectManager:
	def __init__(self, num, obj):
        # オブジェクトプールを準備
		self.pool = []
        # 指定数numだけゲームオブジェクトをプールに追加する
		for i in range(0, num):
			self.pool.append(obj())
	def add(self):
        # プール内の全オブジェクトに対し存在フラグをTrueへ更新する
		for obj in self.pool:
			if obj.exists == False:
				obj.exists = True
				return obj
		return None
	def update(self):
        # プール内の全オブジェクトに対し存在フラグがTrueのときオブジェクトのupdateを動作させる
		for obj in self.pool:
			if obj.exists:
				obj.update()
	def draw(self):
        # プール内の全オブジェクトに対しdrawを動作させる
		for obj in self.pool:
			if obj.exists:
				obj.draw()


class App:
    def __init__(self): # 初期化
        pyxel.init(300, 200, title="SUSHI SHOOTER", fps=10, display_scale=2, capture_scale=2, capture_sec=10)
        self.init()
        self.kirakira_cnt = 0
        self.kirakira_x = 0
        self.kirakira_y = 0
        self.scene = SCENE_TITLE
        self.background = Background()
        #BGM再生(指定MUSICNoをloop再生)
        pyxel.playm(MUSIC_NO, loop = True)
        # アプリケーションの実行(更新関数、描画関数)
        pyxel.run(self.update, self.draw)

    def init(self):
        pyxel.load("sushishooter.pyxres")
        # 撃墜・取得数の初期化
        self.score_0_get = 0
        self.score_1_get = 0
        self.score_2_get = 0
        self.score_3_get = 0
        self.score_4_get = 0
        self.score_5_get = 0
        self.score_6_get = 0
        self.score_heart_get = 0
        self.score_sushiall_get = 0
        self.score_shoyu_get = 0
        # 得点の初期化
        self.score_0 = 0
        self.score_1 = 0
        self.score_2 = 0
        self.score_3 = 0
        self.score_4 = 0
        self.score_5 = 0
        self.score_6 = 0
        self.score_heart = 0
        self.score_sushiall = 0
        self.score_shoyu = 0
        self.score_total = 0
        self.hi_score = 0
        self.hiscore_updt_flg = False
        self.game_mode = INVINCIBLE_MODE # 起動時点では無敵（無限モード）
        self.selectdelay_cnt = 0
        self.accelerated_time = 0

        # Mikuを準備
        # Miku自身SATELLITEを継承。
        # 回転の基準点を画面中央、衛星振舞い（回転）フラグ、周回時半径,編隊数1,隊内order1, 衛星としての初期位置調整値を指定し、単体で回転を行う。
        # 最後の値は加速状態時の追加速度。
        self.miku = MIKU(100, 100, False, 16, 1, 1, 0, ACCELERATED_SPEED)
        if(self.game_mode == HARD_MODE):
            self.miku.addspeed = 2
        
        # Mikuを周回するSushi衛星を準備。回転の中心点は正方形Miku画像の1辺サイズの半分を基準点とする。
        # 引数：寿司ネタ種別, 回転の基準点X, 回転の基準点Y, 衛星振舞い（回転）フラグ、基準点からの距離, 編隊数, 編隊内の順序, 3d回転フラグ
        # 寿司ネタ種別 0:まぐろ 1:はまち 2:たまご 3:とろ軍艦 4:サーモン 5:えび 6:さんま
        self.sushiset_r = []
        for i in range(7):
            self.sushiset_r.append(SUSHI(i, self.miku.x, self.miku.y, True, SATELLITE_RADIUS, 7, (i + 1), self.miku.size/2, FLG_SATELITE_3D_ROTATE))

        # 横に流れるだけの寿司を準備 
        self.sushiset_f = []
        for i in range(7):
            self.sushiset_f.append(SUSHI((6 - i), 17 * i, 183, False, 0, 0, 0, 0, False))

        # 雪を準備 
        self.snow_all_amount = 50
        self.flg_weather_snow = True
        if (self.flg_weather_snow):
            self.yukiset  = []
            for i in range(self.snow_all_amount):
                self.yukiset.append(SNOW(pyxel.rndi(0, pyxel.width), pyxel.rndi(0, pyxel.height), pyxel.rndi(0,1)))


    def update(self): # 更新処理
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

        self.background.update()
        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        elif self.scene == SCENE_PLAY:
            self.update_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.update_gameover_scene()

    def update_gamemode(self):
        # 左右キー打鍵をgamemodeの1(INVINCIBLE),2(EASY),3(NOMAL),4(POST_TWEET)の選択状態に対応させる
        if(self.selectdelay_cnt > 0):
            self.selectdelay_cnt -= 1
        if(self.selectdelay_cnt == 0):
            if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                if (self.game_mode == INVINCIBLE_MODE): 
                    self.game_mode = NORMAL_MODE
                    self.selectdelay_cnt = 3
                elif (self.game_mode == NORMAL_MODE): 
                    self.game_mode = HARD_MODE
                    self.selectdelay_cnt = 3
                elif (self.game_mode == HARD_MODE): 
                    self.game_mode = POST_TWEET_MODE
                    self.selectdelay_cnt = 3
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                if (self.game_mode == POST_TWEET_MODE): 
                    self.game_mode = HARD_MODE
                    self.selectdelay_cnt = 3
                elif (self.game_mode == HARD_MODE): 
                    self.game_mode = NORMAL_MODE
                    self.selectdelay_cnt = 3
                elif (self.game_mode == NORMAL_MODE): 
                    self.game_mode = INVINCIBLE_MODE
                    self.selectdelay_cnt = 3

    def post_tweet(self):
        template_link = "https://twitter.com/intent/tweet?text=%0A-----------------------------%0A%E7%A7%81%E3%81%AE%E3%83%8F%E3%82%A4%E3%82%B9%E3%82%B3%E3%82%A2%E3%81%AF{}%E3%81%A7%E3%81%99%EF%BC%81%0A%3E%3ESUSHI%20SHOOTER%3C%3C%0Ahttps%3A%2F%2Fkitao.github.io%2Fpyxel%2Fwasm%2Flauncher%2F%3Fplay%3Dsejiseji.pyxel-sushi.sushishooter%26gamepad%3Denabled%26packages%3Dnumpy%0A%23Pyxel%20"
        result_score = self.hi_score
        form_link = template_link.format(result_score)
        webbrowser.open(form_link)


    def update_title_scene(self):
        self.update_gamemode()
        if(self.game_mode in (INVINCIBLE_MODE, NORMAL_MODE, HARD_MODE)):
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                self.game_start()
        if(self.game_mode == POST_TWEET_MODE):
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                self.post_tweet()

    def update_play_scene(self):
        
        self.miku.update_recordxy() # 現在位置の記録
        self.miku.update_bullet() # シャリ弾／星弾の射出
        self.miku.update_laser() # レーザーの射出
        self.miku.update_btn() # 上下左右キーで位置座標の増減分dx,dyを取得
        self.update_accelerated() # 加速状態の残り時間を更新する

        update_list(items) # アイテムの状態を更新
        cleanup_list(items)

        update_list(shari_bullets) # シャリ弾の状態を更新
        cleanup_list(shari_bullets)

        update_list(star_bullets)
        cleanup_list(star_bullets)

        update_list(sushineta) # 敵寿司ネタの状態を更新
        cleanup_list(sushineta)

        update_list(shoyu_bullets) # 醤油弾の状態を更新
        cleanup_list(shoyu_bullets)

        update_list(lasers) # レーザー弾の状態を更新
        cleanup_list(lasers)

        update_list(lasers_enemy) # 敵レーザー弾の状態を更新
        cleanup_list(lasers_enemy)

        for enemy in shoyu:
            enemy.update_shoyu_bullet() # 醤油弾の射出

        update_list(shoyu) # 敵醤油の状態を更新
        cleanup_list(shoyu)

        update_list(blasts) # 衝撃波の状態を更新
        cleanup_list(blasts)

        # dx,dyでmikuの位置座標、回転基準座標の更新
        self.miku.x += self.miku.dx
        self.miku.y += self.miku.dy
        # mikuが回転をONにしているときはmikuの周回基準点も更新する
        if(self.miku.FLG_ROT):
            self.miku.BASE_X += self.miku.dx
            self.miku.BASE_Y += self.miku.dy

        # 衛星の位置座標、回転基準座標、存在状態の更新
        for i in range(len(self.sushiset_r)):
            self.sushiset_r[i].x += self.miku.dx
            self.sushiset_r[i].y += self.miku.dy
            self.sushiset_r[i].BASE_X += self.miku.dx
            self.sushiset_r[i].BASE_Y += self.miku.dy
            # self.sushiset_r[i].update_btn() # スペースキーで存在状態を切り替える（drawでの表示・非表示に使用）

        # mikuの周回基準点を衛星の周回基準点として更新し、衛星の周回後座標を求めたのちに衛星座標を更新
        if (pyxel.frame_count > 1):
            for i in range(len(self.sushiset_r)):
                # mikuが回転をONにしているかどうかで衛星の周回基準点を変更する
                if(self.miku.FLG_ROT):
                    self.sushiset_r[i].update_base(self.miku.BASE_X, self.miku.BASE_Y)
                else:
                    self.sushiset_r[i].update_base(self.miku.x, self.miku.y)
                self.sushiset_r[i].update_torot()

        # 敵の寿司ネタを生成 : X座標、Y座標、キャラクタパターン指定（0:まぐろ 1:はまち 2:たまご 3:ねぎとろ 4:鮭 5:エビ 6:コハダ  ）
        # frame_count 指定値毎に1匹生成。
        if pyxel.frame_count % 10 == 0:
            self.addspeed = 1 if self.game_mode == HARD_MODE else 0
            NETA(pyxel.width, pyxel.rndi(0, pyxel.height - ENEMY_HEIGHT), pyxel.rndi(0, 6), self.addspeed) 
        
        # 敵の醤油を生成 : X座標、Y座標
        # frame_count 指定値毎に1匹生成。
        if pyxel.frame_count % 20 == 0:
            self.addspeed = 2 if self.game_mode == HARD_MODE else 0
            SHOYU(pyxel.width, pyxel.rndi(0, pyxel.height - SHOYU_HEIGHT), self.addspeed) 

        # アイテムを生成 : X座標、Y座標、パターン指定（0:ハート 1:加速アイテム）、調整スピード
        # frame_count 指定値毎に生成。
        # game_modeで生成頻度を変える。
        if(self.game_mode in (NORMAL_MODE, INVINCIBLE_MODE)):
            # ハートの生成
            if pyxel.frame_count % 250 == 0:
                ITEM(pyxel.width, pyxel.rndi(0, pyxel.height - ITEM_HEIGHT), 0, 0) 
            # 加速アイテムの生成
            if pyxel.frame_count % 400 == 0:
                ITEM(pyxel.width, pyxel.rndi(0, pyxel.height - ITEM_HEIGHT), 1, 0) 
        if(self.game_mode == HARD_MODE):
            if pyxel.frame_count % 200 == 0:
                ITEM(pyxel.width, pyxel.rndi(0, pyxel.height - ITEM_HEIGHT), 0, 1) 
            if pyxel.frame_count % 350 == 0:
                ITEM(pyxel.width, pyxel.rndi(0, pyxel.height - ITEM_HEIGHT), 1, 1) 

        # アイテムとmikuの当たり判定
        for item in items:
            if (
                self.miku.y + self.miku.h > item.y
                and item.y + item.h > self.miku.y
                and self.miku.x + self.miku.w > item.x
                and item.x + item.w > self.miku.x
            ):
                point = 0
                # アイテム種別ごとの挙動
                if(item.pattern == 0): # ハート
                    pyxel.play(2, 7)
                    point = (SCORE_HEART * (1 + self.miku.feather_flg))
                    self.score_heart += point
                    self.score_heart_get += 1
                    if(self.miku.hp <= 2):
                        self.miku.hp += 1
                if(item.pattern == 1): # 加速アイテム
                    pyxel.play(2, 7)
                    self.miku.accelerated = True
                    self.accelerated_time = ACCELERATED_TIME # 規定frameだけ有効にするため、値をセットする

                item.is_alive = False
                blasts.append(
                    Blast(
                        self.miku.x,
                        self.miku.y,
                        point
                    )
                )
                blasts[len(blasts)-1].kirakira = True
                blasts[len(blasts)-1].kirakira_cnt = KIRAKIRA_CNT

        # 寿司ネタとシャリの当たり判定
        for enemy in sushineta:
            for bullet in shari_bullets:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    point = 0
                    if(enemy.pattern == 0):
                        self.sushiset_r[0].exists = True
                        point = (SCORE_0 * (1 + self.miku.feather_flg))
                        self.score_0 += point
                        self.score_0_get += 1
                    if(enemy.pattern == 1):
                        self.sushiset_r[1].exists = True
                        point = (SCORE_1 * (1 + self.miku.feather_flg))
                        self.score_1 += point
                        self.score_1_get += 1
                    if(enemy.pattern == 2):
                        self.sushiset_r[2].exists = True
                        point = (SCORE_2 * (1 + self.miku.feather_flg))
                        self.score_2 += point
                        self.score_2_get += 1
                    if(enemy.pattern == 3):
                        self.sushiset_r[3].exists = True
                        point = (SCORE_3 * (1 + self.miku.feather_flg))
                        self.score_3 += point
                        self.score_3_get += 1
                    if(enemy.pattern == 4):
                        self.sushiset_r[4].exists = True
                        point = (SCORE_4 * (1 + self.miku.feather_flg))
                        self.score_4 += point
                        self.score_4_get += 1
                    if(enemy.pattern == 5):
                        self.sushiset_r[5].exists = True
                        point = (SCORE_5 * (1 + self.miku.feather_flg))
                        self.score_5 += point
                        self.score_5_get += 1
                    if(enemy.pattern == 6):
                        self.sushiset_r[6].exists = True
                        point = (SCORE_6 * (1 + self.miku.feather_flg))
                        self.score_6 += point
                        self.score_6_get += 1
                    enemy.is_alive = False
                    bullet.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, point)
                    )
                    pyxel.play(1, 5)

        # 醤油（魚）とシャリの当たり判定
        for enemy in shoyu:
            for bullet in shari_bullets:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    point = (SCORE_SHOYU * (1 + self.miku.feather_flg))
                    self.score_shoyu += point
                    self.score_shoyu_get += 1
                    enemy.is_alive = False
                    bullet.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, point)
                    )
                    pyxel.play(1, 5)

        # 醤油（弾）とシャリの当たり判定
        for enemy in shoyu_bullets:
            for bullet in shari_bullets:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    enemy.is_alive = False
                    bullet.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, 0)
                    )
                    pyxel.play(1, 9)

        # 敵レーザーとシャリの当たり判定
        for enemy in lasers_enemy:
            for bullet in shari_bullets:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    enemy.is_alive = False
                    bullet.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, 0)
                    )
                    pyxel.play(1, 9)

        # 寿司ネタと星弾の当たり判定
        for enemy in sushineta:
            for bullet in star_bullets:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    point = 0
                    if(enemy.pattern == 0):
                        self.sushiset_r[0].exists = True
                        point = (SCORE_0 * (1 + self.miku.feather_flg))
                        self.score_0 += point
                        self.score_0_get += 1
                    if(enemy.pattern == 1):
                        self.sushiset_r[1].exists = True
                        point = (SCORE_1 * (1 + self.miku.feather_flg))
                        self.score_1 += point
                        self.score_1_get += 1
                    if(enemy.pattern == 2):
                        self.sushiset_r[2].exists = True
                        point = (SCORE_2 * (1 + self.miku.feather_flg))
                        self.score_2 += point
                        self.score_2_get += 1
                    if(enemy.pattern == 3):
                        self.sushiset_r[3].exists = True
                        point = (SCORE_3 * (1 + self.miku.feather_flg))
                        self.score_3 += point
                        self.score_3_get += 1
                    if(enemy.pattern == 4):
                        self.sushiset_r[4].exists = True
                        point = (SCORE_4 * (1 + self.miku.feather_flg))
                        self.score_4 += point
                        self.score_4_get += 1
                    if(enemy.pattern == 5):
                        self.sushiset_r[5].exists = True
                        point = (SCORE_5 * (1 + self.miku.feather_flg))
                        self.score_5 += point
                        self.score_5_get += 1
                    if(enemy.pattern == 6):
                        self.sushiset_r[6].exists = True
                        point = (SCORE_6 * (1 + self.miku.feather_flg))
                        self.score_6 += point
                        self.score_6_get += 1
                    enemy.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, point)
                    )
                    pyxel.play(1, 5)

        # 醤油（魚）と星弾の当たり判定
        for enemy in shoyu:
            for bullet in star_bullets:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    point = (SCORE_SHOYU * (1 + self.miku.feather_flg))
                    self.score_shoyu += point
                    self.score_shoyu_get += 1
                    enemy.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, point)
                    )
                    pyxel.play(1, 5)

        # 醤油（弾）と星弾の当たり判定
        for enemy in shoyu_bullets:
            for bullet in star_bullets:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    enemy.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, 0)
                    )
                    pyxel.play(1, 9)

        # 敵レーザーと星弾の当たり判定
        for enemy in lasers_enemy:
            for bullet in star_bullets:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    enemy.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, 0)
                    )
                    pyxel.play(1, 9)

        # 寿司ネタと自機レーザーの当たり判定
        for enemy in sushineta:
            for bullet in lasers:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    point = 0
                    if(enemy.pattern == 0):
                        self.sushiset_r[0].exists = True
                        point = (SCORE_0 * (1 + self.miku.feather_flg)) # feather状態中は得点2倍
                        self.score_0 += point
                        self.score_0_get += 1
                    if(enemy.pattern == 1):
                        self.sushiset_r[1].exists = True
                        point = (SCORE_1 * (1 + self.miku.feather_flg))
                        self.score_1 += point
                        self.score_1_get += 1
                    if(enemy.pattern == 2):
                        self.sushiset_r[2].exists = True
                        point = (SCORE_2 * (1 + self.miku.feather_flg))
                        self.score_2 += point
                        self.score_2_get += 1
                    if(enemy.pattern == 3):
                        self.sushiset_r[3].exists = True
                        point = (SCORE_3 * (1 + self.miku.feather_flg))
                        self.score_3 += point
                        self.score_3_get += 1
                    if(enemy.pattern == 4):
                        self.sushiset_r[4].exists = True
                        point = (SCORE_4 * (1 + self.miku.feather_flg))
                        self.score_4 += point
                        self.score_4_get += 1
                    if(enemy.pattern == 5):
                        self.sushiset_r[5].exists = True
                        point = (SCORE_5 * (1 + self.miku.feather_flg))
                        self.score_5 += point
                        self.score_5_get += 1
                    if(enemy.pattern == 6):
                        self.sushiset_r[6].exists = True
                        point = (SCORE_6 * (1 + self.miku.feather_flg))
                        self.score_6 += point
                        self.score_6_get += 1
                    enemy.is_alive = False
                    bullet.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, point)
                    )
                    blasts[len(blasts)-1].kirakira2 = True
                    blasts[len(blasts)-1].kirakira_cnt = KIRAKIRA2_CNT
                    pyxel.play(1, 15)

        # 醤油（魚）と自機レーザーの当たり判定
        for enemy in shoyu:
            for bullet in lasers:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    point = (SCORE_SHOYU * (1 + self.miku.feather_flg))
                    self.score_shoyu += point
                    self.score_shoyu_get += 1
                    enemy.is_alive = False
                    bullet.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2, point)
                    )
                    blasts[len(blasts)-1].kirakira2 = True
                    blasts[len(blasts)-1].kirakira_cnt = KIRAKIRA2_CNT
                    pyxel.play(1, 15)

        # 醤油（弾）と自機レーザーの当たり判定
        for enemy in shoyu_bullets:
            for bullet in lasers:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    enemy.is_alive = False
                    bullet.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2 - 5, enemy.y + ENEMY_HEIGHT / 2 - 5, 0)
                    )
                    blasts[len(blasts)-1].kirakira2 = True
                    blasts[len(blasts)-1].kirakira_cnt = KIRAKIRA2_CNT
                    pyxel.play(1, 9)

        # 敵レーザーと自機レーザーの当たり判定
        for enemy in lasers_enemy:
            for bullet in lasers:
                if (
                    enemy.y + enemy.h > bullet.y
                    and bullet.y + bullet.h > enemy.y
                    and enemy.x + enemy.w > bullet.x
                    and bullet.x + bullet.w > enemy.x
                ):
                    enemy.is_alive = False
                    bullet.is_alive = False
                    blasts.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2 - 5, enemy.y + ENEMY_HEIGHT / 2 - 5, 0)
                    )
                    blasts[len(blasts)-1].kirakira2 = True
                    blasts[len(blasts)-1].kirakira_cnt = KIRAKIRA2_CNT
                    pyxel.play(1, 9)

        # 被弾後の規定フレーム数間はダメージを受けない。被弾後フレームカウントを減らす。
        if (self.miku.after_damage_frame > 0):
            self.miku.after_damage_frame -= 1

        # 被弾後フレームカウントが0のときにダメージを受ける
        if(self.miku.after_damage_frame == 0):
            # 醤油とmikuの当たり判定
            for enemy in shoyu:
                if (
                    self.miku.y + self.miku.h > enemy.y
                    and enemy.y + enemy.h > self.miku.y
                    and self.miku.x + self.miku.w > enemy.x
                    and enemy.x + enemy.w > self.miku.x
                ):
                    pyxel.play(1, 8)
                    enemy.is_alive = False
                    blasts.append(
                        Blast(
                            self.miku.x + self.miku.w / 2,
                            self.miku.y + self.miku.h / 2,
                            -1
                        )
                    )
                    # damageによってfeather状態を解除する
                    if(self.miku.feather_flg == 1):
                        self.miku.feather_flg = 0

                    if(self.game_mode in (NORMAL_MODE, HARD_MODE)):
                        self.miku.hp -= 1
                        if (self.miku.hp == 0):
                            self.scene = SCENE_GAMEOVER
                        # 被弾後フレームカウントを規定値に設定する
                        self.miku.after_damage_frame = AFTER_DAMAGE_FRAME

            # 醤油が放つ弾とmikuの当たり判定
            for enemy in shoyu_bullets:
                if (
                    self.miku.y + self.miku.h > enemy.y
                    and enemy.y + enemy.h > self.miku.y
                    and self.miku.x + self.miku.w > enemy.x
                    and enemy.x + enemy.w > self.miku.x
                ):
                    pyxel.play(1, 8)
                    enemy.is_alive = False
                    blasts.append(
                        Blast(
                            self.miku.x + self.miku.w / 2,
                            self.miku.y + self.miku.h / 2,
                            -1
                        )
                    )
                    # damageによってfeather状態を解除する
                    if(self.miku.feather_flg == 1):
                        self.miku.feather_flg = 0

                    if(self.game_mode in (NORMAL_MODE, HARD_MODE)):
                        self.miku.hp -= 1
                        if (self.miku.hp == 0):
                            self.scene = SCENE_GAMEOVER
                        # 被弾後フレームカウントを規定値に設定する
                        self.miku.after_damage_frame = AFTER_DAMAGE_FRAME

            # 敵レーザーとmikuの当たり判定
            for enemy in lasers_enemy:
                if (
                    self.miku.y + self.miku.h > enemy.y
                    and enemy.y + enemy.h > self.miku.y
                    and self.miku.x + self.miku.w > enemy.x
                    and enemy.x + enemy.w > self.miku.x
                ):
                    pyxel.play(1, 8)
                    enemy.is_alive = False
                    blasts.append(
                        Blast(
                            self.miku.x + self.miku.w / 2,
                            self.miku.y + self.miku.h / 2,
                            -1
                        )
                    )
                    # damageによってfeather状態を解除する
                    if(self.miku.feather_flg == 1):
                        self.miku.feather_flg = 0

                    if(self.game_mode in (NORMAL_MODE, HARD_MODE)):
                        self.miku.hp -= 1
                        if (self.miku.hp == 0):
                            self.scene = SCENE_GAMEOVER
                        # 被弾後フレームカウントを規定値に設定する
                        self.miku.after_damage_frame = AFTER_DAMAGE_FRAME

        # mikuを周回する寿司衛星の存在（表示状態）フラグチェック
        self.satellite_all_flg = True
        for i in range(len(self.sushiset_r)):
            if (not(self.sushiset_r[i].exists)):
                self.satellite_all_flg = False
        
        # 寿司衛星を全種揃えたことに対して加点後、周回衛星全ての存在フラグを折る、
        # 更にブラストを追加し、
        # ブラストのキラキラ描画切替用のフラグをたてるとともに、featherモード有効化、キラキラ表示が有効な表示時間と位置を指定。
        if(self.satellite_all_flg):
            # 得点
            self.score_sushiall += (SCORE_SUSHIALL * (1 + self.miku.feather_flg))
            self.score_sushiall_get += 1
            # feather状態を有効化する
            self.miku.feather_flg = 1
            # キラキラ表示
            for i in range(len(self.sushiset_r)):
                self.sushiset_r[i].exists = False
                blasts.append(Blast(self.sushiset_r[i].x + 16 / 2, self.sushiset_r[i].y + 16 / 2, 0))
                blasts[len(blasts)-1].kirakira = True
                blasts[len(blasts)-1].kirakira_cnt = KIRAKIRA_CNT
                self.kirakira_cnt = KIRAKIRA_CNT
                self.kirakira_x = self.miku.x
                self.kirakira_y = self.miku.y
                pyxel.play(2, 6)

        # INVINCIBLE_MODEの終了
        if(self.game_mode == INVINCIBLE_MODE):
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                self.scene = SCENE_TITLE

        # 合計得点の更新
        self.score_total = self.score_0 + self.score_1 + self.score_2 + self.score_3 + \
                           self.score_4 + self.score_5 + self.score_6 + self.score_heart + \
                           self.score_sushiall + self.score_shoyu

    def update_accelerated(self):
        # 加速有効時間が正であれば、残りtimeを減らす
        if(self.accelerated_time > 0):
            self.accelerated_time -= 1
            # 加速有効時間が0になったらmikuの加速状態を解除する
            if(self.accelerated_time == 0):
                self.miku.accelerated = False

    def update_gameover_scene(self):
        self.update_gamemode()
        update_list(items)
        update_list(shari_bullets)
        update_list(sushineta)
        update_list(blasts)
        update_list(shoyu)
        update_list(shoyu_bullets)
        update_list(lasers)
        update_list(lasers_enemy)
        cleanup_list(items)
        cleanup_list(sushineta)
        cleanup_list(shari_bullets)
        cleanup_list(blasts)
        cleanup_list(shoyu)
        cleanup_list(shoyu_bullets)
        cleanup_list(lasers)
        cleanup_list(lasers_enemy)

        if(self.game_mode in (INVINCIBLE_MODE, NORMAL_MODE, HARD_MODE)):
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                self.game_start()
        
        if(self.game_mode == POST_TWEET_MODE):
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                self.post_tweet()

    def game_start(self):
        self.scene = SCENE_PLAY
        self.miku.x = 100
        self.miku.y = 100
        self.miku.hp = MIKU_HP
        self.miku.after_damage_frame = 0
        self.miku.feather_flg = 0
        # 衛星の位置座標を再計算、存在状態を否へ
        for i in range(len(self.sushiset_r)):
            self.sushiset_r[i].initposition(self.miku.x, self.miku.y, 10, 7, (i + 1), self.miku.size/2)
            self.sushiset_r[i].exists = False
        self.kirakira_cnt = 0
        self.kirakira_x = 0
        self.kirakira_y = 0
        # 撃墜数・取得数の初期化
        self.score_0_get = 0
        self.score_1_get = 0
        self.score_2_get = 0
        self.score_3_get = 0
        self.score_4_get = 0
        self.score_5_get = 0
        self.score_6_get = 0
        self.score_heart_get = 0
        self.score_sushiall_get = 0
        self.score_shoyu_get = 0
        # 得点の初期化
        self.score_0 = 0
        self.score_1 = 0
        self.score_2 = 0
        self.score_3 = 0
        self.score_4 = 0
        self.score_5 = 0
        self.score_6 = 0
        self.score_heart = 0
        self.score_sushiall = 0
        self.score_shoyu = 0
        self.score_total = 0
        self.hiscore_updt_flg = False
        items.clear()
        sushineta.clear()
        shari_bullets.clear()
        blasts.clear()
        shoyu.clear()
        shoyu_bullets.clear()

    def draw(self): # 描画処理
        # 画面背景タイルマップを指定
        # pyxel.bltm(0, 0, 0, 705 + pyxel.frame_count % 256, 0, pyxel.width, pyxel.height) # 夕暮れの町
        pyxel.bltm(0, 0, 0, 0   + pyxel.frame_count % 256, 0, pyxel.width, pyxel.height) # 青海波

        # 波を挿入
        # self.drawdx = math.ceil(3*math.sin(pyxel.frame_count % (360 / 5)))
        # self.drawdy = math.ceil(5*math.cos(pyxel.frame_count % 360))
        # pyxel.blt(-8 - self.drawdx, 120 - self.drawdy, \
        #           0, 0, 144, 176, 112, 0)

        # シーン別の描画
        self.background.draw()
        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_PLAY:
            self.draw_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.draw_gameover_scene()
        # 雪を降らす
        for i in range(self.snow_all_amount):
            self.yukiset[i].draw_fall()        
        # スコア表示
        pyxel.text(10, 2, f"SCORE {self.score_total:5}", 7)
        pyxel.text(230, 2, f"HI-SCORE {self.hi_score:5}", 7)
        # 体力表示
        pyxel.blt(10, 8, 1, 32, 128, 8, 8, 0) if (self.miku.hp >= 1) else pyxel.blt(10, 8, 1, 32, 136, 8, 8, 0)
        pyxel.blt(18, 8, 1, 32, 128, 8, 8, 0) if (self.miku.hp >= 2) else pyxel.blt(18, 8, 1, 32, 136, 8, 8, 0)
        pyxel.blt(26, 8, 1, 32, 128, 8, 8, 0) if (self.miku.hp >= 3) else pyxel.blt(26, 8, 1, 32, 136, 8, 8, 0)
        # text
        pyxel.text(100, 2, "SUSHI AWAITS ME TONIGHT !", pyxel.frame_count % 16)

    def draw_key_list(self):
        # 操作方法の画面表示
        self.text_color = TEXT_COLOR
        pyxel.text(9,  61, "KEYSTROKE", self.text_color)
        pyxel.text(9,  74, "THROW RICE : PRESS SPACE / GAME PAD A", self.text_color)
        pyxel.text(9,  82, "EXTRA SHOT1: PRESS V     / GAME PAD B", self.text_color)
        pyxel.text(9,  90, "-----------: PRESS C     / GAME PAD Y", self.text_color)
        pyxel.text(9,  98, "MOVE RIGHT : PRESS RIGHT / GAME PAD RIGHT", self.text_color)
        pyxel.text(9, 106, "MOVE LEFT  : PRESS LEFT  / GAME PAD LEFT", self.text_color)
        pyxel.text(9, 114, "MOVE UP    : PRESS UP    / GAME PAD UP", self.text_color)
        pyxel.text(9, 122, "MOVE DOWN  : PRESS DOWN  / GAME PAD DOWN", self.text_color)
        pyxel.text(9, 130, "GAME START : PRESS ENTER / GAME PAD X", self.text_color)
        pyxel.text(9, 138, "GAME END   : PRESS Q     / CLOSE BROWSER", self.text_color)
        pyxel.rectb(4, 69, 173, 79, self.text_color)

    def draw_score_list(self):
        # スコアの画面表
        self.text_color = TEXT_COLOR
        pyxel.text(185, 77, "YOUR SCORE DETAIL", self.text_color)
        pyxel.text(185, 90, f"TUNA            :{int(self.score_0_get):4}", self.text_color)
        pyxel.text(185, 98, f"YELLOWTAIL      :{int(self.score_1_get):4}", self.text_color)
        pyxel.text(185, 106, f"EGG             :{int(self.score_2_get):4}", self.text_color)
        pyxel.text(185, 114, f"NEGITORO        :{int(self.score_3_get):4}", self.text_color)
        pyxel.text(185, 122, f"SALMON          :{int(self.score_4_get):4}", self.text_color)
        pyxel.text(185, 130, f"SHRIMP          :{int(self.score_5_get):4}", self.text_color)
        pyxel.text(185, 138, f"SAURY           :{int(self.score_6_get):4}", self.text_color)
        pyxel.text(185, 146, f"SUSHI-7         :{int(self.score_sushiall_get):4} times", self.text_color)
        pyxel.text(185, 154, f"HEART           :{int(self.score_heart_get):4}", self.text_color)
        pyxel.text(185, 162, f"SOYSAUCE PITCHER:{int(self.score_shoyu_get):4}", self.text_color)
        # pyxel.text(185, 90, f"TUNA            :{int(self.score_0 / SCORE_0 if self.score_0 != 0 else 0):4}", self.text_color)
        # pyxel.text(185, 98, f"YELLOWTAIL      :{int(self.score_1 / SCORE_1 if self.score_1 != 0 else 0):4}", self.text_color)
        # pyxel.text(185, 106, f"EGG             :{int(self.score_2 / SCORE_2 if self.score_2 != 0 else 0):4}", self.text_color)
        # pyxel.text(185, 114, f"NEGITORO        :{int(self.score_3 / SCORE_3 if self.score_3 != 0 else 0):4}", self.text_color)
        # pyxel.text(185, 122, f"SALMON          :{int(self.score_4 / SCORE_4 if self.score_4 != 0 else 0):4}", self.text_color)
        # pyxel.text(185, 130, f"SHRIMP          :{int(self.score_5 / SCORE_5 if self.score_5 != 0 else 0):4}", self.text_color)
        # pyxel.text(185, 138, f"SAURY           :{int(self.score_6 / SCORE_6 if self.score_6 != 0 else 0):4}", self.text_color)
        # pyxel.text(185, 146, f"SUSHI-7         :{int(self.score_sushiall / SCORE_SUSHIALL if self.score_sushiall != 0 else 0):4} times", self.text_color)
        # pyxel.text(185, 154, f"HEART           :{int(self.score_heart / SCORE_HEART if self.score_heart != 0 else 0):4}", self.text_color)
        # pyxel.text(185, 162, f"SOYSAUCE PITCHER:{int(self.score_shoyu / SCORE_SHOYU if self.score_shoyu != 0 else 0):4}", self.text_color)
        pyxel.rectb(181, 85, 115, 87, self.text_color)

    def draw_howtoplay(self):
        # 遊び方表示
        self.text_color = TEXT_COLOR
        pyxel.text(185, 61, "HOW TO PLAY", self.text_color)
        pyxel.text(185, 74, "THROW AND HIT THE RICE TO ", self.text_color)
        pyxel.text(185, 82, "GET THE SUSHI. & USE SHOTS.", self.text_color)
        pyxel.text(185, 90, "THERE ARE SEVEN TYPES OF ", self.text_color)
        pyxel.text(185, 98, "SUSHI, AND YOU WILL RECEIVE", self.text_color)
        pyxel.text(185, 106, "A BONUS IF YOU TAKE ALL OF", self.text_color)
        pyxel.text(185, 114, "THEM. A SOY SAUCE PITCHER ", self.text_color)
        pyxel.text(185, 122, "EJECTS SOY SAUCE. IF YOU ", self.text_color)
        pyxel.text(185, 130, "TOUCH THE SOY SAUCE OR THE", self.text_color)
        pyxel.text(185, 138, "SOY SAUCE JUG, YOU WILL BE", self.text_color)
        pyxel.text(185, 146, "DAMAGED. GET ITEMS TO USE.", self.text_color)
        pyxel.text(185, 154, "SELECT GAME MODE AND START", self.text_color)
        pyxel.text(185, 162, "ENJOYING SUSHISHOOTER !!", self.text_color)
        pyxel.rectb(181, 69, 115, 103, self.text_color)

    def draw_gamemode(self):
        self.text_color_base = TEXT_COLOR
        self.text_color_selected = 10
        # gamemodeに応じたcolorセット
        if (self.game_mode == INVINCIBLE_MODE): 
            self.mode1_color, self.mode2_color, self.mode3_color, self.mode4_color = \
                self.text_color_selected, self.text_color_base, self.text_color_base, self.text_color_base
        if (self.game_mode == NORMAL_MODE): 
            self.mode1_color, self.mode2_color, self.mode3_color, self.mode4_color = \
                self.text_color_base, self.text_color_selected, self.text_color_base, self.text_color_base            
        if (self.game_mode == HARD_MODE): 
            self.mode1_color, self.mode2_color, self.mode3_color, self.mode4_color = \
                self.text_color_base, self.text_color_base, self.text_color_selected, self.text_color_base
        if (self.game_mode == POST_TWEET_MODE): 
            self.mode1_color, self.mode2_color, self.mode3_color, self.mode4_color = \
                self.text_color_base, self.text_color_base, self.text_color_base, self.text_color_selected
        pyxel.text(9, 152, "GAME MODE", self.text_color_base)
        pyxel.text(9, 163, "INVINCIBLE", self.mode1_color)
        pyxel.text(65, 163, "NORMAL", self.mode2_color)
        pyxel.text(105, 163, "HARD", self.mode3_color)
        pyxel.text(133, 163, "POST_TWEET", self.mode4_color)
        pyxel.rectb(4, 159, 173, 13, self.text_color_base)

    def draw_title_scene(self):
        pyxel.text(125, 30, "SUSHI SHOOTER", pyxel.frame_count % 16)
        pyxel.text(80, 45, "- SELECT GAME MODE, PRESS ENTER -", 11)
        self.draw_key_list()
        self.draw_gamemode()
        self.draw_howtoplay()
        # frame_countの24スパン内で挙動を変えながら寿司を描画する
        if(pyxel.frame_count % 24 in range(8,17)):
            for i in range(len(self.sushiset_f)):
                self.sushiset_f[i].draw_jump()
        else:
            for i in range(len(self.sushiset_f)):
                self.sushiset_f[i].draw_flow()

    def draw_play_scene(self):

        # mikuを周回する寿司衛星を描画する（描画階層index = -1）
        for i in range(len(self.sushiset_r)):
            if (self.sushiset_r[i].exists and self.sushiset_r[i].draw_index == -1):
                self.sushiset_r[i].draw_circle()

        # mikuを描画する（描画階層index = 0）
        self.miku.draw_circle()
        # mikuを周回する寿司衛星を描画する（描画階層index = 0）
        for i in range(len(self.sushiset_r)):
            if (self.sushiset_r[i].exists and self.sushiset_r[i].draw_index == 0):
                self.sushiset_r[i].draw_circle()

        # mikuを周回する寿司衛星を描画する（描画階層index = 1）
        for i in range(len(self.sushiset_r)):
            if (self.sushiset_r[i].exists and self.sushiset_r[i].draw_index == 1):
                self.sushiset_r[i].draw_circle()

        # mikuの周回後座標の計算、自位置座標を更新
        self.miku.update_torot()

        # アイテム
        draw_list(items)
        # 敵寿司ネタ
        draw_list(sushineta)
        # 敵醤油
        draw_list(shoyu) 
        # 醤油弾
        draw_list(shoyu_bullets)
        # 敵レーザー
        draw_list(lasers_enemy)
        # シャリ弾
        draw_list(shari_bullets)
        # 星弾
        draw_list(star_bullets)
        # レーザー
        draw_list(lasers)
        # 衝撃波
        draw_list(blasts)
        

        # 7種寿司を揃えたことの文字を表示し、キラキラ用ブラスト表示フレームカウントを減らす
        if(self.kirakira_cnt > 0):
            pyxel.text(self.kirakira_x, self.kirakira_y + 10, "Yummy!!", pyxel.frame_count % 16)
            self.kirakira_cnt -= 1

        # 無敵モードの終了案内
        if(self.game_mode == INVINCIBLE_MODE) :
                pyxel.text(50, 17, "- NOW ON INVINCIBLE MODE, PRESS Enter TO TITLE -", 7)

    def draw_gameover_scene(self):
        # HI-SCORE の更新
        if(self.score_total > self.hi_score):
            self.hi_score = self.score_total
            self.hiscore_updt_flg = True
        draw_list(items)
        draw_list(shari_bullets)
        draw_list(star_bullets)
        draw_list(sushineta)
        draw_list(blasts)
        draw_list(shoyu_bullets)
        draw_list(shoyu)
        draw_list(lasers)
        draw_list(lasers_enemy)
        
        if(self.hiscore_updt_flg):
            pyxel.text(81, 38, "Congratulation!! HI-SCORE updated!!", pyxel.frame_count % 16)
        pyxel.text(133, 30, "GAME OVER", 8)
        pyxel.text(101, 45, "- PRESS ENTER TO REPLAY -", 11)
        self.draw_key_list()
        self.draw_gamemode()
        self.draw_score_list()
        # frame_countの24スパン内で挙動を変えながら寿司を描画する
        if(pyxel.frame_count % 24 in range(8,17)):
            for i in range(len(self.sushiset_f)):
                self.sushiset_f[i].draw_jump()
        else:
            for i in range(len(self.sushiset_f)):
                self.sushiset_f[i].draw_flow()

class SATELLITE(GameObject):
    def __init__(self, base_x, base_y, radius, sat_num, order, center_adjust, flg_3d):
        super().__init__()
        self.radius = radius # 周回半径
        self.ddeg = 16 # 周回時偏角固定
        self.drad = math.radians(self.ddeg)
        # 3次元回転での回転計算をする際に用いるz軸の仮値
        self.z = 0
        # 描画時の順序。3d回転を行わない平常時は0
        self.draw_index = 0
        # 3次元回転フラグ
        self.flg_3d = flg_3d
        if(self.flg_3d):
            # 3D回転でどんな軸周りに何ラジアン回転するか規定したQuaternionを生成。
            self.quat = Quaternion(
                axis  = [AXIS_3D_X, AXIS_3D_Y, AXIS_3D_Z], # 回転に使用するxyz3軸を設定。
                angle = math.pi * 0.1 # 回転角度を設定しラジアン値を用いる。
            )
            # 初期配置用
            self.quat_init = Quaternion(
                axis  = [AXIS_3D_X_INIT, AXIS_3D_Y_INIT, AXIS_3D_Z_INIT], # 回転に使用するxyz3軸を設定。
                angle = math.pi * pyxel.rndf(0.04, 0.08) # 回転角度を設定しラジアン値を用いる。
            )
        # 回転基準位置
        self.BASE_X = base_x
        self.BASE_Y = base_y
        # 初期位置は必ず2次元座標上での回転計算を用いてXY平面上に展開する
        self.initposition(base_x, base_y, radius, sat_num, order, center_adjust)
        # 回転後位置の初期化（一旦、初期位置）
        self.rotated_X = self.x
        self.rotated_Y = self.y
        self.rotated_Z = self.z
    def initposition(self, base_x, base_y, radius, sat_num, order, center_adjust):
        # ≫回転の基準となるx,y座標パラメタとそこからの距離radius,予定編隊衛星数sat_num,
        #   そのうちの何番目かorderを受け取って衛星1個自身の初期位置を決める。
        # 編隊位置計算のため偏角算出
        self.initdeg = math.ceil(360/sat_num) * (order - 1) # order数1のときX軸方向に延伸した位置からの角度ゼロ位置。
        self.initrad = math.radians(self.initdeg)
        # 複素平面上でinitradの回転実施
        self.rot_origin_polar = base_x + base_y * 1j
        self.rot_target_polar = (base_x + radius + center_adjust) + (base_y + center_adjust) * 1j
        self.rotated = (self.rot_target_polar - self.rot_origin_polar) * math.e ** (1j * self.initrad) \
                        + self.rot_origin_polar
        # 実部虚部を取り出して衛星のXY座標とする
        self.x = self.rotated.real
        self.y = self.rotated.imag

        if(self.flg_3d):
            self.init_quaternion_rotate()

    def update(self): # フレームの更新処理
        # 回転先の座標を計算して位置情報を更新
        self.rotate()
        self.x = self.rotated_X
        self.y = self.rotated_Y
        self.z = self.rotated_Z
    def baseupdate(self, base_x, base_y): 
        # 回転の基準点を引数の値に更新
        self.BASE_X = base_x
        self.BASE_Y = base_y   
    def rotate(self):
        # 周回後の位置を決定する.
        # 3次元回転をするか否かのフラグ状態で挙動を切り替え。
        if(self.flg_3d):
            self.quaternion_rotate()
        else:
            self.complex_rotate()
    def complex_rotate(self):
        # # 複素平面上の実部・虚部の関係性に置き換えて回転角dradで回転後の座標を計算する
        # # 回転前の座標に対応する極座標
        #   （衛星が周回する中心点から半径radiusだけX軸方向に進んだ座標）
        self.rot_target = (self.x + self.y * 1j)
        # # ★回転の基準となる直交座標で作る極座標
        self.rot_origin = (self.BASE_X + self.BASE_Y * 1j) 
        # 基準点を中心に回転した後の極座標
        self.rotated =  (self.rot_target - self.rot_origin) * math.e ** (1j * self.drad) + self.rot_origin
        # 複素平面の実部・虚部が回転後の直交座標に対応
        self.rotated_X = self.rotated.real # 実部係数
        self.rotated_Y = self.rotated.imag # 虚部係数
    def quaternion_rotate(self):
        # 3次元回転の計算と描画順序層の更新。
        # 回転後のx,yを取得
        [self.rotated_X, self.rotated_Y, self.rotated_Z] = self.quat.rotate([self.x - self.BASE_X, self.y - self.BASE_Y, self.z])
        self.rotated_X += self.BASE_X
        self.rotated_Y += self.BASE_Y
        # zは圧縮して描画順序の更新に利用する.
        self.draw_index = 1 if self.z > 0 else -1
    def init_quaternion_rotate(self):
        # 3次元回転の計算と描画順序層の更新。
        # 回転後のx,yを取得
        [self.rotated_X, self.rotated_Y, self.rotated_Z] = self.quat_init.rotate([self.x, self.y - self.BASE_Y, self.z])
        self.rotated_X += self.BASE_X
        self.rotated_Y += self.BASE_Y
        # zは圧縮して描画順序の更新に利用する.
        self.draw_index = 1 if self.rotated_Z > 0 else -1

class MIKU(SATELLITE):
    # 初期化
    def __init__(self, base_x, base_y, flg_rot, radius, sat_num, order, center_adjust, accelerated_speed):
        self.FLG_ROT = flg_rot
        # 回転フラグがTrueの場合衛星としての振舞いを有効にする。
        # そうでない場合は引数座標を初期位置座標として用いる。
        if (self.FLG_ROT):
            super().__init__(base_x, base_y, radius, sat_num, order, center_adjust)
        else:
            self.x = base_x
            self.y = base_y
        self.size = 16
        self.h = 16
        self.w = 16
        self.dx = 0
        self.dy = 0
        self.hp = MIKU_HP
        self.after_damage_frame = 0
        self.feather_flg = 0 # feather状態
        self.addspeed = 0
        self.accelerated_speed = accelerated_speed
        self.accelerated = False
        # 軌跡描画用の座標記録配列
        self.trajectory_point = []
        self.trajectory_point.append([self.x, self.y])
        # 現在座標を登録
        miku_xy.append([self.x,self.y])
        # bulletカウント
        self.bullet_cnt = 0
        
    def update_btn(self):
        # 増分を初期化
        self.dx = 0
        self.dy = 0
        # 加速状態にあれば規定の追加速度を加味する
        if (self.accelerated):
            speed = MIKU_SPEED + self.accelerated_speed
        else:
            speed = MIKU_SPEED
        # 左右キーに動きを対応させる
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            if (self.x >  speed): # 画面端に達しているときは当該方向への増分をセットしない
                self.dx = -speed
        elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            if (self.x <  pyxel.width - self.size):
                self.dx = speed
        # 上下キーに動きを対応させる
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            if (self.y > speed):
                self.dy = -speed
        elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            if (self.y < pyxel.height - self.size):
                self.dy = speed
        if(self.dx == 0 and self.dy == 0):
            return # 動いていない
        # 移動範囲を制限
        self.x = max(self.x, 0)
        self.x = min(self.x, pyxel.width - self.size)
        self.y = max(self.y, 0)
        self.y = min(self.y, pyxel.height - self.size)

    def update_recordxy(self):
        # 現在座標をAppに更新し続ける
        miku_xy.pop(0)
        miku_xy.append([self.x,self.y])
        # 軌跡の記録
        if (len(self.trajectory_point) == 5):
            self.trajectory_point.pop(0)
        self.trajectory_point.append([self.x, self.y])

    def update_base(self, base_x, base_y):
            # 回転の基準点を引数の内容に更新
        if (self.FLG_ROT):
            super().baseupdate(base_x, base_y) 

    def update_torot(self):
            # 周回後座標を計算して現在地を更新する
        if (self.FLG_ROT):
            super().update()

    def update_bullet(self):
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            # 弾発射をカウント
            self.bullet_cnt += 1
            # 5発に1発徹甲弾--==★ 通常はシャリを投げる
            if(self.bullet_cnt % 5 == 0):
                STAR(self.x + (MIKU_WIDTH - BULLET_WIDTH) / 2, self.y - BULLET_HEIGHT / 2, self.addspeed)
                pyxel.play(2, 16)
            else:
                SHARI(self.x + (MIKU_WIDTH - BULLET_WIDTH) / 2, self.y - BULLET_HEIGHT / 2, self.addspeed)
                pyxel.play(1, 4)

    def update_laser(self):
        if pyxel.btnp(pyxel.KEY_V) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            # 単体発射
            # LASER(self.x + (MIKU_WIDTH) / 2, self.y, pyxel.width, self.y, self.addspeed, 0)

            # 同時に存在する段数を制限する。
            lasers_alive = 0
            for elm in lasers:
                if elm.is_alive:
                    lasers_alive += 1
            # 複数同時発射。ただし最大15発展開。
            if lasers_alive <= 10 :
                LASER(self.x + (MIKU_WIDTH) / 2 - 15, self.y - 20, pyxel.width, self.y, self.addspeed, 0)
                LASER(self.x + (MIKU_WIDTH) / 2 + 5, self.y - 10, pyxel.width, self.y, self.addspeed, 0)
                LASER(self.x + (MIKU_WIDTH) / 2 + 10, self.y, pyxel.width, self.y, self.addspeed, 0)
                LASER(self.x + (MIKU_WIDTH) / 2 + 5, self.y + 10, pyxel.width, self.y, self.addspeed, 0)
                LASER(self.x + (MIKU_WIDTH) / 2 - 15, self.y + 20, pyxel.width, self.y, self.addspeed, 0)
                pyxel.play(1, 10)

    def draw_circle(self): # 描画処理
        # 加速状態にあるときは、軌跡を描画する
        if(self.accelerated):
            if (len(self.trajectory_point)>=5):
                pyxel.blt(self.trajectory_point[4][0], self.trajectory_point[4][1], 1, 64, 16*((pyxel.frame_count - 4) % 8), 16, 16, 0)
            if (len(self.trajectory_point)>=4):
                pyxel.blt(self.trajectory_point[3][0], self.trajectory_point[3][1], 1, 64, 16*((pyxel.frame_count - 3) % 8), 16, 16, 0)        
            if (len(self.trajectory_point)>=3):
                pyxel.blt(self.trajectory_point[2][0], self.trajectory_point[2][1], 1, 64, 16*((pyxel.frame_count - 2) % 8), 16, 16, 0)
            if (len(self.trajectory_point)>=2):
                pyxel.blt(self.trajectory_point[1][0], self.trajectory_point[1][1], 1, 64, 16*((pyxel.frame_count - 1) % 8), 16, 16, 0)

        # 被弾後フレームカウント有効中は点滅表示（描画無し／キャラ描画をフレームごとに切替）とする。
        # 通常、被弾後フレームカウントは0なので、余り0のとき描画を行うようにする。
        if (self.after_damage_frame % 2 == 0):
            # feather状態(0/1)によってmikuの姿の描画を切り替える
                pyxel.blt(self.x, self.y, 1, self.feather_flg * 48, 16*(pyxel.frame_count % 8), 16, 16, 0)
            
    def draw_flow(self): # 描画処理（流れる）
        pyxel.blt((pyxel.frame_count  + self.x) % pyxel.width, \
             self.y, \
             1, 0, 16*(pyxel.frame_count % 8), 16, 16, 0)
    def draw_jump(self): # 描画処理（跳ねる）
        pyxel.blt((pyxel.frame_count +  self.x) % pyxel.width, \
             self.y - math.ceil(10*math.sin((pyxel.frame_count + self.x + self.y) % 90)), \
             1, 0, 16*(pyxel.frame_count % 8), 16, 16, 0)

class LASER():
    # 初期化
    def __init__(self, x, y, target_x, target_y, addspeed, bullet_kind):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.addspeed = addspeed
        self.w = 3
        self.h = 3
        self.pre_shotangle = 0
        self.shot_angle = 0
        self.angle_uv = 0
        self.dx, self.dy = (0, 0)
        self.ux, self.uy = (0, 0)
        self.vx, self.vy = (0, 0)
        self.du, self.dv = (0, 0)
        self.nearest_x, self.nearest_y = pyxel.width, self.y
        # 速度の指定
        self.speed = LASER_SPEED + self.addspeed
        # 軌跡描画用の座標記録配列
        self.trajectory_point = []
        self.trajectory_point.append([self.x, self.y])
        # 自機弾か敵弾か
        self.bullet_kind = bullet_kind
        ### -------draw用の射出方向決定処理
        # 自機弾か敵弾かでターゲットを決める
        if (self.bullet_kind == 0):
            # 最も近い敵性オブジェクトを判定しターゲット座標に指定する
            self.update_nearest_obj()
        if (self.bullet_kind == 1):
            # mikuの座標を指定する
            self.target_x, self.target_y =  miku_xy[0][0], miku_xy[0][1]
        self.update_targetlock()
        self.is_alive = True
        if (self.bullet_kind == 0):
            lasers.append(self)
        if (self.bullet_kind == 1):
            lasers_enemy.append(self)

    def update(self):
        pre_angle = self.angle_uv
        # 自機弾か敵弾かで何をターゲットにするか決める
        if (self.bullet_kind == 0):
            # 最も近い敵性オブジェクトを判定しターゲット座標に指定する
            self.update_nearest_obj()
        if (self.bullet_kind == 1):
            # mikuの座標を指定する
            self.target_x, self.target_y = miku_xy[0][0], miku_xy[0][1]
        # ターゲット座標とレーザーの現在座標から進行方向角度を更新する
        if((self.bullet_kind == 0) or (self.bullet_kind == 1 and self.target_x < self.x)):
            self.update_targetlock() 
        # # 自機が敵弾をよけようとして敵弾進行方向に一定角度がつくときは、敵弾は従前の角度を保って飛ぶ
        # if (self.bullet_kind == 1):
        #     self.update_check_upperangle(pre_angle)
        # Speedと進行方向角度に基づいて進行、レーザー座標を更新する
        self.update_xy()

    def check_nearest_forward_obj_axis(self, list):
        # 指定のリストオブジェクトのうち最も近いものの座標を返す
        rtn_x, rtn_y = pyxel.width, self.y
        rtn_distance = pyxel.width
        for elem in list:
            # 存在フラグが有効なものについてのみ距離を測る
            if (elem.is_alive and elem.x >= self.x):
                distance = math.sqrt((elem.x - self.x)**2 + (elem.y - self.y)**2)
                if (distance <= rtn_distance):
                    (rtn_x, rtn_y) = (elem.x, elem.y)
                    rtn_distance = distance
        return (rtn_x, rtn_y)

    def update_nearest_obj(self):
            # 最も近い攻撃可能オブジェクトの座標を取得し、ターゲットとする
            tmp_x1, tmp_y1 = self.check_nearest_forward_obj_axis(sushineta)
            tmp_x2, tmp_y2 = self.check_nearest_forward_obj_axis(shoyu)
            tmp_x3, tmp_y3 = self.check_nearest_forward_obj_axis(shoyu_bullets)
            tmp_x4, tmp_y4 = self.check_nearest_forward_obj_axis(lasers_enemy)
            distance1 = math.sqrt((tmp_x1 - self.x)**2 + (tmp_y1 - self.y)**2)
            distance2 = math.sqrt((tmp_x2 - self.x)**2 + (tmp_y2 - self.y)**2)
            distance3 = math.sqrt((tmp_x3 - self.x)**2 + (tmp_y3 - self.y)**2)
            distance4 = math.sqrt((tmp_x4 - self.x)**2 + (tmp_y4 - self.y)**2)            
            distance = min(distance1, distance2, distance3, distance4)
            # 最も近い敵性オブジェクト迄の距離が一定値以下になると、自身を加速させる
            if (distance <= 15):
                self.speed += 1
            # 最も近い敵性オブジェクトの座標をnearestな座標として保持する
            if  (distance == distance1):
                self.nearest_x, self.nearest_y = tmp_x1, tmp_y1
            elif(distance == distance2):
                self.nearest_x, self.nearest_y = tmp_x2, tmp_y2
            elif(distance == distance3):
                self.nearest_x, self.nearest_y = tmp_x3, tmp_y3
            else:
                self.nearest_x, self.nearest_y = tmp_x4, tmp_y4
            self.target_x, self.target_y = self.nearest_x, self.nearest_y

    def update_targetlock(self):
        # shotangleuvを退避
        self.pre_shotangle = self.angle_uv
        # 弾→標的ベクトルd(dx, dy)
        self.update_dxdy(self.x, self.y, self.target_x, self.target_y)
        # 射出角度
        self.update_shotangle(self.dx, self.dy)
        # uv座標系での角度を求める
        self.update_uvaxis_shotangle()
        # 進行方向に標的が位置している場合、値は0となる

    def update_uvaxis_shotangle(self):
        ### -------射出方向判定用のuv直交系の計算 
        # 弾の進行方向u(ux,uy)
        self.update_vector_u(self.speed, self.shot_angle)
        # uに直交するベクトルv
        self.update_vector_v(self.ux, self.uy)
        # uv座標系で弾→標的ベクトルduv（du, dv）
        self.update_dudv(self.dx, self.dy, self.ux, self.uy, self.vx, self.vy)
        # uv座標系での進行方向angle_uv
        self.update_angleuv(self.du, self.dv)
    def update_vector_u(self, speed, angle):
        self.ux = speed * pyxel.cos(angle)
        self.uy = speed * pyxel.sin(angle)
    def update_vector_v(self, ux, uy):
            self.vx = uy
            self.vy = -ux
    def update_dudv(self, dx, dy, ux, uy, vx, vy):
        if self.bullet_kind == 0:
            self.du = dx * ux + dy * uy
            self.dv = dx * vx + dy * vy
        if self.bullet_kind == 1:
            self.du = -(dx * ux + dy * uy)
            self.dv = -(dx * vx + dy * vy)
    def update_angleuv(self, du, dv):
        self.angle_uv = pyxel.atan2(du, dv)
    def update_dxdy(self,  x, y, target_x, target_y):
        self.dx = target_x - x
        self.dy = target_y - y
    def update_shotangle(self, dx, dy):
        self.shot_angle = pyxel.atan2(dx, dy)
    def update_check_upperangle(self, pre_angle):
        if((self.angle_uv > math.pi * 1/5)):
            self.angle_uv = pre_angle

    def update_xy(self):
        self.x += pyxel.ceil(self.speed * pyxel.cos(self.angle_uv))
        self.y += pyxel.ceil(self.speed * pyxel.sin(self.angle_uv))
        # 軌跡を描画するために座標履歴を保持する
        if (len(self.trajectory_point) == 5):
            self.trajectory_point.pop(0)
        self.trajectory_point.append([self.x, self.y])
        # 画面左右端を超えたとき、存在フラグを折る
        if self.x > pyxel.width:
            self.is_alive = False
        if self.x < 0:
            self.is_alive = False

    def draw(self):
        # 自機弾
        if (self.bullet_kind == 0):
            # レーザー弾の軌跡を描く
            if (len(self.trajectory_point)>=5):
                pyxel.line(self.trajectory_point[3][0], self.trajectory_point[3][1], self.trajectory_point[4][0], self.trajectory_point[4][1], 7)
            if (len(self.trajectory_point)>=4):
                pyxel.line(self.trajectory_point[2][0], self.trajectory_point[2][1], self.trajectory_point[3][0], self.trajectory_point[3][1], 6)
            if (len(self.trajectory_point)>=3):
                pyxel.line(self.trajectory_point[1][0], self.trajectory_point[1][1], self.trajectory_point[2][0], self.trajectory_point[2][1], 12)
            if (len(self.trajectory_point)>=2):
                pyxel.line(self.trajectory_point[0][0], self.trajectory_point[0][1], self.trajectory_point[1][0], self.trajectory_point[1][1], 5)
            # レーザー弾の弾頭を描く
            pyxel.blt(self.x - 2, self.y - 2, 1, 0, 160 + 5*(pyxel.frame_count % 4), 5, 5, 0)
        # 敵弾
        if (self.bullet_kind == 1):
            if (len(self.trajectory_point)>=5):
                pyxel.line(self.trajectory_point[3][0], self.trajectory_point[3][1], self.trajectory_point[4][0], self.trajectory_point[4][1], 7)
            if (len(self.trajectory_point)>=4):
                pyxel.line(self.trajectory_point[2][0], self.trajectory_point[2][1], self.trajectory_point[3][0], self.trajectory_point[3][1], 14)
            if (len(self.trajectory_point)>=3):
                pyxel.line(self.trajectory_point[1][0], self.trajectory_point[1][1], self.trajectory_point[2][0], self.trajectory_point[2][1], 8)
            if (len(self.trajectory_point)>=2):
                pyxel.line(self.trajectory_point[0][0], self.trajectory_point[0][1], self.trajectory_point[1][0], self.trajectory_point[1][1], 4)
                pyxel.blt(self.x - 2, self.y - 2, 1, 5, 160 + 5*(pyxel.frame_count % 4), 5, 5, 0)

class SUSHI(SATELLITE):
    # 初期化
    def __init__(self, neta, base_x, base_y, flg_rot, radius, sat_num, order, center_adjust, flg_3d):
        self.FLG_ROT = flg_rot
        # 回転フラグがTrueの場合衛星としての振舞いを有効にする。
        # そうでない場合は引数座標を初期位置座標として用いる。
        if (self.FLG_ROT):
            super().__init__(base_x, base_y, radius, sat_num, order, center_adjust, flg_3d)
        else:
            self.x = base_x
            self.y = base_y
        self.NETA = 16 * neta # 0:まぐろ 1:はまち 2:たまご 3:とろ軍艦 4:サーモン 5:えび 6:さんま
    def update_base(self, base_x, base_y):
            # 回転の基準点を引数の内容に更新
        if (self.FLG_ROT):
            super().baseupdate(base_x, base_y) 
    def update_torot(self):
            # 周回後座標を計算して現在地を更新する
        if (self.FLG_ROT):
            super().update()
    def draw_circle(self): # 描画処理（自転のみ）
        pyxel.blt(self.x, self.y, \
             0, self.NETA, 16*(pyxel.frame_count % 8), \
             16, 16, 11)
    def draw_flow(self): # 描画処理（流れる）
        pyxel.blt((pyxel.frame_count + self.x) % pyxel.width, self.y, \
             0, self.NETA, 16*(pyxel.frame_count % 8), \
             16, 16, 11)
    def draw_jump(self): # 描画処理（跳ねる）
        pyxel.blt((pyxel.frame_count + self.x) % pyxel.width, \
             self.y - math.fabs(math.ceil(10*math.sin((pyxel.frame_count + self.x + self.y) % 180))), \
             0, self.NETA, 16*(pyxel.frame_count % 8), \
             16, 16, 11)


class SHARI(GameObject):
    def __init__(self, x, y, addspeed):
        # 射出時点の指定座標で生成
        self.x = x
        self.y = y
        self.w = BULLET_WIDTH
        self.h = BULLET_HEIGHT
        self.is_alive = True
        self.addspeed = addspeed
        shari_bullets.append(self)

    def update(self):
        self.x += BULLET_SPEED + self.addspeed
        # 射出方向の画面端（今回はX軸方向）に達したとき弾の存在フラグを消す
        if self.x + self.w - 1 > pyxel.width:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 1, 16, 128 + 8*(pyxel.frame_count % 2), 8, 8, 0)

class STAR(GameObject):
    def __init__(self, x, y, addspeed):
        # 射出時点の指定座標で生成
        self.x = x
        self.y = y
        self.w = STAR_BULLET_WIDTH
        self.h = STAR_BULLET_HEIGHT
        self.is_alive = True
        self.addspeed = addspeed
        star_bullets.append(self)

    def update(self):
        self.x += STAR_BULLET_SPEED + self.addspeed
        # 射出方向の画面端（今回はX軸方向）に達したとき弾の存在フラグを消す
        if self.x + self.w - 1 > pyxel.width:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 1, 16, 144 + 16*(pyxel.frame_count % 4), 16, 16, 0)

class ITEM(GameObject):
    # 各種アイテム
    def __init__(self, x, y, pattern, addspeed):
        self.x = x
        self.y = y
        self.pattern = pattern
        self.addspeed = addspeed
        self.w = ITEM_WIDTH
        self.h = ITEM_HEIGHT
        self.dir = 1
        self.timer_offset = pyxel.rndi(0, 59)
        self.is_alive = True
        items.append(self)

    def update(self):
        if (pyxel.frame_count + self.timer_offset) % 60 < 30:
            self.y += ITEM_SPEED + self.addspeed
            self.dir = 1
        else:
            self.y -= ITEM_SPEED + self.addspeed
            self.dir = -1
        self.x -= ITEM_SPEED + self.addspeed
        if self.x -self.w + 21 < 0:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 1, 80 + 16*self.pattern, 16*(pyxel.frame_count % 8), 16, 16, 0)

class NETA(GameObject):
    # 敵
    def __init__(self, x, y, pattern, addspeed):
        self.x = x
        self.y = y
        self.pattern = pattern
        self.w = ENEMY_WIDTH
        self.h = ENEMY_HEIGHT
        self.dir = 1
        self.timer_offset = pyxel.rndi(0, 59)
        self.is_alive = True
        self.addspeed = addspeed
        sushineta.append(self)

    def update(self):
        if (pyxel.frame_count + self.timer_offset) % 60 < 30:
            self.y += ENEMY_SPEED + self.addspeed
            self.dir = 1
        else:
            self.y -= ENEMY_SPEED + self.addspeed
            self.dir = -1
        self.x -= ENEMY_SPEED + self.addspeed
        if self.x -self.w + 21 < 0:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 112 + 16*self.pattern, 16*(pyxel.frame_count % 2), 16, 16, 11)


class SHOYU(GameObject):
    # 敵醤油
    def __init__(self, x, y, addspeed):
        self.x = x
        self.y = y
        self.addspeed = addspeed
        self.w = SHOYU_WIDTH
        self.h = SHOYU_HEIGHT
        self.dir = 1
        self.timer_offset = pyxel.rndi(0, 59)
        self.is_alive = True
        shoyu.append(self)

    def update(self):
        if (pyxel.frame_count + self.timer_offset) % 60 < 30:
            self.y += SHOYU_SPEED + self.addspeed
            self.dir = 1
        else:
            self.y -= SHOYU_SPEED + self.addspeed
            self.dir = -1
        self.x -= SHOYU_SPEED + self.addspeed
        if self.x -self.w + 21 < 0:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 1, 16, 16*(pyxel.frame_count % 8), -16, 16, 3)

    def update_shoyu_bullet(self):
        if ((pyxel.frame_count + self.timer_offset) % 40 == 10):
            SHOYUBULLET(self.x + (SHOYU_WIDTH - SHOYU_BULLET_WIDTH) / 2, self.y - SHOYU_BULLET_HEIGHT / 2, self.addspeed)
            # pyxel.play(0, 4)
        if ((pyxel.frame_count + self.timer_offset) % 40 == 15):
            LASER(self.x + (SHOYU_WIDTH - SHOYU_BULLET_WIDTH) / 2, self.y - SHOYU_BULLET_HEIGHT / 2, 0, self.y, self.addspeed, 1)


class SHOYUBULLET(GameObject):
    def __init__(self, x, y, addspeed):
        # 射出時点の指定座標で生成
        self.x = x
        self.y = y
        self.w = SHOYU_BULLET_WIDTH
        self.h = SHOYU_BULLET_HEIGHT
        self.is_alive = True
        self.addspeed = addspeed
        shoyu_bullets.append(self)

    def update(self):
        self.x -= SHOYU_BULLET_SPEED + self.addspeed
        # 射出方向の画面端（今回は-X軸方向）に達したとき弾の存在フラグを消す
        if self.x + self.w - 8 < 0:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 1, 24, 128 + 8*(pyxel.frame_count % 2), 8, 8, 0)


class Blast: # 着弾時の衝撃波
    def __init__(self, x, y, point):
        self.x = x
        self.y = y
        self.radius = BLAST_START_RADIUS
        self.is_alive = True
        self.kirakira = False # アイテム取得時のキラキラ表現
        self.kirakira2 = False # レーザー着弾時の光の表現
        self.kirakira_cnt = 0
        self.point = point
        blasts.append(self)

    def update(self):
        if(self.kirakira or self.kirakira2):
            if(self.kirakira_cnt == 0):
                self.is_alive = False
        else:
            self.radius += 1
            if self.radius > BLAST_END_RADIUS:
                self.is_alive = False

    def draw(self):
        if(self.kirakira and self.kirakira_cnt > 0):
            pyxel.blt(self.x, self.y, 0, 112, 32 + 16*(pyxel.frame_count % 4), 16, 16, 11)
            self.kirakira_cnt -= 1
        elif(self.kirakira2 and self.kirakira_cnt > 0):
            pyxel.blt(self.x - 5, self.y - 5, 0, 224, 0 + 16*(pyxel.frame_count % 8), 16, 16, 0)
            if(self.point != 0):
                # pyxel.text(self.x -6, self.y -10, f"{int(self.point):3}", pyxel.frame_count % 8)
                pyxel.text(self.x -7, self.y -9, f"{int(self.point):3}", 7)
            self.kirakira_cnt -= 1
        else:
            pyxel.circ(self.x, self.y, self.radius, BLAST_COLOR_IN)
            pyxel.circb(self.x, self.y, self.radius, BLAST_COLOR_OUT)
            if(self.point != 0):
                if(self.point > 0):
                    # pyxel.text(self.x -6, self.y -10, f"{int(self.point):3}", pyxel.frame_count % 8)
                    pyxel.text(self.x -7, self.y -9, f"{int(self.point):3}", 7)
                if(self.point < 0):
                    # pyxel.text(self.x -6, self.y -10, f"{int(self.point):3}", pyxel.frame_count % 8)
                    pyxel.text(self.x -7, self.y -9, f"{int(self.point):3}", 8)



class WEATHER:
    # 初期化
    def __init__(self, base_x, base_y):
        self.BASE_X = base_x # 初期位置Ⅹ軸
        self.BASE_Y = base_y # 初期位置Ｙ軸
        # 雪など1px表現可能な天候はリソース不要


class SNOW(WEATHER) :
    # 初期化
    def __init__(self, base_x, base_y, direction):
        super().__init__(base_x, base_y)
        # 入力時の0or1で雪が流れる方向を決定、降雪描画処理でframecountに応じたx進行方向を決定
        if (direction == 0) :
            self.DIRECTION = -1
        else :
            self.DIRECTION = 1
    def draw_fall(self): # 描画処理（降る）
        pyxel.pset(self.DIRECTION * (pyxel.frame_count  + self.BASE_X) % pyxel.width + math.ceil(2*math.sin(pyxel.frame_count % 360)), \
             (pyxel.frame_count +  self.BASE_Y) % pyxel.height, \
                 7) # 白ピクセル


App()
