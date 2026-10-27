import math

import gymnasium as gym
import numpy as np
import pygame

# Kolory
WHITE = (255, 255, 255)
CAR_COLOR = (255, 100, 100)
RED = (200, 0, 0)
YELLOW = (225, 225, 100)

WIDTH, HEIGHT = 800, 600

# Auto
CAR_W, CAR_H = 50, 30
START_X, START_Y = WIDTH // 2 + 50, HEIGHT - 190
MAX_SPEED = 5.0
ROTATION_SPEED = 4

# Radary
SENSOR_OFFSET = math.radians(30)
MAX_RANGE = 300          # maksymalny zasieg radaru w pikselach
DANGER_DIST = 40         # ponizej tej odleglosci linia radaru jest czerwona

MAX_STEPS = 1000         # limit dlugosci epizodu (truncated)


class CarEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, map_path="maps/map1.png", render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        self.map_path = map_path

        # Akcje: [gaz (0/1), kierunek (0=lewo, 1=prosto, 2=prawo)]
        self.action_space = gym.spaces.MultiDiscrete([2, 3])
        # Obserwacje: 3 radary znormalizowane do 0-1
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(3,), dtype=np.float32
        )

        # Mapa wczytana raz jako maska numpy: True = tor (indeks [x, y])
        surface = pygame.image.load(map_path)
        rgb = pygame.surfarray.array3d(surface)
        self.track_mask = rgb[:, :, 1] < 50
        self.track_surface = surface  # do renderowania

        self.screen = None
        self.clock = None
        self._radar_ends = [(START_X, START_Y)] * 3

        self.x = START_X
        self.y = START_Y
        self.angle = 0.0
        self.speed = 0.0
        self.steps = 0

    # ---------- logika ----------
    def is_on_track(self, x, y):
        xi, yi = int(x), int(y)
        if 0 <= xi < WIDTH and 0 <= yi < HEIGHT:
            return bool(self.track_mask[xi, yi])
        return False

    def _radar_distance(self, angle_rad, index):
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)
        dist = 0
        x1, y1 = self.x, self.y
        while dist < MAX_RANGE:
            nx, ny = x1 + dx, y1 + dy
            if not self.is_on_track(nx, ny):
                break
            x1, y1 = nx, ny
            dist += 1
        self._radar_ends[index] = (x1, y1)
        return dist

    def _get_obs(self):
        rad = math.radians(self.angle)
        d = [
            self._radar_distance(rad - SENSOR_OFFSET, 0),
            self._radar_distance(rad, 1),
            self._radar_distance(rad + SENSOR_OFFSET, 2),
        ]
        return (np.array(d, dtype=np.float32) / MAX_RANGE)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.x, self.y = START_X, START_Y
        self.angle = 0.0
        self.speed = 0.0
        self.steps = 0
        return self._get_obs(), {}

    def step(self, action):
        throttle, steer = action

        if throttle == 1:
            self.speed = min(self.speed + 0.1, MAX_SPEED)
        else:
            self.speed *= 0.95

        if steer == 0:
            self.angle -= ROTATION_SPEED
        elif steer == 2:
            self.angle += ROTATION_SPEED

        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)
        self.steps += 1

        terminated = False
        truncated = False

        if not self.is_on_track(self.x, self.y):
            terminated = True
            reward = -100.0
        else:
            reward = 0.1 + self.speed * 0.2

        if self.steps >= MAX_STEPS:
            truncated = True

        obs = self._get_obs()
        return obs, reward, terminated, truncated, {}

    # ---------- renderowanie ----------
    def render(self):
        if self.render_mode != "human":
            return
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Self_Driving_Rectangle")
            self.clock = pygame.time.Clock()
            self.track_surface = self.track_surface.convert()

        pygame.event.pump()
        self.screen.blit(self.track_surface, (0, 0))

        # radary
        for end in self._radar_ends:
            length = math.hypot(end[0] - self.x, end[1] - self.y)
            color = RED if length < DANGER_DIST else YELLOW
            pygame.draw.line(self.screen, color, (self.x, self.y), end, 2)

        # auto
        car_surf = pygame.Surface((CAR_W, CAR_H), pygame.SRCALPHA)
        pygame.draw.rect(car_surf, CAR_COLOR, (0, 0, CAR_W, CAR_H))
        rotated = pygame.transform.rotate(car_surf, -self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        self.screen.blit(rotated, rect.topleft)

        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None


if __name__ == "__main__":
    # Test: losowy agent z podgladem
    env = CarEnv(render_mode="human")
    obs, _ = env.reset(seed=0)
    env.render()  # inicjalizuje pygame i okno
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        obs, reward, terminated, truncated, _ = env.step(env.action_space.sample())
        env.render()
        if terminated or truncated:
            obs, _ = env.reset()
    env.close()