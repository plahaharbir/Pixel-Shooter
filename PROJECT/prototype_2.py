import pygame
from pygame import mixer
import os
import random
import csv

pygame.init()

#PANEL SETTINGS
PANEL_SPAN = 800
PANEL_TALLNESS = int(PANEL_SPAN * 0.8)
panel = pygame.display.set_mode((PANEL_SPAN, PANEL_TALLNESS))
pygame.display.set_caption('Pixel Shooter')

#REFRESH RATE
CLOCK = pygame.time.Clock()
refresh_rate = 60

#WLRD CONSTANTS
GRAVITATIONAL_FORCE = 0.75
PANEL_SHIFT = 280
LAYERS = 16
DIVISIONS = 150
BLOCK_DIMENSION = 40
BLOCK_VARIATION = 20
PEAK_STAGES = 3

#WRLD STATE
camera_offset = 0
canvas_shift = 0
current_stage = 1
stage = 1
game_initiated = False
play_suspended = False

#HERO CONTROLS
D_Left = False
D_Right = False
strike = False
grenade = False
grenade_deployed = False

# IMAGES
# BUTTONS
LAUNCH_BTN = pygame.image.load('BUTTONS/PLAY_BTN.png').convert_alpha()
LEAVE_BTN = pygame.image.load('BUTTONS/EXIT_BTN.png').convert_alpha()
RELAUNCH_BTN = pygame.image.load('BUTTONS/RESTART_BTN.png').convert_alpha()
RESUME_BTN = pygame.image.load('BUTTONS/RESUME_BTN.png').convert_alpha()

# BACKGROUNDS
BACK = pygame.image.load('BACKGROUND/BACK.png').convert_alpha()
MOUNTAINS = pygame.image.load('BACKGROUND/MOUNTAINS.png').convert_alpha()

# TILES
pic_indexes = []
for x in range(BLOCK_VARIATION):
    pic = pygame.image.load(f'TILES/tile{x}.png')
    pic = pygame.transform.scale(pic, (BLOCK_DIMENSION, BLOCK_DIMENSION))
    pic_indexes.append(pic)

# WEAPONS
BULLET_pic = pygame.image.load('ICON/BULLET.png').convert_alpha()
GRENADE_pic = pygame.image.load('ICON/GRENADE.png').convert_alpha()

# LOOT BOXES
vitalitypack_pic = pygame.image.load('ICON/HeathPack.png').convert_alpha()
roundsbox_pic = pygame.image.load('ICON/AmmoBox.png').convert_alpha()
grenadebox_pic = pygame.image.load('ICON/GrenadeBox.png').convert_alpha()
item_boxes = {
    'vitality': vitalitypack_pic,
    'Ammo': roundsbox_pic,
    'Grenade': grenadebox_pic
}

# COLOURS
CANVAS_COLOUR = (144, 201, 120)
RED = (200, 8, 21)
WHITE = (255, 255, 255)
GREEN = (0,110,51)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
PINKISH = (229, 37, 84)
DBLUE = (42, 46, 55)
GREY = (128, 128, 128)


# FONT STYLES
lettering_style = pygame.font.SysFont('FUTURA', 30)  # MAIN FONT FOR TEXT
lettering_style2 = pygame.font.SysFont('FUTURA', 150)  # LARGER FONT FOR HEADINGS

# GAMEPLAY ENTITIES
enemies = pygame.sprite.Group()  # STORES ALL ENEMY OBJECTS
bullets = pygame.sprite.Group()  # HOLDS ALL BULLET OBJECTS
grenades = pygame.sprite.Group()  # MANAGES ALL GRENADE OBJECTS
explosions = pygame.sprite.Group()  # TRACKS ALL EXPLOSION EFFECTS

# INTERACTABLE OBJECTS
collectibles = pygame.sprite.Group()  # HOLDS ITEMS PLAYERS CAN COLLECT
exits = pygame.sprite.Group()  # MANAGES EXIT POINTS IN THE GAME

# ENVIRONMENT OBJECTS
decorations = pygame.sprite.Group()  # STORES DECORATIVE ELEMENTS
aqua = pygame.sprite.Group()  # HOLDS WATER-RELATED OBJECTS

#LEVEL RESET
def Stage_reset():
    # Clear all sprite groups
    groups = [
        enemies, bullets, grenades, explosions, 
        collectibles, decorations, aqua, exits
    ]
    for group in groups:
        group.empty()

    #RESET THE blockS
    data = [[-1] * DIVISIONS for _ in range(LAYERS)]
    
    return data

