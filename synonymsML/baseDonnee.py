# -*- coding: UTF-8 -*-
import sqlite3

class bd:
    # connexion a sqldev
    def connexionBD(self):
        #dsn_tsn = cx_Oracle.makedsn('delta',1521,'decinfo')
        #chaineConnexion = 'e1572156/' + '1234' + '@' + dsn_tsn
        #connexion = cx_Oracle.connect(chaineConnexion)
        connexion=sqlite3.connect('BaseDonnee.db')
        
        return connexion
    
    def ajouterDansBD(self,connexion):
        req_ajoutDictionnaire="CREATE TABLE IF NOT EXISTS DICTIONNAIRE (ID INT PRIMARY KEY ,MOT VARCHAR(255) UNIQUE NOT NULL);  "
        req_ajoutMatrice="CREATE TABLE IF NOT EXISTS MATRICE (IDMOT1 INT,IDMOT2 INT,TAILLE INT,OCCURRENCE INT,PRIMARY KEY(IDMOT1,IDMOT2,TAILLE), FOREIGN KEY (IDMOT1) REFERENCES DICTIONNAIRE (ID)); "
        curseur=connexion.cursor()
        curseur.execute(req_ajoutDictionnaire)
        curseur.execute(req_ajoutMatrice)
        connexion.commit()
        
    def supprimerTable(self,connexion):
        req_supprimerDictionnaire=" "
    #pour rÃ©cupperer le dictionaire de la base de donnÃ©
    def recuperationDict(self,connexion):
        dic = {}
        nbrMot = "SELECT COUNT (*) FROM DICTIONNAIRE"
        curseur = connexion.cursor()
        curseur.execute(nbrMot)
        nbrMot = curseur.fetchall()
        nbrMot = nbrMot[0][0] # +1 pour le dernier mot
    
        mot = "SELECT MOT,ID FROM DICTIONNAIRE" 
        curseur.execute(mot)
        dic = dict(curseur.fetchall())
        
        return dic
    
    """
     COMPTAGE DES OCCURENCES ET INSERTION DANS LA BASE DE DONNÃ‰E: 2 LISTES: INSERTION ET UPDATE
     ARGUMENTS: la liste de mot du texte, la taille de fenetre, le dictionaire de mots, la connexion
    """
    def remplir_coorc(self,texte,tailleFen,dicMots,connexion):
        curseur = connexion.cursor()
        req_existOCC = "SELECT IDMOT1,IDMOT2,OCCURRENCE FROM MATRICE WHERE TAILLE=?"
        curseur.execute(req_existOCC,str(tailleFen),) 
        listOccExistant = curseur.fetchall()
        dExistant = {}
        for i in range(len(listOccExistant)):
           dExistant[(listOccExistant[i][0],listOccExistant[i][1])] = listOccExistant[i][2]
        dCoocs = {}
        tailleFenOri = tailleFen
        tailleFen = tailleFen//2
        for i in range(len(texte)):
            idmot = dicMots[texte[i]]
            for j in range(1,tailleFen+1):
                if i-j >=0:
                    idcooc = dicMots[texte[i-j]]
                    if (idmot,idcooc) not in dCoocs:
                        dCoocs[(idmot,idcooc)]=1
                    else:
                        dCoocs[(idmot,idcooc)]+=1
                if i+j<len(texte):
                    idcooc = dicMots[texte[i+j]]
                    if (idmot,idcooc) not in dCoocs:
                        dCoocs[(idmot,idcooc)]=1
                    else:
                        dCoocs[(idmot,idcooc)]+=1
    
        #insertion dans la db
        insert = []
        update = []
        for (idmot,idcooc),freq in dCoocs.items():
            if (idmot,idcooc) in dExistant:
                update.append((dCoocs[(idmot,idcooc)]+dExistant[(idmot,idcooc)],idmot,idcooc,tailleFen))
            else:
                insert.append((idmot,idcooc,tailleFenOri,freq))
        insertDansMatrice = "INSERT INTO MATRICE (IDMOT1,IDMOT2,TAILLE,OCCURRENCE) VALUES (?,?,?,?)"
        updateDansMatrice = "UPDATE MATRICE SET OCCURRENCE= ? WHERE IDMOT1 = ? AND IDMOT2 = ? AND TAILLE = ?"
        curseur.executemany(insertDansMatrice,insert)
        curseur.executemany(updateDansMatrice,update)
        connexion.commit()
        