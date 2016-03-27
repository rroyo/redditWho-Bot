#################################################################################
#
#   Script per extreure informació de la pàgina http://www.reddit.com/reddits
#   Concretament extreu una llista amb tots els subreddits i el nombre de
#   subscriptors.
#
#   Data creació:           27/03/2016
#   Última modificació:     27/03/2016
#
#   Autor: Ramon Royo
#          Treball de fi de grau (UOC)
#
#   Fonts consultades:
#
#   Scrapping reddit
#   https://gist.github.com/DanBrink91/8375591
#
#   Requests: HTTP for Humans
#   http://docs.python-requests.org/en/master/
#
#################################################################################

from redditWhoLib import loginData
import requests
from time import sleep
import json
import pymysql

#  Capturo 25 subreddits
request = requests.get(r'http://www.reddit.com/reddits/.json',
                       headers = {'User-agent': loginData.APP_UA})
subs = {}
data = request.json()

titles_by_hundreds = 10

db.cursor.execute('USE '+ loginData.DB_NAME +';')
db.connection.commit()

for child in data['data']['children']:
    sub_id = child['data']['id']
    display_name = child['data']['display_name']
    created_utc = child['data']['created_utc']
    description = child['data']['public_description']
    subscribers = child['data']['subscribers']
    over18 = child['data']['over18']

    db.cursor.execute('INSERT INTO subreddits (id, display_name, created_utc,' +
                      'description, subscribers, over18) VALUES(%s, %s, %s, %s, %s, %s)'
                      ,((sub_id,),(display_name,),(created_utc,),(description,),
                      (subscribers,),(over18,)))
    db.connection.commit()

## VALORS CAPTURATS PELS 25 PRIMERS SUBREDDITS
## CAL ITERAR FINS FER TOTES LES PÀGINES
