import pygame
from pygame import mixer
import os
import random
import csv

mixer.init()
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
begin_shift = False
play_suspended = False

#HERO CONTROLS
Dleft = False
Dright = False
STRIKE = False
GRENADE = False
grenade_deployed = False
grenade_cooldown = 0

# IMAGES
# BUTTONS
LAUNCH_BTN = pygame.image.load('BUTTONS/PLAY_BTN.png').convert_alpha()
LEAVE_BTN = pygame.image.load('BUTTONS/EXIT_BTN.png').convert_alpha()
RELAUNCH_BTN = pygame.image.load('BUTTONS/RESTART_BTN.png').convert_alpha()
RESUME_BTN = pygame.image.load('BUTTONS/RESUME_BTN.png').convert_alpha()

# BACKGROUNDS
BACK = pygame.image.load('BACKGROUND/BACK.png').convert_alpha()
MOUNTAINS = pygame.image.load('BACKGROUND/MOUNTAINS.png').convert_alpha()
SKY4 = pygame.image.load('BACKGROUND/4.png').convert_alpha()
SKY5 = pygame.image.load('BACKGROUND/5.png').convert_alpha()
SKY6 = pygame.image.load('BACKGROUND/6.png').convert_alpha()
main_menu_pic = pygame.image.load('BACKGROUND/Main_Menu_background.png')
death_screen_pic = pygame.image.load('BACKGROUND/death_screen.png')
win_screen = pygame.image.load('background/win_screen.png')

# TILES
pic_indexes = []
for x in range(BLOCK_VARIATION):
    pic = pygame.image.load(f'TILES/tile{x}.png')
    pic = pygame.transform.scale(pic, (BLOCK_DIMENSION, BLOCK_DIMENSION))
    pic_indexes.append(pic)

# WEAPONS
Bullet_pic = pygame.image.load('ICON/BULLET.png').convert_alpha()
Grenade_pic = pygame.image.load('ICON/GRENADE.png').convert_alpha()

# LOOT BOXES
vitalitypack_pic = pygame.image.load('ICON/HeathPack.png').convert_alpha()
roundsbox_pic = pygame.image.load('ICON/AmmoBox.png').convert_alpha()
grenadebox_pic = pygame.image.load('ICON/GrenadeBox.png').convert_alpha()
item_boxes = {
    'vitality': vitalitypack_pic,
    'Ammo': roundsbox_pic,
    'Grenade': grenadebox_pic
}

