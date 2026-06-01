# MatplotGallery 📊

A curated gallery of **90+ matplotlib plots** from beginner to advanced level, showcasing the full breadth of Python's most popular data visualization library. Built as a modern Progressive Web App (PWA) with offline support.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Latest-orange?logo=python&logoColor=white)
![PWA](https://img.shields.io/badge/PWA-Enabled-6366f1?logo=pwa&logoColor=white)

---

## 🚀 Getting Started

Follow these steps to set up and populate the gallery:

### 1. Place your master plots file

Copy your `master_plots.py` into the `src/` folder:

```
src/master_plots.py
```

### 2. Format your plot markers

Each plot in `master_plots.py` must be separated by a standalone comment marker in this exact format:

```python
# 1
plt.figure()
plt.plot(x, y)
plt.title("My First Plot")
plt.savefig("figures/1.png", dpi=150, bbox_inches='tight')
plt.close()

# 2
plt.figure()
plt.bar(categories, values)
plt.title("My Bar Chart")
plt.savefig("figures/2.png", dpi=150, bbox_inches='tight')
plt.close()
```

> **Important:** The marker must be a standalone line with ONLY `# ` followed by the plot number — nothing else on that line.

### 3. Ensure each plot saves its figure

Every plot must end with:

```python
plt.savefig("figures/{n}.png", dpi=150, bbox_inches='tight')
plt.close()
```

Where `{n}` is the plot number matching the marker.

### 4. Run the splitter

```bash
python splitter.py
```

This will:
- Parse `src/master_plots.py` into individual plot code blocks
- Save each block to `code_snippets/{n}.txt`
- Execute all plots cumulatively and save figures to `figures/{n}.png`
- Generate `data.json` with placeholder metadata

### 5. Generate AI naming prompts

```bash
python generate_names_prompt.py
```

This creates `naming_prompts.txt` with batch prompts ready to paste into an AI chatbot.

### 6. Get AI-generated names

Open `naming_prompts.txt` and copy each batch prompt into any AI chatbot (Claude, ChatGPT, Gemini). The AI will return professional names, difficulty levels, and tags for each plot.

### 7. Merge AI responses

Combine all AI JSON responses into a single file called `ai_responses.json`:

```json
[
  {"id": 1, "name": "Sine Cosine Line Plot", "difficulty": "Beginner", "tags": ["Line", "Mathematical"]},
  {"id": 2, "name": "Advanced Scatter Plot", "difficulty": "Intermediate", "tags": ["Scatter", "Colormap"]},
  ...
]
```

Then run:

```bash
python merge_names.py
```

### 8. View the gallery

Open `index.html` with **VS Code Live Server** (or any local HTTP server):

```
Right-click index.html → "Open with Live Server"
```

> **Note:** A local server is required because the app fetches `data.json` and images via JavaScript.

---

## 🚀 Deployment Notes

- **Always use VS Code Live Server** to open the project, never open `index.html` directly by double-clicking.
- The `fetch()` API does not work over the `file://` protocol.
- For GitHub Pages deployment: push the entire project folder, enable Pages from the repo settings, and update the SW scope if hosting in a subdirectory.

---

## 📁 Project Structure

```
matplotlib-gallery/
├── figures/                    # Generated PNG images for each plot
├── code_snippets/              # Raw Python code for each plot (no imports)
├── src/
│   └── master_plots.py         # Master file containing all plots
├── icons/                      # PWA icons (8 sizes)
│   ├── icon-72.png
│   ├── icon-96.png
│   ├── icon-128.png
│   ├── icon-144.png
│   ├── icon-152.png
│   ├── icon-192.png
│   ├── icon-384.png
│   └── icon-512.png
├── index.html                  # Main gallery page
├── about.html                  # About page
├── style.css                   # Main stylesheet
├── app.js                      # Gallery application logic
├── search.js                   # Search and filter functionality
├── data.json                   # Plot metadata (name, difficulty, tags, paths)
├── manifest.json               # PWA manifest
├── sw.js                       # Service worker (offline support)
├── splitter.py                 # Splits master_plots.py into individual plots
├── generate_names_prompt.py    # Generates AI prompts for plot naming
├── merge_names.py              # Merges AI responses into data.json
└── README.md                   # This file
```

### Key Files

| File | Purpose |
|------|---------|
| `splitter.py` | Parses the master file, extracts plots, executes them, saves figures and code snippets |
| `generate_names_prompt.py` | Creates batched prompts for AI chatbots to name and categorize plots |
| `merge_names.py` | Merges AI-generated names, difficulties, and tags back into `data.json` |
| `data.json` | Central metadata file linking each plot to its image, code, name, and tags |
| `manifest.json` | PWA configuration (app name, icons, theme, display mode) |
| `sw.js` | Service worker for offline caching and fast loading |

---

## 🎨 PWA Icons

The `icons/` folder contains **placeholder** icon files. Before deploying, replace them with real PNG icons at the following sizes:

| File | Size |
|------|------|
| `icon-72.png` | 72 × 72 px |
| `icon-96.png` | 96 × 96 px |
| `icon-128.png` | 128 × 128 px |
| `icon-144.png` | 144 × 144 px |
| `icon-152.png` | 152 × 152 px |
| `icon-192.png` | 192 × 192 px |
| `icon-384.png` | 384 × 384 px |
| `icon-512.png` | 512 × 512 px |

### Recommended Tool

Use [**RealFaviconGenerator**](https://realfavicongenerator.net/) to generate all required icon sizes from a single high-resolution source image. Upload a 512×512 or larger PNG and download the complete icon set.

---

## 🛠 Tech Stack

| Technology | Usage |
|------------|-------|
| **HTML5** | Page structure and semantic markup |
| **CSS3** | Styling, animations, responsive layout |
| **Vanilla JavaScript** | Gallery logic, search, filtering, PWA |
| **Service Worker API** | Offline caching and background sync |
| **Web App Manifest** | PWA installation and metadata |
| **Python 3.14** | Plot generation and data pipeline |
| **Matplotlib** | All plot visualizations |
| **NumPy** | Numerical data generation |

---

## 🐍 Python Version

This gallery showcases matplotlib plots written in **Python 3.14**. All plot code in `src/master_plots.py` and `code_snippets/` is compatible with Python 3.14 features and syntax.

Make sure you have Python 3.14+ installed to run the pipeline scripts:

```bash
python --version
# Python 3.14.x
```

---

## 👤 Credits

Created by **[Your Name]**

---

## 📄 License

This project is for educational and personal use.
