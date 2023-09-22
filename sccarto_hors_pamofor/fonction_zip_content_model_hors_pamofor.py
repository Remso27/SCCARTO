from qgis.core import *
from qgis.gui import *
from zipfile import ZipFile
from qgis.utils import iface
import re
import os

@qgsfunction(args='auto', group='Custom')
def content_hors_pamofor(chemin, feature, parent):
    print("-" * 148)
    print("---------- V1: VERIFICATION DE LA STRUCTURE DES REPERTOIRES ----------")
    # Vérifier si le chemin correspond au format spécifié
    pattern = r".*(CF\\[a-zA-Z0-9]+(\\[a-zA-Z0-9]+)*)"
    match = re.search(pattern, chemin)
    if match:
        # Si le format est respecté, on extrait le chemin à partir de "\CF" et l'imprime
        chemin_extracted = match.group(1)
        print("Voici la structure du répertoire des fichiers: " + f"'{chemin_extracted}'" + "\nCette structure est conforme.")
    else:
        print("Cette structure du répertoire n'est pas conforme.")
    
    
    print("")
    print("-" * 148)
    print("---------- V2: VERIFICATION DU CONTENU DU DOSSIER CHARGE ----------")
    structure = os.path.join(chemin)   
    # Obtenez la liste des fichiers dans le dossier
    print("Voici la liste des fichiers chargés: ")
    if os.path.exists(chemin):
        fichiers = os.listdir(chemin)
        for fichier in fichiers:
            print(f"'{fichier}'")