import math
import gymnasium as gym
import numpy as np

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

        observation = self._get_obs()
        return observation, {}

    def isOnTrack(self, x, y):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            if self.track_surface.get_at((int(x), int(y)))[1] < 50:
                return True
        return False

    def getLength(self, x1, y1):
        l = (self.x - x1) ** 2 + (self.y - y1) ** 2
        return math.sqrt(l)

    def get_radar_distance(self, angle_rad, accuracy=1, max_steps=300):
        dx = math.cos(angle_rad) * accuracy
        dy = math.sin(angle_rad) * accuracy
        x1 = self.x + dx
        y1 = self.y + dy
        steps = 0
        color = YELLOW
        while self.isOnTrack(x1, y1) and steps < max_steps:
            x1 += dx
            y1 += dy
            steps+=1
        l = self.getLength(x1, y1)
        if l < 40:
            color = RED
        pygame.draw.line(self.screen, color, (self.x, self.y), (x1, y1), 2)
        return self.getLength(x1, y1)
    def _get_obs(self):
        rad=math.radians(self.angle)
        return np.array([
            self.get_radar_distance(rad-offset),
            self.get_radar_distance(rad),
            self.get_radar_distance(rad+offset)
        ],dtype=np.float32)
    def step(self, action):
        throttle,steer=action
        if throttle==1:
            self.speed=min(self.speed+0.1,max_speed)
        else:
            self.speed*=0.95

        if steer==0:
            self.angle-=rotation_speed
        elif steer==2:
            self.angle+=rotation_speed

        rad=math.radians(self.angle)
        self.x+=self.speed*math.cos(rad)
        self.y+=self.speed*math.sin(rad)

        terminated=False
        reward=0.1

        if not self.isOnTrack(self.x,self.y):
            terminated=True
            reward=-100
        else:
            reward+=self.speed*0.2

        observation = self._get_obs()
        return observation,reward,terminated,False,{}

    def render(self):
        self.screen.blit(self.track_surface,(0,0))
        car_surf = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
        pygame.draw.rect(car_surf, CAR_COLOR, (0, 0, 50, 30))
        rotated_car = pygame.transform.rotate(car_surf, -self.angle)
        rect = rotated_car.get_rect(center=(self.x, self.y))

        self._get_obs()
        self.screen.blit(rotated_car,rect.topleft)
        pygame.display.flip()
        self.clock.tick(60)

#Uruchomienie
env=CarEnv()
obs,info=env.reset()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    action = env.action_space.sample()

    obs, reward, terminated, truncated, info = env.step(action)
    env.render()

    if terminated:
        env.reset()
pygame.quit()