"""Strict safety, language, and content validators for LLM outputs."""
from __future__ import annotations

import re
from typing import Any, NamedTuple


class ValidationResult(NamedTuple):
    passed: bool
    rule_results: dict[str, bool]
    failure_reasons: list[str]


# Banned indoor / ventilation vocabulary (English and Hindi transliterated / Devanagari)
INDOOR_VENTILATION_BLACKLIST = [
    "window",
    "windows",
    "door",
    "doors",
    "ventilate",
    "ventilation",
    "stuffy",
    "stuffiness",
    "खिड़की",
    "खिड़कियां",
    "दरवाजा",
    "दरवाजे",
    "हवादार",
    "सफाई",
]

# Medical diagnosis / scaremongering blacklist
MEDICAL_SCARE_BLACKLIST = [
    "asthma",
    "cancer",
    "choke",
    "toxic",
    "poison",
    "poisonous",
    "death",
    "hospital",
    "lung damage",
    "दमा",
    "अस्थमा",
    "जहरीली",
    "कैंसर",
    "मौत",
]


def validate_word_limit(text: str, max_words: int = 20) -> bool:
    """Validate text does not exceed max word count."""
    words = text.strip().split()
    return len(words) <= max_words


def validate_sentence_count(text: str, max_sentences: int = 2) -> bool:
    """Validate text is between 1 and max_sentences."""
    # Split by period, exclamation, question mark, or Devanagari purna viram (।)
    parts = [p.strip() for p in re.split(r"[.!?।]+", text) if p.strip()]
    return 1 <= len(parts) <= max_sentences


def validate_no_indoor_ventilation(text: str) -> bool:
    """Enforce outdoor stance: zero indoor ventilation or door/window mentions."""
    lowered = text.lower()
    for word in INDOOR_VENTILATION_BLACKLIST:
        # Match whole words to avoid sub-word false positives like 'door' in 'indoors'
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            return False
    return True


def validate_no_medical_scare(text: str) -> bool:
    """Ensure no medical scaremongering or clinical diagnoses."""
    lowered = text.lower()
    for word in MEDICAL_SCARE_BLACKLIST:
        if word in lowered:
            return False
    return True


def validate_language_script(text: str, expected_lang: str) -> bool:
    """Check Devanagari character ratio for Hindi and Latin for English."""
    if not text.strip():
        return False

    devanagari_chars = len(re.findall(r"[\u0900-\u097F]", text))
    latin_chars = len(re.findall(r"[a-zA-Z]", text))
    total_alpha = devanagari_chars + latin_chars
    if total_alpha == 0:
        return True

    if expected_lang.lower() in ("hi", "hindi"):
        return (devanagari_chars / total_alpha) >= 0.60
    else:
        return (latin_chars / total_alpha) >= 0.60


def validate_no_hallucinated_digits(text: str, input_facts: dict[str, Any]) -> bool:
    """Ensure no digits appear in text that were not explicitly in input facts."""
    found_digits = re.findall(r"\b\d+\b", text)
    if not found_digits:
        return True

    # Extract all numbers from input facts
    valid_numbers = set()
    for v in input_facts.values():
        if isinstance(v, (int, float)):
            valid_numbers.add(str(int(v)))
            valid_numbers.add(str(v))
        elif isinstance(v, str):
            for d in re.findall(r"\b\d+\b", v):
                valid_numbers.add(d)

    for num in found_digits:
        if num not in valid_numbers:
            return False
    return True


def validate_announcement(text: str, expected_lang: str, input_facts: dict[str, Any]) -> ValidationResult:
    """Run full validator suite on generated announcement."""
    rules = {
        "word_limit": validate_word_limit(text, max_words=22),  # allowance for Hindi compound words
        "sentence_count": validate_sentence_count(text, max_sentences=2),
        "no_indoor_ventilation": validate_no_indoor_ventilation(text),
        "no_medical_scare": validate_no_medical_scare(text),
        "language_script": validate_language_script(text, expected_lang),
        "no_hallucinated_digits": validate_no_hallucinated_digits(text, input_facts),
    }

    reasons = [rule for rule, passed in rules.items() if not passed]
    return ValidationResult(
        passed=all(rules.values()),
        rule_results=rules,
        failure_reasons=reasons,
    )
