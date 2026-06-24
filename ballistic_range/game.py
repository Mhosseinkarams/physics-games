import pygame
import math
from ballistic_range.constants import *
from ballistic_range.physics import get_t_flight, get_predicted_trajectory, Projectile
from ballistic_range.ui import Slider, Button

class Level:
    def __init__(self, level_data, font, small_font):
        self.level_data = level_data
        self.font = font
        self.small_font = small_font

        self.target_x_base = level_data["target_x"]
        self.target_x = self.target_x_base
        self.target_y = level_data["target_y"]
        self.wind_accel = level_data["wind_accel"]
        self.obstacle = level_data["obstacle"]
        self.moving_target = level_data["moving_target"]

        self.angle_slider = Slider(50, 50, 200, 20, 0, 90, "Angle", 45)
        self.velocity_slider = Slider(50, 100, 200, 20, 5, 60, "Velocity", 30)

        self.fire_button = Button(50, 150, 100, 40, "Fire", GREEN)
        self.reset_button = Button(170, 150, 100, 40, "Reset", YELLOW)
        self.next_button = Button(300, 150, 120, 40, "Next Level", BLUE)

        self.projectile = None
        self.predicted_points = []
        self.state = "IDLE" # IDLE, FIRING, LANDED
        self.score = 0
        self.error = 0
        self.predicted_range = 0
        self.actual_range = 0

        self.update_prediction()
        self.time_elapsed = 0

    def update_prediction(self):
        angle_deg = self.angle_slider.val
        velocity = self.velocity_slider.val
        angle_rad = math.radians(angle_deg)
        vx0 = velocity * math.cos(angle_rad)
        vy0 = velocity * math.sin(angle_rad)

        t_flight = get_t_flight(vy0, LAUNCH_HEIGHT, GRAVITY, self.target_y)
        self.predicted_range = vx0 * t_flight if t_flight else 0

        # Prediction formula does NOT include wind term by default as per prompt
        self.predicted_points = get_predicted_trajectory(vx0, vy0, LAUNCH_HEIGHT, GRAVITY, t_flight)

    def update(self, dt):
        self.time_elapsed += dt

        if self.moving_target:
            amp = self.moving_target["amplitude"]
            freq = self.moving_target["frequency"]
            # target_x = base_x + amplitude * sin(time * frequency)
            self.target_x = self.target_x_base + amp * math.sin(self.time_elapsed * freq)

        if self.state == "FIRING" and self.projectile:
            # Projectile update uses Euler integration
            self.projectile.update(dt, self.target_y, self.obstacle)
            if self.projectile.landed:
                self.state = "LANDED"
                self.actual_range = self.projectile.actual_range

                # Scoring: error is distance between actual landing and target position
                # In Level 5, target_x is where the target IS at landing time
                self.error = abs(self.target_x - self.actual_range)
                self.score = max(0, 100 - self.error * SCORE_PENALTY_FACTOR)

        self.fire_button.enabled = (self.state == "IDLE" and self.angle_slider.touched and self.velocity_slider.touched)
        self.reset_button.enabled = (self.state != "IDLE")
        self.next_button.enabled = (self.state == "LANDED")

    def handle_event(self, event):
        if self.state == "IDLE":
            if self.angle_slider.handle_event(event) or self.velocity_slider.handle_event(event):
                self.update_prediction()

            if self.fire_button.handle_event(event):
                self.fire()

        if self.reset_button.handle_event(event):
            self.reset()

        if self.next_button.handle_event(event):
            if self.state == "LANDED":
                return "NEXT"
        return None

    def fire(self):
        angle_deg = self.angle_slider.val
        velocity = self.velocity_slider.val
        angle_rad = math.radians(angle_deg)
        vx0 = velocity * math.cos(angle_rad)
        vy0 = velocity * math.sin(angle_rad)

        # Actual simulation
        self.projectile = Projectile(0, LAUNCH_HEIGHT, vx0, vy0, GRAVITY, self.wind_accel)
        self.state = "FIRING"

    def reset(self):
        self.state = "IDLE"
        self.projectile = None
        self.time_elapsed = 0
        self.update_prediction()

    def to_screen(self, x, y):
        sx = LAUNCH_SCREEN_X + x * PIXELS_PER_METER
        sy = GROUND_SCREEN_Y - y * PIXELS_PER_METER
        return int(sx), int(sy)

    def draw(self, screen):
        # Draw ground
        pygame.draw.line(screen, BLACK, (0, GROUND_SCREEN_Y), (WIDTH, GROUND_SCREEN_Y), 2)

        # Draw cannon base
        cx, cy = self.to_screen(0, LAUNCH_HEIGHT)
        pygame.draw.circle(screen, BLACK, (cx, cy), 10)

        # Draw target
        tx, ty = self.to_screen(self.target_x, self.target_y)
        if self.target_y > 0:
            # Draw platform
            px, py = self.to_screen(self.target_x, 0)
            pygame.draw.rect(screen, GRAY, (tx-20, ty, 40, py-ty))
        pygame.draw.rect(screen, RED, (tx-10, ty-5, 20, 10))

        # Draw obstacle
        if self.obstacle:
            ox, oy = self.to_screen(self.obstacle["x"], self.obstacle["height"])
            gx, gy = self.to_screen(self.obstacle["x"], 0)
            pygame.draw.rect(screen, DARK_GRAY, (ox-5, oy, 10, gy-oy))

        # Draw prediction (dotted line)
        if self.state == "IDLE":
            for p in self.predicted_points:
                px, py = self.to_screen(p[0], p[1])
                pygame.draw.circle(screen, GRAY, (px, py), 2)

        # Draw actual flight (solid line)
        if self.projectile:
            if len(self.projectile.trail) > 1:
                pixel_trail = [self.to_screen(p[0], p[1]) for p in self.projectile.trail]
                pygame.draw.lines(screen, BLACK, False, pixel_trail, 2)

            # Draw current projectile
            curr_pos = self.to_screen(self.projectile.x, self.projectile.y)
            pygame.draw.circle(screen, RED, curr_pos, 5)

        # UI
        self.angle_slider.draw(screen, self.small_font)
        self.velocity_slider.draw(screen, self.small_font)
        self.fire_button.draw(screen, self.small_font)
        self.reset_button.draw(screen, self.small_font)
        self.next_button.draw(screen, self.small_font)

        # Math display
        self.draw_math(screen)

        # Score display
        if self.state == "LANDED":
            res_txt = [
                f"Predicted Range: {self.predicted_range:.2f} m",
                f"Actual Range: {self.actual_range:.2f} m",
                f"Error: {self.error:.2f} m",
                f"Score for Round: {self.score:.1f}"
            ]
            for i, line in enumerate(res_txt):
                t = self.font.render(line, True, BLACK)
                screen.blit(t, (WIDTH - 300, 150 + i * 30))

        # Level Info
        info = self.font.render(self.level_data["name"], True, BLACK)
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 10))
        desc = self.small_font.render(self.level_data["description"], True, DARK_GRAY)
        screen.blit(desc, (WIDTH // 2 - desc.get_width() // 2, 40))

        if self.wind_accel != 0:
            wind_txt = self.small_font.render(f"Wind Accel: {self.wind_accel} m/s^2 (Headwind)", True, BLUE)
            screen.blit(wind_txt, (WIDTH // 2 - wind_txt.get_width() // 2, 70))

        if self.moving_target:
            amp = self.moving_target["amplitude"]
            freq = self.moving_target["frequency"]
            # Velocity of target: v(t) = amp * freq * cos(t * freq)
            curr_v = amp * freq * math.cos(self.time_elapsed * freq)
            target_info = self.small_font.render(f"Target V: {curr_v:.2f} m/s", True, RED)
            screen.blit(target_info, (WIDTH // 2 - target_info.get_width() // 2, 90))

    def draw_math(self, screen):
        angle_deg = self.angle_slider.val
        velocity = self.velocity_slider.val
        angle_rad = math.radians(angle_deg)
        vx0 = velocity * math.cos(angle_rad)
        vy0 = velocity * math.sin(angle_rad)

        lines = [
            f"vx0 = {velocity:.1f} * cos({angle_deg:.1f}°) = {vx0:.2f} m/s",
            f"vy0 = {velocity:.1f} * sin({angle_deg:.1f}°) = {vy0:.2f} m/s",
            f"y(t) = {LAUNCH_HEIGHT} + vy0*t - 0.5*g*t^2",
            f"y(t) = {LAUNCH_HEIGHT} + {vy0:.2f}t - {0.5*GRAVITY:.2f}t^2",
        ]

        if self.target_y != 0:
            lines.append(f"Solve y(t) = {self.target_y} for t_flight")
        else:
            lines.append(f"Solve y(t) = 0 for t_flight")

        for i, line in enumerate(lines):
            t = self.small_font.render(line, True, BLACK)
            screen.blit(t, (WIDTH - 350, 20 + i * 20))
