#!/usr/bin/env python

#################################################################################
#
#   Bot per extreure informacio de la base de dades de reddit, fent us de la
#   seva API.
#
#   Data creacio:           20/03/2016
#   Última modificació:     25/04/2016
#
#   @ Autor: Ramon Royo
#            Treball de fi de grau (UOC)
#
#   @ Fonts consultades:
#
#   Documentacio Python 3
#   https://docs.python.org/3/
#
#   Writing a reddit bot - 02 - Writing ReplyBot (UPDATED)
#   https://www.youtube.com/watch?v=keiATJcZE8g
#
#   PRAW documentation
#   https://praw.readthedocs.org/en/stable/
#
#   Stackoverflow - Multiples consultes
#   http://stackoverflow.com
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
#     amb mes subscriptors.
#
#       >999  punts   0,94% de les publicacions (11591)
#       >1999 punts   0,71% de les publicacions (8678)
#       >2999 punts   0,52% de les publicacions (6438)
#       >3999 punts   0,30% de les publicacions (3664)
#       >4999 punts   0,10% de les publicacions (1217)
#
#################################################################################

import utils                                # Funcions d'us comu
import praw                                 # Wrapper API reddit
import pymysql                              # Per interactuar amb la BBDD
import time
import datetime

SUB_LIMIT = 2000000                         # Subreddits capturats com a maxim amb getSubreddits()
UPDATE_SUBREDDITS = 2000                    # Quan ja s'han capturat TOTS els subreddits, tan sols s'actualitzen els subscriptors
                                            # d'un nombre determinat dels que mes en tenen, aquesta variable estableix el limit.
TOP_SUB_LIMIT = 500                         # Subreddits dels que s'extreuen publicacions

MAX_SUBMISSIONS = 100                       # Limit de publicacions capturades en una sola peticio a l'API
BELOW_MAX_SUBMISSIONS = 75                  # Es necessita capturar un minim de pubs per optimitzar el proces
MIN_SCORE = 500                             # Puntuacio minima per incloure una publicacio a la BBDD

UPDATE_WAIT = ( 3 * 24 * 3600 )             # Temps d'espera en segons, entre actualitzacions de la BBDD, 3 dies
                                            # En producció, caldrà revisar aquest temps d'espera, per saber si és excessiu.
WAIT_FRACTION = ( 2 * 3600 )                # Fraccio de temps que es tarda en enviar un missatge que anuncia que
                                            # s'està esperant per començar una nova iteració.

START_DATE = None                           # Data a partir de la qual comencar a capturar publicacions
                                            #   None, capturara totes les publicacions des de l'inici del subreddit
                                            #   O be des de la data de l'ultima captura
                                            #   31536000 equival a un any en segons
MAX_UPPER = None                            # Data final, fins on capturar publicacions (fixada dintre de start())
GET_SUBS_INTERVAL = 3600                    # Interval de temps inicial per capturar publicacions

MAXIMUM_EXPANSION_MULTIPLIER = 2            # Limit segur per seleccionar intervals per sota

validRequests = 0                           # Nombre total de crides que retornen entre 1 i 99 publicacions
belowRequests = 0                           # Nombre total de crides que retornen menys de 75 publicacions
aboveRequests = 0                           # Nombre total de crides que retornen mes de 99 publicacions
totalSubmissions = 0                        # Nombre total de publicacions emmagatzemades a la BBDD
totalRounds = 1                             # Nombre total d'iteracions del bucle de start()
absoluteStartTime = time.time()             # Temps en que s'inicia el script

