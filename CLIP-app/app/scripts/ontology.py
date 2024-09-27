import csv
import os
import unidecode

def normalize_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove accents
    text = unidecode.unidecode(text)
    # Replace semicolons with a space
    text = text.replace(';', ' ')
    return text

def txt_to_csv(flask_arg):
    # Path to .txt input ontology file
    txt_file_path = f"app/static/{flask_arg}/ontology/{flask_arg}_ontology.txt"
    # Path to .csv output ontology file
    csv_file_path = f"app/static/{flask_arg}/ontology/{flask_arg}_ontology.csv"
    
    # Check if .txt file exists
    if not os.path.exists(txt_file_path):
        print(f"ERROR: The input file {txt_file_path} does not exist.")
        return
    
    # Check if .csv file exists and compare modification times
    if os.path.exists(csv_file_path):
        txt_mod_time = os.path.getmtime(txt_file_path)
        csv_mod_time = os.path.getmtime(csv_file_path)
        
        # If .csv is newer than .txt, no need to update
        if csv_mod_time >= txt_mod_time:
            return
    
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
            lines = txt_file.readlines()
        
        # Open .csv file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            
            # Extract label and caption from each line
            for line in lines:
                parts = line.split('": "')
                if len(parts) == 2:
                    term = parts[0].strip('"')
                    definition = parts[1].strip().strip('"')
                    
                    # Normalising labels and captions
                    term = normalize_text(term)
                    definition = normalize_text(definition)
                    writer.writerow([term, definition])
        
        print(f"The .csv file has been updated successfully.\n")
        
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

# Retrieve FLASK_ARG variable
flask_arg = os.environ.get('FLASK_ARG')

if not flask_arg:
    print("ERROR: The environment variable FLASK_ARG is not set.")
else:
    txt_to_csv(flask_arg)
