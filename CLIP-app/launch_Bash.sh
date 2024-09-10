#!/bin/bash

# ASCII title
echo -e "\033[36m"
echo " ▗▄▄▖▗▖   ▗▄▄▄▖▗▄▄▖      ▗▄▖ ▗▄▄▖ ▗▄▄▖ "
echo "▐▌   ▐▌     █  ▐▌ ▐▌    ▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌"
echo "▐▌   ▐▌     █  ▐▛▀▘     ▐▛▀▜▌▐▛▀▘ ▐▛▀▘ "
echo "▝▚▄▄▖▐▙▄▄▖▗▄█▄▖▐▌       ▐▌ ▐▌▐▌   ▐▌   "
echo "                                       "
echo -e "\033[0m"

################################################
##### FIRST STEP : CHOOSING A PROJECT FILE #####
################################################

# Function to validate the $FLASK_ARG variable
function check_folder() {
    # Check if the variable is empty
    if [ -z "$FLASK_ARG" ]; then
        echo -e "\033[31mWARNING: this field cannot be empty\033[0m"
        echo ""
        return 1
    fi

    # Check if the folder exists
    if [ ! -d "app/static/$FLASK_ARG" ]; then
        echo -e "\033[31mWARNING: Either the folder name is incorrect or does not exist\033[0m"
        echo ""
        return 1
    fi

    return 0
}

# Re-enter the variable until it is valid
while true; do
    echo -ne "\033[36mPlease enter the name of your project folder: \033[0m"
    read FLASK_ARG
    echo ""

    # Validation function
    if check_folder; then
        break
    fi
done

# Export the FLASK_ARG variable to be accessible in Python scripts
export FLASK_ARG

# Display a success message when the variable is validated
echo -e "\033[32mThe project folder '$FLASK_ARG' is valid\033[0m"
echo ""


############################################
##### SECOND STEP : LISTING THE IMAGES #####
############################################

# Construct full paths for the script and output files
scriptPath="app/scripts/recurse.py"
outputFilePath="app/static/$FLASK_ARG/${FLASK_ARG}_directory.txt"

# If the "$FLASK_ARG_list.txt" file does not exist, run the "recurse.py" script
if [ ! -f "$outputFilePath" ]; then
    echo -e "\033[36m... listing the folder '$FLASK_ARG'\033[0m"
    echo ""
    python "$scriptPath" -f "app/static/$FLASK_ARG" > "$outputFilePath"

    # Display a success message when the script has been successfully run
    echo -e "\033[32mSUCCESS: images successfully listed\033[0m"
    echo ""
fi


#############################################
##### THIRD STEP : CONVERTING ONTOLOGY #####
#############################################

# Construct full paths for the script and output files
ontologyScriptPath="app/scripts/ontology.py"
outputFilePath="app/static/$FLASK_ARG/ontology/${FLASK_ARG}_ontology.csv"

# If the "$FLASK_ARG_ontology.txt" file does not exist, run the "ontology.py" script
if [ ! -f "$outputFilePath" ]; then
    targetFilePath="app/static/$FLASK_ARG/ontology/${FLASK_ARG}_ontology.txt"
    
    echo -e "\033[36m... converting the ontology of '$FLASK_ARG'\033[0m"
    echo ""
    python "$ontologyScriptPath" "$targetFilePath"

    # Display a success message when the script has been successfully run
    echo -e "\033[32mSUCCESS: ontology successfully converted\033[0m"
    echo ""
fi


#################################################
##### FOURTH STEP : BUILDING CLIP EMBEDDINGS #####
#################################################

# Check if any model file existing in "app/models" ends with "$FLASK_ARG.pt"
modelPath="app/models"
modelExists=$(find "$modelPath" -name "*$FLASK_ARG.pt")

# If the "*$FLASK_ARG.pt" file does not exist, run the "model.py" script
if [ -z "$modelExists" ]; then
    echo -e "\033[36m... generating the embeddings for '$FLASK_ARG'\033[0m"
    echo ""
    modelScriptPath="app/scripts/model.py"
    python "$modelScriptPath" -f "$FLASK_ARG"

    # Display a success message when the script has been successfully run
    echo -e "\033[32mSUCCESS: embeddings successfully generated\033[0m"
    echo ""
fi


########################################################
##### FIFTH STEP : STARTING THE FLASK APPLICATION ######
########################################################

cd "$(dirname "$0")"

# Chemin vers le script Flask app.py
appScriptPath="app/app.py"

export PYTHONPATH="$(pwd)"
export FLASK_ARG=$FLASK_ARG  # Ensure FLASK_ARG is available to Flask

# Launching the application
echo "... starting Flask application for $FLASK_ARG"
echo ""
flask --app "$appScriptPath" --debug run &

# Wait a few seconds to ensure the app is well run
sleep 20

# Open homepage in the default browser
xdg-open "http://127.0.0.1:5000" || open "http://127.0.0.1:5000"