def start():
    ''' Controla el funcionament del bot. Crida a les funcions que capturen els noms
        dels subreddits, extreu les publicacions i ho emmagatzema tot en una base de
        dades.
    '''
    global totalRounds, MAX_UPPER
    subredditsUpdated = True            # Recull que la funció getSubreddits faci bé la feina

    while True:
        # Data i hora final fins on capturar publicacions. L'offset en segons.
        # Per defecte, 2 dies abans del moment en que comença la iteració
        # per donar temps a que les publicacions obtinguin vots.
        MAX_UPPER = time.time() - ( 2 * 24 * 3600 )

        (r, db) = utils.rwlogin()       # Connecta amb l'API i la BBDD

        print('Consultant el nombre de subreddits emmagatzemats')

        if (db.cur.execute('SELECT count(*) FROM subreddits')):
            storedSubreddits = db.cur.fetchone()[0]
        else:
            storedSubreddits = 0

        print('Hi han {0} subreddits.'.format(storedSubreddits))

        # Hi han més de 700.000 subreddits dintre de la llista que proporciona
        # la funció get_popular_subreddits(), si es supera aquesta xifra,
        # vol dir que s'ha emmagatzemat tots el que poden interessar.
        while subredditsUpdated:
            if (storedSubreddits < 700000):
                # Omple la taula de subreddits (~3h de durada)
                subredditsUpdated = getSubreddits(False, False, r, db)
            else:
                # Actualitza la taula de subreddits (~30min)
                subredditsUpdated = getSubreddits(False, True, r, db)

        # Explora publicacions dels subreddits seleccionats
        getSubmissions(False, r, db)

        # Es tanquen les connexions
        db.con.close()
        del db.cur
        del db.con
        print('Connexions tancades.')

        totalRounds += 1

        #S'espera un temps determinat, per realitzar la propera iteracio
        utils.updateWait(UPDATE_WAIT, WAIT_FRACTION)

def getSubreddits(manual=True, updateTop=False, r=None, db=None):
    ''' Extreu informacio de la pagina http://www.reddit.com/reddits
        Concretament extreu una llista amb tots els subreddits i el nombre de
        subscriptors, entre d'altres dades i ho guarda tot en una taula SQL
        anomenada 'subreddits'. Si el subreddit ja existeix a la taula, s'actualitza
        el nombre de subscriptors.

        us, s'importa i es crida a la funcio get_subreddits, aquesta crida es pot
        fer de dues maneres:

        Des de la linia de comandos -> getSubreddits()
        Des de l'script principal   -> getSubreddits(False, r, db)

        En el primer cas, es connecta a l'API i a la BBDD i en el segon, se li passen
        les connexions ja creades.

        Si com a updateTop es passa True, l'unic que fara sera cercar els 1000 getSubreddits
        amb mes subscriptors i actualizar-ne el nombre.

        :param manual: True o False (opcional)
        :param updateTop:  True o False (opcional)
        :param r: class 'praw.Reddit' (opcional)
        :param db: class 'utils.baseDades' (opcional)

        :return: False si no hi han hagut problemes, True si cal repetir el procés de captura.
        :rType: Boolean
    '''

    startTime = time.time()             # per calcular el temps que es tarda
    newSubs = 0                         # per portar el compte dels subreddits processats
    updatedSubs = 0
    totalSubs = 0

    # En teoria els noms dels subreddits han de ser unics, pero he detectat un
    # subreddit amb el nom duplicat. El descarto, ja que dona problemes.
    discarted = ('ColumbusBlueJackets')

    # Si es fa una crida manual a la funcio (per defecte), es connecta a la BBDD
    # i a l'API. Aixi diferencia entre les crides des de la linia de comandos i
    # les crides des de l'script principal, on ja s'haura fet una connexio.
    if manual:
        (r, db) = utils.rwlogin()       # connexio amb l'API i la BBDD

    if not updateTop:
        subreddits = r.get_popular_subreddits(limit=SUB_LIMIT)
        print('Capturant subreddits...')
    else:
        db.cur.execute('SELECT display_name FROM subreddits ORDER BY subscribers DESC LIMIT {0}'.format(UPDATE_SUBREDDITS))
        subredditsNames = db.cur.fetchall()
        subreddits = []

        print('Actualitzant els subscriptors dels {0} subreddits mes poblats...'.format(UPDATE_SUBREDDITS))

        for name in subredditsNames:
            # Es crea una llista amb objecte PRAW de subreddits, fent servir el nom dels subreddits
            subreddits.append(r.get_subreddit(name[0]))

    # Es recorre el contingut
    try:
        for subreddit in subreddits:
            # Comprova que el subreddit no existeixi ja a la base de dades
            if not (db.cur.execute("SELECT 1 FROM subreddits WHERE idstr = '{0}' LIMIT 1".format(subreddit.id))):
                # Comprova si es un dels 'errors' de reddit, un subreddit amb nom duplicat
                if (subreddit.display_name not in discarted):
                    # Si no existeix i no es un duplicat es crea una nova fila a la BBDD
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

            # Actualitza la taula on es guarden els canvis en el nombre de subscriptors
            if (subreddit.display_name not in discarted):
                db.cur.execute('INSERT INTO subscribers (idsub, subscribers) VALUES({0},{1})'.format(utils.b36(subreddit.id), subreddit.subscribers))

            totalSubs = newSubs + updatedSubs

            # Cada X subreddits, es fa un commit a la BBDD
            if not (totalSubs % 100):
                db.con.commit()
                print('Últim subreddit processat: %s. Total processats: %s' % (subreddit.id, totalSubs))
        # Fi for subreddit in subreddits
    except Exception as e:
        text = 'getSubreddits():Actualització: {4}\nSubreddit on ha fallat: {2} ({3})\nEXCEPCIO: {0}\nMISSATGE: {1}'.format(
                e.__doc__, str(e), subreddit.display_name, subreddit.id, updateTop)
        utils.storeExcept(text, db.cur, db.con)

        if(manual):
            db.con.close()
            del db.cur
            del db.con
            print('Connexio amb la BBDD tancada.')

        print(text)
        return(True)                    # Problemes capturant subreddits, es repeteix el procés

    db.con.commit()                     # Un últim commit per assegurar que la resta de 50, vagi tambe a la BBDD

    if(manual):
        db.con.close()
        del db.cur
        del db.con
        print('Connexio amb la BBDD tancada.')

    # Mostra el temps que ha tardat en total
    utils.printGetSubredditsStats(startTime, newSubs, updatedSubs)
    return False                        # No hi ha problemes, es segueix amb la captura de le spublicacions

