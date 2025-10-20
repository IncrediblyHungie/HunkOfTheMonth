"""
Calendar image generation with themed templates
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import calendar
from datetime import datetime

# 12 Calendar themes with descriptions for image generation
CALENDAR_THEMES = [
    {
        "month": 1,
        "name": "January",
        "theme": "Firefighter",
        "description": "Muscular firefighter in full gear standing heroically in front of burning building with flames and smoke",
        "template_search": "firefighter hero burning building flames"
    },
    {
        "month": 2,
        "name": "February",
        "theme": "Fighter Pilot",
        "description": "Professional fighter pilot in cockpit of F-16 jet with helmet and oxygen mask, instrument panels visible",
        "template_search": "fighter pilot cockpit f-16 helmet"
    },
    {
        "month": 3,
        "name": "March",
        "theme": "Astronaut",
        "description": "Astronaut in white space suit floating in international space station with Earth visible through window",
        "template_search": "astronaut space station earth floating"
    },
    {
        "month": 4,
        "name": "April",
        "theme": "Cowboy",
        "description": "Rugged cowboy on horseback at golden sunset in western landscape with hat and leather vest",
        "template_search": "cowboy horseback sunset western"
    },
    {
        "month": 5,
        "name": "May",
        "theme": "Chef",
        "description": "Professional chef in white uniform and tall hat in gourmet kitchen with flames from cooking",
        "template_search": "professional chef kitchen cooking flames"
    },
    {
        "month": 6,
        "name": "June",
        "theme": "Rock Star",
        "description": "Rock star guitarist on stage with electric guitar, dramatic stage lighting and crowd in background",
        "template_search": "rock star guitarist stage concert lighting"
    },
    {
        "month": 7,
        "name": "July",
        "theme": "Deep Sea Diver",
        "description": "Deep sea diver in full diving suit underwater surrounded by colorful coral reef and tropical fish",
        "template_search": "deep sea diver underwater coral reef"
    },
    {
        "month": 8,
        "name": "August",
        "theme": "Mountain Climber",
        "description": "Mountain climber at summit of snowy peak with climbing gear, ropes, and dramatic mountain vista",
        "template_search": "mountain climber summit peak snow climbing"
    },
    {
        "month": 9,
        "name": "September",
        "theme": "Race Car Driver",
        "description": "Formula 1 race car driver in racing suit and helmet sitting in red F1 car in pit lane",
        "template_search": "formula 1 driver racing suit f1 car"
    },
    {
        "month": 10,
        "name": "October",
        "theme": "Samurai Warrior",
        "description": "Samurai warrior in traditional armor holding katana sword in Japanese temple with cherry blossoms",
        "template_search": "samurai warrior armor katana temple"
    },
    {
        "month": 11,
        "name": "November",
        "theme": "Viking Warrior",
        "description": "Viking warrior with beard and armor on longship with shield and axe, stormy seas in background",
        "template_search": "viking warrior longship armor shield"
    },
    {
        "month": 12,
        "name": "December",
        "theme": "Secret Agent",
        "description": "Secret agent in black tuxedo with bow tie holding silenced pistol in elegant casino setting",
        "template_search": "secret agent tuxedo james bond casino"
    }
]

class CalendarGenerator:
    def __init__(self, year=None):
        """Initialize calendar generator"""
        self.year = year or datetime.now().year + 1  # Default to next year

    def add_calendar_overlay(self, image_path, output_path, month):
        """
        Add calendar overlay to image

        Args:
            image_path: Path to swapped face image
            output_path: Path to save final calendar image
            month: Month number (1-12)
        """
        # Open image
        img = Image.open(image_path)

        # Ensure image is large enough for calendar
        target_size = (1200, 1600)  # Portrait orientation for calendar
        img = img.resize(target_size, Image.Resampling.LANCZOS)

        # Create drawing context
        draw = ImageDraw.Draw(img)

        # Get calendar data
        month_name = calendar.month_name[month]
        cal_text = calendar.month(self.year, month)

        # Define overlay position and style
        overlay_height = 300
        overlay_y = img.height - overlay_height

        # Draw semi-transparent overlay at bottom
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [(0, overlay_y), (img.width, img.height)],
            fill=(0, 0, 0, 180)  # Semi-transparent black
        )

        # Composite overlay onto image
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')

        # Draw text on image
        draw = ImageDraw.Draw(img)

        # Try to load a nice font, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            cal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            cal_font = ImageFont.load_default()

        # Draw month and year
        title_text = f"{month_name} {self.year}"

        # Calculate text position for centering
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (img.width - title_width) // 2
        title_y = overlay_y + 20

        # Draw title
        draw.text((title_x, title_y), title_text, fill='white', font=title_font)

        # Draw calendar grid
        cal_y = title_y + 80
        cal_lines = cal_text.split('\n')[1:]  # Skip the month/year line

        for i, line in enumerate(cal_lines):
            # Center each line
            line_bbox = draw.textbbox((0, 0), line, font=cal_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (img.width - line_width) // 2
            draw.text((line_x, cal_y + i * 30), line, fill='white', font=cal_font)

        # Save final image
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, quality=95)

        return output_path

    @staticmethod
    def get_themes():
        """Return list of all calendar themes"""
        return CALENDAR_THEMES

    @staticmethod
    def get_theme(month):
        """Get theme for specific month"""
        for theme in CALENDAR_THEMES:
            if theme['month'] == month:
                return theme
        return None
