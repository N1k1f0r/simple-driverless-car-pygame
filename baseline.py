import csv
import time

import numpy as np

from car_env import CarEnv


def random_agent(env, obs):
    return env.action_space.sample()


def rule_agent(env, obs, margin=0.05):
    """Gaz zawsze wlaczony, skret w strone radaru z wieksza odlegloscia.

    obs = [lewy, srodkowy, prawy] (znormalizowane 0-1).
    steer: 0 = lewo, 1 = prosto, 2 = prawo.
    """
    left, _, right = obs
    if left > right + margin:
        steer = 0
    elif right > left + margin:
        steer = 2
    else:
        steer = 1
    return np.array([1, steer])


def benchmark(n_steps=100_000):
    """Mierzy szybkosc symulacji (kroki na sekunde) bez okna."""
    env = CarEnv(render_mode=None)
    obs, _ = env.reset(seed=0)
    start = time.perf_counter()
    for _ in range(n_steps):
        obs, r, terminated, truncated, _ = env.step(env.action_space.sample())
        if terminated or truncated:
            obs, _ = env.reset()
    elapsed = time.perf_counter() - start
    print(f"Benchmark: {n_steps} krokow w {elapsed:.2f}s -> {n_steps / elapsed:.0f} krokow/s")


def evaluate(agent_fn, name, n_episodes=100, seed=0):
    """Uruchamia agenta przez n_episodes epizodow i zwraca statystyki."""
    env = CarEnv(render_mode=None)
    rewards, lengths, crashes = [], [], 0
    for ep in range(n_episodes):
        obs, _ = env.reset(seed=seed + ep)
        total, steps = 0.0, 0
        while True:
            action = agent_fn(env, obs)
            obs, r, terminated, truncated, _ = env.step(action)
            total += r
            steps += 1
            if terminated or truncated:
                crashes += int(terminated)
                break
        rewards.append(total)
        lengths.append(steps)

    result = {
        "agent": name,
        "mean_reward": float(np.mean(rewards)),
        "std_reward": float(np.std(rewards)),
        "mean_length": float(np.mean(lengths)),
        "crash_rate": crashes / n_episodes,
    }
    print(
        f"{name:>7}: nagroda {result['mean_reward']:.1f} +/- {result['std_reward']:.1f}, "
        f"dlugosc {result['mean_length']:.0f}, odsetek wypadkow {result['crash_rate']:.0%}"
    )
    return result


if __name__ == "__main__":
    benchmark()

    results = [
        evaluate(random_agent, "random"),
        evaluate(rule_agent, "rule"),
    ]

    with open("baseline_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print("Zapisano baseline_results.csv")