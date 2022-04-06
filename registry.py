from modules.onedrive import OneDriveModule
from modules.localdrive import LocalDriveModule
from modules.scp import SCPModule
from modules.smb import SMBModule

# INSTALLED MODULES
modules = {
OneDriveModule.info()['name']:OneDriveModule,
LocalDriveModule.info()['name']:LocalDriveModule,
SCPModule.info()['name']:SCPModule,
SMBModule.info()['name']:SMBModule
}
