# -*- coding: utf-8 -*-
import pyxel
import math

#-----------------------------------------------
# mikuサイズ
PLAYER_WIDTH  = 16
MIKU_SPEED = 5
# 寿司ネタ敵
ENEMY_WIDTH   = 16
ENEMY_HEIGHT  = 16
ENEMY_SPEED   = 3
# シャリ弾
BULLET_WIDTH  = 8
BULLET_HEIGHT = 8
BULLET_SPEED  = 4
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
# 7つ寿司を揃えた時のキラキラ表示frame_count
KIRAKIRA_CNT = 24

#-----------------------------------------------
# >> オブジェクト種別毎の配列
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
        #BGM再生(MUSIC 0番をloop再生)
        pyxel.playm(0, loop = True)
        # アプリケーションの実行(更新関数、描画関数)
        pyxel.run(self.update, self.draw)

    def init(self):
        pyxel.load("sushishooter.pyxres")
        # 得点の初期化
        self.score_0 = 0
        self.score_1 = 0
        self.score_2 = 0
        self.score_3 = 0
        self.score_4 = 0
        self.score_5 = 0
        self.score_6 = 0
        self.score_sushiall = 0
        self.score_shoyu = 0
        self.score_total = 0

        # Mikuを準備
        # Miku自身SATELLITEを継承し回転の基準点を画面中央、衛星振舞い（回転）フラグ、周回時半径,編隊数1,隊内order1として単体で回転を行う。
        self.miku = MIKU(100, 100, False, 16, 1, 1, 0)
        # Mikuを周回するSushi衛星を準備。回転の中心点は正方形Miku画像の1辺サイズの半分を基準点とする。
        # 引数：寿司ネタ種別, 回転の基準点X, 回転の基準点Y, 衛星振舞い（回転）フラグ、基準点からの距離, 編隊数, 編隊内の順序
        # 寿司ネタ種別 0:まぐろ 1:はまち 2:たまご 3:とろ軍艦 4:サーモン 5:えび 6:さんま
        self.sushiset_r = []
        for i in range(7):
            self.sushiset_r.append(SUSHI(i, self.miku.x, self.miku.y, True, 10, 7, (i + 1), self.miku.size/2))

        # 横に流れるだけの寿司を準備 
        self.sushiset_f = []
        for i in range(7):
            self.sushiset_f.append(SUSHI((6 - i), 17 * i, 183, False, 0, 0, 0, 0))

        # 雪を準備 
        self.snow_all_amount = 50
        self.flg_weather_snow = True
        if (self.flg_weather_snow):
            self.yukiset  = []
            for i in range(self.snow_all_amount):
                self.yukiset.append(SNOW(pyxel.rndi(0, pyxel.width), pyxel.rndi(0, pyxel.height), pyxel.rndi(0,1)))


    def update(self): # 更新処理
        # キー操作に対応させる
        self.miku.update_shari() # シャリの射出
        
        self.miku.update_btn() # 上下左右キーで位置座標の増減分dx,dyを取得

        update_list(shari_bullets) # シャリ弾の状態を更新
        cleanup_list(shari_bullets)

        update_list(sushineta) # 敵寿司ネタの状態を更新
        cleanup_list(sushineta)

        update_list(shoyu_bullets) # 醤油弾の状態を更新
        cleanup_list(shoyu_bullets)

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
            NETA(300, pyxel.rndi(0, pyxel.height - ENEMY_HEIGHT), pyxel.rndi(0, 6)) 
        
        # 敵の醤油を生成 : X座標、Y座標
        # frame_count 指定値毎に1匹生成。
        if pyxel.frame_count % 20 == 0:
            SHOYU(300, pyxel.rndi(0, pyxel.height - ENEMY_HEIGHT)) 

        # 寿司ネタとシャリの当たり判定
        for enemy in sushineta:
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
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2)
                    )
                    pyxel.play(1, 5)
                    if(enemy.pattern == 0):
                        self.sushiset_r[0].exists = True
                        self.score_0 += 5
                    if(enemy.pattern == 1):
                        self.sushiset_r[1].exists = True
                        self.score_1 += 10
                    if(enemy.pattern == 2):
                        self.sushiset_r[2].exists = True
                        self.score_2 += 15
                    if(enemy.pattern == 3):
                        self.sushiset_r[3].exists = True
                        self.score_3 += 20
                    if(enemy.pattern == 4):
                        self.sushiset_r[4].exists = True
                        self.score_4 += 25
                    if(enemy.pattern == 5):
                        self.sushiset_r[5].exists = True
                        self.score_5 += 30
                    if(enemy.pattern == 6):
                        self.sushiset_r[6].exists = True
                        self.score_6 += 35

        # 醤油とシャリの当たり判定
        for enemy in shoyu:
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
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2)
                    )
                    pyxel.play(1, 5)
                    self.score_shoyu += 40

        # 醤油とmikuの当たり判定
        for enemy in shoyu:
            if (
                self.miku.y + self.miku.h > enemy.y
                and enemy.y + enemy.h > self.miku.y
                and self.miku.x + self.miku.w > enemy.x
                and enemy.x + enemy.w > self.miku.x
            ):
                blasts.append(
                    Blast(
                        self.miku.x + self.miku.w / 2,
                        self.miku.y + self.miku.h / 2,
                    )
                )
        # 醤油が放つ弾とmikuの当たり判定
        for enemy in shoyu_bullets:
            if (
                self.miku.y + self.miku.h > enemy.y
                and enemy.y + enemy.h > self.miku.y
                and self.miku.x + self.miku.w > enemy.x
                and enemy.x + enemy.w > self.miku.x
            ):
                blasts.append(
                    Blast(
                        self.miku.x + self.miku.w / 2,
                        self.miku.y + self.miku.h / 2,
                    )
                )

        # mikuを周回する寿司衛星のフラグチェック
        self.satellite_all_flg = True
        for i in range(len(self.sushiset_r)):
            if (not(self.sushiset_r[i].exists)):
                self.satellite_all_flg = False
        
        # 寿司衛星を全種揃えたことの加点、周回衛星全ての存在フラグを折る、
        # 更にブラストを追加し、
        # ブラストのキラキラ描画切替用のフラグをたてるとともに、キラキラ表示が有効な表示時間と位置を指定。
        if(self.satellite_all_flg):
            self.score_sushiall += 200
            for i in range(len(self.sushiset_r)):
                self.sushiset_r[i].exists = False
                blasts.append(Blast(self.sushiset_r[i].x + 16 / 2, self.sushiset_r[i].y + 16 / 2))
                blasts[len(blasts)-1].kirakira = True
                blasts[len(blasts)-1].kirakira_cnt = KIRAKIRA_CNT
                self.kirakira_cnt = KIRAKIRA_CNT
                self.kirakira_x = self.miku.x
                self.kirakira_y = self.miku.y
                pyxel.play(2, 6)

        # 合計得点の更新
        self.score_total = self.score_0 + self.score_1 + self.score_2 + self.score_3 + \
                           self.score_4 + self.score_5 + self.score_6 + self.score_sushiall + self.score_shoyu
            
    def draw(self): # 描画処理
        # 画面背景タイルマップを指定
        # pyxel.bltm(0, 0, 0,  0, 0, 300, 300) # 青海波
        # pyxel.bltm(0, 0, 0, 480, 256, 300, 300) # 昼間の町
        pyxel.bltm(0, 0, 0, 512 + pyxel.frame_count % 256, 0, 300, 200) # 夕暮れの町

        # frame_countの24スパン内で挙動を変えながら寿司を描画する
        if(pyxel.frame_count % 24 in range(8,17)):
            for i in range(len(self.sushiset_f)):
                self.sushiset_f[i].draw_jump()
        else:
            for i in range(len(self.sushiset_f)):
                self.sushiset_f[i].draw_flow()

        # 醤油を描画する
        # self.shoyu.draw_flow()
        # self.shoyu2.draw_flow()

        # mikuを動かす
        self.miku.draw_circle()

        # mikuを周回する寿司衛星を描画する
        for i in range(len(self.sushiset_r)):
            if (self.sushiset_r[i].exists):
                self.sushiset_r[i].draw_circle()

        # mikuの周回後座標の計算、自位置座標を更新
        self.miku.update_torot()

        # シャリ弾
        draw_list(shari_bullets)
        # 敵寿司ネタ
        draw_list(sushineta)
        # 着弾時衝撃波
        draw_list(blasts)

        # 7種寿司を揃えたことの文字を表示し、キラキラ用ブラスト表示フレームカウントを減らす
        if(self.kirakira_cnt > 0):
            pyxel.text(self.kirakira_x, self.kirakira_y + 10, "Yummy!!", pyxel.frame_count % 16)
            self.kirakira_cnt -= 1

        # 醤油弾
        draw_list(shoyu_bullets)
        # 敵醤油
        draw_list(shoyu)

        # 雪を降らす
        for i in range(self.snow_all_amount):
            self.yukiset[i].draw_fall()

        # テキスト表示
        pyxel.text(100, 4, "SUSHI AWAITS ME TONIGHT !", pyxel.frame_count % 16)

        pyxel.text(10, 4, f"SCORE {self.score_total:5}", 7)

                        

