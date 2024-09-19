import logging
from flask import Flask
import clip
import torch
import csv
import sys
import os

# Path to the parent directory to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.config import Config, use_case, torchFolder, img_folder, eval_folder, conf_mat_file, tensor_file, directory_file, directory_summary, image_urls, labels_file

app = Flask(__name__)

app.logger.info('... working on image folder: ' + img_folder)

# Load CLIP model
app.logger.info('...loading the CLIP model')
print(clip.available_models())
try:
    logging.info("Loading CLIP model...")
    model, preprocess = clip.load("ViT-B/32")
    logging.info("Model loaded successfully")
except EOFError:
    logging.error("EOFError: The model file is empty or corrupted")
except FileNotFoundError:
    logging.error("FileNotFoundError: The model file was not found")
except Exception as e:
    logging.error(f"An error occurred: {e}")

model.eval()
input_resolution = model.visual.input_resolution
context_length = model.context_length
vocab_size = model.vocab_size

# Load embeddings
if not os.path.exists(tensor_file):
    app.logger.info("Embeddings file is missing: " + tensor_file)
    quit()
app.logger.info("... loading the embeddings from: " + tensor_file)
image_features = torch.load(tensor_file, map_location=torch.device('cpu'))
app.logger.info(image_features.size())

# Check if the images folder exists
if not os.path.exists(img_folder):
    app.logger.info("Images folder does not exist: " + img_folder)
    quit()

# Read the file listing the path to the images
app.logger.info('... reading the directory list: ' + directory_file)
if not os.path.exists(directory_file):
    app.logger.info("Directory list does not exist: " + directory_file)
    quit()
with open(directory_file) as f:
    image_paths = f.readlines()

# Count the number of images listed in the file
image_count = len(image_paths)
app.logger.info("   number of images found: " + str(image_count))

# Check the number of images matches the number of loaded embeddings
if image_count != image_features.size()[0]:
    app.logger.info("Embeddings size and images number are different")
    quit()

# Check if the project summary file exists
if not os.path.exists(directory_summary):
    app.logger.info("Directory summary does not exist: " + directory_summary)
    quit()
with open(directory_summary) as f:
    summary = f.read()

# Check whether a list of URLs associated with images exists and read it 
urls = []
if not os.path.exists(image_urls):
    app.logger.info("### URLs list does not exist: " + image_urls)
else:
    app.logger.info('...reading the URLs list')
    with open(image_urls) as f:
        urls = f.readlines()
    urls_count = len(urls)
    app.logger.info("   number of URLs found: " + str(urls_count))

# Load image labels and captions
labels = []
captions = []
if not os.path.exists(labels_file):
    app.logger.info("### file for the class labels is missing: " + labels_file)
else:
    gt_classes_idx = []
    examples_tot = 0
    paths = ' '.join(image_paths)
    with open(labels_file, 'r', encoding='utf-8') as f:
        label = csv.reader(f, delimiter=';')
        for row in label:
            labels.append(row[0])
            captions.append(row[1])
            examples = paths.count(f"{use_case}/{row[0]}")
            examples_tot += examples
            app.logger.info(" -examples for class " + row[0] + ": " + str(examples))
            gt_idx = [labels.index(row[0])] * examples
            gt_classes_idx.extend(gt_idx)
    classes_nbr = len(labels)
    app.logger.info("   number of images in subfolders: " + str(examples_tot))

from app.routes import generales
