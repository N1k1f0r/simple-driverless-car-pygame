import numpy as np
import matplotlib.pyplot as plt

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

WIDTH, HEIGHT = 800, 600
track_width = 70
difficulty = 0.75
waves = 4
reverse = True
mask = np.zeros((WIDTH, HEIGHT), dtype=bool)

rng = np.random.default_rng(seed=1)

theta = np.linspace(0, 2*np.pi,400, endpoint =False)

radius_scale=np.ones_like(theta)
for k in range(1,10):
    amplitude = 0.1/k**2
    phase = rng.uniform(0,2*np.pi)
    radius_scale+=amplitude*np.cos(k*theta+phase)

x=400+300*radius_scale*np.cos(theta)
y=300+200*radius_scale*np.sin(theta)
points = np.column_stack([x, y])

closed = np.vstack([points, points[:1]])

dx = np.diff(closed[:, 0])
dy = np.diff(closed[:, 1])
segment_lengths = np.hypot(dx, dy)

distance_along = np.concatenate([[0], np.cumsum(segment_lengths)])
total_length = distance_along[-1]
n=int(total_length)
new_distances=np.linspace(0, total_length, n, endpoint=False)

new_x = np.interp(new_distances,distance_along, closed[:,0])
new_y=np.interp(new_distances, distance_along, closed[:,1])

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
min_radius = min_turn_radius(centerline)
min_sep = min_separation(centerline, track_width)
print("min turn radius:", min_radius, "required:", 0.75 * track_width)
print("min separation: ", min_sep, "required:", 1.05 * track_width)

radius_ok = min_radius >= 0.75 * track_width
separation_ok = min_sep >= 1.05 * track_width
is_valid = radius_ok and separation_ok

print("radius ok:", radius_ok, "| separation ok:", separation_ok, "| valid:", is_valid)
centerline_closed = np.vstack([centerline, centerline[:1]])
centerline_segments = np.hypot(np.diff(centerline_closed[:,0]),np.diff(centerline_closed[:,1]))


brush_radius = track_width // 2

dx, dy = np.mgrid[-brush_radius:brush_radius + 1, -brush_radius:brush_radius + 1]
brush = dx**2 + dy**2 <= brush_radius**2

assert centerline[:, 0].min() >= brush_radius and centerline[:, 0].max() < WIDTH - brush_radius
assert centerline[:, 1].min() >= brush_radius and centerline[:, 1].max() < HEIGHT - brush_radius

for cx, cy in centerline:
    ix, iy = int(round(cx)), int(round(cy))
    mask[ix - brush_radius:ix + brush_radius + 1, iy - brush_radius:iy + brush_radius + 1] |= brush

start_pos = centerline[0]
direction = centerline[1]-centerline[0]

start_angle= np.degrees(np.arctan2(direction[1],direction[0]))

# print("start: ", start_pos)
# print("kąt startu: ", start_angle)

arc_length = np.concatenate([[0], np.cumsum(centerline_segments)[:-1]])
track_length = centerline_segments.sum()

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
