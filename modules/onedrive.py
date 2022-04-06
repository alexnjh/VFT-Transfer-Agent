import os
import cloudsync
import shutil
import cloudsync_onedrive
from typing import Any
from cloudsync import OType
from cloudsync.exceptions import CloudException, CloudTokenError, CloudDisconnectedError, CloudFileNotFoundError, CloudFileExistsError, CloudCursorError, CloudTemporaryError, CloudNamespaceError
from cloudsync.oauth import OAuthConfig
from modules.base import FileModule
from getpass import getpass
from utils.prompts import single_yes_or_no_question

## Override creds_changed class to save creds
class OAuthConfigSavedCred(OAuthConfig):

    def creds_changed(self, creds: Any):
        self._creds = creds

class OneDriveModule(FileModule):

    MAX_RETRIES = 3
    provider = ""

    def info():
        return {
        "name": "onedrive",
        "source": True,
        "destination": True,
        }

    # Module setup
    def __init__(self):

        check = single_yes_or_no_question("This module does not work without a web browser. Are you using a operating system with browser support?")

        if not check:
            raise Exception('Module does not support non desktop based operating systems!')

        client_id = input("Please enter app ID: ")
        client_secret = getpass("Please enter app secret: ")

        if client_id == "" or client_secret == "":
            raise Exception('Invalid app ID or secret!')

        oauth_config=OAuthConfigSavedCred(app_id=client_id,app_secret=client_secret, port_range=[20001,20005])

        # get an instance of the gdrive provider class
        provider = cloudsync.create_provider('onedrive', oauth_config)

        # Start the oauth process to login in to the cloud provider
        creds = provider.authenticate()

        # Use the credentials to connect to the cloud provider
        provider.connect(creds)

        provider.reconnect()

        self.provider = provider

    def list_files(self, root='/'):

        result=[]

        max_retries = self.MAX_RETRIES

        while True:
            try:
                for entry in self.provider.walk(root):
                    if self.provider.info_path(entry.path).otype == OType.FILE:
                        result.append(entry.path)
                return result
            except CloudTokenError:
                if max_retries != 0:
                    max_retries-=1
                    self.provider.reconnect()
                    continue
                else:
                    raise CloudException("Failed to refresh token. Please reinitialize plugin")

    def download_file(self, file_path, directory_path, file_name):

        max_retries = self.MAX_RETRIES

        while True:
            try:
                os.makedirs(directory_path, exist_ok=True)
                local_file_path = os.path.join(directory_path, file_name)
                with open(local_file_path, "wb") as f:
                    self.provider.download_path(file_path, f)
                    return "", True
            except CloudTokenError:
                if max_retries != 0:
                    max_retries-=1
                    self.provider.reconnect()
                    continue
                else:
                    return "Failed to refresh token. Please reinitialize plugin", False
            except CloudException as e:
                return str(e), False

    def upload_file(self, file_path, directory_path, file_name):

        max_retries = self.MAX_RETRIES

        while True:
            try:
                remote_file_path = os.path.join(directory_path, file_name)
                with open(file_path, "r") as f:
                    self.provider.mkdirs(directory_path)
                    self.provider.create(remote_file_path, f)
                    return "", True
            except CloudTokenError:
                if max_retries != 0:
                    max_retries-=1
                    self.provider.reconnect()
                    continue
                else:
                    return "Failed to refresh token. Please reinitialize plugin", False
            except CloudException as e:
                return str(e), False


    def remove_file(self, file_path):

        max_retries = self.MAX_RETRIES

        while True:
            try:
                print(self.provider.info_path(file_path))
                self.provider.delete(self.provider.info_path(file_path).oid)
                return True
            except CloudTokenError:
                if max_retries != 0:
                    max_retries-=1
                    self.provider.reconnect()
                    continue
                else:
                    raise CloudException("Failed to refresh token. Please reinitialize plugin")
