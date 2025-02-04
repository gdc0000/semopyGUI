# SEM Analysis Web App with semopy

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

A professional web application for conducting Structural Equation Modeling (SEM) analyses directly in your browser. Designed for researchers and data analysts in social sciences.

![App Screenshot](https://via.placeholder.com/800x400.png?text=SEM+Analysis+Interface) <!-- Add real screenshot -->

## Features ✨

- **Broad File Support**
  - CSV, Excel (XLS/XLSX), SAS (sas7bdat)
  - Automatic missing data handling with deletion option
  - Real-time data preview

- **Modeling Capabilities**
  - 12+ predefined model templates across 4 categories
  - Live syntax editor with intelligent code suggestions
  - Full SEM parameters estimation (β coefficients, SEs, p-values)

- **Advanced Diagnostics**
  - Comprehensive fit indices: χ², RMSEA, CFI, TLI, NFI, GFI, AGFI
  - APA-style results formatting
  - Interactive parameter tables

## Installation & Setup ⚙️

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/sem-analysis-app.git
   cd sem-analysis-app
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch Application**
   ```bash
   streamlit run main.py
   ```

## Usage Guide 📖

1. **Data Preparation**
   - Upload dataset through sidebar
   - Handle missing values with one click
   - Verify variables in preview table

2. **Model Specification**
   ```mermaid
   graph LR
   A[Select Model Category] --> B[Choose Template]
   B --> C[Edit Syntax]
   C --> D[Run Analysis]
   ```

3. **Key Features**
   - Cross-lagged panel models
   - Multi-group invariance testing
   - Latent interaction models
   - Bifactor modeling

## Technical Specifications 🔧

- **Core Components**
  - Streamlit 1.32+ frontend
  - semopy 2.3.1 SEM backend
  - Pandas 2.0+ data handling

- **Performance**
  - Handles datasets up to 100,000 cells
  - Real-time model fitting <60s for typical models
  - Cached data processing


## Citation & Attribution 📚

If using this tool in research:
```bibtex
@software{DiCicco_SEM_Analysis_2024,
  author = {Di Cicco, Gabriele},
  title = {SEM Analysis Web App},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {https://github.com/yourusername/sem-analysis-app}
}
```

---

**Developed by**  
Gabriele Di Cicco, PhD  
[![ORCID](https://img.shields.io/badge/ORCID-0000--0002--1439--5790-green.svg)](https://orcid.org/0000-0002-1439-5790)  
[![GitHub](https://img.shields.io/badge/GitHub-Profile-blue)](https://github.com/gdc0000)  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://www.linkedin.com/in/gabriele-di-cicco-124067b0/)
```
