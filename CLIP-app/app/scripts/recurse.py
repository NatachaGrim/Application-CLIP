"""
This script generates a list of image files contained in a specified folder and its subfolders

Arguments:
    :project_name: folder where to search for image files

Output:
    .txt file listing image paths found in the specified folder
    This file is saved in the 'app/static/<project_name>' directory
"""

import os
import argparse

# Retrieve the project name from the environment variable
project_name = os.environ.get('FLASK_ARG')

# Initialize argument parser
parser = argparse.ArgumentParser(
    prog = 'recurse.py',
    description = 'Build a list of image files from a folder and its subfolders.'
)
parser.add_argument('-f', '--folderName', help='The folder to be listed', required=True)
args = parser.parse_args()
walk_dir = args.folderName

# Base directory to save the list file
base_dir = os.path.join("app", "static", project_name)

# Generate the output file name and path
output_file = f"{project_name}_list.txt"
list_file_path = os.path.join(base_dir, output_file)

# Open the output file in binary write mode
with open(list_file_path, 'wb') as list_file:
    for root, subdirs, files in os.walk(walk_dir):
        print('--\nroot = ' + root)
        # Sort subdirectories alphabetically to be consistent with labels during confusion matrix computation
        subdirs.sort()
        for subdir in subdirs:
            print('\t- subdirectory ' + subdir)
        i = 0
        # Filter and process image files
        for filename in [filename for filename in files if not("._" in filename) and (filename.lower().endswith((".jpg", ".jpeg", ".png")))]:
            file_path = os.path.join(root, filename)
            if (i % 10 == 0):
                print('\t-%s : %s (full path: %s)' % (str(i), filename, file_path))
            # Write the file path to the list file
            list_file.write(('%s\n' % (file_path)).encode('utf-8'))
            i += 1
        print("files: " + str(i))

print(f"File saved as: {list_file_path}")
