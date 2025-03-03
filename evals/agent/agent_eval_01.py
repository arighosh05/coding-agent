import os
import shutil
import logging
from pathlib import Path

# Configure logging with an appropriate level and format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_file(file_path):
    """
    Reads the contents of a file safely, ensuring resource management
    and handling common I/O errors gracefully.
    """
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        logging.error("File not found: %s", file_path)
    except PermissionError:
        logging.error("Permission denied: %s", file_path)
    except Exception as e:
        logging.error("An error occurred while reading the file: %s", e)
    return None

def log_sensitive_data_detection(data):
    """
    Logs detection of sensitive data, such as the presence of the word 'password'.
    """
    if "password" in data:
        logging.warning("Sensitive data detected!")

def delete_directory(dir_path):
    """
    Deletes a directory safely using shutil, ensuring it exists before attempting to delete.
    """
    try:
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
            logging.info("Temporary folder deleted: %s", dir_path)
        else:
            logging.info("Directory does not exist, or is not a directory: %s", dir_path)
    except PermissionError:
        logging.error("Permission denied while attempting to delete directory: %s", dir_path)
    except Exception as e:
        logging.error("An error occurred when deleting the directory: %s", e)

def process_file(file_path):
    """
    Main function for processing the file: read the file contents, 
    check for sensitive data, and delete a temporary directory.
    """
    file_path = Path(file_path)

    # Validate file path
    if not file_path.is_file():
        logging.error("Invalid file path provided: %s", file_path)
        return

    # Step 1: Read the file safely
    data = read_file(file_path)
    if data is None:
        return

    # Step 2: Log if sensitive data is detected
    log_sensitive_data_detection(data)

    # Step 3: Safely delete the temporary directory
    delete_directory(Path("/tmp/temp_folder"))

    # Returning the read data might be used somewhere; keep this functionality unchanged
    return data
