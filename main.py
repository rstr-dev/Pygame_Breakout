import random
import pygame
import time

pygame.init()

SCREEN = pygame.display.set_mode( (1680,900))
# SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
    
WIDTH, HEIGHT = pygame.display.get_surface().get_size()
FONT = pygame.font.SysFont('arial', 50)
pygame.display.set_caption("PONG DEMO")
SCREEN.fill(BLACK) 

MIDDLE_W = WIDTH / 2
MIDDLE_H = HEIGHT / 2
BRICK_W = WIDTH / 6
BRICK_H = BRICK_W / 5
PADDING = 15

PADDLE_W = WIDTH / 8
PADDLE_H = 20
PADDLE_Y = HEIGHT - (PADDLE_H * 2)

PUCK_S = 50 # width and height of the puck
COMP_SPEED = 1.75

class Puck(): # creates a puck that moves across the screen
    def __init__(self, last_brick):
        self.angle = 0.0 # pucks y axis movement
        self.direction = 1 # puck moves up (-1) or down (1)
        self.rect = pygame.Rect(MIDDLE_W - (PUCK_S / 2), last_brick.rect.top + last_brick.rect.height + (PUCK_S / 2), PUCK_S, PUCK_S) # creating the rectangle
        self.speed = 10.0 # puck movement speed
        self.lives = 3
        self.last_brick = last_brick
        
    def middle(self):
        return self.rect.left + (self.rect.width / 2)
    
    def reset(self):
        self.rect = pygame.Rect(MIDDLE_W - (PUCK_S / 2), self.last_brick.rect.top + self.last_brick.rect.height + (PUCK_S / 2), PUCK_S, PUCK_S) # creating the rectangle
        self.angle = 0.0 # pucks y axis movement
        self.direction = 1 # puck moves up (-1) or down (1)
        
    def update(self): # redraw the puck
        self.rect = pygame.Rect(self.rect.left + self.angle, self.rect.top + (self.direction * self.speed), PUCK_S, PUCK_S) # move according to the direction and angle
        pygame.draw.rect(SCREEN, WHITE, self) # redraw on screen
       
colors = {-1: None, 0: (204, 153, 255), 1: (157, 154, 255), 2: (154, 255, 195), 3: (255, 255, 154), 4: (255, 222, 154), 5: (255, 154, 154)}
 
class Brick():
    def __init__(self, x, y, health): 
        self.rect = pygame.Rect(x, y, BRICK_W, BRICK_H)
        self.health = health
        self.color = colors[6 - health]
        
    def middle(self):
        return self.rect.left + (self.rect.width / 2)
    
    def subtract_health(self):
        self.health = self.health - 1
        print(self.health)
        self.color = colors[self.health]
    
    def update(self):
        pygame.draw.rect(SCREEN, BLACK, self)
        inner_rect = pygame.Rect(self.rect.left + 2, self.rect.top - 2, BRICK_W - 2, BRICK_H - 2)
        pygame.draw.rect(SCREEN, self.color, inner_rect)
        
class Brick_Collection():
    def __init__(self): 
        self.collection = [[Brick(r * BRICK_W, c * BRICK_H, 6 - c) for r in range(6)] for c in range(6)] 
    
    def update(self):
        for row in self.collection:
            for element in row:
                element.update()
        
class Paddle(): # creates a paddle
    def __init__(self, x, y): # create paddle
        self.rect = pygame.Rect(x, PADDLE_Y, PADDLE_W, PADDLE_H)
        
    def update(self):
        x, y = pygame.mouse.get_pos() # get the users mouse coordinates
        self.rect = pygame.Rect(x - PADDLE_W / 2, self.rect.top, PADDLE_W, PADDLE_H) # the players puck matches their mouses Y axis
        prevent_off_screen(self)
        pygame.draw.rect(SCREEN, WHITE, self)
        
    def middle(self):
        return self.rect.top + (self.rect.height / 2)
        
