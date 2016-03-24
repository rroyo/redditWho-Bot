#################################################################################
#
#	Script d'un sol ús, sols cal executar-lo una única vegada, per crear un token
#   de refresc i autoritzar l'accés del bot al compte de reddit.
#
#   El token de refresc permet crear nous tokens d'accés a l'API de reddit,
#   aquests últims tenen una vida de tan sols 60 minuts i cal regenerar-los.
#
#   Data creació:           23/03/2016
#   Última modificació:     24/03/2016
#
#	Autor: Ramon Royo
#	       Treball de fi de grau (UOC)
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

from redditWhoLib import oauth2         # Conté les dades de connexió
import praw, webbrowser

#################################################################################
# Connexió amb l'API
#################################################################################

r = praw.Reddit('redditWho script')     # Nova instància de reddit

# OAuth2 login
r.set_oauth_app_info(oauth2.app_id, oauth2.app_secret, oauth2.app_uri)

#################################################################################
# 1er objectiu. Autoritzar l'accés de l'app al compte d'usuari
#################################################################################

# Generar URL per autoritzar l'accés al compte de reddit
# get_authorize_url(state, scopes, token refreshable)
url = r.get_authorize_url('...',oauth2.app_scopes, True)
webbrowser.open(url)

#################################################################################
# 2on objectiu. Aconseguir el token de refresc
#################################################################################

# S'obrirà una instància del navegador i es demanarà donar autorització al compte
# vinculat a reddit. Un cop garantit, es carregarà l'adreça 'callback' i donarà
# error, ja que hem facilitat l'adreça local en un port on no hi ha cap servidor
# executant-se. No hi ha problema, ja que l'únic que ens interessa és l'adreça.
# Al final d'aquesta hi ha el paràmetre '&code=', seguit d'un codi alfanumèric.
# Cal copiar aquest codi i executar els següents comandos des d'un terminal.
app_callback_code = input('Codi d\'autorització: ')

# A continuació, access_information ara contindrà un diccionari amb l'scope,
# el token d'accés i el token de refresc de l'usuari. Aquest últim token, cal
# copiar-lo i guardar-lo a l'script oauth2.py, amb el nom 'app_refresh'.
# Allà es farà servir dintre de la funció login(), que té com a objectiu
# automatitzar el procés de connexió amb l'API.
access_information = r.get_access_information(app_callback_code)

# Per últim, s'imprimeix el token de refresc, que caldrà copiar.
print('Refresh Token: %s' % access_information['refresh_token'])