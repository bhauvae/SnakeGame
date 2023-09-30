import pygame
from random import randint, choice
from block_size import block_size
import color
from messages import messages

pygame.init()
pygame.display.set_caption("SNAKE")

MAX_SCALE = (pygame.display.Info().current_w, pygame.display.Info().current_h)
MAX_SCALE_BLOCK_SIZE = block_size(MAX_SCALE[0], MAX_SCALE[1], min(MAX_SCALE[0] // 25, MAX_SCALE[1] // 25))
MIN_SCALE = (MAX_SCALE[0] // 2, MAX_SCALE[1] // 2)
MIN_SCALE_BLOCK_SIZE = block_size(MIN_SCALE[0], MIN_SCALE[1], min(MIN_SCALE[0] // 20, MIN_SCALE[1] // 20))
ORIGIN = (0, 0)
PADDING = 20
TITLE_TEXT_SIZE = 100
SCORE_TEXT_SIZE = 50
MESSAGE_TEXT_SIZE = 48
BLINK_TIME = 600
INITIAL_FPS = 12
MAX_FPS = 30
# ADD SETTINGS STATES
GAME_STATES = ("START MENU", "GAME", "GAME OVER", "PAUSE", "MESSAGES")

FONT = 'Minercraftory.ttf'
MESSAGE_FONT = 'DTM-Mono.otf'
INITIAL_GAME_STATE = GAME_STATES[0]


class Game:

    def __init__(self):

        self.is_fullscreen = None
        self.screen_height = MIN_SCALE[1]
        self.screen_width = MIN_SCALE[0]
        self.message = choice(messages)
        self.block_size = MIN_SCALE_BLOCK_SIZE
        self.fps = INITIAL_FPS
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.game_state = INITIAL_GAME_STATE

    def render_title(self, text, text_color, position):
        size = TITLE_TEXT_SIZE
        font = pygame.font.Font(FONT, size)
        title = font.render(text, True, text_color)

        if position == "CENTRE":
            position = ((self.screen_width - title.get_width()) / 2, (self.screen_height - title.get_height()) / 2)

        self.screen.blit(title, position)

    def render_score(self, score, score_color, position, add_blink):

        size = SCORE_TEXT_SIZE
        if position == "PADDED_ORIGIN":
            position = (ORIGIN[0] + PADDING, ORIGIN[1] + PADDING)

        font = pygame.font.Font(FONT, size)

        if add_blink:
            blink_interval = BLINK_TIME  # in milliseconds
            blink_timer = pygame.time.get_ticks()

            text_visible = (blink_timer // blink_interval) % 2 == 0

            if text_visible:
                title = font.render(str(score), True, score_color)
                self.screen.blit(title, position)
        else:
            title = font.render(str(score), True, score_color)
            self.screen.blit(title, position)

    def render_message(self, text, width, font_face):

        size = MESSAGE_TEXT_SIZE
        width = width - 2 * PADDING
        line_y = 0
        line_y_pos = []
        line_spacing = -2
        wrapped_text = []

        font = pygame.font.Font(font_face, size)
        font_height = font.size(font_face)[1]

        text.replace(r'\n', '').replace(r'\r', '').replace(r'\t', '')

        while text:
            i = 1

            while font.size(text[:i])[0] < width and i < len(text):
                i += 1

            if i < len(text):
                i = text.rfind(" ", 0, i) + 1

            wrapped_text.append(text[:i])
            line_y_pos.append(line_y)
            line_y += font_height + line_spacing

            text = text[i:]

        box_height = line_y_pos[-1]
        text_box = pygame.Rect(((self.screen_width - width) / 2, (self.screen_height - box_height) / 2, self.screen_width, box_height))

        for line, wrapped_line_y in zip(wrapped_text, line_y_pos):
            text_line = font.render(str(line), True, color.WHITE)
            self.screen.blit(text_line, (text_box.left, text_box.top + wrapped_line_y))

    def update_screen_dimensions(self, snake, food):

        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        if self.is_fullscreen:
            self.block_size = MAX_SCALE_BLOCK_SIZE
        else:
            self.block_size = MIN_SCALE_BLOCK_SIZE

        snake.velocity = self.block_size
        food.pos = Food.generate(snake.body)
        self.reset(snake,food)

    def increase_fps(self, snake):

        increment_rate = 0.01
        max_fps = MAX_FPS

        new_fps = self.fps + (len(snake.body) * increment_rate)

        self.fps = min(new_fps, max_fps)

    def reset(self, snake, food):

        snake.pos = Snake.generate()
        snake.speed = [0, 0]
        snake.speed[randint(0, 1)] = ((-1) ** randint(0, 1)) * snake.velocity
        snake.score = 0
        snake.body = []
        food.pos = Food.generate(snake.body)
        self.fps = INITIAL_FPS
        self.message = choice(messages)

    def run(self):

        running = True

        snake = Snake(pos=Snake.generate(), velocity=self.block_size)
        snake.speed[randint(0, 1)] = ((-1) ** randint(0, 1)) * snake.velocity

        food = Food(Food.generate(snake.body))

        while running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    if self.is_fullscreen:
                        self.screen = pygame.display.set_mode(MIN_SCALE)
                        self.is_fullscreen = False
                    else:
                        self.screen = pygame.display.set_mode(MAX_SCALE, pygame.FULLSCREEN)
                        self.is_fullscreen = True

                    self.update_screen_dimensions(snake, food)

                elif event.type == pygame.KEYDOWN:

                    # START MENU
                    if self.game_state == GAME_STATES[0]:

                        if event.key == pygame.K_SPACE:
                            self.game_state = GAME_STATES[1]

                        if event.key == pygame.K_m:
                            self.game_state = GAME_STATES[4]

                    # GAME
                    elif self.game_state == GAME_STATES[1]:

                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            if snake.speed[1] != snake.velocity:
                                snake.speed = [0, -snake.velocity]
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            if snake.speed[1] != -snake.velocity:
                                snake.speed = [0, snake.velocity]
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            if snake.speed[0] != snake.velocity:
                                snake.speed = [-snake.velocity, 0]
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            if snake.speed[0] != -snake.velocity:
                                snake.speed = [snake.velocity, 0]

                        elif event.key == pygame.K_p:
                            self.game_state = GAME_STATES[3]

                    # GAME OVER
                    elif self.game_state == GAME_STATES[2]:
                        if event.key == pygame.K_SPACE:
                            self.game_state = GAME_STATES[4]

                    # PAUSE
                    elif self.game_state == GAME_STATES[3]:
                        if event.key == pygame.K_p:
                            self.game_state = GAME_STATES[1]

                    # MESSAGES
                    elif self.game_state == GAME_STATES[4]:
                        if event.key == pygame.K_SPACE:
                            self.game_state = GAME_STATES[1]
                            self.reset(snake, food)

                        if event.key == pygame.K_m:
                            self.message = choice(messages)

            if self.game_state == GAME_STATES[0]:
                self.start_menu()
            if self.game_state == GAME_STATES[1]:
                self.game(snake, food)
            if self.game_state == GAME_STATES[2]:
                self.game_over(snake)
            if self.game_state == GAME_STATES[3]:
                self.pause(snake, food)
            if self.game_state == GAME_STATES[4]:
                self.messages()

    def start_menu(self):

        self.screen.fill(color.BLACK)

        self.render_title("SNAKE", color.WHITE, position="CENTRE")

        pygame.display.update()

    def game(self, snake, food):

        self.screen.fill(color.BLACK)

        snake.update_position()
        if snake.check_game_over():
            self.game_state = GAME_STATES[2]
        if snake.check_collision(food.pos):
            food.pos = Food.generate(snake.body)
            game.increase_fps(snake)

        self.render_score(snake.score, color.WHITE, position="PADDED_ORIGIN", add_blink=False)

        snake.render()
        food.render()

        pygame.display.update()
        self.clock.tick(self.fps)

    def game_over(self, snake):

        self.screen.fill(color.BLACK)

        snake.render(color.GRAY)

        self.render_title("GAME OVER", color.WHITE, position="CENTRE")
        self.render_score(snake.score, color.WHITE, position="PADDED_ORIGIN", add_blink=True)

        pygame.display.update()

    def pause(self, snake, food):

        self.screen.fill(color.BLACK)

        snake.render(color.GRAY)
        food.render(color.GRAY)

        self.render_title("PAUSE", color.WHITE, position="CENTRE")

        pygame.display.update()

    def messages(self):

        self.screen.fill(color.BLACK)

        self.render_message(self.message, self.screen_width, font_face=MESSAGE_FONT)

        pygame.display.update()


class Snake:
    def __init__(self, pos, velocity, speed=None, body=None, score=0):

        if body is None:
            body = []
        if speed is None:
            speed = [0, 0]

        self.pos = pos
        self.speed = speed
        self.body = body
        self.score = score
        self.velocity = velocity

    @staticmethod
    def generate():
        rand_x = randint(0, (game.screen_width - game.block_size) // game.block_size) * game.block_size
        rand_y = randint(0, (game.screen_height - game.block_size) // game.block_size) * game.block_size

        return [rand_x, rand_y]

    def update_position(self):
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]

        if self.pos[0] < ORIGIN[0] or self.pos[0] >= game.screen_width:
            self.pos[0] %= game.screen_width

        if self.pos[1] < ORIGIN[1] or self.pos[1] >= game.screen_height:
            self.pos[1] %= game.screen_height

        self.body.insert(0, [self.pos[0], self.pos[1]])
        if len(self.body) > self.score + 1:
            self.body.pop()

    def check_collision(self, food_pos):
        if self.pos[0] == food_pos[0] and self.pos[1] == food_pos[1]:
            self.score += 1

            return True
        return False

    def check_game_over(self):
        for block in self.body[1:]:
            if block[0] == self.pos[0] and block[1] == self.pos[1]:
                return True
        return False

    def render(self, body_color=None):

        outline_thickness = 1
        if body_color is None:
            body_color = color.WHITE

        for block in self.body:
            pygame.draw.rect(
                game.screen,
                body_color,
                pygame.Rect(block[0], block[1], game.block_size, game.block_size)
            )
            pygame.draw.rect(
                game.screen,
                color.BLACK,
                pygame.Rect(block[0], block[1], game.block_size, game.block_size),
                outline_thickness
            )


class Food:
    def __init__(self, pos):
        self.pos = pos

    @staticmethod
    def generate(snake_body):
        while True:
            food_x = randint(0, (game.screen_width - game.block_size) // game.block_size) * game.block_size
            food_y = randint(0, (game.screen_height - game.block_size) // game.block_size) * game.block_size

            if [food_x, food_y] not in snake_body:
                return [food_x, food_y]

    def render(self, body_color=None):

        outline_thickness = 1
        if body_color is None:
            body_color = color.WHITE

        pygame.draw.rect(
            game.screen,
            body_color,
            pygame.Rect(self.pos[0], self.pos[1], game.block_size, game.block_size)
        )

        pygame.draw.rect(
            game.screen,
            color.BLACK,
            pygame.Rect(
                self.pos[0] - outline_thickness,
                self.pos[1] - outline_thickness,
                game.block_size + 2 * outline_thickness,
                game.block_size + 2 * outline_thickness
            ),
            outline_thickness
        )


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