class SATELLITE(GameObject):
    def __init__(self, base_x, base_y, radius, sat_num, order, center_adjust):
        super().__init__()
        self.radius = radius # 周回半径
        self.ddeg = 16 # 周回時偏角固定
        self.drad = math.radians(self.ddeg)
        # 初期位置
        self.initposition(base_x, base_y, radius, sat_num, order, center_adjust)
        # 回転基準位置
        self.BASE_X = base_x
        self.BASE_Y = base_y
        # 回転後位置（一旦、初期位置）
        self.rotated_X = self.x
        self.rotated_Y = self.y
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
    def update(self): # フレームの更新処理
        # 回転先の座標を計算して位置情報を更新
        self.rotate()
        self.x = self.rotated_X
        self.y = self.rotated_Y
    def baseupdate(self, base_x, base_y): 
        # 回転の基準点を引数の値に更新
        self.BASE_X = base_x
        self.BASE_Y = base_y   
    def rotate(self):
        # 周回後の位置を決定する
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

class MIKU(SATELLITE):
    # 初期化
    def __init__(self, base_x, base_y, flg_rot, radius, sat_num, order, center_adjust):
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
    def update_btn(self):
        self.dx = 0
        self.dy = 0
        # 左右キーに動きを対応させる
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            if (self.x >  MIKU_SPEED): # 画面端に達しているときは当該方向への増分をセットしない
                self.dx = -MIKU_SPEED
        elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            if (self.x <  pyxel.width - self.size):
                self.dx = MIKU_SPEED
        # 上下キーに動きを対応させる
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            if (self.y > MIKU_SPEED):
                self.dy = -MIKU_SPEED
        elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            if (self.y < pyxel.height - self.size):
                self.dy = MIKU_SPEED
        if(self.dx == 0 and self.dy == 0):
            return # 動いていない
        # 移動範囲を制限
        self.x = max(self.x, 0)
        self.x = min(self.x, pyxel.width - self.size)
        self.y = max(self.y, 0)
        self.y = min(self.y, pyxel.height - self.size)

    def update_base(self, base_x, base_y):
            # 回転の基準点を引数の内容に更新
        if (self.FLG_ROT):
            super().baseupdate(base_x, base_y) 
    def update_torot(self):
            # 周回後座標を計算して現在地を更新する
        if (self.FLG_ROT):
            super().update()

    def update_shari(self):
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            SHARI(self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y - BULLET_HEIGHT / 2)
            pyxel.play(0, 4)
    def draw_circle(self): # 描画処理（自転のみ）
        pyxel.blt(self.x, self.y, \
             1, 0, 16*(pyxel.frame_count % 8), 16, 16, 0)
    def draw_flow(self): # 描画処理（流れる）
        pyxel.blt((pyxel.frame_count  + self.x) % pyxel.width, \
             self.y, \
             1, 0, 16*(pyxel.frame_count % 8), 16, 16, 0)
    def draw_jump(self): # 描画処理（跳ねる）
        pyxel.blt((pyxel.frame_count +  self.x) % pyxel.width, \
             self.y - math.ceil(10*math.sin((pyxel.frame_count + self.x + self.y) % 90)), \
             1, 0, 16*(pyxel.frame_count % 8), 16, 16, 0)