def Render_scripts(scripts, lettering_style, scripts_col, x, y):
    display_scripts = lettering_style.render(scripts, True, scripts_col)
    panel.blit(display_scripts, (x, y))

def Draw_background():
    panel.fill(CANVAS_COLOUR)
    span = MOUNTAINS.get_width()
    for pos_x in range(5):
        panel.blit(MOUNTAINS, ((pos_x * span) -canvas_shift * 0.65, PANEL_TALLNESS - BACK.get_height() - 150))

class GameButton:
    def __init__(self, pos_x, y, image, scale):
        # INITIALIZE BUTTON ATTRIBUTES
        span = image.get_width()
        tallness = image.get_height()
        self.image = pygame.transform.scale(image, (int(span * scale), int(tallness * scale)))
        self.rect = self.image.get_rect(topleft=(pos_x, y))
        self.activated = False

    def draw(self, surface):
        # FLAG TO TRACK IF BUTTON IS activated
        action = False

        # GET MOUSE POSITION
        mouse_pos = pygame.mouse.get_pos()

        # verify IF MOUSE IS HOVERING OVER BUTTON
        if self.rect.collidepoint(mouse_pos):
            # verify FOR MOUSE CLICK AND PREVENT MULTIPLE TRIGGERS
            if pygame.mouse.get_pressed()[0] == 1 and not self.activated:
                action = True
                self.activated = True

        # RESET CLICK STATE WHEN MOUSE BUTTON IS RELEASED
        if pygame.mouse.get_pressed()[0] == 0:
            self.activated = False

        # DRAW BUTTON ON THE GIVEN SURFACE
        surface.blit(self.image, self.rect.topleft)

        # RETURN TRUE IF BUTTON WAS activated
        return action
    
class Wrld:
    def __init__(self):
        self.solid_blocks = []

    def Load_map(self, layout):
        # SET STAGE WIDTH
        self.stage_length = len(layout[0])

        # ITEM VARIATIONS MAPPING
        item_variations = {16: "Ammo", 17: "Grenade", 18: "vitality"}

        HERO, vitality_indicator = None, None

        # LOOP THROUGH GRID DATA
        for line_iterator, line in enumerate(layout):
            for pillar_iterator, block in enumerate(line):
                if block < 0:
                    continue  # SKIP EMPTY SPACES

                # GET block IMAGE AND POSITION
                image = pic_indexes[block]
                position = (pillar_iterator * BLOCK_DIMENSION, line_iterator * BLOCK_DIMENSION)

                # CLASSIFY block variation
                if 0 <= block <= 8:
                    self.solid_blocks.append((image, image.get_rect(topleft=position)))
                elif 9 <= block <= 10:
                    aqua.add(Water(image, *position))
                elif 11 <= block <= 13:
                    decorations.add(ObjectDecoration(image, *position))
                elif block == 14:
                    HERO = Trooper('player', *position, 1.65, 6, 20, 5)
                    vitality_indicator = VitalityIndicator(10, 10, HERO.current_vitality, HERO.current_vitality)
                elif block == 15:
                    enemies.add(Trooper('enemy', *position, 1.65, 2.5, 50, 0))
                elif block in item_variations:
                    collectibles.add(ElementBox(item_variations[block], *position))
                elif block == 19:
                    exits.add(Next_Stage_Post(image, *position))

        return HERO, vitality_indicator

    def draw(self):
        for pic, rect in self.solid_blocks:
            # APPLY WINDOW SHIFT TO BLOCK POSITION
            rect.x += camera_offset
            # DRAW block ON THE SCREEN
            panel.blit(pic, rect)

class ElementBox(pygame.sprite.Sprite):
    def __init__(self, item_variation, x, y):
        super().__init__()
        self.item_variation = item_variation
        self.image = item_boxes.get(item_variation)  #SAFER LOOKUP OF ITEM
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + BLOCK_DIMENSION // 2, y + (BLOCK_DIMENSION - self.image.get_height()))

    def update(self):
        # REFRESH POSITION BASED ON CAMERA
        self.rect.x += camera_offset
        
        #VERIFY IF CHARACTER INTERACTS WITH BOX
        if self._collides_with_HERO():
            self._pickup_item()
            self.kill()

    def _collides_with_HERO(self):
        return pygame.sprite.collide_rect(self, HERO)

    def _pickup_item(self):
        if self.item_variation == 'vitality':
            self._gain_vitality()
        elif self.item_variation == 'Ammo':
            self._gain_ammo()
        elif self.item_variation == 'Grenade':
            self._gain_grenades()

    def _gain_vitality(self):
        HERO.current_vitality = min(HERO.current_vitality + 25, HERO.peak_vitalitypoints)

    def _gain_ammo(self):
        HERO.rounds += 15

    def _gain_grenades(self):
        HERO.grenades += 5

