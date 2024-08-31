import os
from flask import current_app as app

def write_tensor(tensor, filename):
    if os.path.exists(filename):
        app.logger.info(f"{filename} already exists!")
        return
    app.logger.info(f"writing in: {filename}")
    with open(filename, 'wb') as conf_file:
        for x in tensor.numpy():
            l = x.tolist()
            values = ';'.join(map(str, l)) if isinstance(l, list) else str(l)
            conf_file.write(values.encode('utf-8'))
            conf_file.write("\n".encode('utf-8'))