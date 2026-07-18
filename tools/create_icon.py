from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT_ROOT / "imgup.png"
TARGET = PROJECT_ROOT / "imgup.ico"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def main():
    with Image.open(SOURCE) as image:
        image.convert("RGBA").save(
            TARGET,
            format="ICO",
            sizes=[(size, size) for size in ICON_SIZES],
        )
    print(f"Created {TARGET}")


if __name__ == "__main__":
    main()
