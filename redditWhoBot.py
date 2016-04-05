#################################################################################
#
#   Bot per extreure informació de la base de dades de reddit, fent ús de la
#   seva API.
#
#   Data creació:           24/03/2016
#   Última modificació:     05/03/2016
#
#   @ Autor: Ramon Royo
#            Treball de fi de grau (UOC)
#
#   @ Fonts consultades:
#
#   Documentació Python 3
#   https://docs.python.org/3/
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
#   UnicodeEncodeError: 'latin-1' codec can't encode character
#   http://stackoverflow.com/questions/3942888/unicodeencodeerror-latin-1-codec-cant-encode-character
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
#   @ Intervals de puntuacions i el percentatge de publicacions que se'n publiquen
#     Valors obtinguts a partir d'un set de 1227822 publicacions, dels dos subreddits
#     amb més subscriptors.
#
#       >999  punts   0,94% de les publicacions (11591)
#       >1999 punts   0,71% de les publicacions (8678)
#       >2999 punts   0,52% de les publicacions (6438)
#       >3999 punts   0,30% de les publicacions (3664)
#       >4999 punts   0,10% de les publicacions (1217)
#
#   Trio 1000 com a valor mínim, que és un valor conservador. Els valors obtinguts
#   no són extrapolables als subreddits inferiors, donat que el nombre de subcriptors
#   a partir del subreddit 100, és 30 vegades inferior al del primer.
#
#################################################################################

import praw                             # Wrapper API reddit
import utils                            # Funcions d'ús comú
import pymysql                          # Per interactuar amb la BBDD
import time
import datetime

SUB_LIMIT = 2000000                     # Subreddits capturats
TOP_SUB_LIMIT = 100                     # Subreddits dels que s'extreuen publicacions
MIN_SCORE = 1000                        # Puntuació mínima per incloure una publicació
UPDATE_WAIT = 86400                     # Temps d'espera en segons, entre actualitzacions de la BBDD
START_DATE = (time.time() - 31536000)   # Data a partir de la qual començar a capturar publicacions
                                        #   None, capturarà totes les publicacions des de l'inici del subreddit
                                        #   31536000 equival a un any en segons
                                        # Ara mateix només es capturen les publicacions de fa un any
                                        # fins ara, donat que el temps que es tarda en capturar totes
                                        # les publicacions de 100 subreddits, per limitacions de l'API,
                                        # és elevat (> 1 any).
GET_SUBS_INTERVAL = 86400               # Interval de temps incial per capturar publicacions

def start():
    ''' Controla el funcionament del bot. Crida a les funcions que capturen els noms
        dels subreddits, extreu les publicacions i ho emmagatzema tot en una base de
        dades.

        És la funció que s'executarà quan es cridi al bot des de la línia de comandos.
    '''    
    while True:        
        (r, db) = utils.rwlogin()       # Connecta amb l'API i la BBDD

        # Actualitza la taula de subreddits (~3h de durada) 
        # getSubreddits(False, r, db)

        # Explora publicacions dels subreddits seleccionats
        getSubmissions(False, r, db)

        # Es tanquen les connexions innecessàries
        db.con.close()
        del db.cur
        del db.con
        print('Connexions tancades.')
        print('Esperant {0} per la propera iteració\n\n'.format(utils.s2hms(UPDATE_WAIT)))
        time.sleep(UPDATE_WAIT)

