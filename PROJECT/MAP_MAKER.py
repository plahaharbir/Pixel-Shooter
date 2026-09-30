import pygame
import button
import csv


pygame.init()

clock = pygame.time.Clock()
FPS = 60

#GAME WINDOW
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('level Editor')


#CODE FLEXIBLES
lines = 16
peak_COLS = 150
block_SIZE = SCREEN_HEIGHT // lines
TYLE_variationS = 20
level = 0
current_block = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

#LOAD IMAGES
BACK = pygame.image.load ('BACKGROUND/BACK.png').convert_alpha()
MOUNTAINS = pygame.image.load ('BACKGROUND/MOUNTAINS.png').convert_alpha()
SKY4 = pygame.image.load ('BACKGROUND/4.png').convert_alpha()
SKY5 = pygame.image.load ('BACKGROUND/5.png').convert_alpha()
SKY6 = pygame.image.load ('BACKGROUND/6.png').convert_alpha()



#PUSH blockS ONTO indexes
pic_indexes = []
for x in range(TYLE_variationS):
    pic = pygame.image.load(f'TILES/tile{x}.png').convert_alpha()
    pic = pygame.transform.scale(pic, (block_SIZE, block_SIZE))
    pic_indexes.append(pic)


save_pic = pygame.image.load('BUTTONS/SAVE_BTN.png').convert_alpha()
load_pic = pygame.image.load('BUTTONS/LOAD_BTN.png').convert_alpha()

#DEF COLOURS
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

#lettering_style
lettering_style = pygame.font.SysFont('Futura', 30)

#EMPTY block indexes
wrld_data = []
for line in range(lines):
    r = [-1] * peak_COLS
    wrld_data.append(r)

#CREATE BOTTOM
for block in range(0, peak_COLS):
    wrld_data[lines -1][block] = 0

print(wrld_data)
#DRAWING BACKGROUND
def draw_CANVAS_COLOUR():
    screen.fill(GREEN)
    width = BACK.get_width()
    for x in range(5):
        screen.blit(BACK, ((x * width) -scroll * 0.5, 0))
        screen.blit(MOUNTAINS, ((x * width) -scroll * 0.65, SCREEN_HEIGHT - BACK.get_height() - 150))
        screen.blit(SKY4, ((x * width) -scroll * 0.75, SCREEN_HEIGHT - BACK.get_height() - 130))
        screen.blit(SKY5, ((x * width) -scroll * 0.85, SCREEN_HEIGHT - BACK.get_height() - 120))
        screen.blit(SKY6, ((x * width) -scroll * 0.95, SCREEN_HEIGHT - BACK.get_height() - 110))

#DRAW GRID
def draw_grid():
    #VERTICLE LINES
    for c in range(peak_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * block_SIZE -scroll, 0), (c * block_SIZE -scroll, SCREEN_HEIGHT))
    #HORIZONTAL LINES
    for c in range(peak_COLS + 1):
        pygame.draw.line(screen, WHITE, (0, c * block_SIZE), (SCREEN_WIDTH, c * block_SIZE))


#DRAWING WRLD blockS
def draw_wrld():
    for y, line in enumerate(wrld_data):
        for x, block in enumerate(line):
            if block >= 0:
                screen.blit(pic_indexes[block], (x * block_SIZE -scroll, y * block_SIZE))


#OUTPUT scrips
def draw_scrips(scrips, lettering_style, scrips_col, x, y):
    pic = lettering_style.render(scrips, True, scrips_col)
    screen.blit(pic, (x, y))

#CREATE BUTTONS
save_button = button.Button(SCREEN_WIDTH // 2 + 25, SCREEN_HEIGHT + LOWER_MARGIN - 65, save_pic, 0.20)
load_button = button.Button(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT + LOWER_MARGIN - 65, load_pic, 0.20)

#BUTTON indexes
button_indexes = []
button_col = 0
button_line = 0
for i in range(len(pic_indexes)):
    block_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_line + 50, pic_indexes[i], 1)
    button_indexes.append(block_button)
    button_col += 1
    if button_col == 3:
        button_line += 1
        button_col = 0



run = True
while run:

    clock.tick(FPS)

    draw_CANVAS_COLOUR()
    draw_grid() 
    draw_wrld()
    
    #DRAW block PANELS AND blockS
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))
    pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT, SCREEN_WIDTH, 200))

    draw_scrips(f'level : {level}', lettering_style, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_scrips('Press UP or DOWN to change level', lettering_style, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

    #LOAD/SAVE DATA
    if save_button.draw(screen):
        with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            for line in wrld_data:
                writer.writerow(line)

    if load_button.draw(screen):
        #LOAD LEVEL DATA
        #RESET SCROLL TO START
        scroll = 0
        with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter = ',')
            for x, line in enumerate(reader):
                for y, block in enumerate(line):
                    wrld_data[x][y] = int(block)


    #CHOOSE blockS
    button_count = 0
    for button_count, i in enumerate(button_indexes):
        if i.draw(screen):
            current_block = button_count

    #SELECTED block IS HIGHLITED
    pygame.draw.rect(screen, RED, button_indexes[current_block].rect, 3)

    #MAP SCROLL
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True and scroll < (peak_COLS * block_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed


    #ADD blockS TO SCREEN
    #GET MOUSE POS
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // block_SIZE
    y = pos[1] // block_SIZE

    #verify MOUSE IS BETWEEN block AREA
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        #Refresh block VALUSE
        if pygame.mouse.get_pressed()[0] == 1:
            if wrld_data[y][x] != current_block:
                wrld_data[y][x] = current_block
        if pygame.mouse.get_pressed()[2] == 1:
            wrld_data[y][x] = -1


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #KEYBOARD PRESSES
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1

            

    pygame.display.update()

pygame.quit()
