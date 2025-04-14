import os
import shutil


# Function to organize files
def organize_files():
    root_dir = os.getcwd()  # Get the current working directory

    # Directories to be created if they don't exist
    subdirs = ['charts', 'reports', 'data']

    # Create subdirectories if they don't exist
    for subdir in subdirs:
        subdir_path = os.path.join(root_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)
            print(f"Created directory: {subdir_path}")

    # Now let's move generated files (charts, reports, etc.) into these folders
    for file in os.listdir(root_dir):
        if file.endswith('.png'):  # Move image files (charts)
            shutil.move(file, os.path.join(root_dir, 'charts', file))
        elif file.endswith('.txt'):  # Move text files (reports)
            shutil.move(file, os.path.join(root_dir, 'reports', file))
        elif file.endswith('.csv'):  # Move CSV files (data)
            shutil.move(file, os.path.join(root_dir, 'data', file))

    print("Files have been organized.")

