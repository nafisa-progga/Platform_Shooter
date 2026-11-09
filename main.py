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


#Load images
#bullet
bullet_img = pygame.image.load("shooter_assets/img/icons/bullet.png").convert_alpha()
#grenade
grenade_img = pygame.image.load("shooter_assets/img/icons/grenade.png").convert_alpha()


# Load ground tile images
img_list = []
tile_path = "shooter_assets/img/tile"
for x in range(len(os.listdir(tile_path))):
    img = pygame.image.load(f"{tile_path}/{x}.png")
    img = pygame.transform.scale(img, (40, 40)) # Adjust tile size if needed
    img_list.append(img)

#define colors
bg = (144, 201, 120)
red = (255, 0, 0)
ground_y = 400

    
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
tile_size = 50

#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

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
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
                
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
        
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction) #self.rect.size[0] is player width
            bullet_group.add(bullet)
            self.ammo -= 1 #reduce ammo
                    
        
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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    
    def update(self):
        #move bullets
        self.rect.x += (self.direction * self.speed)
        
        #check if bullets has gone off screen
        if self.rect.right < 0 or self.rect.left > screen_width:
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
        self.vel_y = -11
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
        
    def update(self):
        self.vel_y += gravity
        dx = self.direction * self.speed
        dy = self.vel_y
        
        #check collision with ground
        if self.rect.bottom + dy > ground_y:
            dy = ground_y - self.rect.bottom
            self.speed = 0
        
        #check collision with screen boundary
        if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
            self.direction *= -1
            dx = self.direction * self.speed #bounce back with the same speed
        
        #update grenade position
        self.rect.x += dx
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
                target.health -= 80
            # Within 2 tile range - medium damage
            elif distance_x < tile_size * 2 and distance_y < tile_size * 2:
                target.health -= 50
            # Within 3 tile range - light damage
            elif distance_x < tile_size * 3 and distance_y < tile_size * 3:
                target.health -= 30
    


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
    


#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
                
    
player = Player("player", 200, 200, 2, 5, 20, 5)
enemy = Player("enemy", 200, 365, 2, 5, 20, 0)
enemy2 = Player("enemy", 400, 365, 2, 5, 20, 0)
enemy_group.add(enemy)
enemy_group.add(enemy2)


run = True
while run:
    
    clock.tick(fps)
    draw_bg()
    
    player.update()
    player.draw()
    
    for enemy in enemy_group:
        enemy.update()
        enemy.draw()
    
    #update and draw groups
    bullet_group.update()
    bullet_group.draw(screen)
    
    grenade_group.update()
    grenade_group.draw(screen)
    
    explosion_group.update()
    explosion_group.draw(screen)
    
    #update player actions
    if player.alive:
        
        #shoot bullets
        if shoot:
            player.shoot()
        #throw grenade
        elif grenade and grenade_thrown == False and player.grenades > 0:
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
        
        player.move(moving_left, moving_right)
    
    
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
                    grenade = True
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
                grenade = False
                grenade_thrown = False

        # Mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and player.alive:  # Left click pressed, # 1 means left mouse button
                shoot = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3 and player.alive:  # Right click pressed, # 3 means right mouse button
                grenade= True
                
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click released
                shoot = False
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Right click released
                grenade = False
                grenade_thrown = False
            
    pygame.display.update()
    
pygame.quit()
