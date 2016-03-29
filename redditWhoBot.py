#################################################################################
#
#   Bot per extreure informació de la base de dades de reddit, fent ús de la
#   seva API.
#
#   Data creació:           24/03/2016
#   Última modificació:     29/03/2016
#
#   @ Autor: Ramon Royo
#            Treball de fi de grau (UOC)
#
#   @ Fonts consultades:
#
#   Writing a reddit bot - 02 - Writing ReplyBot (UPDATED)
#   https://www.youtube.com/watch?v=keiATJcZE8g
#
#   PRAW documentation
#   https://praw.readthedocs.org/en/stable/
#
#   @  subreddits i el nombre de subcriptors:
#
#       1ers 100 ordenats per nombre de subscriptors
#        >370.000 subscriptors
#       1ers 500 ordenats per nombre de subscriptors
#        >90.000 subscriptors
#       1ers 1000 ordenats per nombre de subscriptors
#        >45.000 subscriptors
#       1ers 1500 ordenats per nombre de subscriptors
#        >30.000 subscriptors
#       1ers 2500 ordenats per nombre de subscriptors
#        >17.000 subscriptors
#    
#################################################################################

import rwlogin                          # Script per connectar amb l'API i la BBDD
import praw                             # Wrapper API reddit
import subreddits                       # Pobla i/o actualitza la taula de subreddits

############
# VARIABLES
############

(r, db) = rwlogin.login()               # Connectem amb l'API i la BBDD

limit     = 100                         # Nombre màxim de subreddits per SELECT
offset    = 0                           # Valor de l'Offset del SELECT
SUB_LIMIT = 1000                        # Nombre màxim de subreddits a explorar

# la següent línia cal cridar-la cada x dies
# subreddits.getSubreddits(False, r, db)  # Actualitza la taula de subreddits (~3h de durada)

def processSubs():
    select = db.cur.execute('SELECT display_name FROM subreddits ORDER BY subscribers DESC LIMIT %s OFFSET %s;'
                            % (limit, offset))

    subNames = []                       # s'hi guardaran els noms

    if(select == limit):                # s'han capturat els noms correctament?    
        for name in db.cur._rows:       # name són tuples amb 1 sol valor
            subNames.append(name[0]) 

        # El proper pas després de guardar a la llista, és recorre-la i guardar missatges
        # del subreddit, a la BBDD, per això necessitaré tenir el cursor lliure.


        # Capturar un subreddit i agafar les publicacions HOT
        # r.get_subreddit('learnpython').get_hot(limit=10)
        # for submission in subreddit.get_hot(limit=10)




        offset += limit





##################################################################################

'''
bloc try catch

try:
except pymysql.OperationalError as e:
        print('Error connectant amb la base de dades: ' + str(e))
'''
















# Capturar un subreddit i agafar les publicacions HOT
# r.get_subreddit('learnpython').get_hot(limit=10)
# for submission in subreddit.get_hot(limit=10)

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