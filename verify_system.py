import os

def verify_system():
    # Check if all files exist
    files = [
        "ballistic_range/constants.py",
        "ballistic_range/physics.py",
        "ballistic_range/ui.py",
        "ballistic_range/levels.py",
        "ballistic_range/game.py",
        "ballistic_range/main.py"
    ]

    for f in files:
        if os.path.exists(f):
            print(f"OK: {f} exists")
        else:
            print(f"FAIL: {f} missing")
            return

    # Try importing all modules
    try:
        from ballistic_range import constants, physics, ui, levels, game, main
        print("OK: All modules imported successfully")
    except ImportError as e:
        print(f"FAIL: Import error: {e}")
        return

    print("System verification PASSED")

if __name__ == "__main__":
    verify_system()
