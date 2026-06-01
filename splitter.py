"""
splitter.py — Master Plot File Splitter & Executor

Reads src/master_plots.py, splits it into individual plot code blocks based on
comment markers (# 1, # 2, # 3, ...), saves each block as a code snippet,
executes all plots cumulatively in a shared namespace, and saves the resulting
figures as PNG images.

Generated output:
    figures/          — PNG images for each successfully executed plot
    code_snippets/    — Raw code text for each plot (without imports)
    data.json         — Metadata skeleton for all successful plots
    failed_plots.json — Error report for any plots that failed execution

Usage:
    Run from the project root directory:
        python splitter.py

Requirements:
    - Python 3.14+
    - matplotlib, numpy (and any other libraries used in master_plots.py)
"""

# ─── GLOBAL BACKEND SETUP ─────────────────────────────────────────────────────
# Set the Agg (non-interactive) backend BEFORE any other matplotlib imports.
# This prevents GUI windows from opening during batch execution.
import matplotlib
matplotlib.use('Agg')

# ─── STANDARD LIBRARY IMPORTS ─────────────────────────────────────────────────
import re
import json
import sys
import traceback
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# ANSI COLOR CODES — for colored terminal output using only Python built-ins
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
    WHITE   = "\033[97m"


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING HELPERS — clean, colored status messages
# ═══════════════════════════════════════════════════════════════════════════════

def log_info(msg: str) -> None:
    """Print an informational message (cyan icon)."""
    print(f"  {Colors.CYAN}i{Colors.RESET}  {msg}")


def log_success(msg: str) -> None:
    """Print a success message (green checkmark)."""
    print(f"  {Colors.GREEN}+{Colors.RESET}  {msg}")


def log_warning(msg: str) -> None:
    """Print a warning message (yellow exclamation)."""
    print(f"  {Colors.YELLOW}!{Colors.RESET}  {Colors.YELLOW}{msg}{Colors.RESET}")


def log_error(msg: str) -> None:
    """Print an error message (red X)."""
    print(f"  {Colors.RED}x{Colors.RESET}  {Colors.RED}{msg}{Colors.RESET}")


def log_header(msg: str) -> None:
    """Print a prominent section header."""
    width = 60
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * width}{Colors.RESET}")
    print(f"  {Colors.BOLD}{Colors.MAGENTA}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'=' * width}{Colors.RESET}\n")


