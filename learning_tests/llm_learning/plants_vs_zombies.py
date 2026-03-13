#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物大战僵尸 - 第1-1关 完全还原版
Plants vs. Zombies - Level 1-1 Full Recreation

运行方式: python plants_vs_zombies.py
依赖: pygame  (pip install pygame)
"""

import pygame
import sys
import random
import math

pygame.init()

SCREEN_W, SCREEN_H = 900, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("植物大战僵尸")
clock = pygame.time.Clock()
FPS = 60

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (220, 50,  50)
LAWN_A = (100, 180, 58)
LAWN_B = (86,  160, 46)
GRAY   = (150, 150, 150)
UI_BG  = (40,  68,  22)
UI_LINE= (20,  40,  10)


def _load_fonts():
    for name in ("wenquanyizenhei", "wenquanyimicrohei", None):
        try:
            return {
                "sm":    pygame.font.SysFont(name, 18),
                "md":    pygame.font.SysFont(name, 24),
                "lg":    pygame.font.SysFont(name, 36),
                "xl":    pygame.font.SysFont(name, 54),
                "title": pygame.font.SysFont(name, 72),
            }
        except Exception:
            pass
    return {k: pygame.font.SysFont(None, s)
            for k, s in [("sm", 18), ("md", 24), ("lg", 36), ("xl", 54), ("title", 72)]}

fonts = _load_fonts()


def draw_text(surf, text, key, color, x, y, center=False, shadow=True):
    f = fonts[key]
    if shadow:
        s = f.render(text, True, (0, 0, 0))
        r = s.get_rect()
        if center:
            r.center = (x + 2, y + 2)
        else:
            r.topleft = (x + 2, y + 2)
        surf.blit(s, r)
    img = f.render(text, True, color)
    r = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)
    return r


COLS = 9
ROWS = 5
CW   = 80
CH   = 96
GX   = 135
GY   = 102
LM_X = 78

S_INTRO  = 0
S_MENU   = 1
S_LINTRO = 2
S_GAME   = 3
S_WIN    = 4
S_LOSE   = 5


def cell_rect(col, row):
    return pygame.Rect(GX + col * CW, GY + row * CH, CW, CH)


def cell_center(col, row):
    r = cell_rect(col, row)
    return r.centerx, r.centery


def xy_to_cell(x, y):
    col = int((x - GX) // CW)
    row = int((y - GY) // CH)
    if 0 <= col < COLS and 0 <= row < ROWS:
        return col, row
    return None


def row_y(row):
    return GY + row * CH + CH // 2


def _make_day_bg():
    surf = pygame.Surface((SCREEN_W, SCREEN_H))
    for yy in range(GY):
        t = yy / max(GY, 1)
        r = int(135 + 65 * t)
        g = int(200 + 30 * t)
        surf.fill((r, g, 255), (0, yy, SCREEN_W, 1))
    for row in range(ROWS):
        color = LAWN_A if row % 2 == 0 else LAWN_B
        surf.fill(color, (0, GY + row * CH, SCREEN_W, CH))
    surf.fill((100, 160, 55), (0, GY, GX, ROWS * CH))
    surf.fill((120, 175, 65), (GX + COLS * CW, GY, SCREEN_W - (GX + COLS * CW), ROWS * CH))
    for col in range(COLS + 1):
        x = GX + col * CW
        pygame.draw.line(surf, (0, 0, 0), (x, GY), (x, GY + ROWS * CH), 1)
    for row in range(ROWS + 1):
        y = GY + row * CH
        pygame.draw.line(surf, (0, 0, 0), (GX, y), (GX + COLS * CW, y), 1)
    return surf


def _make_night_bg():
    surf = pygame.Surface((SCREEN_W, SCREEN_H))
    surf.fill((8, 5, 18))
    pygame.draw.rect(surf, (18, 50, 18), (0, 400, SCREEN_W, 200))
    return surf


_day_bg_cache   = None
_night_bg_cache = None


def get_day_bg():
    global _day_bg_cache
    if _day_bg_cache is None:
        _day_bg_cache = _make_day_bg()
    return _day_bg_cache


def get_night_bg():
    global _night_bg_cache
    if _night_bg_cache is None:
        _night_bg_cache = _make_night_bg()
    return _night_bg_cache


def draw_sunflower(surf, cx, cy, frame=0, s=1.0):
    pygame.draw.line(surf, (50, 150, 38),
                     (int(cx), int(cy + 14*s)), (int(cx), int(cy + 40*s)),
                     max(1, int(5*s)))
    pygame.draw.ellipse(surf, (70, 170, 45),
                        (int(cx+2*s), int(cy+22*s), int(18*s), int(9*s)))
    pygame.draw.ellipse(surf, (70, 170, 45),
                        (int(cx-20*s), int(cy+26*s), int(18*s), int(9*s)))
    anim = frame * 0.05
    for i in range(8):
        a  = i * math.pi/4 + anim
        px = cx + math.cos(a) * 18*s
        py = cy - 8*s + math.sin(a) * 18*s
        pygame.draw.ellipse(surf, (255, 190, 10),
                            (int(px-7*s), int(py-5*s), int(14*s), int(9*s)))
    for i in range(8):
        a  = i * math.pi/4 + anim + math.pi/8
        px = cx + math.cos(a) * 16*s
        py = cy - 8*s + math.sin(a) * 16*s
        pygame.draw.ellipse(surf, (255, 210, 30),
                            (int(px-5*s), int(py-4*s), int(10*s), int(7*s)))
    pygame.draw.circle(surf, (75, 48, 8),  (int(cx), int(cy-8*s)), int(12*s))
    pygame.draw.circle(surf, (50, 28, 4),  (int(cx), int(cy-8*s)), int(9*s))
    ey = int(cy - 10*s)
    for ox in [-4, 4]:
        pygame.draw.circle(surf, WHITE, (int(cx+ox*s), ey), max(1, int(2.5*s)))
        pygame.draw.circle(surf, BLACK, (int(cx+ox*s), ey), max(1, int(1.5*s)))
    pygame.draw.arc(surf, (180, 100, 10),
                    pygame.Rect(int(cx-5*s), int(cy-4*s), int(10*s), int(6*s)),
                    math.pi, 0, max(1, int(1.5*s)))


def draw_peashooter(surf, cx, cy, frame=0, s=1.0):
    pygame.draw.line(surf, (38, 138, 38),
                     (int(cx), int(cy+17*s)), (int(cx), int(cy+40*s)),
                     max(1, int(7*s)))
    pygame.draw.rect(surf, (28, 118, 28),
                     (int(cx+7*s), int(cy-7*s), int(30*s), int(13*s)))
    pygame.draw.ellipse(surf, (18, 98, 18),
                        (int(cx+33*s), int(cy-8*s), int(13*s), int(15*s)))
    pygame.draw.circle(surf, (58, 170, 58), (int(cx), int(cy)), int(22*s))
    pygame.draw.circle(surf, (78, 195, 78), (int(cx-4*s), int(cy-4*s)), int(15*s))
    pygame.draw.circle(surf, WHITE, (int(cx-7*s), int(cy-5*s)), max(1, int(5*s)))
    pygame.draw.circle(surf, BLACK, (int(cx-6*s), int(cy-5*s)), max(1, int(3*s)))
    pygame.draw.circle(surf, WHITE, (int(cx+5*s), int(cy-7*s)), max(1, int(3*s)))
    pygame.draw.circle(surf, BLACK, (int(cx+5*s), int(cy-7*s)), max(1, int(2*s)))
    pygame.draw.arc(surf, (28, 120, 28),
                    pygame.Rect(int(cx-8*s), int(cy+3*s), int(13*s), int(9*s)),
                    math.pi, 0, max(1, int(2*s)))


def draw_wallnut(surf, cx, cy, hp_ratio=1.0, s=1.0):
    if hp_ratio > 0.66:
        c1, c2 = (165, 108, 42), (128, 78, 22)
    elif hp_ratio > 0.33:
        c1, c2 = (140, 82, 28), (98, 52, 12)
    else:
        c1, c2 = (112, 58, 16), (72, 32, 6)
    pygame.draw.ellipse(surf, c1,
                        (int(cx-26*s), int(cy-27*s), int(52*s), int(52*s)))
    pygame.draw.arc(surf, c2,
                    pygame.Rect(int(cx-22*s), int(cy-23*s), int(44*s), int(20*s)),
                    0, math.pi, max(1, int(2*s)))
    if hp_ratio < 0.66:
        pygame.draw.line(surf, c2,
                         (int(cx-4*s), int(cy-20*s)), (int(cx+6*s), int(cy+5*s)),
                         max(1, int(2*s)))
    if hp_ratio < 0.33:
        pygame.draw.line(surf, c2,
                         (int(cx+10*s), int(cy-18*s)), (int(cx-8*s), int(cy+8*s)),
                         max(1, int(2*s)))
    ey = int(cy-7*s) if hp_ratio > 0.5 else int(cy-5*s)
    ew = max(1, int(3.5*s * (1 if hp_ratio > 0.5 else 0.5)))
    for ex in [int(cx-9*s), int(cx+9*s)]:
        pygame.draw.ellipse(surf, WHITE, (ex-int(4*s), ey-ew, int(8*s), ew*2))
        pygame.draw.circle(surf, BLACK,  (ex, ey), max(1, int(2*s)))
    mr = pygame.Rect(int(cx-9*s), int(cy+6*s), int(18*s), int(10*s))
    if hp_ratio > 0.5:
        pygame.draw.arc(surf, c2, mr, math.pi, 0, max(1, int(2*s)))
    else:
        pygame.draw.arc(surf, c2, mr, 0, math.pi, max(1, int(2*s)))


def _zombie_body(surf, cx, cy, bc, frame, s):
    walk = math.sin(frame * 0.15)
    lc   = (100, 120, 88)
    l1   = walk * 9 * s
    pygame.draw.line(surf, lc,
                     (int(cx-8*s), int(cy+18*s)), (int(cx-6*s+l1), int(cy+40*s)),
                     max(1, int(6*s)))
    pygame.draw.line(surf, lc,
                     (int(cx+8*s), int(cy+18*s)), (int(cx+6*s-l1), int(cy+40*s)),
                     max(1, int(6*s)))
    pygame.draw.ellipse(surf, (48, 38, 28),
                        (int(cx-14*s+l1), int(cy+35*s), int(14*s), int(7*s)))
    pygame.draw.ellipse(surf, (48, 38, 28),
                        (int(cx-l1), int(cy+35*s), int(14*s), int(7*s)))
    pygame.draw.rect(surf, bc,
                     (int(cx-14*s), int(cy-15*s), int(28*s), int(33*s)))
    pygame.draw.polygon(surf, (68, 88, 168),
                        [(int(cx), int(cy-12*s)), (int(cx-3*s), int(cy)),
                         (int(cx), int(cy+7*s)),  (int(cx+3*s), int(cy))])
    ay = int(cy - 4*s)
    pygame.draw.line(surf, bc,
                     (int(cx-14*s), ay), (int(cx-36*s), ay-int(2*s*walk)),
                     max(1, int(6*s)))
    pygame.draw.line(surf, bc,
                     (int(cx+14*s), ay), (int(cx+28*s), int(cy-14*s)),
                     max(1, int(5*s)))
    pygame.draw.circle(surf, bc, (int(cx-36*s), ay-int(2*s*walk)), max(1, int(5*s)))


def draw_normal_zombie(surf, cx, cy, hp_ratio=1.0, frame=0, s=1.0):
    bc = (128, 148, 118) if hp_ratio > 0.5 else (108, 123, 98)
    _zombie_body(surf, cx, cy, bc, frame, s)
    hc = (148, 168, 138) if hp_ratio > 0.3 else (128, 143, 118)
    pygame.draw.ellipse(surf, hc,
                        (int(cx-16*s), int(cy-46*s), int(32*s), int(32*s)))
    for i in range(4):
        hx = int(cx - 12*s + i*8*s)
        hy = int(cy - 44*s)
        pygame.draw.line(surf, (68, 58, 48),
                         (hx, hy), (hx+(i-1)*3, hy-int(10*s+i*3)),
                         max(1, int(2*s)))
    for ex, ey in [(int(cx-6*s), int(cy-35*s)), (int(cx+6*s), int(cy-35*s))]:
        pygame.draw.circle(surf, (212, 212, 192), (ex, ey), max(1, int(4*s)))
        pygame.draw.circle(surf, BLACK, (ex, ey), max(1, int(2*s)))
    pygame.draw.arc(surf, (88, 68, 58),
                    pygame.Rect(int(cx-8*s), int(cy-26*s), int(16*s), int(8*s)),
                    math.pi, 0, max(1, int(2*s)))


def draw_cone_zombie(surf, cx, cy, hp_ratio=1.0, frame=0, s=1.0, cone_hp=1.0):
    draw_normal_zombie(surf, cx, cy, hp_ratio, frame, s)
    if cone_hp > 0:
        cc  = (255, 108, 0) if cone_hp > 0.5 else (198, 68, 0)
        pts = [(int(cx-16*s), int(cy-43*s)),
               (int(cx+16*s), int(cy-43*s)),
               (int(cx),      int(cy-68*s))]
        pygame.draw.polygon(surf, cc, pts)
        pygame.draw.line(surf, WHITE,
                         (int(cx-11*s), int(cy-51*s)),
                         (int(cx+11*s), int(cy-51*s)),
                         max(1, int(3*s)))


def draw_pea(surf, x, y, frozen=False):
    c   = (48, 198, 48)  if not frozen else (78, 168, 255)
    rim = (28, 138, 28)  if not frozen else (48, 118, 198)
    pygame.draw.circle(surf, c,   (int(x), int(y)), 6)
    pygame.draw.circle(surf, rim, (int(x), int(y)), 6, 1)
    pygame.draw.circle(surf, (198, 255, 198) if not frozen else (198, 228, 255),
                       (int(x)-2, int(y)-2), 2)


def draw_sun(surf, x, y, frame=0, s=0.9):
    cx, cy, r = int(x), int(y), int(18*s)
    for i in range(8):
        a  = i * math.pi/4 + frame * 0.04
        x1 = cx + int(math.cos(a) * (r+3))
        y1 = cy + int(math.sin(a) * (r+3))
        x2 = cx + int(math.cos(a) * (r+12))
        y2 = cy + int(math.sin(a) * (r+12))
        pygame.draw.line(surf, (255, 198, 0), (x1, y1), (x2, y2), 2)
    pygame.draw.circle(surf, (255, 213, 0), (cx, cy), r)
    pygame.draw.circle(surf, (255, 233, 78), (cx-r//4, cy-r//4), r//2)
    ey = cy - r//5
    for ox in [-r//3, r//3]:
        pygame.draw.circle(surf, (218, 148, 0), (cx+ox, ey), max(1, int(r*0.18)))
        pygame.draw.circle(surf, BLACK,          (cx+ox, ey), max(1, int(r*0.10)))
    pygame.draw.arc(surf, (198, 128, 0),
                    pygame.Rect(cx-r//3, cy, int(r*0.66), r//3), math.pi, 0, 2)


def draw_lawnmower(surf, x, y, active=False):
    c = (210, 30, 30) if not active else (255, 80, 80)
    pygame.draw.rect(surf, c,             (int(x),   int(y)-12, 36, 20))
    pygame.draw.rect(surf, (158, 18, 18), (int(x)+4, int(y)-18, 28, 9))
    for wx in [int(x)+8, int(x)+28]:
        pygame.draw.circle(surf, (48, 48, 48), (wx, int(y)+8), 8)
        pygame.draw.circle(surf, GRAY,          (wx, int(y)+8), 5)


class Plant:
    DEFS = {
        "sunflower":  {"name": "向日葵",   "cost": 50,  "hp": 300,  "cd": 7.5},
        "peashooter": {"name": "豌豆射手", "cost": 100, "hp": 300,  "cd": 7.5},
        "wallnut":    {"name": "坚果墙",   "cost": 50,  "hp": 4000, "cd": 30.0},
    }

    def __init__(self, ptype, col, row):
        self.type  = ptype
        self.col   = col
        self.row   = row
        self.hp    = self.DEFS[ptype]["hp"]
        self.timer = 0.0
        self.frame = 0
        self.alive = True

    def max_hp(self):
        return self.DEFS[self.type]["hp"]

    def hp_ratio(self):
        return max(0.0, self.hp / self.max_hp())

    def center(self):
        return cell_center(self.col, self.row)

    def draw(self, surf):
        cx, cy = self.center()
        cy -= 8
        if self.type == "sunflower":
            draw_sunflower(surf, cx, cy, self.frame)
        elif self.type == "peashooter":
            draw_peashooter(surf, cx, cy, self.frame)
        elif self.type == "wallnut":
            draw_wallnut(surf, cx, cy, self.hp_ratio())

    def update(self, dt, game):
        self.timer += dt
        self.frame += 1
        if self.type == "sunflower" and self.timer >= 24.0:
            self.timer = 0.0
            cx, cy = self.center()
            game.spawn_sun(cx, cy - 20, sky=False)
        elif self.type == "peashooter" and self.timer >= 1.5:
            self.timer = 0.0
            if any(z.row == self.row and z.alive for z in game.zombies):
                cx, cy = self.center()
                game.projectiles.append(Projectile(cx + 32, cy - 8, self.row))

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False


class Zombie:
    DEFS = {
        "normal": {"hp": 270, "cone_hp": 0,   "speed": 30.0},
        "cone":   {"hp": 270, "cone_hp": 370,  "speed": 28.0},
    }

    def __init__(self, ztype, row, x=None):
        d = self.DEFS[ztype]
        self.type    = ztype
        self.row     = row
        self.x       = float(x if x is not None else SCREEN_W + 60)
        self.y       = float(row_y(row))
        self.hp      = d["hp"]
        self.max_hp  = d["hp"]
        self.cone_hp = d["cone_hp"]
        self.speed   = d["speed"]
        self.alive   = True
        self.eating  = False
        self.eat_t   = 0.0
        self.frame   = 0
        self.slowed  = 0.0

    def hp_ratio(self):
        return max(0.0, self.hp / self.max_hp)

    def cone_ratio(self):
        return max(0.0, self.cone_hp / 370.0)

    def draw(self, surf):
        if self.type == "normal":
            draw_normal_zombie(surf, self.x, self.y, self.hp_ratio(), self.frame)
        else:
            draw_cone_zombie(surf, self.x, self.y, self.hp_ratio(), self.frame,
                             cone_hp=self.cone_ratio())

    def _find_target(self, game):
        best = None
        for p in game.plants:
            if p.row != self.row:
                continue
            px   = p.center()[0]
            dist = self.x - px
            if 0 <= dist <= CW * 0.72:
                if best is None or dist < self.x - best.center()[0]:
                    best = p
        return best

    def update(self, dt, game):
        self.frame  += 1
        self.slowed  = max(0.0, self.slowed - dt)
        target = self._find_target(game)
        if target:
            self.eating = True
            self.eat_t += dt
            if self.eat_t >= 1.0:
                self.eat_t = 0.0
                target.take_damage(100)
                if not target.alive:
                    game.remove_plant(target)
            return
        self.eating = False
        spd    = self.speed * (0.5 if self.slowed > 0 else 1.0)
        self.x -= spd * dt
        if self.x < GX - 20:
            for lm in game.lawnmowers:
                if lm.row == self.row and not lm.active and lm.alive:
                    lm.activate()
                    self.alive = False
                    return
        if self.x < 30:
            game.state = S_LOSE

    def take_damage(self, dmg, frozen=False):
        if self.cone_hp > 0:
            self.cone_hp -= dmg
            if self.cone_hp <= 0:
                self.cone_hp = 0
        else:
            self.hp -= dmg
        if frozen:
            self.slowed = 3.0
        if self.hp <= 0:
            self.alive = False


class Projectile:
    SPEED = 360.0

    def __init__(self, x, y, row, frozen=False):
        self.x      = float(x)
        self.y      = float(y)
        self.row    = row
        self.frozen = frozen
        self.alive  = True

    def draw(self, surf):
        draw_pea(surf, self.x, self.y, self.frozen)

    def update(self, dt, game):
        self.x += self.SPEED * dt
        if self.x > SCREEN_W + 20:
            self.alive = False
            return
        for z in game.zombies:
            if not z.alive:
                continue
            if abs(z.y - self.y) > 40:
                continue
            if abs(z.x - self.x) < 24:
                z.take_damage(20, self.frozen)
                self.alive = False
                return


class Sun:
    def __init__(self, x, y, target_y, sky=True):
        self.x        = float(x)
        self.y        = float(y)
        self.target_y = float(target_y)
        self.alive    = True
        self.value    = 25
        self.frame    = 0
        self.lifetime = 10.0
        self.speed    = 80.0 if sky else 60.0

    def draw(self, surf):
        draw_sun(surf, self.x, self.y, self.frame)

    def update(self, dt):
        self.frame    += 1
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        if self.y < self.target_y:
            self.y += self.speed * dt

    def hit(self, mx, my):
        return math.hypot(mx - self.x, my - self.y) < 24


class Lawnmower:
    SPEED = 600.0

    def __init__(self, row):
        self.row    = row
        self.x      = float(LM_X)
        self.y      = float(row_y(row))
        self.active = False
        self.alive  = True

    def activate(self):
        self.active = True

    def draw(self, surf):
        if self.alive:
            draw_lawnmower(surf, self.x, self.y, self.active)

    def update(self, dt, game):
        if self.active:
            self.x += self.SPEED * dt
            for z in game.zombies:
                if z.alive and z.row == self.row and abs(z.x - self.x) < 42:
                    z.alive = False
            if self.x > SCREEN_W + 60:
                self.alive = False


class CardSlot:
    W, H = 62, 90

    def __init__(self, ptype, index):
        self.type     = ptype
        self.index    = index
        d             = Plant.DEFS[ptype]
        self.cost     = d["cost"]
        self.name     = d["name"]
        self.cd_max   = d["cd"]
        self.cd       = self.cd_max
        self.selected = False

    def rect(self):
        x = 10 + self.index * (self.W + 4)
        return pygame.Rect(x, 5, self.W, self.H)

    def ready(self, sun):
        return self.cd >= self.cd_max and sun >= self.cost

    def draw(self, surf, sun, frame):
        r = self.rect()
        if self.selected:
            bg, border = (250, 228, 98), (200, 180, 0)
        elif self.ready(sun):
            bg, border = (218, 208, 158), (98, 78, 38)
        else:
            bg, border = (158, 148, 108), (78, 58, 28)
        pygame.draw.rect(surf, bg,     r, border_radius=4)
        pygame.draw.rect(surf, border, r, 2, border_radius=4)
        pcx, pcy = r.centerx, r.top + 36
        if self.type == "sunflower":
            draw_sunflower(surf, pcx, pcy, frame, 0.58)
        elif self.type == "peashooter":
            draw_peashooter(surf, pcx, pcy, frame, 0.58)
        elif self.type == "wallnut":
            draw_wallnut(surf, pcx, pcy, 1.0, 0.55)
        draw_text(surf, self.name, "sm", (50, 28, 8),
                  r.centerx, r.bottom-29, center=True, shadow=False)
        draw_text(surf, str(self.cost), "sm", (198, 148, 0),
                  r.centerx, r.bottom-13, center=True, shadow=False)
        if self.cd < self.cd_max:
            ratio  = 1.0 - self.cd / self.cd_max
            cool_h = max(1, int(r.height * ratio))
            ov = pygame.Surface((r.width, cool_h), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 148))
            surf.blit(ov, (r.x, r.y))

    def update(self, dt, used=False):
        if used:
            self.cd = 0.0
        else:
            self.cd = min(self.cd_max, self.cd + dt)


class Game:
    WAVES = [
        ( 8.0, [("normal", 2)]),
        (18.0, [("normal", 0), ("normal", 4)]),
        (30.0, [("normal", 1), ("normal", 3)]),
        (44.0, [("normal", 0), ("normal", 2), ("normal", 4)]),
        (58.0, [("cone",   1), ("normal", 0), ("normal", 2),
                ("normal", 3), ("normal", 4)]),
    ]
    SUN_INTERVAL = 9.5

    def __init__(self):
        self.state    = S_INTRO
        self.intro_t  = 0.0
        self.lintro_t = 0.0
        self.menu_sel = 0
        self.frame    = 0
        self._game_init()

    def _game_init(self):
        self.plants      = []
        self.zombies     = []
        self.projectiles = []
        self.suns        = []
        self.lawnmowers  = [Lawnmower(r) for r in range(ROWS)]
        self.grid        = {}
        self.sun_count   = 50
        self.selected    = None
        self.shovel_mode = False
        self.cards       = [
            CardSlot("sunflower",  0),
            CardSlot("peashooter", 1),
            CardSlot("wallnut",    2),
        ]
        self.wave_idx       = 0
        self.wave_timer     = 0.0
        self.sun_timer      = 0.0
        self.all_waves_done = False
        self.win_timer      = 0.0
        self.result_t       = 0.0

    def handle_event(self, event):
        if self.state == S_INTRO:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.state = S_MENU

        elif self.state == S_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.menu_sel = (self.menu_sel - 1) % 2
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_sel = (self.menu_sel + 1) % 2
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._menu_confirm()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._menu_click(event.pos)

        elif self.state == S_LINTRO:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if self.lintro_t > 0.8:
                    self._start_game()

        elif self.state == S_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._game_click(event.pos, event.button)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.selected    = None
                    self.shovel_mode = False
                    for c in self.cards:
                        c.selected = False
                elif event.key == pygame.K_s:
                    self.shovel_mode = not self.shovel_mode
                    self.selected    = None
                    for c in self.cards:
                        c.selected = False

        elif self.state in (S_WIN, S_LOSE):
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if self.result_t > 1.0:
                    self.state    = S_MENU
                    self._game_init()

    def _menu_confirm(self):
        if self.menu_sel == 0:
            self.state    = S_LINTRO
            self.lintro_t = 0.0
        else:
            pygame.quit()
            sys.exit()

    def _menu_click(self, pos):
        mx, my = pos
        for i, (bx, by, bw, bh) in enumerate(self._menu_btns()):
            if bx <= mx <= bx+bw and by <= my <= by+bh:
                self.menu_sel = i
                self._menu_confirm()

    def _menu_btns(self):
        bw, bh = 220, 60
        cx = SCREEN_W // 2
        return [(cx-bw//2, 270, bw, bh), (cx-bw//2, 350, bw, bh)]

    def _start_game(self):
        self._game_init()
        self.state = S_GAME

    def _shovel_btn(self):
        sx = 10 + 3 * (CardSlot.W + 4)
        return pygame.Rect(sx, 5, 50, CardSlot.H)

    def _game_click(self, pos, button):
        mx, my = pos
        if button == 3:
            self.selected    = None
            self.shovel_mode = False
            for c in self.cards:
                c.selected = False
            return
        for card in self.cards:
            if card.rect().collidepoint(mx, my):
                if card.ready(self.sun_count):
                    if self.selected == card.type:
                        self.selected  = None
                        card.selected  = False
                    else:
                        self.selected    = card.type
                        self.shovel_mode = False
                        for c in self.cards:
                            c.selected = (c.type == card.type)
                return
        if self._shovel_btn().collidepoint(mx, my):
            self.shovel_mode = not self.shovel_mode
            self.selected    = None
            for c in self.cards:
                c.selected = False
            return
        for sun in self.suns:
            if sun.alive and sun.hit(mx, my):
                sun.alive      = False
                self.sun_count += sun.value
                return
        cell = xy_to_cell(mx, my)
        if cell:
            col, row = cell
            if self.shovel_mode:
                if (col, row) in self.grid:
                    self.remove_plant(self.grid[(col, row)])
            elif self.selected:
                card = next((c for c in self.cards if c.type == self.selected), None)
                if card and card.ready(self.sun_count) and (col, row) not in self.grid:
                    p = Plant(self.selected, col, row)
                    self.plants.append(p)
                    self.grid[(col, row)] = p
                    self.sun_count -= card.cost
                    card.update(0, used=True)
                    self.selected = None
                    for c in self.cards:
                        c.selected = False

    def update(self, dt):
        self.frame += 1
        if self.state == S_INTRO:
            self.intro_t += dt
        elif self.state == S_LINTRO:
            self.lintro_t += dt
            if self.lintro_t >= 3.5:
                self._start_game()
        elif self.state == S_GAME:
            self._update_game(dt)
        elif self.state in (S_WIN, S_LOSE):
            self.result_t += dt

    def _update_game(self, dt):
        for card in self.cards:
            card.update(dt)
        self.sun_timer += dt
        if self.sun_timer >= self.SUN_INTERVAL:
            self.sun_timer = 0.0
            x  = random.randint(GX + 20, GX + COLS*CW - 20)
            ty = random.randint(GY + 20, GY + ROWS*CH - 40)
            self.suns.append(Sun(x, -25, target_y=ty, sky=True))
        if self.wave_idx < len(self.WAVES):
            self.wave_timer += dt
            wt, wzombies = self.WAVES[self.wave_idx]
            if self.wave_timer >= wt:
                for ztype, row in wzombies:
                    ox = random.randint(0, 60)
                    self.zombies.append(Zombie(ztype, row, SCREEN_W + 50 + ox))
                self.wave_idx += 1
                if self.wave_idx >= len(self.WAVES):
                    self.all_waves_done = True
        if self.all_waves_done and not any(z.alive for z in self.zombies):
            self.win_timer += dt
            if self.win_timer >= 0.5:
                self.state    = S_WIN
                self.result_t = 0.0
        for p in self.plants[:]:
            p.update(dt, self)
        for z in self.zombies[:]:
            z.update(dt, self)
        for proj in self.projectiles[:]:
            proj.update(dt, self)
        for sun in self.suns[:]:
            sun.update(dt)
        for lm in self.lawnmowers[:]:
            lm.update(dt, self)
        self.zombies     = [z for z in self.zombies     if z.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.suns        = [s for s in self.suns        if s.alive]
        self.lawnmowers  = [l for l in self.lawnmowers  if l.alive]

    def remove_plant(self, plant):
        self.grid.pop((plant.col, plant.row), None)
        if plant in self.plants:
            self.plants.remove(plant)

    def spawn_sun(self, x, y, sky=True):
        ty = y + random.randint(50, 110) if sky else y + 35
        self.suns.append(Sun(x, y if sky else y - 20, target_y=ty, sky=sky))

    def draw(self, surf):
        if self.state == S_INTRO:
            self._draw_intro(surf)
        elif self.state == S_MENU:
            self._draw_menu(surf)
        elif self.state == S_LINTRO:
            self._draw_level_intro(surf)
        elif self.state in (S_GAME, S_WIN, S_LOSE):
            self._draw_game(surf)
            if self.state == S_WIN:
                self._draw_win(surf)
            elif self.state == S_LOSE:
                self._draw_lose(surf)

    def _draw_intro(self, surf):
        t = self.intro_t
        surf.blit(get_night_bg(), (0, 0))
        pygame.draw.circle(surf, (255, 250, 218), (720, 80), 55)
        pygame.draw.circle(surf, (8, 5, 18),      (742, 65), 48)
        for sx, sy in [(100,40),(200,75),(350,28),(500,55),(648,42),(800,88),(150,118),(420,98)]:
            pygame.draw.circle(surf, WHITE, (sx, sy), 2)
        if t > 0.2:
            for fx, fy_base in [(60,430),(150,415),(390,425),(695,418),(810,428)]:
                rise = min(20.0, (t-0.2)*40) - 20
                draw_sunflower(surf, fx, int(fy_base+rise), self.frame, 0.68)
            for px2, py_base in [(240,420),(540,425),(756,420)]:
                rise = min(15.0, (t-0.2)*35) - 15
                draw_peashooter(surf, px2, int(py_base+rise), self.frame, 0.68)
        if t > 0.4:
            hand_rise = min(90.0, (t-0.4)*110)
            for hx in [268, 590]:
                hy = int(415 - hand_rise)
                pygame.draw.rect(surf, (118, 138, 108), (hx, hy, 28, 80))
                for i in range(4):
                    pygame.draw.rect(surf, (118, 138, 108), (hx+i*7, hy-18, 6, 22))
        if t > 0.6:
            alpha = min(255, int((t-0.6)*220))
            glow  = fonts["title"].render("植物大战僵尸", True, (0, 88, 0))
            base  = glow.get_rect(center=(SCREEN_W//2, 195))
            for ddx, ddy in [(-3,0),(3,0),(0,-3),(0,3)]:
                glow.set_alpha(alpha//2)
                surf.blit(glow, (base.x+ddx, base.y+ddy))
            title = fonts["title"].render("植物大战僵尸", True, (72, 218, 72))
            title.set_alpha(alpha)
            surf.blit(title, base)
            sub = fonts["md"].render("PLANTS vs. ZOMBIES", True, (178, 255, 118))
            sub.set_alpha(alpha)
            surf.blit(sub, sub.get_rect(center=(SCREEN_W//2, 272)))
        if t > 1.8 and int(t*2.5) % 2 == 0:
            draw_text(surf, "按任意键继续", "md", (198, 198, 198),
                      SCREEN_W//2, 508, center=True, shadow=True)

    def _draw_menu(self, surf):
        surf.blit(get_day_bg(), (0, 0))
        tb = pygame.Rect(SCREEN_W//2-258, 55, 516, 115)
        ov = pygame.Surface((tb.w, tb.h), pygame.SRCALPHA)
        ov.fill((0, 32, 0, 195))
        surf.blit(ov, tb.topleft)
        pygame.draw.rect(surf, (0, 148, 0), tb, 3, border_radius=10)
        draw_text(surf, "植物大战僵尸", "title", (78, 252, 78),
                  SCREEN_W//2, 112, center=True, shadow=True)
        draw_sunflower(surf, 78, 355, self.frame, 0.88)
        draw_peashooter(surf, 820, 355, self.frame, 0.88)
        draw_wallnut(surf, 75, 460, 1.0, 0.78)
        for i, label in enumerate(["开始冒险", "退出游戏"]):
            bx, by, bw, bh = self._menu_btns()[i]
            sel    = (i == self.menu_sel)
            bg     = (58, 158, 58)   if sel else (38, 98, 38)
            border = (118, 252, 118) if sel else (78, 178, 78)
            pygame.draw.rect(surf, bg,     (bx, by, bw, bh), border_radius=8)
            pygame.draw.rect(surf, border, (bx, by, bw, bh), 3, border_radius=8)
            fc = (255, 255, 98) if sel else (198, 228, 178)
            draw_text(surf, label, "lg", fc, bx+bw//2, by+bh//2, center=True, shadow=True)
        draw_text(surf, "方向键选择  回车/点击确认", "sm",
                  (178, 218, 178), SCREEN_W//2, 478, center=True, shadow=True)

    def _draw_level_intro(self, surf):
        t = self.lintro_t
        surf.blit(get_day_bg(), (0, 0))
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 168))
        surf.blit(ov, (0, 0))
        alpha = min(255, int(t*380))
        level = fonts["xl"].render("第 1-1 关", True, (255, 228, 78))
        level.set_alpha(alpha)
        surf.blit(level, level.get_rect(center=(SCREEN_W//2, 178)))
        desc = fonts["md"].render("白日 · 冒险开始！", True, (198, 255, 178))
        desc.set_alpha(alpha)
        surf.blit(desc, desc.get_rect(center=(SCREEN_W//2, 238)))
        if t > 0.4:
            seeds = [("sunflower","向日葵"), ("peashooter","豌豆射手"), ("wallnut","坚果墙")]
            for i, (ptype, name) in enumerate(seeds):
                sx = SCREEN_W//2 - (len(seeds)-1)*50 + i*100
                sy = 318
                pygame.draw.rect(surf, (38, 78, 38),  (sx-30, sy-10, 60, 80), border_radius=6)
                pygame.draw.rect(surf, (98, 178, 98),  (sx-30, sy-10, 60, 80), 2, border_radius=6)
                if ptype == "sunflower":
                    draw_sunflower(surf, sx, sy+18, self.frame, 0.5)
                elif ptype == "peashooter":
                    draw_peashooter(surf, sx, sy+18, self.frame, 0.5)
                else:
                    draw_wallnut(surf, sx, sy+18, 1.0, 0.5)
                draw_text(surf, name, "sm", (198, 255, 178), sx, sy+54, center=True, shadow=False)
        if t > 1.2 and int(t*2.2) % 2 == 0:
            draw_text(surf, "点击任意处开始！", "md", WHITE,
                      SCREEN_W//2, 470, center=True, shadow=True)

    def _draw_game(self, surf):
        surf.blit(get_day_bg(), (0, 0))
        mx, my = pygame.mouse.get_pos()
        if self.selected or self.shovel_mode:
            cell = xy_to_cell(mx, my)
            if cell:
                r  = cell_rect(*cell)
                hl = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                hl.fill((255, 80, 80, 88) if self.shovel_mode else (255, 255, 98, 88))
                surf.blit(hl, r.topleft)
        for p in self.plants:
            p.draw(surf)
        for lm in self.lawnmowers:
            lm.draw(surf)
        for z in sorted(self.zombies, key=lambda z: z.y):
            z.draw(surf)
        for proj in self.projectiles:
            proj.draw(surf)
        for sun in self.suns:
            sun.draw(surf)
        # UI 栏
        pygame.draw.rect(surf, UI_BG,   (0, 0, SCREEN_W, 100))
        pygame.draw.rect(surf, UI_LINE,  (0, 98, SCREEN_W, 3))
        for card in self.cards:
            card.draw(surf, self.sun_count, self.frame)
        # 铲子
        sb = self._shovel_btn()
        sc = (148, 92, 38) if not self.shovel_mode else (218, 142, 68)
        pygame.draw.rect(surf, sc,                                              sb, border_radius=4)
        pygame.draw.rect(surf, (218,148,68) if self.shovel_mode else (168,118,58), sb, 2, border_radius=4)
        draw_text(surf, "铲", "lg", (238,208,98) if self.shovel_mode else (198,168,88),
                  sb.centerx, sb.centery-8, center=True, shadow=True)
        draw_text(surf, "铲子", "sm", (200,160,80), sb.centerx, sb.bottom-16, center=True, shadow=False)
        # 阳光
        sx2 = SCREEN_W - 155
        pygame.draw.rect(surf, (38, 28, 8),   (sx2-5, 8, 148, 44), border_radius=6)
        pygame.draw.rect(surf, (198, 148, 0),  (sx2-5, 8, 148, 44), 2, border_radius=6)
        draw_sun(surf, sx2+12, 30, self.frame, 0.78)
        draw_text(surf, str(self.sun_count), "lg", (255, 228, 0), sx2+28, 20, shadow=True)
        self._draw_progress(surf)
        if self.selected:
            s = 0.68
            if   self.selected == "sunflower":  draw_sunflower(surf, mx, my, self.frame, s)
            elif self.selected == "peashooter": draw_peashooter(surf, mx, my, self.frame, s)
            elif self.selected == "wallnut":    draw_wallnut(surf, mx, my, 1.0, s)

    def _draw_progress(self, surf):
        px = SCREEN_W - 25
        py = GY
        ph = ROWS * CH
        pygame.draw.rect(surf, (18, 18, 18), (px-2, py, 22, ph))
        total = len(self.WAVES)
        for i in range(total):
            fy    = py + int((i+1) / total * ph)
            color = (255, 48, 48) if i < self.wave_idx else (198, 198, 198)
            pygame.draw.polygon(surf, color, [(px+2, fy), (px+18, fy-8), (px+18, fy+8)])
        label = "全出" if self.all_waves_done else f"{self.wave_idx}/{total}"
        draw_text(surf, label, "sm", (218, 218, 218), SCREEN_W-14, GY-18, center=True, shadow=True)

    def _draw_win(self, surf):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 155))
        surf.blit(ov, (0, 0))
        draw_text(surf, "胜 利！", "title", (255, 228, 0),
                  SCREEN_W//2, 185, center=True, shadow=True)
        draw_text(surf, "第 1-1 关完成", "xl", (178, 255, 118),
                  SCREEN_W//2, 278, center=True, shadow=True)
        draw_text(surf, "你成功保卫了自己的花园！", "lg", WHITE,
                  SCREEN_W//2, 355, center=True, shadow=True)
        for i in range(6):
            a  = self.frame * 0.02 + i * math.pi / 3
            sx3 = SCREEN_W//2 + int(math.cos(a)*220)
            sy3 = 430 + int(math.sin(a)*30)
            draw_sun(surf, sx3, sy3, self.frame+i*10, 0.75)
        if self.result_t > 1.0 and int(self.result_t*2) % 2 == 0:
            draw_text(surf, "按任意键返回主菜单", "md", (198, 198, 198),
                      SCREEN_W//2, 485, center=True, shadow=True)

    def _draw_lose(self, surf):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((28, 0, 0, 188))
        surf.blit(ov, (0, 0))
        draw_text(surf, "游戏结束", "title", (218, 58, 58),
                  SCREEN_W//2, 185, center=True, shadow=True)
        draw_text(surf, "僵尸吃掉了你的脑子！", "xl", (255, 118, 78),
                  SCREEN_W//2, 278, center=True, shadow=True)
        draw_text(surf, "不要灰心，再试一次吧！", "lg", WHITE,
                  SCREEN_W//2, 355, center=True, shadow=True)
        if self.result_t > 1.0 and int(self.result_t*2) % 2 == 0:
            draw_text(surf, "按任意键返回主菜单", "md", (198, 178, 178),
                      SCREEN_W//2, 485, center=True, shadow=True)


def main():
    game = Game()
    while True:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
