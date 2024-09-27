# Line break
Write-Output ""

# ASCII title
Write-Host @"
 ______   __       __   ______     ______   ______  ______  
/\  ___\ /\ \     /\ \ /\  __ \   /\  __ \ /\  __ \/\  __ \ 
\ \ \____\ \ \____\ \ \\ \  __/   \ \  __ \\ \  __/\ \  __/ 
 \ \_____\\ \_____\\ \_\\ \_\      \ \_\ \_\\ \_\   \ \_\   
  \/_____/ \/_____/ \/_/ \/_/       \/_/\/_/ \/_/    \/_/   
"@ -ForegroundColor Cyan 

Write-Output ""

################################################
##### FIRST STEP : CHOOSING A PROJECT FILE #####
################################################

# Enter the FLASK_ARG variable matching the project folder
Write-Host "Please enter the name of your project folder: " -NoNewline -ForegroundColor Cyan
$env:FLASK_ARG = Read-Host

do {
    # Check if the variable is empty
    if (-not $env:FLASK_ARG) {
        Write-Output ""

        # Display an error message if the variable is empty
        Write-Host "WARNING:" -NoNewline -ForegroundColor Black -BackgroundColor Red
        Write-Host " the project folder name must be entered" -ForegroundColor Red

        Write-Output ""

        # Re-enter the variable
        Write-Host "Please enter the name of your project folder: " -NoNewline -ForegroundColor Cyan
        $env:FLASK_ARG = Read-Host
    }
    
    # Check if the folder exists
    elseif (-not (Test-Path "app\static\$($env:FLASK_ARG)")) {
        Write-Output ""

        # Display an error message if folder name is incorrect
        Write-Host "WARNING:" -NoNewline -ForegroundColor Black -BackgroundColor Red
        Write-Host " either the folder name is incorrect or does not exist" -ForegroundColor Red

        Write-Output ""

        # Re-enter the variable
        Write-Host "Please enter the name of your project folder: " -NoNewline -ForegroundColor Cyan
        $env:FLASK_ARG = Read-Host
    }
} while (-not $env:FLASK_ARG -or -not (Test-Path "app\static\$($env:FLASK_ARG)"))

Write-Output ""

# Display a success message when the variable is validated
Write-Host "SUCCESS:" -NoNewline -ForegroundColor Black -BackgroundColor Green
Write-Host " your project folder is set to: " -NoNewline -ForegroundColor Green
Write-Host "$env:FLASK_ARG"

Write-Output ""

############################################
##### SECOND STEP : LISTING THE IMAGES #####
############################################

# Path to script and output files
$scriptPath = Join-Path -Path $PSScriptRoot -ChildPath "app\scripts\recurse.py"
$outputFilePath = Join-Path -Path $PSScriptRoot -ChildPath "app\static\$($env:FLASK_ARG)\$($env:FLASK_ARG)_directory.txt"

# If the "project_name_list.txt" file does not exist, run the "recurse.py" script
if (-not (Test-Path $outputFilePath)) {
    Write-Host "... listing the folder " -NoNewline -ForegroundColor Cyan
    Write-Host "$env:FLASK_ARG"

    Write-Output ""

    # Run "recurse.py" script with the correct path
    python $scriptPath -f "app\static\$($env:FLASK_ARG)" | Out-File -FilePath $outputFilePath

    # Display a success message when the script has been successfully run
    Write-Host "SUCCESS:" -NoNewline -ForegroundColor Black -BackgroundColor Green
    Write-Host " the recurse.py script has been successfully run" -ForegroundColor Green

    Write-Output ""
}

#############################################
##### SECOND STEP : CONVERTING ONTOLOGY #####
#############################################

# Path to script and output files
$ontologyScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "app\scripts\ontology.py"
$outputFilePath = Join-Path -Path $PSScriptRoot -ChildPath "app\static\$($env:FLASK_ARG)\ontology\$($env:FLASK_ARG)_ontology.csv"

