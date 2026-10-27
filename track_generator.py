import numpy as np
import matplotlib.pyplot as plt

def build_centerline(seed, difficulty, track_width, waves=4, reverse=False):
    rng = np.random.default_rng(seed)

    theta = np.linspace(0, 2 * np.pi, 400, endpoint=False)
    radius_scale = np.ones_like(theta)
    for k in range(1, 10):
        amplitude = 0.1 / k**2
        phase = rng.uniform(0, 2 * np.pi)
        radius_scale += amplitude * np.cos(k * theta + phase)

    x = 400 + 300 * radius_scale * np.cos(theta)
    y = 300 + 200 * radius_scale * np.sin(theta)
    points = np.column_stack([x, y])

    closed = np.vstack([points, points[:1]])
    dx = np.diff(closed[:, 0])
    dy = np.diff(closed[:, 1])
    segment_lengths = np.hypot(dx, dy)

    distance_along = np.concatenate([[0], np.cumsum(segment_lengths)])
    total_length = distance_along[-1]
    n = int(total_length)
    new_distances = np.linspace(0, total_length, n, endpoint=False)

    new_x = np.interp(new_distances, distance_along, closed[:, 0])
    new_y = np.interp(new_distances, distance_along, closed[:, 1])
    centerline = np.column_stack([new_x, new_y])

    tangent = np.roll(centerline, -1, axis=0) - np.roll(centerline, 1, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1, keepdims=True)
    normal = np.column_stack([-tangent[:, 1], tangent[:, 0]])

    n_points = len(centerline)
    s = np.arange(n_points) / n_points
    wave_phase = rng.uniform(0, 2 * np.pi)
    wiggle_amplitude = 0.9 * difficulty * track_width
    offset = wiggle_amplitude * np.sin(2 * np.pi * waves * s + wave_phase)
    centerline = centerline + normal * offset[:, None]

    if reverse:
        centerline = np.vstack([centerline[:1], centerline[1:][::-1]])
    return centerline


def turn_radii(points, step=15):
    tangent = np.roll(points, -1, axis=0) - np.roll(points, 1, axis=0)
    heading = np.arctan2(tangent[:, 1], tangent[:, 0])
    heading_ahead = np.roll(heading, -step)
    turn = (heading_ahead - heading + np.pi) % (2 * np.pi) - np.pi
    return step / np.maximum(np.abs(turn), 1e-9)

def min_turn_radius(points, step=15):
    return turn_radii(points, step).min()


def min_separation(points, width, step=8):
    sample = points[::step]
    m = len(sample)
    idx = np.arange(m)

    dist = np.hypot(sample[:, None, 0] - sample[None, :, 0],
                    sample[:, None, 1] - sample[None, :, 1])

    gap = np.abs(idx[:, None] - idx[None, :])
    gap = np.minimum(gap, m - gap)

    far = gap * step > 3 * width
    return dist[far].min()


def is_track_valid(centerline, track_width, width, height):
    brush_radius = track_width // 2

    radius_ok = min_turn_radius(centerline) >= 0.75 * track_width
    separation_ok = min_separation(centerline, track_width) >= 1.05 * track_width
    fits_ok = (centerline[:, 0].min() >= brush_radius and centerline[:, 0].max() < width - brush_radius
               and centerline[:, 1].min() >= brush_radius and centerline[:, 1].max() < height - brush_radius)

    return radius_ok and separation_ok and fits_ok

def build_mask(centerline, track_width, width, height):
    brush_radius = track_width // 2
    mask = np.zeros((width, height), dtype=bool)

    dx, dy = np.mgrid[-brush_radius:brush_radius + 1, -brush_radius:brush_radius + 1]
    brush = dx**2 + dy**2 <= brush_radius**2

    for cx, cy in centerline:
        ix, iy = int(round(cx)), int(round(cy))
        mask[ix - brush_radius:ix + brush_radius + 1, iy - brush_radius:iy + brush_radius + 1] |= brush
    return mask


def build_arc_length(centerline):
    closed = np.vstack([centerline, centerline[:1]])
    segments = np.hypot(np.diff(closed[:, 0]), np.diff(closed[:, 1]))
    arc_length = np.concatenate([[0], np.cumsum(segments)[:-1]])
    track_length = segments.sum()
    return arc_length, track_length


def build_start(centerline):
    start_pos = centerline[0]
    direction = centerline[1] - centerline[0]
    start_angle = np.degrees(np.arctan2(direction[1], direction[0]))
    return start_pos, start_angle

def generate_valid_centerline(seed, difficulty, track_width=50, width=800, height=600, max_tries=100):
    rng = np.random.default_rng(seed)

    for attempt in range(max_tries):
        attempt_seed = int(rng.integers(0, 2**31))
        reverse = bool(rng.integers(0, 2))

        centerline = build_centerline(attempt_seed, difficulty, track_width, reverse=reverse)
        if is_track_valid(centerline, track_width, width, height):
            return centerline

    raise RuntimeError(f"No valid track for seed={seed}, difficulty={difficulty} after {max_tries} tries")


WIDTH, HEIGHT = 800, 600
track_width = 50
brush_radius = track_width // 2
difficulty = 0.75
waves = 4
seed=2
reverse = True
mask = np.zeros((WIDTH, HEIGHT), dtype=bool)

centerline = generate_valid_centerline(seed, difficulty, track_width)

mask = build_mask(centerline, track_width, WIDTH, HEIGHT)
start_pos, start_angle = build_start(centerline)
arc_length, track_length = build_arc_length(centerline)

# print(len(centerline), len(arc_length), track_length)
# print(arc_length[:5], arc_length[-3:])

def nearest_index(x, y):
    distances = np.hypot(centerline[:, 0] - x, centerline[:, 1] - y)
    return int(np.argmin(distances))

def progress_delta(old_idx, new_idx):
    delta = arc_length[new_idx] - arc_length[old_idx]
    if delta > track_length / 2:
        delta -= track_length
    elif delta < -track_length / 2:
        delta += track_length
    return delta


# print(progress_delta(100, 105))
# print(progress_delta(105, 100))
plt.figure()
plt.imshow(mask.T, cmap="gray")
plt.plot(centerline[:,0],centerline[:,1],"r-",lw=0.6)
plt.arrow(start_pos[0],start_pos[1],40*np.cos(np.radians(start_angle)), 40*np.sin(np.radians(start_angle)),head_width=10,color="green")
plt.show()
