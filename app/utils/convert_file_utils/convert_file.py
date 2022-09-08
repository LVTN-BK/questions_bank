import os

def remove_file(path: str) -> None:
    # time.sleep(3)
    os.unlink(path)
