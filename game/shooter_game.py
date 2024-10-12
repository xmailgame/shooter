from pygame import *
from random import randint
from time import time as timer
from pygame.font import SysFont

score = 0  # сбито кораблей
lost = 0  # пропущено кораблей
goal = 30  # количество сбить, которое нужно сбить
max_lost = 3  # количество сбить, которое можно пропустить
life = 3  # количество очков здоровья


class GameSprite(sprite.Sprite):
    """базовый класс для создания спрайтов"""

    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # конструктор класса
        super().__init__()
        # каждый спрайт - это картинка
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        # каждый спрайт - это прямоугольник rect
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        # нарисовать персонажа
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    """класс-наследник GameSprite, для создания главного героя"""

    def update(self):
        """перемещение персонажа по клавишам"""
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        """выстрел"""
        bullet = Bullet(imb_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)


class Enemy(GameSprite):
    """класс-наследник GameSprite, для создания противника"""

    def update(self):
        """автоматическое перемещение вниз по карте"""
        self.rect.y += self.speed
        global lost
        # исчезает, если дойдёт до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1


class Asteroid(GameSprite):
    """класс-наследник GameSprite, для создания астероида"""

    def update(self):
        """автоматическое перемещение вниз по карте"""
        self.rect.y += self.speed
        # исчезает, если дойдёт до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0


class Bullet(GameSprite):
    """класс-наследник GameSprite, для создания пули"""

    def update(self):
        """автоматическое перемещение вниз по карте"""
        self.rect.y += self.speed
        # исчезает, если дойдёт до края экрана
        if self.rect.y < 0:
            self.kill()


# подключаем музыку
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# подключаем шрифт
font.init()
font1 = font.SysFont('Arial', 80)
font2 = font.SysFont('Arial', 36)

win = font1.render('ПОБЕДА', True, (255, 255, 255))
lose = font1.render('ПОРАЖЕНИЕ', True, (191, 0, 0))

# картинки
img_back = 'galaxy.jpg'
img_hero = 'rocket.png'
img_enemy = 'ufo.png'
imb_bullet = 'bullet.png'
img_asteroid = 'asteroid.png'

# окно игры
win_width = 700
win_height = 500
window = display.set_mode((win_width, win_height))
display.set_caption('Космический шутер')
# фон сцены
background = transform.scale(image.load(img_back), (win_width, win_height))

# создаём спрайты
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)
# враги
monsters = sprite.Group()
for i in range(5):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)
# пули
bullets = sprite.Group()

# астероиды
asteroids = sprite.Group()
for i in range(2):
    asteroid = Asteroid(img_asteroid, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
    asteroids.add(asteroid)

# игровой цикл
finish = False  # вспомогательная переменная
run = True  # флаг цикла

reload_time = False  # флаг отвечающий за перезарядку
num_fire = 0  # счётчик выстрелов
while run:
    # событие "закрыть игру"
    for e in event.get():
        if e.type == QUIT:
            run = False
        # событие нажатия кнопки на пробел - спрайт стреляет
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                # проверяем сколько сделано выстрелов и не идёт ли сейчас перезарядка
                if num_fire < 5 and not reload_time:
                    num_fire += 1
                    fire_sound.play()
                    ship.fire()
                if num_fire >= 5 and not reload_time:
                    # если игрок сделал 5 выстрелов, засекаем время и ставим флаг перезарядки
                    last_time = timer()
                    reload_time = True

    if not finish:
        # отрисовываем фон и персонажей игры
        window.blit(background, (0, 0))

        # пишем текст на экране
        text = font2.render('Счёт: ' + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render('Пропущено: ' + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        # отрисовываем спрайты, воспроизводим их движение
        ship.update()
        ship.reset()

        monsters.update()
        monsters.draw(window)

        bullets.update()
        bullets.draw(window)

        asteroids.update()
        asteroids.draw(window)

        # проверка перезарядки
        if reload_time:
            now_time = timer()
            if now_time - last_time < 3:
                # если перезарядка не кончилась, выводим информацию о ней
                reload = font2.render('Перезарядка, ждите...', 1, 'indianred')
                window.blit(reload, (230, 460))
            else:
                # если 3 сек прошло, обнуляем счётчик пуль и снимаем флаг перезарядки
                num_fire = 0
                reload_time = False

        # обработка столкновения пули и противника
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        # если спрайт коснулся врага, уменьшаем очки здоровья
        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
            sprite.spritecollide(ship, monsters, True)
            sprite.spritecollide(ship, asteroids, True)
            life -= 1

        # поражение - пропустили слишком много противников, или потеряли все очки здоровья
        if lost >= max_lost or life == 0:
            # проиграли, ставим фон и отключаем управление спрайтами
            finish = True
            window.blit(lose, (200, 200))

        # победа - очков набрано достаточно
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))

        # отображаем текст с количеством здоровья, цвет очков здоровья разный в зависимости от значения
        if life == 3:
            life_color = 'lawngreen'
        if life == 2:
            life_color = 'gold'
        if life == 1:
            life_color = 'red'

        text_life = font1.render(str(life), 1, life_color)
        window.blit(text_life, (650, 10))

        display.update()
    time.delay(50)
