import pygame
import os

pygame.init()

screen_width = 800
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platform Shooter")

#set frame rate
clock = pygame.time.Clock()
fps = 60

#define colors
bg = (144, 201, 120)
red = (255, 0, 0)
ground_y = 400


# Load ground tile images
img_list = []
tile_path = "shooter_assets/img/tile"
for x in range(len(os.listdir(tile_path))):
    img = pygame.image.load(f"{tile_path}/{x}.png")
    img = pygame.transform.scale(img, (40, 40)) # Adjust tile size if needed
    img_list.append(img)
    
#draw background and ground tiles
def draw_bg():
    screen.fill(bg)
    
    # Draw tiled ground using tile 0 and tile 3 across the screen width
    tile_width = img_list[0].get_width()
    for x in range(0, screen_width, tile_width):
        # Top grass layer (tile 0)
        screen.blit(img_list[0], (x, ground_y))
        # Dirt layers underneath (tile 3) spanning down to the bottom of the screen
        for y in range(ground_y + tile_width, screen_height, tile_width):
            screen.blit(img_list[3], (x, y))
    
# define game variables
gravity = 0.75

#define player action variables
moving_left = False
moving_right = False

class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        
        self.alive = True
        
        self.char_type = char_type
        self.speed = speed
        self.y_vel = 0 #velocity in y direction
        self.direction = 1
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
                
        # Animation
        
        #load all images for the players
        animation_types = ["Idle", "Run", "Jump"]
        for animation in animation_types:
            # reest temporary list of images
            temp_list = []
            #count number of files in the folder
            number_of_frames = len(os.listdir(f"shooter_assets/img/{self.char_type}/{animation}"))
            
            for i in range(number_of_frames):
                player_img = pygame.image.load(f"shooter_assets/img/{self.char_type}/{animation}/{i}.png")
                player_img = pygame.transform.scale(player_img, (int(player_img.get_width() * scale), int(player_img.get_height()* scale)))
                temp_list.append(player_img)
            self.animation_list.append(temp_list)
        
            
        self.player_img = self.animation_list[self.action][self.frame_index]
        self.rect = self.player_img.get_rect()
        self.rect.center = (x, y)
    
    def move(self, moving_left, moving_right):
        #reset movement variables
        dx = 0
        dy = 0
        
        #assign movement variables if moving left or right
        if moving_left:
            dx = - self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        
        #jump
        if self.jump == True and self.in_air == False:
            self.y_vel = - 10 # top left point (0,0) and y value increases bellow it. 
            # So, in order to move up/jump, we need to decrease the y value
            self.jump = False
            self.in_air = True
            
        #apply gravity
        self.y_vel += gravity
        if self.y_vel > 10:
            self.y_vel = 10
        dy += self.y_vel
        
        #check collision with ground
        if self.rect.bottom + dy > ground_y:
            dy = ground_y - self.rect.bottom
            self.in_air = False
            
        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy
        
    
    def update_animation(self):
        #update animation
        animation_cooldown = 70
        
        #update image depending on current frame
        self.player_img = self.animation_list[self.action][self.frame_index] 

        #check if the time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            
        #if the animation has run out reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
        

    def update_action(self, new_action):
        #check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self. update_time = pygame.time.get_ticks()
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.player_img, self.flip, False), self.rect)
    
    
player = Player("player", 200, 200, 2, 5)
enemy = Player("enemy", 200, 365, 2, 5)

run = True
while run:
    
    clock.tick(fps)
    draw_bg()
    
    player.update_animation()
    player.draw()
    enemy.draw()
    
    #update player actions
    if player.alive:
        if player.in_air:
            player.update_action(2) #2: jump
        elif moving_left or moving_right:
            player.update_action(1) #1: run
        else:
            player.update_action(0) #0: idle
        
    player.move(moving_left, moving_right)
    
    
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
            
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
                
        #keyboard button release 
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            
    pygame.display.update()
    
    
pygame.quit()
