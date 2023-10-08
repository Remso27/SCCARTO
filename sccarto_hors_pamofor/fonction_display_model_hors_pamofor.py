from qgis.core import *
from qgis.gui import *
from osgeo import ogr
from zipfile import ZipFile
import os
import re
from qgis.PyQt.QtCore import QVariant


@qgsfunction(args='auto', group='Custom')
def display_hors_pamofor(dossier, feature, parent):
    resultat_analyse = []
    print("-" * 148)
    print("---------- V1: VERIFICATION DE LA STRUCTURE DES REPERTOIRES ----------")
    # Vérifier si le chemin correspond au format spécifié
    pattern_1 =  r".*(CF\\[a-zA-Z0-9]+(\\[a-zA-Z0-9]+)*)"
    pattern_2 =  r".*(DTV\\[a-zA-Z0-9]+(\\[a-zA-Z0-9]+)*)"
    
    match_1 = re.search(pattern_1, dossier)
    match_2 = re.search(pattern_2, dossier)
    if match_1:
        # Si le format est respecté, on extrait le chemin à partir de "\CF" et l'imprime
        chemin_extracted = match_1.group(1)
        print("Voici la structure du répertoire des fichiers: " + f"'{chemin_extracted}'" + "\nCette structure est conforme.")
    elif match_2:
        chemin_extracted = match_2.group(1)
        print("Voici la structure du répertoire des fichiers: " + f"'{chemin_extracted}'" + "\nCette structure est conforme.")
    else:
        resultat_analyse.append("Non conforme")
        print("==>000 Voici la structure du répertoire des fichiers: " + f"'{dossier}'" + "\nCette structure du répertoire n'est pas conforme.")
    
    
    print("")
    print("-" * 148)
    print("---------- V2: VERIFICATION DU CONTENU DU DOSSIER CHARGE ----------")
    # Obtenez la liste des fichiers dans le dossier
    print("Voici la liste des fichiers chargés: ")
    if os.path.exists(dossier):
        fichiers = os.listdir(dossier)
        for fichier in fichiers:
            print(f"'{fichier}'")
    
    
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
            #geom = couche.wkbType()
            geom_type = couche.geometryType()
            if geom_type == QgsWkbTypes.PointGeometry:
                print("La géométrie du fichier '{}' est de type 'Point'.".format(nom_couche))
            elif geom_type == QgsWkbTypes.PolygonGeometry:
                    print("La géométrie du fichier '{}' est de type 'Polygone'.".format(nom_couche))
            #elif geom_type == QgsWkbTypes.LineGeometry: 
                #print("La géométrie du fichier '{}' est de type 'Line'.".format(nom_couche))
            else:
                resultat_analyse.append("Non conforme")
                print("==>000 La géométrie du fichier '{}' est de type 'Inconnu.'".format(nom_couche))
            # Vérifier le crs des couches
            crs = couche.crs().authid()
            if crs == 'EPSG:32629':
                print("Le fichier '{}' a pour système de coordonnée: '{}'. Ce système est autorisé.".format(nom_couche, "EPSG:32629"))
    
            elif crs == 'EPSG:32630':
                print("Le fichier '{}' a pour système de coordonnée: '{}'. Ce système est autorisé.".format(nom_couche, "EPSG:32630"))
            else:
                resultat_analyse.append("Non conforme")
                print("==>000 Le fichier '{}' a pour système de coordonnée: '{}'. Ce système n'est pas autorisé.".format(nom_couche, crs))
    
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
            polygon = couche.geometryType()
            if polygon == QgsWkbTypes.PolygonGeometry:
                if nom_couche_polygon.startswith("CF_Polyg_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche_polygon, "CF_Polyg_"))
                elif nom_couche_polygon.startswith("DTV_Polyg_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche_polygon, "DTV_Polyg_"))
                else:
                    resultat_analyse.append("Non conforme")
                    print("==>000 Le préfixe du fichier {} n'est pas conforme.".format(nom_couche_polygon))
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
            point = couche.geometryType()
            if point == QgsWkbTypes.PointGeometry:
                if nom_couche_point.startswith("CF_Points_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche_point, "CF_Points_"))
                elif nom_couche_point.startswith("DTV_Points_"):
                    print("Le fichier {} est préfixé par '{}' donc le nom est conforme.".format(nom_couche_point, "DTV_Points_"))
                else:
                    resultat_analyse.append("Non conforme")
                    print("==>000 Le préfixe du fichier {} n'est pas conforme.".format(nom_couche_point))
    couche = None
    
    print(" ")
    print("-" * 148)
    print("-------------- V7: VERIFICATION DES NOMS DES FICHIERS  --------------")
    noms_de_bas = []
    for fichier in fichiers:
        if fichier.endswith('.shp') or fichier.endswith('.dbf') or fichier.endswith('.prj') or fichier.endswith('.shx') or fichier.endswith('.cpg'):
            chemin_fichier = os.path.join(dossier, fichier)
            nom_fichier_poly = os.path.splitext(fichier)[0]
            couche = QgsVectorLayer(chemin_fichier, nom_fichier_poly, 'ogr')
            # Vérifier le type de géométrie de la couche
            if couche.geometryType() == QgsWkbTypes.PolygonGeometry:
                if nom_fichier_poly.startswith("CF_Polyg_"):
                    noms_de_bas.append("CF_Polyg_")
                elif nom_fichier_poly.startswith("DTV_Polyg_"):
                    noms_de_bas.append("DTV_Polyg_")
                
    if os.path.exists(dossier):
        fichiers = os.listdir(dossier)
        for fichier in fichiers:
            if "CF_Polyg_" in noms_de_bas:
                if fichier.startswith("CF_Polyg_") and fichier.endswith(".shp"):
                    print("Le fichier '{}' préfixé par '{}' a le même nom que ses sous fichiers.".format(fichier, "CF_Polyg_"))
            elif "DTV_Polyg_" in noms_de_bas:
                if fichier.startswith("DTV_Polyg_") and fichier.endswith(".shp"):
                    print("Le fichier '{}' préfixé par '{}' a le même nom que ses sous fichiers.".format(fichier, "DTV_Polyg_"))
            else:
                resultat_analyse.append("Non conforme")
                print("==>000 Les noms des fichiers de type polygone ne sont pas identiques.")
        
    noms_de_fichier = []
    for fichier in fichiers:
        if fichier.endswith('.shp') or fichier.endswith('.dbf') or fichier.endswith('.prj') or fichier.endswith('.shx') or fichier.endswith('.cpg'):
            chemin_fichier = os.path.join(dossier, fichier)
            nom_couche_point = os.path.splitext(fichier)[0]
            couche = QgsVectorLayer(chemin_fichier, nom_couche_point, 'ogr')
            # Vérifier le type de géométrie de la couche
            if couche.geometryType() == QgsWkbTypes.PointGeometry:
                if nom_couche_point.startswith("CF_Points_"):
                    noms_de_fichier.append("CF_Points_")
                elif nom_couche_point.startswith("DTV_Points_"):
                    noms_de_fichier.append("DTV_Points_")
                
    if os.path.exists(dossier):
        fichiers = os.listdir(dossier)
        for fichier in fichiers:
            if "CF_Points_" in noms_de_fichier:
                if fichier.startswith("CF_Points_") and fichier.endswith(".shp"):
                    print("Le fichier '{}' préfixé par '{}' a le même nom que ses sous fichiers.".format(fichier, "CF_Points_"))
            elif "DTV_Points_" in noms_de_fichier:
                if fichier.startswith("DTV_Points_") and fichier.endswith(".shp"):
                    print("Le fichier '{}' préfixé par '{}' a le même nom que ses sous fichiers.".format(fichier, "DTV_Points_"))
            else:
                resultat_analyse.append("Non conforme")
                print("==>000 Les noms des fichiers de type polygone ne sont pas identiques.")
    
    
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
                print("Le système de coordonnées du fichier '{}' est : '{}'".format(nom_couche, point_crs))
            elif geom == QgsWkbTypes.MultiPolygon:
                polygon_crs = couche.crs().authid()
                print("Le système de coordonnées du fichier '{}' est : '{}'".format(nom_couche, polygon_crs))
                if point_crs == polygon_crs:
                    print("Vu ce qui précède on en déduit que le système de coordonnées du fichier point est identique à celui du polygone dont crs = '{}'.".format(polygon_crs))
                else:
                    resultat_analyse.append("Non conforme")
                    print('==>000 Vu ce qui précède on en déduit que le système de coordonnées du fichier de type point n\'est pas identique à celui du polygone.')
    couche = None
    
    print(" ")
    print("-" * 148)
    print("-------------- V9: VERIFICATION DU FORMAT DES COLONNES DU POLYGONE --------------")
    colonnes_requises = [
        'NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF','NOM_VILLAG', 'NOM_DEMAND', 'NOM_PROJET', 'NOM_OTA', 'SUPERF']
    colonnes_requises_hp = ['NOM_REGION', 'NOM_DEPART', 'NOM_SSPREF','NOM_VILLAG', 'NOM_PROJET', 'NOM_OTA', 'SUPERF']
    for fichier in fichiers:
        if os.path.splitext(fichier)[-1].lower() in extensions_supportees:
            chemin_fichier = os.path.join(dossier, fichier)
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
                    print("Voici les noms des colonnes du fichier de type polygone: {} ".format(attribute_fields))
                    # Comparez les champs requis avec les champs de la couche
                    missing_fields = list(set(colonnes_requises) - set(attribute_fields))
                    extra_fields = list(set(attribute_fields) - set(colonnes_requises))
                    if missing_fields:
                        forma_cf.append("No")
                        resultat_analyse.append("Non conforme")
                        print(f"==>000 Il manque ce champ '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}' donc cette table n'est pas conforme.")
                    elif extra_fields:
                        forma_cf.append("No")
                        resultat_analyse.append("Non conforme")
                        print("==>000 Le Champ '{}' est inattendu donc le format de la table attributaire de la couche '{}' n'est pas conforme.".format(extra_fields[0], nom_couche))
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
                                    if champ.length() != 100:
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
                                if champ.length() != 20 and precision != 4:
                                    taille_cf.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {} avec une précision de {}, elle ne respecte pas la taille (20) et la précision (2) attendues.".format(colonne, champ.length(), precision))
                                else:
                                    taille_cf.append("Ok")
                                    #print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                    #print(forma_cf)
                    #print(taille_cf)
                    if "No" in forma_cf and "No" in taille_cf:
                        print("Le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))
                    elif "No" in forma_cf and "Ok" in taille_cf:
                        print("Le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))
                    elif "Ok" in forma_cf and "No" in taille_cf:
                        print("Le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))
                    else:
                        print("Le format des champs de la table attributaire de la couche '{}' est conforme.".format(nom_couche))
                    
                # DTV
                elif nom_couche.startswith("DTV_Polyg_"):
                    forma_dtv = []
                    taille_dtv = []
                    attribute_fields = [field.name() for field in layer_polygon.fields()]
                    print("Voici les noms des colonnes du fichier de type polygone: {} ".format(attribute_fields))
                    # Comparez les champs requis avec les champs de la couche
                    missing_fields = list(set(colonnes_requises_hp) - set(attribute_fields))
                    extra_fields = list(set(attribute_fields) - set(colonnes_requises_hp))
                    if missing_fields:
                        resultat_analyse.append("Non conforme")
                        forma_dtv.append("No")
                        print(f"==>000 Il manque ce champ '{', '.join(missing_fields)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}'.")
                    elif extra_fields:
                        forma_dtv.append("No")
                        resultat_analyse.append("Non conforme")
                        print("==>000 Le Champ '{}' est inattendu au niveau de la table attributaire de la couche '{}'.".format(extra_fields[0], nom_couche))
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
                                if champ.length() != 20 and precision != 2:
                                    taille_dtv.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {} avec une précision de {}, elle ne respecte pas la taille (20) et la précision (2) attendues.".format(colonne, champ.length(), precision))
                                else:
                                    taille_dtv.append("Ok")
                                    #print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                    #print(forma_dtv)
                    #print(taille_dtv)
                    if "No" in forma_dtv and "No" in taille_dtv:
                        print("Donc le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))
                    elif "No" in forma_dtv and "Ok" in taille_dtv:
                        print("Donc le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))
                    elif "Ok" in forma_dtv and "No" in taille_dtv:
                        print("Donc le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))
                    else:
                        print("Le format des champs de la table attributaire de la couche '{}' est conforme.".format(nom_couche))
                else:
                    print("Le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))     
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
                forma = []
                taille = []
                attribute_champ = [field.name() for field in layer_point.fields()]
                print("Voici les noms des colonnes du fichier de type point: {} ".format(attribute_champ))
                # Comparez les champs requis avec les champs de la couche
                champs_manquant = list(set(champs_requis) - set(attribute_champ))
                extra_champ = list(set(attribute_champ) - set(champs_requis))
                if champs_manquant:
                    resultat_analyse.append("Non conforme")
                    forma.append("No")
                    print(f"==>000 Il manque ce champ '{', '.join(champs_manquant)}' dans la liste des champs de la table attributaire de la couche '{nom_couche}.")
                elif extra_champ:
                    resultat_analyse.append("Non conforme")
                    forma.append("No")
                    print("==>000 Le Champ '{}' est inattendu au niveau de la table attributaire de la couche '{}'.".format(extra_champ[0], nom_couche))
                else:
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
                                if champ.length() != 20 and precision != 10:
                                    taille.append("No")
                                    resultat_analyse.append("Non conforme")
                                    print("==>000 La taille de colonne '{}' est = {} avec une précision de {}, elle ne respecte pas la taille (20) et la précision (10) attendues.".format(colonne, champ.length(), precision))
                                else:
                                    taille.append("Ok")
                                #    print("Colonne '{}': Longueur = {}.{}".format(colonne,  champ.length(), precision))
                if "No" in forma and "No" in taille:
                    print("Donc le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))
                elif "No" in forma and "Ok" in taille:
                    print("Donc le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))
                elif "Ok" in forma and "No" in taille:
                    print("Donc le format des champs de la table attributaire de la couche '{}' n'est pas conforme.".format(nom_couche))
                else:
                    print("Le format des champs de la table attributaire de la couche '{}' est conforme.".format(nom_couche))
    layer_point = None
    
    print(" ")
    print("-" * 148)
    print("-------------- V11: VERIFICATION DES VALEURS DES CHAMPS  DU POLYGONE --------------")
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
                            resultat_analyse.append("Non conforme")
                            print(f"==>000 Le champ '{colonne}' contient une valeur nulle à la ligne {entite.id() +1}.")
                        else:
                            print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
                    
                    #for feature in polygon_couche.getFeatures():
                    #    valeur = feature[colonne]
                    #    if isinstance(valeur, str):
                    #        if len(valeur) >= 50:
                    #            resultat_analyse.append("Non conforme")
                    #            print("La taille de la valeur '{}' appartenant à la colonne '{}' ne respecte pas le nombre de caractères attendu. Voir la ligne {}".format(valeur, colonne, feature.id() + 1))
                    #    elif isinstance(valeur, float):
                    #        valeur_arrondie = round(valeur, 10)
                    #        if len(str(valeur_arrondie)) >=20:
                    #            resultat_analyse.append("Non conforme")
                    #            print("La taille de la valeur '{}' appartenant à la colonne '{}' ne respecte pas le nombre de caractères attendu. Voir la ligne {}".format(valeur_arrondie, colonne, feature.id() + 1))
                    
    
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
                            resultat_analyse.append("Non conforme")
                            champs_nuls.append(f"==>000 Le champ '{colonne}' contient une valeur nulle à la ligne {valeur.id() + 1}.")
                    if champs_nuls:
                        print("\n".join(champs_nuls))
                    else:
                        print(f"Le champ '{colonne}' est conforme car il ne contient pas de valeurs nulles.")
                    
                    #for feature in point_couche.getFeatures():
                    #    valeur = feature[colonne]
                    #    if isinstance(valeur, str):
                    #        if len(valeur)  >= 50:
                    #            resultat_analyse.append("Non conforme")
                    #            print("La taille de la valeur '{}' appartenant à la colonne '{}' ne respecte pas le nombre de caractères attendu. Voir la ligne {}.".format(valeur, colonne, feature.id() + 1))
                    #    elif isinstance(valeur, float):
                    #        valeur_arrondie = round(valeur, 10)
                    #        if len(str(valeur_arrondie))  >= 20:
                    #            resultat_analyse.append("Non conforme")
                    #            print("La taille de la valeur '{}' appartenant à la colonne '{}' ne respecte pas le nombre de caractères attendu. Voir la ligne {}".format(valeur_arrondie, colonne, feature.id() + 1))
                                
    
    print(" ")
    print("-" * 148)
    print("-------------- DECISION FINALE DE L'ANALYSE --------------")
    #print(resultat_analyse)
    if "Non conforme" in resultat_analyse:
        print("Les données chargées sont invalides car elles contiennent {} points de contrôle non conforme.\n\t --->Veuillez consulter ces points de contrôle ci dessus précédés par ==>000".format(len(resultat_analyse)))
    else:
        print("\t----> 'Les données chargées sont valides.' <----")
    
    return 0