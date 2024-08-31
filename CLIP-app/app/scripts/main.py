from flask import Flask, redirect, request, url_for, render_template
from PIL import Image
from tqdm import tqdm
import torch
import os
import clip
import numpy as np
import random
from torchmetrics.classification import MulticlassConfusionMatrix, MulticlassAccuracy, MulticlassRecall

from app.config import MAX_RESULTS, MAX_THUMBNAILS, TORCH_FOLDER, MIN_PROB, GAP, USE_CASE, IMG_FOLDER, EVAL_FOLDER, CONF_MAT_FILE
from app.utils.chop import chop
from app.utils.confusion_matrix import write_conf_mat
from app.utils.tensor import write_tensor
from app.utils.write_list import write_list

app = Flask(__name__)

app.logger.info(f"...working on image folder: {IMG_FOLDER}")

app.logger.info("...loading the CLIP model")
print(clip.available_models())

model, preprocess = clip.load("ViT-B/32")
model.eval()
input_resolution = model.visual.input_resolution
context_length = model.context_length
vocab_size = model.vocab_size

# Tensor
tensor_file = f"{TORCH_FOLDER}{USE_CASE}_torch.pt"
if not os.path.exists(tensor_file):
    app.logger.info(f"### Torch tensor is missing: {tensor_file}")
    quit()
app.logger.info(f"...loading the embeddings from: {tensor_file}")
image_features = torch.load(tensor_file, map_location=torch.device('cpu'))
app.logger.info(image_features.size())

# Image files
if not os.path.exists(IMG_FOLDER):
    app.logger.info(f"### images folder does not exist: {IMG_FOLDER}")
    quit()
directory_file = f"{IMG_FOLDER}.txt"
app.logger.info(f"...reading the directory list: {directory_file}")
if not os.path.exists(directory_file):
    app.logger.info(f"### directory list does not exist: {directory_file}")
    quit()
with open(directory_file, encoding='utf-8') as f:
    image_paths = f.readlines()
image_count = len(image_paths)
app.logger.info(f"   number of images found: {image_count}")

if image_count != image_features.size()[0]:
    app.logger.info("### Tensor size and images number are different!")
    quit()

# URLs
urls = []
image_urls = f"{IMG_FOLDER}_urls.txt"
if not os.path.exists(image_urls):
    app.logger.info(f"### URLs list does not exist: {image_urls}")
else:
    app.logger.info("...reading the URLs list")
    with open(image_urls) as f:
        urls = f.readlines()
    urls_count = len(urls)
    app.logger.info(f"   number of URLs found: {urls_count}")

# Reading the predefined classes for the classification scenario
labels = []
captions = []
labels_file = f"{IMG_FOLDER}_labels.csv"
if not os.path.exists(labels_file):
    app.logger.info(f"### file for the class labels is missing: {labels_file}")
else:
    # Building the labels and the GT
    gt_classes_idx = []
    examples_tot = 0
    paths = ' '.join(image_paths)
    with open(labels_file, encoding='utf-8') as f:
        label = csv.reader(f, delimiter=',')
        for row in label:
            labels.append(row[0])
            captions.append(row[1])
            examples = paths.count(f"{USE_CASE}/{row[0]}")
            examples_tot += examples
            app.logger.info(f" -examples for class {row[0]}: {examples}")
            gt_idx = [labels.index(row[0])] * examples
            gt_classes_idx.extend(gt_idx)
    classes_nbr = len(labels)
    app.logger.info(f"   number of images in subfolders: {examples_tot}")