#################################################################################
#
#   Script per facilitar el login a l'API, un cop s'ha executat
#   l'script oauth_token.py per primer cop i s'ha autoritzat l'accés de l'app
#   al compte d'usuari i s'ha aconseguit el token de refresc.
#
#   Data creació:           23/03/2016
#   Última modificació:     24/03/2016
#
#   Autor: Ramon Royo
#          Treball de fi de grau (UOC)
#
#   Fonts consultades:
#
#   Writing a reddit bot - 03 - OAuth 2
#   https://www.youtube.com/watch?v=Uvxu2efXuiY
#
#   PRAW and OAUTH
#   http://praw.readthedocs.org/en/stable/pages/oauth.html
#
#################################################################################

from redditWhoLib import loginData
import praw

def login():
    print('Connectant amb l\'API de reddit.')
    r = praw.Reddit(loginData.APP_UA)                       # Nova instància de reddit
    r.set_oauth_app_info(loginData.APP_ID,                  # OAuth2 login
                loginData.APP_SECRET, loginData.APP_URI)
    r.refresh_access_information(loginData.APP_REFRESH)     # Refresc del token
    print('Connexió amb l\'API correcta. '
          'Connectat com a ' + str(r.user) + '.')
    return r                                                # Retorna la instància