def prevent_off_screen(paddle):
    if (paddle.rect.left < 0): # prevent from going off screen top
            paddle.rect = pygame.Rect(0, PADDLE_Y, PADDLE_W, PADDLE_H)
            
    if (WIDTH < paddle.rect.right): # prevent from going off screen bottom
        paddle.rect = pygame.Rect(WIDTH - PADDLE_W, PADDLE_Y, PADDLE_W, PADDLE_H)
        
def draw_score(player_wins, comp_wins): # print out the current scores onto the screen
    FONT = pygame.font.SysFont('arial', 30)
    player_wins = FONT.render(str(player_wins), False, WHITE)
    comp_wins = FONT.render(str(comp_wins), False, WHITE)
    
    SCREEN.blit(player_wins, (50,10))
    SCREEN.blit(comp_wins, (WIDTH - 50, 10))

def get_angle(element, puck): # get the angle the puck should make depending on its previous collision
    difference = element.rect.left - puck.rect.left # calculate how close to puck was to the center
    
    if element.middle() < puck.rect.left:
        difference = -difference
    
    # if type(element) == Brick:
    #     difference = -difference
        
    return float(difference/100.0) # the new angle will be relative to how far the puck was from the center. - means the puck was above the center + means the puck was under the center

def check_collision(bricks, puck, player_paddle):
    if pygame.Rect.colliderect(player_paddle.rect, puck.rect): # puck has hit the paddle
        puck.direction = -1 # puck turns up
        puck.angle = get_angle(player_paddle, puck) # new puck X movement
        puck.rect.bottom = puck.rect.bottom + 5
    elif puck.rect.top - 5 < 0: # puck has hit the top of the screen
        puck.direction = 1 # puck turns down
    elif puck.rect.left < 0:
        puck.angle = 2
    elif WIDTH < puck.rect.right:
        puck.angle = -2
    elif HEIGHT < puck.rect.bottom:
        puck.lives -= 1
        if puck.lives > -1:
            puck.reset()         
    else:
        bricks, puck.direction, puck.angle = check_brick_collision(bricks, puck) # check if the puck collided with a brick
            
def check_brick_collision(bricks, puck):
    remove_row = None
    remove = None

    for row in reversed(bricks.collection):
        for element in reversed(row):
            if puck.rect.colliderect(element.rect):
                print("hit")
                if element.health > 0:
                    element.subtract_health()
                else:
                    remove_row = row
                    remove = element
                break
                    
    if remove != None:
        remove_row.remove(remove)
        while puck.rect.colliderect(remove.rect):
            puck.rect.top += 1
        
        return bricks, 1, get_angle(element, puck)
             
    return bricks, puck.direction, puck.angle
        
def check_win(puck):
    if puck.rect.left < 10: 
        return 0, 1
    if WIDTH - 10 < puck.rect.left: 
        return 1, 0
    
    return 0, 0 


def game_loop():
    player_wins = 0
    
    exit = False
    pause = True
    
    frame_cap = 1.0/60
    time_1 = time.perf_counter()
    unprocessed = 0
    
    bricks = Brick_Collection()
    last_brick = bricks.collection[len(bricks.collection) - 1][0]
    puck = Puck(last_brick)
    player_paddle = Paddle(WIDTH/2 - PADDLE_W, PADDLE_H) # create a paddle object for the player
    pygame.font.init()
    
    while not exit:
        can_render = False
        time_2 = time.perf_counter()
        passed = time_2 - time_1
        unprocessed += passed
        time_1 = time_2

        while(unprocessed >= frame_cap):
            unprocessed -= frame_cap
            can_render = True

        if can_render:
            
            pygame.display.update()
            SCREEN.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = True # if the user closes the window close the game
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pause = not pause
            
            check_collision(bricks, puck, player_paddle)
            
            if not pause:
                puck.update()
                player_paddle.update() # update the players paddle to match their mouse
                bricks.update()
                pygame.display.update()
        
game_loop()