class SUSHI(SATELLITE):
    # 初期化
    def __init__(self, neta, base_x, base_y, flg_rot, radius, sat_num, order, center_adjust):
        self.FLG_ROT = flg_rot
        # 回転フラグがTrueの場合衛星としての振舞いを有効にする。
        # そうでない場合は引数座標を初期位置座標として用いる。
        if (self.FLG_ROT):
            super().__init__(base_x, base_y, radius, sat_num, order, center_adjust)
        else:
            self.x = base_x
            self.y = base_y
        self.NETA = 16 * neta # 0:まぐろ 1:はまち 2:たまご 3:とろ軍艦 4:サーモン 5:えび 6:さんま
    # def update_btn(self):
    #     if pyxel.btnp(pyxel.KEY_SPACE):
    #         if (self.exists):
    #             self.exists = False
    #         else:
    #             self.exists = True
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
    def __init__(self, x, y):
        # 射出時点の指定座標で生成
        self.x = x
        self.y = y
        self.w = BULLET_WIDTH
        self.h = BULLET_HEIGHT
        self.is_alive = True
        shari_bullets.append(self)

    def update(self):
        self.x += BULLET_SPEED
        # 射出方向の画面端（今回はX軸方向）に達したとき弾の存在フラグを消す
        if self.x + self.w - 1 > pyxel.width:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 1, 16, 128 + 8*(pyxel.frame_count % 2), 8, 8, 0)


