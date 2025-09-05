#!/usr/bin/env python3
"""
Streamlit Image Browser for 5-part filenames:
METHOD_LOCATION_SAMPLE_MODE_MAGNIFICATION.ext
(e.g., PCM_BIU_glassLube_NA_10x.jpg)

Reads a metadata.csv created from the filenames with columns:
  filename, method, location, sample, mode, magnification, magnification_value, ext, rel_path

Features:
- Toggle view: By Sample or By Method
- Rich filters: location/mode/magnification, free-text search
- Compare mode: fix one axis (sample or method) and view the other axis in a grid
- Adjustable images-per-row, optional captions, download filtered CSV
- Robust to missing/broken image paths
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from PIL import Image, UnidentifiedImageError
import streamlit as st
import requests
import io

# ---------------------------
# Utilities
# ---------------------------
@st.cache_data(show_spinner=False)
def load_metadata() -> pd.DataFrame:

    script_dir = Path(__file__).resolve().parent   # app/ folder if your script lives there
    repo_root  = script_dir.parent

    # images_dir = repo_root / "images"
    # if not images_dir.exists():
    #     st.warning(f"Images folder not found: {images_dir}")
    #     st.stop()  


    csv_path = repo_root / "metadata.csv"
    df = pd.read_csv(csv_path)
    # df["full_path"] = (images_dir/ df["rel_path"]).apply(lambda x: str(images_dir / x))

    # use this for online hosting
    images_dir = "https://media.githubusercontent.com/media/nate-yang-uk/Polarising-Microscopic-Image-Viewer/main/images"

    df["full_path"] = df["rel_path"].apply(lambda x: f"{images_dir}/{x}")
    # Normalize expected columns (tolerate case differences)
    df.columns = [c.strip().lower() for c in df.columns]
    # Ensure required columns exist
    required = {
        "filename",
        "method",
        "location",
        "sample",
        "mode",
        "magnification",
        "ext",
        "rel_path",
    }
    missing = required - set(df.columns)
    if missing:
        st.error(f"metadata.csv is missing required columns: {sorted(missing)}")
        st.stop()
    # Optional magnification_value
    if "magnification_value" not in df.columns:
        df["magnification_value"] = pd.NA
    # Coerce types
    if "magnification_value" in df.columns:
        df["magnification_value"] = pd.to_numeric(
            df["magnification_value"], errors="coerce"
        )
    # Stringify key columns
    for c in [
        "method",
        "location",
        "sample",
        "mode",
        "magnification",
        "filename",
        "ext",
        "rel_path",
    ]:
        df[c] = df[c].astype(str)
    return df


def safe_open_image(path: Path):
    try:
        return Image.open(path)
    except (FileNotFoundError, UnidentifiedImageError, OSError) as e:
        return None, str(e)


def filtered_df(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    # Global text search (sample, filename)
    q = st.sidebar.text_input(
        "Search (sample / filename)", placeholder="e.g., glassLube or PCM"
    )
    if q.strip():
        key = q.strip().lower()
        df = df[
            df["sample"].str.lower().str.contains(key)
            | df["filename"].str.lower().str.contains(key)
        ]

    # Faceted filters
    methods = sorted(df["method"].dropna().unique().tolist())
    locations = sorted(df["location"].dropna().unique().tolist())
    modes = sorted(df["mode"].dropna().unique().tolist())

    sel_methods = st.sidebar.multiselect("Method", methods, default=methods)
    sel_locations = st.sidebar.multiselect("Location", locations, default=locations)
    sel_modes = st.sidebar.multiselect("Mode", modes, default=modes)

    df = df[
        df["method"].isin(sel_methods)
        & df["location"].isin(sel_locations)
        & df["mode"].isin(sel_modes)
    ]

    # Magnification filter: use text values and numeric range if available
    mags_text = sorted(df["magnification"].dropna().unique().tolist())

    sel_mags_text = st.sidebar.multiselect("magnification", mags_text, default=mags_text)

    df = df[df["magnification"].isin(sel_mags_text)]


    return df


def grid_show(
    df: pd.DataFrame,
    group_rows: pd.DataFrame,
    images_per_row: int,
    show_captions: bool,
    caption_style: str,
):

    cols = st.columns(images_per_row)
    for i, (_, row) in enumerate(group_rows.iterrows()):
        path = Path(row["full_path"])
        img = None
        err = None
        try:
            # img = Image.open(path)
            
            # for online hosting
            url = row["full_path"]
            response = requests.get(url, stream=True)
            response.raise_for_status()    # raise an error if request fails

            img = Image.open(io.BytesIO(response.content))

        except Exception as e:
            err = str(e)

        with cols[i % images_per_row]:
            if img is not None:
                st.image(img, width="stretch")
            else:
                st.warning(f"⚠️ Could not open: {path.name}\n\n{err}")
            if show_captions:
                if caption_style == "Filename":
                    # st.caption(row["filename"])
                    st.markdown(
                        f"<span style='font-size:20px; color:gray;'>**{row['filename']}**</span>",
                        unsafe_allow_html=True,
                    )
                elif caption_style == "Short metadata":

                    st.markdown(
                        f"<span style='font-size:20px; color:gray;'>**{row['method']} | {row['sample']} | {row['magnification']}**</span>",
                        unsafe_allow_html=True,
                    )
                else:

                    st.markdown(
                        f"<span style='font-size:20px; color:gray;'>**Method: {row['method']} • Location: {row['location']} • "
                        f"Sample: {row['sample']} • Mode: {row['mode']} • "
                        f"Mag: {row['magnification']}**</span>",
                        unsafe_allow_html=True,
                    )


# ---------------------------
# Main App
# ---------------------------
def main():
    # Parse CLI arg: --data-root or --csv
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--data-root", type=str, help="Folder containing metadata.csv")
    parser.add_argument(
        "--csv", type=str, help="Path to metadata.csv (overrides --data-root)"
    )
    args, _ = parser.parse_known_args(sys.argv[1:])

    st.set_page_config(page_title="Imaging Browser", layout="wide")
    st.title("Imaging Dataset Viewer")
    st.write(
        "Filter and compare by **Sample**, **Method**, **Location**, **Mode**, and **Magnification**."
    )
    
    # # Source selector (UI fallback)
    # src_mode = st.sidebar.radio("Data source", ["Upload CSV" , "From folder"])
    # csv_path = None

    # if args.csv:
    #     csv_path = Path(args.csv).expanduser().resolve()
    # elif args.data_root:
    #     csv_path = Path(args.data_root).expanduser().resolve() / "metadata.csv"

    # if src_mode == "From folder":
    #     folder = st.sidebar.text_input(
    #         "Folder path (contains metadata.csv)",
    #         value=str(csv_path.parent) if csv_path else "",
    #     )
    #     if folder:
    #         csv_path = Path(folder).expanduser().resolve() / "metadata.csv"
    # else:
    #     uploaded = st.sidebar.file_uploader("Upload metadata.csv", type=["csv"])
    #     if uploaded is not None:
    #         df = pd.read_csv(uploaded)
    #     else:
    #         df = None

    # # Load metadata
    # if src_mode == "Upload CSV":
    #     if df is None:
    #         st.info("Upload a metadata.csv to begin.")
    #         st.stop()
    # else:
    #     if not csv_path or not csv_path.exists():
    #         st.warning("Please provide a valid folder path containing metadata.csv.")
    #         st.stop()

    # script_dir = Path(__file__).resolve().parent   # app/ folder if your script lives there
    # repo_root  = script_dir.parent

    # images_dir = repo_root / "images"
    # if not images_dir.exists():
    #     st.warning(f"Images folder not found: {images_dir}")
    #     st.stop()  

    # csv_path = repo_root / "metadata.csv"

    df = load_metadata()
        
 
    st.set_page_config(
    layout="wide", 
    initial_sidebar_state="expanded"   # or "collapsed"
    )

    with open("README.md", "r", encoding="utf-8") as f:
        readme_text = f.read()

    # Put it inside a text area
    st.sidebar.text_area("Image Info", value=readme_text, width=300, height=300)
    # View controls
    st.sidebar.markdown("---")
    view_mode = st.sidebar.radio("View mode", ["By Sample", "By Method"])
    group_axis = st.sidebar.selectbox(
        "Compare across (grouped by)",
        ["method","location", "sample","mode", "magnification"],
        index=0 if view_mode == "By Sample" else 0,
    )
    images_per_row = st.sidebar.slider("Images per row (change this to 1 for large images)", 1, 8, 2)
    show_captions = st.sidebar.checkbox("Show captions", value=True)
    caption_style = st.sidebar.selectbox(
        "Caption style", ["Filename", "Short metadata", "Full metadata"]
    )

    # Selection
    if view_mode == "By Sample":
        options = sorted(df["sample"].unique().tolist())
        if not options:
            st.info("No data matches your filters.")
            st.stop()
        sample_choice = st.selectbox("Choose a Sample to compare across", options)
        subset = df[df["sample"] == sample_choice].sort_values([group_axis, "filename"])
        st.subheader(f"Sample: {sample_choice}")
        for g, gdf in subset.groupby(group_axis):
            st.markdown(f"### {group_axis.title()}: {g}")
            grid_show(df, gdf, images_per_row, show_captions, caption_style)
            st.markdown("---")
    else:
        options = sorted(df["method"].unique().tolist())
        if not options:
            st.info("No data matches your filters.")
            st.stop()
        method_choice = st.selectbox("Choose a Method to compare across", options)
        subset = df[df["method"] == method_choice].sort_values([group_axis, "filename"])
        st.subheader(f"Method: {method_choice}")
        for g, gdf in subset.groupby(group_axis):
            st.markdown(f"### {group_axis.title()}: {g}")
            grid_show(df, gdf, images_per_row, show_captions, caption_style)
            st.markdown("---")



    # Sidebar filters
    df = filtered_df(df)



    # Footer
    st.caption("Tip: Use the sidebar to refine filters and adjust the layout.")


if __name__ == "__main__":
    main()
