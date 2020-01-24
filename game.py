import phys
from graphics import *

# управление
FIRST_PLAYER_CONTROL  = (K_w, K_a, K_s, K_d, K_q, K_e)
SECOND_PLAYER_CONTROL = (K_i, K_j, K_k, K_l, K_u, K_o)
# игровые константы
ACTOR_BORDER_CORD = 1  # отвечает за крайнюю по модулю координату нахождения актеров на поле
PLAYER_SPEED = .0001
PLAYER_TURN_SPEED = phys.pi/120
PLAYER_LIFE = 1000
PLAYER_ROCKET_SUSPEND = 60 # кадров до перезарядки
PLAYER_LASER_SUSPEND = 8
PLAYER_COLLIDE_DIST = .06
PLAYER_LASER_COLLIDE_DIST = .04
ROCKET_SPEED = .019
ROCKET_LIFETIME = 600  # сколько кадров торпеда будет жить
ROCKET_SLEEP_TIME = 10  # сколько кадров торпеда не детонируется от столкновения
ROCKET_DAMAGE = 400
ROCKET_DAMAGE_RANGE = .35
LASER_DAMAGE = 20
LASER_SAFE_DIST = .05
# веселые параметры
PLAYER_DEAD_ROCKETS = 10
# физические параметры
phys.PhysDot.DIST_MULT = 0.9  # множитель дистанции для гравитационного взаимодействия
CENTER_MASS = 10000
CENTER_COLLIDE_DIST = .1
PLAYER_MASS = 1
ROCKET_MASS = .01
ROCKET_GRAV_MULT = 10.0  # усиление гравитационного воздействия на ракеты для увеличения интересности
# графические параметры 
PLAYER_TEX_SIDE = 45  # текстура -- квадрат. константа -- сторона квадрата
PLAYER_EXPLOSION_COLOUR = pg.Color(255, 0, 0, 100)
ROCKET_TEX_SIDE = 20
ROCKET_EXPLOSION_DIAP = 32, 40
ROCKET_EXPLOSION_LIFE_DIAP = 30, 60
ROCKET_EXPLOSION_COLOUR = (255, 0, 0, 255)
ROCKET_EXPLOSION_SECCOLOUR = (100, 0, 0, 255)
LASER_LENGTH = 3
LASER_DAMAGE_EFFECT_TIME = 5

# контейнер для всех игровых объектов
ACTORS = []
BLACK_HOLE = phys.PhysDot((0, 0), CENTER_MASS, 0)


def from_relcord_to_disp_cord(dot): # это должны быть векторы2
    """переводит относительные декартовы координаты в координаты дисплея"""
    return int(S_W*(dot.x + 1)), \
           int(S_H*(dot.y + 1))


def __to_dekart_int__( dots, scale:int=1, delta_angle=0.0):
    """служебная функция для преобразования координат в координаты дисплея"""
    res = []
    for d in dots:
        phi = d[0] + delta_angle
        res.append((int(d[1] * phys.cos(phi) * scale) + scale >> 1,
                    int(d[1] * phys.sin(phi) * scale) + scale >> 1))
    return res


class Actor:
    """класс актера. поля -- обязательные методы любого игрового объекта"""
    def __init__(self):
        return
    
    def update_events(self, e):
        """принимает событие и обрабатывает его каждый такт"""
        return
        
    def update(self):
        """что происходит с объектом каждый такт"""
        return
        
    def update_after_flip(self):
        """что происходит с объектом после отображения картинки"""
        return
        
    def destroy(self):
        """уничтожить объект"""
        ACTORS.remove(self)


