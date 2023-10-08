from qgis.core import *
from qgis.gui import *
from zipfile import ZipFile
from qgis.utils import iface
import re
import os
import pandas as pd

@qgsfunction(args='auto', group='Custom')
def content_hors_pamofor(chemin, feature, parent):
    """
    print("-" * 148)
    print("---------- V1: VERIFICATION DE LA STRUCTURE DES REPERTOIRES ----------")
    # Vérifier si le chemin correspond au format spécifié
    pattern_1 =  r".*(CF\\[a-zA-Z0-9]+(\\[a-zA-Z0-9]+)*)"
    pattern_2 =  r".*(DTV\\[a-zA-Z0-9]+(\\[a-zA-Z0-9]+)*)"
    
    match_1 = re.search(pattern_1, chemin)
    match_2 = re.search(pattern_2, chemin)
    if match_1:
        # Si le format est respecté, on extrait le chemin à partir de "\CF" et l'imprime
        chemin_extracted = match_1.group(1)
        print("Voici la structure du répertoire des fichiers: " + f"'{chemin_extracted}'" + "\nCette structure est conforme.")
    elif match_2:
        chemin_extracted = match_2.group(1)
        print("Voici la structure du répertoire des fichiers: " + f"'{chemin_extracted}'" + "\nCette structure est conforme.")
    else:
        print("Voici la structure du répertoire des fichiers: " + f"'{chemin}'" + "\nCette structure du répertoire n'est pas conforme.")
    
    
    print("")
    print("-" * 148)
    print("---------- V2: VERIFICATION DU CONTENU DU DOSSIER CHARGE ----------")
    # Obtenez la liste des fichiers dans le dossier
    print("Voici la liste des fichiers chargés: ")
    if os.path.exists(chemin):
        fichiers = os.listdir(chemin)
        for fichier in fichiers:
            print(f"'{fichier}'")
    """
    return None