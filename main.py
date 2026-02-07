import math

import pygame


def get_distance_to_wall(x, y, angle_rad):
    distances = []

    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # 1. Sprawdzamy pionowe ściany (X)
    if cos_a > 0:  # Patrzymy w prawo
        distances.append((WIDTH - x) / cos_a)
    elif cos_a < 0:  # Patrzymy w lewo
        distances.append(-x / cos_a)

    # 2. Sprawdzamy poziome ściany (Y)
    if sin_a > 0:  # Patrzymy w dół
        distances.append((HEIGHT - y) / sin_a)
    elif sin_a < 0:  # Patrzymy w górę
        distances.append(-y / sin_a)

    # Wynikiem jest najmniejsza z dodatnich odległości
    return min(distances) if distances else 0



WIDTH,HEIGHT = 800,600
pygame.init()
screen=pygame.display.set_caption("Self_Driving_Rectangle")
screen = pygame.display.set_mode((WIDTH,HEIGHT))

#Koordynaty Squere
car_width,car_height = 50,30
x = WIDTH//2
y = HEIGHT//2
speed =0
max_speed=5
angle=0
rotation_speed=4
sensor_data=[]

#Kolory
WHITE = (255,255,255)
BLACK = (30,30,30)
RED = (255,100,100)
YELLOW = (225,225,100)

clock=pygame.time.Clock()
running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # fill the screen with a color to wipe away anything from last frame


    # RENDER YOUR GAME HERE
    keys=pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        angle-=rotation_speed
    if keys[pygame.K_RIGHT]:
        angle+=rotation_speed
    if keys[pygame.K_UP]:
        speed=min(speed+0.1,max_speed)
    elif keys[pygame.K_DOWN]:
        speed=max(speed-0.1,-max_speed//2)
    else:
        speed*=0.95
    radians=math.radians(angle)
    x+=speed*math.cos(radians)
    y+=speed*math.sin(radians)
    screen.fill(BLACK)
    car =pygame.Surface((car_width,car_height),pygame.SRCALPHA)
    pygame.draw.rect(car,RED,(0,0,50,30))
    rotated_car=pygame.transform.rotate(car,-angle)
    rect=rotated_car.get_rect(center=(x,y))
    screen.blit(rotated_car,rect.topleft)

    #radar
    offset=math.radians(30)
    radar1_x=x+math.cos(radians)*150
    radar1_y=y+math.sin(radians)*150
    radar2_x=x+math.cos(radians-offset)*150
    radar2_y=y+math.sin(radians-offset)*150
    radar3_x=x+math.cos(radians+offset)*150
    radar3_y=y+math.sin(radians+offset)*150
    pygame.draw.line(screen,YELLOW,(x,y),(radar1_x,radar1_y),4)
    pygame.draw.line(screen,YELLOW,(x,y),(radar2_x,radar2_y),4)
    pygame.draw.line(screen,YELLOW,(x,y),(radar3_x,radar3_y),4)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()