LEVELS = [
    {
        "name": "Level 1: Flat Range",
        "description": "Target at fixed distance, no obstacles.",
        "target_x": 80.0,
        "target_y": 0.0,
        "wind_accel": 0.0,
        "obstacle": None,
        "moving_target": False
    },
    {
        "name": "Level 2: Elevated Target",
        "description": "Target sits on a raised platform.",
        "target_x": 70.0,
        "target_y": 10.0,
        "wind_accel": 0.0,
        "obstacle": None,
        "moving_target": False
    },
    {
        "name": "Level 3: Obstacle",
        "description": "A wall sits between cannon and target.",
        "target_x": 90.0,
        "target_y": 0.0,
        "wind_accel": 0.0,
        "obstacle": {"x": 45.0, "height": 15.0},
        "moving_target": False
    },
    {
        "name": "Level 4: Wind",
        "description": "Constant horizontal force (headwind).",
        "target_x": 60.0,
        "target_y": 0.0,
        "wind_accel": 2.0, # m/s^2 headwind
        "obstacle": None,
        "moving_target": False
    },
    {
        "name": "Level 5: Moving Target",
        "description": "Target oscillates horizontally.",
        "target_x": 70.0,
        "target_y": 0.0,
        "wind_accel": 0.0,
        "obstacle": None,
        "moving_target": {"amplitude": 20.0, "frequency": 1.0}
    }
]
