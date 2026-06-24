import math

def get_t_flight(vy0, launch_height, gravity, target_height=0):
    """
    Solves y(t) = target_height for t using the quadratic formula.
    y(t) = launch_height + vy0*t - 0.5*gravity*t^2
    -0.5*gravity*t^2 + vy0*t + (launch_height - target_height) = 0
    """
    a = -0.5 * gravity
    b = vy0
    c = launch_height - target_height

    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return None

    # t = (-b - sqrt(d)) / (2a)
    # Since a is negative (-0.5 * 9.81), 2a is negative.
    # To get a positive t, we want the more negative numerator.
    t = (-b - math.sqrt(discriminant)) / (2*a)
    return t

def get_predicted_trajectory(vx0, vy0, launch_height, gravity, t_flight, wind_accel=0, num_samples=30):
    """
    Computes points for the predicted trajectory using closed-form equations.
    """
    points = []
    if t_flight is None or t_flight <= 0:
        return points

    for i in range(num_samples + 1):
        t = (t_flight * i) / num_samples
        # x(t) = vx0*t - 0.5*wind_accel*t^2
        x = vx0 * t - 0.5 * wind_accel * t**2
        # y(t) = launch_height + vy0*t - 0.5*gravity*t^2
        y = launch_height + vy0 * t - 0.5 * gravity * t**2
        points.append((x, y))
    return points

class Projectile:
    def __init__(self, x, y, vx, vy, gravity, wind_accel=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.wind_accel = wind_accel
        self.trail = [(x, y)]
        self.landed = False
        self.actual_range = None
        self.t = 0

    def update(self, dt, target_height=0, obstacle=None):
        if self.landed:
            return

        self.t += dt

        # Actual simulated trajectory — Euler integration
        # vy -= GRAVITY * dt
        # vx -= WIND_ACCEL * dt (Level 4)
        # x += vx * dt
        # y += vy * dt

        self.vy -= self.gravity * dt
        self.vx -= self.wind_accel * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.trail.append((self.x, self.y))

        # Obstacle collision
        if obstacle:
            # Simple vertical wall collision
            if abs(self.x - obstacle["x"]) < 0.5: # thin wall
                if self.y <= obstacle["height"]:
                    self.landed = True
                    self.actual_range = self.x
                    return

        # Check for landing.
        # Level 2 fix: only land if we are moving downwards and hit the target height,
        # OR if we are below target height and were previously above it.
        # Simplified: If we are falling (vy < 0) and y <= target_height.
        if self.vy < 0 and self.y <= target_height:
            self.landed = True
            self.actual_range = self.x
            self.y = target_height
