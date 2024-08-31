import os
import clip
import torch
import csv
import glob
from flask import current_app as app

def initialize_app():
    # Log image folder
    app.logger.info(f"...working on image folder: {app.config['USE_CASE']}")

    # Load the CLIP model
    app.logger.info("...loading the CLIP model")
    print(clip.available_models())
    model, preprocess = clip.load("ViT-B/32")
    model.eval()
    input_resolution = model.visual.input_resolution
    context_length = model.context_length
    vocab_size = model.vocab_size

    # Load tensor
    tensor_pattern = os.path.join(app.config['TORCH_FOLDER'], f"clip_model_*_{app.config['USE_CASE']}.pt")
    tensor_files = glob.glob(tensor_pattern)
    if not tensor_files:
        app.logger.info(f".pt file is missing for pattern: {tensor_pattern}")
        quit()
    tensor_file = tensor_files[0]  # Take the first file that matches the pattern
    app.logger.info(f"...loading the embeddings from: {tensor_file}")
    image_features = torch.load(tensor_file, map_location=torch.device('cpu'))
    app.logger.info(image_features.size())

    # Check image folder
    if not os.path.exists(app.config['IMG_FOLDER']):
        app.logger.info(f"Images folder does not exist: {app.config['IMG_FOLDER']}")
        quit()
    directory_file = f"{app.config['PROJECT_LIST_FILE']}"
    app.logger.info(f"...reading the directory list: {directory_file}")
    if not os.path.exists(directory_file):
        app.logger.info(f"Directory list does not exist: {directory_file}")
        quit()
    with open(directory_file, encoding='utf-8') as f:
        image_paths = f.readlines()
    image_count = len(image_paths)
    app.logger.info(f"Number of images found: {image_count}")

    if image_count != image_features.size()[0]:
        app.logger.info("Tensor size and images number are different!")
        quit()

    # Load URLs
    urls = []
    image_urls = f"{app.config['USE_CASE']}_urls.txt"
    if not os.path.exists(image_urls):
        app.logger.info(f"### URLs list does not exist: {image_urls}")
    else:
        app.logger.info("...reading the URLs list")
        with open(image_urls) as f:
            urls = f.readlines()
        urls_count = len(urls)
        app.logger.info(f"Number of URLs found: {urls_count}")

    # Load predefined classes for classification
    labels = []
    captions = []
    labels_file = app.config['ONTOLOGY_FILE']
    if not os.path.exists(labels_file):
        app.logger.info(f"File for the class labels is missing: {labels_file}")
    else:
        # Build labels and ground truth
        gt_classes_idx = []
        examples_tot = 0
        paths = ' '.join(image_paths)
        with open(labels_file, encoding='utf-8') as f:
            label = csv.reader(f, delimiter=',')
            for row in label:
                labels.append(row[0])
                captions.append(row[1])
                examples = paths.count(f"{app.config['USE_CASE']}/{row[0]}")
                examples_tot += examples
                app.logger.info(f" -examples for class {row[0]}: {examples}")
                gt_idx = [labels.index(row[0])] * examples
                gt_classes_idx.extend(gt_idx)
        classes_nbr = len(labels)
        app.logger.info(f"Number of images in subfolders: {examples_tot}")

    return {
        'model': model,
        'preprocess': preprocess,
        'image_features': image_features,
        'image_paths': image_paths,
        'image_count': image_count,
        'urls': urls,
        'labels': labels,
        'captions': captions,
        'gt_classes_idx': gt_classes_idx,
        'classes_nbr': classes_nbr
    }