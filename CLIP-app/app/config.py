import os

class Config():
    DEBUG = os.environ.get("DEBUG")

# Configuration globale
maxResults = 300
maxThumbnails = 30
minProb = 0.6
gap = 0.8

# Récupérer le dossier ciblé depuis la variable d'environnement
try:
    use_case = os.environ["FLASK_ARG"]
except KeyError:
    print("FLASK_ARG env var is not defined!")
    quit()

# Dossiers de l'application
torchFolder = "app/models/"
img_folder = f"app/static/{use_case}/images"
eval_folder = "app/static/_eval/"
conf_mat_file = f"{eval_folder}{use_case}_confusion.txt"

fichiers = os.listdir(torchFolder)

#tensor_file = f"{torchFolder}/royere_gouache_petite_fine_tuned.pt"

#tensor_file = next((os.path.join(torchFolder, fichier) for fichier in fichiers if fichier.endswith(f"_{use_case}_fine_tuned.pt")), None)

#if tensor_file is None:
#tensor_file = f"{torchFolder}/08_14_2024_fine_tuned_royere_gouache_ft.pt"

tensor_file = next((os.path.join(torchFolder, fichier) for fichier in fichiers if fichier.endswith(f"_{use_case}.pt")), None)

directory_file = f"app/static/{use_case}/{use_case}_list.txt"
directory_summary = f"app/static/{use_case}/{use_case}_directory.txt"
image_urls = f"app/static/{use_case}/{use_case}_urls.txt"
labels_file = f"app/static/{use_case}/ontology/{use_case}_ontology.csv"
