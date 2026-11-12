import pygame
import os
import random
import csv

pygame.init()

screen_width = 800
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platform Shooter")

#set frame rate
clock = pygame.time.Clock()
fps = 60


# define game variables
gravity = 0.75
#tile_size = 50
#ground_y = 400
level = 1
rows = 16
cols = 150
tile_size = screen_height // rows
tile_types = 21
scroll_threshold = 200
screen_scroll = 0
bg_scroll = 0
start_game = False


#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade_button = False
grenade_thrown = False


#Load images

#button images
start_img = pygame.image.load("shooter_assets/img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("shooter_assets/img/exit_btn.png").convert_alpha()
restart_img = pygame.image.load("shooter_assets/img/restart_btn.png").convert_alpha()

# background
pine1_img = pygame.image.load("shooter_assets/img/background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("shooter_assets/img/background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("shooter_assets/img/background/mountain.png").convert_alpha()
sky_img = pygame.image.load("shooter_assets/img/background/sky_cloud.png").convert_alpha()


# world images
# store tiles in a list
img_list = []
for x in range(tile_types):
    img = pygame.image.load(f"shooter_assets/img/tile/{x}.png")
    img = pygame.transform.scale(img, (tile_size, tile_size) )
    img_list.append(img)

#bullet
bullet_img = pygame.image.load("shooter_assets/img/icons/bullet.png").convert_alpha()
#grenade
grenade_img = pygame.image.load("shooter_assets/img/icons/grenade.png").convert_alpha()

#pick up boxes
health_box_image = pygame.image.load("shooter_assets/img/icons/health_box.png").convert_alpha()
health_box_image = pygame.transform.scale(health_box_image, (int(health_box_image.get_width() * 0.75), int(health_box_image.get_height()* 0.75)))

ammo_box_image = pygame.image.load("shooter_assets/img/icons/ammo_box.png").convert_alpha()
ammo_box_image = pygame.transform.scale(ammo_box_image, (int(ammo_box_image.get_width() * 0.75), int(ammo_box_image.get_height()* 0.75)))

grenade_box_image = pygame.image.load("shooter_assets/img/icons/grenade_box.png").convert_alpha()
grenade_box_image = pygame.transform.scale(grenade_box_image, (int(grenade_box_image.get_width() * 0.75), int(grenade_box_image.get_height()* 0.75)))

item_boxes = {
    "Health"  : health_box_image,
    "Ammo"    : ammo_box_image,
    "Grenade" : grenade_box_image
}


# Load ground tile images - temporary
#img_list = []
#tile_path = "shooter_assets/img/tile"
#for x in range(len(os.listdir(tile_path))):
    #img = pygame.image.load(f"{tile_path}/{x}.png")
    #img = pygame.transform.scale(img, (40, 40)) # Adjust tile size if needed
    #img_list.append(img)


#define colors
sage_green = (144, 201, 120)
red = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)

# define font
font = pygame.font.SysFont("Futura", 25)

# draw text on screen
def draw_text(text, font, text_color, x , y):
    img = font.render(text, True, text_color)
    screen.blit( img, (x,y))


    
#draw background
def draw_bg():
    screen.fill(sage_green)
    width = sky_img.get_width()
    for x in range(6):
        screen.blit(sky_img, (( x * width) - bg_scroll * 0.5,  0))
        screen.blit(mountain_img, (( x * width) - bg_scroll * 0.6, screen_height - mountain_img.get_height() - 300 ) )
        screen.blit(pine1_img, (( x * width) - bg_scroll * 0.7, screen_height - pine1_img.get_height() - 150 ) )
        screen.blit(pine2_img, (( x * width) - bg_scroll * 0.8, screen_height - pine2_img.get_height() ) )
    
    
    # Draw tiled ground using tile 0 and tile 3 across the screen width - temporary
    #tile_width = img_list[0].get_width()
    #for x in range(0, screen_width, tile_width):
        # Top grass layer (tile 0)
        #screen.blit(img_list[0], (x, ground_y))
        # Dirt layers underneath (tile 3) spanning down to the bottom of the screen
        #for y in range(ground_y + tile_width, screen_height, tile_width):
            #screen.blit(img_list[3], (x, y))


# function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    
    # create empty tile list - for new level even tough not needed for restart
    data = []
    for row in range(rows):
        r = [-1]*cols
        data.append(r)
    
    return data


class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        
        self.alive = True
        self.health = 100
        self.max_health = self.health
        self.char_type = char_type
        self.speed = speed
        self.shoot_cooldown = 0
        self.ammo = ammo
        self.start_ammo = ammo
        self.grenades = grenades
        self.y_vel = 0 #velocity in y direction
        self.direction = 1
        self.jump = False
        self.in_air = True # pygame norm
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        # npc(enemy) specific varibales
        self.npc_move_counter = 0
        self.npc_idling = False
        self.npc_idling_counter = 0
        self.npc_vision = pygame.Rect(0, 0, 150, 20)
        
        
        # PLayer Action Animation
        
        #load all images for the players
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            # reest temporary list of images
            temp_list = []
            #count number of files in the folder
            number_of_frames = len(os.listdir(f"shooter_assets/img/{self.char_type}/{animation}"))
            
            for i in range(number_of_frames):
                player_img = pygame.image.load(f"shooter_assets/img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                player_img = pygame.transform.scale(player_img, (int(player_img.get_width() * scale), int(player_img.get_height()* scale)))
                temp_list.append(player_img)
            self.animation_list.append(temp_list)
        
        
        self.player_img = self.animation_list[self.action][self.frame_index]
        self.rect = self.player_img.get_rect()
        self.rect.center = (x, y)
        self.width = self.player_img.get_width()
        self.height = self.player_img.get_height()
    
    
    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def move(self, moving_left, moving_right):
        #reset movement variables
        dx = 0
        dy = 0
        screen_scroll = 0 #local variable
        
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
            self.y_vel = - 11 # top left point (0,0) and y value increases bellow it.
            # So, in order to move up/jump, we need to decrease the y value
            self.jump = False
            self.in_air = True
            
        #apply gravity
        self.y_vel += gravity
        if self.y_vel > 10:
            self.y_vel = 10
        dy += self.y_vel
        
        #check collision with ground - temporary
        #if self.rect.bottom + dy > ground_y:
            #dy = ground_y - self.rect.bottom
            #self.in_air = False


        #check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height): # tile[0] -> image, tile[1] -> rectangle
                dx = 0
                
                # if the npc has hit the wall, then make it turn around
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.npc_move_counter = 0
                    
            # check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): # tile[0] -> image, tile[1] -> rectangle
                
                # check if bellow the ground, jumping
                if self.y_vel < 0:
                    self.y_vel = 0
                    dy = tile[1].bottom - self.rect.top
                
                # check if above the ground, falling
                elif self.y_vel >= 0:
                    self.y_vel = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        
        
        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
            
        # check if fallen off the map
        if self.rect.bottom > screen_height:
            self.health = 0
        
        
        # check if going off the edges of the screen
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
                dx = 0
        
        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy
        
        # update scroll based on player position
        if self.char_type == "player":
            if ( self.rect.right > screen_width - scroll_threshold and bg_scroll < ( world.level_length * tile_size) - screen_width) \
                or ( self.rect.left < scroll_threshold and bg_scroll > dx ):
                
                self.rect.x -= dx
                screen_scroll = -dx
                
        #print(screen_scroll)
        return screen_scroll
    
    
    
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery, self.direction) #self.rect.size[0] is player width
            bullet_group.add(bullet)
            self.ammo -= 1 # reduce ammo
    
    
    def move_npcs(self):
        
        if self.alive and player.alive:
            
            if self.npc_idling == False and random.randint(1, 600) == 1: # to prevent increasing idling counter when sitting idle
                self.update_action(0) # 0: idle
                self.npc_idling = True
                self.npc_idling_counter = 200
            
            #check if the enemy is near the player
            if self.npc_vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0) # 0:idle
                #shoot
                self.shoot()
            else:
                if self.npc_idling == False:
                    
                    if self.direction == 1:
                        npc_moving_right = True
                    else:
                        npc_moving_right = False
                    
                    npc_moving_left = not npc_moving_right
                    self.move(npc_moving_left, npc_moving_right)
                    
                    self.update_action(1) # run animation
                    self.npc_move_counter += 1
                    # update npc vision as the enemy moves
                    self.npc_vision.center = (self.rect.centerx + 65 * self.direction, self.rect.centery)
                    
                    if self.npc_move_counter > tile_size:
                        self.direction *= -1
                        self.npc_move_counter *= -1 # multiply by 0, to make npc move within 1/2x space
                        
                else:
                    self.npc_idling_counter -= 1
                    if self.npc_idling_counter <= 0:
                        self.npc_idling = False
        
        # scroll
        self.rect.x += screen_scroll
        
        
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
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
        

    def update_action(self, new_action):
        #check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self. update_time = pygame.time.get_ticks()
            
    def check_alive(self):
        if self.health <=0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.player_img, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []
        
    def process_data(self,data):
        self.level_length = len(data[0]) # coulmn length in the 2d array, lenght of the world
        
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    tile_data = (img, img_rect)
                    
                    # check indivudual tiles
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >=9 and tile <= 10:
                        water = Water(img,  x * tile_size, y * tile_size)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decorations(img,  x * tile_size, y * tile_size)
                        decoration_group.add(decoration)
                    elif tile == 15: # create player
                        player = Player("player", x * tile_size, y * tile_size, 1.85, 5, 20, 5) # parameters: char_type, x, y, scale, speed, ammo, grenades
                        health_bar = HealthBar(80, 10, player.health, player.max_health)
                    elif tile == 16: # create enemy
                        enemy = Player("enemy", x * tile_size, y * tile_size, 1.85, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17: # create ammo box
                        item_box = ItemBox("Ammo",  x * tile_size, y * tile_size)
                        item_box_group.add(item_box)
                    elif tile == 18: # create ammo box
                        item_box = ItemBox("Grenade",  x * tile_size, y * tile_size)
                        item_box_group.add(item_box)
                    elif tile == 19: # create ammo box
                        item_box = ItemBox("Health",  x * tile_size, y * tile_size)
                        item_box_group.add(item_box)
                    elif tile == 20: # create exit ~ next level
                        exit = Exit(img,  x * tile_size, y * tile_size)
                        exit_group.add(exit)
        
        return player, health_bar
    
    
    def draw(self):
        for tile in self.obstacle_list:
            # scroll tiles
            tile[1][0] += screen_scroll #tile[1][0] is rect.x
            screen.blit(tile[0], tile[1]) # draw


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = ( x + tile_size //2, y + (tile_size - self.image.get_height() ) )
        
    def update(self):
        self.rect.x += screen_scroll


class Decorations(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = ( x + tile_size //2, y + (tile_size - self.image.get_height() ) )
    
    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = ( x + tile_size //2, y + (tile_size - self.image.get_height() ) )
        
    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = ( (x + tile_size // 2), ( y + ( tile_size - self.image.get_height() ) ) )
        
        
    def update(self):
        # scroll
        self.rect.x += screen_scroll
        
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            
            #check what kind of box it was
            if self.item_type == "Health":
                player.health += 25
                
                if player.health > player.max_health:
                    player.health = player.max_health
                    
            elif self.item_type == "Ammo":
                player.ammo += 10
                
            elif self.item_type == "Grenade":
                player.grenades += 3
            
            # delete the item box
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
    
    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, black, (self.x -2, self.y -2, 154, 24)) #x, y, width, height
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 5
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    
    def update(self):
        #move bullets
        self.rect.x += (self.direction * self.speed) + screen_scroll
        
        #check if bullets has gone off screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()
        
        # check collision with walls
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect): # no need to specify x or y, looking for collision any direction
                self.kill()
        
        #check collision with characters
        #player
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -=5
                self.kill()
        #enemy
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.speed = 7
        self.vel_y = -9
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction
    
    def update(self):
        self.vel_y += gravity
        dx = self.direction * self.speed
        dy = self.vel_y
        
        #check collision with ground - temporary
        #if self.rect.bottom + dy > ground_y:
            #dy = ground_y - self.rect.bottom
            #self.speed = 0
        
        #check collision with screen boundary - temporary
        #if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
            #self.direction *= -1
            #dx = self.direction * self.speed #bounce back with the same speed
        
        
        # check for collision with walls
        
        for tile in world.obstacle_list:
                        
            # check collision in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
                        
            # check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): # tile[0] -> image, tile[1] -> rectangle
                
                self.speed = 0
                
                # check if bellow the ground, thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                
                # check if above the ground, thrown down
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
        
        
        #update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy
        
        #countdown timer for grenade explosion
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            
            #do damade to anyone nearby
            if player.alive:
                self.deal_damage_to(player)

            for enemy in enemy_group:
                if enemy.alive:
                    self.deal_damage_to(enemy)
    
    
    def deal_damage_to(self, target):
            # Calculate distance in tiles 
            distance_x = abs(self.rect.centerx - target.rect.centerx)
            distance_y = abs(self.rect.centery - target.rect.centery)
            
            # Within 1 tile range - severe damage
            if distance_x < tile_size and distance_y < tile_size:
                target.health -= 100
            # Within 2 tile range - medium damage
            elif distance_x < tile_size * 2 and distance_y < tile_size * 2:
                target.health -= 50
            # Within 3 tile range - light damage
            elif distance_x < tile_size * 3 and distance_y < tile_size * 3:
                target.health -= 25


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        
        #handle explosion images
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f"shooter_assets/img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    
    def update(self):
        
        # scroll
        self.rect.x += screen_scroll
        
        explosion_speed = 3
        
        #update explosion animation
        self.counter += 1
        
        if self.counter >= explosion_speed:
            self.counter = 0
            self.frame_index += 1
            
            #if the animation is complete, then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


# button class
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)) )
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False
        
    def draw(self, surface):
        action = False
        
        # get mouse position
        pos = pygame.mouse.get_pos()
        
        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))
        
        return action


