from modules.base import FileModule
from paramiko import SSHClient,AutoAddPolicy
from scp import SCPClient
from getpass import getpass
from utils.prompts import single_yes_or_no_question

class SCPModule(FileModule):

    ssh_host = ""
    ssh_port = 22
    ssh_username = ""
    ssh_password = ""
    ssh_key = ""

    def info():
        return {
        "name": "scp",
        "source": False,
        "destination": True,
        }

    # Module setup
    def __init__(self):

        check = single_yes_or_no_question("Does SSH user have shell access?")
        if not check:
            raise Exception("SSH user needs to have shell access")

        self.ssh_host = input("SSH hostname: ")
        self.ssh_port = input("SSH port: ")
        check = single_yes_or_no_question("Use SSH key?")
        if check:
            self.ssh_key = input("Please enter path to SSH key: ")
        else:
            self.ssh_username = input("SSH username: ")
            self.ssh_password = getpass("SSH password: ")

    def list_files(self, root='/'):
        pass

    def download_file(self, file_path, directory_path, file_name):
        pass

    def upload_file(self, file_path, directory_path, file_name):
        with SSHClient() as ssh:

            try:
                ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(AutoAddPolicy())
                ssh.connect(self.ssh_host, self.ssh_port, self.ssh_username, self.ssh_password)
                ssh.exec_command('mkdir -p ' + directory_path)

                with SCPClient(ssh.get_transport()) as scp:
                    scp.put(file_path, recursive=True, remote_path="{}/{}".format(directory_path,file_name))

                return "", True
            except Exception as e:
                return str(e), False

    def remove_file(self, file_path):
        pass
