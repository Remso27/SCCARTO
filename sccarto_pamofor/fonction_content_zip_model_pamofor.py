from qgis.core import *
from qgis.gui import *
from zipfile import ZipFile
import re
import os


@qgsfunction(args='auto', group='Custom')
def content_pamofor(zip_file_path, feature, parent):
    fichier = os.path.basename(zip_file_path)
    return None