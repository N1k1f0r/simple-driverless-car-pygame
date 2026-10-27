from track_generator import generate_track

t = generate_track(seed=5, difficulty=0.5)
print(t.track_length, t.mask.shape)