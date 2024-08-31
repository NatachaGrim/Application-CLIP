import csv
import os
import unidecode

def normalize_text(text):
    # Convertir en minuscules
    text = text.lower()
    # Supprimer les accents
    text = unidecode.unidecode(text)
    # Remplacer les points-virgules par un espace
    text = text.replace(';', ' ')
    return text

def txt_to_csv(flask_arg):
    # Construire le chemin vers le fichier .txt
    txt_file_path = f"app/static/{flask_arg}/ontology/{flask_arg}_ontology.txt"
    # Construire le chemin vers le fichier .csv
    csv_file_path = f"app/static/{flask_arg}/ontology/{flask_arg}_ontology.csv"

    try:
        with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
            lines = txt_file.readlines()
        
        # Ouvrir le fichier CSV pour écrire avec l'encodage UTF-8
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            
            # Traiter chaque ligne du fichier .txt
            for line in lines:
                # Extraire le terme et la définition
                parts = line.split('": "')
                if len(parts) == 2:
                    term = parts[0].strip('"')
                    definition = parts[1].strip().strip('"')
                    
                    # Normaliser le terme et la définition
                    term = normalize_text(term)
                    definition = normalize_text(definition)
                    
                    # Écrire dans le fichier CSV
                    writer.writerow([term, definition])
        
        print(f"Le fichier CSV a été créé avec succès : {csv_file_path}")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

# Récupérer FLASK_ARG depuis les variables d'environnement
flask_arg = os.environ.get('FLASK_ARG')

if not flask_arg:
    print("ERROR: The environment variable FLASK_ARG is not set.")
else:
    txt_to_csv(flask_arg)
