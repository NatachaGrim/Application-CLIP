import os

class Config():
    DEBUG = os.environ.get("DEBUG")

# Maximum number of images in query results
maxResults = 300

# Maximum number of images to display on home page
maxThumbnails = 30

# Threshold above which a result is considered valid
minProb = 0.6
gap = 0.8

# Retrieve target folder from the "FLASK_ARG" variable
try:
    use_case = os.environ["FLASK_ARG"]
except KeyError:
    print("FLASK_ARG is not defined!")
    quit()

# Folder containing embeddings
torchFolder = "app/models/"

# Folder containing the images
img_folder = f"app/static/{use_case}/images"

# Folder containing confidence scores
eval_folder = "app/static/_eval/"

# Folder containing the confusion matrices
conf_mat_file = f"{eval_folder}{use_case}_confusion.txt"

# Get the list of files in the torchFolder
fichiers = os.listdir(torchFolder)

# File containing project image embeddings
tensor_file = next((os.path.join(torchFolder, fichier) for fichier in fichiers if fichier.endswith(f"_{use_case}.pt")), None)

# File containing the list of image paths
directory_file = f"app/static/{use_case}/{use_case}_list.txt"

# File containing the project summary
directory_summary = f"app/static/{use_case}/{use_case}_directory.txt"

# File containing image URLs
image_urls = f"app/static/{use_case}/{use_case}_urls.txt"

# File containing labels and captions
labels_file = f"app/static/{use_case}/ontology/{use_case}_ontology.csv"
