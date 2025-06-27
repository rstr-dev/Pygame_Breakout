import pygame
import time

pygame.init()
pygame.font.init()
pygame.display.set_caption("BREAKOUT DEMO")

SCREEN = pygame.display.set_mode( (1680,900))
# SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
    
WIDTH, HEIGHT = pygame.display.get_surface().get_size()
FONT = pygame.font.SysFont('arial', 50)
SCREEN.fill(BLACK) 

MIDDLE_W = WIDTH / 2
MIDDLE_H = HEIGHT / 2
BRICK_W = WIDTH / 6
BRICK_H = BRICK_W / 5
PADDING = 15

PADDLE_W = WIDTH / 8
PADDLE_H = 20
PADDLE_Y = HEIGHT - (PADDLE_H * 2)

OPTION_WIDTH = 800
OPTION_HEIGHT = 50
INNERBOX_OFFSET = 5

PUCK_S = 50 # width and height of the puck
COMP_SPEED = 1.75
COLORS = 6
LIVES = 5

colors = {0: (204, 153, 255), 1: (157, 154, 255), 2: (154, 255, 195), 3: (255, 255, 154), 4: (255, 222, 154), 5: (255, 154, 154), 6: (0, 0, 0)} # 0 is purple 5 is red. 6 is used for a brick that is about to be deleted

class Puck(): # creates a puck that moves across the screen
    def __init__(self, paddle):
        self.angle = 0.0 # pucks y axis movement
        self.direction = 0 # puck moves up (-1) or down (1)
        self.speed = 10.0 # puck movement speed
        self.lives = LIVES
        
        self.rect = pygame.Rect(paddle.rect.width / 2, paddle.rect.top + 2, PUCK_S, PUCK_S) # creating the rectangle
        
        self.paddle = paddle
        self.free = False
        
    def let_puck_go(self):
        self.free = True
        self.direction = -1
    
    def reset(self):
        self.rect = pygame.Rect(self.paddle.rect.left + (self.paddle.rect.width / 2 - (self.rect.width / 2)), self.paddle.rect.top - self.rect.height - 2, PUCK_S, PUCK_S) # the puck sits on top of the paddle
        self.free = False
        self.angle = 0.0 # pucks y axis movement
        self.direction = 1 # puck moves up (-1) or down (1)
        
    def update(self): # redraw the puck
        if self.free == False:
            self.rect = pygame.Rect(self.paddle.rect.left + (self.paddle.rect.width / 2 - (self.rect.width / 2)), self.paddle.rect.top - self.rect.height - 2, PUCK_S, PUCK_S) # the puck sits on top of the paddle
        else:
            self.rect = pygame.Rect(self.rect.left + self.angle, self.rect.top + (self.direction * self.speed), PUCK_S, PUCK_S) # move according to the direction and angle
        pygame.draw.rect(SCREEN, WHITE, self.rect) # redraw on screen       
        
class Brick():
    def __init__(self, x, y, health): 
        self.rect = pygame.Rect(x, y, BRICK_W, BRICK_H)
        self.health = health
        self.color = colors[COLORS - health]
    
    def update(self):
        rect = pygame.Rect(self.rect.left + 2, self.rect.top - 2, BRICK_W - 2, BRICK_H - 2)
        pygame.draw.rect(SCREEN, self.color, rect)
        
    def collision_check(self, puck):
        if puck.rect.colliderect(self.rect):
            if self.health > 0:
                self.health = self.health - 1
            self.color = colors[COLORS - self.health]
            return True
        return False
        
class Brick_Collection():
    def __init__(self, rows, cols): 
        self.rows = rows
        self.cols = cols
        self.collection = [[Brick(r * BRICK_W, c * BRICK_H, rows - c) for r in range(rows)] for c in range(cols)] 
    
    def reset(self):
        self.collection = [[Brick(r * BRICK_W, c * BRICK_H, self.rows - c) for r in range(self.rows)] for c in range(self.cols)] 
        
    def empty(self):
        for row in self.collection:
            if len(row) > 0:
                return False
        return True     
        
    def collision(self, puck):
        bricks_to_remove = [] # array in case multiple bricks are hit at once
                        
        for row in reversed(self.collection): # moving through the array in reverse as it is most likely for the bricks on the bottom to be hit first- this can save some processing time
            for element in reversed(row):
                if element.collision_check(puck):
                        if 1 > element.health:
                            bricks_to_remove.append([row, element])
                        puck.direction = 1
                        get_angle(element.rect, puck)

        for element in bricks_to_remove:
            element[0].remove(element[1])
                 
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
        
        if (self.rect.left < 0): # prevent from going off screen left
            self.rect = pygame.Rect(0, PADDLE_Y, PADDLE_W, PADDLE_H)
            
        if (WIDTH < self.rect.right): # prevent from going off screen right
            self.rect = pygame.Rect(WIDTH - PADDLE_W, PADDLE_Y, PADDLE_W, PADDLE_H)
            
        pygame.draw.rect(SCREEN, WHITE, self)
    
    def collision(self, puck):
        if self.rect.colliderect(puck.rect):
            collision_rect = pygame.Rect.clip(self.rect, puck.rect)
            get_angle(collision_rect, puck)
            puck.direction = -1
        