class LifeStatusBar(Actor):
    """Индикатор здоровья. Возможно прикрепить к любому разрушаемому предмету."""
    surface = pg.Surface(SCREEN_RECT.size)
    def __init__(self, rect, colour, seccolour, max_life,):
        self.pos = rect.topleft
        rect.topleft = (0, 0)
        self.rect = rect
        self.__surf__ = pg.Surface(rect.size)
        self.colour = colour
        self.seccolour = seccolour
        self.max_life = max_life
        Actor.__init__(self)
        self.__style_dots__ = (-10, rect.midleft[1]),(10, -10), (-20, -10), (-20, rect.bottomleft[1] + 10), (10, rect.bottomleft[1]+10)
        self.update_indicator(max_life)

    def update_indicator(self, life):
        """перерисовывает индикатор здоровья"""
        self.__surf__.fill(self.seccolour)
        cur_life_rect = Rect(self.rect.topleft,
                             (int(life*(self.rect.bottomright[0])/self.max_life),
                              self.rect.bottomright[1]))
        pg.draw.rect(self.__surf__, self.colour, cur_life_rect)
        pg.draw.rect(self.__surf__, (255, 255, 255), self.rect, 3)
        pg.draw.polygon(self.__surf__, (255, 255, 255), self.__style_dots__)


    def update(self):
        """отрисовка каждый кадр"""
        LifeStatusBar.surface.blit(self.__surf__, self.pos)


class Breakable(Actor):
    """обеспечивает общие функции и поля для разрушаемых объектов"""
    def __init__(self, life, status_bar=None):
        self.life = life
        self.status_bar = status_bar
        Actor.__init__(self)

    def damage(self, damage):
        """нанести урон, если есть статус бар, обновить его"""
        self.life -= damage
        if self.status_bar:
            self.status_bar.update_indicator(self.life)

    def __dest_func__(self):
        """что случается при уничтожении объекта"""
        return

    def update(self):
        """если жизни нет, то уничтожить объект, очистить память"""
        if self.life < 0:
            self.__dest_func__()
            self.destroy()


class LineCollider(Actor):
    """Обработка пересечений с прямой
    typ:
    1) лазер"""
    __targets__ = []
    def __init__(self, pos1, pos2, typ):
        b = (pos1.x - pos2.x)/(pos2.y - pos1.y)
        self.diap = pos1, pos2
        self.equation =  b, -pos2.x - b*pos2.y  
        self.typ = typ
    
    def __is_around__(self, dot, dist):
        """если объект около прямой"""
        return abs(dot.x + self.equation[0]*dot.y + self.equation[1]) / \
               ((1 + self.equation[0]**2)**.5) < dist
    
    def __detect_collisions__(self):
        """проверить пересечения с прямой"""
        for actor in ACTORS:
            for target in LineCollider.__targets__:
                if type(actor) == target[0]:
                    if self.typ == 1 and \
                    (actor.phys_body.pos - self.diap[0]).length() > LASER_SAFE_DIST and \
                    self.__is_around__(actor.phys_body.pos, PLAYER_LASER_COLLIDE_DIST) and \
                    (self.diap[1] - self.diap[0]).length() > (self.diap[1] - actor.phys_body.pos).length():
                        actor.damage(LASER_DAMAGE)
                        actor.__laser_damage_effect__()
                        
    def update(self):
        """Посмотреть пересечения"""
        self.__detect_collisions__()
                        
    def update_after_flip(self):
        """Коллайдер сработал, теперь можно его удалить"""
        self.destroy()


