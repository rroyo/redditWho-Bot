#################################################################################
#
#   Script per extreure informació de la pàgina http://www.reddit.com/reddits
#   Concretament extreu una llista amb tots els subreddits i el nombre de
#   subscriptors, entre d'altres dades i ho guarda tot en una taula SQL
#   anomenada 'subreddits'. Si el subreddit ja existeix a la taula, s'actualitza
#   el nombre de subscriptors.
#
#   Ús, s'importa i es crida a la funció get_subreddits, aquesta crida es pot
#   fer de dues maneres:
#
#   Des de la línia de comandos -> getSubreddits()
#   Des de l'script principal   -> getSubreddits(False, r, db)
#
#   En el primer cas, es connecta a l'API i a la BBDD i en el segon, se li passen
#   les connexions ja creades.
#
#   Data creació:           27/03/2016
#   Última modificació:     29/03/2016
#
#   @ Autor: Ramon Royo
#            Treball de fi de grau (UOC)
#
#   @ Fonts consultades:
#
#   Documentació Python 3
#   https://docs.python.org/3/
#
#   UnicodeEncodeError: 'latin-1' codec can't encode character
#   http://stackoverflow.com/questions/3942888/unicodeencodeerror-latin-1-codec-cant-encode-character
#
#################################################################################

from redditWhoLib import loginData
import rwlogin, pymysql, praw
from time import sleep

def getSubreddits(manual=True, r=None, db=None):
    count = 0                           # per portar el compte dels subreddits processats
    setLimit = 1000000                  # nombre màxim de subreddits a capturar

    # Si es fa una crida manual a la funció (per defecte), es connecta a la BBDD
    # i a l'API. Així diferencia entre les crides des de la línia de comandos i
    # les crides des de l'script principal, on ja s'haura fet una connexió.
    if(manual):
        (r, db) = rwlogin.login()       # connexió amb l'API i la BBDD    

    subreddits = r.get_popular_subreddits(limit=setLimit)
    
    # Es recorre el contingut
    for subreddit in subreddits:       
        # comprova que el subreddit no existeixi ja a la base de dades
        if not (db.cur.execute("SELECT idr FROM subreddits WHERE idr = '%s'" % subreddit.id)):
            # si no existeix es crea una nova entrada amb les dades capturades
            db.cur.execute('INSERT INTO subreddits (idr, display_name, created_utc,' +
                           'description, subscribers, over18) VALUES(%s, %s, %s, %s, %s, %s)',
                           ((subreddit.id,),(subreddit.display_name,),
                           (int(subreddit.created_utc),),(subreddit.public_description,),
                           (subreddit.subscribers,),(subreddit.over18,)))
        # si ja existeix, s'actualitza el nombre de subscriptors
        else:
            db.cur.execute("UPDATE subreddits SET subscribers = %s, over18 = %s WHERE idr = '%s'"
                            % (subreddit.subscribers, subreddit.over18, subreddit.id))

        count += 1                      # compta subreddits

        if not (count % 100):
            db.con.commit()             # es processen els INSERTS i UPDATES
            print('Últim subreddit processat: %s. Total processats: %s' % (subreddit.id, count))

    # FI bucle for    
    
    if(manual):
        db.con.close()                  # si crida manual, es tanca connexió

    return