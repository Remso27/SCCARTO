from qgis.core import *
from qgis.gui import *
from osgeo import ogr
from zipfile import ZipFile
import os
import re
from qgis.PyQt.QtCore import QVariant
import math
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


@qgsfunction(args='auto', group='Custom')
def display_hors_pamofor(dossier, feature, parent):
    resultat_analyse = []
    print("-" * 114)
    print("---------- Le shapefile doit être fourni au format compressé (.zip) ----------")
    if ZipFile(dossier, "r"):
        print("Le shapefile est fourni au format .zip.")
    else :
        print("==>000 Le shapefile n'est pas fourni au format .zip")
   
    print("")
    print("-" * 114)
    fichier = os.path.basename(dossier)
    chemin_complet = os.path.join(dossier)
    pattern_cf = r'^CF-\d{2}-\d{4}-\d{6}-HP\.zip$'
    pattern_tv = r'^TV-\d{2}-\d{3}-\d{3}-\d{4}-HP\.zip$'
    if re.match(pattern_cf, fichier):
        print("---------- Vérifier le nom du Fichier SIG : CF-DD-AAAA-NNNNNN-HP.zip ----------")
        print("Le nom du fichier zip respecte la spécification.")
    elif re.match(pattern_tv, fichier):
        print("---------- Vérifier le nom du Fichier SIG : TV-RR-DDD-SSS-VVVV-HP.zip ----------")
        print("Le nom du fichier zip respecte la spécification.")
    else:
        resultat_analyse.append("Non conforme")
        print("---------- Vérifier le nom du Fichier SIG ----------")
        print("==>000 Le nom du fichier zip ne respecte pas la spécification.")
    
    print("")
    print("-" * 114)
    print("---------- Le zip doit contenir les 4 fichiers suivants pour le point et la polygone : .shp, .prj, .dbf, .shx ----------")
    contenu_zip = set()
    # Charger le fichier ZIP
    zip_path = str(dossier)
    # Vérifier si le chemin du fichier ZIP existe
    if os.path.exists(zip_path):
        # Ouvrir le fichier ZIP en mode lecture
        with ZipFile(zip_path, 'r') as zip_ref:
            # Obtenir la liste des fichiers dans le ZIP
            file_list = zip_ref.namelist()
        # Créer une chaîne de texte avec la liste des fichiers
        #content_text = "\n".join(file_list)

        # Afficher le contenu dans la console
        #print(content_text)
        for fichier in file_list:
            #print(fichier)
            if fichier.endswith(".shp") or fichier.endswith(".SHP"):
                contenu_zip.add(fichier)
            elif fichier.endswith(".prj") or fichier.endswith(".PRJ"):
                contenu_zip.add(fichier)
            elif fichier.endswith(".dbf") or fichier.endswith(".DBF"):
                contenu_zip.add(fichier)
            elif fichier.endswith(".shx") or fichier.endswith(".SHX"):
                contenu_zip.add(fichier)
        if len(contenu_zip) % 2 == 0:
            print("Le zip contient les 4 fichiers requis : .shp, .prj, .dbf, .shx")
        else:
            resultat_analyse.append("Non conforme")
            print("==>000 Le zip ne contient pas les 4 fichiers requis : .shp, .prj, .dbf, .shx")
    else:
        QgsMessageLog.logMessage("Le fichier ZIP spécifié n'existe pas.", "MonPlugin", QgsMessageLog.CRITICAL)
   
  
  # Vérification de la géometrie des couches
    print("")
    print("-" * 114)
    geom_layer = set()
    zip_file_name = os.path.splitext(dossier)[0]
    # Créez un dossier pour sauvegarder le contenu du ZIP s'il n'existe pas déjà
    output_folder = os.path.join(os.path.dirname(dossier), zip_file_name)
    # output_folder est le dossier de sauvegarde du contenu du ZIP
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with ZipFile(dossier, 'r') as zipfile:
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
            if couche.geometryType() == QgsWkbTypes.PointGeometry or couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                geom_layer.add("PointPolyg")
            else:
                geom_layer.add("NoPointPolyg")
    
    if ("PointPolyg" in geom_layer) and ("NoPointPolyg" not in geom_layer):
        print("---------- Le fichier .zip doit contenir : Un fichier Shape de type Polygone et Point. ----------")
        print("Le zip contient un shape de type Polygone et Point.")
    else :
        resultat_analyse.append("Non conforme")
        print("---------- Le fichier .zip doit contenir : Un fichier Shape de type Polygone et Point. ----------")
        print("==>000 Le zip ne contient pas un shape de type Polygone et Point.")
    
    print("")
    print("-" * 132)
    print("-------------- Les systèmes de coordonnées autorisés sont EPSG:32629 et EPSG:32630 --------------")
    crs_layer = set()
    zip_file_name = os.path.splitext(dossier)[0]
    # Créez un dossier pour sauvegarder le contenu du ZIP s'il n'existe pas déjà
    output_folder = os.path.join(os.path.dirname(dossier), zip_file_name)
    # output_folder est le dossier de sauvegarde du contenu du ZIP
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with ZipFile(dossier, 'r') as zipfile:
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
            crs = couche.crs().authid()
            # Vérifier le type de géométrie de la couche
            if couche.geometryType() == QgsWkbTypes.PointGeometry:
                if crs == "EPSG:32629" or crs == "EPSG:32629":
                    crs_layer.add(crs)
            elif couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                crs_layer.add(crs)
    if 'EPSG:32629' in crs_layer or 'EPSG:32630' in crs_layer:
        print("Le système de coordonnées correspond à ceux autorisés  EPSG:32629 et EPSG:32630.")
    else:
        resultat_analyse.append("Non conforme")
        print("==>000 Le système de coordonnées ne correspond pas à ceux autorisés  EPSG:32629 et EPSG:32630.")        
    
    # Vérification du préfixe
    zip_file_name = os.path.splitext(dossier)[0]
    # Créez un dossier pour sauvegarder le contenu du ZIP s'il n'existe pas déjà
    output_folder = os.path.join(os.path.dirname(dossier), zip_file_name)
    # output_folder est le dossier de sauvegarde du contenu du ZIP
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with ZipFile(dossier, 'r') as zipfile:
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
            crs = couche.crs().authid()
            # Vérifier le type de géométrie de la couche
            if couche.geometryType() == QgsWkbTypes.PointGeometry:
                if nom_couche.startswith("CF_Points_"):
                    print("")
                    print("-" * 114)
                    print("-------------- Vérifier que le nom des fichiers du Shape du point doit être préfixé par <CF_Points_>. --------------")
                    print("Le nom des fichiers du Shape du point est bien préfixé")
                elif  nom_couche.startswith("DTV_Points_"):
                    print("")
                    print("-" * 114)
                    print("-------------- Vérifier que le nom des fichiers du Shape du point doit être préfixé par <DTV_Points_>. --------------")
                    print("Le nom des fichiers du Shape du point est bien préfixé")
                else:
                    print("")
                    print("-" * 114)
                    resultat_analyse.append("Non conforme")
                    print("-------------- Vérifier le préfixe du nom des fichiers du Shape du point. --------------")
                    print("==>000 Le nom des fichiers du Shape du point n'est pas bien préfixé.")
            
            elif couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                if nom_couche.startswith("CF_Polyg_"):
                    print("")
                    print("-" * 114)
                    print("-------------- Vérifier que le nom des fichiers du Shape de la polygone doit être préfixé par <CF_Polyg_>. --------------")
                    print("Le nom des fichiers du Shape de la polygone est bien préfixé.")
                elif nom_couche.startswith("DTV_Polyg_"):
                    print("")
                    print("-" * 114)
                    print("-------------- Vérifier que le nom des fichiers du Shape de la polygone doit être préfixé par <DTV_Polyg_>. --------------")
                    print("Le nom des fichiers du Shape de la polygone est bien préfixé")
                    
                else:
                    print("")
                    print("-" * 114)
                    resultat_analyse.append("Non conforme")
                    print("-------------- Vérifier le préfixe du nom des fichiers. --------------")
                    print("==>000 Le nom des fichiers n'est pas bien préfixé")
                    
            else:
                print("")
                print("-" * 114)
                resultat_analyse.append("Non conforme")
                print("-------------- Vérifier le préfixe du nom des fichiers. --------------")
                print("==>000 Le nom des fichiers n'est pas bien préfixé.")
                
                
    # Vérification du nom des shapes
    prefix = set()
    zip_file_name = os.path.splitext(dossier)[0]
    # Créez un dossier pour sauvegarder le contenu du ZIP s'il n'existe pas déjà
    output_folder = os.path.join(os.path.dirname(dossier), zip_file_name)
    # output_folder est le dossier de sauvegarde du contenu du ZIP
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with ZipFile(dossier, 'r') as zipfile:
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
            crs = couche.crs().authid()
            # Vérifier le type de géométrie de la couche
            if couche.geometryType() == QgsWkbTypes.PointGeometry:
                if nom_couche.startswith("CF_Points_"):
                        prefix.add("CF_Points_")
                elif  nom_couche.startswith("DTV_Points_"):
                    prefix.add("DTV_Points_")
            elif couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                if nom_couche.startswith("DTV_Polyg_"):
                    prefix.add("DTV_Polyg_")
                elif nom_couche.startswith("CF_Polyg_"):
                    prefix.add("CF_Polyg_")
    nom = set()                
    if os.path.exists(output_folder):
        fichiers = os.listdir(output_folder)
        for fichier in fichiers:
            if prefix:
               if ("CF_Points_" and "CF_Polyg_") in prefix and (fichier.startswith("CF_Points_") or  fichier.startswith("CF_Polyg_")):
                  print("")
                  print("-" * 114)
                  print("-------------- Vérifier que tous les fichiers ont le même nom --------------")
                  print("Tous les fichiers ont le même nom.")
                  break
               elif ("DTV_Points_" and "DTV_Polyg_") in prefix and (fichier.startswith("DTV_Points_") or  fichier.startswith("DTV_Polyg_")):
                  print("")
                  print("-" * 114)
                  print("-------------- Vérifier que tous les fichiers ont le même nom --------------")
                  print("Tous les fichiers ont le même nom.")
                  break
                  
            else:
                print("")
                print("-" * 114)
                resultat_analyse.append("Non conforme")
                print("-------------- Vérifier le nom des fichiers --------------")
                print("==>000 Le nom des fichiers ne respecte pas la spécification.")
    
    # Comparaison des crs des couches
    print("")
    print("-" * 114)
    print("-------------- Le système de coordonnées du fichier de point doit être identique à celui du polygone --------------")
    point_syst = set()
    polyg_syst = set()
    zip_file_name = os.path.splitext(dossier)[0]
    # Créez un dossier pour sauvegarder le contenu du ZIP s'il n'existe pas déjà
    output_folder = os.path.join(os.path.dirname(dossier), zip_file_name)
    # output_folder est le dossier de sauvegarde du contenu du ZIP
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with ZipFile(dossier, 'r') as zipfile:
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
            #crs = couche.crs().authid()
            # Vérifier le type de géométrie de la couche
            if couche.geometryType() == QgsWkbTypes.PointGeometry:
                point_crs  = couche.crs().authid()
                point_syst.add(point_crs)
            elif couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                polyg_crs  = couche.crs().authid()
                polyg_syst.add(polyg_crs)
    if  point_syst == polyg_syst:
        print("Le système de coordonnées du fichier de point est identique à celui du polygone.")
    else:
        resultat_analyse.append("Non conforme")
        print("==>000 Le système de coordonnées du fichier de point n'est pas identique à celui du polygone.")
        
        
    print(" ")
    print("-" * 114)
    print("-------------- Vérifier que le format des colonnes du polygone est respecté --------------")
    extensions_supportees = [".shp", ".SHP"]
    colonnes_requises = [
        'NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF','NOM_VILLAG', 'NOM_DEMAND', 'NOM_OTA', 'SUPERF']
    colonnes_requises_hp = ['NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF','NOM_VILLAG', 'NOM_PROJET', 'NOM_OTA', 'SUPERF']
    for fichier in os.listdir(output_folder):
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(output_folder, fichier)
            nom_couche = os.path.splitext(fichier)[0]
            layer_polygon = QgsVectorLayer(chemin_fichier, nom_couche, 'ogr')
            # Vérifier le type de géométrie de la couche
            polygon = layer_polygon.wkbType()
            if polygon == QgsWkbTypes.MultiPolygon:
                # CF
                if nom_couche.startswith("CF_Polyg_"):
                    forma_cf = []
                    taille_cf = []
                    attribute_fields = [field.name() for field in layer_polygon.fields()]
                    #print("Voici les noms des colonnes du fichier de type polygone: {} ".format(attribute_fields))
                    # Comparez les champs requis avec les champs de la couche
                    missing_fields = list(set(colonnes_requises) - set(attribute_fields))
                    extra_fields = list(set(attribute_fields) - set(colonnes_requises))
                    if missing_fields:
                        forma_cf.append("No")
                        resultat_analyse.append("Non conforme")
                        print(f"==>000 Il manque ce champ '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}' donc cette table n'est pas conforme.")
                    #elif extra_fields:
                    #    forma_cf.append("No")
                    #    resultat_analyse.append("Non conforme")
                    #    print("==>000 Le Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' n'est pas conforme.".format(extra_fields[0], nom_couche))
                    else:
                        forma_cf.append("Ok")
                        #print("Ce format des champs de la table attributaire de la couche '{}' est conforme.".format(nom_couche))
                    # vérification de la taille des champs
                    for colonne  in layer_polygon.fields().names():
                            champ = layer_polygon.fields().field(colonne)
                            #print(colonne)
                            # Vérifier si le champ est de type String
                            if champ.type() == QVariant.String:
                                if colonne == "NOM_DEMAND":
                                    if not champ.length() <= 100:
                                        taille_cf.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (100).".format(colonne, champ.length()))
                                    else:
                                        taille_cf.append("Ok")
                                elif champ.length() != 50:
                                    taille_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_cf.append("Ok")
                                    #print("Colonne '{}': Longueur = {}".format(colonne,  champ.length()))
                            elif champ.type() == QVariant.Double:
                                precision = champ.precision()
                                if not champ.length() <= 20 and precision != 4:
                                    taille_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {} avec une précision de {}, elle ne respecte pas la taille (20) et la précision (2) attendues.".format(colonne, champ.length(), precision))
                                else:
                                    taille_cf.append("Ok")
                                    #print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                    #print(forma_cf)
                    #print(taille_cf)
                    if "No" in forma_cf and "No" in taille_cf:
                        print("Le format des colonnes du polygone n'est pas respecté.")
                    elif "No" in forma_cf and "Ok" in taille_cf:
                        print("Le format des colonnes du polygone n'est pas respecté.")
                    elif "Ok" in forma_cf and "No" in taille_cf:
                        print("Le format des colonnes du polygone n'est pas respecté.")
                    else:
                        print("Le format des colonnes du polygone est respecté.")
                    
                # DTV
                elif nom_couche.startswith("DTV_Polyg_"):
                    forma_dtv = []
                    taille_dtv = []
                    attribute_fields = [field.name() for field in layer_polygon.fields()]
                    #print("Voici les noms des colonnes du fichier de type polygone: {} ".format(attribute_fields))
                    # Comparez les champs requis avec les champs de la couche
                    missing_fields = list(set(colonnes_requises_hp) - set(attribute_fields))
                    extra_fields = list(set(attribute_fields) - set(colonnes_requises_hp))
                    if missing_fields:
                        resultat_analyse.append("Non conforme")
                        forma_dtv.append("No")
                        print(f"==>000 Il manque ce champ '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}'.")
                    #elif extra_fields:
                    #    forma_dtv.append("No")
                    #    resultat_analyse.append("Non conforme")
                    #    print("==>000 Le Champ '{}' est inattendu au niveau de la table attributaire de la couche '{}'.".format(extra_fields[0], nom_couche))
                    else:
                        forma_dtv.append("Ok")
                        #print("Ce format des champs de la table attributaire de la couche '{}' est conforme.".format(nom_couche))
                
                    # vérification de la taille des champs
                    for colonne  in layer_polygon.fields().names():
                            champ = layer_polygon.fields().field(colonne)
                            # Vérifier si le champ est de type String
                            if champ.type() == QVariant.String:
                                if champ.length() != 50:
                                    taille_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_dtv.append("Ok")
                                    #print("Colonne '{}': Longueur = {}".format(colonne,  champ.length()))
                            elif champ.type() == QVariant.Double:
                                precision = champ.precision()
                                if not champ.length() <= 20 and precision != 4:
                                    taille_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {} avec une précision de {}, elle ne respecte pas la taille (20) et la précision (2) attendues.".format(colonne, champ.length(), precision))
                                else:
                                    taille_dtv.append("Ok")
                                    #print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                    #print(forma_dtv)
                    #print(taille_dtv)
                    if "No" in forma_dtv and "No" in taille_dtv:
                        print("Le format des colonnes du polygone n'est pas respecté.")
                    elif "No" in forma_dtv and "Ok" in taille_dtv:
                        print("Le format des colonnes du polygone n'est pas respecté.")
                    elif "Ok" in forma_dtv and "No" in taille_dtv:
                        print("Le format des colonnes du polygone n'est pas respecté.")
                    else:
                        print("Le format des colonnes du polygone est respecté.") 
                else:
                    print("Le format des colonnes du polygone n'est pas respecté.")     
               
    
    print(" ")
    print("-" * 114)
    print("-------------- Vérifier que le format des colonnes du point est respecté --------------")
    champs_requis = ['COORD_X', 'COORD_Y', 'NUM_SOMMET']
    forma = []
    taille = []
    for fichier in os.listdir(output_folder):
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(output_folder, fichier)
            nom_couche = os.path.splitext(fichier)[0]
            layer_point = QgsVectorLayer(chemin_fichier, nom_couche, 'ogr')
            # Vérifier le type de géométrie de la couche
            #point = layer_point.wkbType()
            if layer_point.geometryType() == QgsWkbTypes.PointGeometry:
                attribute_champ = [field.name() for field in layer_point.fields()]
                #print("Voici les noms des colonnes du fichier de type point: {} ".format(attribute_champ))
                # Comparez les champs requis avec les champs de la couche
                champs_manquant = list(set(champs_requis) - set(attribute_champ))
                extra_champ = list(set(attribute_champ) - set(champs_requis))
                if champs_manquant:
                    resultat_analyse.append("Non conforme")
                    forma.append("No")
                    print(f"==>000 Il manque ce champ '{', '.join(champs_manquant)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}.")
                #elif extra_champ:
                #    resultat_analyse.append("Non conforme")
                #    forma.append("No")
                #    print("==>000 Le Champ '{}' est inattendu au niveau de la table attributaire de la couche '{}'.".format(extra_champ[0], nom_couche))
                elif not champs_manquant:
                    forma.append("Ok")
                    #print("Ce format des champs de la table attributaire de la couche '{}' est conforme.".format(nom_couche))
                # vérification de la taille des champs
                for colonne  in layer_point.fields().names():
                            champ = layer_point.fields().field(colonne)
                            # Vérifier si le champ est de type String
                            if champ.type() == QVariant.String:
                                if champ.length() != 10:
                                    #taille_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    taille.append("No")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (10).".format(colonne, champ.length()))
                                else:
                                    taille.append("Ok")
                                    #print("Colonne '{}': Longueur = {}".format(colonne,  champ.length()))
                            elif champ.type() == QVariant.Double:
                                precision = champ.precision()
                                if not champ.length() <= 20 and not precision <= 10:
                                    taille.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {} avec une précision de {}, elle ne respecte pas la taille (20) et la précision (10) attendues.".format(colonne, champ.length(), precision))
                                else:
                                    taille.append("Ok")
                                #    print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                #print(forma)
                #print(taille)
                if "No" in forma and "No" in taille:
                    print(" Le format des colonnes du point n'est pas respecté.")
                elif "No" in forma and "Ok" in taille:
                    print(" Le format des colonnes du point n'est pas respecté.")
                elif "Ok" in forma and "No" in taille:
                    print(" Le format des colonnes du point n'est pas respecté.")
                else:
                    print("Le format des colonnes du point est respecté.")
               
    
    print(" ")
    print("-" * 114)
    print("-------------- Vérifier que tous les champs obligatoires du polygone sont remplis par des valeurs --------------")
    value_null = set()
    for fichier in os.listdir(output_folder):
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
                            resultat_analyse.append("Non conforme")
                            value_null.add("No")
                            print(f"==>000 Le champ '{colonne}' contient une valeur nulle à la ligne {entite.id() +1}.")
                        elif colonne == "SUPERF":
                            if str(entite[colonne]) == "NULL" or str(entite[colonne]) is None:
                              value_null.add("Ok")  
                        else:
                            value_null.add("Ok")
                            #print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
    if "No" in  value_null and "Ok" in value_null:
        print("Tous les champs obligatoires du polygone ne sont pas remplis par des valeurs.")
    elif "No" in  value_null:
        print("Tous les champs obligatoires du polygone ne sont pas remplis par des valeurs.")
    else:
        print("Tous les champs obligatoires du polygone sont remplis par des valeurs.")
                    
                    
    
    print(" ")
    print("-" * 114)
    print("-------------- Vérifier que tous les champs obligatoires du point sont remplis par des valeurs --------------")
    # Créez un dictionnaire pour stocker les champs et les lignes avec des valeurs nulles
    champs_nuls = set()
    for fichier in os.listdir(output_folder):
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(output_folder, fichier)
            nom_couche_point = os.path.splitext(fichier)[0]
            point_couche = QgsVectorLayer(chemin_fichier, nom_couche_point, 'ogr')
            # Vérifier le type de géométrie de la couche
            if point_couche.isValid() and point_couche.geometryType() == QgsWkbTypes.PointGeometry:
                # Boucler à travers les entités de la couche
                for colonne  in point_couche.fields().names():
                    # verifier les valeurs des champs
                    for valeur in point_couche.getFeatures():
                        if str(valeur[colonne]) == "NULL" or valeur[colonne] is None:
                            resultat_analyse.append("Non conforme")
                            champs_nuls.add("No")
                            print(f"==>000 Le champ '{colonne}' contient une valeur nulle à la ligne {valeur.id() + 1}.")
                        else:
                            champs_nuls.add("Ok")
                            #print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
                    
    if "No" in  champs_nuls and "Ok" in champs_nuls:
        print("Tous les champs obligatoires du point ne sont pas remplis par des valeurs.")
    elif "No" in  champs_nuls:
        print("Tous les champs obligatoires du point ne sont pas remplis par des valeurs.")
    else:
        print("Tous les champs obligatoires du point sont remplis par des valeurs.")                
                                
    print(" ")
    print("-" * 114)
    print("-------------- Le nombre de points doit être identique au nombre de sommets des parcelles --------------")
    nombre_points = 0
    nombre_sommets = 0
    zip_file_name = os.path.splitext(dossier)[0]
    # Créez un dossier pour sauvegarder le contenu du ZIP s'il n'existe pas déjà
    output_folder = os.path.join(os.path.dirname(dossier), zip_file_name)
    # output_folder est le dossier de sauvegarde du contenu du ZIP
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with ZipFile(dossier, 'r') as zipfile:
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
            # Calculer le nombre de point de la couche point
            if couche.geometryType() == QgsWkbTypes.PointGeometry:
                nbre_point = couche.featureCount()
                nombre_points += nbre_point
            # Calculer le nombre de point de la couche polygone
            elif couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                for entite in couche.getFeatures():
                    geom = entite.geometry()
                    if geom.type() == QgsWkbTypes.PolygonGeometry:
                         polygone = geom.asMultiPolygon()[0]
                         for point in polygone:
                             nombre_sommets += len(point)
    #print(nombre_points)
    #print(nombre_sommets)
    if nombre_points == nombre_sommets:
        print("Le nombre de points est identique au nombre de sommets des parcelles.")
    else:
        resultat_analyse.append("Non conforme")
        print("==>000 Le nombre de points n'est pas identique au nombre de sommets des parcelles")
              
    
    print(" ")
    print("-" * 114)
    print("-------------- Les coordonnées des points doivent obligatoirement épouser (tolérance 0) les sommets des polygones parcelle --------------")
    TOLERANCE = 0.0
    coord_points = []
    resultat_distance = []
    zip_file_name = os.path.splitext(dossier)[0]
    # Créez un dossier pour sauvegarder le contenu du ZIP s'il n'existe pas déjà
    output_folder = os.path.join(os.path.dirname(dossier), zip_file_name)
    # output_folder est le dossier de sauvegarde du contenu du ZIP
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with ZipFile(dossier, 'r') as zipfile:
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
            geom_layer = couche.wkbType()
            # Calculer le nombre de point de la couche point
            if couche.geometryType() == QgsWkbTypes.PointGeometry:
                # Récupérer les coordonnées du premier point de la première entité
                for entite in couche.getFeatures():
                    point_geometry = entite.geometry()
                    point_coords = point_geometry.asPoint()
                    x_p, y_p = round(point_coords.x(), 2), round(point_coords.y(), 2)
                    coord_point = Point(x_p, y_p)
                    coord_points.append(coord_point)
                    #print(f"Point: {point}")
                    #print("Coordonnées du point {} : {}, {}".format(numero_pt, round(x_p, 2), round(y_p, 2)))
                    
                    #points.append(point_coords)
            # Calculer le nombre de point de la couche polygone
            elif couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                # Récupérer les sommets du premier polygone de la première entité
                for entite in couche.getFeatures():
                    poly_geom = entite.geometry()
                    for polygon in poly_geom.asMultiPolygon():
                        for sommet in polygon:
                            for point in sommet:
                                x_s, y_s = round(point.x(), 2), round(point.y(), 2)
                                sommet_p = Point(x_s, y_s)
                                #print(f" Les points: {coord_points}")
                                #break
                                # Calculer la distance pour chaque point par rapport aux sommets des polygones
                                for coord in coord_points:
                                    if coord.equals(sommet_p):
                                        # Calculer la distance entre le point et le sommet
                                        distance = math.sqrt((coord.x - x_s)**2 + (coord.y - y_s)**2)
                                        resultat_distance.append(distance)
                                        if distance != 0:
                                            resultat_distance.append(distance)
                                        #print(distance)
                                        #print(f"Distance entre le point {coord_point} et le sommet ({x_s}, {y_s}): {distance}")
    # Vérification de la tolérance
    verification = set()
    for resultat in resultat_distance:
        if resultat == TOLERANCE:
            verification.add("Ok")
        else:
            verification.add("No")
    if "Ok" in verification and "No" not in verification:
        print("Les coordonnées des points épousent les sommets des polygones parcelle")
    else:
        resultat_analyse.append("Non conforme")
        print("==>000 Les coordonnées des points n'épousent pas les sommets des polygones parcelle")
    
    
    print(" ")
    print("-" * 114)
    print("-------------- Les sommets sont en doublon dans la couche des polygones --------------")
    sommets = []
    zip_file_name = os.path.splitext(dossier)[0]
    # Créez un dossier pour sauvegarder le contenu du ZIP s'il n'existe pas déjà
    output_folder = os.path.join(os.path.dirname(dossier), zip_file_name)
    # output_folder est le dossier de sauvegarde du contenu du ZIP
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with ZipFile(dossier, 'r') as zipfile:
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
            # identifier les sommets doubles de la couche polygone
            if couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                # Récupérer les sommets du premier polygone de la première entité
                for entite in couche.getFeatures():
                    poly_geom = entite.geometry()
                    for sommet in poly_geom.asMultiPolygon():
                        for point in sommet:
                            for coord in point:
                                x_s, y_s = round(coord.x(), 2), round(coord.y(), 2)
                                sommet_p = Point(x_s, y_s)
                                sommets.append(sommet_p)
    # Initialiser un ensemble pour stocker les coordonnées uniques
    coordonnees_uniques = []
    # Initialiser une liste pour stocker les coordonnées en double
    coordonnees_en_double = []
    # Parcourir la liste des sommets
    for sommet in sommets:
        # Convertir l'objet CoordinateSequence en une liste de tuples
        coordonnees = [tuple(coord) for coord in sommet.coords]
        # Vérifier si la coordonnée est déjà présente dans l'ensemble
        if coordonnees  in coordonnees_uniques:
            coordonnees_en_double.append(coordonnees)
        else:
            # Ajouter la coordonnée à l'ensemble si elle n'est pas déjà présente
            coordonnees_uniques.append(coordonnees)
    
    
    # Afficher les coordonnées en double
    if coordonnees_en_double:
        #print("Coordonnées en double :")
        for coord in coordonnees_en_double:
            #print(coord)
            resultat_analyse.append("Non conforme")
            print("==>000 Les sommets sont en doublons dans la couche des polygones.")
            break
    else:
        print("Les sommets  ne sont pas en doublon dans la couche des polygones")
    
    print(" ")
    print("-" * 114)
    print("-------------- Décision finale de l'analyse --------------")
    #print(resultat_analyse)
    if "Non conforme" in resultat_analyse:
        print("Les données chargées sont invalides car elles contiennent {} point(s) de contrôle non conforme.\n\t---> Veuillez consulter ces points de contrôle ci dessus précédés par ==>000".format(len(resultat_analyse)))
    else:
        print("\t----> 'Les données chargées sont valides.' <----")
    
    return None