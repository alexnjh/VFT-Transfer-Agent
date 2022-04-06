import os
from getpass import getpass
from modules.base import FileModule
from utils.prompts import single_yes_or_no_question
from smb.SMBConnection import SMBConnection

class SMBModule(FileModule):


    conn = None
    root = "/"

    def info():
        return {
        "name": "smb",
        "source": True,
        "destination": False,
        }

    # Module setup
    def __init__(self):
        username = input("Username:")
        password = getpass("Password: ")
        hostname = input("Hostname:")
        domain = input("Domain (Leave blank if not applicable):")
        if username == "" or password == "" or hostname == "":
            raise ValueException("Invalid credentials please try again.")

        conn = SMBConnection(username,password,username,hostname,domain,use_ntlm_v2=True,
                             sign_options=SMBConnection.SIGN_WHEN_SUPPORTED,
                             is_direct_tcp=True)

        connected = conn.connect(hostname,445)
        if not connected:
            raise Exception("Failed to connect to network share")

        self.conn = conn

    def list_files(self, root='/'):

        result = []

        for i in self.__smb_walk(root.lstrip('/')):
            if len(i[2]) > 0:
                for file in i[2]:
                    result.append("{}/{}/{}".format(root,i[0],file).replace('\\','/'))

        # Set share name for usage later
        self.root = root.lstrip('/')
        return result

    def download_file(self, file_path, directory_path, file_name):

        file_path = file_path.replace(self.root,"").lstrip('/')
        file_path = "/{}".format(file_path)
        os.makedirs(directory_path, exist_ok=True)
        with open("{}/{}".format(directory_path,file_name), 'wb') as fp:
            self.conn.retrieveFile(self.root, file_path, fp)
            return "", True

    def upload_file(self, file_path, directory_path, file_name):
        directory_path = directory_path.replace(self.root,"").lstrip('/')
        directory_path = "/{}".format(file_path)
        self.conn.createDirectory(self.root, directory_path)
        with open(file_path, 'wb') as fp:
            self.conn.storeFile(self.root, "{}/{}".format(directory_path,file_name), fp)
            return "", True

    def remove_file(self, file_path):
        file_path = file_path.replace(self.root,"").lstrip('/')
        file_path = "/{}".format(file_path)
        self.conn.deleteFiles(self.root, file_path)

    def __smb_walk(self, shareddevice, top='/'):

        conn = self.conn

        dirs, nondirs = [], []
        if not isinstance(conn, SMBConnection):
            raise TypeError("SMBConnection required")

        names = conn.listPath(shareddevice, top)
        for name in names:
            if name.isDirectory:
                if name.filename not in [u'.', u'..']:
                    dirs.append(name.filename)
            else:
                nondirs.append(name.filename)
        yield top, dirs, nondirs
        for name in dirs:
            new_path = os.path.join(top, name)
            for x in self.__smb_walk(shareddevice, new_path):
                yield x
