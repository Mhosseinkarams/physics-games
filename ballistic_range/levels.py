LEVELS = [
    {
        "name": "Level 1: The Outer Wall",
        "description": "A simple target. Find your range, commander.",
        "target_x": 80.0,
        "target_y": 0.0,
        "wind_accel": 0.0,
        "obstacle": None,
        "moving_target": False
    },
    {
        "name": "Level 2: The Hilltop Keep",
        "description": "Their tower sits higher than the rest.",
        "target_x": 70.0,
        "target_y": 10.0,
        "wind_accel": 0.0,
        "obstacle": None,
        "moving_target": False
    },
    {
        "name": "Level 3: The Barricade",
        "description": "A wall blocks your shot. Arc over it.",
        "target_x": 90.0,
        "target_y": 0.0,
        "wind_accel": 0.0,
        "obstacle": {"x": 45.0, "height": 15.0},
        "moving_target": False
    },
    {
        "name": "Level 4: The Storm Siege",
        "description": "Wind fights your aim today.",
        "target_x": 60.0,
        "target_y": 0.0,
        "wind_accel": 2.0,
        "obstacle": None,
        "moving_target": False
    },
    {
        "name": "Level 5: The Supply Cart",
        "description": "Hit a moving target — time your shot.",
        "target_x": 70.0,
        "target_y": 0.0,
        "wind_accel": 0.0,
        "obstacle": None,
        "moving_target": {"amplitude": 20.0, "frequency": 1.0}
    }
]
