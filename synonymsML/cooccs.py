# -*- coding: UTF-8 -*-
import numpy as np
from _operator import index
from numpy import insert
import sys
import baseDonnee
import cluster as clust
import re
from _ast import arg, Index
from optparse import Option

class options:
    def __init__(self):
    #liste de mot a eviter
        self.motsAEviter = ["le","la","lui","elle","il","on","tu","je","vous","nous","ils","car","parce","que","cet","cette","toujours","pendant","par"
                ,"dans","ce","ca","mon","ma","mais","les","l","de","du","des","ton","ta","son","sa","mes","ses","ces","tes","notre"
                ,"votre","leur","leurs","nos","vos","elles","et","oÃ¹","ou","donc","alors","quoi","quand","avec","sans","toi","moi","eux","sur"
                ,"Ã ","d","par","pas","qu","m","ce","plus","ces","se","ne","tout","toutes","tous","un","pour","une","peu","cette","cettes",
                 "cet","comme","s","en","n","c","--","a","est","Ã©tait","avait","j","au","qui","y","me","artagnan","athos","si","dit","mÃªme"
                 ,"dont","sous","air","aux","jusqu","la","lÃ ","maintenant","moins","mot","ni","nommÃ©s","peut","plupart","pourquoi","quel","quelle",
                 "quelles","quels","seulement","sien","sont","soyez","tandis","tellement","tels","trop","trÃ¨s","voient","vont","vu","Ã§a","Ã©taient",
                 "Ã©tat","Ã©tions","Ã©tÃ©","Ãªtre","ai","a","ah","eh","est-ce","un"]

    def lire(self,ch, enc):
        f = open(ch, 'r', encoding = enc)
        s = f.read().lower()
        f.close()
    
        return s

    """
        pour calculer le score, RETOURNE UN LISTE DE RESULTAT
        ARGUMENTS: dictionaire, mot choisi par l'utilisateur, la taille de fenetre, la connexion
    """
    def calculerScore(self,dico, motChoisi, methode,taille,connexion):
        produitScalaire = 0
        leastSqares = 1
        cityBlock = 2
        methode = int(methode)
        enonce_R_Matrice = "SELECT * FROM MATRICE WHERE TAILLE = :1 "
        resultat = []
        tailleDico = len(dico)
        vecteur = np.zeros((tailleDico,tailleDico))
        curseur = connexion.cursor()
        curseur.execute(enonce_R_Matrice,taille)
        retourDesValeurs = curseur.fetchall()
        for mesValeurs in retourDesValeurs:
            if int(mesValeurs[2]) == int(taille):
                if mesValeurs[0] != mesValeurs[1]:
                    vecteur[mesValeurs[0]-1][mesValeurs[1]-1] = mesValeurs[3]
                    
        if dico.get(motChoisi) != None and motChoisi in dico:
            vecteurMot = vecteur[dico.get(motChoisi)-1] #1
            indexDeMot = dico[motChoisi]
            for i in dico.keys():
                if i not in self.motsAEviter and i != motChoisi:
                    vecteurComparer = vecteur[dico.get(i)-1]
                    if methode == produitScalaire:
                        produit = np.dot(vecteurMot,vecteurComparer)
                    elif methode == leastSqares:
                        produit = np.sum((vecteurMot - vecteurComparer)**2)
                    elif methode == cityBlock:
                        produit = np.sum(abs(vecteurMot - vecteurComparer))
                    resultat.append((produit, i))
    
            if methode == produitScalaire:
                resultat = sorted(resultat,reverse = True)
            else:
                resultat = sorted(resultat)
        else :
            print("NavrÃ©, mais Le mot n'existe pas dans la base de donnÃ©e!")
        return resultat

    """
        verification des arguments pour voir s'il sonts valide, verification de la taille dans une autre fonction
        argument stringDeARGV: string qu'on rammase au debut de l'Ã©xectuction
    """
    def verificationDesArguments(self,stringDeARGV):
        modeEntrainement = False
        modeRecherche = False
        modeClust = False
        manqueArguments = False
        modeVerif = 0
          
        resultatsDesARGV = {"-t" : "",
                            "--enc" : "",
                            "--chemin": "",
                            "-n":"",
                            "--nc":"",
                            "--mots":""}
    
        argvSepare = stringDeARGV.split(" ",-1) #separe tout les argv en une liste
        #print(len(argvSepare),argvSepare )
        #print(len(argvSepare))
        if len(argvSepare) <= 7 or len(argvSepare) > 2:
            for indexARGV in range(len(argvSepare)):
                if argvSepare[indexARGV] == "-e":
                    modeEntrainement = True
                    modeVerif+=1
                    if len(argvSepare) !=7:
                        print("Trop ou pas assez d'argument dans les options pour un entrainement")
                        input("n'importe quel button pour terminer")
                elif argvSepare[indexARGV] == "-r":
                    modeRecherche = True
                    modeVerif+=1
                    if len(argvSepare) != 3:
                        print("Trop ou pas assez d'argument dans les options pour une recherche")
                        input("n'importe quel button pour terminer")
                elif argvSepare[indexARGV] == "-c":
                    modeClust = True
                    modeVerif+=1
                    if len(argvSepare) < 7:
                        print("Trop ou pas assez d'argument dans les options pour un clustering")
                        input("n'importe quel button pour terminer")
                if modeVerif !=1:
                    print("vous ne pouvez pas prendre deux options d'operations en meme temps au lancement du logiciel")
                    input("n'importe quel button pour terminer")
                    sys.exit()
                if argvSepare[indexARGV] in resultatsDesARGV:
                    if argvSepare[indexARGV] == "--mots":
                        n=1
                        while indexARGV+n != len(argvSepare):
                            resultatsDesARGV[argvSepare[indexARGV]] +=" "+argvSepare[indexARGV+n]
                            n+=1
                    else:
                        resultatsDesARGV[argvSepare[indexARGV]] = argvSepare[indexARGV+1]
                           
        return resultatsDesARGV
    """
        verification de l'argument taille si c un chiffre, et replisage des options choisi par l'utilisateur
        argument1: dictionaire qui contient les arguments : dic = {"-t" : "",
                                                                "--enc" : "",
                                                                "--chemin": ""}
    """
    def remplisageDesOptions(self,dic):
        taille = dic["-t"]
        listeDeRetour = []
        listeDeRetour.append(taille)
        if not taille.isdigit():
            print("la taille de fenetree n'est pas un chiffre ou un nombre")
            input("n'importe quel button pour terminer")
            sys.exit()
        if dic["--enc"] != "" and dic["--chemin"] != "":
            encodage = dic["--enc"]
            chemin = dic["--chemin"]
            listeDeRetour.append(encodage)
            listeDeRetour.append(chemin)
        else:
            nbMotAfficher = dic["-n"]
            nbCentroid = dic["--nc"]
            listeDeMotCentr = dic["--mots"].split()
            listeDeRetour.append(nbMotAfficher)
            listeDeRetour.append(nbCentroid)
            listeDeRetour.append(listeDeMotCentr)
        return listeDeRetour

    def choixCluster(self,connexion,taille,nbMots,listeMots):
        print(nbMots,listeMots)
        dic = baseDonnee.bd().recuperationDict(connexion)
        dicTaille = len(dic)
        clust.Clustering().toCluster(dic,listeMots,taille,connexion,nbMots)
        
        
    def choixRecherche(self,connexion,taille):
            recupDictionnaire=baseDonnee.bd().recuperationDict(connexion)#je prend de la bd les mots ainsi que le nbre de mots dans la bd
            #insertionMatrice(recupDictionnaire, listeMot, int(taille),connexion)
            print("Entrez un mot dont vous dÃ©sirez les synonymes,ainsi que Le nombre de rÃ©sultats dÃ©sirÃ© et la mÃ©thode qui vous convient :i.e produit scalaire:0, least-squares:1. city-block: 2" )
            resultat = input()
            motChoisi, nbSynonymes , methode = resultat.split()
            nbSynonymes= int(nbSynonymes)
            resultatScore=self.calculerScore(recupDictionnaire, motChoisi, methode,taille,connexion)
            if len(resultatScore) != 0:
                for i in range(nbSynonymes):
                    print(str(resultatScore[i][0]) + "--> " + str(resultatScore[i][1]))
                print("note: si les rÃ©sultats ci dessus sont tous des 0 et que le choix de recherche est city-bloc, cela veut dire que le mot n'a pas Ã©tÃ© entrainÃ© de la taille de fenetre choisi")
                    
    def choixEntrainement(self,connexion,taille,encodage,chemin):
        texte = self.lire(chemin, encodage)
        dicRecup = {}
        dicRecup = baseDonnee.bd().recuperationDict(connexion)
        dicMots = {}
        listeMot = []
        listeMot.extend(re.findall('[\w\-?\]]+', texte))
        curseur = connexion.cursor()
        idDansDB = "SELECT COUNT(*) FROM DICTIONNAIRE"
        curseur.execute(idDansDB)
        indexDictMotUnique = curseur.fetchall()
        indexDictMotUnique = indexDictMotUnique[0][0]
        indexDictMotUnique = int(indexDictMotUnique) # prend le nbr de mot dans dic de db
    
        """
            indexage des mots qui existe pas et les places dans le dictionnaire
        """
        for i in range(len(listeMot)):# longeur du texte
            if listeMot[i] not in dicRecup: # dic db
                if listeMot[i] not in dicMots:
                    indexDictMotUnique+=1
                    dicMots[listeMot[i]] = indexDictMotUnique # ajoute dans dic memoire
            else:
                dicMots[listeMot[i]] = dicRecup[listeMot[i]]
    
    
        DicListe = []
        for key in dicMots:
            if key not in dicRecup:
                DicListe.append([key,dicMots[key]])
        
        #insertion dans la db s'il y a des nouveau mots
        if DicListe:
            requeteInsertDic = "INSERT INTO DICTIONNAIRE(MOT,ID) VALUES (?,?)"
            curseur.executemany(requeteInsertDic,DicListe)
            connexion.commit()
        baseDonnee.bd().remplir_coorc(listeMot,int(taille),dicMots,connexion)

