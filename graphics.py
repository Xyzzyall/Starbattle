import pygame as pg
from pygame.locals import *
import random as rnd
import math

# видео
S_W, S_H = 700, 700
SCREEN_RECT = Rect(0, 0, S_W, S_H)
FPS = 60
# упрощающие жизнь константы
NULLCOLOUR = (0, 0, 0, 0)
# цветовые схемы
FIRST_PLAYER_MESH_COLOURS = (160, 75, 42), (97, 14, 14), (97, 14, 14), (95, 80, 73), (162, 91, 91), (99, 103, 128)
SECOND_PLAYER_MESH_COLOURS = (60, 65, 130), (44, 17, 160), (44, 17, 160), (107, 112, 179), (155, 144, 205), (99, 103, 128)
PLAYER_LASER_DAMAGE_COLOURS = (255, 255, 255), (200, 200, 200), (200, 200, 200), (255, 255, 255), (255, 255, 255), (200, 200, 200)
ROCKET_MESH_COLORS = (121, 17, 17), (160, 48, 48), (172, 0, 0)
# меши
ROCKET_MESH = (
(0, 1), (-.4, .6), (-.4, -.2), (-.2, -.6), (.2, -.6), (.4, -.2), (.4, .6)
),(
(0, 1), (-.2, .4), (-.2, -.2), (0, -.6), (.2, -.2), (.2, .4)
),(
(-.2, -.4), (-.4, -.8), (.4,-.8), (.2, -.4)
)
PLAYER_MESH =(
(.2, .4), (-.2, .4), (-.4, .2), (-.4, -.2), (-.2, -.4), (.2, -.4), (.4, -.2), (.4, .2), (.2,.4)
),(
(-.4, .2), (-.6, .4), (-.8, .2), (-.8, -.2), (-.6, -.4), (-.4, -.2)
),(
(.4, .2), (.6, .4), (.8, .2), (.8, -.2), (.6, -.4), (.4, -.2)
),(
(0, 1), (-.1, .9), (-.2, .7), (-.2, 0), (-.1, -.1), (.1, -.1), (.2, 0), (.2, .7), (.1, .9)
),(
(0, .1), (-.4, -.6), (.4, -.6)
),(
(0, .9), (-.1, .8), (-.1, .7), (.1, .7), (.1, .8)
)
#

def init_pygame():
    """инициализация графического окна"""
    # Initialize pygame
    pg.init()

    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREEN_RECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREEN_RECT.size, winstyle, bestdepth)
    draw_background()
    return screen


