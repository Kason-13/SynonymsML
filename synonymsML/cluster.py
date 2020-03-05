# -*- coding: UTF-8 -*-
import numpy as np
import time
import random
import operator
from builtins import input
from test.test_lzma import INPUT
from pip._vendor.html5lib._ihatexml import digit
import sys
import csv

class Clustering:
    def __init__(self):
        self.motsAEviter = ["le","la","lui","elle","il","on","tu","je","vous","nous","ils","car","parce","que","cet","cette","toujours","pendant","par"
                            ,"dans","ce","ca","mon","ma","mais","les","l","de","du","des","ton","ta","son","sa","mes","ses","ces","tes","notre"
                            ,"votre","leur","leurs","nos","vos","elles","et","où","ou","donc","alors","quoi","quand","avec","sans","toi","moi","eux","sur"
                            ,"à","d","par","pas","qu","m","ce","plus","ces","se","ne","tout","toutes","tous","un","pour","une","peu","cette","cettes",
                            "cet","comme","s","en","n","c","--","a","est","était","avait","j","au","qui","y","me","artagnan","athos","si","dit","même"
                            ,"dont","sous","air","aux","jusqu","la","là","maintenant","moins","mot","ni","nommés","peut","plupart","pourquoi","quel","quelle",
                            "quelles","quels","seulement","sien","sont","soyez","tandis","tellement","tels","trop","très","voient","vont","vu","ça","étaient",
                            "état","étions","été","être","ai","a","ah","eh","est-ce","un"]
    
    """
        param 1:liste de mot chosi au depart, 2:liste de mot les plus proche, 3: dictionaire, 4:listeLS, 5:nbCluster, 6 vecteurs
    """
    def barycentreCalc(self,listeMotPlusProche,nbCentroids,vecteur):
        newCenters = []
        emplacementCentroide = []
        for c in range(nbCentroids): #pour le nb de centroids
            emplacementMot = []
            for i in range(len(listeMotPlusProche)): #fait le tour de tout les mots qui on ete donné à leur centroide
                if listeMotPlusProche[i] == c: #si le mot appartien on vecteur c, rentre et append son emplacement dans la liste
                    emplacementMot.append(vecteur[i])
            emplacementCentroide.append(emplacementMot) #mettre tout les emplacements des mots dans une liste pourcalculer le point milieu du prochain centroide

        for baryCenter in range(nbCentroids) :
            newCenters.append(np.mean(emplacementCentroide[baryCenter], axis = 0))#calculer la position des centroides
             
        return newCenters
    """
        pour obtenir distance
    """
    def obtenirDistEuclidean(self,row1,row2):
      return np.sum((row1 - row2)**2)
    """
        PARAM: 1:CONNEXION, 2:TAILLE DE FENETRE, 3:LISTE DE LIGNES DE VECTEURS DES NOUVEAU CENTRES, 4:DICTIONNAIRE
    """
    def TrouverPointCluster(self,nouveauCentres,dico,matrice,iter,rand,lsLesPlusProche):
        tailleDico = len(dico)
        listeLS = []
        vecteurCluster = []
        mesClusterEnScore = []
        listeMotPlusProche=[]

        # pour chaque point        
        for motChoisi in range(len(nouveauCentres)):
            resultat = {}
            #vecteur de mots horizontal du vecteur reconstruit

            vecteurMot = nouveauCentres[motChoisi]

            # calcul du score least square
            for i in dico.keys():
                vecteurComparer = matrice[dico.get(i)-1]
                produit = self.obtenirDistEuclidean(vecteurMot,vecteurComparer)
                resultat[i] = produit
            # append into list of score 
            listeLS.append(resultat) #liste des least square scores
        
        for i in range(len(nouveauCentres)):
            vecteurCluster.append(listeLS[i]) #passe les dictionaires de scores
         
            
        
        inversedDic = {v: k for k, v in dico.items()}
        if iter == 0 and rand == True: # si on veux trouver les clusters de facon random on return la liste maintenant
            return lsLesPlusProche, listeLS
        else:
            for i in range(tailleDico): #tour de tout les mots 
                toFilter = []
                """
                    on fait le tour des cluster -> append son score dans la liste toFilter -> 
                    on append à listeMotPlusProche l'index (représente à quel centroid il appartient)du score le plus bas de toFilter 
                """
                for j in range(len(nouveauCentres)):
                    toFilter.append(vecteurCluster[j][inversedDic[i+1]])
                listeMotPlusProche.append(toFilter.index(min(toFilter))) #,key = DicoToFilter.get
        return listeMotPlusProche , listeLS
    
    """
        reconstruction de la matrice de coocurences
        PARAM: 1:LISTE DE VALEURS VENANT DE LA BASE DE DONNÉE, 2:TAILLE DE DICTIONAIRE, 3:TAILLE DE FENETRE
    """
    def ReconstrucTabCooc(self, valuesFromDB,tailleDico,taille):
        vecteur = np.zeros((tailleDico,tailleDico))
        for mesValeurs in valuesFromDB:
            if int(mesValeurs[2]) == int(taille):
                if mesValeurs[0] != mesValeurs[1]:
                    vecteur[mesValeurs[0]-1][mesValeurs[1]-1] = mesValeurs[3]
        return vecteur  
    """
        assignation de chaque mots a un centroid random
    """
    def definitionDePointsRandom(self,tailleDico,nbCluster,vecteur):
        nouveauxCentres = []
        emplacementCentroides =[]
        lsVec = []
        listeRandomDesMots=[]
        
        #Faire des équipes de cluster random
        for mot in range(tailleDico):
                clusterRandom = random.randint(0, nbCluster-1)
                listeRandomDesMots.append(clusterRandom)
                #liste de la position 
                lsVec.append(vecteur[mot])
        for i in range(nbCluster):
            n=0
            lsLignes = []
            for j in range(len(listeRandomDesMots)):
                if listeRandomDesMots[j] == i:
                    lsLignes.append(lsVec[j])
                    n+=1
            emplacementCentroides.append(lsLignes)
            print("nombre de mots dans centroid ",i+1," : ",n)
        print("----------------------------------------------------------------")
        for baryCenter in range(nbCluster) :
            nouveauxCentres.append(np.mean(emplacementCentroides[baryCenter], axis = 0)) 
            
        return listeRandomDesMots,lsVec,emplacementCentroides,nouveauxCentres
    
    """
        boucle de chaque iteration (appelle des fonctions) et verifie si le clustering est fini (plsu aucun changement)
    """
    def boucleCentroid(self,nouveauxCentres,dico,vecteur,nbrIteration,randPoints,listeRandomDesMots,nbCluster,tempListe):
        clustDone = False 
        debut = time.time()
        ancienneListe, listeLS= self.TrouverPointCluster(nouveauxCentres,dico,vecteur,nbrIteration,randPoints,listeRandomDesMots)
        #param 1:liste de mot, 2:liste de mot les plus proche, 3: dictionaire, 4:listeLS, 5:nbcluster, 6 vecteurs
        nouveauxCentres = self.barycentreCalc(ancienneListe,nbCluster,vecteur)
        
        ancienneListe = np.array(ancienneListe)
        tempListe = np.array(tempListe)
        
        #changements = len(ancienneListe[ancienneListe != tempListe])
        #nbParCluster = [len(ancienneListe[ancienneListe == i]) for i in range(nbCLusters)]
        
        verifListe = np.equal(ancienneListe,tempListe)
        if verifListe.all():
            clustDone = True
            print("clustering finished")
            changementC = "aucune autre changement "
        else:
            changementC = 0
            for i in range(len(tempListe)):
                if tempListe[i] != ancienneListe[i]:
                   changementC+=1 
        print(time.time()-debut,"secondes pour cette iteration")
        print("--------------------------------------------------------")
        tempListe = ancienneListe
        nbrIteration+=1
        print("iteration #",nbrIteration)
        print(changementC, "dans cette iteration")
        for i in range(nbCluster):
            n=0
            for j in range(len(ancienneListe)):
                if ancienneListe[j] == i:
                   n+=1 

            print("nombres de points dans centroid ",i+1,": ",n)
        return listeLS,nouveauxCentres,nbrIteration,clustDone,tempListe,ancienneListe
    """
        dernier sort des valeurs et des scores pour afficher les resultats
    """
    def resultSorting(self,nbCluster,ancienneListe,inversedDic,listeLS):
        listeResultatDesResultat = []
        for j in range(nbCluster):
            dicoDesResultats = {}
            for i in range(len(ancienneListe)):
                if ancienneListe[i] == j:
                    if inversedDic[i+1] not in self.motsAEviter:
                        dicoDesResultats[inversedDic[i+1]] = listeLS[j][inversedDic[i+1]]

            listeResultatDesResultat.append(sorted(dicoDesResultats.items(),key=lambda t: t[1])) #sort la liste pour avoir les scores les plus petits
        return listeResultatDesResultat
    """
        pour imprimer les resultats pour chaque centroids avec son score ls
    """
    def printResults(self,nbCluster,nbMots,listeResultatDesResultat,vecteur,dico,TSVdic):
        for i in range(nbCluster):
            print("-----------------------------------------------------------")
            print("resultats du ",i+1,"ème centroide")
            for j in range(int(nbMots)):
                if j+1 < len(listeResultatDesResultat[i]): 
                    print(listeResultatDesResultat[i][j]," est un ",self.kNearN(vecteur,dico,TSVdic,listeResultatDesResultat[i][j][0]))
    """
        fonction principale de clustering
    """                   
    def toCluster(self,dico,listeToCluster,taille,connexion,nbMots):
        listeLS = []
        """
            ramasse les coocurences dans la bd
        """
        enonce_R_Matrice = "SELECT * FROM MATRICE WHERE TAILLE = ? "
        tailleDico = len(dico)
        curseur = connexion.cursor()
        curseur.execute(enonce_R_Matrice,taille)
        retourDesValeurs = curseur.fetchall()
        nouveauxCentres = []
        tempListe = []
        listeRandomDesMots=[]
        nbrIteration = 0
        newCenters=[]
        randPoints = False
        clustDone = False
        inversedDic = {v: k for k, v in dico.items()}
        """
            apport du lexique de langue francaise
        """
        lexiqueTSV_path = "Lexique382.tsv"
        sep = "\t"
        etiq = self.lireLines(lexiqueTSV_path)
        etiq_delimited = self.tsv_To_ls(etiq)
        TSVdic = self.creationDeRefDbTsv(etiq_delimited)
        #sys.stdout = open("Resultats.txt", "w")
        """
            reconstruction du vecteur de coocurence
        """
        vecteur = self.ReconstrucTabCooc(retourDesValeurs,tailleDico,taille)
        """
            etablit les nouveaux centres selon si l'utilisateur veut utiliser la fonction alleatoire ou choisir ses mots
        """
        if listeToCluster[0].isdigit(): # verifie si s'est un nombre au lieu de mots dans le nombre de centroid (on determine si on veut random ou pas)
            randPoints = True
            nbCluster = int(listeToCluster)
            lsVec = []
            emplacementCentroides = []
            listeRandomDesMots,lsVec,emplacementCentroides,nouveauxCentres = self.definitionDePointsRandom(tailleDico,nbCluster,vecteur)
        else:
            nbCluster = len(listeToCluster)
            for motChoisi in listeToCluster:
                nouveauxCentres.append(vecteur[dico.get(motChoisi)-1]) # ligne au complet
                
        tempListe = np.zeros(tailleDico)      
        while(clustDone == False):
            listeLS,nouveauxCentres,nbrIteration,clustDone,tempListe,ancienneListe = self.boucleCentroid(nouveauxCentres, dico, vecteur, nbrIteration, randPoints, listeRandomDesMots, nbCluster,tempListe)
            
        # listeLS key = word value = score
        listeResultatDesResultat = []
        listeResultatDesResultat = self.resultSorting(nbCluster,ancienneListe,inversedDic,listeLS)
        self.printResults(nbCluster,nbMots,listeResultatDesResultat,vecteur,dico,TSVdic) 
     
     
    def kNearN(self,vecteur,dico,TSVdic,mot):
        #valeur de K (nombres de voisin)
        kValue = 15
        return self.traiter_donnees(vecteur, dico,TSVdic,mot,kValue)
    
    def creationDeRefDbTsv(self,etiq_delimited):
        vecteur = {}
        for data in etiq_delimited:
            vecteur[data[0]] = data[3]
        return vecteur
    
    def lireLines(self,ch):
        with open(ch,"r",encoding = "utf8") as f:
            return  f.read().splitlines() 
    
    def tsv_To_ls(self,etiq):
       return csv.reader(etiq, delimiter='\t')
   
    def traiter_donnees(self,vecteur,dico,TSVdic,mot,kValue):
        ligneMatriceDuMot = vecteur[dico[mot]]
        dicCategory = {"NOM":0,"VER":0,"ADJ":0,"AUX":0,"PRE":0,"ADV":0,"ONO":0,"CON":0,"ADJ:num":0,"PRO:ind":0,"ADJ:pos":0,"ADJ:int":0,"ADJ:ind":0,"ADJ:dem":0,"ART:def":0,"ART:ind":0,"PRE":0,"PRO:dem":0,"PRO:int":0,"PRO:per":0,
                       "PRO:rel":0,"PRO:pos":0}
        lsWordValue = {}
        for i in dico.keys():
            vecteurComparer = vecteur[dico.get(i)-1]
            produit = self.obtenirDistEuclidean(ligneMatriceDuMot,vecteurComparer)
            lsWordValue[i] = produit
        sortedLs = sorted(lsWordValue.items(),key=lambda t: t[1])
        k = 0
        #mesVoisins = []
        i=0
        for key,value in sortedLs:
            if key in TSVdic:
                #mesVoisins.append(TSVdic[key])
                dicCategory[TSVdic[key]]+= 1/((sortedLs[i][1])+1)
                k+=1
            if k>=kValue:
                break
            i=+1
        stringDeVote=""
        for key in dicCategory:
            if dicCategory[key] !=0:
                stringDeVote += key +" : "+str(dicCategory[key])+" "
        print("\n votes: ",stringDeVote," En pouvoir de votes (total de ",kValue," votes)")
        return max(dicCategory, key=dicCategory.get)
            
            
        
        
        