def getSubreddits(manual=True, r=None, db=None):
    ''' Extreu informació de la pàgina http://www.reddit.com/reddits
        Concretament extreu una llista amb tots els subreddits i el nombre de
        subscriptors, entre d'altres dades i ho guarda tot en una taula SQL
        anomenada 'subreddits'. Si el subreddit ja existeix a la taula, s'actualitza
        el nombre de subscriptors.
    
        Ús, s'importa i es crida a la funció get_subreddits, aquesta crida es pot
        fer de dues maneres:

        Des de la línia de comandos -> getSubreddits()
        Des de l'script principal   -> getSubreddits(False, r, db)

        En el primer cas, es connecta a l'API i a la BBDD i en el segon, se li passen
        les connexions ja creades.

        :param manual: True o False (opcional)
        :param r: class 'praw.Reddit' (opcional)
        :param db: class 'utils.baseDades' (opcional)
    '''

    startTime = time.time()             # per calcular el temps que es tarda
    newSubs = 0                         # per portar el compte dels subreddits processats
    updatedSubs = 0
    totalSubs = 0

    # En teoria els noms dels subreddits han de ser únics, però he detectat alguns
    # subreddits amb els noms duplicats, són pocs i amb pocs subcriptors, per tant
    # els descarto, donat que a la BBDD he creat un índex per la columna dels noms,
    # per tal d'incrementar la velocitat i no hi poden haver duplicats.
    dupes = ('ColumbusBlueJackets')

    print('Capturant subreddits...')

    # Si es fa una crida manual a la funció (per defecte), es connecta a la BBDD
    # i a l'API. Així diferencia entre les crides des de la línia de comandos i
    # les crides des de l'script principal, on ja s'haurà fet una connexió.
    if(manual):
        (r, db) = utils.rwlogin()       # connexió amb l'API i la BBDD    

    subreddits = r.get_popular_subreddits(limit=SUB_LIMIT)
    
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
                newSubs += 1
        # Si ja existeix, s'actualitza
        else:
            db.cur.execute("UPDATE subreddits SET subscribers = %s, over18 = %s WHERE idstr = '%s' LIMIT 1"
                  % (subreddit.subscribers, subreddit.over18, subreddit.id))
            updatedSubs += 1                              
        
        totalSubs = newSubs + updatedSubs

        # Cada 100 subreddits, es fa un commit a la BBDD
        if not (totalSubs % 100):
            db.con.commit()
            print('Últim subreddit processat: %s. Total processats: %s' % (subreddit.id, totalSubs))         
    # FI bucle for    
    
    if(manual):
        db.con.close()
        del db.cur
        del db.con
        print('Connexió amb la BBDD tancada.')

    # Mostra el temps que ha tardat en total
    utils.printGetSubsStats(startTime, newSubs, updatedSubs)

def getSubmissions(manual=True, r=None, db=None):
    ''' Captura un nombre de subreddits determinat per TOP_SUB_LIMIT i ordenats per nombre
        de subscriptors. Després un a un, en captura les publicacions.

        :param manual: True o False (opcional)
        :param r: class 'praw.Reddit' (opcional)
        :param db: class 'utils.baseDades' (opcional)

        :return: El nombre de publicacions noves i actualitzades
        :rtype: str i str
    '''
    totalNewposts = 0                   # Nombre total de missatges nous afegits (sessió)
    totalUpdates = 0                    # Nombre total de missatges actualitzats (sessió)
    newposts = 0                        # Nombre missatges nous (subreddit)
    updates = 0                         # Nombre missatges actualitzats (subreddit)
    subsCount = 1                       # Comptador per saber els subreddits processats

    print('Capturant publicacions...')

    if(manual):
        (r, db) = utils.rwlogin()       # connexió amb l'API i la BBDD 

    try:
        # Es fa una consulta per capturar els noms dels subreddits
        select = db.cur.execute('SELECT display_name FROM subreddits ORDER BY subscribers ' + 
                                'DESC LIMIT %s;' % TOP_SUB_LIMIT)

        if (select == TOP_SUB_LIMIT):           # s'han capturat el nombre de noms esperat?
            subNames = db.cur.fetchall()        # es guarden els noms dels subreddits
        # Si la consulta retorna un valor diferent de l'esperat, es llença una excepció
        else:
            raise pymysql.MySQLError('S\'esperaven %d files i se n\'han extret %d'
                                     % (TOP_SUB_LIMIT, select))
            return

        # Es crea una llista amb els noms retornats per la consulta
        subList = []
        for subName in subNames:
            subList.append(subName[0])

        # Un a un, es processen tots els subreddits
        for subreddit in subList:
            (newposts, updates, subsCount) = get_all_posts(subreddit=subreddit, db=db, r=r, subsCount=subsCount, lower=START_DATE)
            totalNewposts += newposts
            totalUpdates += updates            

    except pymysql.MySQLError as e:
        text = ('getSubmissions:Select noms subreddits. Excepció: ' + str(e))
        utils.storeExcept(text, db.cur, db.con)     

    if(manual):
        db.con.close()
        del db.cur
        del db.con
        print('Connexió amb la BBDD tancada.')

    # Es mostren els resultats de la sessió
    utils.printSQLStats(None, totalNewposts, totalUpdates)