def log_step(step_num: int, msg: str) -> None:
    """Print a numbered step heading."""
    print(f"\n  {Colors.BOLD}{Colors.BLUE}[STEP {step_num}]{Colors.RESET}  {Colors.BOLD}{msg}{Colors.RESET}")
    print(f"  {Colors.DIM}{'-' * 50}{Colors.RESET}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    log_header("MATPLOTLIB MASTER PLOT SPLITTER")

    # ─── CONFIGURATION ────────────────────────────────────────────────────────
    master_file      = Path("src/master_plots.py")
    figures_dir      = Path("matplotlib-gallery/figures")
    snippets_dir     = Path("matplotlib-gallery/code_snippets")
    data_json_path   = Path("matplotlib-gallery/data.json")
    failed_json_path = Path("matplotlib-gallery/failed_plots.json")

    # Regex for plot markers: lines containing ONLY "# " followed by digits
    # and optional trailing whitespace — nothing else on the line.
    marker_pattern = re.compile(r'^# \d+\s*$', re.MULTILINE)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 1 — SETUP: Verify master file and create output directories
    # ══════════════════════════════════════════════════════════════════════════
    log_step(1, "SETUP — Verifying master file & creating directories")

    # Check that the master file exists
    if not master_file.exists():
        log_error(f"Master file not found: {master_file.resolve()}")
        log_error("Make sure you are running this script from the project root directory.")
        log_error(f"Expected file at: {master_file}")
        sys.exit(1)
    log_success(f"Master file found: {master_file}")

    # Create output directories, handling permission errors
    for directory in [figures_dir, snippets_dir]:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            log_success(f"Directory ready: {directory}/")
        except PermissionError:
            log_error(f"Permission denied when creating directory: {directory}/")
            log_error("Check your filesystem permissions and try again.")
            sys.exit(1)
        except OSError as e:
            log_error(f"OS error creating directory {directory}/: {e}")
            sys.exit(1)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 — PARSE: Read master file, extract imports & plot blocks
    # ══════════════════════════════════════════════════════════════════════════
    log_step(2, "PARSE — Reading and splitting master file")

    # Read the entire master file as a string
    content = master_file.read_text(encoding="utf-8")
    log_info(f"Read {len(content):,} characters ({len(content.splitlines()):,} lines) from {master_file}")

    # Find all plot markers in the file
    markers = list(marker_pattern.finditer(content))

    if not markers:
        log_error("No plot markers found in the master file!")
        log_error("Expected standalone comment lines like:  # 1   # 2   # 3  ...")
        sys.exit(1)

    log_info(f"Found {len(markers)} plot markers")

    # ── Extract the IMPORTS BLOCK ─────────────────────────────────────────────
    # Everything from the top of the file up to (but not including) the first
    # plot marker. This typically contains import statements and shared variables.
    imports_block = content[:markers[0].start()].strip()
    log_success(f"Extracted imports block ({len(imports_block.splitlines())} lines)")

    # ── Extract each plot's code block ────────────────────────────────────────
    # The code between one marker and the next (or end of file).
    # The marker line itself is NOT included in the code block.
    plots = {}  # {plot_number (int): code_string}

    for i, marker in enumerate(markers):
        # Extract the plot number from the marker text (e.g., "# 42" → 42)
        plot_num = int(re.search(r'\d+', marker.group()).group())

        # Code starts right after the marker line ends
        code_start = marker.end()

        # Code ends at the start of the next marker, or at end of file
        if i + 1 < len(markers):
            code_end = markers[i + 1].start()
        else:
            code_end = len(content)

        # Extract the raw code block and strip leading/trailing newlines
        code_block = content[code_start:code_end]
        code_block = code_block.strip('\n').strip('\r\n').strip('\r')

        plots[plot_num] = code_block
        log_info(f"  Plot #{plot_num:<4}  {len(code_block.splitlines()):>3} lines")

    log_success(f"Parsed {len(plots)} plot code blocks successfully")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 3 — SAVE CODE SNIPPETS: Write each plot's code to a .txt file
    # ══════════════════════════════════════════════════════════════════════════
    log_step(3, "SAVE — Writing code snippets to files")

    for plot_num in sorted(plots.keys()):
        snippet_path = snippets_dir / f"{plot_num}.txt"

        # Strip leading and trailing blank lines before saving
        clean_code = plots[plot_num].strip()
        
        # Add the import instruction comment at the top
        final_code = "# NOTE: Please import relevant libraries (e.g., import matplotlib.pyplot as plt, import numpy as np) before running this snippet.\n\n" + clean_code

        snippet_path.write_text(final_code, encoding="utf-8")
        log_success(f"Saved: {snippet_path}")

    log_success(f"All {len(plots)} code snippets saved to {snippets_dir}/")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 4 — EXECUTE: Run plots cumulatively and save figures
    # ══════════════════════════════════════════════════════════════════════════
    log_step(4, "EXECUTE — Running plots cumulatively & saving figures")

    # Create a single shared namespace for all plots.
    # Variables defined in earlier plots will be available in later plots.
    namespace = {}

    # Execute the imports block first to set up the shared environment
    # (imports, shared variables like x, y1, y2, etc.)
    try:
        exec(imports_block, namespace)
        log_success("Imports block executed successfully in shared namespace")
    except Exception as e:
        log_error(f"Failed to execute imports block: {e}")
        log_error("Cannot continue without imports. Exiting.")
        sys.exit(1)

    successful_plots = []       # List of plot numbers that executed without errors
    failed_plots     = []       # List of (plot_num, error_message) tuples

    for plot_num in sorted(plots.keys()):
        plot_code = plots[plot_num]

        # ── Inject plt.savefig() to capture figures ───────────────────────────
        # The master file uses plt.show() to display plots interactively.
        # Since we're using the Agg backend (non-interactive), we replace each
        # plt.show() call with plt.savefig() so the figure is saved to disk.
        modified_code = plot_code.replace(
            'plt.show()',
            f'plt.savefig("matplotlib-gallery/figures/{plot_num}.png", dpi=150, bbox_inches="tight")'
        )

        try:
            # Execute this plot's code in the SAME shared namespace
            exec(modified_code, namespace)
            successful_plots.append(plot_num)
            log_success(f"Plot #{plot_num:<4} — executed and saved to figures/{plot_num}.png")

        except Exception as e:
            # Catch any exception, log it, and continue to the next plot
            error_msg = f"{type(e).__name__}: {e}"
            failed_plots.append((plot_num, error_msg))
            log_warning(f"Plot #{plot_num:<4} — FAILED: {error_msg}")

            # Print the full traceback for debugging purposes
            tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
            for line in tb_lines:
                for sub_line in line.rstrip().split('\n'):
                    log_warning(f"    {sub_line}")

        finally:
            # Clean up all matplotlib figures after each plot to free memory
            # and prevent cross-contamination between plots
            try:
                if 'plt' in namespace:
                    namespace['plt'].close('all')
                else:
                    matplotlib.pyplot.close('all')
            except Exception:
                pass

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 5 — GENERATE: Create data.json and failed_plots.json
    # ══════════════════════════════════════════════════════════════════════════
    log_step(5, "GENERATE — Creating JSON metadata files")

    # ── data.json — metadata skeleton for successful plots ────────────────────
    data_entries = []
    for plot_num in sorted(successful_plots):
        data_entries.append({
            "id": plot_num,
            "name": f"Plot {plot_num}",
            "difficulty": "Beginner",
            "tags": [],
            "image": f"figures/{plot_num}.png",
            "code_file": f"code_snippets/{plot_num}.txt"
        })

    data_json_path.write_text(
        json.dumps(data_entries, indent=2),
        encoding="utf-8"
    )
    log_success(f"Created {data_json_path} with {len(data_entries)} entries")

    # ── failed_plots.json — error report for failed plots ─────────────────────
    failed_entries = []
    for plot_num, error_msg in failed_plots:
        failed_entries.append({
            "plot_number": plot_num,
            "error": error_msg
        })

    failed_json_path.write_text(
        json.dumps(failed_entries, indent=2),
        encoding="utf-8"
    )
    log_success(f"Created {failed_json_path} with {len(failed_entries)} entries")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 6 — FINAL SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    log_step(6, "SUMMARY — Final report")

    total        = len(plots)
    passed       = len(successful_plots)
    failed_count = len(failed_plots)

    print()
    print(f"  {Colors.BOLD}{'-' * 50}{Colors.RESET}")
    print(f"  {Colors.BOLD}Total plots found:       {Colors.CYAN}{total}{Colors.RESET}")
    print(f"  {Colors.BOLD}Successfully executed:    {Colors.GREEN}{passed}{Colors.RESET}")
    print(f"  {Colors.BOLD}Failed:                  ", end="")
    if failed_count == 0:
        print(f"{Colors.GREEN}{failed_count}{Colors.RESET}")
    else:
        print(f"{Colors.RED}{failed_count}{Colors.RESET}")

    if failed_plots:
        failed_nums = [str(f[0]) for f in failed_plots]
        print(f"  {Colors.BOLD}Failed plot numbers:     {Colors.RED}{', '.join(failed_nums)}{Colors.RESET}")

    print()
    print(f"  {Colors.BOLD}Generated files:{Colors.RESET}")
    print(f"    {Colors.DIM}|--{Colors.RESET} {figures_dir}/            ({passed} PNG figures)")
    print(f"    {Colors.DIM}|--{Colors.RESET} {snippets_dir}/      ({total} code snippets)")
    print(f"    {Colors.DIM}|--{Colors.RESET} {data_json_path}            (plot metadata)")
    print(f"    {Colors.DIM}|--{Colors.RESET} {failed_json_path}    (failure report)")
    print(f"  {Colors.BOLD}{'-' * 50}{Colors.RESET}")
    print()

    if failed_count == 0:
        log_success("All plots processed successfully!")
    else:
        log_warning(f"{failed_count} plot(s) failed. Check {failed_json_path} for details.")

    print()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