# AUDIO AND MUSIC
pygame.mixer.music.load('MUSIC/BACKGROUND_MUSIC.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_audio = pygame.mixer.Sound('MUSIC/JUMPING_SOUND.wav')
jump_audio.set_volume(0.25)
striking_audio = pygame.mixer.Sound('MUSIC/GUN_SOUND.wav')
striking_audio.set_volume(0.25)
explosion_audio = pygame.mixer.Sound('MUSIC/EXPLOSION_SOUND.wav')
explosion_audio.set_volume(0.5)
button_audio = pygame.mixer.Sound('MUSIC/CLICK_SOUND.mp3')
button_audio.set_volume(0.5)

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

def Render_scripts(scripts, lettering_style, scripts_col, pos_x, pos_y):
    display_scripts = lettering_style.render(scripts, True, scripts_col)
    panel.blit(display_scripts, (pos_x, pos_y))

def Draw_background():
    panel.fill(CANVAS_COLOUR)
    span = BACK.get_width()
    for pos_x in range(5):
        panel.blit(BACK, ((pos_x * span) -canvas_shift * 0.5, 0))
        panel.blit(MOUNTAINS, ((pos_x * span) -canvas_shift * 0.65, PANEL_TALLNESS - BACK.get_height() - 150))
        panel.blit(SKY4, ((pos_x * span) -canvas_shift * 0.75, PANEL_TALLNESS - BACK.get_height() - 130))
        panel.blit(SKY6, ((pos_x * span) -canvas_shift * 0.95, PANEL_TALLNESS - BACK.get_height() - 110))
        
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
                button_audio.play()  # PLAY CLICK audio

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
                    enemies.add(Trooper('enemy', *position, 1.65, 3, 50, 0))
                elif block in item_variations:
                    collectibles.add(ElementBox(item_variations[block], *position))
                elif block == 19:
                    exits.add(Next_Stage_Post(image, *position))

        return HERO, vitality_indicator

    def draw(self):
        for pic, rect in self.solid_blocks:
            # APPLY WINDOW SHIFT TO block POSITION
            rect.x += camera_offset
            # DRAW block ON THE SCREEN
            panel.blit(pic, rect)

class ElementBox(pygame.sprite.Sprite):
    def __init__(self, item_variation, pos_x, pos_y):
        super().__init__()
        self.item_variation = item_variation
        self.image = item_boxes.get(item_variation)  # Safer lookup of item image
        self.rect = self.image.get_rect()
        self.rect.midtop = (pos_x + BLOCK_DIMENSION // 2, pos_y + (BLOCK_DIMENSION - self.image.get_height()))

    def update(self):
        # Refresh the position based on camera shift
        self.rect.x += camera_offset
        
        # verify if the HERO interacts with the box
        if self._collides_with_hero():
            self._pickup_item()
            self.kill()

    def _collides_with_hero(self):
        return pygame.sprite.collide_rect(self, HERO)

    def _pickup_item(self):
        if self.item_variation == 'vitality':
            self._gain_vitality()
        elif self.item_variation == 'Ammo':
            self._gain_ammunition()
        elif self.item_variation == 'Grenade':
            self._gain_grenades()

    def _gain_vitality(self):
        HERO.current_vitality = min(HERO.current_vitality + 25, HERO.peak_vitalitypoints)

    def _gain_ammunition(self):
        HERO.rounds += 15

    def _gain_grenades(self):
        HERO.grenades += 5

class ObjectDecoration(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (pos_x + BLOCK_DIMENSION // 2, pos_y + (BLOCK_DIMENSION - self.image.get_height()))

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
    def __init__(self, pic, pos_x, pos_y):
        super().__init__()  # Use `super()` for clarity
        self.image = pic
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            pos_x + BLOCK_DIMENSION // 2, 
            pos_y + (BLOCK_DIMENSION - self.image.get_height())
        )

    def update(self):
        # APPLY WINDOW SHIFT TO RECTANGLE POSITION
        self.rect.x += camera_offset

class Transition:
    def __init__(self, course, colour, speed, panel_span, panel_tallness, panel):
        self.course = course
        self.color = colour
        self.velocity = speed
        self.panel_span = panel_span
        self.panel_tallness = panel_tallness
        self.panel = panel
        self.fade_progress = 0

    def Refresh(self):
        self.fade_progress += self.velocity

        if self.course == 1:  #FULL SCREEN FADE
            self._fade_full_panel()
        elif self.course == 2:  #VERICLE FADE
            self._fade_vertical()

        #DETERMINE IF THE FADE IS COMPLETE
        peak_limit = self.panel_span if self.course == 1 else self.panel_tallness
        return self.fade_progress >= peak_limit

    def _fade_full_panel(self):
        #HORIZONTAL FADE RECTANGLES
        left_rect = (0 - self.fade_progress, 0, self.panel_span // 2, self.panel_tallness)
        right_rect = (self.panel_span // 2 + self.fade_progress, 0, self.panel_span, self.panel_tallness)

        #VERTICLE FADE RECTANGLES
        top_rect = (0, 0 - self.fade_progress, self.panel_span, self.panel_tallness // 2)
        bottom_rect = (0, self.panel_tallness // 2 + self.fade_progress, self.panel_span, self.panel_tallness)

        #DRAW ALL FADE RECTANGLES
        pygame.draw.rect(self.panel, self.color, left_rect)
        pygame.draw.rect(self.panel, self.color, right_rect)
        pygame.draw.rect(self.panel, self.color, top_rect)
        pygame.draw.rect(self.panel, self.color, bottom_rect)

    def _fade_vertical(self):
        vertical_rect = (0, 0, self.panel_span, self.fade_progress)
        pygame.draw.rect(self.panel, self.color, vertical_rect)
        

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
        
        # ANIMATION
        self.motions_indexes = []
        self.motions_position = 0
        self.refresh_interval = 20
        
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
        

        # LOAD IMAGES FOR HERO ANIMATIONS
        self.load_animation_motions(scale)

        # SET INITIAL IMAGE, RECTANGLE, AND DIMENSIONS
        self.image = self.motions_indexes[self.behavior][self.motions_position]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.span = self.image.get_width()
        self.tallness = self.image.get_height()

    def load_animation_motions(self, scale):
        sprite_animations = ['IDLING', 'RUNNING', 'JUMPING', 'DEATH']
        for animation in sprite_animations:
            motionsary_indexes = []
            num_of_motions = len(os.listdir(f'{self.character_variation}/{animation}'))

            for i in range(num_of_motions):
                pic = pygame.image.load(f'{self.character_variation}/{animation}/animation{i}.png').convert_alpha()
                pic = pygame.transform.scale(pic, (int(pic.get_width() * scale), int(pic.get_height() * scale)))
                motionsary_indexes.append(pic)

            self.motions_indexes.append(motionsary_indexes)

    def verify_if_living(self):
        if self.current_vitality <= 0:
            self.living = False
            self.behavior = 3

    def Refresh_strike_delay(self):
        if self.strike_delay > 0:
            self.strike_delay -= 1

    def Refresh(self):
        # Refresh ANIMATION, vitality, AND strike delay
        self.refresh_motions()
        self.verify_if_living()
        self.Refresh_strike_delay() 
        
    def movement(self, Dleft, Dright):
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
        if Dleft:
            change_x = -self.velocity
            self.turn = True
            self.course = -1
        if Dright : 
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
            striking_audio.play()

    def Hostiles(self):
        if self.living and HERO.living:
            #IDLE BEHAVIOR: RANDOMLE IDLE
            if not self.inactivity and random.randint(1, 200) == 1:
                self.refresh_motion(0)  #IDLE MOTION
                self.inactivity = True
                self.inactivity_ticker = 50

            #DETECT HERO AND STRIKE
            if self.view.colliderect(HERO.rect):
                self.refresh_motion(0)  #STOIP MOVING TO STRIKE
                self.Strike()
            else:
                if not self.inactivity:
                    #MOVE OPPS
                    self.movement(self.course == -1, self.course == 1)
                    self.refresh_motion(1)  #RUNNING ANIMATION

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

                    #UNDATE VISION IN COURSE OF VIEW
                    self.view.center = (self.rect.centerx + 110 * self.course, self.rect.centery)
                    self.path_tracker += 1
                else:
                    self.inactivity_ticker -= 1 
                    if self.inactivity_ticker <= 0:
                        self.inactivity = False

            #ALLOW AI TO MOVE WITH ROLL
        self.rect.x += camera_offset

    def refresh_motion(self, next_move):
        # IF THE NEW MOVE IS DIFFERENT, Refresh THE ACTION
        if next_move != self.behavior:
            # SWITCH TO THE NEW ACTION
            self.behavior = next_move
            
            # RESET ANIMATION PARAMETERS
            self.motions_position = 0
            self.refresh_interval = pygame.time.get_ticks()
            
    def refresh_motions(self):
        #REFRESH MOTIONS BASED ON TIME
        MOTION_DELAY = 100
        self.image = self.motions_indexes[self.behavior][self.motions_position]

        if pygame.time.get_ticks() - self.refresh_interval > MOTION_DELAY:
            self.refresh_interval = pygame.time.get_ticks()  # RESET ANIMATION fuse_timer
            self.motions_position += 1  # MOVE TO NEXT MOTIONS

        if self.motions_position >= len(self.motions_indexes[self.behavior]):
            if self.behavior == 3:
                self.motions_position = len(self.motions_indexes[self.behavior]) - 1  # STAY ON DEATH ANIMATION
            else:
                self.motions_position = 0  # RESET TO FIRST motions

    def if_living(self):
        # verify IF HERO IS living AND Refresh STATUS
        if self.current_vitality <= 0:
            self.current_vitality = 0  # HERO IS DEAD
            self.velocity = 0  # STOP MOVEMENT
            self.living = False  # SET HERO STATUS TO DEAD
            self.refresh_motion(3)  # SET DEATH ANIMATION

    def draw(self):
        # DRAW HERO ON SCREEN WITH FLIP FOR course
        panel.blit(pygame.transform.flip(self.image, self.turn, False), self.rect)

class VitalityIndicator():
    def __init__(self, x, y, current_vitality, peak_vitalitypoints):
        self.x = x
        self.y = y
        self.current_vitality = current_vitality
        self.peak_vitalitypoints = peak_vitalitypoints
    
    def Update(self, current_vitality):
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
        self.image = Grenade_pic  # GRENADE IMAGE
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
            explosion_audio.play()  # PLAY EXPLOSION SOUND
            explosion = Blast(self.rect.x, self.rect.y)  # CREATE EXPLOSION
            explosions.add(explosion)

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
        self.image = Bullet_pic  # BULLET IMAGE
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

class Blast(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=1, velocity=4, folder="EXPLOSION"):
        super().__init__()
        self.motions = []  # STORE EXPLOSION FRAMES
        self.load_motions(folder, scale)  # LOAD FRAMES FROM FOLDER
        self.motions_index = 0  # CURRENT FRAME INDEX
        self.image = self.motions[self.motions_index]  # SET INITIAL FRAME
        self.rect = self.image.get_rect(center=(x, y))  # SET POSITION
        self.velocity = velocity  # ANIMATION SPEED
        self.ticker = 0  # FRAME COUNTER

    def load_motions(self, folder, scale):
        # LOAD AND SCALE EACH FRAME OF THE EXPLOSION
        for i in range(1, 10):
            pic = pygame.image.load(f"{folder}/{i}.png").convert_alpha()
            pic = pygame.transform.scale(
                pic, (int(pic.get_width() * scale), int(pic.get_height() * scale))
            )
            self.motions.append(pic)

    def update(self):
        # ADJUST POSITION BASED ON CAMERA SHIFT
        self.rect.x += camera_offset

        # UPDATE ANIMATION FRAME
        self.ticker += 1
        if self.ticker >= self.velocity:  # CHECK IF IT'S TIME TO CHANGE FRAME
            self.ticker = 0
            self.motions_index += 1
            if self.motions_index >= len(self.motions):  # CHECK IF ANIMATION IS COMPLETE
                self.kill()  # REMOVE EXPLOSION
            else:
                self.image = self.motions[self.motions_index]  # SWITCH TO NEXT FRAME
                
    
# DEFINE WINDOW TRANSITIONS
transitions = Transition(1, BLACK, 4, PANEL_SPAN, PANEL_TALLNESS, panel)  # GENERAL TRANSITION
death_panel = Transition(2, RED, 4, PANEL_SPAN, PANEL_TALLNESS, panel)    # DEATH SCREEN TRANSITION
win_panel = Transition(2, GREEN, 4, PANEL_SPAN, PANEL_TALLNESS, panel)    # WIN SCREEN

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
HERO, vitality_indicator = wrld.Load_map(wrld_data)  # LOAD MAP AND GET HERO AND HEALTH INDICATOR

# CREATE MAIN MENU BUTTONS
start_button = GameButton(PANEL_SPAN // 2 - 94, PANEL_TALLNESS // 2 - 100, LAUNCH_BTN, 1)  # START BUTTON
exit_button = GameButton(PANEL_SPAN // 2 - 94, PANEL_TALLNESS // 2 + 100, LEAVE_BTN, 1)    # EXIT BUTTON

# CREATE PAUSE MENU BUTTONS
resume_button = GameButton(PANEL_SPAN // 2 - 150, PANEL_TALLNESS // 2 - 180, RESUME_BTN, 1)  # RESUME BUTTON
pause_restart_button = GameButton(PANEL_SPAN // 2 - 188, PANEL_TALLNESS // 2 - 50, RELAUNCH_BTN, 1)  # RESTART BUTTON
pause_exit_button = GameButton(PANEL_SPAN // 2 - 94, PANEL_TALLNESS // 2 + 47, LEAVE_BTN, 1)  # EXIT BUTTON

# CREATE LEVEL COMPLETE MENU BUTTONS
complete_restart_button = GameButton(PANEL_SPAN // 2 - 440, PANEL_TALLNESS // 2 - 190, RELAUNCH_BTN, 1.5)  # RESTART BUTTON
complete_exit_button = GameButton(PANEL_SPAN // 2 + 95, PANEL_TALLNESS // 2 + 80, LEAVE_BTN, 1.25)  # EXIT BUTTON

# CREATE DEATH SCREEN BUTTONS
death_restart_button = GameButton(PANEL_SPAN // 2 - 415, PANEL_TALLNESS // 2 - 100, RELAUNCH_BTN, 1.5)  # RESTART BUTTON
death_exit_button = GameButton(PANEL_SPAN // 2 - 250, PANEL_TALLNESS // 2 + 150, LEAVE_BTN, 1.5)  # EXIT BUTTON

# MAIN GAME LOOP FLAG
run = True  # SET TO FALSE TO STOP THE GAME
while run:
    CLOCK.tick(refresh_rate)  # CONTROL GAME FRAME RATE

    if game_initiated == False:
        # DRAW START MENU
        panel.blit(main_menu_pic, (0, 0))  # DISPLAY MAIN MENU BACKGROUND
        # DRAW BUTTONS
        if start_button.draw(panel):  # CHECK IF START BUTTON IS CLICKED
            game_initiated = True
            begin_shift = True
        if exit_button.draw(panel):  # CHECK IF EXIT BUTTON IS CLICKED
            run = False

    elif play_suspended == True:
        # PAUSE MENU LOGIC
        if resume_button.draw(panel):  # CHECK IF RESUME BUTTON IS CLICKED
            play_suspended = False
        elif pause_restart_button.draw(panel):  # CHECK IF RESTART BUTTON IS CLICKED
            play_suspended = False
            begin_shift = True
            stage = current_stage
            canvas_shift = 0
            wrld_data = Stage_reset()  # RESET WORLD DATA
            with open(f'level{stage}_data.csv', newline='') as csvfile:
                decoder = csv.reader(csvfile, delimiter=',')
                for x, layer in enumerate(decoder):
                    for y, block in enumerate(layer):
                        wrld_data[x][y] = int(block)  # LOAD LEVEL DATA
            wrld = Wrld()
            HERO, vitality_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
            
        elif pause_exit_button.draw(panel):  # CHECK IF EXIT BUTTON IS CLICKED
            stage = 1
            current_stage = 1
            game_initiated = False
            play_suspended = False
            begin_shift = True
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
        vitality_indicator.Update(HERO.current_vitality)  # DRAW HEALTH INDICATOR

        # DISPLAY AMMO AND GRENADE COUNTS
        Render_scripts('AMMO: ', lettering_style, WHITE, 10, 35)  # DISPLAY AMMO TEXT
        for x in range(HERO.rounds):
            panel.blit(Bullet_pic, (90 + (x * 10), 40))  # DRAW BULLET ICONS
        Render_scripts('GRENADES: ', lettering_style, WHITE, 10, 60)  # DISPLAY GRENADE TEXT
        for x in range(HERO.grenades):
            panel.blit(Grenade_pic, (135 + (x * 15), 64))  # DRAW GRENADE ICONS

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
        explosions.update()  # UPDATE EXPLOSIONS
        explosions.draw(panel)  # DRAW EXPLOSIONS
        exits.update()  # UPDATE EXIT OBJECTS
        exits.draw(panel)  # DRAW EXIT OBJECTS

        # INTRO TRANSITION
        if begin_shift == True:
            if transitions.Refresh():  # CHECK IF TRANSITION IS COMPLETE
                begin_shift = False
                transitions.fade_progress = 0  # RESET TRANSITION PROGRESS
            
        # HANDLE HERO ACTIONS
        if HERO.living:
            # SHOOTING
            if STRIKE:
                HERO.Strike()  # HERO SHOOTS

            # GRENADE THROW WITH COOLDOWN
            if GRENADE and not grenade_deployed and HERO.grenades > 0 and grenade_cooldown <= 0:
                grenade = Grenade(HERO.rect.centerx + (0.5 * HERO.rect.size[0] * HERO.course), HERO.rect.top, HERO.course)
                grenades.add(grenade)  # ADD GRENADE TO SPRITE GROUP
                HERO.grenades -= 1  # DECREASE GRENADE COUNT
                grenade_deployed = True  # SET GRENADE DEPLOYMENT FLAG
                grenade_cooldown = 30  # SET COOLDOWN TIMER

            # UPDATE GRENADE COOLDOWN
            if grenade_cooldown > 0:
                grenade_cooldown -= 1  # DECREASE COOLDOWN TIMER

            # HANDLE ANIMATIONS AND MOVEMENT
            if HERO.airborne:
                HERO.refresh_motion(2)  # JUMPING ANIMATION
            elif Dleft or Dright:
                HERO.refresh_motion(1)  # RUNNING ANIMATION
            else:
                HERO.refresh_motion(0)  # IDLE ANIMATION

            camera_offset, stage_cleared = HERO.movement(Dleft, Dright)  # UPDATE HERO MOVEMENT
            canvas_shift -= camera_offset  # UPDATE CAMERA OFFSET
    
            # CHECK LEVEL COMPLETION
            if stage_cleared:
                begin_shift = True
                stage += 1  # MOVE TO NEXT LEVEL
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
                    HERO, vitality_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
            elif stage > PEAK_STAGES:
                if win_panel.Refresh(): # CHECK IF WIN TRANSITION IS COMPLETE
                    panel.blit(win_screen, (0, 0))
                    if complete_restart_button.draw(panel):  # CHECK IF RESTART BUTTON IS CLICKED
                        camera_offset = 0
                        stage = 1
                        current_stage = 1
                        begin_shift = True
                        canvas_shift = 0
                        win_panel.fade_progress = 0
                        wrld_data = Stage_reset()  # RESET WORLD DATA
                        with open(f'level{stage}_data.csv', newline='') as csvfile:
                            decoder = csv.reader(csvfile, delimiter=',')
                            for x, layer in enumerate(decoder):
                                for y, block in enumerate(layer):
                                    wrld_data[x][y] = int(block)  # LOAD LEVEL DATA
                        wrld = Wrld()
                        HERO, vitality_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
                    elif complete_exit_button.draw(panel):  # CHECK IF EXIT BUTTON IS CLICKED
                        game_initiated = False
                        camera_offset = 0
                        stage = 1
                        current_stage = 1
                        death_panel.fade_progress = 0
                        win_panel.fade_progress = 0
                        canvas_shift = 0
                        wrld_data = Stage_reset()  # RESET WORLD DATA
                        with open(f'level{stage}_data.csv', newline='') as csvfile:
                            decoder = csv.reader(csvfile, delimiter=',')
                            for x, layer in enumerate(decoder):
                                for y, block in enumerate(layer):
                                    wrld_data[x][y] = int(block)  # LOAD LEVEL DATA
                        wrld = Wrld()
                        HERO, vitality_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP

        else:
            camera_offset = 0
            if death_panel.Refresh():  # CHECK IF DEATH TRANSITION IS COMPLETE
                panel.blit(death_screen_pic, (0, 0))
                if death_restart_button.draw(panel):  # CHECK IF RESTART BUTTON IS CLICKED
                    stage = current_stage
                    death_panel.fade_progress = 0  
                    win_panel.fade_progress = 0
                    begin_shift = True
                    canvas_shift = 0
                    wrld_data = Stage_reset()  # RESET WORLD DATA
                    with open(f'level{stage}_data.csv', newline='') as csvfile:
                        decoder = csv.reader(csvfile, delimiter=',')
                        for x, layer in enumerate(decoder):
                            for y, block in enumerate(layer):
                                wrld_data[x][y] = int(block)  # LOAD LEVEL DATA
                    wrld = Wrld()
                    HERO, vitality_indicator = wrld.Load_map(wrld_data)  # RELOAD MAP
                elif death_exit_button.draw(panel):
                    game_initiated = False
                    camera_offset = 0
                    stage = 1
                    current_stage = 1
                    death_panel.fade_progress = 0
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
                Dleft = True
            if event.key == pygame.K_d:  # MOVE RIGHT
                Dright = True
            if event.key == pygame.K_SPACE:  #SHOOT
                STRIKE = True
            if event.key == pygame.K_q:  # THROW GRENADE
                GRENADE = True
            if event.key == pygame.K_w and HERO.living:  # JUMP
                HERO.jump = True
                jump_audio.play()  # PLAY JUMP SOUND
            if event.key == pygame.K_ESCAPE and game_initiated == True:  # PAUSE GAME
                play_suspended = True
            if event.key == pygame.K_1:  # DEBUG: EXIT GAME
                run = False

        # KEYBOARD RELEASES
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:  # STOP MOVING LEFT
                Dleft = False
            if event.key == pygame.K_d:  # STOP MOVING RIGHT
                Dright = False
            if event.key == pygame.K_SPACE:  # STOP SHOOTING
                STRIKE = False
            if event.key == pygame.K_q:  # STOP THROWING GRENADE
                GRENADE = False
                grenade_deployed = False  # RESET GRENADE DEPLOYMENT FLAG

    pygame.display.update()  # UPDATE DISPLAY

pygame.quit()  # EXIT PYGAME