# Path to the target .txt file
$targetFilePath = Join-Path -Path $PSScriptRoot -ChildPath "app\static\$($env:FLASK_ARG)\ontology\$($env:FLASK_ARG)_ontology.txt"

Write-Host "... converting the ontology of " -NoNewline -ForegroundColor Cyan
Write-Host "$env:FLASK_ARG"

Write-Output ""

# Run "ontology.py" script
python $ontologyScriptPath $targetFilePath

# Display a success message when the script has been successfully run
Write-Host "SUCCESS:" -NoNewline -ForegroundColor Black -BackgroundColor Green
Write-Host " the ontology.py script has been successfully run" -ForegroundColor Green

Write-Output ""


#################################################
##### THIRD STEP : BUILDING CLIP EMBEDDINGS #####
#################################################

# Check if any model file exists in "app/models" that ends with "$($env:FLASK_ARG).pt"
$modelPath = Join-Path -Path $PSScriptRoot -ChildPath "app\models"
$modelExists = Get-ChildItem -Path $modelPath -Filter "*$($env:FLASK_ARG).pt" | Where-Object { $_.Name -like "*$($env:FLASK_ARG).pt" }

if (-not $modelExists) {
    Write-Host "... generating the embeddings for " -NoNewline -ForegroundColor Cyan
    Write-Host "$env:FLASK_ARG"

    Write-Output ""

    # Path to the "model.py" script
    $modelScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "app\scripts\model.py"

    # Run "model.py" script
    python $modelScriptPath -f "$env:FLASK_ARG"

    # Display a success message when the script has been successfully run
    Write-Host "SUCCESS:" -NoNewline -ForegroundColor Black -BackgroundColor Green
    Write-Host " the model.py script has been successfully run" -ForegroundColor Green

    Write-Output ""
 }
# else {
#     # Ask the user if they want to fine-tune the model
#     do {
#         Write-Host "Do you want to fine-tune your model? Enter YES or NO: " -NoNewline -ForegroundColor Cyan
#         $fineTuneResponse = Read-Host
#         Write-Output ""

#         if ($fineTuneResponse -eq "YES") {
#             Write-Host "Starting fine-tuning process..." -ForegroundColor Cyan

#             # Define paths
#             $fineTuneScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "fine_tune\scripts\fine_tune_clip.py"
#             $fineTuneDataPath = Join-Path -Path $PSScriptRoot -ChildPath "fine_tune\data"
            
#             # Run the fine-tuning script
#             python $fineTuneScriptPath -f "$env:FLASK_ARG"

#             # Display a success message when the script has been successfully run
#             Write-Host "SUCCESS:" -NoNewline -ForegroundColor Black -BackgroundColor Green
#             Write-Host " the fine_tune_clip.py script has been successfully run" -ForegroundColor Green

#             Write-Output ""
#             break
#         } elseif ($fineTuneResponse -eq "NO") {
#             Write-Host "Fine-tuning process skipped" -ForegroundColor Cyan
#             Write-Output ""
#             break
#         } else {
#             Write-Host "WARNING:" -NoNewline -ForegroundColor Black -BackgroundColor Red
#             Write-Host " invalid input, please enter YES or NO" -ForegroundColor Red
#             Write-Output ""
#         }
#     } while ($true)
# }

########################################################
##### FOURTH STEP : STARTING THE FLASK APPLICATION #####
########################################################

Set-Location -Path $PSScriptRoot

# Path to script
$appScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "app\app.py"

$env:PYTHONPATH = "$PSScriptRoot"

Write-Host "... starting Flask application for " -NoNewline -ForegroundColor Cyan
Write-Host "$env:FLASK_ARG"

Write-Output ""

# Launching the application
Start-Process "flask" "--app $appScriptPath --debug run" -NoNewWindow

# Wait a few seconds to ensure the app is well run
Start-Sleep -Seconds 15

# Open homepage in default browser
Start-Process "http://127.0.0.1:5000"
