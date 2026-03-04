import math
import gymnasium as gym

import pygame
#Kolory
WHITE = (255,255,255)
BLACK = (30,30,30)
CAR_COLOR=(255,100,100)
RED = (200,0,0)
YELLOW = (225,225,100)

WIDTH,HEIGHT = 800,600

#Koordynaty Car
car_width,car_height = 50,30
start_x = WIDTH//2+50
start_y = 600-190
x,y=start_x,start_y
speed =0
max_speed=5
angle=0
rotation_speed=4
sensor_data=[]
offset = math.radians(30)

class CarEnv(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.MultiDiscrete([2, 3])  # 2 stany gazu i 3 stany kierunku
        self.observation_space = gym.spaces.Box(low=0, high=100, shape=(3,), dtype=float)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Self_Driving_Rectangle")
        self.track_surface = pygame.image.load("maps/map1.png").convert()
        self.clock=pygame.time.Clock()
        self.reset()
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.x,self.y=start_x,start_y
        self.angle=0
        self.speed=0

    def isOnTrack(self, x, y):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            if self.track_surface.get_at((int(x), int(y)))[1] < 50:
                return True
        return False

    def get_radar_distance(self,x, y, angle_rad, accurcy=1, max_steps=100):
        def getLength(x, y, x1, y1):
            l = (x - x1) ** 2 + (y - y1) ** 2
            return math.sqrt(l)
        dx = math.cos(angle_rad) * accurcy
        dy = math.sin(angle_rad) * accurcy
        x1 = x + dx
        y1 = y + dy
        steps = 0
        color = YELLOW
        while self.isOnTrack(x1, y1) and steps < max_steps:
            x1 += dx
            y1 += dy
            steps+=1
        l = getLength(x, y, x1, y1)
        if l < 40:
            color = RED
        pygame.draw.line(self.screen, color, (x, y), (x1, y1), 2)
        return getLength(x, y, x1, y1)

















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
    if isOnTrack(x,y):
        car =pygame.Surface((car_width,car_height),pygame.SRCALPHA)
        pygame.draw.rect(car,CAR_COLOR,(0,0,50,30))
        rotated_car=pygame.transform.rotate(car,-angle)
        rect=rotated_car.get_rect(center=(x,y))
        screen.blit(rotated_car,rect.topleft)
        print(get_radar_distance(x,y,radians-offset),
        get_radar_distance(x,y,radians),
        get_radar_distance(x,y,radians+offset))
    else:
        reset()


    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()