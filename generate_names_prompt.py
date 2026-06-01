"""
generate_names_prompt.py — AI Prompt Generator for Plot Naming

Reads data.json and each plot's code snippet, then generates batched prompts
(10 plots per batch) that can be pasted into any AI chatbot to get back
professional names, difficulty levels, and tags for each plot.

Output:
    naming_prompts.txt — All batch prompts, ready to copy-paste into AI

Usage:
    python generate_names_prompt.py
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
# PROMPT TEMPLATE — the instruction block sent to the AI for each batch
# ═══════════════════════════════════════════════════════════════════════════════

PROMPT_TEMPLATE = """\
You are analyzing Python matplotlib code snippets. For each plot below, provide:
1. A short, descriptive, professional name for the plot (max 6 words)
2. Difficulty level: exactly one of these three words only: Beginner, Intermediate, Advanced
   - Beginner: basic single plots, simple customization, standard chart types
   - Intermediate: multiple subplots, custom styling, annotations, twin axes, moderately complex data manipulation
   - Advanced: 3D plots, animations, highly custom layouts, complex statistical plots, custom colormaps, interactive elements
3. Tags: a list of relevant tags from this list only:
   ["Line", "Bar", "Scatter", "Histogram", "Pie", "3D", "Heatmap", "Statistical", "Boxplot", "Violin", "Surface", "Contour", "Quiver", "Stream", "Polar", "Subplots", "Animation", "Colormap", "Mathematical", "Distribution", "Time Series", "Multi-line", "Filled", "Logarithmic", "Error Bars", "Stem", "Step", "Bubble", "Radar", "Sankey"]
   Pick as many as apply, minimum 1, maximum 4.

Return your answer as a JSON array ONLY, no explanation, no markdown, just raw JSON. Format:
[
  {{"id": 1, "name": "Your Plot Name", "difficulty": "Beginner", "tags": ["Line", "Mathematical"]}},
  ...
]

Here are the plots:
"""


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    log_header("AI PROMPT GENERATOR FOR PLOT NAMING")

    # ── Configuration ─────────────────────────────────────────────────────────
    data_json_path  = Path("matplotlib-gallery/data.json")
    snippets_dir    = Path("matplotlib-gallery/code_snippets")
    output_path     = Path("naming_prompts.txt")
    batch_size      = 10

    # ── Validate inputs ──────────────────────────────────────────────────────
    if not data_json_path.exists():
        log_error(f"{data_json_path} not found. Run splitter.py first.")
        sys.exit(1)

    if not snippets_dir.exists():
        log_error(f"{snippets_dir}/ directory not found. Run splitter.py first.")
        sys.exit(1)

    # ── Read data.json ────────────────────────────────────────────────────────
    data = json.loads(data_json_path.read_text(encoding="utf-8"))
    log_success(f"Loaded {len(data)} plot entries from {data_json_path}")

    # ── Read all code snippets ────────────────────────────────────────────────
    plot_codes = {}  # {id: code_string}

    for entry in data:
        plot_id = entry["id"]
        snippet_path = snippets_dir / f"{plot_id}.txt"

        if snippet_path.exists():
            plot_codes[plot_id] = snippet_path.read_text(encoding="utf-8")
        else:
            log_warning(f"Code snippet not found: {snippet_path} — skipping plot #{plot_id}")

    log_success(f"Read {len(plot_codes)} code snippets from {snippets_dir}/")

    # ── Sort plot IDs for consistent ordering ─────────────────────────────────
    sorted_ids = sorted(plot_codes.keys())

    # ── Group into batches of 10 ──────────────────────────────────────────────
    batches = []
    for i in range(0, len(sorted_ids), batch_size):
        batch = sorted_ids[i:i + batch_size]
        batches.append(batch)

    log_info(f"Created {len(batches)} batches of up to {batch_size} plots each")

    # ── Generate prompts for each batch ───────────────────────────────────────
    all_prompts = []

    for batch_idx, batch_ids in enumerate(batches, start=1):
        # Start with the instruction template
        prompt_parts = [PROMPT_TEMPLATE]

        # Append each plot's code snippet
        for plot_id in batch_ids:
            code = plot_codes[plot_id]
            prompt_parts.append(f"--- Plot {plot_id} ---")
            prompt_parts.append(code)
            prompt_parts.append("")  # blank line between plots

        # Combine into a single prompt string
        full_prompt = "\n".join(prompt_parts).rstrip()

        # Wrap with batch header/footer for easy identification
        batch_header = (
            f"{'=' * 70}\n"
            f"  BATCH {batch_idx} OF {len(batches)}  "
            f"(Plots {batch_ids[0]} - {batch_ids[-1]})\n"
            f"{'=' * 70}\n"
        )
        batch_footer = f"\n{'=' * 70}\n"

        all_prompts.append(batch_header + full_prompt + batch_footer)

        log_success(
            f"Batch {batch_idx}: Plots {batch_ids[0]}-{batch_ids[-1]} "
            f"({len(batch_ids)} plots)"
        )

    # ── Write all prompts to output file ──────────────────────────────────────
    separator = "\n\n\n"
    output_content = separator.join(all_prompts)
    output_path.write_text(output_content, encoding="utf-8")

    log_success(f"Saved all prompts to {output_path}")

    # ── Final summary ─────────────────────────────────────────────────────────
    print()
    print(f"  {Colors.BOLD}{'-' * 50}{Colors.RESET}")
    print(f"  {Colors.BOLD}Total plots:           {Colors.CYAN}{len(plot_codes)}{Colors.RESET}")
    print(f"  {Colors.BOLD}Batches generated:     {Colors.CYAN}{len(batches)}{Colors.RESET}")
    print(f"  {Colors.BOLD}Output file:           {Colors.GREEN}{output_path}{Colors.RESET}")
    print(f"  {Colors.BOLD}{'-' * 50}{Colors.RESET}")
    print()
    print(f"  {Colors.BOLD}Next steps:{Colors.RESET}")
    print(f"    1. Open {Colors.CYAN}naming_prompts.txt{Colors.RESET}")
    print(f"    2. Copy each batch prompt into an AI chatbot")
    print(f"    3. Collect all JSON responses into {Colors.CYAN}ai_responses.json{Colors.RESET}")
    print(f"    4. Run {Colors.CYAN}python merge_names.py{Colors.RESET} to merge into data.json")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
