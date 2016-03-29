#################################################################################
#
#   Script per facilitar el login tant a l'API de reddit, com a la BBDD.
#
#   Ús, després d'importar-lo, es crida a la funció login().
#
#   Retorna dues variables:
#       r -> praw.Reddit object
#       db -> dblogin.baseDades
#
#   Data creació:           29/03/2016
#   Última modificació:     29/03/2016
#
#   @ Autor: Ramon Royo
#            Treball de fi de grau (UOC)
#
#################################################################################

import oauth2                           # Connexió amb l'API de reddit
import dblogin                          # Connexió amb la BBDD
import praw                             # Wrapper API reddit
import inspect

def login():
    # Per assegurar que s'estableix una connexió amb l'API, es comproven 3 condicions
    # si r està definida, si r és instància de praw.Reddit i si r conté una connexió Oauth2
    while True:
        if(('r' not in locals()) or (not isinstance(r, praw.Reddit)) or (not(r.is_oauth_session()))):
            r = oauth2.login()          # Instància de reddit            
        else:
            break                       # es compleixen les 3 condicions, es trenca el bucle

    # Igual que l'anterior, comprovacions per assegurar una connexió correcta
    while True:
        if(('db' not in locals()) or (not isinstance(db, dblogin.baseDades))):
            db = dblogin.login()        # Instància de la BBDD
        else:
            break

    return(r, db)