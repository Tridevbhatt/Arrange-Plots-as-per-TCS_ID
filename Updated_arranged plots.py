# streamlit_app.py

import os
import shutil
import streamlit as st
import pandas as pd
from datetime import datetime

def organize_files_by_prefix(source_folder):
    created_folders = set()
    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)

        if not os.path.isfile(file_path):
            continue

        # Extract the prefix based on delimiters
        delimiters = ['-', '_', '@', '•']
        prefix = file_name
        for delimiter in delimiters:
            prefix = prefix.split(delimiter)[0]

        if not prefix:
            st.warning(f"Skipped: {file_name} (No valid prefix found)")
            continue

        subfolder_path = os.path.join(source_folder, prefix)
        os.makedirs(subfolder_path, exist_ok=True)

        shutil.move(file_path, os.path.join(subfolder_path, file_name))
        created_folders.add(prefix)
        st.success(f"Moved: {file_name} → {subfolder_path}")

    return created_folders

def group_folders_by_comments(source_folder, excel_file):
    df = pd.read_excel(excel_file)

    # Normalize column names
    df.columns = [col.lower() for col in df.columns]

    required_columns = ["4g nomenclature b28", "4g nomenclature b01", "4g nomenclature b41", "comments"]
    if not all(col in df.columns for col in required_columns):
        st.error("The required columns are missing from the Excel file.")
        return

    folders_moved = set()
    all_folders = set(os.listdir(source_folder))

    for _, row in df.iterrows():
        comment = row["comments"]
        b28_folders = row["4g nomenclature b28"]
        b01_folders = row["4g nomenclature b01"]
        b41_folders = row["4g nomenclature b41"]

        if pd.isna(comment):
            st.warning("Skipped a row with no comment.")
            continue

        # Clean and split
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
                st.success(f"Moved: {folder_name} → {comment_folder}")
            else:
                st.error(f"Folder not found: {folder_name}")

    remaining = all_folders - folders_moved
    if remaining:
        st.warning("The following folders were not moved:")
        for folder in remaining:
            st.write(f"- {folder}")
    else:
        st.success("All folders have been successfully grouped!")

# Streamlit UI
def main():
    st.set_page_config(page_title="Folder Organizer", page_icon="📂", layout="wide")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #f2f6fc;
            padding: 20px;
        }}
        .title-container {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .logo {{
            height: 60px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([8, 1])
    with col1:
        st.title("📁 Smart File Organizer")
        st.subheader("Automatically organize files and folders based on name prefixes and comments in Excel.")
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/512px-React-icon.svg.png", width=70)

    st.markdown("---")

    with st.form("file_form"):
        source_folder = st.text_input("📂 Enter the full path of the folder to organize:")
        excel_file = st.file_uploader("📄 Upload the Excel file with comments", type=["xlsx", "xls"])

        submitted = st.form_submit_button("Start Organizing")

    if submitted:
        if not os.path.exists(source_folder):
            st.error("Invalid folder path. Please enter a valid path.")
            return
        if excel_file is None:
            st.error("Please upload a valid Excel file.")
            return

        st.info("Step 1: Organizing files into folders by prefix...")
        created = organize_files_by_prefix(source_folder)

        st.info("Step 2: Grouping folders by comments in Excel...")
        temp_excel_path = os.path.join(source_folder, "temp_uploaded_excel.xlsx")
        with open(temp_excel_path, "wb") as f:
            f.write(excel_file.read())

        group_folders_by_comments(source_folder, temp_excel_path)
        os.remove(temp_excel_path)

        st.success("🎉 Folder organization complete!")

if __name__ == "__main__":
    main()
