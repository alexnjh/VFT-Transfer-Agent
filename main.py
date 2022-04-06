import sys,os
import time
import click
import questionary
from utils.helper import flush_input
from registry import modules
# using datetime module
import datetime

# Override request function in order for it to use a different cert bundle
def override_where():
    """ overrides certifi.core.where to return actual location of cacert.pem"""
    # change this to match the location of cacert.pem
    return os.path.abspath("cacert.pem")

# is the program compiled?
if hasattr(sys, "frozen"):
    import certifi.core

    os.environ["REQUESTS_CA_BUNDLE"] = override_where()
    certifi.core.where = override_where

    # delay importing until after where() has been replaced
    import requests.utils
    import requests.adapters
    # replace these variables in case these modules were
    # imported before we replaced certifi.core.where
    requests.utils.DEFAULT_CA_BUNDLE_PATH = override_where()
    requests.adapters.DEFAULT_CA_BUNDLE_PATH = override_where()

#########

class QuestionaryOption(click.Option):

    def __init__(self, param_decls=None, **attrs):
        click.Option.__init__(self, param_decls, **attrs)
        if not isinstance(self.type, click.Choice):
            raise Exception('ChoiceOption type arg must be click.Choice')

    def prompt_for_value(self, ctx):
        val = questionary.select(self.prompt, choices=self.type.choices).unsafe_ask()
        return val

# Generate modules list
src = []
dst = []

for mod in modules.values():
    if mod.info()["source"]:
        src.append(mod.info()['name'])
    if mod.info()["destination"]:
        dst.append(mod.info()['name'])

source_dir="/firmware"
destination_dir = '/firmware'

#to get the current working directory
curr_directory = os.getcwd()
temp_dir = os.path.join(curr_directory, "temp").replace('\\','/')

def remove_file_from_temp(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("The file does not exist")

@click.command()
@click.option('--polling-interval', prompt='Polling timeout (Seconds)', default=300)
@click.option('--source-module', prompt='Source module', type=click.Choice(src, case_sensitive=False), cls=QuestionaryOption)
# @click.option('--source-module',
#               type=click.Choice(['onedrive', 'local', 'scp', 'smb'], case_sensitive=True))
@click.option('--source-dir', prompt='Please enter source directory to monitor')
@click.option('--destination-module', prompt='Destination module', type=click.Choice(dst, case_sensitive=False), cls=QuestionaryOption)
# @click.option('--destination-module',
#               type=click.Choice(['onedrive', 'local', 'scp', 'smb'], case_sensitive=True))
@click.option('--destination-dir', prompt='Please enter destination directory to monitor')
def main(polling_interval, source_module, source_dir, destination_module, destination_dir):

    if source_module == None:
        print("[ERROR] --source-module option is required")
        return

    if destination_module == None:
        print("[ERROR] --destination-module option is required")
        return

    destination_dir = destination_dir.replace('\\','/')


    print("\n############################# {} CONFIG #############################\n".format(source_module))
    source_module = modules[source_module]()
    flush_input()
    print("\n############################# {} CONFIG #############################\n".format(destination_module))
    destination_module = modules[destination_module]()

    while True:

        for i in source_module.list_files(source_dir):

            # Step 1: Ensure temp folder is created
            os.makedirs(temp_dir, exist_ok=True)

            # Step 2: Filter out needed components from the file path
            filename = os.path.basename(i)
            directory = os.path.dirname(i)

            # Step 3: Remove the source path from the absolute path of the file
            if directory.startswith(source_dir):
                directory=directory.replace(source_dir,"")

            # Step 4: Download the file in to the temp folder
            print("{} [*] Downloading file {} to {}".format(datetime.datetime.now(),i,temp_dir))
            msg, status = source_module.download_file(i,temp_dir, filename)

            if status == False:
                print(msg)
                continue

            # Step 5: Upload the file to the destination
            dest_dir_path = "{}/{}".format(destination_dir.replace('\\','/'), directory.lstrip('/').replace('\\','/'))
            file_path = os.path.join(temp_dir.replace('\\','/'), filename.lstrip('/').replace('\\','/'))

            if destination_module == "local":
                os.makedirs(dest_dir_path, exist_ok=True)

            print("{} [*] Moving {} to {}".format(datetime.datetime.now(),i, dest_dir_path))

            msg, status = destination_module.upload_file(file_path, dest_dir_path, filename)

            if status == False:
                print(msg)
                continue

            print("{} [*] Removing {} from {}".format(datetime.datetime.now(),i, temp_dir))
            # Remove file from temp location
            remove_file_from_temp(file_path)

            print("{} [*] Removing {} from {}".format(datetime.datetime.now(),i, source_dir))
            # Remove file from source location
            source_module.remove_file(i)

        time.sleep(polling_interval)


if __name__ == '__main__':
    main()