def draw_information(player_wins, puck): # print out the current scores onto the screen
    FONT = pygame.font.SysFont("arial", 30)
    player_wins = FONT.render(str(player_wins), False, WHITE)
    lives = FONT.render(str(puck.lives), False, WHITE)
    
    SCREEN.blit(player_wins, (50,10))
    SCREEN.blit(lives, (WIDTH - 50, 10))

def get_angle(collision_rect, puck): # get the angle the puck should make depending on its previous collision
    left_edge_closeness = abs(collision_rect.left - puck.rect.left)
    right_edge_closeness = abs(collision_rect.right - puck.rect.right)
    
    if left_edge_closeness < right_edge_closeness: # puck collided with left edge of paddle
        puck.angle = -((PADDLE_W - left_edge_closeness)/(PADDLE_W / 4))
    elif right_edge_closeness < left_edge_closeness: # puck collided with right edge of paddle
        puck.angle = ((PADDLE_W - right_edge_closeness)/(PADDLE_W / 4))
    else: # puck is center of paddle
        puck.angle = 0 
        
    if puck.direction == 1:
        puck.angle = -puck.angle
        
def check_collision(bricks, puck, player_paddle):   
    if puck.rect.top - 5 < 0: # puck has hit the top of the screen
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
        player_paddle.collision(puck) # check if puck collided with paddle
        bricks.collision(puck) # check if the puck collided with a brick

def show_options(text):
    rect = pygame.Rect(MIDDLE_W - (OPTION_WIDTH / 2) + (INNERBOX_OFFSET / 2), MIDDLE_H - (OPTION_HEIGHT / 2) + (INNERBOX_OFFSET / 2), OPTION_WIDTH - INNERBOX_OFFSET, OPTION_HEIGHT - INNERBOX_OFFSET) # the players puck matches their mouses Y axis
    pygame.draw.rect(SCREEN, BLACK, rect)
    
    text = FONT.render(text, False, WHITE)
    text_rect = text.get_rect(center = (rect.centerx, rect.centery)) # places text in the middle of the square
    SCREEN.blit(text, text_rect)
    
def check_win(puck):
    if puck.rect.left < 10: 
        return 0, 1
    if WIDTH - 10 < puck.rect.left: 
        return 1, 0
    return 0, 0 

def game_loop():
    player_wins = 0
    
    exit = False
    
    frame_cap = 1.0/60
    time_1 = time.perf_counter()
    unprocessed = 0
    
    title = True
    pause = False
    won = False
    
    bricks = Brick_Collection(6,6)
    player_paddle = Paddle(WIDTH/2 - PADDLE_W, PADDLE_H) # create a paddle object for the player
    puck = Puck(player_paddle)
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
            SCREEN.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = True # if the user closes the window close the game
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: 
                        if title:
                            title = False
                        elif won:
                            won = False
                            puck.lives = LIVES
                            bricks.reset()
                        elif pause:
                            pause = False
                        else:
                            pause = True
                    if puck.free == False and event.key == pygame.K_SPACE:
                        puck.let_puck_go()
            
            if title:
                show_options("Press space to return- when in game press return to pause")
            elif pause:
                show_options("Press return to resume")
            elif bricks.empty():
                show_options("You won- press enter to restart")
                player_wins += 1
            elif 0 > puck.lives:
                puck.lives = LIVES
                bricks.reset()
            else: 
                check_collision(bricks, puck, player_paddle)
                player_paddle.update() # update the players paddle to match their mouse
                puck.update()
                bricks.update()
                draw_information(player_wins, puck)
            pygame.display.update()
        
game_loop()