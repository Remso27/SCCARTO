from qgis.core import *
from qgis.gui import *
from zipfile import ZipFile
import re
import os

@qgsfunction(args='auto', group='Custom')
def content_pamofor(zip_file_path, feature, parent):
    print("-" * 148)
    print("---------- V1: VERIFICATION DU NOM DU FICHIER LE FICHIER ZIP ----------")
    fichier = os.path.basename(zip_file_path)
        
    chemin_complet = os.path.join(zip_file_path)
    pattern_prov = r'^CF-\d{6}-\d{4}-06-LProv\.zip$'
    pattern_def = r'^CF-\d{6}-\d{4}-15-LDef\.zip$'
    
    #Vérifier si le nom de fichier correspond au modèle
    if re.match(pattern_prov, fichier):
        print("Le nom du fichier '{}' est conforme.".format(fichier))
    elif re.match(pattern_def, fichier):
        print("Le nom du fichier '{}' est conforme.".format(fichier))
    else:
        print("Le nom du fichier '{}' est non conforme.".format(fichier))
    
    print("")
    print("-" * 148)
    print("---------- V2: LE FICHIER ZIP DOIT CONTENIR LES 4 FICHIERS SUIVANTS POUR LE POINT ET LA POLYGONE : .shp, .prj, .dbf, .shx ----------")
    # Charger le fichier ZIP
    zip_path = str(zip_file_path)
    # Vérifier si le chemin du fichier ZIP existe
    if os.path.exists(zip_path):
        # Ouvrir le fichier ZIP en mode lecture
        with ZipFile(zip_path, 'r') as zip_ref:
            # Obtenir la liste des fichiers dans le ZIP
            file_list = zip_ref.namelist()

        # Créer une chaîne de texte avec la liste des fichiers
        content_text = "\n".join(file_list)

        # Afficher le contenu dans la console
        print(content_text)
        
        # Vous pouvez également enregistrer le contenu dans un fichier ou le renvoyer en tant que résultat selon vos besoins

    else:
        QgsMessageLog.logMessage("Le fichier ZIP spécifié n'existe pas.", "MonPlugin", QgsMessageLog.CRITICAL)
    print(" ")
    print("-" * 148)
    return None