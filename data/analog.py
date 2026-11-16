"""
analog.py: which target(s) each Earth site is compared with, read from its "Analog for" text.

A Moon analog is compared only with the Moon target, a Mars analog only with the Mars
target, and a site that names both (or says "both") with both.
Typo safety: whole words only ("Mars" does not match "marsh"), any capitals, and
"lunar" / "Martian" count too. If the text names neither body, we show BOTH targets
(never hide data because of a typo) and build.py prints a warning to fix the Sheet.
"""
import re

# Words that mark each target type. "both" marks both.
WORDS = {"moon_target": r"\b(moon|lunar)\b", "mars_target": r"\b(mars|martian)\b"}
BOTH = r"\bboth\b"
GROUP_NAMES = {("moon_target",): "Moon analogs", ("mars_target",): "Mars analogs",
               ("moon_target", "mars_target"): "Moon and Mars analogs"}


def named_targets(analog_for):
    """Target types the text names, e.g. 'Mars (dust storms)' -> ['mars_target']. Empty if none."""
    text = str(analog_for).lower()
    return [kind for kind, pattern in WORDS.items() if re.search(pattern, text) or re.search(BOTH, text)]


def compared_targets(analog_for):
    """Target types this site is compared with. Unrecognised text -> both (never hide data)."""
    return named_targets(analog_for) or list(WORDS)


def group_name(analog_for):
    """Map filter group: 'Moon analogs', 'Mars analogs' or 'Moon and Mars analogs'."""
    return GROUP_NAMES[tuple(compared_targets(analog_for))]


def keep_matching(scores, sites):
    """Only the score rows for targets each site is compared with."""
    analog_for = sites.set_index("name")["analog_for"]
    keep = [row.target_type in compared_targets(analog_for.get(row.site)) for row in scores.itertuples()]
    return scores[keep]


def warnings(sites):
    """Earth sites whose 'Analog for' names neither the Moon nor Mars (probably a typo)."""
    earth = sites[sites["type"] == "earth"]
    return [f"'Analog for' of {name} names neither Moon nor Mars ({text!r}): both targets shown. Fix the Sheet."
            for name, text in zip(earth["name"], earth["analog_for"]) if not named_targets(text)]