class ObjectDecoration(pygame.sprite.Sprite):
    def __init__(self, image, position_x, position_y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (position_x + BLOCK_DIMENSION // 2, position_y + (BLOCK_DIMENSION - self.image.get_height()))

    def update(self):
        self.rect.x += camera_offset

class Next_Stage_Post(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (pos_x + BLOCK_DIMENSION // 2, pos_y + (BLOCK_DIMENSION - self.image.get_height()))

    def update(self):
        self.rect.x += camera_offset


class Water(pygame.sprite.Sprite):
    def __init__(self, pic, x, y):
        super().__init__()  # Use `super()` for clarity
        self.image = pic
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + BLOCK_DIMENSION // 2, 
            y + (BLOCK_DIMENSION - self.image.get_height())
        )

    def update(self):
        # APPLY WINDOW SHIFT TO RECTANGLE POSITION
        self.rect.x += camera_offset


class Trooper(pygame.sprite.Sprite):
    def __init__(self, character_variation: str, x: int, y: int, scale: float, velocity: int, rounds: int, grenades: int):
        pygame.sprite.Sprite.__init__(self)
        
        # GENERAL ATTRIBUTES
        self.living = True
        self.character_variation = character_variation 
        
        # vitality AND COMBAT
        self.current_vitality = 100
        self.peak_vitalitypoints = self.current_vitality
        self.rounds = rounds
        self.start_rounds = rounds
        self.grenades = grenades
        self.strike_delay = 0
        
        # POSITIONING AND MOVEMENT
        self.velocity = velocity
        self.course = 1 #1 = RIGHT, -1 = LEFT
        self.dy_velocity = 0
        self.jump = False
        self.airborne = True
        self.turn = False
        
        # AI AND BEHAVIOR
        self.behavior = 0
        self.path_tracker = 0
        self.view = pygame.Rect(0, 0, 250, 20)
        self.inactivity = False
        self.inactivity_ticker = 0
        
        # SET INITIAL IMAGE, RECTANGLE, AND DIMENSIONS
        self.image = pygame.image.load(f'{self.character_variation}/IDLING/animation0.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.span = self.image.get_width()
        self.tallness = self.image.get_height()

    def verify_if_living(self):
        if self.current_vitality <= 0:
            self.living = False
            self.kill()

    def Refresh_strike_delay(self):
        if self.strike_delay > 0:
            self.strike_delay -= 1

    def Refresh(self):
        # vitality, AND strike delay
        self.verify_if_living()
        self.Refresh_strike_delay() 
        
    def movement(self, D_Left, D_Right):
        #RESET MOVE VARIABLES
        camera_offset = 0
        change_x, change_y = 0, 0
        
        #JUMP
        if self.jump and not self.airborne:
            self.dy_velocity = -12
            self.jump = False
            self.airborne = True

        #APPLY GRAVITY
        self.dy_velocity = min(self.dy_velocity + GRAVITATIONAL_FORCE, 10)  # APPLY GRAVITY AND LIMIT FALL VELOCITY
        change_y += self.dy_velocity  # ADD GRAVITY TO VERTICAL MOVEMENT

        #ASSIGN MOVEMENT VARIABLES
        if D_Left:
            change_x = -self.velocity
            self.turn = True
            self.course = -1
        if D_Right : 
            change_x = self.velocity
            self.turn = False
            self.course = 1

        # verify COLLISION WITH BLOCKS
        change_x, change_y = self.verify_collisions(change_x, change_y)

        # HANDLE WATER AND EXIT
        stage_cleared = self.verify_water_and_exit()

        # HERO OFF MAP verify
        if self.rect.bottom > PANEL_TALLNESS:
            self.current_vitality = 0  # HERO FALLS OFF SCREEN AND DIES

        # GAME EDGES
        if self.character_variation == 'player' and (self.rect.left + change_x < 0 or self.rect.right + change_x > PANEL_SPAN):
            change_x = 0  # PREVENT HERO FROM MOVING OUTSIDE THE SCREEN

        # Refresh RECTANGLE POSITION
        self.rect.x += change_x
        self.rect.y += change_y

        # Refresh ROLLING
        camera_offset = self.Refresh_Shift(change_x)  # HANDLE CAMERA ROLLING

        return camera_offset, stage_cleared  # RETURN CAMERA OFFSET AND STAGE STATUS

    def verify_water_and_exit(self):
        # verify IF HERO COLLIDES WITH WATER OR EXIT
        if pygame.sprite.spritecollide(self, aqua, False):
            self.current_vitality = 0  # HERO DIES IN WATER
        if pygame.sprite.spritecollide(self, exits, False):
            return True  # STAGE CLEARED
        return False  # STAGE NOT CLEARED
    
    def verify_collisions(self, change_x, change_y):
        # verify COLLISIONS WITH ENVIRONMENT BLOCKS
        for block in wrld.solid_blocks:
            if block[1].colliderect(self.rect.x + change_x, self.rect.y, self.span, self.tallness):
                change_x = 0  # COLLISION WITH X AXIS
            if block[1].colliderect(self.rect.x, self.rect.y + change_y, self.span, self.tallness):
                if self.dy_velocity < 0:
                    self.dy_velocity = 0  # STOP FALLING
                    change_y = block[1].bottom - self.rect.top  # ADJUST VERTICAL POSITION
                elif self.dy_velocity >= 0:
                    self.dy_velocity = 0  # STOP JUMPING
                    self.airborne = False  # HERO IS ON THE GROUND
                    change_y = block[1].top - self.rect.bottom  # ADJUST VERTICAL POSITION
        return change_x, change_y
    
    def Refresh_Shift(self, change_x):
        camera_offset = 0
        if self.character_variation == 'player':
            # verify IF HERO IS NEAR THE EDGE TO ROLL
            near_right_edge = self.rect.right > PANEL_SPAN - PANEL_SHIFT
            can_shift_right = canvas_shift < (wrld.stage_length * BLOCK_DIMENSION) - PANEL_SPAN
            near_left_edge = self.rect.left < PANEL_SHIFT
            can_ROLL_left = canvas_shift > abs(change_x)

            if (near_right_edge and can_shift_right) or (near_left_edge and can_ROLL_left):
                self.rect.x -= change_x  # MOVE HERO AND ROLL CAMERA
                camera_offset = -change_x  # Refresh CAMERA OFFSET

        return camera_offset

    def Strike(self):
        if self.strike_delay == 0 and self.rounds > 0:
            self.strike_delay = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.course), self.rect.centery, self.course)
            bullets.add(bullet)
            #REDUCING ROUNDS
            self.rounds -= 1

    def Hostiles(self):
        if self.living and HERO.living:
            #IDLE BEHAVIOR: RANDOMLE IDLE
            if not self.inactivity and random.randint(1, 200) == 1:
                self.inactivity = True
                self.inactivity_ticker = 50

            #DETECT HERO AND STRIKE
            if self.view.colliderect(HERO.rect):
                self.Strike()
            else:
                if not self.inactivity:
                    #MOVE OPPS
                    self.movement(self.course == -1, self.course == 1)

                    #PLATFORM EDGE DETECTION
                    edge_vision = pygame.Rect(
                        self.rect.centerx + (self.course * 5),
                        self.rect.bottom,
                        5,
                        10
                    )
                    on_land = False
                    for block in wrld.solid_blocks:
                        if block[1].colliderect(edge_vision):
                            on_land = True
                            break

                    #TURN AROUND IF AT EDGE
                    if not on_land or self.path_tracker > 100:
                        self.course *= -1
                        self.path_tracker = 0

                    #UNDATE VISION IN course OF VIEW
                    self.view.center = (self.rect.centerx + 110 * self.course, self.rect.centery)
                    self.path_tracker += 1
                else:
                    self.inactivity_ticker -= 1 
                    if self.inactivity_ticker <= 0:
                        self.inactivity = False

            #ALLOW AI TO MOVE WITH ROLL
        self.rect.x += camera_offset

    def if_living(self):
        # verify IF HERO IS living AND Refresh STATUS
        if self.current_vitality <= 0:
            self.current_vitality = 0  # HERO IS DEAD
            self.velocity = 0  # STOP MOVEMENT
            self.living = False  # SET HERO STATUS TO DEAD

    def draw(self):
        # DRAW HERO ON SCREEN WITH FLIP FOR course
        panel.blit(pygame.transform.flip(self.image, self.turn, False), self.rect)


class VitalityIndicator():
    def __init__(self, x, y, current_vitality, peak_vitalitypoints):
        self.x = x
        self.y = y
        self.current_vitality = current_vitality
        self.peak_vitalitypoints = peak_vitalitypoints
    
    def draw(self, current_vitality):
        # Refresh vitality indicator
        self.Refresh_vitality(current_vitality)

        # CALCULATE vitality RATIO
        vitalitypoint_ratio = self.calculate_vitality_ratio()

        # DRAW vitality indicator (BORDER, BACKGROUND, AND CURRENT vitality)
        self.draw_border()
        self.draw_background()
        self.draw_vitality(vitalitypoint_ratio)

    def Refresh_vitality(self, current_vitality):
        self.current_vitality = current_vitality

    def calculate_vitality_ratio(self):
        return self.current_vitality / self.peak_vitalitypoints

    def draw_border(self):
        pygame.draw.rect(panel, BLACK, (self.x - 2, self.y - 2, 154, 24))

    def draw_background(self):
        pygame.draw.rect(panel, RED, (self.x, self.y, 150, 20))

    def draw_vitality(self, vitalitypoint_ratio):
        pygame.draw.rect(panel, GREEN, (self.x, self.y, 150 * vitalitypoint_ratio, 20))


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, course):
        pygame.sprite.Sprite.__init__(self)
        self.fuse_timer = 100  # TIME BEFORE EXPLOSION
        self.dy_velocity = -11  # INITIAL VERTICAL VELOCITY (UPWARD)
        self.velocity = 7  # HORIZONTAL VELOCITY
        self.image = GRENADE_pic  # GRENADE IMAGE
        self.rect = self.image.get_rect()  # GRENADE RECTANGLE
        self.rect.center = (x, y)  # SET INITIAL POSITION
        self.span = self.image.get_width()  # GRENADE WIDTH
        self.tallness = self.image.get_height()  # GRENADE HEIGHT
        self.course = course  # DIRECTION (LEFT/RIGHT)
        self.damage_radius = BLOCK_DIMENSION * 2  # DAMAGE RADIUS

    def update(self):
        # APPLY CAMERA OFFSET
        self.rect.x += camera_offset

        # APPLY GRAVITY
        self.dy_velocity += GRAVITATIONAL_FORCE
        change_x = self.course * self.velocity  # HORIZONTAL MOVEMENT
        change_y = self.dy_velocity  # VERTICAL MOVEMENT

        # CHECK COLLISIONS WITH BLOCKS
        for block in wrld.solid_blocks:
            # HORIZONTAL COLLISION
            if block[1].colliderect(self.rect.x + change_x, self.rect.y, self.span, self.tallness):
                self.course *= -1  # REVERSE DIRECTION
                change_x = self.course * self.velocity  # UPDATE HORIZONTAL MOVEMENT
            # VERTICAL COLLISION
            if block[1].colliderect(self.rect.x, self.rect.y + change_y, self.span, self.tallness):
                self.velocity = 0  # STOP HORIZONTAL MOVEMENT
                if self.dy_velocity < 0:
                    self.dy_velocity = 0  # STOP MOVING UP
                    change_y = block[1].bottom - self.rect.top  # ADJUST POSITION
                elif self.dy_velocity >= 0:
                    self.dy_velocity = 0  # STOP MOVING DOWN
                    change_y = block[1].top - self.rect.bottom  # ADJUST POSITION

        # UPDATE POSITION
        self.rect.x += change_x + camera_offset
        self.rect.y += change_y

        # COUNTDOWN TO EXPLOSION
        self.fuse_timer -= 1
        if self.fuse_timer <= 0:
            self.kill()  # REMOVE GRENADE


            # DAMAGE PLAYER IF IN RANGE
            if abs(self.rect.centerx - HERO.rect.centerx) < self.damage_radius and \
                abs(self.rect.centery - HERO.rect.centery) < self.damage_radius:
                HERO.current_vitality -= 50  # REDUCE PLAYER HEALTH

            # DAMAGE ENEMIES IF IN RANGE
            for OPPS in enemies:
                if abs(self.rect.centerx - OPPS.rect.centerx) < self.damage_radius and \
                    abs(self.rect.centery - OPPS.rect.centery) < self.damage_radius:
                    OPPS.current_vitality -= 50  # REDUCE ENEMY HEALTH

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, course):
        pygame.sprite.Sprite.__init__(self)
        self.velocity = 10  # BULLET SPEED
        self.image = BULLET_pic  # BULLET IMAGE
        self.rect = self.image.get_rect()  # BULLET RECTANGLE
        self.rect.center = (x, y)  # SET INITIAL POSITION
        self.course = course  # DIRECTION (LEFT/RIGHT)

    def update(self):
        # MOVE BULLET BASED ON DIRECTION AND CAMERA OFFSET
        self.rect.x += (self.course * self.velocity) + camera_offset

        # CHECK IF BULLET IS OFF SCREEN
        if self.rect.right < 0 or self.rect.left > PANEL_SPAN:
            self.kill()  # REMOVE BULLET

        # CHECK COLLISION WITH LEVEL BLOCKS
        for block in wrld.solid_blocks:
            if block[1].colliderect(self.rect):
                self.kill()  # REMOVE BULLET ON COLLISION

        # CHECK COLLISION WITH PLAYER
        if pygame.sprite.spritecollide(HERO, bullets, False):
            if HERO.living:
                HERO.current_vitality -= 10  # REDUCE PLAYER HEALTH
                self.kill()  # REMOVE BULLET

        # CHECK COLLISION WITH ENEMIES
        for OPPS in enemies:
            if pygame.sprite.spritecollide(OPPS, bullets, False):
                if OPPS.living:
                    OPPS.current_vitality -= 34  # REDUCE ENEMY HEALTH
                    self.kill()  # REMOVE BULLET