def draw_background():
    """Нарисовать бэкграунд. В подпрограмме заложены константы, отвечающие за его параметры.
    Рисуется слоями:
    1) тумманости
    2) звезды
    3) черная дыра"""
    back_surface = pg.Surface(SCREEN_RECT.size)
    # ----
    NEBULA_COUNT = 2000
    NEBULA_DEF_COLOR = pg.Color(31, 41, 50, 0)
    STARS_COUNT = 100
    STARS_COLOURS = (255, 255, 255), (255, 200, 200), (200, 255, 200), (200, 200, 255), (200, 100, 100)
    BLACK_HOLE_RADIUS = 80
    # ----
    # NEBULA
    for i in range( NEBULA_COUNT ):
        c = NEBULA_DEF_COLOR.correct_gamma(rnd.random()/4+1)
        pg.draw.circle(back_surface, c, ( rnd.randint(0, S_W), rnd.randint(0, S_H) ), rnd.randint(1, 100))

    back_surface = pg.transform.smoothscale(back_surface, (S_W//3, S_H//3))
    back_surface = pg.transform.smoothscale(back_surface, (S_W, S_H))
    # STARS
    for i in range(STARS_COUNT):
        pg.draw.circle(back_surface, rnd.choice(STARS_COLOURS), (rnd.randint(0, S_W), rnd.randint(0, S_H)), rnd.randint(1, 5))

    back_surface = pg.transform.smoothscale(back_surface, (int(S_W / 1.21), int(S_H / 1.21)))
    back_surface = pg.transform.smoothscale(back_surface, (S_W, S_H))
    # BLACK HOLE
    buf = pg.Surface((BLACK_HOLE_RADIUS<<1, BLACK_HOLE_RADIUS<<1))
    buf = buf.convert_alpha()
    buf.fill(NULLCOLOUR)

    def black_hole_colour(i):
        return 0, 0, 0, int(200 - 200/BLACK_HOLE_RADIUS*i)

    for i in range(2, BLACK_HOLE_RADIUS)[::-1]:
        pg.draw.circle(buf, black_hole_colour(i),(BLACK_HOLE_RADIUS, BLACK_HOLE_RADIUS), i)

    back_surface.blit(buf, ((S_W >> 1) - BLACK_HOLE_RADIUS, (S_H >> 1) - BLACK_HOLE_RADIUS))
    buf = pg.transform.smoothscale(buf, (BLACK_HOLE_RADIUS, BLACK_HOLE_RADIUS))
    back_surface.blit(buf, ((S_W  - BLACK_HOLE_RADIUS) >> 1, (S_H - BLACK_HOLE_RADIUS) >> 1))
    pg.draw.circle(back_surface, (0,0,0), (S_W >> 1, S_H >> 1), BLACK_HOLE_RADIUS//3)

    return back_surface

    
def __to_polar__(dot):
    """перевод в полярные координаты"""
    r = (dot[0]**2 + dot[1]**2)**.5
    if r == 0:
        return 0, 0
    else:
        return r, math.atan2(dot[1], dot[0])


def convert_to_mesh(palette, dots):
    """Переводит точки в формат меша.
    выходной формат: палитра цветов, затем многоугольники с номером цвета в палитре"""
    def to_polar(polygon, colour):
        g = [__to_polar__(dot) for dot in polygon]
        return [g] + [colour]

    res = []
    for polygon in enumerate(dots):
        res.append(to_polar(polygon[1], polygon[0]))
    return tuple(palette), tuple(res)

FIRST_PlAYER_MESH = convert_to_mesh(FIRST_PLAYER_MESH_COLOURS, PLAYER_MESH)
SECOND_PlAYER_MESH = convert_to_mesh(SECOND_PLAYER_MESH_COLOURS, PLAYER_MESH)
ROCKET_MESH = convert_to_mesh(ROCKET_MESH_COLORS, ROCKET_MESH)


class Mesh:
    @staticmethod
    def __to_dekart_int__( dots, scale:tuple=(1, 1), delta_angle=0.0):
        """перевести координаты в декартовы и округлить"""
        res = []
        for d in dots:
            phi = d[1] + delta_angle
            res.append((d[0] * math.cos(phi) * scale[0] / 2 + scale[0] / 2,
                        d[0] * math.sin(phi) * scale[1] / 2 + scale[1] / 2))
        return res
        
    def __init__(self, mesh, tex_rect, sec_colour_scheme=None):
        self.__polygons__ = mesh
        self.rect = tex_rect
        self.sec_colour_scheme = sec_colour_scheme
        self.colour_scheme = 0 # default colours
        self.__angle__ = 0.0
        self.surface = pg.Surface(tex_rect.size).convert_alpha()
        self.surface.fill(NULLCOLOUR)
    
    def __redraw__(self):
        """перерисовать меш с учетом угла смещения"""
        self.surface.fill(NULLCOLOUR)            
        for polygon in self.__polygons__[1]:
            if self.colour_scheme:
                dec_dots = Mesh.__to_dekart_int__(polygon[0], scale=self.rect.size, delta_angle=self.__angle__)
                pg.draw.polygon(self.surface, self.sec_colour_scheme[self.colour_scheme-1][polygon[1]], dec_dots)
            else:
                dec_dots = Mesh.__to_dekart_int__(polygon[0], scale=self.rect.size, delta_angle=self.__angle__)
                pg.draw.polygon(self.surface, self.__polygons__[0][polygon[1]], dec_dots)
    
    def turn(self, angle):
        """повернуть меш и перерисовать его"""
        self.__angle__ += angle
        self.__redraw__()
    
    def rotation(self, angle):
        """изменить ротацию меша и перерисовать его"""
        self.__angle__ = angle
        self.__redraw__()
