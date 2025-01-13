import os
import json
import pygame
import random
from datetime import datetime
import sys
pygame.init()

screen_width = 680
screen_height = 780
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders")

player_img = pygame.image.load("assets/sprites/ship.png").convert_alpha()
enemy_img = pygame.image.load("assets/sprites/enemy.png").convert_alpha()
bullet_img = pygame.image.load('assets/sprites/bullet.png').convert_alpha()

font = pygame.font.Font("assets/fonts/Pixel.ttf", 30)
game_over_font = pygame.font.Font("assets/fonts/Pixel.ttf", 60)

class Star:
    def __init__(self, x, y, speed, size):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size

    def move(self):
        self.y += self.speed
        if self.y > screen_height:
            self.y = 0
            self.x = random.randint(0, screen_width)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.size)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed_to_right_left = 8
        self.alive = True

    def draw(self):
        screen.blit(player_img, (self.x, self.y))

    def move(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
            self.x -= self.speed_to_right_left
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < screen_width - player_img.get_width():
            self.x += self.speed_to_right_left
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.y > 0:
            self.y -= 10
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.y < screen_height - player_img.get_height():
            self.y += 10

class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed * 1.5
        self.direction = random.choice([-1, 1])

    def draw(self):
        screen.blit(enemy_img, (self.x, self.y))

    def move(self):
        self.y += self.speed
        self.x += self.speed * self.direction
        if self.x <= 0 or self.x >= screen_width - enemy_img.get_width():
            self.direction *= -1
        if self.y > screen_height:
            self.y = 0
            self.x = random.randint(0, screen_width - enemy_img.get_width())

class Bullet:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.active = True

    def draw(self):
        if self.active:
            screen.blit(bullet_img, (self.x, self.y))

    def move(self):
        if self.active:
            self.y -= self.speed
            if self.y < 0:
                self.active = False

class TripleShot:
    def __init__(self, x, y, speed):
        self.bullets = [
            Bullet(x - 20, y, speed),
            Bullet(x, y, speed),
            Bullet(x + 20, y, speed)
        ]

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()

    def move(self):
        for bullet in self.bullets:
            bullet.move()

    def is_active(self):
        return any(bullet.active for bullet in self.bullets)

    def check_collisions(self, enemies, score):
        for bullet in self.bullets:
            if bullet.active:
                for enemy in enemies:
                    if (bullet.x >= enemy.x and bullet.x <= enemy.x + enemy_img.get_width()) and \
                            (bullet.y >= enemy.y and bullet.y <= enemy.y + enemy_img.get_height()):
                        bullet.active = False
                        enemy.y = 0
                        enemy.x = random.randint(0, screen_width - enemy_img.get_width())
                        score += 10
        return score



def save_score(score, level):
    record_data = load_score_data()
    current_date = datetime.now().strftime("%d.%m.%y")

    if score > record_data[level]["score"]:
        record_data[level] = {"score": score, "date": current_date}

    with open('highscore.json', 'w') as file:
        json.dump(record_data, file)

def load_score_data():
    if os.path.exists('highscore.json'):
        with open('highscore.json', 'r') as file:
            return json.load(file)
    else:
        return {
            "easy": {"score": 0, "date": "00.00.00"},
            "medium": {"score": 0, "date": "00.00.00"},
            "hard": {"score": 0, "date": "00.00.00"},
            "easy demon": {"score": 0, "date": "00.00.00"},
            "medium demon": {"score": 0, "date": "00.00.00"},
        }

def show_scoreboard():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    running = False  
                    main_menu()  

        screen.fill((0, 0, 0))
        highscore_data = load_score_data()
        y_position = 50  
        for difficulty, data in highscore_data.items():
            score_text = font.render(f"{difficulty} ==  {data['score']} == Date: {data['date']} ", True, (255, 255, 255))
            screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, y_position))
            y_position += 40

        pygame.display.flip()
        pygame.time.Clock().tick(60)    

def help_menu_items():
    return {
        "Shoot": ["LMB", "Space"],
        "Triple Shot": ["RMB", "E"],
        "Move Up": ["Up Arrow", "W"],
        "Move Down": ["Down Arrow", "S"],
        "Move Left": ["Left Arrow", "A"],
        "Move Right": ["Right Arrow", "D"]
    }

def help_menu():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    running = False
                    main_menu()

        screen.fill((0, 0, 0))

        menu_items = help_menu_items()
        y_position = 50

        for action, keys in menu_items.items():
            action_text = font.render(action, True, (255, 0, 0))
            screen.blit(action_text, (50, y_position))

            keys_text = font.render(f"Press: {', '.join(keys)}", True, (255, 255, 255))
            screen.blit(keys_text, (250, y_position))

            y_position += 40  

        pygame.display.flip()
        pygame.time.Clock().tick(60)


