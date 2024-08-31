from flask import request, render_template
import clip
import torch
import random
import os
from pathlib import Path
import csv
# from app import app
from app.app import app, model, image_features, labels, captions, image_paths, urls, classes_nbr, conf_mat_file, eval_folder, use_case, examples_tot, image_count, img_folder
from app.config import maxResults, gap, maxThumbnails
from app.utils.chop import chop
from app.utils.confusion_matrix import write_conf_mat
from app.utils.tensor import write_tensor
from app.utils.write_list import write_list
from torchmetrics.classification import MulticlassConfusionMatrix, MulticlassAccuracy

def generate_image_paths():
    use_case = os.environ.get("FLASK_ARG", "")
    base_path = Path(f"app/static/{use_case}/images")

    image_paths = []

    if base_path.exists() and base_path.is_dir():
        for category_path in base_path.iterdir():
            if category_path.is_dir():
                # Chercher les fichiers .jpg, .jpeg, et .png dans chaque sous-dossier
                for ext in ["*.jpg", "*.jpeg", "*.png"]:
                    image_paths.extend([
                        str(img.relative_to(Path("app/static"))).replace("\\", "/")
                        for img in category_path.glob(ext)
                    ])

    return image_paths

@app.route('/', methods=("POST", "GET"))
def page():
    
    image_paths = generate_image_paths()
    
    if request.method == "POST":
        app.logger.info('...receiving POST request')

        query = request.form["prompt"]
        urls_top_prob = []

        if query in labels:
            label_index = labels.index(query)
            caption = captions[label_index]
            app.logger.info("#################")
            app.logger.info("Query: " + caption)
            app.logger.info(" against " + str(classes_nbr) + " classes")
            text_descriptions = [f"{label}" for label in captions]
            text_tokens = clip.tokenize(text_descriptions)
            with torch.no_grad():
                text_features = model.encode_text(text_tokens).float()
                text_features /= text_features.norm(dim=-1, keepdim=True)
            text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)

            top_probs, top_labels = text_probs.cpu().topk(2, dim=-1)
            write_tensor(top_probs, eval_folder + use_case + "_probs2.txt")
            app.logger.info("####### top probs for the top-2 classes [10 first images] ##########")
            app.logger.info(top_probs[:10])
            app.logger.info("####### label index for the top-2 classes")
            app.logger.info(top_labels[:10])

            tuples = []
            num_images = min(len(top_labels), len(top_probs), len(image_paths))
            for i in range(num_images):
                if ((top_labels[i][0] == label_index) or (top_labels[i][1] == label_index and top_probs[i][1] / top_probs[i][0] > gap)):
                    if query in image_paths[i]:
                        css1 = "green" if top_labels[i][0] == label_index else "silver"
                        css2 = "silver" if top_labels[i][0] != label_index else "green"
                    else:
                        css1 = "crimson"
                        css2 = "crimson"
                    tuples.append((image_paths[i], top_labels[i][0], float(top_probs[i][0]), top_labels[i][1], float(top_probs[i][1]), css1, css2, i))

            '''
            tuples = []
            for i, image in enumerate(image_paths):
                if ((top_labels[i][0] == label_index) or (top_labels[i][1] == label_index and top_probs[i][1] / top_probs[i][0] > gap)):
                    if query in image_paths[i]:
                        css1 = "green" if top_labels[i][0] == label_index else "silver"
                        css2 = "silver" if top_labels[i][0] != label_index else "green"
                    else:
                        css1 = "crimson"
                        css2 = "crimson"
                    tuples.append((image_paths[i], top_labels[i][0], float(top_probs[i][0]), top_labels[i][1], float(top_probs[i][1]), css1, css2, i))
            '''
                    
            app.logger.info("  number of images validating the query: " + str(len(tuples)))

            decreasing = sorted(tuples, key=lambda criteria: criteria[2], reverse=True)
            name_image_top_prob = [i[0] for i in decreasing[:maxResults]]
            FP1 = [i[5] for i in decreasing[:maxResults]]
            FP2 = [i[6] for i in decreasing[:maxResults]]
            if len(urls) != 0:
                urls_top_prob = [i[7] for i in decreasing[:maxResults]]
            app.logger.info("####### files for the result images ##########")
            app.logger.info(name_image_top_prob[:10])
            prob1 = [i[2] for i in decreasing[:maxResults]]
            string_prob1 = ["%.2f" % number for number in prob1]
            class1 = [labels[i[1]] for i in decreasing[:maxResults]]
            app.logger.info("####### top prob #1 for the result images ##########")
            app.logger.info(string_prob1[:10])
            app.logger.info("####### class of the top prob #1 ##########")
            app.logger.info(class1[:10])

            prob2 = [i[4] for i in decreasing[:maxResults]]
            string_prob2 = ["%.2f" % number for number in prob2]
            class2 = [labels[i[3]] for i in decreasing[:maxResults]]
            app.logger.info("####### top prob #2 for the result images ##########")
            app.logger.info(string_prob2[:10])
            app.logger.info("####### class of the top prob #2 ##########")
            app.logger.info(class2[:10])

            if os.path.exists(conf_mat_file):
                app.logger.info(conf_mat_file + " already exists!")
                confmatfile = conf_mat_file
            elif image_count != examples_tot:
                conf_msg = "## Confusion Matrix calculation: something is wrong with the ground truth!\n(images must be stored in subfolders; subfolders must be named accordingly to labels; labels must be sorted) ##"
                app.logger.info(conf_msg)
                app.logger.info("images files: " + str(image_count))
                app.logger.info("images in GT folders: " + str(examples_tot))
                confmatfile = "static/_eval/_confusion.txt"
            else:
                app.logger.info("...computing the confusion matrix")
                pred_classes_idx = torch.argmax(text_probs, dim=1)
                pred = torch.tensor(pred_classes_idx)
                target = torch.tensor(gt_classes_idx)
                conf_mat = MulticlassConfusionMatrix(num_classes=classes_nbr)
                confusion = conf_mat(pred, target)

                write_tensor(pred, eval_folder + use_case + "_pred.txt")
                write_tensor(target, eval_folder + use_case + "_GT.txt")
                GT_labels = [labels[i] for i in target]
                write_list(GT_labels, eval_folder + use_case + "_GT_labels.txt")
                pred_labels = [labels[i] for i in pred]
                write_list(pred_labels, eval_folder + use_case + "_pred_labels.txt")

                metric = MulticlassAccuracy(num_classes=classes_nbr, average="micro")
                acc = metric(pred, target) * 100.0
                accuracy1 = "%.2f" % acc
                app.logger.info(accuracy1)
                metric = MulticlassAccuracy(num_classes=classes_nbr, average=None)
                acc = metric(pred, target)
                acc_class = [i * 100.0 for i in acc]
                acc_class = ["%.2f" % number for number in acc_class]
                accuracy2 = ' % / '.join(acc_class) + " %"
                app.logger.info(accuracy2)
                write_conf_mat(confusion, conf_mat_file, accuracy1, accuracy2)
                confmatfile = conf_mat_file
            return render_template("grid_classif.html", files=name_image_top_prob, urls=urls_top_prob, nlabels=classes_nbr, target_class=query, use_case=use_case, caption=caption, class1=class1, prob1=string_prob1, fp1=FP1, fp2=FP2, class2=class2, prob2=string_prob2, confmatfile=confmatfile, nb_results=str(len(tuples)), comment_fr=str(maxResults) + " affichés au maximum", comment=str(maxResults) + " maximum displayed")
        else:
            text_descriptions = [f"" + query]
            app.logger.info(text_descriptions)
            text_tokens = clip.tokenize(text_descriptions)
            with torch.no_grad():
                text_features = model.encode_text(text_tokens).float()
                text_features /= text_features.norm(dim=-1, keepdim=True)
            text_probs = (image_features @ text_features.T)
            sorted_values, indices = torch.sort(text_probs, dim=0, descending=True)
            name_image_top_prob = [image_paths[i] for i in indices[:maxResults]]
            urls_top_prob = [urls[i] for i in indices[:maxResults]] if len(urls) != 0 else []
            prob = sorted_values[:maxResults]
            string_prob = ["%.3f" % number for number in prob]
            return render_template("grid_cbir.html", files=name_image_top_prob, urls=urls_top_prob, prob=string_prob, query=query, use_case=use_case, comment_fr="(" + str(maxResults) + " premiers résultats affichés)", comment="(first " + str(maxResults) + " results displayed)")
    else:
        app.logger.info('...Starting to populate the image grid')
        app.logger.info('   from folder: ' + img_folder)

        image_paths = generate_image_paths()  # Génère les chemins des images
        random_files = random.sample(image_paths, min(len(image_paths), maxThumbnails))

        app.logger.info(f"   files: {len(image_paths)}")

        '''
        random_files = []
        i = 0
        n = 0
        r = int(image_count / maxThumbnails)
        for filename in image_paths:
            n += 1
            rdm = random.randint(0, r)
            if rdm == r:
                filename = filename[:-1]
                random_files.append(filename)
                i += 1
            if i >= maxThumbnails:
                break
        app.logger.info(f"   files: {n}")
        '''

        app.logger.info(labels)
        if not labels:
            return render_template("home.html", files=random_files, urls=urls, msg='Use a free query:', classes='', count=image_count)
        else:
            return render_template("home.html", files=random_files, urls=urls, msg='Utilisez une requête libre ou une des classes ci-dessous (use a free query OR one of these predefined classes) : ', classes=', '.join(labels), count=image_count)