# create buttons
start_button = Button(screen_width // 2 - 130, screen_height // 2 - 150, start_img, 1)
exit_button = Button(screen_width // 2 - 110, screen_height // 2 + 50, exit_img, 1)
restart_button = Button(screen_width // 2 - 100, screen_height // 2 - 50, restart_img, 2)


#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# create instances
# create player & it's instances
#player = Player("player", 200, 200, 1.85, 5, 20, 5) # parameters: char_type, x, y, scale, speed, ammo, grenades
#health_bar = HealthBar(80, 10, player.health, player.max_health)
# create enemy
#enemy = Player("enemy", 300, 365, 1.85, 2, 20, 0)
#enemy2 = Player("enemy", 600, 365, 1.85, 2, 20, 0)
#enemy_group.add(enemy)
#enemy_group.add(enemy2)

# temp = create item boxes
#item_box = ItemBox("Health", 100, 350)
#item_box_group.add(item_box)
#item_box = ItemBox("Ammo", 400, 350)
#item_box_group.add(item_box)
#item_box = ItemBox("Grenade", 500, 350)
#item_box_group.add(item_box)



# create empty tile list
world_data = []
for row in range(rows):
    r = [-1]*cols
    world_data.append(r)

# load in level data and create world
with open(f"shooter_assets/level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)


world = World()
player, health_bar = world.process_data(world_data)


run = True
while run:
    
    clock.tick(fps)
    
    if start_game == False:
        # draw main menu
        screen.fill(sage_green)
        
        #add buttons
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
    
    else:
        
        # draw background
        draw_bg()
            
        #draw world map
        world.draw()
        
        # show health
        draw_text("Health: ", font, black, 10, 10)
        health_bar.draw(player.health)
        
        # calculate health percentage
        health_percentage = int((player.health / player.max_health) * 100)
        draw_text(f"{health_percentage}%", font, white, 245, 10)
        
        # Show ammo
        draw_text("AMMO: ", font, black, 10, 35)
        draw_text(str(player.ammo), font, white, 80, 35)
        for i in range(player.ammo):
            screen.blit(bullet_img, (130 + (i * 10), 40))
        
        # Show grenades 
        draw_text("Grenades: ", font, black, 10, 60)
        draw_text(str(player.grenades), font, white, 110, 60)
        for i in range(player.grenades):
            screen.blit(grenade_img, (150 + (i * 15), 60))

        
        player.update()
        player.draw()
        
        for enemy in enemy_group:
            enemy.move_npcs()
            enemy.update()
            enemy.draw()
        
        #update and draw groups
        bullet_group.update()
        bullet_group.draw(screen)
        
        grenade_group.update()
        grenade_group.draw(screen)
        
        explosion_group.update()
        explosion_group.draw(screen)
        
        item_box_group.update()
        item_box_group.draw(screen)
        
        water_group.update()
        water_group.draw(screen)
        
        decoration_group.update()
        decoration_group.draw(screen)
        
        exit_group.update()
        exit_group.draw(screen)


        #update player actions
        if player.alive:
            
            #shoot bullets
            if shoot:
                player.shoot()
            #throw grenade
            elif grenade_button and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                            player.rect.top, player.direction)
                grenade_group.add(grenade)
                #reduce grenades
                player.grenades -= 1
                grenade_thrown = True
            
            #player action state update - idle, run, jump
            if player.in_air:
                player.update_action(2) #2: jump
            elif moving_left or moving_right:
                player.update_action(1) #1: run
            else:
                player.update_action(0) #0: idle
            
            screen_scroll = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            
            #print(screen_scroll)
            
        else:  # player not alive, died
            screen_scroll = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                
                # load in level data and create world
                with open(f"shooter_assets/level{level}_data.csv", newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                
                world = World()
                player, health_bar = world.process_data(world_data)
    
    
    for event in pygame.event.get():
        # Quit game
        if event.type == pygame.QUIT:
            run = False
            
        # Keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                if player.alive:
                    player.jump = True
            if event.key == pygame.K_e:
                if player.alive:
                    shoot = True
            if event.key == pygame.K_q:
                if player.alive:
                    grenade_button = True
            if event.key == pygame.K_ESCAPE:
                run = False
                
        # Keyboard button release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_e:
                shoot = False
            if event.key == pygame.K_q:
                grenade_button = False
                grenade_thrown = False


        # Mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and player.alive:  # Left click pressed, # 1 means left mouse button
                shoot = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3 and player.alive:  # Right click pressed, # 3 means right mouse button
                grenade_button = True
                grenade_thrown = False
                
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click released
                shoot = False
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Right click released
                grenade_button = False
                grenade_thrown = False
            
    pygame.display.update()
    
pygame.quit()
