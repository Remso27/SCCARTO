from qgis.core import *
from qgis.gui import *
from zipfile import ZipFile
from qgis.utils import iface
import re
import os


@qgsfunction(args='auto', group='Custom')
def content_hors_pamofor(chemin, feature, parent):
    fichier = os.path.basename(chemin)
    return None