# INITIALIZE WORLD DATA WITH DEFAULT VALUES
wrld_data = [[-1] * DIVISIONS for _ in range(LAYERS)]  # CREATE A 2D LIST FOR WORLD DATA

# LOAD LEVEL DATA FROM A CSV FILE
with open(f'level{stage}_data.csv', newline='') as csvfile:
    decoder = csv.reader(csvfile, delimiter=',')  # READ CSV FILE
    for x, layer in enumerate(decoder):           # ITERATE THROUGH EACH LAYER
        for y, block in enumerate(layer):         # ITERATE THROUGH EACH BLOCK IN THE LAYER
            wrld_data[x][y] = int(block)          # STORE BLOCK DATA IN WORLD DATA

# PROCESS WORLD DATA AND CREATE GAME OBJECTS
wrld = Wrld()  # INITIALIZE WORLD OBJECT
HERO, vitalitypoints_indicator = wrld.Load_map(wrld_data)  # LOAD MAP AND GET HERO AND HEALTH INDICATOR

# CREATE MAIN MENU BUTTONS
start_button = GameButton(PANEL_SPAN // 2 - 94, PANEL_TALLNESS // 2 - 100, LAUNCH_BTN, 1)  # START BUTTON
exit_button = GameButton(PANEL_SPAN // 2 - 94, PANEL_TALLNESS // 2 + 150, LEAVE_BTN, 1)    # EXIT BUTTON

# CREATE PAUSE MENU BUTTONS
resume_button = GameButton(PANEL_SPAN // 2 - 150, PANEL_TALLNESS // 2 - 180, RESUME_BTN, 1)  # RESUME BUTTON
pause_restart_button = GameButton(PANEL_SPAN // 2 - 188, PANEL_TALLNESS // 2 - 80, RELAUNCH_BTN, 1)  # RESTART BUTTON
pause_exit_button = GameButton(PANEL_SPAN // 2 - 94, PANEL_TALLNESS // 2 + 47, LEAVE_BTN, 1)  # EXIT BUTTON

# CREATE LEVEL COMPLETE MENU BUTTONS
complete_restart_button = GameButton(PANEL_SPAN // 2 - 440, PANEL_TALLNESS // 2 - 190, RELAUNCH_BTN, 1.5)  # RESTART BUTTON
complete_exit_button = GameButton(PANEL_SPAN // 2 + 95, PANEL_TALLNESS // 2 + 80, LEAVE_BTN, 1.25)  # EXIT BUTTON

# CREATE DEATH SCREEN BUTTONS
death_restart_button = GameButton(PANEL_SPAN // 2 - 300, PANEL_TALLNESS // 2 - 100, RELAUNCH_BTN, 1.5)  # RESTART BUTTON
death_exit_button = GameButton(PANEL_SPAN // 2 - 150, PANEL_TALLNESS // 2 + 100, LEAVE_BTN, 1.5)  # EXIT BUTTON

# MAIN GAME LOOP FLAG
run = True  # SET TO FALSE TO STOP THE GAME
while run:
    CLOCK.tick(refresh_rate)  # CONTROL GAME FRAME RATE

    if game_initiated == False:
        # DRAW START MENU
        panel.fill(PURPLE)
        # DRAW BUTTONS
        if start_button.draw(panel):  # CHECK IF START BUTTON IS CLICKED
            game_initiated = True

        if exit_button.draw(panel):  # CHECK IF EXIT BUTTON IS CLICKED
            run = False
            
        pygame.draw.line(panel, DBLUE, (PANEL_SPAN // 2 - 345, PANEL_TALLNESS // 2 - 195)\
                    , (PANEL_SPAN // 2 + 345, PANEL_TALLNESS // 2 - 195), 10)
        title = Render_scripts('Pixel Shooter', lettering_style2, PINKISH, PANEL_SPAN // 2 - 342.5, PANEL_TALLNESS // 2 - 290)


    elif play_suspended == True:
        # PAUSE MENU LOGIC
        if resume_button.draw(panel):  # CHECK IF RESUME BUTTON IS CLICKED
            play_suspended = False
            
        elif pause_restart_button.draw(panel):  # CHECK IF RESTART BUTTON IS CLICKED
            play_suspended = False
            stage = current_stage
            canvas_shift = 0
            wrld_data = Stage_reset()  # RESET WORLD DATA
            with open(f'level{stage}_data.csv', newline='') as csvfile:
                decoder = csv.reader(csvfile, delimiter=',')
                for x, layer in enumerate(decoder):
                    for y, block in enumerate(layer):
                        wrld_data[x][y] = int(block)  # LOAD LEVEL DATA
            wrld = Wrld()
            HERO, vitalitypoints_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
            
        elif pause_exit_button.draw(panel):  # CHECK IF EXIT BUTTON IS CLICKED
            stage = 1
            current_stage = 1
            game_initiated = False
            play_suspended = False
            canvas_shift = 0
            wrld_data = Stage_reset()  # RESET WORLD DATA
            with open(f'level{stage}_data.csv', newline='') as csvfile:
                        decoder = csv.reader(csvfile, delimiter=',')
                        for x, layer in enumerate(decoder):
                            for y, block in enumerate(layer):
                                wrld_data[x][y] = int(block)  # LOAD NEW LEVEL DATA
            wrld = Wrld()
            HERO, vitality_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
    else:
        # GAME LOGIC
        Draw_background()  # DRAW GAME BACKGROUND
        wrld.draw()  # DRAW WORLD
        vitalitypoints_indicator.draw(HERO.current_vitality)  # DRAW HEALTH INDICATOR

        # DISPLAY AMMO AND GRENADE COUNTS
        Render_scripts('AMMO: ', lettering_style, WHITE, 10, 35)  # DISPLAY AMMO TEXT
        for x in range(HERO.rounds):
            panel.blit(BULLET_pic, (90 + (x * 10), 40))  # DRAW BULLET ICONS
        Render_scripts('GRENADES: ', lettering_style, WHITE, 10, 60)  # DISPLAY GRENADE TEXT
        for x in range(HERO.grenades):
            panel.blit(GRENADE_pic, (135 + (x * 15), 64))  # DRAW GRENADE ICONS

        # UPDATE AND DRAW HERO
        HERO.Refresh()  # UPDATE HERO STATE
        HERO.draw()  # DRAW HERO

        # UPDATE AND DRAW ENEMIES
        for OPPS in enemies:
            OPPS.Hostiles()  # UPDATE ENEMY BEHAVIOR
            OPPS.Refresh()  # UPDATE ENEMY STATE
            OPPS.draw()  # DRAW ENEMY

        # UPDATE AND DRAW SPRITE GROUPS
        bullets.update()  # UPDATE BULLETS
        bullets.draw(panel)  # DRAW BULLETS
        grenades.update()  # UPDATE GRENADES
        grenades.draw(panel)  # DRAW GRENADES
        collectibles.update()  # UPDATE COLLECTIBLES
        collectibles.draw(panel)  # DRAW COLLECTIBLES
        decorations.update()  # UPDATE DECORATIONS
        decorations.draw(panel)  # DRAW DECORATIONS
        aqua.update()  # UPDATE WATER OBJECTS
        aqua.draw(panel)  # DRAW WATER OBJECTS
        exits.update()  # UPDATE EXIT OBJECTS
        exits.draw(panel)  # DRAW EXIT OBJECTS

        # HANDLE HERO ACTIONS
        if HERO.living:
            # SHOOTING
            if strike:
                HERO.Strike()  # HERO SHOOTS

            # GRENADE THROW WITH COOLDOWN
            if grenade and not grenade_deployed and HERO.grenades > 0:
                grenade = Grenade(HERO.rect.centerx + (0.5 * HERO.rect.size[0] * HERO.course), HERO.rect.top, HERO.course)
                grenades.add(grenade)  # ADD GRENADE TO SPRITE GROUP
                HERO.grenades -= 1  # DECREASE GRENADE COUNT
                grenade_deployed = True  # SET GRENADE DEPLOYMENT FLAG

            camera_offset, stage_cleared = HERO.movement(D_Left, D_Right)  # UPDATE HERO MOVEMENT
            canvas_shift -= camera_offset  # UPDATE CAMERA OFFSET

            # CHECK LEVEL COMPLETION
            if stage_cleared:  
                stage += 1    # MOVE TO NEXT LEVEL
                current_stage += 1
                canvas_shift = 0
                wrld_data = Stage_reset()  # RESET WORLD DATA
                if stage <= PEAK_STAGES:
                    with open(f'level{stage}_data.csv', newline='') as csvfile:
                        decoder = csv.reader(csvfile, delimiter=',')
                        for x, layer in enumerate(decoder):
                            for y, block in enumerate(layer):
                                wrld_data[x][y] = int(block)  # LOAD NEW LEVEL DATA
                    wrld = Wrld()
                    HERO, vitalitypoints_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
                    
            elif stage > PEAK_STAGES:
                panel.fill(GREEN)  # DISPLAY LEVEL COMPLETE SCREEN
                
                if complete_restart_button.draw(panel):  # CHECK IF RESTART BUTTON IS CLICKED
                    stage = 1
                    current_stage = 1
                    canvas_shift = 0
                    wrld_data = Stage_reset()  # RESET WORLD DATA
                    with open(f'level{stage}_data.csv', newline='') as csvfile:
                        decoder = csv.reader(csvfile, delimiter=',')
                        for x, layer in enumerate(decoder):
                            for y, block in enumerate(layer):
                                wrld_data[x][y] = int(block)  # LOAD LEVEL DATA
                    wrld = Wrld()
                    HERO, vitalitypoints_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
                    
                elif complete_exit_button.draw(panel):  # CHECK IF EXIT BUTTON IS CLICKED
                    game_initiated = False
                    stage = 1
                    current_stage = 1
                    canvas_shift = 0
                    wrld_data = Stage_reset()  # RESET WORLD DATA
                    with open(f'level{stage}_data.csv', newline='') as csvfile:
                        decoder = csv.reader(csvfile, delimiter=',')
                        for x, layer in enumerate(decoder):
                            for y, block in enumerate(layer):
                                wrld_data[x][y] = int(block)  # LOAD LEVEL DATA
                    wrld = Wrld()
                    HERO, vitalitypoints_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
        else:
            camera_offset = 0
            if death_restart_button.draw(panel):  # CHECK IF RESTART BUTTON IS CLICKED
                stage = current_stage
                canvas_shift = 0
                wrld_data = Stage_reset()  # RESET WORLD DATA
                with open(f'level{stage}_data.csv', newline='') as csvfile:
                    decoder = csv.reader(csvfile, delimiter=',')
                    for x, layer in enumerate(decoder):
                        for y, block in enumerate(layer):
                            wrld_data[x][y] = int(block)  # LOAD LEVEL DATA
                wrld = Wrld()
                HERO, vitalitypoints_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
                
            elif death_exit_button.draw(panel):
                    game_initiated = False
                    camera_offset = 0
                    stage = 1
                    current_stage = 1
                    canvas_shift = 0
                    wrld_data = Stage_reset()  # RESET WORLD DATA
                    with open(f'level{stage}_data.csv', newline='') as csvfile:
                        decoder = csv.reader(csvfile, delimiter=',')
                        for x, layer in enumerate(decoder):
                            for y, block in enumerate(layer):
                                wrld_data[x][y] = int(block)  # LOAD LEVEL DATA
                    wrld = Wrld()
                    HERO, vitality_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP

    # HANDLE EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # CHECK IF WINDOW IS CLOSED
            run = False

        # KEYBOARD INPUTS
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # MOVE LEFT
                D_Left = True
            if event.key == pygame.K_d:  # MOVE RIGHT
                D_Right = True
            if event.key == pygame.K_SPACE:  # SHOOT
                strike = True
            if event.key == pygame.K_q:  # THROW GRENADE
                grenade = True
            if event.key == pygame.K_w and HERO.living:  # JUMP
                HERO.jump = True
            if event.key == pygame.K_ESCAPE and game_initiated == True:  # PAUSE GAME
                play_suspended = True
            if event.key == pygame.K_1:  # DEBUG: EXIT GAME
                run = False

        # KEYBOARD RELEASES
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:  # STOP MOVING LEFT
                D_Left = False
            if event.key == pygame.K_d:  # STOP MOVING RIGHT
                D_Right = False
            if event.key == pygame.K_SPACE:  # STOP SHOOTING
                strike = False
            if event.key == pygame.K_q:  # STOP THROWING GRENADE
                grenade = False
                grenade_deployed = False  # RESET GRENADE DEPLOYMENT FLAG
                
                

    pygame.display.update()  # UPDATE DISPLAY

pygame.quit()  # EXIT PYGAME