class Effect(Actor):
    """для эффектов
    typ:
    1) взрыв (кружочек)
       [0] -- сторона квадрата текстуры, максимальный размер
       [1] -- сколько кадров будет взрываться
    2) след лазера
       [0] -- толщина линии
       [1] -- (x2, y2)
       [2] -- сколько кадров останется на картинке"""
    surface = pg.Surface(SCREEN_RECT.size) # слой эффектов
    
    def __init__(self, pos, colour, seccolour, typ, props, sleep=0, alpha=50):
        self.pos = from_relcord_to_disp_cord(pos)
        self.colour = colour
        self.seccolour = seccolour
        self.typ = typ
        self.props = props
        self.sleep = sleep
        self.alpha = alpha
        self.__eff_custom_init__()
        
    def __eff_custom_init__(self):
        """выбор метода инициализации"""
        if self.typ == 1:
            self.life = 0
            self.__surf__ = pg.Surface((self.props[0], self.props[0]))
            self.__surf__.fill(NULLCOLOUR)
            self.__surf__ = self.__surf__.convert_alpha()
            self.__surf__.set_alpha(self.alpha)
        elif self.typ == 2:
            self.life = 0  # немного быдлокода с лазером. сделать его оказалось сложнее, чем я думал
            self.pos = self.pos[0]//2, self.pos[1]//2
            self.pos2 = from_relcord_to_disp_cord(self.props[1])
            self.pos2 = self.pos2[0] // 2, self.pos2[1] // 2
        
    def __explosion_upd__(self):
        """обновление эффекта, если этот эффект -- эффект взрыва"""
        if self.life >= self.props[1]:
            self.destroy()
        # хотелось бы сделать плавный переход цветов
        self.__surf__.fill(NULLCOLOUR)
        pg.draw.circle( self.__surf__, self.colour, (self.props[0]//2, self.props[0]//2), 
                        int(self.props[0]/self.props[1]/2 * self.life) )
        Effect.surface.blit(self.__surf__,
                            (self.pos[0] - self.props[0] >> 1, self.pos[1] - self.props[0] >> 1),
                            special_flags=BLEND_RGBA_ADD)
        self.life += 1

    def __laser_upd__(self):
        """обновление эффекта, если этот эффект -- след лазера"""
        if self.life >= self.props[2]:
            self.destroy()
        pg.draw.line(Effect.surface, self.colour, self.pos, self.pos2, self.props[0])
        self.life += 1

    def __chose_upd_meth__(self):
        """выбор метода обновления"""
        if self.typ == 1:
            return self.__explosion_upd__
        elif self.typ == 2:
            return self.__laser_upd__

    def update(self):
        """обновить"""
        if self.sleep:
            self.sleep -= 1
        else:
            self.__chose_upd_meth__()()
        
    def update_after_flip(self):
        """обновление после отрисовки"""
        if self.typ == 1:
            self.__surf__.fill(NULLCOLOUR)


class Torpedo(Breakable):
    """Объект имеет начальный импульс, затем летит свободно
    Взрывоопасна и имеет сплешевый урон, распространяющийся по линейному закону
    Разрушаемый объект, ему можно наносить урон
    При запуске имеет задержку, чтобы не взорваться прямо в руках заряжающего
    Интересна тем, что наносит относительно большой урон и летит не по прямой траектории
    Некоторые тактики:
    * ) Пустить торпеду рядом с целью и подорвать ее лазером, когда она приблизится достаточно близко.
    * ) Если отправить ее в край экрана, она появится с другой стороны. Вот сюрприз для зазевавшегося противника!
    * ) Торпеда -- физический объект, так почему бы не запустить ее по кривой?
    * ) Если хочется убить и себя, и противника, то можно просто напускать тучу торпед по игровому полю. Авось попадет!
    * ) Если скучковать несколько торпед и подорвать одну из них, то взрыв будет очень впечатляющим!"""
    surface = pg.Surface(SCREEN_RECT.size)  # слой торпед
    __targets__ = []  # здесь и далее. с какими целями объект будет сталкиваться
    
    def __init__(self, position, angle, force, visible=True):
        self.phys_body = phys.PhysDot(position, ROCKET_MASS, 1, g_force_mult=ROCKET_GRAV_MULT)
        self.visible = visible
        self.phys_body.force( force )
        self.__sleep__ = ROCKET_SLEEP_TIME
        self.__surf__ = pg.Surface( (ROCKET_TEX_SIDE, ROCKET_TEX_SIDE) )
        self.__surf__.fill(NULLCOLOUR)
        self.__surf__ = self.__surf__.convert_alpha()
        self.lifetime = ROCKET_LIFETIME
        self.mesh = Mesh( ROCKET_MESH, Rect(0, 0, ROCKET_TEX_SIDE, ROCKET_TEX_SIDE))
        self.mesh.rotation(angle)
        Breakable.__init__(self, 1)

    def __blow_up__(self):
        """Взорваться"""
        for actor in ACTORS:
            for target in Torpedo.__targets__:
                if type(actor) == target[0]:
                    d = self.phys_body.dist_to(actor.phys_body)
                    if d < ROCKET_DAMAGE_RANGE:
                        actor.damage(ROCKET_DAMAGE/ROCKET_DAMAGE_RANGE * (ROCKET_DAMAGE_RANGE-d))

        ACTORS.append(Effect(self.phys_body.pos,
                             ROCKET_EXPLOSION_SECCOLOUR, None, 1,
                             (rnd.randint(*ROCKET_EXPLOSION_DIAP),
                              rnd.randint(*ROCKET_EXPLOSION_LIFE_DIAP)), sleep=30))
        ACTORS.append(Effect(self.phys_body.pos,
                             ROCKET_EXPLOSION_COLOUR, None, 1,
                             (rnd.randint(*ROCKET_EXPLOSION_DIAP),
                              rnd.randint(*ROCKET_EXPLOSION_LIFE_DIAP))))

        self.phys_body.delete()
        self.destroy()

    def __detect_collisions__(self):
        """определить столкновения"""
        if self.__sleep__ == 0:
            for actor in ACTORS:
                for target in Torpedo.__targets__:
                    if type(actor) == target[0] and not(actor is self) and \
                    actor.phys_body.is_collided(self.phys_body, target[1]):
                        if type(actor) == Torpedo and actor:
                            actor.__blow_up__()
                        if self:
                            self.__blow_up__()
                        return
        else:
            self.__sleep__ -= 1

    def __laser_damage_effect__(self):
        """что делать при попадании лазера"""
        self.__blow_up__()
        
    def render_to(self, screen):
        """в какую поверхонсть рисовать"""
        if self.visible:
            dcords = from_relcord_to_disp_cord(self.phys_body.pos)
            screen.blit(self.mesh.surface, (dcords[0] - ROCKET_TEX_SIDE >> 1, dcords[1] - ROCKET_TEX_SIDE >> 1))

    def update(self):
        if self.life < 0:
            self.__dest_func__()
        self.__detect_collisions__()
        self.render_to(Torpedo.surface)

        self.lifetime -= 1 
        if not self.lifetime:
            self.__blow_up__()
        
        if self.phys_body.is_collided(BLACK_HOLE, CENTER_COLLIDE_DIST):
            self.__blow_up__()

        if self.phys_body.pos.x > ACTOR_BORDER_CORD or self.phys_body.pos.x < -ACTOR_BORDER_CORD:
            self.phys_body.pos.x = -self.phys_body.pos.x
        elif self.phys_body.pos.y > ACTOR_BORDER_CORD or self.phys_body.pos.y < -ACTOR_BORDER_CORD:
            self.phys_body.pos.y = -self.phys_body.pos.y

                 
class Player(Breakable):
    """Класс игрока.
    Ваша посудина хоть и хлипка, но еще может показать маленьким мальчикам, как надо драться!
    Обладает инерцией, на корабль постоянно действуют силы тяжести.
    Следует учесть, что торпеды будут иметь импульс корабля. Соответственно корабль будет также иметь импульс торпеды.
    Кроме медленных и разрушительных торпед, на борту спрятана лазерная указка с нестабильной тритиевой батареей. Этой
    штукой лучше не светить в глаза!
    Конструкция трюма такова, что все его содержимое после уничтожения корпуса вылетает наружу. В том числе и торпеды.
    Будь осторожен!"""
    surface = pg.Surface(SCREEN_RECT.size) # слой игроков
    __targets__ = []

    def __init__(self, position, mesh, controls, angle=0.0, visible=True, status_bar=None):
        self.phys_body = phys.PhysDot(position, PLAYER_MASS, 1)
        self.visible = visible
        self.mesh = Mesh(mesh, Rect(0, 0, PLAYER_TEX_SIDE, PLAYER_TEX_SIDE), sec_colour_scheme=[PLAYER_LASER_DAMAGE_COLOURS])
        self.controls = controls
        self.rocket_suspend = PLAYER_ROCKET_SUSPEND
        self.rocket_reload = 0
        self.laser_suspend = PLAYER_LASER_SUSPEND
        self.laser_reload = 0
        self.__laser_damage_trig__ = 0  # чтобы поменять метод отрисовки в случае попадания лазера
        self.__controls_down__ = [False]*len(controls)
        self.__surf__ = pg.Surface((PLAYER_TEX_SIDE, PLAYER_TEX_SIDE))
        self.__surf__.fill(NULLCOLOUR)
        self.__surf__ = self.__surf__.convert_alpha()
        self.mesh.rotation(angle) # угол поворота от изначальных координа
        Breakable.__init__(self, PLAYER_LIFE, status_bar)
    
    def __detect_collisions__(self):
        """определение коллизий"""
        for actor in ACTORS:
                for target in Player.__targets__:
                    if type(actor) == target[0] and not(actor is self) and \
                    actor.phys_body.is_collided( self.phys_body, target[1]):
                        actor.damage(100500)
                        self.damage(100500)
    
    def update_events(self, e):
        """обрабатывает события внутри объекта"""
        if e.type == KEYDOWN:
            for key in enumerate(self.controls):
                if e.key == key[1]:
                    self.__controls_down__[key[0]] = True
                    break

        if e.type == KEYUP:
            for key in enumerate(self.controls):
                if e.key == key[1]:
                    self.__controls_down__[key[0]] = False
                    break

    def __torpedo__(self):
        """Пустить торпеду"""
        f = ROCKET_MASS * ROCKET_SPEED
        real_angle = self.mesh.__angle__ + phys.pi / 2
        fvec = f * phys.cos(real_angle), f * phys.sin(real_angle)
        self.phys_body.force((-fvec[0], -fvec[1]))
        pl_imp = self.phys_body.speed.x * ROCKET_MASS, \
                 self.phys_body.speed.y * ROCKET_MASS
        ACTORS.append(Torpedo((self.phys_body.pos.x, self.phys_body.pos.y),
                              self.mesh.__angle__, (pl_imp[0] + fvec[0], pl_imp[1] + fvec[1])
                              ))

    def __laser__(self):
        """Включить лазерную указку"""
        real_angle = phys.pi / 2 + self.mesh.__angle__
        pos2 = phys.Vector2((self.phys_body.pos.x + phys.cos(real_angle) * LASER_LENGTH,
                             self.phys_body.pos.y + phys.sin(real_angle) * LASER_LENGTH))
        ACTORS.append(LineCollider(self.phys_body.pos, pos2, 1))
        ACTORS.append(Effect(
            self.phys_body.pos,
            (255, 255, 255, 100), None,
            2, (3, pos2, 1)
        ))

    def __upd_controls__(self):
        """Обработка управления"""
        real_angle = phys.pi/2 + self.mesh.__angle__
        if self.__controls_down__[0]:  # forward
            self.phys_body.accelerate([phys.Vector2((PLAYER_SPEED * phys.cos(real_angle),
                                                     PLAYER_SPEED * phys.sin(real_angle)))])

        if self.__controls_down__[1]:  # left
            self.turn(-PLAYER_TURN_SPEED)

        if self.__controls_down__[2]:  # backward
            self.phys_body.accelerate([phys.Vector2((-PLAYER_SPEED * phys.cos(real_angle),
                                                     -PLAYER_SPEED * phys.sin(real_angle)))])

        if self.__controls_down__[3]:  # right
            self.turn(PLAYER_TURN_SPEED)

        if self.__controls_down__[4] and not self.rocket_reload:  # rocket
            self.rocket_reload = self.rocket_suspend
            self.__torpedo__()

        if self.__controls_down__[5] and not self.laser_reload:
            self.laser_reload = self.laser_suspend
            self.__laser__()

    def __laser_damage_effect__(self):
        """Эффект от попадания лазера"""
        self.__laser_damage_trig__ = LASER_DAMAGE_EFFECT_TIME
        self.mesh.colour_scheme = 1
        self.mesh.__redraw__()
    
    def turn(self, angle):
        """поворот на angle радиан влево"""
        self.mesh.turn(angle)

    def render_to(self, screen):
        """в какую поверхность рисовать"""
        if self.visible:
            if self.__laser_damage_trig__:
                self.__laser_damage_trig__ -= 1
                if not self.__laser_damage_trig__:
                    self.mesh.colour_scheme = 0
                    self.mesh.__redraw__()

            dcords = from_relcord_to_disp_cord(self.phys_body.pos)
            screen.blit(self.mesh.surface, (dcords[0] - PLAYER_TEX_SIDE >> 1, dcords[1] - PLAYER_TEX_SIDE >> 1))

    def __reload__(self):
        """перезарядка оружия"""
        if self.rocket_reload:
            self.rocket_reload -= 1
        if self.laser_reload:
            self.laser_reload -= 1

    def __rocket_madness__(self, count):
        for i in range(count):
            self.turn(2*phys.pi/count * i)
            self.__torpedo__()

    def __dest_func__(self):
        """уничтожить корабль!"""
        for i in range(20):
            ACTORS.append(Effect(
                self.phys_body.pos + phys.Vector2(( (rnd.random()*2 - 1) * PLAYER_COLLIDE_DIST,
                                                    (rnd.random()*2 - 1) * PLAYER_COLLIDE_DIST )),
                pg.Color( rnd.randint(0, 255), rnd.randint(0, 255),rnd.randint(0, 255), 255),
                None, 1,
                [rnd.randint(32,50), rnd.randint(40,50)], sleep= rnd.randint(0,50) + i*20
            ))

    def destroy(self):
        self.__rocket_madness__(PLAYER_DEAD_ROCKETS)
        Breakable.destroy(self)

    def update(self):
        self.__detect_collisions__()
        Breakable.update(self)
        self.__upd_controls__()
        self.__reload__()
        self.__surf__.fill(NULLCOLOUR)
        self.render_to(Player.surface)

        if self.phys_body.is_collided(BLACK_HOLE, CENTER_COLLIDE_DIST):
            self.damage(100500)

        if self.phys_body.pos.x > ACTOR_BORDER_CORD or self.phys_body.pos.x < -ACTOR_BORDER_CORD:
            self.phys_body.pos.x = -self.phys_body.pos.x
        elif self.phys_body.pos.y > ACTOR_BORDER_CORD or self.phys_body.pos.y < -ACTOR_BORDER_CORD:
            self.phys_body.pos.y = -self.phys_body.pos.y


def init_collisions():
    """Прописать, какие объекты будут сталкиваться друг с другом"""
    Torpedo.__targets__.append((Player, PLAYER_COLLIDE_DIST))
    Torpedo.__targets__.append((Torpedo, PLAYER_COLLIDE_DIST))
    Player.__targets__.append((Player, PLAYER_COLLIDE_DIST))
    LineCollider.__targets__.append((Player, PLAYER_COLLIDE_DIST))
    LineCollider.__targets__.append((Torpedo, PLAYER_COLLIDE_DIST))


def start():
    """Приготовления"""
    init_pygame()
    init_collisions()

    Effect.surface = Effect.surface.convert_alpha()
    #Torpedo.surface = Torpedo.surface.convert_alpha()
    Player.surface = Player.surface.convert_alpha()
    LifeStatusBar.surface = Effect.surface
    Torpedo.surface = Player.surface

    lifebar_rect = Rect(0, 0, 200, 20)
    lifebar_rect.midleft = (5, 10)
    lb1 = LifeStatusBar( lifebar_rect.copy(), (0, 255, 0), (255, 0, 0), PLAYER_LIFE)
    lifebar_rect.midright = (S_W-5, 10)
    lb2 = LifeStatusBar(lifebar_rect.copy(), (0, 255, 0), (255, 0, 0), PLAYER_LIFE)
    ACTORS.append(lb1)
    ACTORS.append(lb2)

    ACTORS.append( Player([.7,0], FIRST_PlAYER_MESH, FIRST_PLAYER_CONTROL, -phys.pi, status_bar=lb2))
    ACTORS.append( Player([-.7,0], SECOND_PlAYER_MESH, SECOND_PLAYER_CONTROL, status_bar=lb1 ))
    #ACTORS.append( Torpedo([.5,.5], (255, 0, 0, 255), (200, 0, 0, 255), 1, .001))
    #ACTORS.append( Effect( , (255,255,255,255), None, 1, (100,300) ) )


def loop():
    """основной луп"""
    clock = pg.time.Clock()
    back_surface = draw_background()

    while 1:
        for event in pg.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
            for actor in ACTORS:
                actor.update_events(event)

        phys.PhysDot.simulate(10)

        for actor in ACTORS:
            actor.update()

        pg.display.get_surface().blit(back_surface, (0, 0), )
        #pg.display.get_surface().blit(LifeStatusBar.surface, (0, 0))
        pg.display.get_surface().blit(Player.surface, (0, 0))
        #pg.display.get_surface().blit(Torpedo.surface, (0, 0))
        pg.display.get_surface().blit(Effect.surface, (0, 0))
        pg.display.flip()

        Player.surface.fill(NULLCOLOUR)
        #Torpedo.surface.fill(NULLCOLOUR)
        Effect.surface.fill(NULLCOLOUR)
        #LifeStatusBar.surface.fill(NULLCOLOUR)

        pg.display.get_surface().fill(NULLCOLOUR)
        for actor in ACTORS:
            actor.update_after_flip()

        clock.tick_busy_loop(FPS)