class NETA(GameObject):
    # 敵
    def __init__(self, x, y, pattern):
        self.x = x
        self.y = y
        self.pattern = pattern
        self.w = ENEMY_WIDTH
        self.h = ENEMY_HEIGHT
        self.dir = 1
        self.timer_offset = pyxel.rndi(0, 59)
        self.is_alive = True
        sushineta.append(self)

    def update(self):
        if (pyxel.frame_count + self.timer_offset) % 60 < 30:
            self.y += ENEMY_SPEED
            self.dir = 1
        else:
            self.y -= ENEMY_SPEED
            self.dir = -1
        self.x -= ENEMY_SPEED
        if self.x -self.w + 21 < 0:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 112 + 16*self.pattern, 16*(pyxel.frame_count % 2), 16, 16, 11)

# class SHOYU(GameObject):
#     # 初期化
#     def __init__(self, base_x, base_y):
#         self.x = base_x # 初期位置Ⅹ軸
#         self.y = base_y # 初期位置Ｙ軸
#     def update(self): # フレームの更新処理
#         """NONE"""
#     def draw_flow(self): # 描画処理（流れる）
#         pyxel.blt((pyxel.frame_count  + self.x) % pyxel.width, self.y, \
#                 1, 16, 16*(pyxel.frame_count % 8), \
#                  16, 16, 3)

class SHOYU(GameObject):
    # 敵醤油
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = SHOYU_WIDTH
        self.h = SHOYU_HEIGHT
        self.dir = 1
        self.timer_offset = pyxel.rndi(0, 59)
        self.is_alive = True
        shoyu.append(self)

    def update(self):
        if (pyxel.frame_count + self.timer_offset) % 60 < 30:
            self.y += SHOYU_SPEED
            self.dir = 1
        else:
            self.y -= SHOYU_SPEED
            self.dir = -1
        self.x -= SHOYU_SPEED
        if self.x -self.w + 21 < 0:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 1, 16, 16*(pyxel.frame_count % 8), -16, 16, 3)

    def update_shoyu_bullet(self):
        if ((pyxel.frame_count + self.timer_offset) % 40 == 20):
            SHOYUBULLET(self.x + (SHOYU_WIDTH - SHOYU_BULLET_WIDTH) / 2, self.y - SHOYU_BULLET_HEIGHT / 2)
            # pyxel.play(0, 4)

class SHOYUBULLET(GameObject):
    def __init__(self, x, y):
        # 射出時点の指定座標で生成
        self.x = x
        self.y = y
        self.w = SHOYU_BULLET_WIDTH
        self.h = SHOYU_BULLET_HEIGHT
        self.is_alive = True
        shoyu_bullets.append(self)

    def update(self):
        self.x -= SHOYU_BULLET_SPEED
        # 射出方向の画面端（今回は-X軸方向）に達したとき弾の存在フラグを消す
        if self.x + self.w - 8 < 0:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 1, 24, 128 + 8*(pyxel.frame_count % 2), 8, 8, 0)

class Blast: # 着弾時の衝撃波
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BLAST_START_RADIUS
        self.is_alive = True
        self.kirakira = False
        self.kirakira_cnt = 0
        blasts.append(self)

    def update(self):
        if(self.kirakira):
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
        else:
            pyxel.circ(self.x, self.y, self.radius, BLAST_COLOR_IN)
            pyxel.circb(self.x, self.y, self.radius, BLAST_COLOR_OUT)

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
