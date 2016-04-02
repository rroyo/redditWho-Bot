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
#   How to retrieve SQL result column value using column name in Python?
#   http://stackoverflow.com/questions/10195139/how-to-retrieve-sql-result-column-value-using-column-name-in-python
#
#   Timesearch.py
#   https://github.com/voussoir/reddit/blob/master/Prawtimestamps/timesearch.py
#
#   @  Subreddits i el nombre de subcriptors (per decidir quants en processo):
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

import praw                             # Wrapper API reddit
import subreddits                       # Pobla i/o actualitza la taula de subreddits
import utils                            # Funcions d'ús comú
import time
import datetime

SUB_LIMIT = 100                         # Nombre màxim de subreddits a explorar
SCORE_MIN = 100                         # Puntuació mínima perquè una publicació sigui guardada

def start():
# La següent línia cal cridar-la cada periòdicament, per actualitzar el nombre de subscriptors.
#    subreddits.getSubreddits(False, r, db)  # Actualitza la taula de subreddits (~3h de durada)
    (r, db) = utils.rwlogin()           # Connectem amb l'API i la BBDD
    #getSubmissions()

    totalNewposts = 0                       # Nombre total de missatges nous afegits
    totalUpdates = 0                        # Nombre total de missatges actualitzats

    get_all_posts(subreddit='luc', db=db, r=r)
    utils.printSQLStats(None, totalNewposts, totalUpdates)





    db.con.close()
    del db.cur
    del db.con



def getSubmissions():
    ''' Captura un nombre de subreddits determinat per SUB_LIMIT i ordenats per nombre
        de subscriptors.
    '''
    try:
        # Es fa una consulta per capturar els noms dels subreddits
        select = db.cur.execute('SELECT display_name FROM subreddits ORDER BY subscribers ' + 
                                'DESC LIMIT %s;' % SUB_LIMIT)

        if (select == SUB_LIMIT):               # s'han capturat el nombre de noms esperat?
            subNames = db.cur.fetchall()        # es guarden els noms dels subreddits
        # Si la consulta retorna un valor diferent de l'esperat, es llença una excepció
        else:
            raise pymysql.MySQLError('S\'esperaven %d files i se n\'han extret %d'
                                     % (SUB_LIMIT, select))

        for subName in subNames:
            subreddit = r.get_subreddit(subName[0])


        # Capturar un subreddit i agafar les publicacions HOT
        # r.get_subreddit('learnpython').get_hot(limit=10)
        # for submission in subreddit.get_hot(limit=10)


        #row = db.cur.fetchone()   #pilla una sola fila
        #I amb row[0], row[1], ... Obtens els valors, finx a X, on X és el nombre
        #de columnes demanades



    except pymysql.MySQLError as e:
        print('Error extraïent dades de la BBDD: ' + str(e))


def get_all_posts(subreddit, db, r, lower=None, maxupper=None,
                  interval=864000000):
    '''
    subreddit:  s'envia el nom del subreddit, com a cadena.
    lower:      data inferior a partir de la que buscar.
                None, busca des de la creació del subreddit.
                update, afegeix els nous missatges des de l'últim cop
                que es va correr el programa.
    maxupper:   per defecte, el present.


    Get submissions from a subreddit or user between two points in time
    If lower and upper are None, get ALL posts from the subreddit or user.
    '''
    SCORE_MIN
    MAXIMUM_EXPANSION_MULTIPLIER = 2
    queryNewposts = 0                   # Noves publicacions, valor parcial
    queryUpdates = 0                    # Publicacions actualitzades
    newposts = 0                        # Noves publicacions, total subreddit
    updates = 0                         # Publicacions actualizades
    offset = -time.timezone
    
    if lower == 'update':        
        # Seguirà capturant missatges, des de l'últim que hi hagi a la BBDD
        db.cur.execute("SELECT idstr FROM posts WHERE subreddit like '%s' " +
                       "ORDER BY idstr DESC LIMIT 1;" % subreddit)
        row = cur.fetchone()
        if row:
            lower = row[0]              # [0], una sola columna demanada
        else:
            lower = None

    if lower is None:
        # la data mínima per començar a capturar missatges
        # serà la de la creació del subreddit
        lower = r.get_subreddit(subreddit).created_utc

    if maxupper is None:
        nowstamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        maxupper = nowstamp

    lower -= offset                     # Ajust dels valors, a la zona horaria
    maxupper -= offset
    cutlower = lower
    cutupper = maxupper
    upper = lower + interval
    itemcount = 0

    toomany_inarow = 0
    while lower < maxupper:
        print('\nCurrent interval: ', utils.s2hms(interval))
        print('Lower', utils.human(lower), lower)
        print('Upper', utils.human(upper), upper)
        while True:
            try:
                query = 'timestamp:%d..%d' % (lower, upper)
                searchresults = list(r.search(query, subreddit=subreddit, sort='new', limit=100, syntax='cloudsearch'))
                break
            except:
                traceback.print_exc()
                print('resuming in 5...')
                time.sleep(5)
                continue
        #Fi while

        searchresults.reverse()
        # La següent línia mostra els ids de les publicacions capturades,
        # la comento per evitar saturar la línia de comandos amb text.
        #print([i.id for i in searchresults])

        itemsfound = len(searchresults)
        itemcount += itemsfound
        print('Found', itemsfound, 'items')
        if itemsfound < 75:
            print('Too few results, increasing interval', end='')
            diff = (1 - (itemsfound / 75)) + 1
            diff = min(MAXIMUM_EXPANSION_MULTIPLIER, diff)
            interval = int(interval * diff)
        if itemsfound > 99:
            #Intentionally not elif
            print('Too many results, reducing interval', end='')
            interval = int(interval * (0.8 - (0.05*toomany_inarow)))
            upper = lower + interval
            toomany_inarow += 1
        else:
            lower = upper
            upper = lower + interval
            toomany_inarow = max(0, toomany_inarow-1)
            (queryNewposts, queryUpdates) = utils.smartinsert(db.con, db.cur, searchresults)
            newposts += queryNewposts
            updates += queryUpdates
        print()
    #Fi while

    utils.printSQLStats(subreddit, newposts, updates)




if (__name__ == '__main__'):
    start()
