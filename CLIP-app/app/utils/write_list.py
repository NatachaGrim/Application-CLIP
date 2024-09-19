import os
from flask import current_app as app

def write_list(a_list, filename):
    """
    This function writes a list to a file in binary mode. The file is only created if it does not already exist.

    Arguments:
        :a_list: a Python list containing the data to be written to the file
        :filename: name of the file in which the tensor will be written

    Output:
        A file containing the written list
    """
    if os.path.exists(filename):
        app.logger.info(f"{filename} already exists!")
        return
    app.logger.info(f"writing in: {filename}")
    with open(filename, 'wb') as conf_file:
        for x in a_list:
            conf_file.write(str(x).encode('utf-8'))
            conf_file.write("\n".encode('utf-8'))
