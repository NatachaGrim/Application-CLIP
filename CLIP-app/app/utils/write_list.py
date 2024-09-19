import os
from flask import current_app as app

# Function that writes a list to a file in binary mode
def write_list(a_list, filename):
    if os.path.exists(filename):
        app.logger.info(f"{filename} already exists!")
        return
    app.logger.info(f"writing in: {filename}")
    with open(filename, 'wb') as conf_file:
        for x in a_list:
            conf_file.write(str(x).encode('utf-8'))
            conf_file.write("\n".encode('utf-8'))
