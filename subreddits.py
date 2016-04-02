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
#   Última modificació:     01/04/2016
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

import pymysql, praw, utils
from time import time

def getSubreddits(manual=True, r=None, db=None):
    count = 0                           # per portar el compte dels subreddits processats
    setLimit = 2000000                  # nombre màxim de subreddits a capturar
    startTime = time()                  # per calcular el temps que es tarda

    # En teoria els noms dels subreddits han de ser únics, però he detectat alguns
    # subreddits amb els noms duplicats, són pocs i amb pocs subcriptors, per tant
    # els descarto, donat que a la BBDD he creat un índex per la columna dels noms,
    # per tal d'incrementar la velocitat i no hi poden haver duplicats.
    dupes = ('ColumbusBlueJackets')

    # Si es fa una crida manual a la funció (per defecte), es connecta a la BBDD
    # i a l'API. Així diferencia entre les crides des de la línia de comandos i
    # les crides des de l'script principal, on ja s'haurà fet una connexió.
    if(manual):
        (r, db) = utils.rwlogin()       # connexió amb l'API i la BBDD    

    subreddits = r.get_popular_subreddits(limit=setLimit)
    
    # Es recorre el contingut
    for subreddit in subreddits:   
        # Comprova que el subreddit no existeixi ja a la base de dades
        if not (db.cur.execute("SELECT 1 FROM subreddits WHERE idstr = '%s' LIMIT 1" % subreddit.id)):
            # Comprova si és un dels 'errors' de reddit, un subreddit amb nom duplicat
            if (subreddit.display_name not in dupes):
                # Si no existeix i no és un duplicat es crea una nova fila a la BBDD
                db.cur.execute('INSERT INTO subreddits (idstr, idint, display_name, created_utc,' +
                               'description, subscribers, over18) VALUES(%s, %s, %s, %s, %s, %s, %s)',
                               ((subreddit.id,),(utils.b36(subreddit.id),),(subreddit.display_name,),
                               (int(subreddit.created_utc),),(subreddit.public_description,),
                               (subreddit.subscribers,),(subreddit.over18,)))
        # Si ja existeix, s'actualitza
        else:
            db.cur.execute("UPDATE subreddits SET subscribers = %s, over18 = %s WHERE idstr = '%s' LIMIT 1"
                  % (subreddit.subscribers, subreddit.over18, subreddit.id))

        count += 1                      # compta subreddits explorats

        # Cada 100 subreddits, es fa un commit a la BBDD
        if not (count % 100):
            db.con.commit()
            print('Últim subreddit processat: %s. Total processats: %s' % (subreddit.id, count))            

    # FI bucle for    
    
    if(manual):
        db.con.close()                  # si la crida és des del , es tanca connexió
        print('Connexió amb la BBDD tancada.')

    # Mostra el temps que ha tardat en total    
    print ('Temps transcorregut total: ' % utils.chrono(startTime))

    return

# Quan l'script es crida directament des de la línia de comandos,
# p.ex. amb python subreddits.py, el següent codi s'executa directament.
# Però no s'executa si s'importa el codi com un mòdul des d'un altre script.
if __name__ == '__main__':
    getSubreddits()

