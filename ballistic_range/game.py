import pygame
import math
import os
import sys

# Ensure parent directory is in sys.path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ballistic_range.constants import *
from ballistic_range.physics import get_t_flight, get_predicted_trajectory, Projectile
from ballistic_range.ui import Slider, Button

class Level:
    def __init__(self, level_data, font, small_font, level_idx=0):
        self.level_idx = level_idx
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

        self.unlocked_colors = [TREBUCHET_WOOD]
        self.color_options = [
            TREBUCHET_WOOD,
            (100, 100, 100), # Steel
            (139, 69, 19),  # SaddleBrown
            (210, 180, 140), # Tan
            (160, 82, 45)   # Sienna
        ]

        self.projectile = None
        self.predicted_points = []
        self.state = "IDLE" # IDLE, ANIMATING, FIRING, LANDED
        self.score = 0
        self.error = 0
        self.predicted_range = 0
        self.actual_range = 0

        # Animation and feedback state
        self.animation_stage = None
        self.animation_timer = 0
        self.particles = []
        self.wall_state = "INTACT" # INTACT, COLLAPSING, RUBBLE
        self.wall_timer = 0
        self.feedback_text = ""
        self.feedback_timer = 0
        self.morale = 0
        self.trebuchet_color = TREBUCHET_WOOD
        self.miss_flavor_text = [
            "Try again, commander.",
            "Adjust your aim and fire again.",
            "Close — recalculate your angle."
        ]

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

    def update_particles(self, dt):
        for p in self.particles[:]:
            p['vy'] -= GRAVITY * dt
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            if p['life'] <= 0:
                self.particles.remove(p)

    def spawn_particles(self, x, y):
        import random
        for _ in range(10):
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(2, 8),
                'life': 0.5
            })

    def update(self, dt):
        self.time_elapsed += dt
        self.update_particles(dt)

        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback_text = ""

        if self.wall_state == "COLLAPSING":
            self.wall_timer -= dt
            if self.wall_timer <= 0:
                self.wall_state = "RUBBLE"

        if self.state == "ANIMATING":
            self.animation_timer += dt
            if self.animation_stage == "WIND_UP":
                if self.animation_timer >= 0.3:
                    self.animation_stage = "RELEASE"
                    # Release is instant visually, but let's give it one frame or just move to firing
                    self.fire_actual()
            return # Don't do other updates while animating

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
                self.error = abs(self.target_x - self.actual_range)

                # Hit threshold 2.0m
                if self.error < 2.0:
                    self.feedback_text = "BREACH!"
                    self.feedback_timer = 1.0
                    self.wall_state = "COLLAPSING"
                    self.wall_timer = 0.5
                    self.spawn_particles(self.actual_range, self.target_y)

                    # Morale bonus
                    self.score = max(0, 100 - self.error * SCORE_PENALTY_FACTOR)
                    if self.morale == 100:
                        self.score *= 2
                        self.morale = 0
                    else:
                        self.morale = min(100, self.morale + 25)
                else:
                    import random
                    self.feedback_text = random.choice(self.miss_flavor_text)
                    self.feedback_timer = 1.0
                    self.morale = 0
                    self.score = max(0, 100 - self.error * SCORE_PENALTY_FACTOR)

        self.fire_button.enabled = (self.state == "IDLE" and self.angle_slider.touched and self.velocity_slider.touched)
        self.reset_button.enabled = (self.state != "IDLE")
        self.next_button.enabled = (self.state == "LANDED")

    def handle_event(self, event):
        if self.state == "LANDED":
            # Color picker
            for i in range(min(len(self.color_options), self.level_idx + 1)):
                 color = self.color_options[i]
                 rect = pygame.Rect(WIDTH - 300 + i * 40, 300, 30, 30)
                 if event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(event.pos):
                     self.trebuchet_color = color

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
        self.state = "ANIMATING"
        self.animation_stage = "WIND_UP"
        self.animation_timer = 0

    def fire_actual(self):
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
        self.wall_state = "INTACT"
        self.update_prediction()

    def to_screen(self, x, y):
        sx = LAUNCH_SCREEN_X + x * PIXELS_PER_METER
        sy = GROUND_SCREEN_Y - y * PIXELS_PER_METER
        return int(sx), int(sy)

    def draw_background(self, screen):
        # Sky gradient
        pygame.draw.rect(screen, SKY_TOP, (0, 0, WIDTH, GROUND_SCREEN_Y // 2))
        pygame.draw.rect(screen, SKY_BOTTOM, (0, GROUND_SCREEN_Y // 2, WIDTH, GROUND_SCREEN_Y // 2))

        # Clouds
        pygame.draw.ellipse(screen, CLOUD_WHITE, (100, 50, 100, 40))
        pygame.draw.ellipse(screen, CLOUD_WHITE, (140, 60, 120, 50))
        pygame.draw.ellipse(screen, CLOUD_WHITE, (600, 80, 150, 60))

        # Ground
        pygame.draw.rect(screen, (34, 139, 34), (0, GROUND_SCREEN_Y, WIDTH, HEIGHT - GROUND_SCREEN_Y))
        pygame.draw.line(screen, BLACK, (0, GROUND_SCREEN_Y), (WIDTH, GROUND_SCREEN_Y), 2)

    def draw_trebuchet(self, screen):
        cx, cy = self.to_screen(0, LAUNCH_HEIGHT)
        # Base
        pygame.draw.rect(screen, self.trebuchet_color, (cx - 20, cy, 40, 10))
        # Support
        pygame.draw.rect(screen, self.trebuchet_color, (cx - 5, cy - 30, 10, 30))

        # Arm
        arm_length = 40
        pivot_x, pivot_y = cx, cy - 30

        # Default angle is based on player input or animation
        if self.state == "IDLE":
            arm_angle = math.radians(90) # Vertical
        elif self.state == "ANIMATING":
            if self.animation_stage == "WIND_UP":
                # backward from 90 to 135
                p = self.animation_timer / 0.3
                arm_angle = math.radians(90 + 45 * p)
            else: # RELEASE
                arm_angle = math.radians(self.angle_slider.val)
        else: # FIRING or LANDED
            arm_angle = math.radians(self.angle_slider.val)
            if self.state == "LANDED" and self.error >= 2.0:
                # Droop
                arm_angle -= math.radians(10)

        end_x = pivot_x + arm_length * math.cos(arm_angle)
        end_y = pivot_y - arm_length * math.sin(arm_angle)
        pygame.draw.line(screen, self.trebuchet_color, (pivot_x, pivot_y), (end_x, end_y), 4)

    def draw_castle_wall(self, screen):
        tx, ty = self.to_screen(self.target_x, self.target_y)
        brick_w, brick_h = 10, 8

        color = CASTLE_STONE if self.wall_state == "INTACT" else CASTLE_RUBBLE
        y_offset = 0
        if self.wall_state == "COLLAPSING":
            y_offset = (0.5 - self.wall_timer) * 20
        elif self.wall_state == "RUBBLE":
            y_offset = 10

        # Simple 4x3 brick grid
        for row in range(4):
            for col in range(3):
                bx = tx - 15 + col * brick_w
                by = ty - 5 + row * brick_h + y_offset
                if self.wall_state == "RUBBLE":
                    by += 5
                pygame.draw.rect(screen, color, (bx, by, brick_w - 1, brick_h - 1))

        # Flag on top
        if not self.moving_target: # Assume levels 1-4 are fixed targets with flags
             pygame.draw.line(screen, BLACK, (tx, ty - 5 + y_offset), (tx, ty - 20 + y_offset), 2)
             pygame.draw.polygon(screen, RED, [(tx, ty - 20 + y_offset), (tx + 10, ty - 15 + y_offset), (tx, ty - 10 + y_offset)])

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_trebuchet(screen)
        self.draw_castle_wall(screen)

        # Draw platform for elevated target
        if self.target_y > 0:
            tx, ty = self.to_screen(self.target_x, self.target_y)
            px, py = self.to_screen(self.target_x, 0)
            pygame.draw.rect(screen, DARK_GRAY, (tx-20, ty+10, 40, py-ty))

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

            # Draw current projectile with spin
            curr_pos = self.to_screen(self.projectile.x, self.projectile.y)
            # Create a small rotated square
            angle = self.time_elapsed * 10
            points = []
            for i in range(4):
                a = angle + math.radians(i * 90)
                px = curr_pos[0] + 5 * math.cos(a)
                py = curr_pos[1] + 5 * math.sin(a)
                points.append((px, py))
            pygame.draw.polygon(screen, BLACK, points)

        # UI
        self.angle_slider.draw(screen, self.small_font)
        self.velocity_slider.draw(screen, self.small_font)
        self.fire_button.draw(screen, self.small_font)
        self.reset_button.draw(screen, self.small_font)
        self.next_button.draw(screen, self.small_font)

        # Feedback and particles
        self.draw_feedback(screen)

        # Morale
        self.draw_morale(screen)

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

            # Draw color picker
            picker_txt = self.small_font.render("Select Trebuchet Color:", True, BLACK)
            screen.blit(picker_txt, (WIDTH - 300, 275))
            for i in range(min(len(self.color_options), self.level_idx + 1)):
                color = self.color_options[i]
                rect = pygame.Rect(WIDTH - 300 + i * 40, 300, 30, 30)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                if self.trebuchet_color == color:
                    pygame.draw.rect(screen, YELLOW, rect, 4)

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

    def draw_feedback(self, screen):
        if self.feedback_text:
            color = GREEN if self.feedback_text == "BREACH!" else RED
            # Scale-up animation for BREACH
            size_bonus = 0
            if self.feedback_text == "BREACH!":
                size_bonus = int(math.sin((1.0 - self.feedback_timer) * 10) * 10)

            f_font = pygame.font.SysFont("Arial", 48 + size_bonus, bold=True)
            txt = f_font.render(self.feedback_text, True, color)
            rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(txt, rect)

        for p in self.particles:
            px, py = self.to_screen(p['x'], p['y'])
            pygame.draw.circle(screen, GRAY, (px, py), 3)

    def draw_morale(self, screen):
        # Morale bar at top
        bar_w = 200
        bar_h = 20
        x, y = 200, 15
        pygame.draw.rect(screen, GRAY, (x, y, bar_w, bar_h))
        pygame.draw.rect(screen, YELLOW, (x, y, int(bar_w * self.morale / 100), bar_h))
        pygame.draw.rect(screen, BLACK, (x, y, bar_w, bar_h), 2)

        txt = self.small_font.render(f"MORALE: {self.morale}", True, BLACK)
        screen.blit(txt, (x + bar_w + 10, y))

        if self.morale == 100:
            msg = self.small_font.render("MORALE FULL — NEXT HIT DOUBLES SCORE", True, RED)
            screen.blit(msg, (x, y + 25))

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
