# Polarising Microscopic Image Viewer

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20Demo-brightgreen)](https://polarising-microscopic-image-viewer--nate-yang.streamlit.app/)

An interactive **Streamlit web application** for visualising and exploring polarising light microscopy (PLM) and related imaging datasets.  
Designed for quick browsing, metadata filtering, and comparison of experimental samples.

---

## 🚀 Live Demo
Try it here: [Polarising Microscopic Image Viewer](https://polarising-microscopic-image-viewer--nate-yang.streamlit.app/)

---

## 📦 Features
- Browse microscopy images with metadata-driven filters
- Supports PLM, PCM, and EHD methods
- Toggle between imaging modes (Cross-polarisation, Full-wave plate, DIC, etc.)
- Organised sample/experiment metadata for reproducibility

---

## 🖥️ Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Polarising-Microscopic-Image-Viewer.git
cd Polarising-Microscopic-Image-Viewer
```


### 2. Create and activate a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Launch the app
```
python -m streamlit run scripts/streamlit_viewer_local.py


Then open http://localhost:8501
 in your browser.
```


## 📂 Repository Structure
```
.
├── images/                        # Microscopy images
├── metadata.xlsx                  # Metadata table (sample, method, mode, etc.)
├── scripts/
│   ├── streamlit_viewer_local.py  # Main Streamlit app
│   ├── make_metadata_from_filenames.py
│   └── ...
├── requirements.txt
└── README.md
```



## 🧪 Metadata Reference

**Methods**

- PLM - Polarising Light Microscopy
- PCM Phase Contrast Microscopy
- EHD - Elastohydrodynamic from PCS

**Locations**

- BIU — Biomedical Imaging Unit
- nCAT — National Centre for Advanced Tribology
- nC2 — Enterprise Unit

**Samples**

- blobs of liquid crystals - S#
- glass
- lubricant or lubricant&glass (liquid crystal)

**Modes**

- NA — Not applicable
- Null — No filter
- CP — Cross-polarisation
- WP — Full-wave plate at cross-polarisation
- DIC — Differential interference contrast microscopy