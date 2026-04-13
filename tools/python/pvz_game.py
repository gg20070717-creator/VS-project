#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物大战僵尸 1-1 小游戏
Plants vs. Zombies Level 1-1 Mini Game
完全还原原版 PvZ 1-1 内容，采用中文界面
"""

import pygame
import math
import random
import sys
import os

# ======================================================
#  初始化
# ======================================================
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=256)

# ======================================================
#  常量
# ======================================================
SCREEN_W, SCREEN_H = 800, 600
FPS = 60
TITLE = "植物大战僵尸"

# 游戏网格
GRID_COLS = 9
GRID_ROWS = 5
CELL_W = 75
CELL_H = 90
GRID_X = 90     # 网格左边X
GRID_Y = 90     # 网格上边Y

# 颜色
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
SKY         = (110, 200, 250)
GRASS1      = (100, 180, 60)
GRASS2      = (85,  160, 50)
SOIL        = (150, 110, 60)
YELLOW      = (255, 230, 0)
SUN_COL     = (255, 210, 0)
ORANGE      = (255, 140, 0)
RED         = (210, 50,  50)
DARK_RED    = (160, 20,  20)
GREEN       = (60,  200, 60)
DARK_GREEN  = (20,  140, 20)
LEAF_GREEN  = (50,  190, 80)
BROWN       = (160, 100, 40)
DARK_BROWN  = (110, 70,  20)
GRAY        = (140, 140, 140)
DARK_GRAY   = (80,  80,  80)
LIGHT_GRAY  = (220, 220, 220)
ZOMBIE_SKIN = (155, 195, 130)
ZOMBIE_DARK = (120, 165, 100)
BLUE_GRAY   = (100, 120, 160)
PURPLE      = (140, 50,  170)
PINK        = (255, 160, 180)
CREAM       = (255, 248, 220)
TRANSLUCENT_BLACK = (0, 0, 0, 160)

# 游戏状态
STATE_INTRO   = 0
STATE_MENU    = 1
STATE_PLAYING = 2
STATE_WIN     = 3
STATE_LOSE    = 4
STATE_PAUSE   = 5

# 植物类型
PLANT_SUNFLOWER  = 'sunflower'
PLANT_PEASHOOTER = 'peashooter'
PLANT_WALLNUT    = 'wallnut'

# 僵尸类型
ZOMBIE_NORMAL = 'normal'
ZOMBIE_CONE   = 'cone'
ZOMBIE_FLAG   = 'flag'

# 植物配置
PLANTS_CFG = {
    PLANT_SUNFLOWER: {
        'name': '向日葵',
        'cost': 50,
        'hp': 300,
        'sun_timer': 1440,   # ~24秒出一个阳光 (帧数)
        'sun_amount': 25,
        'cooldown': 420,     # 7秒再种间隔
    },
    PLANT_PEASHOOTER: {
        'name': '豌豆射手',
        'cost': 100,
        'hp': 300,
        'shoot_cd': 90,      # 1.5秒射一颗豌豆
        'cooldown': 420,
    },
    PLANT_WALLNUT: {
        'name': '坚果墙',
        'cost': 50,
        'hp': 4000,
        'cooldown': 1800,    # 30秒再种
    },
}

# 僵尸配置
ZOMBIES_CFG = {
    ZOMBIE_NORMAL: {'name': '普通僵尸', 'hp': 270,  'speed': 28, 'damage': 100, 'atk_cd': 60},
    ZOMBIE_CONE:   {'name': '路障僵尸', 'hp': 560,  'speed': 25, 'damage': 100, 'atk_cd': 60},
    ZOMBIE_FLAG:   {'name': '旗帜僵尸', 'hp': 270,  'speed': 32, 'damage': 100, 'atk_cd': 60},
}

# 1-1 关卡波次  [(zombie_type, row), ...]
LEVEL_WAVES = [
    [('normal', 2)],
    [('normal', 1), ('normal', 3)],
    [('flag', 0), ('normal', 2), ('normal', 4)],
    [('normal', 0), ('normal', 1), ('normal', 3), ('normal', 4)],
    [('flag', 0), ('normal', 1), ('cone', 2), ('normal', 3), ('flag', 4), ('cone', 2)],
]
# 波次触发时间 (秒)
WAVE_TRIGGER = [12, 38, 68, 105, 148]

# 僵尸死亡动画持续帧数
ZOMBIE_DEATH_ANIMATION_FRAMES = 30

# ======================================================
#  字体加载
# ======================================================
# 候选字体路径 (跨平台: Linux → macOS → Windows)
_CJK_FONT_CANDIDATES = [
    # Linux (NotoSansCJK)
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
    # macOS
    '/System/Library/Fonts/PingFang.ttc',
    '/Library/Fonts/Arial Unicode MS.ttf',
    # Windows
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simhei.ttf',
]
_CJK_BOLD_CANDIDATES = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc',
    '/System/Library/Fonts/PingFang.ttc',
    'C:/Windows/Fonts/msyhbd.ttc',
    'C:/Windows/Fonts/simhei.ttf',
]


def _find_font(candidates: list[str]) -> str | None:
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


_font_cache: dict = {}

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        candidates = _CJK_BOLD_CANDIDATES if bold else _CJK_FONT_CANDIDATES
        path = _find_font(candidates)
        if path:
            _font_cache[key] = pygame.font.Font(path, size)
        else:
            # 最终回退: 系统字体
            _font_cache[key] = pygame.font.SysFont(
                'microsoftyahei,pingfang sc,noto sans cjk sc,arial', size, bold=bold)
    return _font_cache[key]


def draw_text(surf: pygame.Surface, text: str, x: int, y: int,
              size: int = 20, color=WHITE, bold: bool = False,
              center: bool = False, shadow: bool = False):
    font = get_font(size, bold)
    if shadow:
        s = font.render(text, True, BLACK)
        if center:
            sr = s.get_rect(center=(x + 2, y + 2))
        else:
            sr = s.get_rect(topleft=(x + 2, y + 2))
        surf.blit(s, sr)
    img = font.render(text, True, color)
    if center:
        r = img.get_rect(center=(x, y))
    else:
        r = img.get_rect(topleft=(x, y))
    surf.blit(img, r)
    return r


# ======================================================
#  绘制工具 - 所有精灵的绘制函数
# ======================================================

def draw_sunflower(surf: pygame.Surface, x: int, y: int,
                   scale: float = 1.0, hp_ratio: float = 1.0, blink: bool = False):
    """绘制向日葵"""
    if blink:
        return
    cx = x + int(37 * scale)
    cy = y + int(45 * scale)
    stem_w = max(2, int(8 * scale))
    # 茎
    pygame.draw.line(surf, DARK_GREEN,
                     (cx, cy + int(15 * scale)),
                     (cx, y + int(85 * scale)), stem_w)
    # 叶片
    leaf_col = LEAF_GREEN if hp_ratio > 0.5 else (100, 160, 60)
    leaf_pts = [
        (cx, cy + int(25 * scale)),
        (cx - int(22 * scale), cy + int(40 * scale)),
        (cx - int(5 * scale), cy + int(30 * scale)),
    ]
    pygame.draw.polygon(surf, leaf_col, leaf_pts)
    # 花瓣 (12片)
    petal_col = (255, 220, 0) if hp_ratio > 0.5 else (200, 170, 30)
    r_petal = int(10 * scale)
    r_head  = int(16 * scale)
    for i in range(12):
        angle = math.radians(i * 30)
        px = cx + int(math.cos(angle) * (r_head + r_petal - 2) * scale)
        py = cy + int(math.sin(angle) * (r_head + r_petal - 2) * scale)
        pygame.draw.circle(surf, petal_col, (px, py), r_petal)
    # 花心
    pygame.draw.circle(surf, BROWN, (cx, cy), r_head)
    pygame.draw.circle(surf, DARK_BROWN, (cx, cy), r_head, 2)
    # 眼睛和嘴巴 (可爱的脸)
    eye_r = max(1, int(3 * scale))
    ex_off = int(5 * scale)
    ey_off = int(4 * scale)
    pygame.draw.circle(surf, BLACK, (cx - ex_off, cy - ey_off), eye_r)
    pygame.draw.circle(surf, BLACK, (cx + ex_off, cy - ey_off), eye_r)
    # 微笑
    smile_rect = pygame.Rect(cx - int(7 * scale), cy + int(2 * scale),
                              int(14 * scale), int(7 * scale))
    pygame.draw.arc(surf, BLACK, smile_rect, math.pi, 2 * math.pi, max(1, int(2 * scale)))


def draw_peashooter(surf: pygame.Surface, x: int, y: int,
                    scale: float = 1.0, hp_ratio: float = 1.0, blink: bool = False):
    """绘制豌豆射手"""
    if blink:
        return
    cx = x + int(30 * scale)
    cy = y + int(50 * scale)
    body_col = GREEN if hp_ratio > 0.5 else (60, 140, 60)
    dark_col = DARK_GREEN
    # 茎/身体
    body_rect = pygame.Rect(cx - int(14 * scale), cy - int(15 * scale),
                             int(28 * scale), int(50 * scale))
    pygame.draw.rect(surf, body_col, body_rect, border_radius=int(8 * scale))
    pygame.draw.rect(surf, dark_col, body_rect, 2, border_radius=int(8 * scale))
    # 炮管 (向右伸出)
    barrel_w = int(30 * scale)
    barrel_h = int(10 * scale)
    barrel_rect = pygame.Rect(cx, cy - barrel_h // 2, barrel_w, barrel_h)
    pygame.draw.rect(surf, (40, 160, 40), barrel_rect, border_radius=int(4 * scale))
    pygame.draw.rect(surf, dark_col, barrel_rect, 2, border_radius=int(4 * scale))
    # 头部
    head_r = int(18 * scale)
    pygame.draw.circle(surf, body_col, (cx, cy - int(10 * scale)), head_r)
    pygame.draw.circle(surf, dark_col, (cx, cy - int(10 * scale)), head_r, 2)
    # 眼睛
    eye_r = max(1, int(3 * scale))
    pygame.draw.circle(surf, BLACK, (cx - int(5 * scale), cy - int(14 * scale)), eye_r)
    pygame.draw.circle(surf, BLACK, (cx + int(5 * scale), cy - int(14 * scale)), eye_r)
    # 叶片
    leaf_pts = [
        (cx - int(10 * scale), cy + int(5 * scale)),
        (cx - int(28 * scale), cy - int(10 * scale)),
        (cx - int(15 * scale), cy + int(20 * scale)),
    ]
    pygame.draw.polygon(surf, LEAF_GREEN, leaf_pts)


def draw_wallnut(surf: pygame.Surface, x: int, y: int,
                 scale: float = 1.0, hp_ratio: float = 1.0, blink: bool = False):
    """绘制坚果墙"""
    if blink:
        return
    cx = x + int(37 * scale)
    cy = y + int(50 * scale)
    # 颜色随HP变化
    if hp_ratio > 0.6:
        col = (190, 130, 60)
        face = 'happy'
    elif hp_ratio > 0.3:
        col = (180, 110, 40)
        face = 'worried'
    else:
        col = (160, 80, 30)
        face = 'scared'
    # 主体椭圆
    body_rect = pygame.Rect(cx - int(28 * scale), cy - int(32 * scale),
                             int(56 * scale), int(64 * scale))
    pygame.draw.ellipse(surf, col, body_rect)
    pygame.draw.ellipse(surf, DARK_BROWN, body_rect, 2)
    # 纹路
    for i in range(-1, 2):
        lx = cx + i * int(10 * scale)
        pygame.draw.line(surf, DARK_BROWN,
                         (lx, cy - int(25 * scale)),
                         (lx, cy + int(25 * scale)), 1)
    # 眼睛
    eye_r = max(1, int(4 * scale))
    ex = int(9 * scale)
    ey = int(8 * scale)
    if face == 'happy':
        pygame.draw.circle(surf, BLACK, (cx - ex, cy - ey), eye_r)
        pygame.draw.circle(surf, BLACK, (cx + ex, cy - ey), eye_r)
        sm = pygame.Rect(cx - int(9*scale), cy+int(2*scale), int(18*scale), int(8*scale))
        pygame.draw.arc(surf, BLACK, sm, math.pi, 2*math.pi, 2)
    elif face == 'worried':
        pygame.draw.circle(surf, BLACK, (cx - ex, cy - ey), eye_r)
        pygame.draw.circle(surf, BLACK, (cx + ex, cy - ey), eye_r)
        # 倒扣嘴巴
        sm = pygame.Rect(cx - int(9*scale), cy+int(4*scale), int(18*scale), int(8*scale))
        pygame.draw.arc(surf, BLACK, sm, 0, math.pi, 2)
    else:  # scared
        # 惊吓的眼睛
        pygame.draw.circle(surf, BLACK, (cx - ex, cy - ey), eye_r + 1)
        pygame.draw.circle(surf, BLACK, (cx + ex, cy - ey), eye_r + 1)
        pygame.draw.circle(surf, WHITE, (cx - ex + 1, cy - ey - 1), max(1, eye_r - 1))
        pygame.draw.circle(surf, WHITE, (cx + ex + 1, cy - ey - 1), max(1, eye_r - 1))
        # 嘴巴大开
        pygame.draw.ellipse(surf, BLACK,
                             pygame.Rect(cx - int(7*scale), cy+int(3*scale),
                                         int(14*scale), int(10*scale)))


def draw_zombie(surf: pygame.Surface, x: int, y: int,
                ztype: str = ZOMBIE_NORMAL, scale: float = 1.0,
                hp_ratio: float = 1.0, anim_frame: int = 0):
    """绘制僵尸"""
    skin = ZOMBIE_SKIN if hp_ratio > 0.4 else (130, 165, 100)
    suit = BLUE_GRAY if hp_ratio > 0.4 else (80, 100, 130)
    cx   = x + int(30 * scale)
    # 腿部动画
    leg_swing = math.sin(anim_frame * 0.2) * int(8 * scale)
    # 左腿
    pygame.draw.line(surf, suit,
                     (cx - int(8*scale), y + int(62*scale)),
                     (cx - int(8*scale) + int(leg_swing), y + int(85*scale)),
                     max(2, int(7*scale)))
    # 右腿
    pygame.draw.line(surf, suit,
                     (cx + int(8*scale), y + int(62*scale)),
                     (cx + int(8*scale) - int(leg_swing), y + int(85*scale)),
                     max(2, int(7*scale)))
    # 身体
    body_rect = pygame.Rect(cx - int(16*scale), y + int(30*scale),
                             int(32*scale), int(35*scale))
    pygame.draw.rect(surf, suit, body_rect, border_radius=4)
    pygame.draw.rect(surf, DARK_GRAY, body_rect, 1, border_radius=4)
    # 伸出的手臂 (向左伸)
    arm_y = y + int(42*scale)
    arm_swing = math.sin(anim_frame * 0.2 + 1) * int(4 * scale)
    pygame.draw.line(surf, skin,
                     (cx - int(16*scale), arm_y),
                     (cx - int(40*scale), arm_y + int(arm_swing)),
                     max(2, int(6*scale)))
    pygame.draw.line(surf, skin,
                     (cx + int(16*scale), arm_y + int(5*scale)),
                     (cx + int(12*scale), arm_y + int(20*scale)),
                     max(2, int(6*scale)))
    # 头部
    head_r = int(15*scale)
    pygame.draw.circle(surf, skin,
                        (cx, y + int(18*scale)), head_r)
    pygame.draw.circle(surf, DARK_GRAY,
                        (cx, y + int(18*scale)), head_r, 1)
    # 头发 (稀疏)
    hair_col = (50, 40, 30)
    for i in range(3):
        hx = cx - int(8*scale) + i * int(8*scale)
        pygame.draw.line(surf, hair_col,
                         (hx, y + int(4*scale)),
                         (hx, y + int(10*scale)), max(1, int(2*scale)))
    # 眼睛
    pygame.draw.circle(surf, RED, (cx - int(5*scale), y + int(15*scale)), max(1, int(3*scale)))
    pygame.draw.circle(surf, RED, (cx + int(5*scale), y + int(15*scale)), max(1, int(3*scale)))
    pygame.draw.circle(surf, BLACK, (cx - int(5*scale), y + int(15*scale)), max(1, int(2*scale)))
    pygame.draw.circle(surf, BLACK, (cx + int(5*scale), y + int(15*scale)), max(1, int(2*scale)))
    # 嘴巴
    pygame.draw.arc(surf, (180, 40, 40),
                    pygame.Rect(cx - int(7*scale), y + int(20*scale),
                                int(14*scale), int(6*scale)),
                    0, math.pi, max(1, int(2*scale)))
    # 路障 (锥形僵尸)
    if ztype == ZOMBIE_CONE:
        cone_pts = [
            (cx - int(12*scale), y + int(5*scale)),
            (cx + int(12*scale), y + int(5*scale)),
            (cx, y - int(16*scale)),
        ]
        pygame.draw.polygon(surf, ORANGE, cone_pts)
        pygame.draw.polygon(surf, (200, 100, 0), cone_pts, 2)
        # 条纹
        for i in range(2):
            stripe_y = y + int((3 - i * 6) * scale)
            pygame.draw.line(surf, WHITE,
                             (cx - int((6+i*3)*scale), stripe_y),
                             (cx + int((6+i*3)*scale), stripe_y), 1)
    # 旗帜
    if ztype == ZOMBIE_FLAG:
        pole_x = cx + int(16*scale)
        pygame.draw.line(surf, DARK_BROWN,
                         (pole_x, y + int(5*scale)),
                         (pole_x, y + int(50*scale)), max(1, int(2*scale)))
        flag_pts = [
            (pole_x, y + int(5*scale)),
            (pole_x + int(20*scale), y + int(13*scale)),
            (pole_x, y + int(22*scale)),
        ]
        pygame.draw.polygon(surf, RED, flag_pts)


def draw_pea(surf: pygame.Surface, x: int, y: int, scale: float = 1.0):
    """绘制豌豆"""
    r = max(3, int(7 * scale))
    pygame.draw.circle(surf, GREEN, (x, y), r)
    pygame.draw.circle(surf, DARK_GREEN, (x, y), r, 1)
    pygame.draw.circle(surf, (150, 255, 150), (x - r//3, y - r//3), max(1, r//3))


def draw_sun(surf: pygame.Surface, x: int, y: int, r: int = 20, alpha: float = 1.0):
    """绘制阳光"""
    # 光晕
    glow_r = int(r * 1.5)
    glow_surf = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
    glow_col = (255, 230, 0, int(80 * alpha))
    pygame.draw.circle(glow_surf, glow_col, (glow_r, glow_r), glow_r)
    surf.blit(glow_surf, (x - glow_r, y - glow_r))
    # 光线
    ray_col = (255, 200, 0)
    for i in range(8):
        angle = math.radians(i * 45)
        x1 = x + int(math.cos(angle) * r)
        y1 = y + int(math.sin(angle) * r)
        x2 = x + int(math.cos(angle) * (r + 6))
        y2 = y + int(math.sin(angle) * (r + 6))
        pygame.draw.line(surf, ray_col, (x1, y1), (x2, y2), 2)
    # 主体
    pygame.draw.circle(surf, SUN_COL, (x, y), r)
    pygame.draw.circle(surf, (255, 240, 50), (x - r//4, y - r//4), r//2)
    pygame.draw.circle(surf, ORANGE, (x, y), r, 2)
    # 脸
    pygame.draw.circle(surf, BLACK, (x - 5, y - 4), 2)
    pygame.draw.circle(surf, BLACK, (x + 5, y - 4), 2)
    sm = pygame.Rect(x - 6, y + 3, 12, 6)
    pygame.draw.arc(surf, BLACK, sm, math.pi, 2*math.pi, 2)


def draw_lawnmower(surf: pygame.Surface, x: int, y: int, moving: bool = False):
    """绘制割草机"""
    # 机身
    body = pygame.Rect(x, y - 15, 40, 20)
    pygame.draw.rect(surf, RED, body, border_radius=4)
    pygame.draw.rect(surf, DARK_RED, body, 2, border_radius=4)
    # 把手
    pygame.draw.line(surf, DARK_GRAY, (x + 35, y - 15), (x + 45, y - 28), 3)
    # 轮子
    wheel_col = DARK_GRAY if not moving else (60, 60, 60)
    pygame.draw.circle(surf, wheel_col, (x + 8, y + 5), 8)
    pygame.draw.circle(surf, wheel_col, (x + 30, y + 5), 8)
    pygame.draw.circle(surf, GRAY, (x + 8, y + 5), 5)
    pygame.draw.circle(surf, GRAY, (x + 30, y + 5), 5)
    # 刀片 (旋转动画)
    pygame.draw.line(surf, LIGHT_GRAY, (x + 8, y - 5), (x + 32, y - 5), 3)


def draw_seed_packet(surf: pygame.Surface, x: int, y: int,
                     ptype: str, cost: int, selected: bool = False,
                     cd_ratio: float = 0.0, can_afford: bool = True):
    """绘制种子包"""
    w, h = 55, 70
    # 背景
    if selected:
        bg_col = (220, 200, 100)
        border_col = (255, 220, 50)
    elif not can_afford:
        bg_col = (80, 80, 80)
        border_col = (120, 120, 120)
    else:
        bg_col = (60, 100, 60)
        border_col = (100, 160, 100)

    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surf, bg_col, rect, border_radius=6)
    pygame.draw.rect(surf, border_col, rect, 2, border_radius=6)

    # 植物图标 (小版)
    icon_surf = pygame.Surface((w - 8, 36), pygame.SRCALPHA)
    icon_surf.fill((0, 0, 0, 0))
    if ptype == PLANT_SUNFLOWER:
        draw_sunflower(icon_surf, -4, -5, scale=0.5)
    elif ptype == PLANT_PEASHOOTER:
        draw_peashooter(icon_surf, -4, -5, scale=0.5)
    elif ptype == PLANT_WALLNUT:
        draw_wallnut(icon_surf, -4, -5, scale=0.5)
    surf.blit(icon_surf, (x + 4, y + 2))

    # 名字
    draw_text(surf, PLANTS_CFG[ptype]['name'], x + w//2, y + 42,
              size=11, color=WHITE, center=True)
    # 费用
    draw_text(surf, str(cost), x + w//2, y + 55,
              size=13, color=SUN_COL, bold=True, center=True)

    # 冷却遮罩
    if cd_ratio > 0:
        mask = pygame.Surface((w, int(h * cd_ratio)), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 160))
        surf.blit(mask, (x, y))


def draw_background(surf: pygame.Surface):
    """绘制游戏背景 (天空 + 草坪)"""
    # 天空
    sky_rect = pygame.Rect(0, 0, SCREEN_W, GRID_Y)
    pygame.draw.rect(surf, SKY, sky_rect)
    # 背景树/装饰 (简化)
    for i, bx in enumerate([10, 100, 680, 770]):
        tree_h = 60 + (i % 2) * 15
        # 树干
        pygame.draw.rect(surf, DARK_BROWN, (bx + 8, GRID_Y - tree_h + 20, 10, tree_h - 20))
        # 树冠
        pygame.draw.circle(surf, DARK_GREEN, (bx + 13, GRID_Y - tree_h + 20), 22)
        pygame.draw.circle(surf, GREEN, (bx + 13, GRID_Y - tree_h + 18), 18)

    # 草坪条纹
    for r in range(GRID_ROWS):
        ry = GRID_Y + r * CELL_H
        col = GRASS1 if r % 2 == 0 else GRASS2
        row_rect = pygame.Rect(0, ry, SCREEN_W, CELL_H)
        pygame.draw.rect(surf, col, row_rect)

    # 网格线 (淡)
    grid_line_col = (0, 80, 0)
    for c in range(GRID_COLS + 1):
        px = GRID_X + c * CELL_W
        pygame.draw.line(surf, grid_line_col,
                         (px, GRID_Y), (px, GRID_Y + GRID_ROWS * CELL_H), 1)
    for r in range(GRID_ROWS + 1):
        py = GRID_Y + r * CELL_H
        pygame.draw.line(surf, grid_line_col,
                         (GRID_X, py), (GRID_X + GRID_COLS * CELL_W, py), 1)

    # 底栏
    bar_rect = pygame.Rect(0, GRID_Y + GRID_ROWS * CELL_H, SCREEN_W, SCREEN_H - GRID_Y - GRID_ROWS * CELL_H)
    pygame.draw.rect(surf, (80, 60, 30), bar_rect)


def draw_topbar(surf: pygame.Surface, sun: int,
                seed_packets: list, selected_plant: str | None):
    """绘制顶部工具栏"""
    bar_rect = pygame.Rect(0, 0, SCREEN_W, GRID_Y)
    pygame.draw.rect(surf, (50, 80, 40), bar_rect)
    pygame.draw.line(surf, DARK_BROWN, (0, GRID_Y - 2), (SCREEN_W, GRID_Y - 2), 3)

    # 阳光计数
    sun_bg = pygame.Rect(5, 8, 70, 72)
    pygame.draw.rect(surf, (180, 150, 50), sun_bg, border_radius=8)
    pygame.draw.rect(surf, SUN_COL, sun_bg, 2, border_radius=8)
    draw_sun(surf, 30, 32, r=14)
    draw_text(surf, str(sun), 40, 52, size=18, color=BLACK, bold=True, center=True)

    # 种子包
    for i, sp in enumerate(seed_packets):
        sx = 85 + i * 62
        sy = 8
        selected = selected_plant == sp['type']
        cd_ratio = sp.get('cooldown_left', 0) / PLANTS_CFG[sp['type']]['cooldown']
        can_afford = sun >= PLANTS_CFG[sp['type']]['cost']
        draw_seed_packet(surf, sx, sy, sp['type'],
                         PLANTS_CFG[sp['type']]['cost'],
                         selected=selected,
                         cd_ratio=max(0.0, cd_ratio),
                         can_afford=can_afford)


def draw_progress_bar(surf: pygame.Surface, progress: float,
                      wave: int, total_waves: int, label: str = ""):
    """绘制波次进度条"""
    bar_y = GRID_Y + GRID_ROWS * CELL_H
    bar_h = SCREEN_H - bar_y
    bg_rect = pygame.Rect(0, bar_y, SCREEN_W, bar_h)
    pygame.draw.rect(surf, (80, 60, 30), bg_rect)

    # 进度条
    pbar_rect = pygame.Rect(10, bar_y + 8, SCREEN_W - 20, bar_h - 16)
    pygame.draw.rect(surf, (50, 40, 20), pbar_rect, border_radius=5)
    fill_w = int((SCREEN_W - 22) * min(1.0, progress))
    if fill_w > 0:
        fill_rect = pygame.Rect(11, bar_y + 9, fill_w, bar_h - 18)
        pygame.draw.rect(surf, (200, 100, 50), fill_rect, border_radius=4)
    pygame.draw.rect(surf, BROWN, pbar_rect, 2, border_radius=5)

    # 波次标记
    for i in range(total_waves):
        mx = int(10 + (SCREEN_W - 20) * (i / total_waves))
        pygame.draw.line(surf, WHITE, (mx, bar_y + 8), (mx, bar_y + bar_h - 8), 2)

    # 文字
    if label:
        draw_text(surf, label, SCREEN_W // 2, bar_y + bar_h // 2,
                  size=14, color=WHITE, bold=True, center=True, shadow=True)
    else:
        wave_text = f"第 {wave}/{total_waves} 波"
        draw_text(surf, wave_text, SCREEN_W // 2, bar_y + bar_h // 2,
                  size=14, color=WHITE, center=True, shadow=True)


# ======================================================
#  游戏实体类
# ======================================================

class Sun:
    """阳光 - 可点击收集"""
    def __init__(self, x: int, y: int, target_y: int, amount: int = 25,
                 source: str = 'sky'):
        self.x = x
        self.y = y
        self.target_y = target_y
        self.amount = amount
        self.source = source
        self.speed = 60  # pixels/second
        self.radius = 20
        self.collect_timer = 0
        self.collect_max = 600  # 10秒后消失
        self.collected = False
        self.collect_anim = 0  # 收集动画帧数
        self.reached = False
        self.bob_offset = 0.0
        self.bob_timer = 0

    def update(self, dt_sec: float):
        if self.collected:
            self.collect_anim += 1
            return self.collect_anim < 20
        if not self.reached:
            self.y += self.speed * dt_sec
            if self.y >= self.target_y:
                self.y = self.target_y
                self.reached = True
        else:
            self.bob_timer += dt_sec
            self.bob_offset = math.sin(self.bob_timer * 3) * 3
            self.collect_timer += 1
        return self.collect_timer < self.collect_max

    def draw(self, surf: pygame.Surface):
        if self.collected:
            alpha = max(0, 255 - self.collect_anim * 13)
            s = pygame.Surface((50, 50), pygame.SRCALPHA)
            draw_sun(s, 25, 25, r=int(self.radius * (1 + self.collect_anim * 0.05)))
            s.set_alpha(alpha)
            surf.blit(s, (self.x - 25, int(self.y + self.bob_offset) - 25))
        else:
            draw_sun(surf, self.x, int(self.y + self.bob_offset), r=self.radius)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.radius, int(self.y + self.bob_offset) - self.radius,
                           self.radius * 2, self.radius * 2)

    def collect(self):
        self.collected = True


class Projectile:
    """子弹 (豌豆)"""
    def __init__(self, x: int, y: int, speed: int = 350, damage: int = 20):
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.damage = damage
        self.alive = True
        self.radius = 7

    def update(self, dt_sec: float):
        self.x += self.speed * dt_sec

    def draw(self, surf: pygame.Surface):
        draw_pea(surf, int(self.x), int(self.y))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius,
                           self.radius * 2, self.radius * 2)


class Plant:
    """植物基类"""
    def __init__(self, ptype: str, col: int, row: int):
        self.ptype = ptype
        self.col = col
        self.row = row
        cfg = PLANTS_CFG[ptype]
        self.hp = cfg['hp']
        self.max_hp = cfg['hp']
        self.alive = True
        self.x = GRID_X + col * CELL_W
        self.y = GRID_Y + row * CELL_H
        # 动画
        self.blink_timer = 0
        self.blink = False
        # 功能计时器
        self.timer = 0
        self.sun_timer = 0
        self.shoot_timer = 0

    @property
    def hp_ratio(self) -> float:
        return max(0.0, self.hp / self.max_hp)

    def take_damage(self, dmg: int):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
        self.blink_timer = 6

    def update(self, dt_sec: float, zombies: list, projectiles: list,
               suns: list) -> list:
        """返回新产生的阳光列表"""
        new_suns = []
        self.timer += 1
        if self.blink_timer > 0:
            self.blink_timer -= 1
            self.blink = self.blink_timer % 2 == 1
        else:
            self.blink = False

        if not self.alive:
            return new_suns

        # 向日葵: 产生阳光
        if self.ptype == PLANT_SUNFLOWER:
            self.sun_timer += 1
            if self.sun_timer >= PLANTS_CFG[PLANT_SUNFLOWER]['sun_timer']:
                self.sun_timer = 0
                sx = self.x + CELL_W // 2 + random.randint(-15, 15)
                sy = self.y + 10
                ty = self.y + 30
                new_suns.append(Sun(sx, sy, ty, 25, source='sunflower'))

        # 豌豆射手: 射击
        if self.ptype == PLANT_PEASHOOTER:
            # 检查同行是否有僵尸
            has_zombie = any(
                z.row == self.row and z.x > self.x and z.alive
                for z in zombies
            )
            if has_zombie:
                self.shoot_timer += 1
                if self.shoot_timer >= PLANTS_CFG[PLANT_PEASHOOTER]['shoot_cd']:
                    self.shoot_timer = 0
                    px = self.x + CELL_W + 5
                    py = self.y + CELL_H // 2 - 5
                    projectiles.append(Projectile(px, py))
            else:
                self.shoot_timer = max(0, self.shoot_timer - 1)

        return new_suns

    def draw(self, surf: pygame.Surface):
        if self.ptype == PLANT_SUNFLOWER:
            draw_sunflower(surf, self.x, self.y, hp_ratio=self.hp_ratio, blink=self.blink)
        elif self.ptype == PLANT_PEASHOOTER:
            draw_peashooter(surf, self.x, self.y, hp_ratio=self.hp_ratio, blink=self.blink)
        elif self.ptype == PLANT_WALLNUT:
            draw_wallnut(surf, self.x, self.y, hp_ratio=self.hp_ratio, blink=self.blink)

        # HP条
        if self.hp_ratio < 1.0 and self.alive:
            bw = CELL_W - 10
            bx = self.x + 5
            by = self.y + CELL_H - 8
            pygame.draw.rect(surf, DARK_RED, (bx, by, bw, 4))
            pygame.draw.rect(surf, RED, (bx, by, int(bw * self.hp_ratio), 4))


class Zombie:
    """僵尸基类"""
    def __init__(self, ztype: str, row: int):
        self.ztype = ztype
        self.row = row
        cfg = ZOMBIES_CFG[ztype]
        self.hp = cfg['hp']
        self.max_hp = cfg['hp']
        self.speed = cfg['speed']
        self.damage = cfg['damage']
        self.atk_cd = cfg['atk_cd']
        self.alive = True
        # 起始位置 (屏幕右侧)
        self.x = float(SCREEN_W + 50)
        self.y = float(GRID_Y + row * CELL_H)
        self.atk_timer = 0
        self.anim_frame = 0
        self.eating = False        # 正在啃食植物
        self.target_plant = None   # 被啃的植物
        self.blink_timer = 0

    @property
    def hp_ratio(self) -> float:
        return max(0.0, self.hp / self.max_hp)

    def take_damage(self, dmg: int):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
        self.blink_timer = 4

    def update(self, dt_sec: float, plants: list):
        if not self.alive:
            return
        self.anim_frame += 1
        if self.blink_timer > 0:
            self.blink_timer -= 1

        # 检查前方是否有植物
        self.eating = False
        self.target_plant = None
        for p in plants:
            if not p.alive:
                continue
            if p.row != self.row:
                continue
            # 僵尸在植物的右侧, 相距较近
            px_right = p.x + CELL_W
            if abs(self.x - px_right) < 10:
                self.eating = True
                self.target_plant = p
                break

        if self.eating and self.target_plant:
            self.atk_timer += 1
            if self.atk_timer >= self.atk_cd:
                self.atk_timer = 0
                self.target_plant.take_damage(self.damage)
        else:
            self.x -= self.speed * dt_sec

    def draw(self, surf: pygame.Surface):
        if not self.alive:
            return
        blink_visible = self.blink_timer <= 0 or (self.blink_timer % 2 == 0)
        if not blink_visible:
            return
        draw_zombie(surf, int(self.x), int(self.y),
                    ztype=self.ztype,
                    hp_ratio=self.hp_ratio,
                    anim_frame=self.anim_frame)
        # HP条
        bar_w = 40
        bx = int(self.x) + 5
        by = int(self.y) + 2
        pygame.draw.rect(surf, DARK_RED, (bx, by, bar_w, 4))
        pygame.draw.rect(surf, RED, (bx, by, int(bar_w * self.hp_ratio), 4))


class Lawnmower:
    """割草机 - 每行一个, 末线防御"""
    def __init__(self, row: int):
        self.row = row
        self.x = float(GRID_X - 50)
        self.y = float(GRID_Y + row * CELL_H + CELL_H // 2)
        self.active = False
        self.speed = 350  # pixels/second
        self.alive = True

    def activate(self):
        self.active = True

    def update(self, dt_sec: float, zombies: list):
        if not self.alive:
            return
        if self.active:
            self.x += self.speed * dt_sec
            if self.x > SCREEN_W + 60:
                self.alive = False
            # 检查碰撞
            for z in zombies:
                if z.alive and z.row == self.row:
                    zr = pygame.Rect(int(z.x), int(z.y), 60, CELL_H)
                    mr = pygame.Rect(int(self.x), int(self.y) - 15, 40, 20)
                    if mr.colliderect(zr):
                        z.take_damage(99999)

    def draw(self, surf: pygame.Surface):
        if not self.alive:
            return
        draw_lawnmower(surf, int(self.x), int(self.y), moving=self.active)


# ======================================================
#  关卡管理
# ======================================================

class Level:
    """管理 1-1 关卡的波次和进度"""
    def __init__(self):
        self.waves = LEVEL_WAVES
        self.wave_triggers = WAVE_TRIGGER
        self.current_wave = 0       # 已触发的波次
        self.time_elapsed = 0.0     # 游戏时间 (秒)
        self.all_waves_done = False

    def update(self, dt_sec: float, zombies: list) -> list:
        """返回本帧需要生成的新僵尸列表"""
        self.time_elapsed += dt_sec
        new_zombies = []

        while (self.current_wave < len(self.waves) and
               self.time_elapsed >= self.wave_triggers[self.current_wave]):
            wave = self.waves[self.current_wave]
            # 加入偏移避免堆叠
            for i, (ztype, row) in enumerate(wave):
                z = Zombie(ztype, row)
                z.x = SCREEN_W + 50 + i * 40
                new_zombies.append(z)
            self.current_wave += 1

        # 判断关卡完成
        if self.current_wave >= len(self.waves):
            alive = [z for z in zombies if z.alive]
            if len(alive) == 0:
                self.all_waves_done = True

        return new_zombies

    @property
    def progress(self) -> float:
        """总进度 0.0 ~ 1.0"""
        if not self.wave_triggers:
            return 1.0
        total_time = self.wave_triggers[-1] + 10
        return min(1.0, self.time_elapsed / total_time)

    @property
    def wave_label(self) -> str:
        if self.all_waves_done:
            return "全部击退！"
        w = self.current_wave
        if w >= len(self.waves):
            return "最后一波！"
        return f"第 {w+1}/{len(self.waves)} 波"


# ======================================================
#  开场动画
# ======================================================

class IntroState:
    """开场动画状态"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.timer = 0
        self.done = False
        self.phase = 0
        # 花朵动画
        self.flower_grow = 0.0
        self.title_alpha = 0
        self.sub_alpha = 0
        self.blink_timer = 0

    def handle_event(self, event: pygame.event.Event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            if self.timer > 60:
                self.done = True

    def update(self):
        self.timer += 1
        t = self.timer

        # 阶段0: 黑屏淡入
        if t < 60:
            self.phase = 0
        # 阶段1: 花朵生长
        elif t < 180:
            self.phase = 1
            self.flower_grow = min(1.0, (t - 60) / 80)
        # 阶段2: 标题出现
        elif t < 300:
            self.phase = 2
            self.flower_grow = 1.0
            self.title_alpha = min(255, int((t - 180) / 120 * 255))
        # 阶段3: 副标题 + 等待
        elif t < 420:
            self.phase = 3
            self.title_alpha = 255
            self.sub_alpha = min(255, int((t - 300) / 80 * 255))
        else:
            self.phase = 4
            self.title_alpha = 255
            self.sub_alpha = 255
            self.blink_timer += 1

        if self.timer > 600:
            self.done = True

    def draw(self):
        self.screen.fill(BLACK)
        t = self.timer

        # 背景渐变
        if self.phase >= 1:
            bg_alpha = min(255, int((t - 60) / 40 * 180))
            # 简单渐变背景
            for ry in range(SCREEN_H):
                ratio = ry / SCREEN_H
                r = int(20 + ratio * 30)
                g = int(60 + ratio * 80)
                b = int(20 + ratio * 30)
                pygame.draw.line(self.screen, (r, g, b), (0, ry), (SCREEN_W, ry))

        # 地面
        if self.phase >= 1:
            ground_alpha = min(255, int((t - 60) / 40 * 255))
            ground_surf = pygame.Surface((SCREEN_W, 120), pygame.SRCALPHA)
            ground_surf.fill((80, 130, 50, ground_alpha))
            self.screen.blit(ground_surf, (0, SCREEN_H - 120))
            # 草地纹理
            for gx in range(0, SCREEN_W, 20):
                blade_h = 15 + (gx % 3) * 5
                pygame.draw.line(self.screen, (50, 110, 30),
                                 (gx, SCREEN_H - 120),
                                 (gx + 5, SCREEN_H - 120 - blade_h), 2)

        # 向日葵生长
        if self.phase >= 1:
            scale = self.flower_grow
            for i, (sx, sy) in enumerate([(SCREEN_W//2 - 160, SCREEN_H - 250),
                                           (SCREEN_W//2 + 80, SCREEN_H - 230)]):
                offset_scale = scale * (0.7 + i * 0.15)
                draw_sunflower(self.screen, sx, sy, scale=min(1.0, offset_scale))

            # 豌豆射手
            ps_x, ps_y = SCREEN_W//2 - 30, SCREEN_H - 240
            draw_peashooter(self.screen, ps_x, ps_y, scale=min(1.0, scale))

        # 标题
        if self.phase >= 2 and self.title_alpha > 0:
            title_surf = pygame.Surface((SCREEN_W, 120), pygame.SRCALPHA)
            # 光晕背景
            for offset in range(8, 0, -1):
                glow_col = (0, 180, 0, 20)
                t_font = get_font(62 + offset, bold=True)
                ts = t_font.render(TITLE, True, (0, max(0, 180 - offset*20), 0))
                ts.set_alpha(30)
                title_surf.blit(ts, (SCREEN_W//2 - ts.get_width()//2, 10 + offset//2))
            t_font = get_font(62, bold=True)
            ts = t_font.render(TITLE, True, (50, 220, 50))
            ts2 = t_font.render(TITLE, True, (220, 255, 100))
            title_surf.blit(ts, (SCREEN_W//2 - ts.get_width()//2 + 3, 13))
            title_surf.blit(ts2, (SCREEN_W//2 - ts2.get_width()//2, 10))
            title_surf.set_alpha(self.title_alpha)
            self.screen.blit(title_surf, (0, SCREEN_H//2 - 200))

        # 副标题
        if self.phase >= 3 and self.sub_alpha > 0:
            sub_surf = pygame.Surface((SCREEN_W, 40), pygame.SRCALPHA)
            s_font = get_font(22)
            ss = s_font.render("冒险模式 · 第一关", True, (200, 255, 150))
            sub_surf.blit(ss, (SCREEN_W//2 - ss.get_width()//2, 5))
            sub_surf.set_alpha(self.sub_alpha)
            self.screen.blit(sub_surf, (0, SCREEN_H//2 - 100))

        # 等待提示 (闪烁)
        if self.phase >= 4:
            if (self.blink_timer // 30) % 2 == 0:
                draw_text(self.screen, "按任意键继续",
                          SCREEN_W // 2, SCREEN_H - 60,
                          size=22, color=(220, 220, 100),
                          center=True, shadow=True)

        # 初始黑屏遮罩淡出
        if t < 30:
            fade_alpha = int(255 * (1 - t / 30))
            mask = pygame.Surface((SCREEN_W, SCREEN_H))
            mask.fill(BLACK)
            mask.set_alpha(fade_alpha)
            self.screen.blit(mask, (0, 0))


# ======================================================
#  主菜单
# ======================================================

class Button:
    def __init__(self, x: int, y: int, w: int, h: int, text: str,
                 bg=(80, 140, 60), hover=(100, 180, 80), text_color=WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.bg = bg
        self.hover = hover
        self.text_color = text_color
        self.hovered = False

    def update(self, mouse_pos: tuple):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surf: pygame.Surface):
        col = self.hover if self.hovered else self.bg
        pygame.draw.rect(surf, col, self.rect, border_radius=10)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=10)
        draw_text(surf, self.text,
                  self.rect.centerx, self.rect.centery,
                  size=24, color=self.text_color,
                  bold=True, center=True, shadow=True)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


class MenuState:
    """主菜单状态"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.action = None
        cx = SCREEN_W // 2
        self.btn_start = Button(cx - 120, 280, 240, 55, "冒险模式",
                                bg=(40, 120, 40), hover=(60, 160, 60))
        self.btn_quit  = Button(cx - 120, 365, 240, 55, "退出游戏",
                                bg=(120, 40, 40), hover=(160, 60, 60))
        self.timer = 0
        # 动画用的背景僵尸
        self.bg_zombies: list[dict] = []
        for i in range(3):
            self.bg_zombies.append({
                'x': SCREEN_W + 50 + i * 200,
                'y': SCREEN_H - 80 - (i % 3) * 20,
                'row': i % GRID_ROWS,
                'frame': i * 30,
                'speed': 20 + i * 5,
            })

    def handle_event(self, event: pygame.event.Event):
        if self.btn_start.is_clicked(event):
            self.action = 'start'
        if self.btn_quit.is_clicked(event):
            self.action = 'quit'

    def update(self):
        self.timer += 1
        mouse_pos = pygame.mouse.get_pos()
        self.btn_start.update(mouse_pos)
        self.btn_quit.update(mouse_pos)
        # 移动背景僵尸
        for z in self.bg_zombies:
            z['x'] -= z['speed'] / FPS
            z['frame'] += 1
            if z['x'] < -80:
                z['x'] = SCREEN_W + 50

    def draw(self):
        # 背景
        for ry in range(SCREEN_H):
            ratio = ry / SCREEN_H
            r = int(60 + ratio * 30)
            g = int(120 + ratio * 40)
            b = int(40 + ratio * 20)
            pygame.draw.line(self.screen, (r, g, b), (0, ry), (SCREEN_W, ry))

        # 地面
        ground_rect = pygame.Rect(0, SCREEN_H - 120, SCREEN_W, 120)
        pygame.draw.rect(self.screen, (70, 120, 45), ground_rect)
        for gx in range(0, SCREEN_W, 18):
            blade_h = 10 + gx % 15
            pygame.draw.line(self.screen, (45, 100, 25),
                             (gx, SCREEN_H - 120),
                             (gx + 4, SCREEN_H - 120 - blade_h), 2)

        # 背景中的向日葵
        for i, (bx, by) in enumerate([(60, SCREEN_H - 220), (680, SCREEN_H - 200),
                                       (160, SCREEN_H - 210), (570, SCREEN_H - 215)]):
            draw_sunflower(self.screen, bx, by, scale=0.85)

        # 背景僵尸 (半透明)
        for z in self.bg_zombies:
            tmp = pygame.Surface((80, CELL_H), pygame.SRCALPHA)
            draw_zombie(tmp, 0, 0, ZOMBIE_NORMAL, scale=0.9, anim_frame=z['frame'])
            tmp.set_alpha(100)
            self.screen.blit(tmp, (int(z['x']), int(z['y'])))

        # 标题
        shadow_font = get_font(68, bold=True)
        title_shadow = shadow_font.render(TITLE, True, (0, 80, 0))
        self.screen.blit(title_shadow,
                         (SCREEN_W//2 - title_shadow.get_width()//2 + 4,
                          90 + 4))
        title_font = get_font(68, bold=True)
        # 渐变色标题
        title_surf = pygame.Surface((SCREEN_W, 100), pygame.SRCALPHA)
        wave_off = math.sin(self.timer * 0.05) * 5
        for ci, char in enumerate(TITLE):
            char_surf = title_font.render(char, True,
                                          (100 + ci * 20 % 100,
                                           220 - ci * 10 % 60,
                                           50))
            char_x = (SCREEN_W - title_font.size(TITLE)[0]) // 2 + title_font.size(TITLE[:ci])[0]
            char_y = int(wave_off * math.sin(ci * 0.8 + self.timer * 0.05))
            title_surf.blit(char_surf, (char_x, 10 + char_y))
        self.screen.blit(title_surf, (0, 86))

        # 副标题
        draw_text(self.screen, "第一关: 白天", SCREEN_W//2, 195,
                  size=22, color=(200, 255, 150), center=True, shadow=True)

        # 装饰线
        pygame.draw.line(self.screen, (100, 200, 80),
                         (SCREEN_W//2 - 200, 230), (SCREEN_W//2 + 200, 230), 2)

        # 按钮
        self.btn_start.draw(self.screen)
        self.btn_quit.draw(self.screen)

        # 操作说明
        draw_text(self.screen, "鼠标左键: 选择/放置植物  |  右键: 取消选择",
                  SCREEN_W//2, SCREEN_H - 30,
                  size=14, color=(180, 180, 180), center=True)


# ======================================================
#  胜利/失败画面
# ======================================================

class WinState:
    """胜利画面"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.timer = 0
        cx = SCREEN_W // 2
        self.btn_menu = Button(cx - 110, 380, 220, 55, "返回主菜单",
                               bg=(40, 120, 40), hover=(60, 160, 60))
        self.action = None
        self.stars: list[dict] = []
        for _ in range(30):
            self.stars.append({
                'x': random.randint(50, SCREEN_W - 50),
                'y': random.randint(50, SCREEN_H - 50),
                'r': random.randint(3, 8),
                'speed_y': random.uniform(-80, -30),
                'speed_x': random.uniform(-20, 20),
                'alpha': 255,
            })

    def handle_event(self, event: pygame.event.Event):
        if self.btn_menu.is_clicked(event):
            self.action = 'menu'

    def update(self):
        self.timer += 1
        self.btn_menu.update(pygame.mouse.get_pos())
        dt = 1 / FPS
        for s in self.stars:
            s['y'] += s['speed_y'] * dt
            s['x'] += s['speed_x'] * dt
            s['alpha'] = max(0, s['alpha'] - 1)
            if s['alpha'] == 0 or s['y'] < 0:
                s['x'] = random.randint(50, SCREEN_W - 50)
                s['y'] = SCREEN_H + 10
                s['alpha'] = 255
                s['speed_y'] = random.uniform(-80, -30)

    def draw(self):
        # 背景
        for ry in range(SCREEN_H):
            ratio = ry / SCREEN_H
            r = int(20 + ratio * 20)
            g = int(40 + ratio * 80)
            b = int(10 + ratio * 20)
            pygame.draw.line(self.screen, (r, g, b), (0, ry), (SCREEN_W, ry))

        # 星星
        for s in self.stars:
            star_surf = pygame.Surface((s['r']*2, s['r']*2), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, (255, 230, 50, s['alpha']),
                                (s['r'], s['r']), s['r'])
            self.screen.blit(star_surf, (int(s['x'] - s['r']), int(s['y'] - s['r'])))

        # 庆祝植物
        for i, bx in enumerate([100, 300, 500, 700]):
            draw_sunflower(self.screen, bx, SCREEN_H - 200, scale=1.0)

        # 标题
        wave_y = math.sin(self.timer * 0.08) * 8
        draw_text(self.screen, "关卡完成！",
                  SCREEN_W//2, int(150 + wave_y),
                  size=64, color=(80, 255, 80), bold=True,
                  center=True, shadow=True)
        draw_text(self.screen, "🌟 你成功保卫了家园！ 🌟",
                  SCREEN_W//2, 260,
                  size=28, color=(255, 230, 100),
                  center=True, shadow=True)
        draw_text(self.screen, "第1关 · 第1天 — 完成",
                  SCREEN_W//2, 320,
                  size=22, color=(200, 255, 180),
                  center=True)
        self.btn_menu.draw(self.screen)


class LoseState:
    """失败画面"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.timer = 0
        cx = SCREEN_W // 2
        self.btn_retry = Button(cx - 120, 350, 240, 55, "再试一次",
                                bg=(120, 80, 40), hover=(160, 110, 60))
        self.btn_menu  = Button(cx - 120, 430, 240, 55, "返回主菜单",
                                bg=(80, 40, 40), hover=(120, 60, 60))
        self.action = None
        self.shake = 20

    def handle_event(self, event: pygame.event.Event):
        if self.btn_retry.is_clicked(event):
            self.action = 'retry'
        if self.btn_menu.is_clicked(event):
            self.action = 'menu'

    def update(self):
        self.timer += 1
        if self.shake > 0:
            self.shake -= 1
        self.btn_retry.update(pygame.mouse.get_pos())
        self.btn_menu.update(pygame.mouse.get_pos())

    def draw(self):
        # 黑暗背景
        for ry in range(SCREEN_H):
            ratio = ry / SCREEN_H
            r = int(60 + ratio * 40)
            g = int(10 + ratio * 10)
            b = int(10 + ratio * 10)
            pygame.draw.line(self.screen, (r, g, b), (0, ry), (SCREEN_W, ry))

        # 僵尸群
        for i in range(5):
            zx = 80 + i * 140
            draw_zombie(self.screen, zx, SCREEN_H - 180, ZOMBIE_NORMAL,
                        scale=0.9, anim_frame=self.timer + i * 20)

        # 震动文字
        shake_x = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        shake_y = random.randint(-self.shake//2, self.shake//2) if self.shake > 0 else 0

        draw_text(self.screen, "僵尸吃掉了你的脑子！",
                  SCREEN_W//2 + shake_x, 140 + shake_y,
                  size=48, color=(220, 50, 50), bold=True,
                  center=True, shadow=True)
        draw_text(self.screen, "别灰心，再试一次吧！",
                  SCREEN_W//2, 240,
                  size=28, color=(255, 180, 100),
                  center=True, shadow=True)

        self.btn_retry.draw(self.screen)
        self.btn_menu.draw(self.screen)


# ======================================================
#  游戏主状态
# ======================================================

class GameState:
    """游戏进行状态"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.reset()

    def reset(self):
        self.sun = 150
        self.plants: list[Plant] = []
        self.zombies: list[Zombie] = []
        self.projectiles: list[Projectile] = []
        self.suns: list[Sun] = []
        self.lawnmowers: list[Lawnmower] = [Lawnmower(r) for r in range(GRID_ROWS)]
        self.level = Level()
        self.selected_plant: str | None = None
        self.hovering_cell: tuple[int, int] | None = None
        self.result = None  # 'win' or 'lose'
        self.timer = 0
        self.sky_sun_timer = 0
        self.next_sky_sun = random.randint(450, 750)
        self.seed_packets = [
            {'type': PLANT_SUNFLOWER, 'cooldown_left': 0},
            {'type': PLANT_PEASHOOTER, 'cooldown_left': 0},
            {'type': PLANT_WALLNUT, 'cooldown_left': 0},
        ]
        # 消息提示
        self.messages: list[dict] = []
        # 初始引导消息
        self._add_message("种植向日葵来收集更多阳光！", 4.0, (255, 230, 100))

    def _add_message(self, text: str, duration: float = 3.0, color=WHITE):
        self.messages.append({'text': text, 'timer': duration * FPS, 'color': color})

    def _get_cell(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        mx, my = pos
        col = (mx - GRID_X) // CELL_W
        row = (my - GRID_Y) // CELL_H
        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            return col, row
        return None

    def _cell_occupied(self, col: int, row: int) -> bool:
        return any(p.col == col and p.row == row and p.alive for p in self.plants)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if event.button == 3:  # 右键取消选择
                self.selected_plant = None
                return

            if event.button == 1:
                # 点击种子包
                for i, sp in enumerate(self.seed_packets):
                    sx = 85 + i * 62
                    sr = pygame.Rect(sx, 8, 55, 70)
                    if sr.collidepoint(mx, my):
                        ptype = sp['type']
                        cost = PLANTS_CFG[ptype]['cost']
                        on_cd = sp['cooldown_left'] > 0
                        if self.sun >= cost and not on_cd:
                            if self.selected_plant == ptype:
                                self.selected_plant = None
                            else:
                                self.selected_plant = ptype
                        elif self.sun < cost:
                            self._add_message("阳光不够！", 2.0, (255, 100, 100))
                        elif on_cd:
                            self._add_message("正在冷却中...", 2.0, (200, 200, 100))
                        return

                # 点击阳光
                for s in self.suns:
                    if not s.collected and s.reached and s.get_rect().collidepoint(mx, my):
                        s.collect()
                        self.sun += s.amount
                        return

                # 放置植物
                if self.selected_plant:
                    cell = self._get_cell((mx, my))
                    if cell:
                        col, row = cell
                        cost = PLANTS_CFG[self.selected_plant]['cost']
                        if self._cell_occupied(col, row):
                            self._add_message("这里已经有植物了！", 2.0, (255, 100, 100))
                        elif self.sun < cost:
                            self._add_message("阳光不够！", 2.0, (255, 100, 100))
                        else:
                            self.plants.append(Plant(self.selected_plant, col, row))
                            self.sun -= cost
                            # 设置冷却
                            for sp in self.seed_packets:
                                if sp['type'] == self.selected_plant:
                                    sp['cooldown_left'] = PLANTS_CFG[self.selected_plant]['cooldown']
                            self.selected_plant = None
                    return

                # 没有选中植物时点击阳光 (宽松检测)
                for s in self.suns:
                    if not s.collected and s.get_rect().collidepoint(mx, my):
                        s.collect()
                        self.sun += s.amount
                        return

    def update(self):
        dt = 1.0 / FPS
        self.timer += 1

        # 更新种子包冷却
        for sp in self.seed_packets:
            if sp['cooldown_left'] > 0:
                sp['cooldown_left'] -= 1

        # 天空掉落阳光
        self.sky_sun_timer += 1
        if self.sky_sun_timer >= self.next_sky_sun:
            self.sky_sun_timer = 0
            self.next_sky_sun = random.randint(450, 750)
            sx = GRID_X + random.randint(0, GRID_COLS * CELL_W)
            ty = GRID_Y + random.randint(0, GRID_ROWS * CELL_H - 30)
            self.suns.append(Sun(sx, 0, ty, 25, 'sky'))

        # 更新关卡, 获取新僵尸
        new_zombies = self.level.update(dt, self.zombies)
        if new_zombies:
            self.zombies.extend(new_zombies)
            if any(z.ztype == ZOMBIE_FLAG for z in new_zombies):
                self._add_message("大波僵尸来袭！！！", 4.0, (255, 60, 60))

        # 更新阳光
        self.suns = [s for s in self.suns if s.update(dt)]

        # 更新植物, 收集新阳光和子弹
        for p in self.plants:
            new_suns = p.update(dt, self.zombies, self.projectiles, self.suns)
            self.suns.extend(new_suns)
        self.plants = [p for p in self.plants if p.alive]

        # 更新子弹
        for proj in self.projectiles:
            proj.update(dt)
            if proj.x > SCREEN_W + 20:
                proj.alive = False
            else:
                for z in self.zombies:
                    if z.alive and pygame.Rect(int(z.x), int(z.y), 60, CELL_H).colliderect(proj.get_rect()):
                        if z.row == self._get_proj_row(proj):
                            z.take_damage(proj.damage)
                            proj.alive = False
                            break
        self.projectiles = [p for p in self.projectiles if p.alive]

        # 更新僵尸
        for z in self.zombies:
            z.update(dt, self.plants)
        # 死亡僵尸延迟移除
        self.zombies = [z for z in self.zombies if z.alive or (
            hasattr(z, '_death_timer') and z._death_timer < ZOMBIE_DEATH_ANIMATION_FRAMES)]
        for z in self.zombies:
            if not z.alive:
                if not hasattr(z, '_death_timer'):
                    z._death_timer = 0
                z._death_timer += 1

        # 更新割草机
        for lm in self.lawnmowers:
            lm.update(dt, self.zombies)
            if not lm.active and lm.alive:
                # 检查是否有僵尸到达割草机区域
                for z in self.zombies:
                    if z.alive and z.row == lm.row and z.x < GRID_X - 5:
                        lm.activate()
                        self._add_message("割草机启动！", 2.0, (255, 200, 100))
                        break

        # 消息更新
        for msg in self.messages:
            msg['timer'] -= 1
        self.messages = [m for m in self.messages if m['timer'] > 0]

        # 悬停格
        mx, my = pygame.mouse.get_pos()
        self.hovering_cell = self._get_cell((mx, my))

        # 胜负判断
        if self.level.all_waves_done:
            self.result = 'win'
        else:
            for z in self.zombies:
                if z.alive and z.x < GRID_X - 60:
                    # 检查是否还有割草机
                    has_mower = any(lm.row == z.row and lm.alive and not lm.active
                                    for lm in self.lawnmowers)
                    if not has_mower:
                        self.result = 'lose'
                        break

    def _get_proj_row(self, proj: Projectile) -> int:
        """根据子弹y坐标判断所在行"""
        row = (int(proj.y) - GRID_Y) // CELL_H
        return max(0, min(GRID_ROWS - 1, row))

    def draw(self):
        # 背景
        draw_background(self.screen)

        # 高亮悬停格子
        if self.selected_plant and self.hovering_cell:
            col, row = self.hovering_cell
            hx = GRID_X + col * CELL_W
            hy = GRID_Y + row * CELL_H
            highlight = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
            if self._cell_occupied(col, row):
                highlight.fill((255, 50, 50, 60))
            else:
                highlight.fill((100, 255, 100, 60))
            self.screen.blit(highlight, (hx, hy))
            # 预览植物 (半透明)
            preview = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
            preview.fill((0, 0, 0, 0))
            if self.selected_plant == PLANT_SUNFLOWER:
                draw_sunflower(preview, 0, 0)
            elif self.selected_plant == PLANT_PEASHOOTER:
                draw_peashooter(preview, 0, 0)
            elif self.selected_plant == PLANT_WALLNUT:
                draw_wallnut(preview, 0, 0)
            preview.set_alpha(140)
            self.screen.blit(preview, (hx, hy))

        # 割草机
        for lm in self.lawnmowers:
            lm.draw(self.screen)

        # 植物
        for p in self.plants:
            p.draw(self.screen)

        # 子弹
        for proj in self.projectiles:
            proj.draw(self.screen)

        # 僵尸
        for z in self.zombies:
            z.draw(self.screen)

        # 阳光
        for s in self.suns:
            s.draw(self.screen)

        # 顶栏
        draw_topbar(self.screen, self.sun, self.seed_packets, self.selected_plant)

        # 进度条
        label = ""
        if self.level.all_waves_done:
            label = "全部击退！"
        elif self.level.current_wave >= len(LEVEL_WAVES):
            label = "最后一波！"
        draw_progress_bar(self.screen, self.level.progress,
                          self.level.current_wave,
                          len(LEVEL_WAVES), label=label)

        # 消息
        for i, msg in enumerate(reversed(self.messages)):
            alpha = min(255, msg['timer'] * 3)
            msg_surf = pygame.Surface((500, 35), pygame.SRCALPHA)
            draw_text(msg_surf, msg['text'], 250, 17,
                      size=22, color=msg['color'], bold=True, center=True, shadow=True)
            msg_surf.set_alpha(int(alpha))
            self.screen.blit(msg_surf, (SCREEN_W//2 - 250, 100 + i * 40))

        # 鼠标图标 (选中植物时显示植物缩图)
        if self.selected_plant:
            mx, my = pygame.mouse.get_pos()
            cursor_surf = pygame.Surface((40, 50), pygame.SRCALPHA)
            cursor_surf.fill((0, 0, 0, 0))
            if self.selected_plant == PLANT_SUNFLOWER:
                draw_sunflower(cursor_surf, -10, -10, scale=0.5)
            elif self.selected_plant == PLANT_PEASHOOTER:
                draw_peashooter(cursor_surf, -10, -10, scale=0.5)
            elif self.selected_plant == PLANT_WALLNUT:
                draw_wallnut(cursor_surf, -10, -10, scale=0.5)
            self.screen.blit(cursor_surf, (mx, my - 10))


# ======================================================
#  主游戏控制器
# ======================================================

class PvZGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self._set_icon()
        self.state_id = STATE_INTRO
        self.intro  = IntroState(self.screen)
        self.menu   = MenuState(self.screen)
        self.game   = GameState(self.screen)
        self.win    = WinState(self.screen)
        self.lose   = LoseState(self.screen)
        # 隐藏系统光标 (在放置植物时显示自定义)
        pygame.mouse.set_visible(True)

    def _set_icon(self):
        """用向日葵作为窗口图标"""
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        icon.fill((0, 0, 0, 0))
        draw_sunflower(icon, -5, -5, scale=0.45)
        pygame.display.set_icon(icon)

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)
            self._update()
            self._draw()
            pygame.display.flip()

    def _handle_event(self, event: pygame.event.Event):
        if self.state_id == STATE_INTRO:
            self.intro.handle_event(event)
        elif self.state_id == STATE_MENU:
            self.menu.handle_event(event)
        elif self.state_id == STATE_PLAYING:
            self.game.handle_event(event)
        elif self.state_id == STATE_WIN:
            self.win.handle_event(event)
        elif self.state_id == STATE_LOSE:
            self.lose.handle_event(event)

    def _update(self):
        if self.state_id == STATE_INTRO:
            self.intro.update()
            if self.intro.done:
                self.state_id = STATE_MENU

        elif self.state_id == STATE_MENU:
            self.menu.update()
            if self.menu.action == 'start':
                self.game.reset()
                self.state_id = STATE_PLAYING
                self.menu.action = None
            elif self.menu.action == 'quit':
                pygame.quit()
                sys.exit()

        elif self.state_id == STATE_PLAYING:
            self.game.update()
            if self.game.result == 'win':
                self.win = WinState(self.screen)
                self.state_id = STATE_WIN
            elif self.game.result == 'lose':
                self.lose = LoseState(self.screen)
                self.state_id = STATE_LOSE

        elif self.state_id == STATE_WIN:
            self.win.update()
            if self.win.action == 'menu':
                self.menu = MenuState(self.screen)
                self.state_id = STATE_MENU
                self.win.action = None

        elif self.state_id == STATE_LOSE:
            self.lose.update()
            if self.lose.action == 'retry':
                self.game.reset()
                self.state_id = STATE_PLAYING
                self.lose.action = None
            elif self.lose.action == 'menu':
                self.menu = MenuState(self.screen)
                self.state_id = STATE_MENU
                self.lose.action = None

    def _draw(self):
        if self.state_id == STATE_INTRO:
            self.intro.draw()
        elif self.state_id == STATE_MENU:
            self.menu.draw()
        elif self.state_id == STATE_PLAYING:
            self.game.draw()
        elif self.state_id == STATE_WIN:
            self.win.draw()
        elif self.state_id == STATE_LOSE:
            self.lose.draw()


# ======================================================
#  入口
# ======================================================

def main():
    game = PvZGame()
    game.run()


if __name__ == '__main__':
    main()