def get_all_posts(subreddit, db, r, subsCount, lower=None, maxupper=None, interval=GET_SUBS_INTERVAL):
    ''' Funció extreta de:

        https://github.com/voussoir/reddit/blob/master/Prawtimestamps/timesearch.py
        Autor: Voussoir

        Modificada per adaptar-la a les necessitats del projecte.

        Captura les publicacions del subreddit passat com a paràmetre. Es poden
        indicar els límits de dates inferiors i superiors, si no es fa, es capturen
        totes les publicacions del subreddit.

        :param subreddit: el nom del subreddit a explorar, com a cadena.
        :param db:
        :param r: 
        :param subsCount: int per comptar quants subreddits s'han processat
        :param lower: data inferior a partir de la que buscar. Format UNIX.
                      None - Per defecte, la data de creació del subreddit.
                      update - captura missatges del subreddit, a partir de
                      la data de l'últim capturat.
        :param maxupper: data superior. Per defecte, el present.
        :param interval: interval parcial en el que buscar publicacions.
                         La funció redueix o amplia aquest interval, segons
                         si troba més de 100 publicacions o menys de 75.

        :return: El nombre de noves publicacions i d'aquelles que s'hagin actualitzat
                 en cas de que ja existissin i el número de subreddit processat.
        :rtype: int, int, int
    '''
    MAXIMUM_EXPANSION_MULTIPLIER = 2
    queryNewposts = 0                   # Noves publicacions, valor parcial
    queryUpdates = 0                    # Publicacions actualitzades
    newposts = 0                        # Noves publicacions, total subreddit
    updates = 0                         # Publicacions actualizades
    offset = -time.timezone
    
    if lower == 'update':        
        # Seguirà capturant missatges, des de l'últim que hi hagi a la BBDD
        db.cur.execute("SELECT created_utc FROM posts WHERE subreddit like '%s' " +
                       "ORDER BY idstr DESC LIMIT 1;" % subreddit)
        row = cur.fetchone()
        if row:
            lower = row[0]              # [0], una sola columna demanada
        else:
            lower = None

    if lower is None:
        # La data mínima per començar a capturar missatges
        # serà la de la creació del subreddit
        lower = r.get_subreddit(subreddit).created_utc

    if maxupper is None:
        nowstamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        maxupper = nowstamp

    lower -= offset                     # Ajust dels valors a la zona horaria
    maxupper -= offset
    upper = lower + interval            # Interval - Tall per sobre
    itemcount = 0

    toomany_inarow = 0
    while lower < maxupper:
        text = ' Subreddit: {0} ({1} de {2}) '.format(subreddit, subsCount, TOP_SUB_LIMIT)
        print(text)
        print(len(text) * '-')
        print('Current interval:', utils.s2hms(interval))
        print('Lower', utils.human(lower), lower)
        print('Upper', utils.human(upper), upper)
        while True:
            try:
                query = 'timestamp:%d..%d' % (lower, upper)
                searchresults = list(r.search(query, subreddit=subreddit, sort='new', limit=100, syntax='cloudsearch'))
                break
            except:
                text = ('get_all_posts:r.search. Excepció: ' + str(e))
                utils.storeExcept(text, db.cur, db.con)                
                print('\nException: {0}, resuming in 5...\n'.format(e))
                time.sleep(5)
                continue
        #Fi while True

        searchresults.reverse()
        # La següent línia mostra els ids de les publicacions capturades,
        # la comento per evitar saturar la línia de comandos amb text.
        # print([i.id for i in searchresults])

        itemsfound = len(searchresults)
        itemcount += itemsfound
        print('Found', itemsfound, 'items')

        # El següent codi computa el nombre de publicacions trobades en l'interval
        # de temps utilitzat, si són més de 99 (reddit limita a 100) o menys de
        # 75 (per optimitzar les consultes), modifica l'interval i torna a cercar.
        # Quan troba un nombre de publicacions acceptable, les introdueix a la
        # base de dades.

        if itemsfound < 75:
            print('Too few results, increasing interval')
            diff = (1 - (itemsfound / 75)) + 1
            diff = min(MAXIMUM_EXPANSION_MULTIPLIER, diff)
            interval = int(interval * diff)
        if itemsfound > 99:
            #Intentionally not elif
            print('Too many results, reducing interval')
            interval = int(interval * (0.8 - (0.05*toomany_inarow)))
            upper = lower + interval
            toomany_inarow += 1
        else:
            lower = upper
            upper = lower + interval
            toomany_inarow = max(0, toomany_inarow-1)
            (queryNewposts, queryUpdates) = utils.smartinsert(db.con, db.cur, searchresults, MIN_SCORE)
            newposts += queryNewposts
            updates += queryUpdates
        print()
    #Fi while lower < maxupper

    utils.printSQLStats(subreddit, newposts, updates)
    return(newposts, updates, subsCount+1)

if (__name__ == '__main__'):
    start()
