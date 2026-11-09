# UET-VNU LaTeX Beamer Presentation Template

A modern, elegant, and standardized **LaTeX Beamer** template for academic presentations, thesis defenses, conferences, and seminars at **VNU University of Engineering and Technology (UET - VNU)**.

---

## 🌟 Key Features

- **Clean White Canvas (`Aspect Ratio 16:9`):** High-contrast, minimalist, and sleek design tailored for international conferences and academic defenses.
- **Brand Identity (Blue & Green Theme):**
  - Primary Navy Blue (`#003A69`) & Vibrant Academic Emerald Green (`#10954A`).
  - Official high-resolution transparent UET Logo.
- **Modern Typography:** Crisp Sans-serif Helvetica font with full Unicode / Vietnamese diacritics support (`T5, T1` encoding).
- **Standalone Title Cover:** Enlarged, vertically centered university header, prominent topic card, author, supervisor, and date.
- **Automatic Section Divider Slides (`\enableSectionSlides`):** Elegant transition slides generated on each `\section{...}`.
- **Header Breadcrumbs & Compact Footer:**
  - Header displays active section name on the top right.
  - Persistent bottom footer with UET logo, university name, short title, and slide number badge (`n / N`).
- **Rich Pre-built Presentation Components:**
  - 📊 **Stat / Metric Cards (`\statcard`):** High-impact big number callouts (+95.8%, 8.5×, -42%).
  - 🧠 **TikZ Network & Architecture Diagram:** Multi-node graph with contraction edges and index legs.
  - ✅ **Visual Comparison Table:** With `\cmark` ($\checkmark$) and `\xmark` ($\times$) indicators and highlight rows.
  - 📋 **Standard Bullet Lists & 2-Column Cards (`accentcard`, `uetcard`).**
  - 💡 **Block Environments (`block`, `alertblock`, `exampleblock`).**
  - 💻 **Syntax-Highlighted Source Code Listing (`listings` Python).**
  - 🎯 **Q&A & Contact Closing Slide.**

---

## 📁 Repository Structure

```text
TemplateSlideUET/
├── assets/
│   ├── uet_logo.png         # High-resolution transparent UET-VNU logo
│   └── fit_logo.png         # Faculty / Department logo
├── beamerthemeUET.sty       # Core custom Beamer theme package
├── main.tex                 # Presentation source file
├── main.pdf                 # Compiled output PDF presentation
├── previews/                # Exported slide preview images
├── .vscode/
│   └── settings.json        # LaTeX Workshop configuration & auto-build
├── .gitignore               # Ignored LaTeX auxiliary build files
└── README.md                # Documentation & usage instructions
```

---

## 🚀 Compilation Instructions

### 1. Command Line (Linux / macOS / Windows)
```bash
# Compile using pdflatex (run twice for TOC & cross-references)
pdflatex main.tex && pdflatex main.tex

# Or using XeLaTeX
xelatex main.tex
```

### 2. Overleaf
1. Download or clone this repository as a `.zip` file.
2. Open [Overleaf](https://www.overleaf.com), select **New Project** $\to$ **Upload Project**.
3. Ensure `main.tex` is set as the root document and compile.

### 3. VS Code
Open the project directory in VS Code with the **LaTeX Workshop** extension installed. Auto-formatting with `latexindent` and compilation on save are pre-configured in `.vscode/settings.json`.

---

## ⚙️ Quick Customization in `main.tex`

```latex
% Presentation Metadata
\title[Short Topic]{Your Presentation Topic}
\author[Author Name]{Le Van A}
\supervisor{Dr. Supervisor Name}
\date{\today}

% Custom University Name (if needed)
\setunivname{VNU University of Engineering and Technology}
```

---

## 📄 License
This template is open-sourced and available for students, faculty, and researchers.
