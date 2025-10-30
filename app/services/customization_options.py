"""
Calendar customization options
Allows users to personalize their calendar generation
"""

CUSTOMIZATION_OPTIONS = {
    "gender": {
        "label": "Calendar Gender",
        "description": "Choose the gender presentation for your calendar",
        "options": [
            {
                "value": "male",
                "label": "Male Hunk",
                "description": "Masculine, muscular male body"
            },
            {
                "value": "female",
                "label": "Female Bombshell",
                "description": "Feminine, fit female body"
            },
            {
                "value": "nonbinary",
                "label": "Non-Binary",
                "description": "Androgynous, athletic body"
            }
        ],
        "default": "male"
    },
    "body_type": {
        "label": "Body Type",
        "description": "Select the fitness level",
        "options": [
            {
                "value": "extremely_muscular",
                "label": "Extremely Muscular",
                "description": "Bodybuilder physique with huge muscles"
            },
            {
                "value": "athletic",
                "label": "Athletic & Toned",
                "description": "Fit and defined, not overly bulky"
            },
            {
                "value": "fit",
                "label": "Fit & Healthy",
                "description": "In-shape with visible muscle tone"
            },
            {
                "value": "average",
                "label": "Average Build",
                "description": "Normal, everyday body type"
            }
        ],
        "default": "athletic"
    },
    "style": {
        "label": "Clothing Style",
        "description": "How revealing should the photos be?",
        "options": [
            {
                "value": "sexy",
                "label": "Sexy & Revealing",
                "description": "Shirtless, minimal clothing, showing off the body"
            },
            {
                "value": "modest",
                "label": "Modest & Clothed",
                "description": "Fully clothed, appropriate attire"
            },
            {
                "value": "comedic",
                "label": "Comedic & Silly",
                "description": "Funny costumes and ridiculous outfits"
            },
            {
                "value": "dramatic",
                "label": "Dramatic & Cinematic",
                "description": "Movie-quality action poses and lighting"
            }
        ],
        "default": "sexy"
    },
    "tone": {
        "label": "Overall Tone",
        "description": "What vibe do you want?",
        "options": [
            {
                "value": "serious",
                "label": "Serious & Intense",
                "description": "Brooding, mysterious, model-like"
            },
            {
                "value": "funny",
                "label": "Funny & Lighthearted",
                "description": "Comedic situations, gag gift vibes"
            },
            {
                "value": "over_the_top",
                "label": "Over-the-Top",
                "description": "Absurdly exaggerated, ridiculously sexy"
            },
            {
                "value": "playful",
                "label": "Playful & Cheeky",
                "description": "Flirty and fun, not too serious"
            }
        ],
        "default": "funny"
    }
}

def get_default_preferences():
    """Get default customization preferences"""
    return {
        "gender": "male",
        "body_type": "athletic",
        "style": "sexy",
        "tone": "funny"
    }

def get_customization_options():
    """Get all customization options"""
    return CUSTOMIZATION_OPTIONS

def validate_preferences(preferences):
    """
    Validate user preferences

    Args:
        preferences: Dict of user selections

    Returns:
        Validated preferences with defaults for missing values
    """
    validated = get_default_preferences()

    for key, value in preferences.items():
        if key in CUSTOMIZATION_OPTIONS:
            # Check if the value is valid
            valid_values = [opt["value"] for opt in CUSTOMIZATION_OPTIONS[key]["options"]]
            if value in valid_values:
                validated[key] = value

    return validated
