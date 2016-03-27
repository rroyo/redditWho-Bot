#################################################################################
#
#   Bot per extreure informació de la base de dades de reddit, fent ús de la
#   seva API.
#
#   
#   
#
#   Data creació:           24/03/2016
#   Última modificació:     24/03/2016
#
#   Autor: Ramon Royo
#          Treball de fi de grau (UOC)
#
#   Fonts consultades:
#
#   Writing a reddit bot - 02 - Writing ReplyBot (UPDATED)
#   https://www.youtube.com/watch?v=keiATJcZE8g
#
#   PRAW documentation
#   https://praw.readthedocs.org/en/stable/
#    
#################################################################################

import oauth2                           # Connexió amb l'API de reddit
import dblogin                          # Connexió amb la BBDD

if not(is_oauth_session())              # True si està connectat amb l'API
    r = oauth2.login()                  # Instància de reddit

db = dblogin.login()                    # Instància de la BBDD




##################################################################################
'''
while True:
    subreddit = r.get_subreddit('learnpython').get_hot(limit=10)
    for submission in subreddit.get_hot(limit=10)
'''

'''
Base de dades

try:
        db = pymysql.connect(host = loginData.DB_HOST,
                             user = loginData.DB_USER,
                             password = loginData.DB_PASS,
                             db = loginData.DB_NAME)
        cursor = db.cursor()
        print('Connexió amb la base de dades correcta.')
        return cursor
    except pymysql.OperationalError as e:
        print('Error connectant amb la base de dades: ' + str(e))
'''
















# Capturar un subreddit i agafar les publicacions HOT
# r.get_subreddit('learnpython').get_hot(limit=10)

# Capturar un post pel seu id i guardar-lo
# variable = r.get_submission(submission_id = "105aru")

# Veure les propietats d'un objecte
# print(vars(variable))

# Posts més votats de l'any en un subreddit
# popular.get_top_from_year()
# Després de fer:
'''
p = r.get_popular_subreddits()  # 25 en total
for popular in p:
    print (dir(popular))

Per imprimir el contingut de l'últim subreddit popular:

for var in popular.get_top_from_year():
    print(var)

I s'imprimeixen els vots i el títols dels posts més populars de l'últim any    
'''


# Per aconseguir veure el contingut d'un objecte, amb clau:valor quan l'objecte
# no és un diccionari i vars() no funciona, importa la llibreria inspect.
#
# import inspect
# inspect.getmembers(<objecte>)