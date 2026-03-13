"""
植物大战僵尸 - 第1-1关完整版
Plants vs. Zombies - Level 1-1 Complete Recreation

运行方式: python pvz_game.py
依赖: pygame (pip install pygame)
"""

import os
import sys
import math
import random

# ---------------------------------------------------------------------------
# 优先使用软件渲染，避免无显示器环境报错
os.environ.setdefault("SDL_VIDEODRIVER", "x11")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
# ---------------------------------------------------------------------------

import pygame

pygame.init()
pygame.mixer.init()

# ============================================================
# 常量
# ============================================================
SCREEN_W = 900
SCREEN_H = 600
FPS = 60
TITLE = "植物大战僵尸"

# 颜色
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
GRAY        = (128, 128, 128)
RED         = (220,  50,  50)
GREEN       = ( 50, 180,  50)
YELLOW      = (255, 220,   0)
GRASS_A     = (124, 179,  66)   # 浅草色
GRASS_B     = (100, 153,  52)   # 深草色
DIRT        = (110,  75,  35)
HUD_BG      = ( 74,  46,  13)
HUD_BORDER  = ( 50,  30,   5)
SUN_YELLOW  = (255, 228,   0)

# 格子参数
GRID_X    = 80    # 格子左边缘
GRID_Y    = 72    # 格子上边缘（HUD下方）
CELL_W    = 75    # 格子宽
CELL_H    = 90    # 格子高
GRID_ROWS = 5
GRID_COLS = 9
GRID_W    = CELL_W * GRID_COLS   # 675
GRID_H    = CELL_H * GRID_ROWS   # 450

# 割草机位置 x（格子左侧）
MOWER_X = 45

# 植物类型
PT_SUNFLOWER  = 1
PT_PEASHOOTER = 2

# 僵尸类型
ZT_BASIC = 1

# 游戏状态
ST_INTRO   = 0
ST_MENU    = 1
ST_PLAYING = 2
ST_WIN     = 3
ST_LOSE    = 4

# ============================================================
# 植物 / 僵尸 数据
# ============================================================
PLANT_DATA = {
    PT_SUNFLOWER: {
        "name": "向日葵",
        "cost": 50,
        "hp": 300,
        "card_cooldown": 7.0,
        "sun_interval": 24.0,
        "sun_amount": 25,
    },
    PT_PEASHOOTER: {
        "name": "豌豆射手",
        "cost": 100,
        "hp": 300,
        "card_cooldown": 7.5,
        "fire_interval": 1.4,
        "pea_damage": 20,
        "pea_speed": 250,
    },
}

ZOMBIE_DATA = {
    ZT_BASIC: {
        "name": "普通僵尸",
        "hp": 270,
        "speed": 30,    # px/秒
        "dps": 100,     # 对植物每秒伤害
    },
}

# 波次数据: (触发时间秒, 僵尸类型, 数量, 是否旗帜波)
WAVE_DATA = [
    (18,  ZT_BASIC, 1, False),
    (42,  ZT_BASIC, 1, False),
    (68,  ZT_BASIC, 2, True),
    (98,  ZT_BASIC, 1, False),
    (122, ZT_BASIC, 2, False),
    (150, ZT_BASIC, 4, True),
]

# ============================================================
# 字体工具
# ============================================================
_font_cache: dict = {}


def get_font(size: int) -> pygame.font.Font:
    """获取支持中文的字体。"""
    if size in _font_cache:
        return _font_cache[size]
    candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    font = None
    for path in candidates:
        if os.path.exists(path):
            font = pygame.font.Font(path, size)
            break
    if font is None:
        font = pygame.font.SysFont("sans", size)
    _font_cache[size] = font
    return font


def render_text(text: str, size: int, color) -> pygame.Surface:
    return get_font(size).render(text, True, color)


def draw_text(surface: pygame.Surface, text: str, size: int, color,
              cx: float, cy: float) -> None:
    """以 (cx, cy) 为中心绘制文字。"""
    surf = render_text(text, size, color)
    rect = surf.get_rect(center=(int(cx), int(cy)))
    surface.blit(surf, rect)


def draw_text_shadow(surface: pygame.Surface, text: str, size: int,
                     color, cx: float, cy: float,
                     shadow_color=(0, 0, 0)) -> None:
    """绘制带阴影的文字。"""
    shadow = render_text(text, size, shadow_color)
    main = render_text(text, size, color)
    rect = main.get_rect(center=(int(cx), int(cy)))
    surface.blit(shadow, (rect.x + 3, rect.y + 3))
    surface.blit(main, rect)


# ============================================================
# 绘制 / 精灵函数
# ============================================================

def draw_rounded_rect(surface: pygame.Surface, color, rect,
                      radius: int = 8, border: int = 0,
                      border_color=None) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border,
                         border_radius=radius)


