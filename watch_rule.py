import pygame
from car_env import CarEnv
from baseline import rule_agent

env = CarEnv(render_mode="human")
obs, _ = env.reset(seed=0)
env.render()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            raise SystemExit
    obs, r, term, trunc, _ = env.step(rule_agent(env, obs))
    env.render()
    if term or trunc:
        obs, _ = env.reset()