def main_menu(difficulty=None, prev_score=0):
    menu_items = ["Easy", "Medium", "Hard", "Easy Demon", "Medium Demon", "Help", "ScoreBoard", "Exit"]
    selected_item = 0
    highscore_data = load_score_data()

    button_rects = []
    button_height = 40
    button_padding = 10

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, button_rect in enumerate(button_rects):
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        if menu_items[i] == "ScoreBoard":
                            show_scoreboard()
                        elif menu_items[i] == "Help":
                            help_menu()  # вызов функции для помощи
                        elif menu_items[i] == "Exit":
                            pygame.quit()
                            sys.exit()
                        else:
                            main_game(menu_items[i].lower(), resume=False) 
                            return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_item = (selected_item - 1) % len(menu_items)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_item = (selected_item + 1) % len(menu_items)
                if event.key == pygame.K_RETURN or event.key == pygame.K_f:
                    if menu_items[selected_item] == "ScoreBoard":
                        show_scoreboard()
                    elif menu_items[selected_item] == "Help":
                        help_menu()  # вызов функции для помощи
                    elif menu_items[selected_item] == "Exit":
                        pygame.quit()
                        sys.exit()
                    else:
                        main_game(menu_items[selected_item].lower(), resume=False) 
                        return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


        screen.fill((0, 0, 0))
        button_rects.clear()

        for i, item in enumerate(menu_items):
            color = (255, 0, 0) if i == selected_item else (255, 255, 255)
            text = font.render(item, True, color)
            button_rect = screen.blit(text, (screen_width // 2 - text.get_width() // 2,
                                             screen_height // 2 - text.get_height() // 2 + i * button_height + button_padding))
            button_rects.append(button_rect)

        pygame.display.flip()
        pygame.time.Clock().tick(120)
def game_over_screen(score, level):
    game_over_text = game_over_font.render("Game Over...", True, (255, 0, 0))
    press_enter_text = font.render("Press enter...", True, (255, 255, 255))

    screen.fill((0, 0, 0))
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 3))
    screen.blit(press_enter_text, (screen_width // 2 - press_enter_text.get_width() // 2, screen_height // 2))
    pygame.display.flip()

    save_score(score, level)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                main_menu(difficulty=level, prev_score=score)
                return






def main_game(difficulty, resume=False, prev_score=0):
    player = Player(screen_width // 2, screen_height - 60)
    enemy_speed = {"easy": 3, "medium": 3, "hard": 4, "easy demon": 5, "medium demon": 6}[difficulty]
    enemy_count = {"easy": 15, "medium": 16, "hard": 17, "easy demon": 18, "medium demon": 19,}[difficulty]
    enemies = [Enemy(random.randint(0, screen_width - enemy_img.get_width()), random.randint(-100, -40), random.randint(1, enemy_speed)) for _ in range(enemy_count)]
    bullets = []
    stars = [Star(random.randint(0, screen_width), random.randint(0, screen_height), random.uniform(1, 3), random.randint(2, 4)) for _ in range(50)]
    score = prev_score if resume else 0
    level = difficulty

    last_shot_time = pygame.time.get_ticks()
    last_triple_shot_time = pygame.time.get_ticks()
    triple_shot_cooldown = 400  # Задержка на 400 мс
    bullet_cooldown = 120

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pygame.time.get_ticks() - last_shot_time >= bullet_cooldown:
                    bullet = Bullet(player.x + player_img.get_width() // 2 - bullet_img.get_width() // 2, player.y, 10)
                    bullets.append(bullet)
                    last_shot_time = pygame.time.get_ticks()
                elif event.button == 3 and pygame.time.get_ticks() - last_triple_shot_time >= triple_shot_cooldown:
                    triple_shot = TripleShot(player.x + player_img.get_width() // 2, player.y, 10)
                    bullets.append(triple_shot)
                    last_triple_shot_time = pygame.time.get_ticks()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and pygame.time.get_ticks() - last_shot_time >= bullet_cooldown:
                    bullet = Bullet(player.x + player_img.get_width() // 2 - bullet_img.get_width() // 2, player.y, 10)
                    bullets.append(bullet)
                    last_shot_time = pygame.time.get_ticks()
                elif event.key == pygame.K_e and pygame.time.get_ticks() - last_triple_shot_time >= triple_shot_cooldown:
                    triple_shot = TripleShot(player.x + player_img.get_width() // 2, player.y, 10)
                    bullets.append(triple_shot)
                    last_triple_shot_time = pygame.time.get_ticks()
                elif event.key == pygame.K_ESCAPE:
                    main_menu(difficulty=level, prev_score=score)
                    return

        player.move()
        for enemy in enemies:
            enemy.move()

        for bullet in bullets[:]:
            if isinstance(bullet, TripleShot):
                bullet.move()
                score = bullet.check_collisions(enemies, score)
                if not bullet.is_active():
                    bullets.remove(bullet)
            else:
                bullet.move()
                if bullet.active:
                    for enemy in enemies:
                        if (bullet.x >= enemy.x and bullet.x <= enemy.x + enemy_img.get_width()) and \
                                (bullet.y >= enemy.y and bullet.y <= enemy.y + enemy_img.get_height()):
                            bullet.active = False
                            enemy.y = 0
                            enemy.x = random.randint(0, screen_width - enemy_img.get_width())
                            score += 10
                else:
                    bullets.remove(bullet)

        for star in stars:
            star.move()

        for enemy in enemies:
            if (enemy.x < player.x < enemy.x + enemy_img.get_width() or
                enemy.x < player.x + player_img.get_width() < enemy.x + enemy_img.get_width()) and \
                (enemy.y < player.y < enemy.y + enemy_img.get_height() or
                 enemy.y < player.y + player_img.get_height() < enemy.y + enemy_img.get_height()):
                player.alive = False
                game_over_screen(score, level)
                return

        screen.fill((0, 0, 0))

        for star in stars:
            star.draw(screen)

        player.draw()

        for enemy in enemies:
            enemy.draw()

        for bullet in bullets:
            bullet.draw()

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

main_menu()
