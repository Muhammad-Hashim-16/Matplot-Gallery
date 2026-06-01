"""
merge_names.py — Merge AI-Generated Names into data.json

Reads AI responses from ai_responses.json (a JSON array of objects with
id, name, difficulty, and tags fields) and merges them into data.json,
overwriting the placeholder values.

Input:
    data.json         — Current plot metadata (with placeholder names)
    ai_responses.json — Combined AI responses (all batches in one JSON array)

Output:
    data.json         — Updated with real names, difficulties, and tags

Usage:
    1. Collect all AI JSON responses into a single file: ai_responses.json
       The file should contain one JSON array with all entries, e.g.:
       [
         {"id": 1, "name": "Sine Cosine Line Plot", "difficulty": "Beginner", "tags": ["Line", "Mathematical"]},
         {"id": 2, "name": "Advanced Color Scatter", "difficulty": "Intermediate", "tags": ["Scatter", "Colormap"]},
         ...
       ]
    2. Run: python merge_names.py
"""

import json
import sys
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# ANSI COLOR CODES
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    """ANSI escape codes for colored terminal output."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def log_info(msg):
    print(f"  {Colors.CYAN}i{Colors.RESET}  {msg}")

def log_success(msg):
    print(f"  {Colors.GREEN}+{Colors.RESET}  {msg}")

def log_warning(msg):
    print(f"  {Colors.YELLOW}!{Colors.RESET}  {Colors.YELLOW}{msg}{Colors.RESET}")

def log_error(msg):
    print(f"  {Colors.RED}x{Colors.RESET}  {Colors.RED}{msg}{Colors.RESET}")

def log_header(msg):
    width = 60
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * width}{Colors.RESET}")
    print(f"  {Colors.BOLD}{Colors.MAGENTA}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'=' * width}{Colors.RESET}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

ALLOWED_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}

ALLOWED_TAGS = {
    "Line", "Bar", "Scatter", "Histogram", "Pie", "3D", "Heatmap",
    "Statistical", "Boxplot", "Violin", "Surface", "Contour", "Quiver",
    "Stream", "Polar", "Subplots", "Animation", "Colormap", "Mathematical",
    "Distribution", "Time Series", "Multi-line", "Filled", "Logarithmic",
    "Error Bars", "Stem", "Step", "Bubble", "Radar", "Sankey"
}


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    log_header("MERGE AI RESPONSES INTO DATA.JSON")

    # ── Configuration ─────────────────────────────────────────────────────────
    data_json_path      = Path("matplotlib-gallery/data.json")
    ai_responses_path   = Path("ai_responses.json")

    # ── Validate input files exist ────────────────────────────────────────────
    if not data_json_path.exists():
        log_error(f"{data_json_path} not found. Run splitter.py first.")
        sys.exit(1)

    if not ai_responses_path.exists():
        log_error(f"{ai_responses_path} not found.")
        log_error("Create this file by combining all AI JSON responses into one array.")
        log_error("Example format:")
        log_error('  [{"id": 1, "name": "...", "difficulty": "...", "tags": [...]}, ...]')
        sys.exit(1)

    # ── Load data.json ────────────────────────────────────────────────────────
    data = json.loads(data_json_path.read_text(encoding="utf-8"))
    log_success(f"Loaded {len(data)} entries from {data_json_path}")

    # Build a lookup dict keyed by id for fast matching
    data_by_id = {entry["id"]: entry for entry in data}

    # ── Load ai_responses.json ────────────────────────────────────────────────
    try:
        ai_responses = json.loads(ai_responses_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON in {ai_responses_path}: {e}")
        log_error("Make sure the file contains a valid JSON array.")
        sys.exit(1)

    if not isinstance(ai_responses, list):
        log_error(f"{ai_responses_path} must contain a JSON array at the top level.")
        sys.exit(1)

    log_success(f"Loaded {len(ai_responses)} AI responses from {ai_responses_path}")

    # ── Merge responses into data ─────────────────────────────────────────────
    updated_count   = 0
    warning_count   = 0
    skipped_count   = 0

    for response in ai_responses:
        # Validate that the response has an "id" field
        if "id" not in response:
            log_warning("Response missing 'id' field — skipping")
            skipped_count += 1
            continue

        plot_id = response["id"]

        # Check that this id exists in data.json
        if plot_id not in data_by_id:
            log_warning(f"Plot #{plot_id} not found in data.json — skipping")
            skipped_count += 1
            continue

        entry = data_by_id[plot_id]
        has_warnings = False

        # ── Merge "name" ──────────────────────────────────────────────────────
        if "name" in response:
            entry["name"] = response["name"]
        else:
            log_warning(f"Plot #{plot_id}: missing 'name' field in AI response")
            has_warnings = True

        # ── Merge "difficulty" with validation ────────────────────────────────
        if "difficulty" in response:
            difficulty = response["difficulty"]
            if difficulty not in ALLOWED_DIFFICULTIES:
                log_warning(
                    f"Plot #{plot_id}: invalid difficulty '{difficulty}' "
                    f"(expected one of: {', '.join(sorted(ALLOWED_DIFFICULTIES))})"
                )
                has_warnings = True
            # Still save it even if invalid
            entry["difficulty"] = difficulty
        else:
            log_warning(f"Plot #{plot_id}: missing 'difficulty' field in AI response")
            has_warnings = True

        # ── Merge "tags" with validation ──────────────────────────────────────
        if "tags" in response:
            tags = response["tags"]
            if isinstance(tags, list):
                # Check each tag against the allowed list
                invalid_tags = [t for t in tags if t not in ALLOWED_TAGS]
                if invalid_tags:
                    log_warning(
                        f"Plot #{plot_id}: invalid tags: {invalid_tags}"
                    )
                    has_warnings = True
                # Still save all tags even if some are invalid
                entry["tags"] = tags
            else:
                log_warning(f"Plot #{plot_id}: 'tags' is not a list — skipping tags")
                has_warnings = True
        else:
            log_warning(f"Plot #{plot_id}: missing 'tags' field in AI response")
            has_warnings = True

        if has_warnings:
            warning_count += 1

        updated_count += 1
        log_success(f"Plot #{plot_id:<4} -> {entry.get('name', '???')}")

    # ── Save updated data.json ────────────────────────────────────────────────
    data_json_path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )
    log_success(f"Saved updated {data_json_path}")

    # ── Final summary ─────────────────────────────────────────────────────────
    print()
    print(f"  {Colors.BOLD}{'-' * 50}{Colors.RESET}")
    print(f"  {Colors.BOLD}Total entries in data.json:    {Colors.CYAN}{len(data)}{Colors.RESET}")
    print(f"  {Colors.BOLD}AI responses received:         {Colors.CYAN}{len(ai_responses)}{Colors.RESET}")
    print(f"  {Colors.BOLD}Successfully merged:           {Colors.GREEN}{updated_count}{Colors.RESET}")
    print(f"  {Colors.BOLD}Merged with warnings:          ", end="")
    if warning_count > 0:
        print(f"{Colors.YELLOW}{warning_count}{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}0{Colors.RESET}")
    print(f"  {Colors.BOLD}Skipped (no match):            ", end="")
    if skipped_count > 0:
        print(f"{Colors.RED}{skipped_count}{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}0{Colors.RESET}")
    print(f"  {Colors.BOLD}{'-' * 50}{Colors.RESET}")
    print()

    if updated_count == len(data):
        log_success("All plots in data.json have been updated!")
    elif updated_count > 0:
        log_info(
            f"{len(data) - updated_count} plot(s) in data.json were not updated "
            f"(no matching AI response)."
        )
    else:
        log_warning("No entries were updated. Check your ai_responses.json file.")

    print()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
