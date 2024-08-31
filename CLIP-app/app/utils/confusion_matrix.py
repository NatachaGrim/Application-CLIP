import os
from flask import current_app as app

def write_conf_mat(tensor, filename, labels, accuracy1, accuracy2):
    app.logger.info(f"writing in: {filename}")
    with open(filename, 'wb') as conf_file:
        labs = '\t'.join(map(lambda s: s[:5], labels))
        app.logger.info(labs)
        conf_file.write('GT\\pred '.encode('utf-8') + labs.encode('utf-8'))
        conf_file.write("\n".encode('utf-8'))
        for i, x in enumerate(tensor.numpy()):
            conf_file.write("\n".encode('utf-8'))
            l = x.tolist()
            values = '\t'.join(map(str, l))
            app.logger.info(values)
            conf_file.write(labels[i][:5].encode('utf-8') + '\t'.encode('utf-8') + values.encode('utf-8'))
        conf_file.write("\n\n".encode('utf-8'))
        conf_file.write(f"Accuracy (micro average): {accuracy1}\n".encode('utf-8'))
        conf_file.write("Accuracy (per class): \n".encode('utf-8'))
        heading = ' / '.join(labels)
        conf_file.write(heading.encode('utf-8'))
        conf_file.write("\n".encode('utf-8'))
        conf_file.write(accuracy2.encode('utf-8'))