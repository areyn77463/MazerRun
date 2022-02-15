import pygame

#initialize pygame window
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('MazeRun')

#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

#define colors
white = (255, 255, 255)
black = (0, 0, 0)

#game variables
tile_size = 25
game_over = 0

#load images
bg_img = pygame.image.load('resources/images/back_img.png')
restart_img = pygame.image.load('restart.png')

#function to display text on screen by creating picture
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#function for level reset
def reset_level():
    player.reset(150, screen_height - 50)
    exit_group.empty()
    coin_group.empty()
    ladder_group.empty()
    acid_group.empty()

    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image): #coordinates for where button go and switchable image (restart, quit, etc)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos): #check for collision with point rather than rectangle or sprite
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: #0 left mouse 1 middle 2 right
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0: #reset clicked to false
            self.clicked = False

        #draw button
        screen.blit(self.image, self.rect)

        return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        #dx,dy for collision
        dx = 0
        dy = 0
        walk_cooldown = 10 #animation timing
        #col_thresh = 20

        #if game_over != 0 movement stops
        if game_over == 0:
            # get key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -15  # negative moves up | positive moves down
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key [pygame.K_UP] and pygame.sprite.spritecollide(self, ladder_group, False):
                dy -= 5
                self.counter += 1
                self.direction = 2
            if key [pygame.K_DOWN] and pygame.sprite.spritecollide(self, ladder_group, False):
                dy += 5
                self.counter += 1
                self.direction = 2
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False \
                    and key[pygame.K_DOWN] == False and key[pygame.K_UP] == False:
                self.counter = 0
                self.index = 0
                self.image = self.begin_img

            # animations
            # using counter and cooldown to space steps apart
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0  # resetting the counter for no OUT OF BOUNDS
                if self.direction == 1:
                    self.image = self.images_right[self.index]  # setting new character image based on index of list
                if self.direction == -1:
                    self.image = self.images_left[self.index]
                if self.direction == 2:
                    self.image = self.images_climb[self.index]



            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10

            dy += self.vel_y

            # check for collision
            self.in_air = True
            for tile in world.tile_list:
                # check for collision in x-axis
                # colliderect is collision between two rectangles
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                # check for collision in y-axis
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below block or jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0  # so that the character does not stick when bumping head
                        # check if above block or falling/standing
                    elif self.vel_y >= 0:  # elif not if | otherwise you clip through bottom of block
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # door collision
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # ladder collision
            if pygame.sprite.spritecollide(self, ladder_group, False):
                self.vel_y = 0
                self.vel_y -=1
                self.in_air = False

            #acid collision
            if pygame.sprite.spritecollide(self, acid_group, False):
                game_over = -1


            #update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):
        # arrays for animations
        self.images_right = []
        self.images_left = []
        self.images_climb = []
        self.index = 0  # counter for image animation
        self.counter = 0  # to slow the animation

        # beginning image
        begin_img = pygame.image.load('resources/images/player_img.png')
        self.begin_img = pygame.transform.scale(begin_img, (tile_size, tile_size))
        self.image = self.begin_img

        # left and right images
        for num in range(1, 3):
            img_right = pygame.image.load(f'resources/images/step{num}_img.png')  # f {variable} inputs into string
            img_right = pygame.transform.scale(img_right, (tile_size, tile_size))  # resizing character

            # generating mirror image by flip | flip(image, y-axis mirror, x-axis mirror
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        for num in range(1, 3):
            img_climb = pygame.image.load(f'resources/images/climb{num}_img.png')  # f {variable} inputs into string
            img_climb = pygame.transform.scale(img_climb, (tile_size, tile_size))  # resizing character
            self.images_climb.append(img_climb)

        self.rect = self.image.get_rect()  # creates rectangle from image
        # sets x and y of rectangle for image
        self.rect.x = x
        self.rect.y = y

        # width and height for collision
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.vel_y = 0  # velocity variable
        self.jumped = False
        self.direction = 0  # for left, right, up, or down