def draw_sunflower(surface: pygame.Surface, x: int, y: int,
                   frame: int = 0, health_ratio: float = 1.0) -> None:
    """在格子 (x, y) 处绘制向日葵。"""
    cx = x + CELL_W // 2
    cy = y + CELL_H // 2 - 5
    sway = int(math.sin(frame * 0.05) * 3)

    # 花盆
    pot_color = (120, 80, 40) if health_ratio > 0.5 else (80, 50, 25)
    pot_top = cy + 25
    pygame.draw.polygon(surface, pot_color, [
        (cx - 14, pot_top),
        (cx + 14, pot_top),
        (cx + 10, pot_top + 20),
        (cx - 10, pot_top + 20),
    ])
    pygame.draw.rect(surface, (90, 60, 25), (cx - 14, pot_top - 4, 28, 6))

    # 茎
    stem_color = (55, 130, 50) if health_ratio > 0.3 else (90, 110, 50)
    pygame.draw.line(surface, stem_color,
                     (cx + sway // 2, pot_top),
                     (cx, cy - 15), 4)

    # 叶子
    lc = (70, 150, 55)
    pygame.draw.polygon(surface, lc,
                        [(cx, cy), (cx - 22, cy - 8), (cx - 17, cy + 8)])
    pygame.draw.polygon(surface, lc,
                        [(cx, cy + 5), (cx + 22, cy - 3), (cx + 17, cy + 12)])

    # 花瓣（8片）
    head_cx, head_cy = cx, cy - 15
    pc = (255, 220, 0) if health_ratio > 0.3 else (200, 170, 0)
    for i in range(8):
        ang = math.radians(i * 45 + frame * 1.5)
        px = head_cx + math.cos(ang) * 16
        py = head_cy + math.sin(ang) * 16
        pygame.draw.ellipse(surface, pc,
                            (int(px) - 7, int(py) - 5, 14, 10))

    # 花心
    pygame.draw.circle(surface, (150, 90, 30), (head_cx, head_cy), 11)
    pygame.draw.circle(surface, (120, 70, 20), (head_cx, head_cy), 8)

    # 花心表情
    ec = (200, 130, 50)
    pygame.draw.circle(surface, ec, (head_cx - 3, head_cy - 2), 2)
    pygame.draw.circle(surface, ec, (head_cx + 3, head_cy - 2), 2)
    pygame.draw.arc(surface, ec,
                    (head_cx - 4, head_cy + 1, 8, 5),
                    math.pi, 2 * math.pi, 1)


def draw_peashooter(surface: pygame.Surface, x: int, y: int,
                    frame: int = 0, shooting: bool = False,
                    health_ratio: float = 1.0) -> None:
    """在格子 (x, y) 处绘制豌豆射手。"""
    cx = x + CELL_W // 2
    cy = y + CELL_H // 2

    # 花盆
    pc = (100, 65, 30) if health_ratio > 0.5 else (70, 45, 20)
    pygame.draw.polygon(surface, pc, [
        (cx - 16, cy + 22),
        (cx + 16, cy + 22),
        (cx + 12, cy + 38),
        (cx - 12, cy + 38),
    ])
    pygame.draw.rect(surface, (80, 50, 20), (cx - 16, cy + 18, 32, 6))

    # 身体
    bc = (50, 155, 50) if health_ratio > 0.3 else (100, 130, 60)
    pygame.draw.ellipse(surface, bc, (cx - 22, cy - 18, 44, 42))
    pygame.draw.ellipse(surface, (80, 190, 80), (cx - 12, cy - 14, 14, 10))

    # 炮管
    tc = (40, 130, 40)
    tube_y = cy - 2
    pygame.draw.rect(surface, tc, (cx + 15, tube_y - 6, 28, 12))
    pygame.draw.rect(surface, (30, 110, 30), (cx + 37, tube_y - 8, 6, 16))

    # 眼睛
    pygame.draw.circle(surface, (255, 255, 200), (cx - 5, cy - 8), 6)
    pygame.draw.circle(surface, (255, 255, 200), (cx + 8, cy - 8), 6)
    ey = cy - 8 + (2 if shooting else 0)
    pygame.draw.circle(surface, (30, 30, 100), (cx - 4, ey), 3)
    pygame.draw.circle(surface, (30, 30, 100), (cx + 9, ey), 3)
    pygame.draw.circle(surface, WHITE, (cx - 6, ey - 2), 1)
    pygame.draw.circle(surface, WHITE, (cx + 7, ey - 2), 1)


def draw_zombie(surface: pygame.Surface, x: float, y: float,
                frame: int = 0, health_ratio: float = 1.0) -> None:
    """以 (x, y) 为中心绘制普通僵尸。"""
    wc = frame % 40
    bob = int(math.sin(wc * math.pi / 20) * 3)
    ll = int(math.sin(wc * math.pi / 20) * 8)
    lr = -ll

    body_c = (160, 185, 140) if health_ratio > 0.5 else (140, 155, 115)
    shirt_c = (90, 100, 85)
    skin_c = (170, 200, 150)
    hair_c = (50, 45, 35)

    zx, zy = int(x), int(y + bob)

    # 阴影
    shd = pygame.Surface((50, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(shd, (0, 0, 0, 60), (0, 0, 50, 10))
    surface.blit(shd, (zx - 25, zy + 28))

    # 腿
    pygame.draw.rect(surface, shirt_c,
                     (zx - 12, zy + 10 + ll, 10, 22))
    pygame.draw.rect(surface, shirt_c,
                     (zx + 2,  zy + 10 + lr, 10, 22))

    # 身体
    pygame.draw.rect(surface, shirt_c, (zx - 16, zy - 8, 32, 22))

    # 左臂（前伸）
    pygame.draw.rect(surface, skin_c, (zx - 28, zy - 12, 14, 8))
    # 右臂
    pygame.draw.rect(surface, skin_c, (zx + 16, zy - 6, 12, 8))

    # 颈部
    pygame.draw.rect(surface, skin_c, (zx - 6, zy - 16, 12, 10))

    # 头部
    hc = skin_c if health_ratio > 0.4 else (180, 195, 140)
    pygame.draw.rect(surface, hc,
                     (zx - 14, zy - 36, 28, 24), border_radius=4)

    # 头发
    pygame.draw.rect(surface, hair_c,
                     (zx - 14, zy - 36, 28, 8), border_radius=4)
    pygame.draw.rect(surface, hair_c, (zx + 6, zy - 44, 8, 12))
    pygame.draw.rect(surface, hair_c, (zx - 4, zy - 42, 6, 10))

    # 眼睛
    pygame.draw.rect(surface, WHITE,
                     (zx - 11, zy - 28, 8, 6), border_radius=2)
    pygame.draw.rect(surface, WHITE,
                     (zx + 3,  zy - 28, 8, 6), border_radius=2)
    pygame.draw.circle(surface, (20, 20, 20), (zx - 7, zy - 25), 2)
    pygame.draw.circle(surface, (20, 20, 20), (zx + 7, zy - 25), 2)

    # 嘴
    pygame.draw.rect(surface, (100, 60, 60),
                     (zx - 6, zy - 18, 12, 6), border_radius=2)

    # 领带
    pygame.draw.polygon(surface, (180, 30, 30), [
        (zx, zy - 8), (zx - 4, zy - 4),
        (zx, zy + 10), (zx + 4, zy - 4),
    ])

    if health_ratio < 0.5:
        pygame.draw.line(surface, (200, 50, 50),
                         (zx - 8, zy - 32), (zx + 4, zy - 20), 2)


def draw_pea(surface: pygame.Surface, x: float, y: float) -> None:
    pygame.draw.circle(surface, (50, 190, 50), (int(x), int(y)), 7)
    pygame.draw.circle(surface, (80, 220, 80), (int(x) - 2, int(y) - 2), 3)


def draw_sun(surface: pygame.Surface, x: float, y: float,
             size: int = 28, frame: int = 0) -> None:
    """绘制太阳（含光芒动画）。"""
    ray_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
    rc = size * 2
    for i in range(12):
        ang = math.radians(i * 30 + frame * 3)
        inner, outer = size + 2, size + 10
        x1 = rc + math.cos(ang) * inner
        y1 = rc + math.sin(ang) * inner
        x2 = rc + math.cos(ang) * outer
        y2 = rc + math.sin(ang) * outer
        pygame.draw.line(ray_surf, (255, 220, 0, 160),
                         (int(x1), int(y1)), (int(x2), int(y2)), 3)
    surface.blit(ray_surf, (int(x) - rc, int(y) - rc))

    pygame.draw.circle(surface, SUN_YELLOW, (int(x), int(y)), size)
    pygame.draw.circle(surface, (255, 210, 0), (int(x), int(y)), size - 3)

    # 表情
    ec = (180, 130, 0)
    pygame.draw.circle(surface, ec, (int(x) - 8, int(y) - 6), 3)
    pygame.draw.circle(surface, ec, (int(x) + 8, int(y) - 6), 3)
    pygame.draw.circle(surface, (100, 80, 0), (int(x) - 7, int(y) - 6), 2)
    pygame.draw.circle(surface, (100, 80, 0), (int(x) + 9, int(y) - 6), 2)
    pygame.draw.arc(surface, ec,
                    (int(x) - 10, int(y) - 2, 20, 14),
                    math.pi, 2 * math.pi, 2)


def draw_lawnmower(surface: pygame.Surface, x: float, y: float) -> None:
    ix, iy = int(x), int(y)
    pygame.draw.rect(surface, (220, 80, 30),
                     (ix - 20, iy - 12, 40, 22), border_radius=4)
    for wx in (ix - 14, ix + 14):
        pygame.draw.circle(surface, (40, 40, 40), (wx, iy + 12), 8)
        pygame.draw.circle(surface, (80, 80, 80), (wx, iy + 12), 5)
    pygame.draw.line(surface, (100, 60, 20),
                     (ix + 18, iy - 12), (ix + 22, iy - 28), 4)
    pygame.draw.line(surface, (100, 60, 20),
                     (ix + 22, iy - 28), (ix + 10, iy - 28), 4)
    pygame.draw.rect(surface, (200, 200, 50),
                     (ix - 22, iy + 8, 4, 6))


def draw_mini_sunflower(surface: pygame.Surface, cx: int, cy: int) -> None:
    for i in range(8):
        ang = math.radians(i * 45)
        px = cx + math.cos(ang) * 10
        py = cy + math.sin(ang) * 10
        pygame.draw.circle(surface, (255, 215, 0), (int(px), int(py)), 5)
    pygame.draw.circle(surface, (140, 85, 30), (cx, cy), 7)


def draw_mini_peashooter(surface: pygame.Surface, cx: int, cy: int) -> None:
    pygame.draw.ellipse(surface, (50, 165, 50),
                        (cx - 14, cy - 12, 28, 26))
    pygame.draw.rect(surface, (35, 120, 35),
                     (cx + 10, cy - 4, 18, 8))


def draw_plant_card(surface: pygame.Surface,
                    rect: tuple,
                    plant_type: int,
                    cooldown_ratio: float = 0.0,
                    selected: bool = False,
                    can_afford: bool = True) -> None:
    x, y, w, h = rect
    if selected:
        bg, border = (255, 240, 150), (255, 200, 0)
    elif not can_afford:
        bg, border = (100, 80, 60), (70, 55, 40)
    else:
        bg, border = (180, 150, 100), (140, 110, 70)

    draw_rounded_rect(surface, bg, rect, radius=5,
                      border=2, border_color=border)

    icon_h = h - 22
    mini = pygame.Surface((w - 4, icon_h), pygame.SRCALPHA)
    mcx, mcy = (w - 4) // 2, icon_h // 2
    if plant_type == PT_SUNFLOWER:
        draw_mini_sunflower(mini, mcx, mcy)
    else:
        draw_mini_peashooter(mini, mcx, mcy)
    surface.blit(mini, (x + 2, y + 2))

    # 费用
    cost_color = YELLOW if can_afford else GRAY
    cost = render_text(str(PLANT_DATA[plant_type]["cost"]), 13, cost_color)
    cr = cost.get_rect(centerx=x + w // 2, bottom=y + h - 2)
    surface.blit(cost, cr)

    # 冷却遮罩
    if cooldown_ratio > 0:
        ov = pygame.Surface((w - 4, max(1, int(icon_h * cooldown_ratio))),
                            pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        surface.blit(ov, (x + 2, y + 2))


def draw_sun_counter(surface: pygame.Surface,
                     x: int, y: int, amount: int) -> None:
    draw_rounded_rect(surface, (60, 40, 10),
                      (x, y, 78, 50), radius=8,
                      border=2, border_color=(40, 25, 5))
    draw_sun(surface, x + 22, y + 25, size=14, frame=0)
    num = render_text(str(amount), 20, YELLOW)
    surface.blit(num, num.get_rect(midleft=(x + 40, y + 25)))


def draw_hud_background(surface: pygame.Surface) -> None:
    pygame.draw.rect(surface, HUD_BG, (0, 0, SCREEN_W, 72))
    for i in range(0, SCREEN_W, 14):
        pygame.draw.line(surface, (85, 55, 18), (i, 0), (i + 6, 72), 1)
    pygame.draw.rect(surface, HUD_BORDER, (0, 68, SCREEN_W, 4))


def draw_lawn_background(surface: pygame.Surface) -> None:
    """绘制草坪背景。"""
    # 天空
    pygame.draw.rect(surface, (100, 180, 240), (0, 0, SCREEN_W, GRID_Y + 10))
    # 交替草条
    for row in range(GRID_ROWS):
        color = GRASS_A if row % 2 == 0 else GRASS_B
        pygame.draw.rect(surface, color,
                         (0, GRID_Y + row * CELL_H, SCREEN_W, CELL_H))
    # 下方土地
    dirt_y = GRID_Y + GRID_H
    pygame.draw.rect(surface, DIRT,
                     (0, dirt_y, SCREEN_W, SCREEN_H - dirt_y))
    # 格子线（淡）
    lc = (0, 0, 0)
    for col in range(GRID_COLS + 1):
        lx = GRID_X + col * CELL_W
        pygame.draw.line(surface, lc, (lx, GRID_Y), (lx, GRID_Y + GRID_H), 1)
    for row in range(GRID_ROWS + 1):
        ly = GRID_Y + row * CELL_H
        pygame.draw.line(surface, lc,
                         (GRID_X, ly), (GRID_X + GRID_W, ly), 1)


def draw_house(surface: pygame.Surface) -> None:
    """绘制左侧房子。"""
    # 房身
    pygame.draw.rect(surface, (220, 195, 155),
                     (5, GRID_Y + 20, 55, GRID_H - 40))
    # 屋顶
    pygame.draw.polygon(surface, (180, 100, 50), [
        (0,  GRID_Y + 20),
        (30, GRID_Y - 10),
        (60, GRID_Y + 20),
    ])
    # 门
    pygame.draw.rect(surface, (140, 90, 50),
                     (22, GRID_Y + GRID_H - 75, 22, 40))
    # 窗户
    for wx, wy in ((8, GRID_Y + 30), (35, GRID_Y + 30),
                   (8, GRID_Y + 70), (35, GRID_Y + 70)):
        pygame.draw.rect(surface, (200, 230, 255), (wx, wy, 18, 18))
        pygame.draw.line(surface, (150, 180, 210),
                         (wx + 9, wy), (wx + 9, wy + 18), 1)
        pygame.draw.line(surface, (150, 180, 210),
                         (wx, wy + 9), (wx + 18, wy + 9), 1)


# ============================================================
# 实体类
# ============================================================

class Plant:
    def __init__(self, plant_type: int, col: int, row: int) -> None:
        self.plant_type = plant_type
        self.col = col
        self.row = row
        data = PLANT_DATA[plant_type]
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.frame = 0
        self.dead = False
        self.x = GRID_X + col * CELL_W
        self.y = GRID_Y + row * CELL_H

        if plant_type == PT_SUNFLOWER:
            self.sun_timer = data["sun_interval"] * 0.5
        if plant_type == PT_PEASHOOTER:
            self.fire_timer = 0.0
            self.shooting = False

    def update(self, dt: float, game) -> None:
        self.frame += 1
        if self.dead:
            return

        if self.plant_type == PT_SUNFLOWER:
            self.sun_timer -= dt
            if self.sun_timer <= 0:
                self.sun_timer = PLANT_DATA[PT_SUNFLOWER]["sun_interval"]
                sx = self.x + CELL_W // 2 + random.randint(-20, 20)
                sy = self.y + CELL_H // 2
                game.suns.append(Sun(sx, sy, from_flower=True,
                                     target_y=sy + 35))

        elif self.plant_type == PT_PEASHOOTER:
            has_target = any(
                z.row == self.row and z.x > self.x and not z.dead
                for z in game.zombies
            )
            self.shooting = has_target
            if has_target:
                self.fire_timer -= dt
                if self.fire_timer <= 0:
                    d = PLANT_DATA[PT_PEASHOOTER]
                    self.fire_timer = d["fire_interval"]
                    px = self.x + CELL_W + 5
                    py = self.y + CELL_H // 2
                    game.projectiles.append(
                        Projectile(px, py, self.row,
                                   d["pea_speed"], d["pea_damage"])
                    )

    def take_damage(self, dmg: float) -> None:
        self.hp -= dmg
        if self.hp <= 0:
            self.dead = True

    def draw(self, surface: pygame.Surface) -> None:
        hr = self.hp / self.max_hp
        if self.plant_type == PT_SUNFLOWER:
            draw_sunflower(surface, self.x, self.y, self.frame, hr)
        elif self.plant_type == PT_PEASHOOTER:
            draw_peashooter(surface, self.x, self.y, self.frame,
                            getattr(self, "shooting", False), hr)
        if self.hp < self.max_hp and not self.dead:
            bw = CELL_W - 10
            bx, by = self.x + 5, self.y + CELL_H - 12
            pygame.draw.rect(surface, RED, (bx, by, bw, 6))
            pygame.draw.rect(surface, GREEN,
                             (bx, by, int(bw * hr), 6))


class Zombie:
    def __init__(self, zombie_type: int, row: int) -> None:
        self.zombie_type = zombie_type
        self.row = row
        data = ZOMBIE_DATA[zombie_type]
        self.hp = float(data["hp"])
        self.max_hp = float(data["hp"])
        self.speed = float(data["speed"])
        self.dps = float(data["dps"])
        self.frame = 0
        self.dead = False
        self.eating = False
        self.x = float(SCREEN_W + 50)
        self.y = float(GRID_Y + row * CELL_H + CELL_H // 2)

    def update(self, dt: float, game) -> None:
        self.frame += 1
        if self.dead:
            return

        self.eating = False
        for plant in game.plants:
            if plant.row == self.row and not plant.dead:
                pr = plant.x + CELL_W - 5
                pl = plant.x + 5
                if self.x - 20 <= pr and self.x + 10 >= pl:
                    self.eating = True
                    plant.take_damage(self.dps * dt)
                    break

        if not self.eating:
            self.x -= self.speed * dt

        if self.x <= MOWER_X + 25:
            mower = game.get_mower(self.row)
            if mower and not mower.activated:
                mower.activate(game)

    def take_damage(self, dmg: float) -> None:
        self.hp -= dmg
        if self.hp <= 0:
            self.dead = True

    def draw(self, surface: pygame.Surface) -> None:
        hr = self.hp / self.max_hp
        draw_zombie(surface, self.x, self.y, self.frame, hr)
        bw = 44
        bx = int(self.x) - bw // 2
        by = int(self.y) - 48
        pygame.draw.rect(surface, RED, (bx, by, bw, 5))
        pygame.draw.rect(surface, GREEN, (bx, by, max(0, int(bw * hr)), 5))


class Projectile:
    def __init__(self, x: float, y: float, row: int,
                 speed: float, damage: float) -> None:
        self.x = x
        self.y = y
        self.row = row
        self.speed = speed
        self.damage = damage
        self.dead = False

    def update(self, dt: float, game) -> None:
        self.x += self.speed * dt
        for z in game.zombies:
            if z.row == self.row and not z.dead:
                if abs(self.x - z.x) < 20 and abs(self.y - z.y) < 30:
                    z.take_damage(self.damage)
                    self.dead = True
                    return
        if self.x > SCREEN_W + 20:
            self.dead = True

    def draw(self, surface: pygame.Surface) -> None:
        draw_pea(surface, self.x, self.y)


class Sun:
    def __init__(self, x: float, y: float, from_flower: bool = False,
                 target_y: float = None) -> None:
        self.x = x
        self.y = y
        self.from_flower = from_flower
        self.target_y = target_y if target_y is not None else y + random.randint(80, 160)
        self.frame = 0
        self.dead = False
        self.value = 25
        self.lifetime = 10.0
        self.landed = False

    def update(self, dt: float) -> None:
        self.frame += 1
        if not self.landed:
            if self.y < self.target_y:
                self.y += 60.0 * dt
            else:
                self.landed = True
        else:
            self.lifetime -= dt
        if self.lifetime <= 0:
            self.dead = True

    def collect(self) -> int:
        self.dead = True
        return self.value

    def check_click(self, mx: int, my: int) -> bool:
        return math.hypot(mx - self.x, my - self.y) < 28

    def draw(self, surface: pygame.Surface) -> None:
        alpha = 255
        if self.lifetime < 2.0:
            alpha = max(0, int(255 * self.lifetime / 2.0))
        if alpha < 255:
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            draw_sun(s, 60, 60, 28, self.frame)
            s.set_alpha(alpha)
            surface.blit(s, (int(self.x) - 60, int(self.y) - 60))
        else:
            draw_sun(surface, self.x, self.y, 28, self.frame)


class LawnMower:
    def __init__(self, row: int) -> None:
        self.row = row
        self.x = float(MOWER_X)
        self.y = float(GRID_Y + row * CELL_H + CELL_H // 2)
        self.activated = False
        self.dead = False
        self.speed = 650.0

    def activate(self, game) -> None:
        self.activated = True

    def update(self, dt: float, game) -> None:
        if self.activated:
            self.x += self.speed * dt
            for z in game.zombies:
                if z.row == self.row and not z.dead:
                    if abs(self.x - z.x) < 30:
                        z.dead = True
            if self.x > SCREEN_W + 60:
                self.dead = True

    def draw(self, surface: pygame.Surface) -> None:
        if not self.dead:
            draw_lawnmower(surface, self.x, self.y)


# ============================================================
# 画面类
# ============================================================

class IntroScreen:
    """片头动画 (PopCap logo → 游戏标题)"""

    def __init__(self) -> None:
        self.timer = 0.0
        self.phase = 0   # 0=logo  1=title
        self.done = False

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.phase == 0 and self.timer > 2.8:
            self.phase = 1
            self.timer = 0.0
        elif self.phase == 1 and self.timer > 4.5:
            self.done = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.done = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)
        t = self.timer

        if self.phase == 0:
            # ---- PopCap 标志 ----
            if t < 1.0:
                alpha = int(t * 255)
            elif t < 1.8:
                alpha = 255
            else:
                alpha = max(0, int(255 - (t - 1.8) * 280))
            logo = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            pygame.draw.circle(logo, (0, 150, 255, alpha),
                               (SCREEN_W // 2, SCREEN_H // 2 - 40), 65)
            pygame.draw.circle(logo, (255, 255, 255, alpha),
                               (SCREEN_W // 2 - 20, SCREEN_H // 2 - 55), 15)
            txt = render_text("PopCap Games", 36, WHITE)
            txt.set_alpha(alpha)
            surface.blit(logo, (0, 0))
            surface.blit(txt, txt.get_rect(
                center=(SCREEN_W // 2, SCREEN_H // 2 + 50)))

        else:
            # ---- 游戏标题 ----
            # 渐变背景
            for i in range(SCREEN_H):
                r = i / SCREEN_H
                pygame.draw.line(surface,
                                 (int(20 + r * 30),
                                  int(60 + r * 80),
                                  int(10 + r * 20)),
                                 (0, i), (SCREEN_W, i))

            # 动态太阳
            sx = SCREEN_W // 2 + int(math.sin(t * 1.5) * 50)
            sy = 100 + int(math.cos(t) * 20)
            draw_sun(surface, sx, sy, 45, int(t * 30))

            # 标题淡入
            ta = min(255, int(t * 130))
            title_bg = render_text("植物大战僵尸", 80, (0, 80, 0))
            title_bg.set_alpha(ta // 2)
            title_fg = render_text("植物大战僵尸", 80, (80, 220, 50))
            title_fg.set_alpha(ta)
            for surf, off in ((title_bg, 4), (title_fg, 0)):
                r = surf.get_rect(center=(SCREEN_W // 2 + off,
                                          SCREEN_H // 2 - 60 + off))
                surface.blit(surf, r)

            # 副标题
            if t > 1.2:
                sa = min(255, int((t - 1.2) * 200))
                sub = render_text("第1-1关 · 白昼", 40, (255, 230, 100))
                sub.set_alpha(sa)
                surface.blit(sub, sub.get_rect(
                    center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))

            # 植物和僵尸装饰
            if t > 1.8:
                pa = min(255, int((t - 1.8) * 200))
                dummy = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
                dummy.set_alpha(pa)
                draw_sunflower(dummy, 0, 0, int(t * 30))
                surface.blit(dummy, (SCREEN_W // 2 - 200,
                                     SCREEN_H // 2 + 90))
                draw_peashooter(surface,
                                SCREEN_W // 2 - 100,
                                SCREEN_H // 2 + 90,
                                int(t * 20))
                draw_zombie(surface,
                            SCREEN_W // 2 + 160 + int(math.sin(t) * 5),
                            SCREEN_H // 2 + 135,
                            int(t * 30))

            # 提示文字（闪烁）
            if t > 2.8 and int(t * 4) % 2 == 0:
                hint = render_text("按任意键开始", 24, (255, 255, 200))
                surface.blit(hint, hint.get_rect(
                    center=(SCREEN_W // 2, SCREEN_H - 50)))


class MenuScreen:
    """主菜单"""

    def __init__(self) -> None:
        self.frame = 0
        self.hovered = -1
        self.result = None   # 'start' | 'quit'
        self._buttons = [
            {"text": "开始游戏",
             "rect": pygame.Rect(SCREEN_W // 2 - 120, 290, 240, 60)},
            {"text": "退出游戏",
             "rect": pygame.Rect(SCREEN_W // 2 - 120, 380, 240, 60)},
        ]

    def update(self, dt: float) -> None:
        self.frame += 1
        mx, my = pygame.mouse.get_pos()
        self.hovered = -1
        for i, btn in enumerate(self._buttons):
            if btn["rect"].collidepoint(mx, my):
                self.hovered = i

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn in enumerate(self._buttons):
                if btn["rect"].collidepoint(event.pos):
                    self.result = "start" if i == 0 else "quit"

    def draw(self, surface: pygame.Surface) -> None:
        f = self.frame
        # 草坪背景
        pygame.draw.rect(surface, (100, 180, 240),
                         (0, 0, SCREEN_W, GRID_Y + 10))
        for row in range(GRID_ROWS):
            c = GRASS_A if row % 2 == 0 else GRASS_B
            pygame.draw.rect(surface, c,
                             (0, GRID_Y + row * CELL_H, SCREEN_W, CELL_H))
        pygame.draw.rect(surface, DIRT,
                         (0, GRID_Y + GRID_H, SCREEN_W,
                          SCREEN_H - GRID_Y - GRID_H))

        # 装饰：太阳
        sx = 700 + int(math.sin(f * 0.02) * 30)
        sy = 80 + int(math.cos(f * 0.015) * 20)
        draw_sun(surface, sx, sy, 45, f)

        # 几株向日葵装饰
        for col in range(0, 9, 2):
            for row in range(GRID_ROWS):
                draw_sunflower(surface,
                               GRID_X + col * CELL_W,
                               GRID_Y + row * CELL_H,
                               f + col * 10 + row * 7)

        # 半透明面板
        panel = pygame.Surface((540, 380), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 100))
        pygame.draw.rect(panel, (0, 100, 0, 60), (0, 0, 540, 380),
                         border_radius=20)
        surface.blit(panel, (SCREEN_W // 2 - 270, 130))

        # 标题
        draw_text_shadow(surface, "植物大战僵尸", 70, (80, 230, 60),
                         SCREEN_W // 2, 195, (0, 60, 0))
        draw_text(surface, "第1-1关  ·  白昼", 28, (255, 230, 100),
                  SCREEN_W // 2, 250)

        # 按钮
        for i, btn in enumerate(self._buttons):
            r = btn["rect"]
            hov = (i == self.hovered)
            bg = (255, 200, 50) if hov else (100, 160, 60)
            bd = (255, 140, 0) if hov else (70, 120, 40)
            tc = (80, 30, 0) if hov else WHITE
            draw_rounded_rect(surface, bg, r, radius=12, border=3,
                              border_color=bd)
            draw_text(surface, btn["text"], 32, tc, r.centerx, r.centery)

        draw_text(surface, "用鼠标种植植物，点击阳光收集，消灭所有僵尸！",
                  16, (200, 220, 200), SCREEN_W // 2, SCREEN_H - 25)


class GameScreen:
    """游戏主画面（第1-1关）"""

    # HUD 卡片区域 (x, y, w, h)
    CARD_RECTS = [
        (98,  4, 78, 64),
        (180, 4, 78, 64),
    ]
    CARD_PLANTS = [PT_SUNFLOWER, PT_PEASHOOTER]
    SHOVEL_RECT = pygame.Rect(272, 10, 52, 52)

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.sun = 50
        self.plants: list[Plant] = []
        self.zombies: list[Zombie] = []
        self.projectiles: list[Projectile] = []
        self.suns: list[Sun] = []
        self.mowers: list[LawnMower] = [LawnMower(r) for r in range(GRID_ROWS)]

        self.selected_plant = None
        self.shovel_active = False
        self.card_cooldowns = {PT_SUNFLOWER: 0.0, PT_PEASHOOTER: 0.0}

        self.wave_index = 0
        self.game_timer = 0.0
        self.all_waves_done = False

        self.sky_sun_timer = random.uniform(5.0, 10.0)
        self.frame = 0
        self.result = None   # 'win' | 'lose'

        self.message = ""
        self.message_timer = 0.0
        self.hover_cell = None

    def get_mower(self, row: int):
        for m in self.mowers:
            if m.row == row and not m.dead:
                return m
        return None

    def update(self, dt: float) -> None:
        if self.result:
            return

        self.frame += 1
        self.game_timer += dt

        # 冷却倒计时
        for pt in self.card_cooldowns:
            if self.card_cooldowns[pt] > 0:
                self.card_cooldowns[pt] = max(0.0,
                                              self.card_cooldowns[pt] - dt)

        # 天空阳光
        self.sky_sun_timer -= dt
        if self.sky_sun_timer <= 0:
            self.sky_sun_timer = random.uniform(7.0, 12.0)
            sx = random.randint(GRID_X + 30, GRID_X + GRID_W - 30)
            ty = random.randint(GRID_Y + 40, GRID_Y + GRID_H - 40)
            self.suns.append(Sun(sx, GRID_Y - 20, target_y=ty))

        # 波次触发
        if self.wave_index < len(WAVE_DATA):
            wt, ztype, count, is_flag = WAVE_DATA[self.wave_index]
            if self.game_timer >= wt:
                self.wave_index += 1
                if is_flag:
                    msg = ("最终大波僵尸来袭！"
                           if self.wave_index == len(WAVE_DATA)
                           else "旗帜波！僵尸来了！")
                    self.message = msg
                    self.message_timer = 3.0
                for i in range(count):
                    row = random.randint(0, GRID_ROWS - 1)
                    z = Zombie(ztype, row)
                    z.x = float(SCREEN_W + 50 + i * 90)
                    self.zombies.append(z)

        if self.wave_index >= len(WAVE_DATA):
            self.all_waves_done = True

        # 更新实体
        for p in self.plants:
            p.update(dt, self)
        self.plants = [p for p in self.plants if not p.dead]

        for z in self.zombies:
            z.update(dt, self)

        for pr in self.projectiles:
            pr.update(dt, self)
        self.projectiles = [pr for pr in self.projectiles if not pr.dead]

        for s in self.suns:
            s.update(dt)
        self.suns = [s for s in self.suns if not s.dead]

        for m in self.mowers:
            m.update(dt, self)
        self.mowers = [m for m in self.mowers if not m.dead]

        self.zombies = [z for z in self.zombies if not z.dead]

        # 失败条件
        for z in self.zombies:
            if z.x < 15:
                self.result = "lose"
                return

        # 胜利条件
        if self.all_waves_done and len(self.zombies) == 0:
            self.result = "win"
            return

        # 消息倒计时
        if self.message_timer > 0:
            self.message_timer -= dt

        # 悬停格子
        mx, my = pygame.mouse.get_pos()
        col = (mx - GRID_X) // CELL_W
        row = (my - GRID_Y) // CELL_H
        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            self.hover_cell = (col, row)
        else:
            self.hover_cell = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # 收集阳光
            for s in self.suns[:]:
                if s.check_click(mx, my):
                    self.sun += s.collect()
                    return

            # 植物卡片
            for pt, rt in zip(self.CARD_PLANTS, self.CARD_RECTS):
                if pygame.Rect(*rt).collidepoint(mx, my):
                    data = PLANT_DATA[pt]
                    if (self.sun >= data["cost"]
                            and self.card_cooldowns[pt] <= 0):
                        self.selected_plant = (None
                                               if self.selected_plant == pt
                                               else pt)
                        self.shovel_active = False
                    return

            # 铲子
            if self.SHOVEL_RECT.collidepoint(mx, my):
                self.shovel_active = not self.shovel_active
                self.selected_plant = None
                return

            # 格子点击
            if (GRID_X <= mx < GRID_X + GRID_W
                    and GRID_Y <= my < GRID_Y + GRID_H):
                col = (mx - GRID_X) // CELL_W
                row = (my - GRID_Y) // CELL_H

                if self.shovel_active:
                    for p in self.plants:
                        if p.col == col and p.row == row:
                            self.plants.remove(p)
                            self.shovel_active = False
                            refund = PLANT_DATA[p.plant_type]["cost"] // 2
                            self.sun += refund
                            self.message = f"铲除植物，返还{refund}阳光"
                            self.message_timer = 2.0
                            return

                elif self.selected_plant is not None:
                    occupied = any(p.col == col and p.row == row
                                   for p in self.plants)
                    if not occupied:
                        pt = self.selected_plant
                        cost = PLANT_DATA[pt]["cost"]
                        if self.sun >= cost:
                            self.sun -= cost
                            self.plants.append(Plant(pt, col, row))
                            self.card_cooldowns[pt] = (
                                PLANT_DATA[pt]["card_cooldown"])
                            self.selected_plant = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.selected_plant = None
                self.shovel_active = False

    def draw(self, surface: pygame.Surface) -> None:
        draw_lawn_background(surface)
        draw_house(surface)

        # 悬停高亮
        if self.hover_cell and self.selected_plant is not None:
            col, row = self.hover_cell
            hx = GRID_X + col * CELL_W
            hy = GRID_Y + row * CELL_H
            occ = any(p.col == col and p.row == row for p in self.plants)
            hl = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
            hl.fill((255, 255, 0, 80) if not occ else (255, 0, 0, 80))
            surface.blit(hl, (hx, hy))

        for m in self.mowers:
            m.draw(surface)
        for p in self.plants:
            p.draw(surface)
        for pr in self.projectiles:
            pr.draw(surface)
        for z in self.zombies:
            z.draw(surface)
        for s in self.suns:
            s.draw(surface)

        # HUD
        draw_hud_background(surface)
        draw_sun_counter(surface, 8, 11, self.sun)

        for pt, rt in zip(self.CARD_PLANTS, self.CARD_RECTS):
            data = PLANT_DATA[pt]
            cd = self.card_cooldowns[pt]
            cdr = (cd / data["card_cooldown"]) if cd > 0 else 0.0
            draw_plant_card(surface, rt, pt, cdr,
                            self.selected_plant == pt,
                            self.sun >= data["cost"] and cd <= 0)

        # 植物名称提示
        mx, my = pygame.mouse.get_pos()
        for pt, rt in zip(self.CARD_PLANTS, self.CARD_RECTS):
            if pygame.Rect(*rt).collidepoint(mx, my):
                name = PLANT_DATA[pt]["name"]
                draw_text(surface, name, 18, WHITE,
                          pygame.Rect(*rt).centerx, 76)

        # 铲子
        sr = self.SHOVEL_RECT
        sb = (200, 150, 50) if self.shovel_active else (150, 120, 60)
        sbd = (255, 200, 0) if self.shovel_active else (100, 80, 40)
        draw_rounded_rect(surface, sb, sr, radius=6, border=2,
                          border_color=sbd)
        scx, scy = sr.centerx, sr.centery
        pygame.draw.line(surface, (180, 120, 50),
                         (scx, scy - 18), (scx, scy + 14), 4)
        pygame.draw.ellipse(surface, (160, 160, 170),
                            (scx - 8, scy - 22, 16, 14))

        # 进度条
        progress = self.wave_index / len(WAVE_DATA)
        bx, by = SCREEN_W - 200, 14
        bw, bh = 185, 16
        pygame.draw.rect(surface, (60, 40, 10), (bx, by, bw, bh),
                         border_radius=8)
        if progress > 0:
            pygame.draw.rect(surface, (220, 80, 30),
                             (bx, by, int(bw * progress), bh),
                             border_radius=8)
        draw_text(surface, "进度", 14, WHITE, bx - 22, by + 8)
        draw_text(surface,
                  f"第{self.wave_index}/{len(WAVE_DATA)}波",
                  14, (255, 220, 100), bx + bw // 2, by + 8)

        # 计时
        ts = int(self.game_timer)
        t_surf = render_text(f"{ts // 60:02d}:{ts % 60:02d}", 16,
                             (200, 220, 200))
        surface.blit(t_surf, (SCREEN_W - 52, 50))

        # 提示消息
        if self.message_timer > 0 and self.message:
            alpha = min(255, int(self.message_timer * 140))
            ms = render_text(self.message, 38, (255, 80, 80))
            ms.set_alpha(alpha)
            surface.blit(ms, ms.get_rect(
                center=(SCREEN_W // 2, SCREEN_H // 2 - 100)))

        # 鼠标跟随植物幽灵
        if self.selected_plant is not None:
            ghost = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
            ghost.set_alpha(180)
            if self.selected_plant == PT_SUNFLOWER:
                draw_sunflower(ghost, 0, 0, self.frame)
            else:
                draw_peashooter(ghost, 0, 0, self.frame)
            surface.blit(ghost, (mx - CELL_W // 2, my - CELL_H // 2))


class WinScreen:
    """胜利画面"""

    def __init__(self) -> None:
        self.frame = 0
        self.result = None
        self.btn = pygame.Rect(SCREEN_W // 2 - 110, 430, 220, 55)

    def update(self, dt: float) -> None:
        self.frame += 1

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn.collidepoint(event.pos):
                self.result = "menu"
        if event.type == pygame.KEYDOWN:
            self.result = "menu"

    def draw(self, surface: pygame.Surface) -> None:
        f = self.frame
        for i in range(SCREEN_H):
            r = i / SCREEN_H
            pygame.draw.line(surface,
                             (int(20 + r * 40),
                              int(80 + r * 80),
                              int(20 + r * 30)),
                             (0, i), (SCREEN_W, i))

        # 旋转太阳
        for i in range(6):
            ang = math.radians(f * 2 + i * 60)
            draw_sun(surface,
                     SCREEN_W // 2 + int(math.cos(ang) * 200),
                     SCREEN_H // 2 + int(math.sin(ang) * 80),
                     30, f + i * 20)

        # 奖杯
        cx, cy = SCREEN_W // 2, SCREEN_H // 2 - 60
        pygame.draw.polygon(surface, YELLOW, [
            (cx - 40, cy - 80), (cx + 40, cy - 80),
            (cx + 50, cy - 30), (cx,      cy + 10),
            (cx - 50, cy - 30),
        ])
        pygame.draw.rect(surface, (200, 160, 0), (cx - 20, cy + 10, 40, 20))
        pygame.draw.rect(surface, (180, 140, 0), (cx - 35, cy + 30, 70, 12))

        draw_text_shadow(surface, "你赢了！", 80, (255, 230, 50),
                         SCREEN_W // 2, 155, (0, 100, 0))
        draw_text(surface, "成功守护了你的家园！", 36, (200, 255, 200),
                  SCREEN_W // 2, 240)
        draw_text(surface, "第1-1关  完成！", 28, (255, 220, 100),
                  SCREEN_W // 2, 290)

        hov = self.btn.collidepoint(pygame.mouse.get_pos())
        draw_rounded_rect(surface,
                          (255, 180, 0) if hov else (200, 140, 0),
                          self.btn, radius=10,
                          border=3, border_color=(255, 230, 100))
        draw_text(surface, "返回主菜单", 28, (80, 30, 0),
                  self.btn.centerx, self.btn.centery)


class LoseScreen:
    """失败画面"""

    def __init__(self) -> None:
        self.frame = 0
        self.result = None
        self.retry_btn = pygame.Rect(SCREEN_W // 2 - 150, 410, 190, 55)
        self.menu_btn  = pygame.Rect(SCREEN_W // 2 +  30, 410, 190, 55)

    def update(self, dt: float) -> None:
        self.frame += 1

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.retry_btn.collidepoint(event.pos):
                self.result = "retry"
            elif self.menu_btn.collidepoint(event.pos):
                self.result = "menu"
        if event.type == pygame.KEYDOWN:
            self.result = "retry"

    def draw(self, surface: pygame.Surface) -> None:
        f = self.frame
        for i in range(SCREEN_H):
            r = i / SCREEN_H
            pygame.draw.line(surface,
                             (int(40 + r * 20),
                              int(10 + r * 5),
                              int(10 + r * 5)),
                             (0, i), (SCREEN_W, i))

        for i in range(5):
            zx = 90 + i * 160 + int(math.sin(f * 0.04 + i) * 15)
            draw_zombie(surface, zx, 395, f + i * 20)

        draw_text_shadow(surface, "僵尸吃掉了你的脑！", 52,
                         (255, 80, 80), SCREEN_W // 2, 145, (100, 0, 0))
        draw_text(surface, "你输了", 80, (220, 50, 50),
                  SCREEN_W // 2, 240)
        draw_text(surface, "第1-1关  失败", 28, (255, 180, 180),
                  SCREEN_W // 2, 315)

        for btn, txt in ((self.retry_btn, "重新开始"),
                         (self.menu_btn,  "返回主菜单")):
            hov = btn.collidepoint(pygame.mouse.get_pos())
            bg = (255, 120, 50) if hov else (200, 80, 30)
            draw_rounded_rect(surface, bg, btn, radius=10,
                              border=3, border_color=(255, 150, 100))
            draw_text(surface, txt, 26, WHITE, btn.centerx, btn.centery)


# ============================================================
# 主游戏类
# ============================================================

class PvZGame:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.state = ST_INTRO

        self.intro = IntroScreen()
        self.menu  = MenuScreen()
        self.game  = GameScreen()
        self.win   = WinScreen()
        self.lose  = LoseScreen()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if self.state == ST_INTRO:
                    self.intro.handle_event(event)
                elif self.state == ST_MENU:
                    self.menu.handle_event(event)
                elif self.state == ST_PLAYING:
                    self.game.handle_event(event)
                elif self.state == ST_WIN:
                    self.win.handle_event(event)
                elif self.state == ST_LOSE:
                    self.lose.handle_event(event)

            # 更新 + 绘制 + 状态切换
            if self.state == ST_INTRO:
                self.intro.update(dt)
                self.intro.draw(self.screen)
                if self.intro.done:
                    self.state = ST_MENU

            elif self.state == ST_MENU:
                self.menu.update(dt)
                self.menu.draw(self.screen)
                if self.menu.result == "start":
                    self.game.reset()
                    self.state = ST_PLAYING
                    self.menu.result = None
                elif self.menu.result == "quit":
                    running = False

            elif self.state == ST_PLAYING:
                self.game.update(dt)
                self.game.draw(self.screen)
                if self.game.result == "win":
                    self.win = WinScreen()
                    self.state = ST_WIN
                elif self.game.result == "lose":
                    self.lose = LoseScreen()
                    self.state = ST_LOSE

            elif self.state == ST_WIN:
                self.win.update(dt)
                self.win.draw(self.screen)
                if self.win.result == "menu":
                    self.menu = MenuScreen()
                    self.state = ST_MENU

            elif self.state == ST_LOSE:
                self.lose.update(dt)
                self.lose.draw(self.screen)
                if self.lose.result == "retry":
                    self.game.reset()
                    self.state = ST_PLAYING
                elif self.lose.result == "menu":
                    self.menu = MenuScreen()
                    self.state = ST_MENU

            pygame.display.flip()

        pygame.quit()
        sys.exit()


def main() -> None:
    game = PvZGame()
    game.run()


if __name__ == "__main__":
    main()
