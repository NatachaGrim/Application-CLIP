"""
This script generates CLIP embeddings for a list of image files.

Arguments:
    :folderName: Folder where to search for image files. Must be within 'static/'.

Output:
    Torch tensor (.pt file) containing CLIP embeddings for the images.
    The file is saved in 'app/models/' with a filename formatted as 'clip_model_MM-DD-YYYY_projectName.pt'.
"""

try:
    from packaging import version
except ImportError:
    from pkg_resources import packaging

import numpy as np
import clip
import torch
import os
import argparse
from datetime import datetime
from PIL import Image

# Folder where the tensors are saved
model_folder = "app/models/"

# Argument parser initialization
parser = argparse.ArgumentParser(
    prog = 'model.py',
    description = 'Generates the CLIP embeddings for a list of images'
)
parser.add_argument('-f', '--folderName', help='The folder to be processed (must be in static/)', required=True)
args = parser.parse_args()
img_folder = os.path.join("app", "static", args.folderName, "images")

# Check if the specified image folder exists
if not os.path.exists(img_folder):
    print(f"'{img_folder}' folder does not exist!\n")
    quit()

print("... reading directory list for: ", img_folder)

# Read image paths from the directory list file
directory_file = os.path.join("app", "static", args.folderName, f"{args.folderName}_list.txt")
with open(directory_file) as f:
    image_paths = f.readlines()
image_count = len(image_paths)
print("Number of images found:", image_count)

# CLIP model setup
print("... loading the CLIP model.\n")
print("Torch version:", torch.__version__)

# Print available CLIP models
print(clip.available_models())

# Determine device (GPU if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load CLIP model
model, preprocess = clip.load("ViT-B/32", device=device)
model.to(device).eval()

# Display model parameters and configurations
input_resolution = model.visual.input_resolution
context_length = model.context_length
vocab_size = model.vocab_size

print(f"   Model parameters: {np.sum([int(np.prod(p.shape)) for p in model.parameters()]):,}")
print("   Input resolution:", input_resolution)
print("   Context length:", context_length)
print("   Vocab size:", vocab_size)

# Image preprocessing
preprocess

# Text preprocessing example
clip.tokenize("Hello world!").to(device)

# Process each image in the list
images = []
i = 0
print("... processing the images")

for filename in image_paths:
    filename = filename[:-1] # Chop newline character
    if (i % 10 == 0):
        print(i, " : ", filename)
    image = Image.open(filename).convert("RGB")
    images.append(preprocess(image))
    i += 1

# Convert processed images to torch tensor
print("... building the torch tensor")
image_input = torch.tensor(np.stack(images)).to(device)

# Generate CLIP embeddings for the images
print("... now generating the image features")
with torch.no_grad():
    image_features = model.encode_image(image_input).float()
    image_features /= image_features.norm(dim=-1, keepdim=True)

# Constructing model name with current date and project name
current_date = datetime.now().strftime("%m_%d_%Y")
model_name = f"{current_date}_{args.folderName}.pt"

# Path to save the output embeddings
output = os.path.join(model_folder, model_name)

# Save the embeddings tensor to a .pt file
print(f"Embeddings saved in {output}\n")
torch.save(image_features, output)