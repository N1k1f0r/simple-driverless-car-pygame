import math

import pygame
#Kolory
WHITE = (255,255,255)
BLACK = (30,30,30)
RED = (255,100,100)
YELLOW = (225,225,100)

WIDTH,HEIGHT = 800,600
pygame.init()
screen=pygame.display.set_caption("Self_Driving_Rectangle")
screen = pygame.display.set_mode((WIDTH,HEIGHT))
track_surface=pygame.image.load("maps/map1.png").convert()

def isOnTrack(x,y):
    if 0<=x<WIDTH and 0<=y<HEIGHT:
        if track_surface.get_at((int(x),int(y)))[1]<50:
            print(track_surface.get_at((int(x),int(y))))
            return True
    return False

def getLength(x,y,x1,y1):
    l=(x-x1)**2+(y-y1)**2
    return math.sqrt(l)



def get_radar_distance(x, y, angle_rad,accurcy=1,max_steps=100):
    dx=math.cos(angle_rad)*accurcy
    dy=math.sin(angle_rad)*accurcy
    x1=x+dx
    y1=y+dy
    steps=0
    while isOnTrack(x1,y1) and steps<max_steps:
        x1+=dx
        y1+=dy
    pygame.draw.line(screen,YELLOW,(x,y),(x1,y1),2)
    return getLength(x,y,x1,y1)




#Koordynaty Car
car_width,car_height = 50,30
x = WIDTH//2
y = HEIGHT//2
speed =0
max_speed=5
angle=0
rotation_speed=4
sensor_data=[]



clock=pygame.time.Clock()
running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        
    screen.blit(track_surface,(0,0))
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
    #screen.fill(BLACK)
    car =pygame.Surface((car_width,car_height),pygame.SRCALPHA)
    pygame.draw.rect(car,RED,(0,0,50,30))
    rotated_car=pygame.transform.rotate(car,-angle)
    rect=rotated_car.get_rect(center=(x,y))
    screen.blit(rotated_car,rect.topleft)

    #radar
    offset=math.radians(30)
    # radar1_x=x+math.cos(radians)*150
    # radar1_y=y+math.sin(radians)*150
    # radar2_x=x+math.cos(radians-offset)*150
    # radar2_y=y+math.sin(radians-offset)*150
    # radar3_x=x+math.cos(radians+offset)*150
    # radar3_y=y+math.sin(radians+offset)*150
    get_radar_distance(x,y,radians-offset)
    get_radar_distance(x,y,radians)
    get_radar_distance(x,y,radians+offset)
    # pygame.draw.line(screen,YELLOW,(x,y),(radar1_x,radar1_y),4)
    # pygame.draw.line(screen,YELLOW,(x,y),(radar2_x,radar2_y),4)
    # pygame.draw.line(screen,YELLOW,(x,y),(radar3_x,radar3_y),4)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()