class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load('resources/images/dirt_img.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size)) # will scale image to size x size
                    img_rect = img.get_rect()  #lookup vid 1
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                if tile == 3:
                    coin = Coin(col_count * tile_size, row_count * tile_size)
                    coin_group.add(coin)
                if tile == 4:
                    ladder = Ladder(col_count * tile_size, row_count * tile_size)
                    ladder_group.add(ladder)
                if tile == 5:
                    acid = Acid(col_count * tile_size, row_count * tile_size + (tile_size // 2))  # // for int
                    acid_group.add(acid)
                col_count += 1
            row_count +=1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


ladder_img = pygame.image.load('resources/images/ladder_img.png')

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        door_img = pygame.image.load('resources/images/door_img.png')
        self.image = pygame.transform.scale(door_img, (int(tile_size * 2), int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        coin_img = pygame.image.load('resources/images/coin_img.png')
        self.image = pygame.transform.scale(coin_img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        #self.rect.center = (x, y) #center of coin  instead of top left corner
        self.rect.x = x
        self.rect.y = y

class Ladder(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        ladder_img = pygame.image.load('resources/images/ladder_img.png')
        self.image = pygame.transform.scale(ladder_img, (tile_size , tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Acid(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        acid_img = pygame.image.load('resources/images/acid_img.png')
        self.image = pygame.transform.scale(acid_img, (tile_size , tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

player = Player (150, screen_height - 50)

#object groups
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
ladder_group = pygame.sprite.Group()
acid_group = pygame.sprite.Group()

world_data = [
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,2,0,3,0,3,0,3,0,3,0,3,0,3,0,3,0,3,0,3,0,3,0,3,0,3,0,3,0,3,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4,1],
[1,3,0,3,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,4,1],
[1,0,3,0,3,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,1,0,0,0,0,0,4,1],
[1,3,0,3,0,3,1,0,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0,0,4,1],
[1,0,3,0,3,0,1,1,1,0,0,0,0,0,0,1,0,0,1,1,0,0,0,1,1,1,0,0,0,0,0,1],
[1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1],
[1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,0,3,0,3,0,1,1,1,1,1,0,0,0,0,0,1],
[1,5,5,5,5,5,1,3,3,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1],
[1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1],
[1,0,0,3,0,3,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1],
[1,4,1,1,1,1,1,1,1,0,0,0,0,0,1,1,0,0,1,1,0,0,0,1,1,1,0,0,0,0,0,1],
[1,4,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,1,1,1,0,0,0,1,1,0,0,0,0,0,1],
[1,4,1,0,0,3,3,3,1,1,0,0,0,0,0,1,0,0,1,1,1,1,0,0,0,1,1,0,0,0,0,1],
[1,4,1,0,0,1,1,1,1,0,0,0,0,0,0,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,0,1],
[1,4,1,3,3,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,1,1,0,0,0,1,1,0,0,1],
[1,4,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,1],
[1,4,1,0,0,3,3,0,0,0,0,0,0,0,0,1,0,0,1,4,1,0,0,0,1,1,0,0,0,0,0,1],
[1,4,1,0,0,1,1,0,0,0,0,0,0,0,0,1,0,0,1,4,1,1,0,0,0,1,1,1,1,1,1,1],
[1,4,1,3,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,4,1,1,1,0,0,0,3,0,3,0,3,1],
[1,4,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,4,1,1,1,1,0,3,0,3,0,3,0,1],
[1,4,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,4,1,1,1,1,1,0,3,0,3,0,3,1],
[1,4,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,4,1,1,1,1,1,1,1,1,1,1,1,1],
[1,4,1,0,1,0,0,1,1,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,4,1,0,1,5,5,5,5,5,5,5,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,4,1,0,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,4,1],
[1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,4,1],
[1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,3,0,3,0,3,0,3,0,3,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

world = World(world_data)

#create buttons
restart_button = Button(screen_width // 2 - 100, screen_height //2 + 100, restart_img)

run = True
while run == True:

    clock.tick(fps)
    screen.blit(bg_img, (0,0))

    world.draw()

    pygame.sprite.spritecollide(player, coin_group, True)

    game_over = player.update(game_over)

    exit_group.draw(screen)
    coin_group.draw(screen)
    ladder_group.draw(screen)
    acid_group.draw(screen)

    # if player dies
    if game_over == -1:
        if restart_button.draw():
            world = reset_level()
            game_over = 0

    # if level completed
    if game_over == 1:
        draw_text('YOU WIN', font, white, (screen_width // 2) - 140, screen_height // 2)
        # restart game
        if restart_button.draw():
            world = reset_level()
            game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()