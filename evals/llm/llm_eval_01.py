import os
import shutil

def process_file(file_path):
    """Reads a file, checks for sensitive data, and safely removes a temp folder."""
    if not os.path.isfile(file_path):
        print("Error: Invalid file path.")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()

        if "password" in data.lower():  # Case-insensitive search
            print("Warning: Potential sensitive data detected!")

        temp_folder = "/tmp/temp_folder"
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)  # Safe deletion
            print("Temporary folder removed.")

        return data

    except Exception as e:
        print(f"Error processing file: {e}")
        return None
