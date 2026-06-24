from physics import get_t_flight, get_predicted_trajectory, Projectile
import math

def test_physics():
    gravity = 9.81
    launch_height = 1.0
    velocity = 30.0
    angle_deg = 45.0
    angle_rad = math.radians(angle_deg)
    vx0 = velocity * math.cos(angle_rad)
    vy0 = velocity * math.sin(angle_rad)

    t_flight = get_t_flight(vy0, launch_height, gravity)
    predicted_range = vx0 * t_flight

    print(f"Predicted flight time: {t_flight:.4f} s")
    print(f"Predicted range: {predicted_range:.4f} m")

    # Simulate
    projectile = Projectile(0, launch_height, vx0, vy0, gravity)
    dt = 1/60.0
    while not projectile.landed:
        projectile.update(dt)
        if projectile.t > 10: # Safety break
            break

    print(f"Actual range: {projectile.actual_range:.4f} m")
    error = abs(predicted_range - projectile.actual_range)
    print(f"Difference: {error:.4f} m")

    if error < 0.5: # 0.5m is reasonable for Euler at 60fps
        print("Physics test PASSED")
    else:
        print("Physics test FAILED")

if __name__ == "__main__":
    test_physics()
