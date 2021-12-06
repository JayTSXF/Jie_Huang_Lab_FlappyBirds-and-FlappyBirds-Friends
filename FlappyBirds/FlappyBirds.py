import pygame
import random
import os

W, H = 288, 512

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("FlappyBirds and FlappyBirds' friends")
clock = pygame.time.Clock()

images = {}
for image in os.listdir("assets/sprites"):
    name, extension = os.path.splitext(image)
    path = os.path.join('assets/sprites', image)
    images[name] = pygame.image.load(path)

floor_y = H - images['floor'].get_height()
start = pygame.mixer.Sound('assets/audio/start.wav')
die = pygame.mixer.Sound('assets/audio/die.wav')
hit = pygame.mixer.Sound('assets/audio/hit.wav')
score_x = pygame.mixer.Sound('assets/audio/score.wav')
flap_audio = pygame.mixer.Sound('assets/audio/flap.wav')

def main():

    while True:
        start.play()
        images['background'] = images[random.choice(['day', 'night', 'ice', 'rock', 'sky', 'green', 'rocky'])]
        images['birds'] = images[random.choice(['girl-1', 'girl-2', 'slime', 'tomato', 'dragon', 'doraemon', 'red-mid', 'yellow-mid', 'blue-mid', 'red-up', 'yellow-up', 'blue-up', 'red-down', 'yellow-down', 'blue-down'])]
        images['pipes'] = images[random.choice(['green-pipe', 'red-pipe'])]

        menu_window()
        result = game_window()
        end_window(result)

def menu_window():

    floor_gap = images['floor'].get_width() - W
    floor_x = 0

    guide_x = (W - images['guide'].get_width())/2
    guide_y = (floor_y - images['guide'].get_height())/2

    bird_x = W * 0.2
    bird_y = (H - images['birds'].get_height())/2
    bird_y_vel = 1
    bird_y_range = [bird_y - 8, bird_y + 8]



    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

        floor_x -= 4
        if floor_x <= - floor_gap:
            floor_x = 0

        bird_y += bird_y_vel
        if bird_y < bird_y_range[0] or bird_y > bird_y_range[1]:
            bird_y_vel *= -1

        screen.blit(images['background'], (0, 0))
        screen.blit(images['floor'], (floor_x, floor_y))
        screen.blit(images['guide'], (guide_x, guide_y))
        screen.blit(images['birds'], (bird_x, bird_y))
        pygame.display.update()
        clock.tick(45)

def game_window():
    score = 1
    score_y = 0
    flap_audio.play()
    floor_gap = images['floor'].get_width() - W
    floor_x = 0
    bird = Bird(W * 0.2, H * 0.4)
    pipes = []
    n_pairs = 4
    distance = 150
    pipe_gap = 150
    FPS = 20


    for i in range(n_pairs):
        pipe_y = random.randint(int(H*0.3), int(H*0.7))
        pipe_up = Pipe(W + i * distance, pipe_y, True)
        pipe_down = Pipe(W + i * distance, pipe_y - pipe_gap, False)
        pipes.append(pipe_up)
        pipes.append(pipe_down)

    while True:
        flap = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                flap = True
                flap_audio.play()

        FPS += 0.02
        if FPS >= 35:
            FPS = 35

        pipe_gap -= 0.2
        if pipe_gap <= 100:
            pipe_gap = 100

        floor_x -= 4
        if floor_x <= - floor_gap:
            floor_x = 0

        bird.update(flap)
        first_pipe_up = pipes[0]
        first_pipe_down = pipes[1]
        if first_pipe_up.rect.right < 0:
            pipes.remove(first_pipe_up)
            pipes.remove(first_pipe_down)
            pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
            new_pipe_up = Pipe(first_pipe_up.rect.x + n_pairs * distance, pipe_y)
            new_pipe_down = Pipe(first_pipe_down.rect.x + n_pairs * distance, pipe_y - pipe_gap, False)
            pipes.append(new_pipe_up)
            pipes.append(new_pipe_down)
            del first_pipe_down, first_pipe_up

        for pipe in pipes:
            pipe.update()

        if bird.rect.y > floor_y - 30 or bird.rect.y < 0:
            hit.play()
            die.play()
            result = {'bird': bird, 'score': score}
            return result

        for pipe in pipes:
            right_to_left = max(bird.rect.right, pipe.rect.right) - min(bird.rect.left, pipe.rect.left)
            bottom_to_top = max(bird.rect.bottom, pipe.rect.bottom) - min(bird.rect.top, pipe.rect.top)
            if right_to_left < bird.rect.width + pipe.rect.width and bottom_to_top < bird.rect.height + pipe.rect.height:
                hit.play()
                die.play()
                result = {'bird': bird, 'score': score}
                return result

        if pipes[0].rect.right < bird.rect.left:
            score_y += 1
        if score_y == 16:
            score += 1
            score_x.play()
            score_y = 0

        screen.blit(images['background'], (0, 0))
        for pipe in pipes:
            screen.blit(pipe.image, pipe.rect)
        screen.blit(images['floor'], (floor_x, floor_y))

        show_scores(score)

        screen.blit(bird.image, bird.rect)
        pygame.display.update()
        clock.tick(FPS)


def end_window(result):

    gameover_x = (W - images['gameover'].get_width())/2
    gameover_y = (floor_y - images['gameover'].get_height())/2

    bird = result['bird']
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return

        bird.go_die()
        screen.blit(images['background'], (0, 0))
        screen.blit(images['floor'], (0, floor_y))
        screen.blit(images['gameover'], (gameover_x, gameover_y))
        show_scores(result['score'])
        screen.blit(images['R'], (gameover_x, gameover_y + 250))
        screen.blit(images['rip'], (gameover_x + 50, gameover_y + 105))
        screen.blit(bird.image, bird.rect)
        pygame.display.update()
        clock.tick(30)


def show_scores(score):
    score_str = str(score)
    n = len(score_str)
    w = images['0'].get_width() * 1.1
    x = (W - n * w) / 2
    y = H * 0.1
    for number in score_str:
        screen.blit(images[number], (x, y))
        x += w

class Bird:
    def __init__(self, x, y):
        self.image_x = images['birds']
        self.image = self.image_x
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y_vel = -10
        self.y_max = 10
        self.gravity = 1
        self.rotate = 45
        self.rotate_max = -20
        self.rotate_vel = -3
        self.y_vel_after_flap = -10
        self.rotate_after_flap = 45


    def update(self, flap = False):
        if flap:
            self.y_vel = self.y_vel_after_flap
            self.rotate = self.rotate_after_flap

        self.image = self.image_x

        self.y_vel = min(self.y_vel + self.gravity, self.y_max)
        self.rect.y += self.y_vel

        self.rotate = max(self.rotate + self.rotate_vel, self.rotate_max)
        self.image = pygame.transform.rotate(self.image, self.rotate)

    def go_die(self):
        if self.rect.y < floor_y - 30:
            self.rect.y += self.y_max
            self.rotate = -90
            self.image = self.image_x
            self.image = pygame.transform.rotate(self.image, self.rotate)

class Pipe():
    def __init__(self, x, y, upwards=True):
        self.rotate = 180
        if upwards:
            self.image = images['pipes']
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.top = y
        else:
            self.image = images['pipes']
            self.image = pygame.transform.rotate(self.image, self.rotate)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
        self.x_vel = -4

    def update(self):
        self.rect.x += self.x_vel

main()
