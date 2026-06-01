# MatplotGallery 📊

A curated gallery of **90+ matplotlib plots** from beginner to advanced level, showcasing the full breadth of Python's most popular data visualization library. The backend pipeline is powered by pure Python, and the frontend is a modern Progressive Web App (PWA) built with Vanilla HTML/JS/CSS.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Latest-orange?logo=python&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-black?logo=vercel&logoColor=white)

---

## 🚀 The Backend Pipeline

This project features a fully automated python pipeline that takes a single file containing all your matplotlib plots and instantly generates a production-ready website gallery.

### 1. Edit the Source Code
Open the file at `src/master_plots.py`. Each plot in this file must be separated by a standalone comment marker like `# 1`, `# 2`, etc.

```python
# 1
x = np.linspace(0, 10, 100)
plt.figure()
plt.plot(x, np.sin(x))
plt.title("My First Plot")
plt.savefig("matplotlib-gallery/figures/1.png", dpi=150, bbox_inches='tight')
plt.close()
```

### 2. Run the Splitter Engine
Open your terminal in the root project folder and run:
```bash
python splitter.py
```
This powerful script will automatically:
- Parse `src/master_plots.py` into individual plot blocks.
- Execute every plot cumulatively and save the generated PNGs into `matplotlib-gallery/figures/`.
- Save the raw python code for each plot into `matplotlib-gallery/code_snippets/`.
- Regenerate the base `data.json` for the frontend.

### 3. Add AI-Powered Metadata (Optional)
If you add new plots, you can generate AI prompts to automatically name and categorize them:
```bash
python generate_names_prompt.py
```
Paste the output into ChatGPT/Claude/Gemini, save the JSON responses in `ai_responses.json`, and run:
```bash
python merge_names.py
```

---

## 🌐 The Frontend Web App

The actual gallery website lives entirely inside the `matplotlib-gallery/` folder. It is a blazing-fast, static frontend featuring:
- **Instant Search:** Fuzzy matching across names, difficulties, and tags.
- **Smart Filtering:** Filter by plot type or difficulty level.
- **Dark/Light Mode:** First-class responsive themes.
- **Code Copying:** 1-click copy for all Python snippets.

### Local Development
Because the frontend uses the JavaScript `fetch()` API to load the plot code and `data.json`, you **cannot** just double click `index.html`.
You must serve it over a local server:
1. Open the project in VS Code.
2. Right-click `matplotlib-gallery/index.html` → **"Open with Live Server"**.

---

## 📁 Project Architecture

```text
Project Matplotlib/
├── src/
│   └── master_plots.py         # The single source of truth for all plot code
├── splitter.py                 # Engine that executes plots and builds the web assets
├── generate_names_prompt.py    # Generates AI prompts for metadata
├── merge_names.py              # Injects AI metadata into data.json
├── ai_responses.json           # Your saved AI responses
├── naming_prompts.txt          # The generated prompts for the AI
│
└── matplotlib-gallery/         # Frontend Web Application (Set as Vercel Root)
    ├── index.html              # Main gallery page
    ├── about.html              # About page
    ├── style.css               # Main stylesheet
    ├── app.js                  # Core gallery logic and modal
    ├── search.js               # Fuzzy search engine
    ├── data.json               # Auto-generated database for the UI
    ├── figures/                # Auto-populated by splitter.py
    └── code_snippets/          # Auto-populated by splitter.py
```

---

## 👤 Author

Created by **Muhammad Hashim**, CS Student and Python Programmer from Faisalabad, Pakistan.
Check out my [GitHub](https://github.com/Muhammad-Hashim-16) or connect with me on [LinkedIn](https://www.linkedin.com/in/muhammad-hashim-naeem-053b6a271).
