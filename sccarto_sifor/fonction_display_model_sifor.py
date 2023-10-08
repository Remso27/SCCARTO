from qgis.core import *
from qgis.gui import *
from osgeo import ogr
from zipfile import ZipFile
import os
import re
from qgis.PyQt.QtCore import QVariant
from colorama import Fore, Back, Style



@qgsfunction(args='auto', group='Custom')
# le paramètre layers est le chemin du dossier
def display_sifor(zip_file, feature, parent):
    print("-" * 140)
    print("---------- V1: VERIFICATION DU NOM DU FICHIER LE FICHIER ZIP ----------")
    print(Fore.RED + 'NC')
    resultat_analyse = []
    fichier = os.path.basename(zip_file)
    chemin_complet = os.path.join(zip_file)
    pattern_prov = r'^CF-\d{6}-\d{4}-06-LProv\.zip$'
    pattern_prov_TV = r'^TV-\d{6}-06-LProv\.zip$'
    pattern_def = r'^CF-\d{6}-\d{4}-15-LDef\.zip$'
    pattern_def_TV = r'^TV-\d{6}-15-LDef\.zip$'
    
    #Vérifier si le nom de fichier correspond au modèle
    if re.match(pattern_prov, fichier) or re.match(pattern_def, fichier) or re.match(pattern_prov_TV, fichier) or re.match(pattern_def_TV, fichier):
        print("Le nom du fichier '{}' est conforme.".format(fichier))
    else:
        resultat_analyse.append("Non conforme")
        print("Le nom du fichier '{}' est non conforme.".format(fichier))
    
    print("")
    print("-" * 140)
    print("---------- V2: LE FICHIER ZIP DOIT CONTENIR LES 4 FICHIERS SUIVANTS POUR LE POINT ET LA POLYGONE : .shp, .prj, .dbf, .shx ----------")
    # Charger le fichier ZIP
    zip_path = str(zip_file)
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
    print("-------------- V3 & V4 : VERIFICATION DE LA GEOMETRIE ET LES SYSTÈMES  DE COORDONNÉES DES COUCHES --------------")
    zip_file_name = os.path.splitext(zip_file)[0]
    # Créez un dossier pour sauvegarder le contenu du ZIP s'il n'existe pas déjà
    output_folder = os.path.join(os.path.dirname(zip_file), zip_file_name)
    # output_folder est le dossier de sauvegarde du contenu du ZIP
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with ZipFile(zip_file, 'r') as zipfile:
        # Décompression du fichier zip
        zipfile.extractall(output_folder)
    extension = [".shp", ".SHP"]
    # Vérification de la validité du chemin des fichiers
    if not output_folder:
        raise ValueError("Le chemin des couches est vide")
    # Parcourir les fichiers du dossier
    for fichier in os.listdir(output_folder):
        chemin_fichier = os.path.join(output_folder, fichier)
        # Vérifier si le fichier a une extension de shapefile
        if os.path.isfile(chemin_fichier) and any(fichier.endswith(ext) for ext in extension):
            # Extraire le nom de fichier sans extension pour le nom de la couche
            nom_couche = os.path.splitext(fichier)[0]
            # Charger la couche vecteur depuis le shapefile
            couche = QgsVectorLayer(chemin_fichier, nom_couche, "ogr")
            
            # Vérifier si la couche a été chargée avec succès
            if couche.isValid():
                # Ajouter la couche à la vue QGIS
                QgsProject.instance().addMapLayer(couche)
            else:
                print("Impossible de charger la couche vecteur depuis {}.".format(chemin_fichier))

            # Vérifier le type de géométrie de la couche
            geom = couche.wkbType()
            if geom == QgsWkbTypes.Point:
                print("La géométrie du fichier '{}' est de type 'Point'.".format(nom_couche))
            elif geom == QgsWkbTypes.MultiPolygon:
                print("La géométrie du  fichier '{}' est de type 'Polygone.'".format(nom_couche))
            else:
                print("La géométrie du fichier '{}' est de type 'Inconnu.'".format(nom_couche))
              
            crs = couche.crs().authid()
            if crs == 'EPSG:32629':
                print("Le fichier '{}' a pour système de coordonnée: {}. Ce système est autorisé.".format(nom_couche, "EPSG:32629"))
                print("-"* 50)
            elif crs == 'EPSG:32630':
                print("Le fichier '{}' a pour système de coordonnée: {}. Ce système est autorisé.".format(nom_couche, "EPSG:32630"))
            else:
                resultat_analyse.append("Non conforme")
                print("Le fichier '{}' a pour système de coordonnée: {}. Ce système n'est pas autorisé.".format(nom_couche, crs))
    print(" ")
    print("-" * 148)
    print("-------------- V5: VERIFICATION DES PREFIXES DES FICHIERS DE TYPE POLYGONE --------------")
    for fichier in os.listdir(output_folder):
        chemin_fichier = os.path.join(output_folder, fichier)
        # Vérifier si le fichier a une extension de shapefile
        if os.path.isfile(chemin_fichier) and any(fichier.endswith(ext) for ext in extension):
            # Extraire le nom de fichier sans extension pour le nom de la couche
            nom_couche = os.path.splitext(fichier)[0]
            # Charger la couche vecteur depuis le shapefile
            couche = QgsVectorLayer(chemin_fichier, nom_couche, "ogr")
            geom = couche.wkbType()
            if geom == QgsWkbTypes.MultiPolygon:
                if nom_couche.startswith("CF_Polyg_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche, "CF_Polyg_"))
                elif nom_couche.startswith("DTV_Polyg_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche, "DTV_Polyg_"))
                else:
                    resultat_analyse.append("Non conforme")
                    print("Le préfixe du fichier {} n'est pas conforme.".format(nom_couche))
    
    print(" ")
    print("-" * 148)
    print("-------------- V6: VERIFICATION DES PREFIXES DES FICHIERS DE TYPE POINT --------------")
    for fichier in os.listdir(output_folder):
        chemin_fichier = os.path.join(output_folder, fichier)
        # Vérifier si le fichier a une extension de shapefile
        if os.path.isfile(chemin_fichier) and any(fichier.endswith(ext) for ext in extension):
            # Extraire le nom de fichier sans extension pour le nom de la couche
            nom_couche = os.path.splitext(fichier)[0]
            # Charger la couche vecteur depuis le shapefile
            couche = QgsVectorLayer(chemin_fichier, nom_couche, "ogr")
            geom = couche.wkbType()
            if geom == QgsWkbTypes.Point:
                if nom_couche.startswith("CF_Points_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche, "CF_Points_"))
                elif nom_couche.startswith("DTV_Points_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche, "DTV_Points_"))
                else:
                    resultat_analyse.append("Non conforme")
                    print("Le préfixe du fichier {} n'est pas conforme.".format(nom_couche))
                    
    print(" ")
    print("-" * 148)
    print("-------------- V7: VERIFICATION DES NOMS DES FICHIERS  --------------")
    noms_de_bas = {}
    for fichier in os.listdir(output_folder):
        chemin_fichier = os.path.join(output_folder, fichier)
        # Extraire le nom de fichier sans extension pour le nom de la couche
        if fichier.endswith('.shp') or fichier.endswith('.dbf') or fichier.endswith('.prj') or fichier.endswith('.shx') or fichier.endswith('.cpg'):
            # Charger la couche vecteur depuis le shapefile
            couche = QgsVectorLayer(chemin_fichier, nom_couche, "ogr")
            polygon = couche.wkbType()
            # Vérifiez si la couche est valide et qu'elle est composée de polygones
            if polygon == QgsWkbTypes.MultiPolygon:
                # Séparez le nom du fichier et son extension
                nom_base, extension = os.path.splitext(fichier)
                # Ajout du nom de base au dictionnaire
                noms_de_bas[nom_base] = noms_de_bas.get(nom_base, 0) + 1
    # Vérification si tous les fichiers ont le même nom de base
    if len(noms_de_bas) == 1:
        print("Tous les fichiers de type polygone préfixé par 'CF_Polyg_' ont le même nom.")
    else:
        resultat_analyse.append("Non conforme")
        print("Tous les fichiers de type polygone préfixé par 'CF_Polyg_' n'ont pas le même nom.")
    
    
    noms_de_base = {}
    for fichier in os.listdir(output_folder):
        chemin_fichier = os.path.join(output_folder, fichier)
        # Extraire le nom de fichier sans extension pour le nom de la couche
        if fichier.endswith('.shp') or fichier.endswith('.dbf') or fichier.endswith('.prj') or fichier.endswith('.shx') or fichier.endswith('.cpg'):
            # Charger la couche vecteur depuis le shapefile
            couche = QgsVectorLayer(chemin_fichier, nom_couche, "ogr")
            point = couche.wkbType()
            # Vérifiez si la couche est valide et qu'elle est composée de polygones
            if point == QgsWkbTypes.Point:
                # Séparez le nom du fichier et son extension
                nom_base, extension = os.path.splitext(fichier)
                # Ajout du nom de base au dictionnaire
                noms_de_base[nom_base] = noms_de_base.get(nom_base, 0) + 1
    # Vérification si tous les fichiers ont le même nom de base
    if len(noms_de_base) == 1:
        print("Tous les fichiers de type point préfixé par 'CF_Point_' ont le même nom.")
    else:
        resultat_analyse.append("Non conforme")
        print("Tous les fichiers de type point préfixé par 'CF_Point_' n'ont pas le même nom.")
    
    print(" ")
    print("-" * 148)
    print("-------------- V8: VERIFICATION DU SYSTEME DE COORDONNEES DES FICHIERS DE TYPE POLYGONE ET DE TYPE POINT --------------")
    crs = couche.crs().authid()
    for fichier in os.listdir(output_folder):
        chemin_fichier = os.path.join(output_folder, fichier)
        # Vérifier si le fichier a une extension de shapefile
        if os.path.isfile(chemin_fichier) and any(fichier.endswith(ext) for ext in extension):
            # Extraire le nom de fichier sans extension pour le nom de la couche
            nom_couche = os.path.splitext(fichier)[0]
            # Charger la couche vecteur depuis le shapefile
            couche = QgsVectorLayer(chemin_fichier, nom_couche, "ogr")
            polygon = couche.wkbType()
            point = couche.wkbType()
            # Vérifiez si les crs  de polygone et de point sont identique
            if point == QgsWkbTypes.Point:
                point_crs = couche.crs().authid()
                print("Le système de coordonnées du fichier '{}' est : {}".format(nom_couche, point_crs))
            elif polygon == QgsWkbTypes.MultiPolygon:
                poly_crs = couche.crs().authid()
                print("Le système de coordonnées du fichier '{}' est : {}".format(nom_couche, poly_crs))
                if poly_crs == point_crs:
                    print('Vu ce qui précède on en déduit que le système de coordonnées du fichier point est identique à celui du polygone dont scr = {}.'.format(poly_crs))
                else:
                    resultat_analyse.append("Non conforme")
                    print('Vu ce qui précède on en déduit que le système de coordonnées du fichier de type point n\'est pas identique à celui du polygone.')

    print(" ")
    print("-" * 148)
    print("-------------- V9: VERIFICATION DU FORMAT DES COLONNES DU POLYGONE --------------")
    colonnes_requises = [
        'FID', 'NUM_DOSS', 'NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF',
        'NOM_VILLAG', 'NOM_DEMAND', 'SUPERF', 'PERIM', 'NOM_PROJET', 'NOM_OTA'
    ]
    for polygon_file in os.listdir(output_folder):
        polygon_path = os.path.join(output_folder, polygon_file)
        # Vérifier si le fichier est une couche vecteur
        if polygon_file.lower().endswith('.shp'):
            # Essayer d'ouvrir la couche vecteur
            layer_polygon = QgsVectorLayer(polygon_path, polygon_file, "ogr")
            #polygon = couche.wkbType()
            if layer_polygon.geometryType() == QgsWkbTypes.PolygonGeometry:
                attribute_fields = [field.name() for field in layer_polygon.fields()]
                print("Voici les noms des colonnes du fichier de type polygone: {} ".format(attribute_fields))
                # Comparez les champs requis avec les champs de la couche
                missing_fields = list(set(colonnes_requises) - set(attribute_fields))
                extra_fields = list(set(attribute_fields) - set(colonnes_requises))
                if missing_fields:
                    print(f"Il manque ce champ '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{polygon_file}' donc cette table n'est pas conforme.")
                elif extra_fields:
                    print(" Ce Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' donc la table n'est pas conforme.".format(extra_fields[0], polygon_file))
                else:
                    resultat_analyse.append("Non conforme")
                    print("Ce format des champs de la table attributaire de la couche '{}' est conforme.".format(polygon_file))
                
    
            
    print(" ")
    print("-" * 148)
    print("-------------- V10: VERIFICATION DU FORMAT DES COLONNES DU POINT --------------")
    champs_requis = ['FID', 'NUM_DOSS', 'NOM_REGION', 'NOM_DEPART', 
        'NOM_SSPREF', 'NOM_VILLAG', 'NUM_SOMMET', 'COORD_X', 'COORD_Y', 
        'TYP_LEVE', 'TYP_SOMMET', 'SOMM_SUIV', 'DIST_SUIV', 'NOM_PROJET', 'NOM_OTA']
    for point_file in os.listdir(output_folder):
        point_path = os.path.join(output_folder, point_file)
        # Vérifier si le fichier est une couche vecteur
        if point_file.lower().endswith('.shp'):
            # Essayer d'ouvrir la couche vecteur
            layer_point = QgsVectorLayer(point_path, point_file, "ogr")
            point = couche.wkbType()
            if layer_point.geometryType() == QgsWkbTypes.PointGeometry:
                attribute_fields = [field.name() for field in layer_point.fields()]
                print("Voici les noms des colonnes du fichier de type point: {} ".format(attribute_fields))
                # Comparez les champs requis avec les champs de la couche
                missing_fields = list(set(champs_requis) - set(attribute_fields))
                extra_fields = list(set(attribute_fields) - set(champs_requis))
                print()
                if missing_fields:
                    print(f"Il manque ce champ '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{point_file}' donc cette table n'est pas conforme.")
                elif extra_fields:
                    print(" Ce Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' donc la table n'est pas conforme.".format(extra_fields[0], point_file))
                else:
                    resultat_analyse.append("Non conforme")
                    print("Ce format des champs de la table attributaire de la couche '{}' est conforme.".format(point_file))
                
    
    print(" ")
    print("-" * 148)
    print("-------------- V11: VERIFICATION DES CHAMPS OBLIGATOIRES DES COLONNES  DU POLYGONE --------------")
    extensions_supportees = ['.shp','.SHP']
    fichiers = os.listdir(output_folder)
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(output_folder, fichier)
            nom_couche = os.path.splitext(fichier)[0]
            polygon_couche = QgsVectorLayer(chemin_fichier, nom_couche, 'ogr')
            # Vérifier le type de géométrie de la couche
            polygon = polygon_couche.wkbType()
            if polygon == QgsWkbTypes.MultiPolygon:
                # Boucler à travers les entités de la couche
                for colonne  in polygon_couche.fields().names():
                    # verifier les valeurs des champs
                    for entite in polygon_couche.getFeatures():
                        if str(entite[colonne]) == "NULL" or str(entite[colonne]) is None:
                            print(f"Le champ '{colonne}' contient une valeur nulle à la ligne {entite.id() +1}.")
                        else:
                            resultat_analyse.append("Non conforme")
                            print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
                
    print(" ")
    print("-" * 148)
    print("-------------- V12: VERIFICATION DES CHAMPS OBLIGATOIRES DES COLONNES  DU POINT --------------")
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(output_folder, fichier)
            nom_couche_point = os.path.splitext(fichier)[0]
            point_couche = QgsVectorLayer(chemin_fichier, nom_couche_point, 'ogr')
            # Vérifier le type de géométrie de la couche
            if point_couche.isValid() and point_couche.geometryType() == QgsWkbTypes.PointGeometry:
                # Boucler à travers les entités de la couche
                for colonne  in point_couche.fields().names():
                    # verifier les valeurs des champs
                    champs_nuls = []
                    for valeur in point_couche.getFeatures():
                        if str(valeur[colonne]) == "NULL" or valeur[colonne] is None:
                            champs_nuls.append(f"Le champ '{colonne}' contient une valeur nulle à la ligne {valeur.id() + 1}.")
                    if champs_nuls:
                        print("\n".join(champs_nuls))
                    else:
                        resultat_analyse.append("Non conforme")
                        print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
                        
    print(" ")
    print("-" * 148)
    print("-------------- RESULTAT DE L'ANALYSE --------------")
    if "Non conforme" in resultat_analyse:
        print("Les données chargées sont invalides car elles contiennent {} points de contrôle non conforme.\nVeuillez consulter ces points ci dessus.".format(len(resultat_analyse)))
    else:
        print("Les données chargées sont valides.")