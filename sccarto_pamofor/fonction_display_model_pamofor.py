from qgis.core import *
from qgis.gui import *
from osgeo import ogr
from zipfile import ZipFile
import os
import re
from qgis.PyQt.QtCore import QVariant

@qgsfunction(args='auto', group='Custom')
# le paramètre layers est le chemin du dossier
def display_pamofor(zip_file, feature, parent):
    resultat_analyse = []
    print("-" * 118)
    print("---------- Le shapefile doit être fourni au format compressé (.zip). ----------")
    
    if ZipFile(zip_file, "r"):
        print("Le shapefile est fourni au format .zip.")
    else :
        resultat_analyse.append("Non conforme")
        print("==>000 Le shapefile n'est pas fourni au format .zip")
    
    print("")
    print("-" * 118)
    fichier = os.path.basename(zip_file)
    chemin_complet = os.path.join(zip_file)
    pattern_prov = r'^CF-\d{6}-\d{5}-06-LPProv\.zip$'
    pattern_prov_TV = r'^TV-\d{6}-06-LPProv\.zip$'
    pattern_def = r'^CF-\d{6}-\d{5}-14-LPDef\.zip$'
    pattern_def_TV = r'^TV-\d{6}-14-LPDef\.zip$'
    
    #Vérifier si le nom de fichier correspond au modèle
    prov_cf = []
    def_cf = []
    prov_tv = []
    def_tv = []
    
    if re.match(pattern_prov, fichier):
        prov_cf.append("ok")
        #print("---------- Vérifier le nom du Fichier SIG provisoire: CF-SSSVVV-NNNN-06-LProv.zip. ----------")
        #print("Le nom du fichier zip respecte la spécification.")
        #print("Le nom du fichier '{}' est conforme.".format(fichier))
    elif re.match(pattern_def, fichier):
        def_cf.append("ok")
        #print("---------- Vérifier le nom du Fichier SIG définitif : CF-SSSVVV-NNNN-15-LDef.zip ----------")
        #print("Le nom du fichier zip respecte la spécification.")
        #print("Le nom du fichier '{}' est conforme.".format(fichier))
    elif re.match(pattern_prov_TV, fichier):
        prov_tv.append("ok")
        #print("---------- Vérifier le nom du Fichier SIG provisoire : TV-SSSVVV-06-LProv.zip ----------")
        #print("Le nom du fichier zip respecte la spécification.")
        #print("Le nom du fichier '{}' est conforme.".format(fichier))
    elif re.match(pattern_def_TV, fichier):
        def_tv.append("ok")
        #print("---------- Vérifier le nom du Fichier SIG définitif : TV-SSSVVV-15-LDef.zip ----------")
        #print("Le nom du fichier zip respecte la spécification.")
        #print("Le nom du fichier '{}' est conforme.".format(fichier))
    
    if prov_cf:
        print("---------- Vérifier le nom du Fichier SIG provisoire: CF-SSSVVV-NNNN-06-LPProv.zip. ----------")
        if "ok" in prov_cf:
            print("Le nom du fichier zip respecte la spécification.")
        else:
            resultat_analyse.append("Non conforme")
            print("==>000 Le nom du fichier zip ne respecte pas la spécification.")
    elif def_cf:
        print("---------- Vérifier le nom du Fichier SIG définitif : CF-SSSVVV-NNNN-14-LPDef.zip ----------")
        if "ok" in def_cf:
            print("Le nom du fichier zip respecte la spécification.")
        else:
            resultat_analyse.append("Non conforme")
            print("==>000 Le nom du fichier zip ne respecte pas la spécification.")
    elif prov_tv:
        print("---------- Vérifier le nom du Fichier SIG provisoire : TV-SSSVVV-06-LPProv.zip ----------")
        if "ok" in prov_tv:
            print("Le nom du fichier zip respecte la spécification.")
        else:
            resultat_analyse.append("Non conforme")
            print("==>000 Le nom du fichier zip ne respecte pas la spécification.")
    
    elif def_tv:
        print("---------- Vérifier le nom du Fichier SIG définitif : TV-SSSVVV-14-LPDef.zip ----------")
        if "ok" in def_tv:
            print("Le nom du fichier zip respecte la spécification.")
        else:
            resultat_analyse.append("Non conforme")
            print("==>000 Le nom du fichier zip ne respecte pas la spécification.")
    else:
        resultat_analyse.append("Non conforme")
        print("---------- Vérifier le nom du Fichier SIG  ----------")
        print("==>000 Le nom du fichier zip ne respecte pas la spécification.")
    
    print("")
    print("-" * 118)
    print("---------- Le zip doit contenir les 4 fichiers suivants pour le point et la polygone : .shp, .prj, .dbf, .shx ----------")
    contenu_zip = set()
    # Charger le fichier ZIP
    zip_path = str(zip_file)
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
    
    print(" ")
    print("-" * 118)
    geom_layer = set()
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
            if couche.geometryType() == QgsWkbTypes.PointGeometry:
                geom_layer.add("Point")
            elif couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                geom_layer.add("Polyg")
            elif couche.geometryType() == QgsWkbTypes.LineGeometry:
                geom_layer.add("Line")
    #print(geom_layer)
    if "Point" in geom_layer and "Polyg" in geom_layer:
        print("---------- Le fichier .zip doit contenir : Un fichier Shape de type Polygone et Point. ----------")
        print("Le zip contient un shape de type Polygone et Point.")
    elif "Point" in geom_layer and "Line" in geom_layer:
        print("---------- Le fichier .zip doit contenir : Un fichier Shape de type Ligne et Point. ----------")
        print("Le zip contient un shape de type Ligne et Point.")
    else :
        print("---------- Vérifier les géometries des données chargées ----------")
        resultat_analyse.append("Non conforme")
        print("==>000 Les géometries des données chargées ne sont pas repectées.")
        
    print("")
    print("-" * 118)
    print("-------------- Les systèmes de coordonnées autorisés sont EPSG:32629 et EPSG:32630 --------------")
    crs_layer = set()
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
            # Vérifier du crs des couches
            crs = couche.crs().authid()
            geom = couche.wkbType()
            if geom == QgsWkbTypes.Point:
                if crs == 'EPSG:32629' or crs == 'EPSG:32630':
                    crs_layer.add(crs)
                    #print("La géométrie du fichier '{}' est de type 'Point'.".format(nom_couche))
            elif geom == QgsWkbTypes.MultiPolygon:
                if crs == 'EPSG:32629' or crs == 'EPSG:32630':
                    crs_layer.add(crs)
                #print("La géométrie du  fichier '{}' est de type 'Polygone.'".format(nom_couche))
            elif couche.geometryType() == QgsWkbTypes.LineGeometry:
                if crs == 'EPSG:32629' or crs == 'EPSG:32630':
                    crs_layer.add(crs)
                
    if 'EPSG:32629' in crs_layer or 'EPSG:32630' in crs_layer:
        print("Le système de coordonnées correspond à ceux autorisés  EPSG:32629 et EPSG:32630.")
    else:
        resultat_analyse.append("Non conforme")
        print("==>000 Le système de coordonnées ne correspond pas à ceux autorisés  EPSG:32629 et EPSG:32630.")
        
    #print("-------------- V5: VERIFICATION DES PREFIXES DES FICHIERS DE TYPE POLYGONE --------------")
    for fichier in os.listdir(output_folder):
        chemin_fichier = os.path.join(output_folder, fichier)
        # Vérifier si le fichier a une extension de shapefile
        if os.path.isfile(chemin_fichier) and any(fichier.endswith(ext) for ext in extension):
            # Extraire le nom de fichier sans extension pour le nom de la couche
            nom_couche = os.path.splitext(fichier)[0]
            # Charger la couche vecteur depuis le shapefile
            couche = QgsVectorLayer(chemin_fichier, nom_couche, "ogr")
            geom = couche.geometryType()
            if geom == QgsWkbTypes.PolygonGeometry:
                if nom_couche.startswith("CF_Polyg_"):
                    print(" ")
                    print("-" * 118)
                    print("-------------- Vérifier que le nom des fichiers du Shape de la polygo doit être préfixé par <CF_Polyg_>. --------------")
                    print("Le nom des fichiers du Shape du polygo est bien préfixé.")
                elif nom_couche.startswith("DTV_Polyg_"):
                    print(" ")
                    print("-" * 118)
                    print("-------------- Vérifier que le nom des fichiers du Shape de la polygo doit être préfixé par <DTV_Polyg_>. --------------")
                    print("Le nom des fichiers du Shape du polygone est bien préfixé.")
                else:
                    print(" ")
                    print("-" * 118)
                    resultat_analyse.append("Non conforme")
                    print("-------------- Vérifier les préfixes du Shape du polygone --------------")
                    print("==>000 Le nom des fichiers du Shape du polygone n'est pas bien préfixé")
            elif geom == QgsWkbTypes.LineGeometry:
                print(" ")
                print("-" * 118)
                print("-------------- Vérifier que le nom des fichiers du Shape des tronçons doit être préfixé par <DTV_Lignes_> --------------")
                if nom_couche.startswith("DTV_Lignes_"):
                    print("Le nom des fichiers du Shape du tronçon est bien préfixé.")
                else:
                    resultat_analyse.append("Non conforme")
                    print("==>000 Le nom des fichiers du Shape du tronçon n'est pas bien préfixé.")
            
    
    
    print(" ")
    print("-" * 118)
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
                    print("-------------- Vérifier que le nom des fichiers du Shape du point doit être préfixé par <CF_Points_> --------------")
                    print("Le nom des fichiers du Shape du point est bien préfixé")
                elif nom_couche.startswith("DTV_Points_"):
                    print("-------------- Vérifier que le nom des fichiers du Shape du point doit être préfixé par <DTV_Points_> --------------")
                    print("Le nom des fichiers du Shape du point est bien préfixé.")
                else:
                    print("-------------- Vérifier les préfixes du Shape du point --------------")
                    resultat_analyse.append("Non conforme")
                    print("==>000 Le nom des fichiers du Shape du point n'est pas bien préfixé.")
                    
    print(" ")
    print("-" * 118)
    extensions_supportees = ['.shp','.SHP']
    # Obtenir la liste des fichiers dans le dossier
    fichiers = [fichier for fichier in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, fichier))]
    print("-------------- Vérifier que tous les fichiers ont le même nom --------------")
    noms_de_bas = []
    for fichier in fichiers:
        if fichier.endswith('.shp') or fichier.endswith('.dbf') or fichier.endswith('.prj') or fichier.endswith('.shx') or fichier.endswith('.cpg'):
            chemin_fichier = os.path.join(output_folder, fichier)
            nom_fichier = os.path.splitext(fichier)[0]
            couche = QgsVectorLayer(chemin_fichier, nom_fichier, 'ogr')
            # Vérifier le type de géométrie de la couche
            if couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                if nom_fichier.startswith("CF_Polyg_"):
                    noms_de_bas.append("CF_Polyg_")
                elif nom_fichier.startswith("DTV_Polyg_"):
                    noms_de_bas.append("DTV_Polyg_")
            elif couche.geometryType() == QgsWkbTypes.LineGeometry:
                if nom_fichier.startswith("DTV_Lignes_"):
                    noms_de_bas.append("DTV_Lignes_")
            elif couche.geometryType() == QgsWkbTypes.PointGeometry:
                if nom_fichier.startswith("CF_Points_"):
                    noms_de_bas.append("CF_Points_")
                elif nom_fichier.startswith("DTV_Points_"):
                    noms_de_bas.append("DTV_Points_")
    nom = set()                
    if os.path.exists(output_folder):
        fichiers = os.listdir(output_folder)
        for fichier in fichiers:
            if noms_de_bas:
                if "CF_Polyg_" in noms_de_bas and (fichier.startswith("CF_Polyg_") and fichier.endswith(".shp")):
                    nom.add("ok")
                elif "DTV_Lignes_" in noms_de_bas and (fichier.startswith("DTV_Lignes_") and fichier.endswith(".shp")):
                    nom.add("ok") 
                elif "DTV_Polyg_" in noms_de_bas and (fichier.startswith("DTV_Polyg_") and fichier.endswith(".shp")):
                    nom.add("ok")
                elif "CF_Points_" in noms_de_bas and (fichier.startswith("CF_Points_") and fichier.endswith(".shp")):
                    nom.add("ok")
                elif "DTV_Points_" in noms_de_bas and (fichier.startswith("DTV_Points_") and fichier.endswith(".shp")):
                    nom.add("ok")
            #else: 
            #    resultat_analyse.append("Non conforme")
            #    print("==>000 Les préfixes des fichiers ne sont pas ne sont pas respectés.")
            #    break
    if "ok" in nom :
        print("Tous les fichiers ont le même nom.")
    else:
        resultat_analyse.append("Non conforme")
        print("==>000 Les noms des fichiers ne respectent pas la spécification.")
    
    print(" ")
    print("-" * 118)
    #print("-------------- V8: VERIFICATION DU SYSTEME DE COORDONNEES DES FICHIERS DE TYPE POLYGONE ET DE TYPE POINT --------------")
    #crs = couche.crs().authid()
    point_sys = set()
    poly_sys = set()
    ligne_sys = set()
    for fichier in os.listdir(output_folder):
        chemin_fichier = os.path.join(output_folder, fichier)
        # Vérifier si le fichier a une extension de shapefile
        if os.path.isfile(chemin_fichier) and any(fichier.endswith(ext) for ext in extension):
            # Extraire le nom de fichier sans extension pour le nom de la couche
            nom_couche = os.path.splitext(fichier)[0]
            # Charger la couche vecteur depuis le shapefile
            couche = QgsVectorLayer(chemin_fichier, nom_couche, "ogr")
            # Vérifier si la couche est valide
            if not couche.isValid():
                print("La couche n'est pas valide. Vérifiez le chemin du fichier.")
            else:
                # Détermination des crs des couches
                if couche.geometryType() == QgsWkbTypes.PointGeometry:
                    point_crs = couche.crs().authid()
                    point_sys.add(point_crs)
                elif couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                    poly_crs = couche.crs().authid()
                    poly_sys.add(poly_crs)
                elif couche.geometryType() == QgsWkbTypes.LineGeometry:
                    ligne_crs = couche.crs().authid()
                    ligne_sys.add(ligne_crs)
    # Comparaison des crs
    if poly_sys == point_sys:
        print("-------------- Le système de coordonnées du fichier de point doit être identique à celui du polygone --------------")
        print('Le système de coordonnées du fichier de point est identique à celui du polygone.')
    
    elif point_sys == ligne_sys:
        print("-------------- Le système de coordonnées du fichier de point doit être identique à celui du tronçon --------------")
        print('Le système de coordonnées du fichier de point est identique à celui du tronçon.')
    else:
        print("-------------- Le système de coordonnées du fichier de point doit être identique à celui du polygone --------------")
        resultat_analyse.append("Non conforme")
        print('Le système de coordonnées du fichier de point n\'est pas identique à celui du polygone.')
            
    
    print(" ")
    print("-" * 118)
    #print("-------------- V9: VERIFICATION DU FORMAT DES COLONNES DU POLYGONE --------------")
    fichiers = [fichier for fichier in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, fichier))]
    colonnes_cf = [
        'NUM_DOSS', 'NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF',
        'NOM_VILLAG', 'NOM_DEMAND', 'SUPERF', 'PERIM', 'NOM_PROJET', 'NOM_OTA']
    colonnes_requises_dtv = [
        'NBTRONCONS', 'NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF',
        'NOM_VILLAG','ID_VILLAGE', 'SUPERF', 'PERIM']
    colonne_troncon = [
        'TYPELIMITE', 'POSITION','VILLAGEVOI','TYPE_NATUR','LONG_LEVE', 'NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF',
        'NOM_VILLAG']
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(output_folder, fichier)
            nom_couche = os.path.splitext(fichier)[0]
            layer_polygon = QgsVectorLayer(chemin_fichier, nom_couche, 'ogr')
            #Vérifier le type de géométrie de la couche
            #polygon = layer_polygon.wkbType()
            if layer_polygon.geometryType() == QgsWkbTypes.PolygonGeometry:
                print("--------------  Vérifier que le format des colonnes du polygone est respecté --------------")
                # CF
                if nom_couche.startswith("CF"):
                    forma_cf = []
                    taille_cf = []
                    attribute_fields = [field.name() for field in layer_polygon.fields()]
                    #print("Voici les noms des colonnes du fichier de type polygone: {} ".format(attribute_fields))
                    # Comparez les champs requis avec les champs de la couche
                    missing_fields = list(set(colonnes_cf) - set(attribute_fields))
                    #extra_fields = list(set(attribute_fields) - set(colonnes_cf))
                    if missing_fields:
                        forma_cf.append("No")
                        resultat_analyse.append("Non conforme")
                        print(f"==>000 Il manque le(s) champ(s) '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}'.")
                    #elif extra_fields:
                    #    forma_cf.append("No")
                    #    resultat_analyse.append("Non conforme")
                    #    print("==>000 Le Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' n'est pas conforme.".format(extra_fields[0], nom_couche))
                    else:
                        forma_cf.append("Ok")
                    # vérification de la taille des champs
                    for colonne  in layer_polygon.fields().names():
                            champ = layer_polygon.fields().field(colonne)
                            #print(colonne)
                            # Vérifier si le champ est de type String
                            if champ.type() == QVariant.String:
                                #if colonne == "NO_TRANS":
                                #    if champ.length() != 15:
                                #        taille_cf.append("No")
                                #        resultat_analyse.append("Non conforme")
                                #        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (15).".format(colonne, champ.length()))
                                #    else:
                                #        taille_cf.append("Ok")
                                if colonne == "NOM_DEMAND":
                                    if not 50 <= champ.length() <= 100:
                                        taille_cf.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (100).".format(colonne, champ.length()))
                                elif colonne == "NUM_DOSS":
                                    if champ.length() != 50:
                                        taille_cf.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                elif colonne == "NOM_REGION":
                                    if champ.length() != 50:
                                        taille_cf.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                
                                elif colonne == "NOM_DEPART":
                                    if champ.length() != 50:
                                        taille_cf.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                elif colonne == "NOM_SSPREF":
                                    if champ.length() != 50:
                                        taille_cf.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                elif colonne == "NOM_VILLAG":
                                    if champ.length() != 50:
                                        taille_cf.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_cf.append("Ok")
                                    #print("Colonne '{}': Longueur = {}".format(colonne,  champ.length()))
                            elif champ.type() == QVariant.Double:
                                taille_cf.append("Ok")
                                #print("==>000 La taille de colonne '{}' est = {} avec une précision de {}, elle ne respecte pas la taille (20) et la précision (2) attendues.".format(colonne, champ.length(), precision))
                                
                            
                    #print(forma_cf)
                    #print(taille_cf)
                    if "No" in forma_cf and "No" in taille_cf:
                        print("Le format des colonnes du Polygone n'est pas respecté.")
                    elif "No" in forma_cf and "Ok" in taille_cf:
                        print("Le format des colonnes du Polygone n'est pas respecté.")
                    elif "Ok" in forma_cf and "No" in taille_cf:
                        print("Le format des colonnes du Polygone n'est pas respecté.")
                    else:
                        print(" Le format des colonnes du Polygone est respecté")
                elif nom_couche.startswith("DTV"):
                    forma_dtv = []
                    taille_dtv = []
                    attribute_fields = [field.name() for field in layer_polygon.fields()]
                    print("Voici les noms des colonnes du fichier de type polygone: {} ".format(attribute_fields))
                    # Comparez les champs requis avec les champs de la couche
                    missing_fields = list(set(colonnes_requises_dtv) - set(attribute_fields))
                    #extra_fields = list(set(attribute_fields) - set(colonnes_requises_hp))
                    if missing_fields:
                        resultat_analyse.append("Non conforme")
                        forma_dtv.append("No")
                        print(f"==>000 Il manque le(s) champ(s) '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}'.")
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
                                #if colonne == "NO_TRANS":
                                #    if champ.length() != 15:
                                #        taille_dtv.append("No")
                                #        resultat_analyse.append("Non conforme")
                                #        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (15).".format(colonne, champ.length()))
                                if colonne == "NOM_REGION":
                                    if champ.length() != 50:
                                        taille_dtv.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                elif colonne == "NOM_DEPART":
                                    if champ.length() != 50:
                                        taille_dtv.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                elif colonne == "NOM_SSPREF":
                                    if champ.length() != 50:
                                        taille_dtv.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                elif colonne == "NOM_VILLAG":
                                    if champ.length() != 50:
                                        taille_dtv.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_dtv.append("Ok")
                                    #print("Colonne '{}': Longueur = {}".format(colonne,  champ.length()))
                            elif champ.type() == QVariant.Double:
                                if colonne == "SUPERF":
                                    precision = champ.precision()
                                    if champ.length() != 20 and precision != 2:
                                        taille_dtv.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {} avec une précision de {}, elle ne respecte pas la taille (20) et la précision (2) attendues.".format(colonne, champ.length(), precision))
                                    else:
                                        taille_dtv.append("Ok")
                                    #print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                            elif champ.type() == QVariant.Integer:
                                if colonne == "NBTRONCONS":
                                    if champ.length() != 10:
                                        taille_dtv.append("No")
                                        resultat_analyse.append("Non conforme")
                                        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (10).".format(colonne, champ.length()))
                                    
                    #print(forma_dtv)
                    #print(taille_dtv)
                    if "No" in forma_dtv and "No" in taille_dtv:
                        print("Le format des colonnes du Polygone n'est pas respecté.")
                    elif "No" in forma_dtv and "Ok" in taille_dtv:
                        print("Le format des colonnes du Polygone n'est pas respecté.")
                    elif "Ok" in forma_dtv and "No" in taille_dtv:
                        print("Le format des colonnes du Polygone n'est pas respecté.")
                    else:
                        print(" Le format des colonnes du polygone est respecté.")
            elif layer_polygon.geometryType() == QgsWkbTypes.LineGeometry:
                print("--------------  Vérifier que le format des colonnes du tronçon est respecté --------------")
                forma_tr = []
                taille_tr = []
                attribute_fields = [field.name() for field in layer_polygon.fields()]
                #print("Voici les noms des colonnes du fichier de type polygone: {} ".format(attribute_fields))
                # Comparez les champs requis avec les champs de la couche
                missing_fields = list(set(colonne_troncon) - set(attribute_fields))
                #extra_fields = list(set(attribute_fields) - set(colonnes_cf))
                if missing_fields:
                    forma_tr.append("No")
                    resultat_analyse.append("Non conforme")
                    print(f"==>000 Il manque le(s) champ(s) '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}'.")
                #elif extra_fields:
                #    forma_cf.append("No")
                #    resultat_analyse.append("Non conforme")
                #    print("==>000 Le Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' n'est pas conforme.".format(extra_fields[0], nom_couche))
                else:
                    forma_tr.append("Ok")
                # vérification de la taille des champs
                for colonne  in layer_polygon.fields().names():
                        champ = layer_polygon.fields().field(colonne)
                        # Vérifier si le champ est de type String
                        if champ.type() == QVariant.String:
                            #if colonne == "NO_TRANS":
                            #    if champ.length() != 15:
                            #        taille_tr.append("No")
                            #        resultat_analyse.append("Non conforme")
                            #        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (15).".format(colonne, champ.length()))
                            if colonne == "TYPELIMITE":
                                if champ.length() != 20:
                                    taille_tr.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (20).".format(colonne, champ.length()))
                            elif colonne == "POSITION":
                                if champ.length() != 20:
                                    taille_tr.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (20).".format(colonne, champ.length()))
                            
                            elif colonne == "VILLAGEVOI":
                                if champ.length() != 100:
                                    taille_tr.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (100).".format(colonne, champ.length()))
                            
                            elif colonne == "TYPE_NATUR":
                                if champ.length() != 30:
                                    taille_tr.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (30).".format(colonne, champ.length()))
                            
                            elif colonne == "NOM_REGION":
                                if champ.length() != 50:
                                    taille_tr.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            
                            elif colonne == "NOM_DEPART":
                                if champ.length() != 50:
                                    taille_tr.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            elif colonne == "NOM_SSPREF":
                                if champ.length() != 50:
                                    taille_tr.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            elif colonne == "NOM_VILLAG":
                                if champ.length() != 50:
                                    taille_tr.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            else:
                                taille_tr.append("Ok")
                                #print("Colonne '{}': Longueur = {}".format(colonne,  champ.length()))
                        elif champ.type() == QVariant.Double:
                            if colonne == "LONG_LEVE":
                                precision = champ.precision()
                                if champ.length() != 20 and precision != 10:
                                    taille_tr.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {} avec une précision de {}, elle ne respecte pas la taille (20) et la précision (10) attendues.".format(colonne, champ.length(), precision))
                                else:
                                    taille_tr.append("Ok")
                                #print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                if "No" in forma_tr and "No" in taille_tr:
                        print("Le format des colonnes du Tronçon n'est pas respecté.")
                elif "No" in forma_tr and "Ok" in taille_tr:
                    print("Le format des colonnes du Tronçon n'est pas respecté.")
                elif "Ok" in forma_tr and "No" in taille_tr:
                    print("Le format des colonnes du Tronçon n'est pas respecté.")
                else:
                    print(" Le format des colonnes du Tronçon est respecté.")        
                
    print(" ")
    print("-" * 118)
    print("-------------- Vérifier que le format des colonnes du point est respecté --------------")
    champs_requis_cf = ['NUM_DOSS', 'NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF',  'NOM_DEPART', 
        'NOM_SSPREF', 'NOM_VILLAG', 'NUM_SOMMET', 'COORD_X', 'COORD_Y', 
         'TYP_SOMMET','TYP_LEVE', 'SOMM_SUIV', 'NOM_PROJET','DIST_SUIV', 'NUM_LIMIT', 'NOM_VOIS', "NOM_OTA"]
    champs_requis_dtv = [ 'TYP_LEVE', 'AMORCE', 'NOM_REGION', 'NOM_DEPART', 
        'NOM_SSPREF', 'NOM_VILLAG', 'NUM_SOMMET', 'COORD_X', 'COORD_Y', 
         'TYP_SOMMET', 'SOMM_SUIV', 'DIST_SUIV', 'NOM_VOIS', "NUM_TRONC"]
    forma_pt_cf = []
    taille_pt_cf = []
    for point_file in os.listdir(output_folder):
        point_path = os.path.join(output_folder, point_file)
        # Vérifier si le fichier est une couche vecteur
        if point_file.lower().endswith('.shp'):
            # Essayer d'ouvrir la couche vecteur
            layer_point = QgsVectorLayer(point_path, point_file, "ogr")
            point = couche.wkbType()
            if layer_point.geometryType() == QgsWkbTypes.PointGeometry:
                if point_file.startswith("CF"):
                    forma_pt_cf = []
                    taille_pt_cf = []
                    attribute_fields = [field.name() for field in layer_point.fields()]
                    #print("Voici les noms des colonnes du fichier de type point: {} ".format(attribute_fields))
                    # Comparez les champs requis avec les champs de la couche
                    missing_fields = list(set(champs_requis_cf) - set(attribute_fields))
                    #extra_fields = list(set(attribute_fields) - set(champs_requis_cf))
                    if missing_fields:
                        resultat_analyse.append("Non conforme")
                        forma_pt_cf.append("No")
                        print(f"==>000 Il manque le(s) champ(s) '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{point_file}'.")
                    #elif extra_fields:
                    #    print(" Ce Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' donc la table n'est pas conforme.".format(extra_fields[0], point_file))
                    else:
                        forma_pt_cf.append("Ok")
                        #print("Le format des champs de la table attributaire de la couche '{}' est conforme.".format(point_file))
                    for colonne  in layer_polygon.fields().names():
                        champ = layer_polygon.fields().field(colonne)
                        # Vérifier si le champ est de type String
                        if champ.type() == QVariant.String:
                            if colonne == "TYP_LEVE":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            
                            elif colonne == "TYP_SOMMET":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            
                            elif colonne == "NUM_LIMIT":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            
                            elif colonne == "NOM_REGION":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            
                            elif colonne == "NOM_DEPART":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            elif colonne == "NOM_SSPREF":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            elif colonne == "NOM_VILLAG":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            elif colonne == "NUM_LIMIT":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            elif colonne == "NOM_VOIS":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            elif colonne == "NOM_OTA":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            elif colonne == "NOM_PROJET":
                                if champ.length() != 50:
                                    taille_pt_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                            else:
                                taille_pt_cf.append("Ok")
                                #print("Colonne '{}': Longueur = {}".format(colonne,  champ.length()))
                        
                                #print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                        elif champ.type() == QVariant.Double:
                            taille_pt_cf.append("Ok")
                        
                    if "No" in forma_pt_cf and "No" in taille_pt_cf:
                            print("Le format des colonnes du Point n'est pas respecté.")
                    elif "No" in forma_pt_cf and "Ok" in taille_pt_cf:
                        print("Le format des colonnes du Point n'est pas respecté.")
                    elif "Ok" in forma_pt_cf and "No" in taille_pt_cf:
                        print("Le format des colonnes du Point n'est pas respecté.")
                    else:
                        print(" Le format des colonnes du Point est respecté.")
                elif point_file.startswith("DTV"):
                    forma_pt_dtv = []
                    taille_pt_dtv = []
                    attribute_fields = [field.name() for field in layer_point.fields()]
                    #print("Voici les noms des colonnes du fichier de type point: {} ".format(attribute_fields))
                    # Comparez les champs requis avec les champs de la couche
                    missing_fields = list(set(champs_requis_dtv) - set(attribute_fields))
                    #extra_fields = list(set(attribute_fields) - set(champs_requis_cf))
                    if missing_fields:
                        resultat_analyse.append("Non conforme")
                        forma_pt_dtv.append("No")
                        print(f"==>000 Il manque le champ '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{point_file}'.")
                    #elif extra_fields:
                    #    print(" Ce Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' donc la table n'est pas conforme.".format(extra_fields[0], point_file))
                    else:
                        forma_pt_dtv.append("Ok")
                        #print("Le format des champs de la table attributaire de la couche '{}' est conforme.".format(point_file))
                    for colonne  in layer_polygon.fields().names():
                        champ = layer_polygon.fields().field(colonne)
                        # Vérifier si le champ est de type String
                        if champ.type() == QVariant.String:
                            #if colonne == "NO_TRANS":
                            #    if champ.length() != 15:
                            #        taille_pt_dtv.append("No")
                            #        resultat_analyse.append("Non conforme")
                            #        print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (15).".format(colonne, champ.length()))
                            if colonne == "TYP_LEVE":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            elif colonne == "TYP_SOMMET":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            elif colonne == "NUM_LIMIT":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            elif colonne == "NOM_REGION":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            elif colonne == "NOM_DEPART":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            elif colonne == "NOM_SSPREF":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            elif colonne == "NOM_VILLAG":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            elif colonne == "NUM_LIMIT":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            elif colonne == "NOM_VOIS":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            elif colonne == "NOM_OTA":
                                if champ.length() != 50:
                                    taille_pt_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {}, elle ne respecte pas la taille attendue (50).".format(colonne, champ.length()))
                                else:
                                    taille_pt_dtv.append("Ok")
                            else:
                                taille_pt_cf.append("Ok")
                                #print("Colonne '{}': Longueur = {}".format(colonne,  champ.length()))
                        
                                #print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                    #print(forma_pt_dtv)
                    #print(taille_pt_dtv)
                    if "No" in forma_pt_dtv and "No" in taille_pt_dtv:
                            print("Le format des colonnes du Point n'est pas respecté.")
                    elif "No" in forma_pt_dtv and "Ok" in taille_pt_dtv:
                        print("Le format des colonnes du Point n'est pas respecté.")
                    elif "Ok" in forma_pt_dtv and "No" in taille_pt_dtv:
                        print("Le format des colonnes du Point n'est pas respecté.")
                    else:
                        print(" Le format des colonnes du Point est respecté.")
                    
    print(" ")
    print("-" * 118)
    #print("-------------- V11: VERIFICATION DES CHAMPS OBLIGATOIRES DES COLONNES  DU POLYGONE --------------")
    polygon_oblig = []
    troncon_oblig = []
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
                print("-------------- Vérifier que tous les champs obligatoires du polygone sont remplis par des valeurs --------------")
                # Boucler à travers les entités de la couche
                for colonne  in polygon_couche.fields().names():
                    # verifier les valeurs des champs
                    for entite in polygon_couche.getFeatures():
                        if str(entite[colonne]) == "NULL" or str(entite[colonne]) is None:
                            resultat_analyse.append("Non conforme")
                            polygon_oblig.append("No")
                            print(f"==>000 Le(s) champ(s) '{colonne}' contient une valeur nulle à la ligne {entite.id() +1}.")
                        else:
                            polygon_oblig.append("Ok")
                            #print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
                if "No" in polygon_oblig:
                    print("Tous les champs obligatoires du polygone ne sont pas remplis par des valeurs")
                else:
                    print("Tous les champs obligatoires du polygone sont remplis par des valeurs.")
            elif polygon_couche.geometryType() == QgsWkbTypes.LineGeometry:
                print("-------------- Vérifier que tous les champs obligatoires du tronçon sont remplis par des valeurs --------------")
                for colonne  in polygon_couche.fields().names():
                    # verifier les valeurs des champs
                    for entite in polygon_couche.getFeatures():
                        if colonne == "TYPE_NATUR":
                           if str(entite[colonne]) == "NULL" or str(entite[colonne]) is None:
                               troncon_oblig.append("Ok")
                        elif str(entite[colonne]) == "NULL" or str(entite[colonne]) is None:
                            resultat_analyse.append("Non conforme")
                            troncon_oblig.append("No")
                            print(f"==>000 Le(s) champ(s) '{colonne}' contient une valeur nulle à la ligne {entite.id() +1}.")
                        else:
                            troncon_oblig.append("Ok")
                if "No" in troncon_oblig:
                    print("Tous les champs obligatoires du tronçon ne sont pas remplis par des valeurs.")
                else:
                    print("Tous les champs obligatoires du tronçon sont remplis par des valeurs.")
    print(" ")
    print("-" * 118)
    print("-------------- Vérifier que tous les champs obligatoires du point sont remplis par des valeurs --------------")
    point_oblig = []
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
                            resultat_analyse.append("Non conforme")
                            point_oblig.append("No")
                            champs_nuls.append(f"==>000 Le champ '{colonne}' contient une valeur nulle à la ligne {valeur.id() + 1}.")
                    if champs_nuls:
                        resultat_analyse.append("Non conforme")
                        print("\n".join(champs_nuls))
                    else:
                        point_oblig.append("Ok")
                        #print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
                if "No" in point_oblig:
                    print("Tous les champs obligatoires du point ne sont pas remplis par des valeurs.")
                else:
                    print("Tous les champs obligatoires du point sont remplis par des valeurs.")
    print(" ")
    print("-" * 118)
    print("-------------- Décision de l'analyse --------------")
    if "Non conforme" in resultat_analyse:
        print("Les données chargées sont invalides car elles contiennent {} points de contrôle non conforme.\n\tVeuillez consulter ces points ci-dessus, précédés par ==>000.".format(len(resultat_analyse)))
    else:
        print("-------> 'Les données chargées sont valides.' <-------")