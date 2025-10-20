"""
Create placeholder template images for testing
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_placeholder_templates(output_dir="templates/themes"):
    """Create 12 placeholder template images"""

    themes = [
        ("01_firefighter.jpg", "FIREFIGHTER", "#FF4500"),
        ("02_pilot.jpg", "FIGHTER PILOT", "#1E90FF"),
        ("03_astronaut.jpg", "ASTRONAUT", "#000080"),
        ("04_cowboy.jpg", "COWBOY", "#8B4513"),
        ("05_chef.jpg", "CHEF", "#FFFFFF"),
        ("06_rockstar.jpg", "ROCK STAR", "#8B008B"),
        ("07_diver.jpg", "DEEP SEA DIVER", "#00CED1"),
        ("08_climber.jpg", "MOUNTAIN CLIMBER", "#708090"),
        ("09_racer.jpg", "RACE CAR DRIVER", "#DC143C"),
        ("10_samurai.jpg", "SAMURAI", "#8B0000"),
        ("11_viking.jpg", "VIKING", "#4B0082"),
        ("12_agent.jpg", "SECRET AGENT", "#000000")
    ]

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for filename, text, color in themes:
        # Create image with colored background
        img = Image.new('RGB', (1200, 1600), color=color)
        draw = ImageDraw.Draw(img)

        # Try to load font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()

        # Draw centered text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (1200 - text_width) // 2
        y = (1600 - text_height) // 2

        # Draw text with outline
        outline_color = "white" if color != "#FFFFFF" else "black"
        text_color = "white" if color != "#FFFFFF" else "black"

        # Draw outline
        for adj_x in range(-3, 4):
            for adj_y in range(-3, 4):
                draw.text((x+adj_x, y+adj_y), text, font=font, fill=outline_color)

        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)

        # Add a face placeholder circle
        circle_y = y - 300
        draw.ellipse([500, circle_y, 700, circle_y + 200], fill="gray", outline=outline_color, width=5)

        # Save
        output_path = Path(output_dir) / filename
        img.save(output_path, quality=95)
        print(f"Created: {output_path}")

    print(f"\n✓ Created {len(themes)} placeholder templates")

if __name__ == "__main__":
    create_placeholder_templates()
