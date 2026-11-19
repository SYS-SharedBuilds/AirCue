"""Outdoor activity guidance mapping from CPCB AQI alert level.

Precautionary and non-diagnostic guidance derived from official CPCB category guidance.
Strictly excludes all indoor, ventilation, window, and door references.
"""
from __future__ import annotations

from typing import Dict, NamedTuple


class ActivityAdvice(NamedTuple):
    level: int
    name: str
    summary: str
    action_en: str
    action_hi: str


OUTDOOR_ADVICE_TABLE: Dict[int, ActivityAdvice] = {
    0: ActivityAdvice(
        level=0,
        name="Normal",
        summary="Air quality is acceptable for all outdoor school activities.",
        action_en="Outdoor activities can proceed normally.",
        action_hi="सभी बाहरी गतिविधियाँ सामान्य रूप से जारी रखी जा सकती हैं।",
    ),
    1: ActivityAdvice(
        level=1,
        name="Moderate",
        summary="Sensitive students should avoid prolonged heavy physical exertion.",
        action_en="Students with breathing sensitivity should take frequent rests outdoors.",
        action_hi="सांस की संवेदनशीलता वाले छात्र बाहरी गतिविधियों में अधिक श्रम न करें।",
    ),
    2: ActivityAdvice(
        level=2,
        name="Poor",
        summary="Air quality is poor. Reduce outdoor exertion and prefer indoor play.",
        action_en="Please reduce outdoor sports and conduct light activities indoors.",
        action_hi="कृपया बाहरी खेलकूद कम करें और गतिविधियाँ भीतर आयोजित करें।",
    ),
    3: ActivityAdvice(
        level=3,
        name="Very Poor",
        summary="Air quality is very poor. Move all outdoor activities indoors.",
        action_en="Please move all outdoor sports and physical training indoors immediately.",
        action_hi="कृपया सभी बाहरी खेल और सभा तुरंत भीतर स्थानांतरित करें।",
    ),
    4: ActivityAdvice(
        level=4,
        name="Severe",
        summary="Air quality is severe. Strictly avoid outdoor exposure; cancel outdoor activities.",
        action_en="Please keep all students indoors and cancel all outdoor activities.",
        action_hi="कृपया सभी छात्रों को भीतर रखें और बाहरी गतिविधियाँ रद्द करें।",
    ),
}


def get_advice(level: int) -> ActivityAdvice:
    """Retrieve outdoor activity advice for a given alert level (0 to 4)."""
    clamped = max(0, min(4, level))
    return OUTDOOR_ADVICE_TABLE[clamped]
