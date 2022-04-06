import shutil
import os
from os import walk
from modules.base import FileModule

class LocalDriveModule(FileModule):

    def info():
        return {
        "name": "local",
        "source": True,
        "destination": True,
        }

    # Module setup
    def __init__(self):
        pass

    def list_files(self, root='/'):

        result=[]

        for subdir, dirs, files in os.walk(root):
            for file in files:
                result.append(os.path.join(subdir, file))

        return result

    def download_file(self, file_path, directory_path, file_name):
        try:
            os.makedirs(directory_path, exist_ok=True)
            shutil.copy(file_path, "{}/{}".format(directory_path,file_name))
            return "", True
        except Exception as e:
            return str(e), False

    def upload_file(self, file_path, directory_path, file_name):
        try:
            os.makedirs(directory_path, exist_ok=True)
            shutil.copy(file_path, "{}/{}".format(directory_path,file_name))
            return "", True
        except Exception as e:
            return str(e), False

    def remove_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("The file does not exist")
