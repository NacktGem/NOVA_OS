"""
Theme definitions for the Black Rose platform.

This module centralises the definition of all available themes so that both
the frontend and backend can refer to the same source of truth. Each theme
specifies a human‑readable name and a sequence of CSS colours that can be
applied to the application. If you add or modify themes here, consider
updating the corresponding files in the frontend (under `frontend/themes`).
"""

from typing import List, Dict


Theme = Dict[str, object]

ALL_THEMES: List[Theme] = [
    {
        "name": "Moody Floral",
        "colors": [
            "#3C3C44",
            "#49475B",
            "#6F7275",
            "#ADA284",
            "#F2AE72",
            "#BE4450",
        ],
    },
    {
        "name": "Stormy Mountain",
        "colors": [
            "#2E3A46",
            "#4C6A88",
            "#5B7F95",
            "#8DA3B9",
            "#B9C5D8",
            "#EAF0F8",
        ],
    },
    {
        "name": "Muted Ocean",
        "colors": [
            "#1B2E35",
            "#3A6B7C",
            "#4E8598",
            "#7CA8B5",
            "#AECFD6",
            "#E0EEF2",
        ],
    },
    {
        "name": "Vintage Rose",
        "colors": [
            "#4D2E33",
            "#7E2A40",
            "#A53B5C",
            "#CA6C7D",
            "#EAB0A1",
            "#F5D6C6",
        ],
    },
    {
        "name": "Misty Purple",
        "colors": [
            "#3E284B",
            "#5E3E66",
            "#7C4D7A",
            "#A76E9C",
            "#D0A5CF",
            "#E8D6E9",
        ],
    },
    {
        "name": "Luxe Silver",
        "colors": [
            "#1F1F1F",
            "#313131",
            "#4D4D4D",
            "#7A7A7A",
            "#B0B0B0",
            "#E5E5E5",
        ],
    },
    {
        "name": "Forest Whisper",
        "colors": [
            "#233D4D",
            "#426A5A",
            "#688E5A",
            "#9DBF4E",
            "#C7D59F",
            "#E4EBD7",
        ],
    },
]

__all__ = ["ALL_THEMES", "Theme"]