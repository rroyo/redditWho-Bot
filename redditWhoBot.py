# Guia per poder autentificar l'aplicació amb l'API de reddit
# https://github.com/reddit/reddit/wiki/OAuth2
# HOW TO
# https://tsenior.com/2014-01-23-authenticating-with-reddit-oauth
# https://www.reddit.com/r/redditdev/comments/197x36/using_oauth_to_send_valid_requests/c8lz57u

# Writing a reddit bot - 03 - OAuth 2
# https://www.youtube.com/watch?v=Uvxu2efXuiY

#Recorda que ne algun moment has instal·lat PRAW, cal reflexar-ho a la memòria

#################################################################################
#
#	redditWho bot
#
#	author: Ramon Royo
#	for:	Treball de fi de grau (UOC)
#
#
#
#
#
#################################################################################

from redditWhoLib import oauth2
import praw, webbrowser

version = '2016.03.22'

# New reddit Instance
r = praw.Reddit('redditWho v%s' % (version))

# OAuth2 login
r.set_oauth_app_info(oauth2.app_id, oauth2.app_secret, oauth2.app_uri)

# Request access to the developer account
# get_authorize_url(state, scopes, token refreshable)
url = r.get_authorize_url('...', oauth2.app_scopes, True)
webbrowser.open(url)
