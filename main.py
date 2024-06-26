import pygame
import numpy as np
from collections import deque

def initialize_pygame():
    pygame.init()
    WIDTH, HEIGHT = 800, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Three-Body Problem Simulation")
    return screen, WIDTH, HEIGHT

def to_screen_coords(position, WIDTH, HEIGHT, SCALE):
    x = WIDTH // 2 + int(position[0] / SCALE)
    y = HEIGHT // 2 - int(position[1] / SCALE)
    return x, y

def gravitational_force(m1, m2, r1, r2):
    G = 6.67430e-11
    r = np.linalg.norm(r2 - r1)
    if r == 0:
        return np.zeros(2)
    force = G * m1 * m2 * (r2 - r1) / r**3
    return force

def derivatives(state, masses):
    positions = state[:6].reshape((3, 2))
    velocities = state[6:].reshape((3, 2))
    forces = np.zeros((3, 2))
    
    for i in range(3):
        for j in range(3):
            if i != j:
                forces[i] += gravitational_force(masses[i], masses[j], positions[i], positions[j])
    
    dydt = np.zeros(12)
    dydt[:6] = velocities.flatten()
    dydt[6:] = (forces / masses[:, np.newaxis]).flatten()
    return dydt

def runge_kutta_step(state, masses, dt):
    k1 = derivatives(state, masses) * dt
    k2 = derivatives(state + 0.5 * k1, masses) * dt
    k3 = derivatives(state + 0.5 * k2, masses) * dt
    k4 = derivatives(state + k3, masses) * dt
    return state + (k1 + 2*k2 + 2*k3 + k4) / 6

def initialize_simulation():
    masses = np.array([1.989e30, 1.989e30, 1.989e30])  # Three Earths
    positions = np.array([[1.496e11, 0], [-1.496e11, 0], [0, 0]])  # Initial positions
    velocities = np.array([[0, 2.98e4], [0, -2.98e4], [0, 1e3]])  # Initial velocities
    state = np.hstack((positions.flatten(), velocities.flatten()))
    dt = 2e4
    return masses, state, dt

def update_simulation(state, masses, dt):
    new_state = runge_kutta_step(state, masses, dt)
    positions = new_state[:6].reshape((3, 2))
    return new_state, positions

def draw_simulation(screen, positions, earth_trajectories, WIDTH, HEIGHT, SCALE, max_orbit_length):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    AQUA = (0, 255, 255)
    ORANGE = (255, 165, 0)
    YELLOW = (255, 255, 0)
    screen.fill(BLACK)
    
    for i in range(3):
        x_pos, y_pos = to_screen_coords(positions[i], WIDTH, HEIGHT, SCALE)
        
        if len(earth_trajectories[i]) > 2:
            orbit_points = [to_screen_coords(pos, WIDTH, HEIGHT, SCALE) for pos in earth_trajectories[i]]
            pygame.draw.lines(screen, GREY, False, orbit_points, 1)
            
        if len(earth_trajectories[i]) > max_orbit_length:
            earth_trajectories[i].popleft()
            
        if i == 0:
            pygame.draw.circle(screen, GREEN, (x_pos, y_pos), 7)
        elif i == 1:
            pygame.draw.circle(screen, RED, (x_pos, y_pos), 7)
        else:
            pygame.draw.circle(screen, AQUA, (x_pos, y_pos), 7)
            
    pygame.display.flip()

def main():
    screen, WIDTH, HEIGHT = initialize_pygame()
    SCALE = 2e9
    masses, state, dt = initialize_simulation()
    max_orbit_length = 1000  # Set the maximum number of frames to show for the orbit
    earth_trajectories = [deque(maxlen=max_orbit_length) for _ in range(3)]  # Using deque for efficient pop from the left
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        state, positions = update_simulation(state, masses, dt)
        
        for i in range(3):
            earth_trajectories[i].append(positions[i])
            
        draw_simulation(screen, positions, earth_trajectories, WIDTH, HEIGHT, SCALE, max_orbit_length)
        clock.tick(144)
        
    pygame.quit()

if __name__ == "__main__":
    main()