def getSubmissions(manual=True, r=None, db=None):
    ''' Captura un nombre de subreddits determinat per TOP_SUB_LIMIT i ordenats per nombre
        de subscriptors. Despres un a un, en captura les publicacions.

        :param manual: True o False (opcional)
        :param r: class 'praw.Reddit' (opcional)
        :param db: class 'utils.baseDades' (opcional)

        :return: El nombre de publicacions noves i actualitzades
        :rtype: str i str
    '''
    totalNewposts = 0                   # Nombre total de missatges nous afegits (sessio)
    totalUpdates = 0                    # Nombre total de missatges actualitzats (sessio)
    newposts = 0                        # Nombre missatges nous (subreddit)
    updates = 0                         # Nombre missatges actualitzats (subreddit)
    subsCount = 1                       # Comptador per saber els subreddits processats
    totalTime = 0

    print('Capturant publicacions...\n')

    if(manual):
        (r, db) = utils.rwlogin()       # connexio amb l'API i la BBDD

    try:
        # Es fa una consulta per capturar els ids i noms dels subreddits
        select = db.cur.execute('SELECT idint, display_name FROM subreddits ORDER BY subscribers ' +
                                'DESC LIMIT {0}'.format(TOP_SUB_LIMIT))

        if (select == TOP_SUB_LIMIT):           # s'han capturat el nombre de noms esperat?
            subreddits = db.cur.fetchall()      # es guarden els noms dels subreddits
        # Si la consulta retorna un valor diferent de l'esperat, es llenca una EXCEPCIO
        else:
            raise pymysql.MySQLError('S\'esperaven {0} files i se n\'han extret {1}'.format(
                                     (TOP_SUB_LIMIT, select)))

        # Un a un, es processen tots els subreddits
        for subreddit in subreddits:
            subredditSubmissions = utils.getNumberSubmissions(subreddit[0], db)

            (newposts, updates, subsCount, submissionsChrono) = get_all_posts(
                                                  subredditSubmissions,
                                                  idint=subreddit[0],
                                                  subreddit=subreddit[1],
                                                  db=db,
                                                  r=r,
                                                  subsCount=subsCount
                                                  )
            totalNewposts += newposts
            totalUpdates += updates
            totalTime += submissionsChrono

    except pymysql.MySQLError as e:
        text = 'getSubmissions():Select noms subreddits\n{2}\nEXCEPCIO: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e), e)
        utils.storeExcept(text, db.cur, db.con)
        print(text)
        raise SystemExit                # Es surt

    if(manual):
        db.con.close()
        del db.cur
        del db.con
        print('Connexio amb la BBDD tancada.')

    # Es mostren els resultats de la sessio
    utils.printSQLStats(None, totalNewposts, totalUpdates, time=totalTime)

