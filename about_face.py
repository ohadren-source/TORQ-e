"""
ABOUT_FACE: Zero Meta-Speak Filter (Future Actions Only)

Strips meta-speak about FUTURE/INTENTIONAL actions from all responses.
After tools execute, Claude has COMPLETE FREEDOM to explain, elaborate, analyze results.

CEMENT DEFINITION OF META-SPEAK:
Meta-speak = Text describing actions Claude is ABOUT TO TAKE, not actions he already took.
- FORBIDDEN (Future/Intentional): "Running...", "Fetching...", "I'm going to...", "I'll now...", "Let me...", "Before I...", "First I'll..."
- FORBIDDEN (Present-tense process): "analyzing now", "checking", "pulling data", "running query"
- ALLOWED (Past tense analysis): "The data shows...", "analysis reveals...", "I found...", "This indicates..."
- ALLOWED (Elaboration): Explaining what was found, why it matters, what it means

RULE: Never narrate the process BEFORE. Complete freedom to explain AFTER.
"Running metrics now" ✗
"The metrics show enrollment dropped 3%" ✓
"""

import re
from typing import List, Tuple

# Precise regex patterns for FUTURE-tense meta-speak ONLY
# These catch "I'm about to do X" but NOT "The analysis shows X"
META_SPEAK_PATTERNS = {
    "future_intentional": [
        r"\bi'm\s+going\s+to\s+",
        r"\bi'll\s+(?:now\s+)?(?:pull|fetch|run|execute|query|analyze)",
        r"\blet\s+me\s+(?:pull|fetch|run|execute|query|analyze|check)",
        r"\bbefore\s+i\s+(?:pull|fetch|run|execute|query)",
        r"\bfirst\s+i'll\s+(?:pull|fetch|run|execute|query)",
        r"\bnow\s+(?:i|let)\s+(?:pull|fetch|run|execute|query)",
        r"\bjust\s+(?:let\s+me|pull|fetch)\s+",
    ],
    "present_process_action": [
        r"\brunning\s+(?:all|the|these|my|metrics|queries)",
        r"\bfetching\s+(?:live\s+)?data",
        r"\bpulling\s+",
        r"\bexecuting\s+",
        r"\bquerying\s+",
    ],
}

# Combine all patterns into one compiled regex (case-insensitive)
_COMPILED_PATTERN = re.compile(
    "|".join(
        pattern
        for patterns in META_SPEAK_PATTERNS.values()
        for pattern in patterns
    ),
    re.IGNORECASE
)


def detect_meta_speak(text: str) -> List[Tuple[str, int, int]]:
    """
    Detect meta-speak patterns in text.
    Returns list of (matched_text, start_pos, end_pos) tuples.
    """
    matches = []
    for match in _COMPILED_PATTERN.finditer(text):
        matches.append((match.group(), match.start(), match.end()))
    return matches


def strip_meta_speak(text: str) -> str:
    """
    Remove meta-speak from text by detecting and removing matching patterns.
    Also removes entire lines that are purely meta-speak.
    """
    if not text:
        return text

    # First pass: Remove patterns mid-sentence
    cleaned = _COMPILED_PATTERN.sub("", text)

    # Second pass: Remove lines that became empty or are purely whitespace after removal
    lines = cleaned.split("\n")
    filtered_lines = [line for line in lines if line.strip()]

    # Third pass: Remove lines that are ONLY meta-speak (like standalone "Running metrics now")
    final_lines = []
    for line in filtered_lines:
        # Check if the line is essentially pure meta-speak
        if _COMPILED_PATTERN.sub("", line).strip():
            final_lines.append(line)

    result = "\n".join(final_lines).strip()
    return result if result else ""


def is_meta_speak_only(text: str) -> bool:
    """Check if text is purely meta-speak (no substantial content)."""
    cleaned = strip_meta_speak(text)
    return len(cleaned.strip()) == 0


def about_face(text: str, strict: bool = False) -> str:
    """
    Apply ABOUT_FACE filter to remove meta-speak.

    Args:
        text: The response text to filter
        strict: If True, also remove sentences with weak meta-speak patterns

    Returns:
        Filtered text with meta-speak removed
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = strip_meta_speak(text)

    # In strict mode, also filter lines that START with certain weak patterns
    if strict:
        lines = cleaned.split("\n")
        strict_lines = []
        weak_patterns = [
            r"^let\s+me\s+",
            r"^i\s+can\s+",
            r"^to\s+summarize",
            r"^in\s+summary",
        ]
        weak_regex = re.compile("|".join(weak_patterns), re.IGNORECASE)

        for line in lines:
            if not weak_regex.match(line.strip()):
                strict_lines.append(line)
        cleaned = "\n".join(strict_lines).strip()

    return cleaned


# Testing helper
if __name__ == "__main__":
    test_cases = [
        ("Running all six aggregate metrics now — fetching live data before summarizing.", "STRIP (present process)"),
        ("I'm going to pull the enrollment data and analyze it.", "STRIP (future intentional)"),
        ("enrollment_rate: 87.3% | claims_processing: 95.2%", "KEEP (results)"),
        ("Let me check the governance log and pull recent actions.", "STRIP (future intentional)"),
        ("🟢 HIGH confidence (0.95) | Enrollment: 87.3% | Source: emedny.org", "KEEP (results)"),
        ("The analysis reveals that enrollment dropped 3% this quarter.", "KEEP (past analysis)"),
        ("Based on the data I found, compliance is at 92%.", "KEEP (past explanation)"),
        ("This indicates a systematic issue in provider verification.", "KEEP (elaboration)"),
    ]

    for test, expected in test_cases:
        filtered = about_face(test)
        print(f"ORIGINAL: {test}")
        print(f"FILTERED: {filtered}")
        print(f"EXPECTED: {expected}")
        print(f"IS META-ONLY: {is_meta_speak_only(test)}")
        print()
