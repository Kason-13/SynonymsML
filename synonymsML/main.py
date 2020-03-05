# -*- coding: UTF-8 -*-
import sys
import cooccs 
import baseDonnee 
import cluster
def main():
    synonyme = ""
    mesArgv=' '.join(sys.argv[1:])
    dicOptions = cooccs.options().verificationDesArguments(mesArgv)
    listeDesOptions = cooccs.options().remplisageDesOptions(dicOptions)
    print(listeDesOptions)
    if "-e" in mesArgv or "-r" in mesArgv:
        taille = listeDesOptions[0]
        encodage = listeDesOptions[1]
        chemin = listeDesOptions[2]
    else:
        taille = listeDesOptions[0]
        nbMots = listeDesOptions[1]
        nbCentroid = listeDesOptions[2]
        listeMotCentroid = listeDesOptions[3]
 
    connexion = baseDonnee.bd().connexionBD()
    baseDonnee.bd().ajouterDansBD(connexion)
    #crï¿½er le vecteur de cooccs
    if "-e" in mesArgv :
       cooccs.options().choixEntrainement(connexion,taille,encodage,chemin)
       print("Bien inséré!")
    if "-r" in mesArgv:# pour la recherche, pas besoin de chemin ou encodage seulement taille
        cooccs.options().choixRecherche(connexion,taille)
    if "-c" in mesArgv and "-e" not in mesArgv:
        if len(listeMotCentroid) != 0: # si l'utilisateur rentre des mots. cela permet de get le nombre
            nbCentroid = listeMotCentroid
        cooccs.options().choixCluster(connexion,taille,nbMots,nbCentroid)
    connexion.close()

if __name__ =='__main__':
    sys.exit(main()) 