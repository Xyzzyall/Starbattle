"""Модуль для работы с физикой, векторами и координатами
"""
from math import *


class Vector2:
    """Класс для двумерных векторов
    Создан для собственных нужд"""
    def __init__(self, c: tuple):
        self.x, self.y = c

    def __add__(self, other):
        return Vector2((self.x + other.x, self.y + other.y))

    def __mul__(self, other):
        return Vector2((self.x * other, self.y * other))

    def __sub__(self, other):
        return Vector2((self.x - other.x, self.y - other.y))

    def length(self):
        """Длина вектора"""
        return sqrt(self.x**2 + self.y**2)
    
    @staticmethod    
    def from_polar(phi, r):
        """получить вектор из полярных координат"""
        return Vector2( (r*cos(phi), r*sin(phi)) )


class PhysDot:
    """Двумерная физика гравитации материальных точек.
    Точки не обязательно где-то хранить. Сам класс записывает их в статические поля и обрабатывает при вызове функций.
    Некоторые общие слова про параметры:
    *) pos -- кортеж с двумя вещественными, отвечает за координаты
      - в алгоритмах используется собственная система координат, не вмешивайтесь! :)
    Про статические поля:
    *) DIST_MULT -- множитель расстояния для рассчета взаимодействий
    *) simulate_dynamic_rel -- симулировать ли притяжение движущихся частиц друг к другу?
      - спорная и тяжелая штука, но будет весело!
    *) delta_time -- сколько секунд брать за один такт симуляции
      - чем больше, тем симуляция будет менее точной на меньших расстояниях. Иными словами, отвечает за дискретизацию процесса"""
    __G__ = 6.6740831313131*(10**-11)  # гравитационная постоянная
    __static_dots__ = []
    __dyn_dots__ = []
    #__col_pairs__ = []
    DIST_MULT = 1.0
    simulate_dynamic_rel = False  # симулировать притяжение динамических частиц друг к другу?
    delta_time = .1  # число секунд за 1 такт симуляции

    def __init__(self, pos: tuple, mass, typ, speed=(0, 0), g_force_mult = 1.0):
        """typ -- тип материальной точки.
          - 0: неподвижный источник гравитации
          - 1: подвижные частицы
        mass -- масса материальной точки"""
        self.mass = mass
        self.pos = Vector2(pos)
        self.typ = typ
        self.g_force_mult = g_force_mult
        if typ:
            self.speed = Vector2(speed)
            PhysDot.__dyn_dots__.append(self)
        else:
            PhysDot.__static_dots__.append(self)

    def delete(self):
        """удаляет объект из симуляции"""
        if self.typ:
            PhysDot.__dyn_dots__.remove(self)
        else:
            PhysDot.__static_dots__.remove(self)

    def is_collided(self, dot, dist):
        """если точка сблизится на расстояние столкновения"""
        return (self.pos - dot.pos).length() < dist

    def __calc_accelerate__(self, dot):
        """высчитать ускорение от гравитационных сил"""
        vec = dot.pos + self.pos*-1  # мне захотелось сделать физику более аркадной, сорян
        return vec * (self.g_force_mult * PhysDot.__G__ *
                      dot.mass * (PhysDot.DIST_MULT * vec.length())**-3) #должно быть в -3 

    def accelerate(self, vec):
        """прибавить к вектору скорости векторы vec"""
        for v in vec:
            self.speed = self.speed + v * PhysDot.delta_time

    def dist_to(self, dot):
        """расстояние до другой материальной точки"""
        return (self.pos - dot.pos).length()

    def force(self, f: tuple):
        """приложить силу f к объекту"""
        a = Vector2((f[0]/self.mass,f[1]/self.mass))
        self.accelerate([a])

    @staticmethod
    def simulate(times=1):
        """Симулирует мир times раз и выходит из метода"""
        for i in range(times):
            for dot in PhysDot.__dyn_dots__:
                dot.accelerate([dot.__calc_accelerate__(sd) for sd in PhysDot.__static_dots__])
                if PhysDot.simulate_dynamic_rel:
                    dot.accelerate([dot.__calc_accelerate__(sd) for sd in PhysDot.__dyn_dots__])

                dot.pos = dot.speed + dot.pos
