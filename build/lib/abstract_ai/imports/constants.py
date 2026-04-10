IMAGE_INSTRUCTION_KEYS = {
        "alt_text": {
            "instruction": (
                "Provide a concise description of what the image visibly contains. "
                "Avoid phrases like 'image of'. Keep under 160 characters."
            ),
            "example": "Abstract Endeavors logo representing innovative wealth management solutions",
            "default": True
        },
        "title_tag": {
            "instruction": (
                "Generate a clean and descriptive title for the image, suitable for HTML title tags "
                "and search engine previews."
            ),
            "example": "Abstract Endeavors - The Future of Wealth Management",
            "default": True
        },
        "longdesc": {
            "instruction": (
                "Write a detailed, multi-sentence description summarizing the visual appearance, "
                "purpose, and context of the image."
            ),
            "example": (
                "Explore the Abstract Endeavors logo, a symbol of innovative approaches in wealth "
                "management, reflecting a new perspective on financial growth and strategy."
            ),
            "default": True
        },
        "caption": {
            "instruction": (
                "Provide a short, natural-language caption that could appear under the image in an article."
            ),
            "example": "Abstract Endeavors - The Future of Wealth Management",
            "default": True
        },
        "keywords": {
            "instruction": (
                "Provide a comma-separated list of SEO keywords relevant to the image. "
                "Avoid special characters and include 7-15 items."
            ),
            "example": "wealth management, innovative logo, finance strategy, branding, modern design",
            "default": True
        },
    }
