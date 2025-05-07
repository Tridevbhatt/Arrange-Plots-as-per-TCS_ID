import os
import shutil
import pandas as pd
import streamlit as st
from streamlit_file_browser import file_browser

st.set_page_config(page_title="Folder Organizer", layout="wide")
st.markdown("""
    <style>
        .main { background-color: #f4f6f7; }
        h1 { color: #2e8b57; }
        .stButton > button { background-color: #4CAF50; color: white; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""<h1>📁 Smart Folder & Comment Grouping Tool</h1>""", unsafe_allow_html=True)

st.markdown("### 👉 Step 1: Browse and Select a Folder Containing Raw Files")
source_folder = file_browser(select_folder=True)

if source_folder:
    st.success(f"Selected folder: {source_folder}")

    if st.button("1️⃣ Organize files into subfolders by prefix"):
        created_folders = set()
        for file_name in os.listdir(source_folder):
            file_path = os.path.join(source_folder, file_name)
            if not os.path.isfile(file_path):
                continue

            delimiters = ['-', '_', '@', '•']
            prefix = file_name
            for delimiter in delimiters:
                prefix = prefix.split(delimiter)[0]

            if not prefix:
                continue

            subfolder_path = os.path.join(source_folder, prefix)
            os.makedirs(subfolder_path, exist_ok=True)
            shutil.move(file_path, os.path.join(subfolder_path, file_name))
            created_folders.add(prefix)

        st.success("✅ Files organized into folders by prefix.")

    st.markdown("### 👉 Step 2: Upload Excel File to Group Folders by Comments")
    excel_file = st.file_uploader("Upload the Excel File", type=["xlsx", "xls"])

    if excel_file and st.button("2️⃣ Group Folders by Comments"):
        df = pd.read_excel(excel_file)
        df.columns = [col.lower() for col in df.columns]

        required_columns = ["4g nomenclature b28", "4g nomenclature b01", "4g nomenclature b41", "comments"]
        if not all(col in df.columns for col in required_columns):
            st.error("❌ The required columns are missing in the uploaded Excel file.")
        else:
            folders_moved = set()
            all_folders = set(os.listdir(source_folder))

            for _, row in df.iterrows():
                comment = row["comments"]
                b28_folders = row["4g nomenclature b28"]
                b01_folders = row["4g nomenclature b01"]
                b41_folders = row["4g nomenclature b41"]

                if pd.isna(comment):
                    continue

                b28 = list(set(str(b28_folders).split(', '))) if pd.notna(b28_folders) else []
                b01 = list(set(str(b01_folders).split(', '))) if pd.notna(b01_folders) else []
                b41 = list(set(str(b41_folders).split(', '))) if pd.notna(b41_folders) else []

                folders_to_move = list(set(b28 + b01 + b41))

                comment_folder = os.path.join(source_folder, str(comment))
                os.makedirs(comment_folder, exist_ok=True)

                for folder_name in folders_to_move:
                    folder_path = os.path.join(source_folder, folder_name)
                    if os.path.exists(folder_path):
                        shutil.move(folder_path, os.path.join(comment_folder, folder_name))
                        folders_moved.add(folder_name)
                    else:
                        st.warning(f"⚠️ Folder not found: {folder_name}")

            remaining_folders = all_folders - folders_moved
            if remaining_folders:
                st.warning("Some folders were not grouped:")
                for folder in remaining_folders:
                    st.text(f"- {folder}")
            else:
                st.success("✅ All folders have been successfully grouped by comments.")
