from abc import ABC, abstractmethod

class FileModule(ABC):

    @abstractmethod
    def list_files(self):
        pass

    @abstractmethod
    def download_file(self, file_path, directory_path, file_name):
        pass

    @abstractmethod
    def upload_file(self, file_path, directory_path, file_name):
        pass

    @abstractmethod
    def remove_file(self, file_path):
        pass