def get_all_posts(subredditSubmissions, idint, subreddit, db, r, subsCount, lower=START_DATE,
                  maxupper=MAX_UPPER, interval=GET_SUBS_INTERVAL):
    ''' Funcio extreta de:

        https://github.com/voussoir/reddit/blob/master/Prawtimestamps/timesearch.py
        Autor: Ethan Dalool (Voussoir)

        Modificada per adaptar-la a les necessitats del projecte.

        Captura les publicacions del subreddit passat com a parametre. Es poden
        indicar els limits de dates inferiors i superiors, si no es fa, es capturen
        totes les publicacions del subreddit.

        :paran idint: l'id en base 10 del subreddit
        :param subreddit: el nom del subreddit a explorar, com a cadena.
        :param db: objecte baseDades
        :param r: objecte PRAW
        :param subsCount: int per comptar quants subreddits s'han processat
        :param lower: data inferior a partir de la que buscar. Format UNIX.
                      None - Per defecte, la data de creacio del subreddit.
                      update - captura missatges del subreddit, a partir de
                      la data de l'ultim capturat.
        :param maxupper: data superior. Per defecte, el present.
        :param interval: interval parcial en el que buscar publicacions.
                         La funcio redueix o amplia aquest interval, segons
                         si troba mes de 100 publicacions o menys de 75.
        :param subredditSubmissions: nombre de publicacions en el moment de comencar a
                                     actualitzar.

        :return: El nombre de noves publicacions i d'aquelles que s'hagin actualitzat
                 en cas de que ja existissin i el numero de subreddit processat. Com a
                 quart valor, retorna els segons transcorreguts.
        :rtype: int, int, int, float
    '''
    chrono = 0
    queryNewposts = 0                   # Noves publicacions, valor parcial
    queryUpdates = 0                    # Publicacions actualitzades, valor parcial
    newposts = 0                        # Noves publicacions, total subreddit
    updates = 0                         # Publicacions actualitzades, total subreddit
    offset = -time.timezone             # Compensacio per la zona horaria
    startTime = time.time()             # Temps d'inici de captura de les publicacions
    global validRequests                # Nombre total de crides que retornen entre 1 i 99 publicacions
    global belowRequests                # Nombre total de crides que retornen menys de 75 publicacions
    global aboveRequests                # Nombre total de crides que retornen mes de 99 publicacions
    global totalSubmissions             # Nombre total de publicacions emmagatzemades a la BBDD
    global totalRounds                  # Nombre total d'iteracions del bucle de start()

    # Inicialment es comprova si lower te algun valor. En cas afirmatiu es mantindra
    # aquest valor. En cas de que sigui None, es captura la data de finalitzacio de
    # l'ultima exploracio en aquest subreddit. Si no existeix tal data, no es modifica
    # lower, que seguira sent None. En cas contrari, se li assigna la data.
    if lower is None:
        # Seguira capturant missatges, des de l'ultim que s'hagi trobat durant la
        # ultima iteracio del script.
        lastDate = utils.getLastDate(idint, db)

        if lastDate:
            lower = lastDate + 1        # Última data on es va finalitzar en una iteració
                                        # anterior, més un segon

    # Es comprova de nou si lower és None, en cas de ser-ho se li assigna
    # la data de creacio del subreddit a explorar.
    if lower is None:
        # La data minima per comencar a capturar missatges
        # sera la de la creacio del subreddit
        lower = r.get_subreddit(subreddit).created_utc

    if maxupper is None:
        nowstamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        maxupper = nowstamp

    maxupper -= offset                  # Ajust del valor a la zona horaria
    upper = lower + interval            # Interval - Tall per sobre
    itemcount = 0

    toomany_inarow = 0                  # Modifica la velocitat en que es varien els intervals
    intervalDiff = 0                    # Per mostrar la diferencia entre interval present i anterior
                                        # Comença com un int, acaba com una cadena
    while (lower < maxupper):
        while True:                     # Cerca de publicacions dintre d'un interval
            try:
                query = 'timestamp:%d..%d' % (lower, upper)
                searchresults = list(r.search(query, subreddit=subreddit, sort='new',
                                        limit=MAX_SUBMISSIONS, syntax='cloudsearch'))
                break
            except Exception as e:
                text = 'get_all_posts():r.search. Query: {2}\nEXCEPCIO: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e), query)
                utils.storeExcept(text, db.cur, db.con)
                time.sleep(5)
                continue
        #Fi while True

        searchresults.reverse()
        itemsfound = len(searchresults)
        itemcount += itemsfound

        # El seguent codi computa el nombre de publicacions trobades en l'interval
        # de temps utilitzat, si son mes del valor MAX_SUBMISSIONS o menys del
        # 75% d'aquest, modifica l'interval i torna a cercar.
        # Quan troba un nombre de publicacions acceptable, les introdueix a la
        # base de dades.
        # La variable toomany_inarow ajuda a accelerar la modificacio de l'interval,
        # en cas de que es produeixin diversos casos seguits en que s'obtinguin
        # massa resultats.

        # Valors utilitzats per imprimir les estadistiques de cada iteracio
        printInterval = interval
        printLower = lower
        printUpper = upper
        textResults = ''

        if (itemsfound < BELOW_MAX_SUBMISSIONS):
            diff = 2 - (itemsfound / BELOW_MAX_SUBMISSIONS)
            diff = min(MAXIMUM_EXPANSION_MULTIPLIER, diff)
            interval = int(interval * diff)
            belowRequests += 1
        if (itemsfound > (MAX_SUBMISSIONS - 1)):
            # Intencionalment no elif.
            # En cas d'obtenir pocs resultats, es guarden igualment amb l'else.
            interval = int(interval * (0.8 - (0.05 * toomany_inarow)))
            toomany_inarow += 1
            aboveRequests += 1
        else:
            (queryNewposts, queryUpdates, subredditSubmissions) = utils.smartinsert(
                db.con, db.cur, searchresults, idint, MIN_SCORE, subredditSubmissions)
            # Es guarda l'ultima data, quan cerqui fins al present,
            # la data correspondrà a MAX_UPPER
            utils.storeLastDate(idint, upper, db)
            lower = upper
            toomany_inarow = max(0, toomany_inarow-1)
            newposts += queryNewposts
            updates += queryUpdates
            validRequests += 1
            totalSubmissions += itemsfound

        # Titol del subreddit i comptador de temps
        textSubreddit = ' Subreddit: {0} ({1} de {2}). Iteracio: {3} '.format(subreddit,
            subsCount, TOP_SUB_LIMIT, totalRounds)
        chrono = time.time() - startTime
        absChrono = time.time() - absoluteStartTime

        #Mostra informacio de cada peticio
        utils.gapStats(textSubreddit, chrono, printInterval, intervalDiff, printLower,
                       printUpper, validRequests, totalSubmissions, itemsfound,
                       belowRequests, aboveRequests, MAX_SUBMISSIONS,
                       BELOW_MAX_SUBMISSIONS, absChrono, absoluteStartTime)

        upper = lower + interval

        # Upper no pot ser superior a maxupper o la variable que guarda el nombre
        # total de posts, serà erronia. Si s'executa l'if, s'esta cercant a l'ultim
        # interval, abans de la data i hora fixades com a límit màxim.
        if (upper > maxupper):
            upper = maxupper

        intervalDiff = printInterval - interval

        print()
    #Fi while lower < maxupper

    utils.printSQLStats(subreddit, newposts, updates, time=None)
    return(newposts, updates, subsCount+1, chrono)

if (__name__ == '__main__'):
    start()
