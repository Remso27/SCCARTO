from qgis.core import *
from qgis.gui import *
from osgeo import ogr
from zipfile import ZipFile
import os
import re
import geopandas as gpd
from qgis.PyQt.QtCore import QVariant


@qgsfunction(args='auto', group='Custom')
def display_hors_pamofor(dossier, feature, parent):
    print("")
    print("-" * 148)
    print("-------------- V3 & V4 : VERIFICATION DE LA GÉOMETRIE ET LES SYSTÈMES  DE COORDONNÉES DES FICHIERS CHARGÉS --------------")
    # Liste des extensions de fichiers de couches vecteurs supportées
    extensions_supportees = ['.shp','.SHP']
    # Obtenir la liste des fichiers dans le dossier
    fichiers = [fichier for fichier in os.listdir(dossier) if os.path.isfile(os.path.join(dossier, fichier))]
    # Charger les couches vecteurs et les ajouter à la vue QGIS
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(dossier, fichier)
            nom_couche = os.path.splitext(fichier)[0]
            couche = QgsVectorLayer(chemin_fichier, nom_couche, 'ogr')
            if couche.isValid():
                QgsProject.instance().addMapLayer(couche)
                #print(f"La couche {fichier} a été chargée avec succès.")
            else:
                print(f"La couche {fichier} n'est pas valide et n'a pas été chargée.")
            # Vérifier le type de géométrie de la couche
            geom = couche.wkbType()
            if geom == QgsWkbTypes.Point:
                print("La géométrie du fichier '{}' est de type 'Point'.".format(nom_couche))
            elif geom == QgsWkbTypes.MultiPolygon:
                    print("La géométrie du fichier '{}' est de type 'Polygone'.".format(nom_couche))
            else:
                print("La géométrie du fichier '{}' est de type 'Inconnu.'".format(nom_couche))
            # Vérifier le crs des couches
            crs = couche.crs().authid()
            if crs == 'EPSG:32629':
                print("Le fichier '{}' a pour système de coordonnée: {}. Ce système est autorisé.".format(nom_couche, "EPSG:32629"))
    
            elif crs == 'EPSG:32630':
                print("Le fichier '{}' a pour système de coordonnée: {}. Ce système est autorisé.".format(nom_couche, "EPSG:32630"))
            else:
                print("Le fichier '{}' a pour système de coordonnée: {}. Ce système n'est pas autorisé.".format(nom_couche, crs))
    
    couche = None
    
    print(" ")
    print("-" * 148)
    print("-------------- V5: VERIFICATION DES PREFIXES DES FICHIERS DE TYPE POLYGONE --------------")
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(dossier, fichier)
            nom_couche_polygon = os.path.splitext(fichier)[0]
            couche = QgsVectorLayer(chemin_fichier, nom_couche_polygon, 'ogr')
            # Vérifier le type de géométrie de la couche
            polygon = couche.wkbType()
            if polygon == QgsWkbTypes.MultiPolygon:
                if nom_couche.startswith("CF_Polyg_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche_polygon, "CF_Polyg_"))
                else:
                    print("Le préfixe du fichier {} n'est pas conforme.".format(nom_couche_polygon))
                    
    couche = None
    
    print(" ")
    print("-" * 148)
    print("-------------- V6: VERIFICATION DES PREFIXES DES FICHIERS DE TYPE POINT --------------")
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(dossier, fichier)
            nom_couche_point = os.path.splitext(fichier)[0]
            couche = QgsVectorLayer(chemin_fichier, nom_couche_point, 'ogr')
            # Vérifier le type de géométrie de la couche
            point = couche.wkbType()
            if point == QgsWkbTypes.Point:
                if nom_couche.startswith("CF_Points_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche_point, "CF_Points_"))
                else:
                    print("Le préfixe du fichier {} n'est pas conforme.".format(nom_couche_point))
    couche = None
    
    print(" ")
    print("-" * 148)
    print("-------------- V7: VERIFICATION DES NOMS DES FICHIERS  --------------")
    noms_de_bas = {}
    for fichier in fichiers:
        if fichier.endswith('.shp') or fichier.endswith('.dbf') or fichier.endswith('.prj') or fichier.endswith('.shx') or fichier.endswith('.cpg'):
            chemin_fichier = os.path.join(dossier, fichier)
            nom_fichier_poly = os.path.splitext(fichier)[0]
            couche = QgsVectorLayer(chemin_fichier, nom_fichier_poly, 'ogr')
            # Vérifier le type de géométrie de la couche
            if couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                # Séparez le nom du fichier et son extension
                nom_base, extension = os.path.splitext(fichier)
                # Ajout du nom de base au dictionnaire
                noms_de_bas[nom_base] = noms_de_bas.get(nom_base, 0) + 1
            
    # Vérification si tous les fichiers ont le même nom de base
    if len(noms_de_bas) == 1:
        print("Tous les fichiers de type polygone préfixé par 'CF_Polyg_' ont le même nom.")
    else:
        print("Tous les fichiers de type polygone préfixé par 'CF_Polyg_' n'ont pas le même nom.")
    
    noms_de_fichier = {}
    for fichier in fichiers:
        if fichier.endswith('.shp') or fichier.endswith('.dbf') or fichier.endswith('.prj') or fichier.endswith('.shx') or fichier.endswith('.cpg'):
            chemin_fichier = os.path.join(dossier, fichier)
            nom_couche_point = os.path.splitext(fichier)[0]
            couche = QgsVectorLayer(chemin_fichier, nom_couche_point, 'ogr')
            # Vérifier le type de géométrie de la couche
            if couche.geometryType() == QgsWkbTypes.PointGeometry:
                # Séparez le nom du fichier et son extension
                nom_base, extension = os.path.splitext(fichier)
                # Ajout du nom de base au dictionnaire
                noms_de_fichier[nom_base] = noms_de_fichier.get(nom_base, 0) + 1
            
    # Vérification si tous les fichiers ont le même nom de base
    if len(noms_de_fichier) == 1:
        print("Tous les fichiers de type polygone préfixé par 'CF_Points_' ont le même nom.")
    else:
        print("Tous les fichiers de type polygone préfixé par 'CF_Points_' n'ont pas le même nom.")            
    couche = None
    
    print(" ")
    print("-" * 148)
    print("-------------- V8: VERIFICATION DU SYSTEME DE COORDONNEES DES FICHIERS DE TYPE POLYGONE ET DE TYPE POINT --------------")
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(dossier, fichier)
            nom_couche = os.path.splitext(fichier)[0]
            couche = QgsVectorLayer(chemin_fichier, nom_couche, 'ogr')
            geom = couche.wkbType()
            # Vérifier le crs des couches
            crs = couche.crs().authid()
            if geom == QgsWkbTypes.Point:
                point_crs = couche.crs().authid()
                print("Le système de coordonnées du fichier '{}' est : {}".format(nom_couche, point_crs))
            elif geom == QgsWkbTypes.MultiPolygon:
                polygon_crs = couche.crs().authid()
                print("Le système de coordonnées du fichier '{}' est : {}".format(nom_couche, polygon_crs))
                if polygon_crs == point_crs:
                    print('Vu ce qui précède on en déduit que le système de coordonnées du fichier point est identique à celui du polygone dont crs = {}.'.format(polygon_crs))
                else:
                    print('Vu ce qui précède on en déduit que le système de coordonnées du fichier de type point n\'est pas identique à celui du polygone.')
    couche = None
    print(" ")
    print("-" * 148)
    print("-------------- V9: VERIFICATION DU FORMAT DES COLONNES DU POLYGONE --------------")
    
    colonnes_requises = [
        'NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF','NOM_VILLAG', 'NOM_DEMAND', 'NOM_PROJET', 'NOM_OTA', 'SUPERF']
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(dossier, fichier)
            nom_couche = os.path.splitext(fichier)[0]
            layer_polygon = QgsVectorLayer(chemin_fichier, nom_couche, 'ogr')
            # Vérifier le type de géométrie de la couche
            polygon = layer_polygon.wkbType()
            if polygon == QgsWkbTypes.MultiPolygon:
                attribute_fields = [field.name() for field in layer_polygon.fields()]
                print("Voici les noms des colonnes du fichier de type polygone: {} ".format(attribute_fields))
                # Comparez les champs requis avec les champs de la couche
                missing_fields = list(set(colonnes_requises) - set(attribute_fields))
                extra_fields = list(set(attribute_fields) - set(colonnes_requises))
                if missing_fields:
                    print(f"Il manque ce champ '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}' donc cette table n'est pas conforme.")
                elif extra_fields:
                    print(" Ce Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' n'est pas conforme.".format(extra_fields[0], nom_couche))
                else:
                    print("Ce format des champs de la table attributaire de la couche '{}' est conforme.".format(nom_couche))
    
    layer_polygon = None            
    
    print(" ")
    print("-" * 148)
    print("-------------- V10: VERIFICATION DU FORMAT DES COLONNES DU POINT --------------")
    
    champs_requis = ['COORD_X', 'COORD_Y', 'NUM_SOMMET']
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(dossier, fichier)
            nom_couche = os.path.splitext(fichier)[0]
            layer_point = QgsVectorLayer(chemin_fichier, nom_couche, 'ogr')
            # Vérifier le type de géométrie de la couche
            point = layer_point.wkbType()
            if point == QgsWkbTypes.Point:
                attribute_champ = [field.name() for field in layer_point.fields()]
                print("Voici les noms des colonnes du fichier de type point: {} ".format(attribute_champ))
                # Comparez les champs requis avec les champs de la couche
                champs_manquant = list(set(champs_requis) - set(attribute_champ))
                extra_champ = list(set(attribute_champ) - set(champs_requis))
                if champs_manquant:
                    print(f"Il manque ce champ '{', '.join(champs_manquant)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}' donc cette table n'est pas conforme.")
                elif extra_champ:
                    print(" Ce Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' n'est pas conforme.".format(extra_champ[0], nom_couche))
                else:
                    print("Ce format des champs de la table attributaire de la couche '{}' est conforme.".format(nom_couche))
    layer_point = None
    print(" ")
    print("-" * 148)
    print("-------------- V11: VERIFICATION DES VALEURS DES CHAMPS  DU POLYGONE --------------")
    # Créez un dictionnaire pour stocker les champs et les lignes avec des valeurs nulles
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(dossier, fichier)
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
                            print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
                            
    
    print(" ")
    print("-" * 148)
    print("-------------- V12: VERIFICATION DES VALEURS DES CHAMPS  DU POINT --------------")
    # Créez un dictionnaire pour stocker les champs et les lignes avec des valeurs nulles
    
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(dossier, fichier)
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
                        print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
    
    return 0