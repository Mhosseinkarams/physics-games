# Ballistic Range — Physics Prediction Game

Ballistic Range is a 2D physics game built with Pygame that challenges players to predict the trajectory of a projectile using real-world kinematics equations.

## How to Play

### Running the Game
To run the game, use one of the following commands from the root directory:
```bash
python -m ballistic_range
```
or
```bash
python ballistic_range/main.py
```

### Gameplay Steps
1.  **Observe the Goal:** Look at the target's distance and height. Some levels have obstacles or wind.
2.  **Input Parameters:** Use the sliders to adjust the **Launch Angle** (0-90°) and **Initial Velocity** (5-60 m/s).
3.  **Analyze the Prediction:** A dotted line shows your *predicted* trajectory based on the math equations displayed on the right.
4.  **Fire:** Once you're confident, click the **Fire** button. A solid line will show the *actual* simulated path.
5.  **Score:** Your score is based on how close your predicted landing point was to the actual landing point.
    *   `Score = max(0, 100 - error_meters * 10)`
6.  **Progress:** Complete each level to unlock the next.

## Physics Logic

The game uses standard kinematic equations. All calculations are done in **meters and seconds** and converted to pixels only for rendering.

### Velocity Decomposition
The initial velocity $v$ at angle $\theta$ is decomposed into horizontal ($v_{x0}$) and vertical ($v_{y0}$) components:
- $v_{x0} = v \cdot \cos(\theta)$
- $v_{y0} = v \cdot \sin(\theta)$

### Time of Flight (Prediction)
To find the predicted landing time ($t_{flight}$), we solve the quadratic equation $y(t) = h_{target}$:
$h_{launch} + v_{y0} \cdot t - \frac{1}{2} g \cdot t^2 = h_{target}$
Using the quadratic formula:
$t_{flight} = \frac{-v_{y0} - \sqrt{v_{y0}^2 - 4(-0.5g)(h_{launch} - h_{target})}}{2(-0.5g)}$

### Predicted Range
$Range_{predicted} = v_{x0} \cdot t_{flight}$

### Actual Simulation
The actual flight is simulated using Euler integration every frame:
- $v_y = v_y - g \cdot dt$
- $v_x = v_x - wind\_accel \cdot dt$
- $x = x + v_x \cdot dt$
- $y = y + v_y \cdot dt$

## Levels

1.  **Flat Range:** Basic introduction.
2.  **Elevated Target:** Target is on a platform ($h_{target} > 0$).
3.  **Obstacle:** A wall is placed between the cannon and the target.
4.  **Wind:** A headwind affects the *actual* flight, but not the *prediction* formula shown (you must compensate manually!).
5.  **Moving Target:** The target moves horizontally. Predict where it will be at $t_{flight}$.

## Technical Details

- **Language:** Python 3
- **Library:** Pygame
- **Coordinate System:** Physics uses y-up, Rendering converts to y-down.
- **Scale:** 10 pixels = 1 meter.
