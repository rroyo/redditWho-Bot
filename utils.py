#################################################################################
#
#   Script amb diferents funcions utils i d'us comu.
#
#   Data creacio:           24/03/2016
#   ultima modificacio:     15/04/2016
#
#   @ Autor: Ramon Royo
#            Treball de fi de grau (UOC)
#
#   @ Fonts consultades:
#
#   PyMySQL documentation
#   https://github.com/PyMySQL/PyMySQL#pymysql
#
#   PRAW and OAUTH
#   http://praw.readthedocs.org/en/stable/pages/oauth.html
#
#   Using % and .format() for great good!
#   https://pyformat.info/
#
#################################################################################

import logindata
from urllib import parse
import time, datetime, praw, pymysql, re

class baseDades(object):
    ''' Classe retornada pel metode dblogin()

        :atributtes: objecte amb dos atributs
        :atype: pymysql.connections.Connection object
        :atype: pymysql.cursors.Cursor object
    '''
    def __init__(self, connection, cursor):
        self.con = connection
        self.cur = cursor

def dblogin():
    ''' Per connectar amb la base de dades

        :return: connexio amb la BBDD
        :rtype: pymysql.connections.Connection object
        :rtype: pymysql.cursors.Cursor object
    '''
    try:
        connection = pymysql.connect(host = logindata.DB_HOST,
                                     user = logindata.DB_USER,
                                     password = logindata.DB_PASS,
                                     db = logindata.DB_NAME,
                                     use_unicode = True,
                                     charset='utf8mb4')

        cursor = connection.cursor()

        # S'usa la BBDD on es guarda tot el contingut
        cursor.execute('USE '+ logindata.DB_NAME +';')

        print('Connexio amb la base de dades correcta.')
        return baseDades(connection, cursor)

    except pymysql.OperationalError as e:
        print('Error connectant amb la base de dades: ' + str(e))

def oauth2():
    ''' Connecta amb l'API de Reddit. Cal tenir un token de refresc,
        generat amb el script oauth_token.py.

        :return: una connexio amb l'API de reddit
        :rtype: praw.Reddit object
    '''
    print('Connectant amb l\'API de reddit.')
    r = praw.Reddit(logindata.APP_UA)                       # Nova instancia de reddit
    r.set_oauth_app_info(logindata.APP_ID,                  # OAuth2 login
                logindata.APP_SECRET, logindata.APP_URI)
    r.refresh_access_information(logindata.APP_REFRESH)     # Refresc del token
    print('Connexio amb l\'API correcta. '
          'Connectat com a ' + str(r.user) + '.')
    return r

def rwlogin():
    ''' Connecta amb la BBDD i l'API

    :return: Connexio amb l'API de reddit i amb la BBDD
    :rtype: praw.Reddit object
    :rtype: dblogin.baseDades
    '''
    # Per assegurar que s'estableix una connexio amb l'API, es comproven 3 condicions
    # si r esta definida, si r es instancia de praw.Reddit i si r conte una connexio Oauth2
    while True:
        if(('r' not in locals()) or (not isinstance(r, praw.Reddit)) or (not(r.is_oauth_session()))):
            r = oauth2()                # Instancia de reddit
        else:
            break                       # es compleixen les 3 condicions, es trenca el bucle

    # Igual que l'anterior, comprovacions per assegurar una connexio correcta
    while True:
        if(('db' not in locals()) or (not isinstance(db, baseDades))):
            db = dblogin()              # Instancia de la BBDD
        else:
            break
    return(r, db)

def s2dhms(seconds):
    ''' Formata segons a d:hh:mm:ss

    :param seconds: nombre de segons

    :return: dies, hores, minuts i segons
    :rtype: str
    '''
    if (isinstance(seconds, float)):
        seconds = int(seconds)

    if (isinstance(seconds, int)):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        dhms = {'days': d, 'hours': h, 'minutes': m, 'seconds': s}

        return('{days}d:{hours:02d}h:{minutes:02d}m:{seconds:02d}s'.format(**dhms))
    else:
        print('s2dhms: es necessita un int o float (representant segons) per fer la conversio')
        return

def chrono(startTime):
    ''' Retorna el temps transcorregut des del temps inicial passat

    :param startTime: segons des del EPOCH

    :return: hores, minuts i segons
    :rtype: str
    '''
    if (isinstance(startTime, (int, float))):
        interval = int(time.time()) - startTime
        return(s2dhms(interval))
    else:
        print('chrono: es necessita un int o float (segons des del EPOCH) per calcular el temps transcorregut')
        return

def printSQLStats(str, newposts, updates, time):
    ''' Imprimeix el nombre de publicacions processades

        :param str: el titol del bloc a imprimir
        :param newposts: el nombre de publicacions noves afegides a la BBDD
        :param updates: el nombre de publicacions actualitzades
        :param time: el temps de durada
    '''
    if (str != None):
        text = ' Subreddit: {0} '.format(str)
    else:
        text = ' Valors sessio '

    print(len(text) * '-')
    print(text)
    print(len(text) * '-')
    if(time != None):
        print('Durada total:', s2dhms(time))
    print('Noves:', newposts)
    print('Actualitzades:', updates)
    print()

def printGetSubredditsStats(startTime, new, updated):
    ''' Imprimeix el nombre de subreddits afegits a la BBDD
        i el temps que s'ha tardat.

        :param startime: el temps en que s'ha iniciat el proces, format UNIX
        :param new: el nombre de subreddits nous afegits a la BBDD
        :param updated: el nombre de subreddits actualitzats
    '''
    print()
    text = ' getSubreddits '
    print(text)
    print(len(text) * '-')
    print('Temps total:', chrono(startTime))
    print('Nous:', new)
    print('Actualitzats:', updated)
    print()

def storeExcept(e, cur, con):
    ''' Guarda l'excepcio passada a la base de dades

        :param e: el text amb la descripcio de l'excepcio
    '''
    try:
        error = re.escape(str(e))
        query = 'INSERT INTO excepts (description) VALUES("{0}")'.format(error)
        cur.execute(query)
        con.commit()
    except pymysql.MySQLError as e:
        text = 'storeExcept(). \nEXCEPCIo: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e))
        print(text)
        print(human(time.time()))
        # Intencionadament es surt, no s'hauria d'haver arribat aqui, s'ha produit algun error greu
        # i no es poden emmagatzemar les excepcions i segurament cap altra dada.
        # Per futures modificacions, intentare tenir en compte totes les possibles situacions i
        # eliminare la sortida del script.
        raise SystemExit

def updateWait(wait, waitFraction):
    ''' Espera un temps determinat i ho anuncia cada x minuts.

        :param wait: El temps total a esperar, en format UNIX.
        :param waitFraction: El temps que passa entre cada anunci.
    '''
    while wait >= 0:
        print('Falten {0} per la propera iteracio'.format(s2dhms(wait)))
        wait -= waitFraction
        time.sleep(waitFraction)
    print()

def gapStats(textSubreddit, chrono, printInterval, intervalDiff, printLower, printUpper,
             validRequests, totalSubmissions, itemsfound, belowRequests, aboveRequests,
             MAX_SUBMISSIONS, BELOW_MAX_SUBMISSIONS, absChrono, absoluteStartTime):
    ''' Mostra informacio sobre cada peticio de publicacions, durada, publicacions capturades,
        limits i interval, etc.
    '''
    optimalRequests = validRequests - belowRequests
    totalRequests = validRequests + aboveRequests

    if totalRequests == 0:
        totalRequests = 1

    percentOptimal = optimalRequests / totalRequests * 100
    percentBelow = belowRequests / totalRequests * 100
    percentAbobe = aboveRequests / totalRequests * 100

    if validRequests == 0:
        mitjana = 0
    else:
        mitjana = int(totalSubmissions/validRequests)

    if (intervalDiff > 0):
        intervalDiffSign = '-'
    else:
        intervalDiffSign = '+'

    print(textSubreddit)
    print(len(textSubreddit) * '-')
    print('Temps subreddit: {0}. Temps absolut: {1}. Iniciat: {2}'.format(s2dhms(chrono), s2dhms(absChrono), human(absoluteStartTime)))
    print('Interval: {0} ({1}{2})'.format(s2dhms(printInterval), intervalDiffSign,
                                          s2dhms(abs(intervalDiff))))
    print('Data inferior:', human(printLower), printLower)
    print('Data superior:', human(printUpper), printUpper)
    print()
    print('Peticions segons el nombre de publicacions obtingudes.')
    print('**{7} a {6}**: {0} ({3:.1f}%). **<75**: {1} ({4:.1f}%). **>99**: {2} ({5:.1f}%)'.format(optimalRequests,
        belowRequests, aboveRequests, percentOptimal, percentBelow, percentAbobe, (MAX_SUBMISSIONS-1), BELOW_MAX_SUBMISSIONS))
    print('Mitjana de publicacions guardades:', mitjana)

    if (itemsfound > (MAX_SUBMISSIONS-1)):
        print('S\'han trobat', itemsfound, 'publicacions o mes, reduint interval.')
    elif (itemsfound < BELOW_MAX_SUBMISSIONS):
        print('S\'han trobat', itemsfound, 'publicacions, incrementant interval.')
        print('Guardant publicacions')
    else:
        print('S\'han trobat', itemsfound, 'publicacions.')
        print('Guardant publicacions')

def getDomain(url):
    ''' Retorna el domini de la URL passada

        :param url: l'adreca

        :return: retorna el domini
        :rType: str
    '''
    return parse.urlparse(url)[1]

def getNumberSubmissions(idint, db):
    ''' Retorna el nombre de publicacions d'un subreddit

        :param idint: id en base 10 del subreddit

        :return: el nombre de publicacions o None si es produeix una excepcio
        :rType: int o None
    '''
    try:
        rows = db.cur.execute('SELECT submissions FROM subreddits WHERE idint={0} LIMIT 1'.format(idint))

        if (rows):
            return db.cur.fetchone()[0]
        else:
            return 0

    except pymysql.MySQLError as e:
        text = 'getNumberSubmissions(). \nEXCEPCIo: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e))
        storeExcept(text, db.cur, db.con)
        # Intencionadament es surt, no s'hauria d'haver arribat aqui. es preferible sortir, a
        # que es pugui modificar erroniament el valor que recull el nombre total de publicacions.
        raise SystemExit

def storeLastDate(idint, lastDate, db):
    ''' Emmagatzema la data de l'ultima publicacio trobada per get_all_posts()

        :param idint: id en base 10 del subreddit
        :param lastDate: data en format UNIX i zona horaria UTC, de la ultima publicacio
        :db: objecte baseDades
    '''

    try:
        lastDate = int(lastDate)

        db.cur.execute('SELECT * FROM latestposts WHERE idsub={0} LIMIT 1'.format(idint))

        if db.cur.fetchone():
            db.cur.execute('UPDATE latestposts SET lastDateUTC = {0} WHERE idsub={1}'.format(lastDate, idint))
        else:
            db.cur.execute('INSERT INTO latestposts (idsub, lastDateUTC) VALUES({0}, {1})'.format(idint, lastDate))

        db.con.commit()
    except pymysql.MySQLError as e:
        text = 'storedLastDate(). Subreddit: {2}. Data no guarda: {3}\nEXCEPCIo: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e), idint, lastData)
        storeExcept(text, db.cur, db.con)

def getLastDate(idint, db):
    ''' Retorna la data de l'ultima publicacio guardada del subreddit passat

        :param idint: id en base 10 del subreddit
        :db: objecte baseDades

        :return: data en format UNIX
        :rType: int
    '''
    rows = db.cur.execute('SELECT lastDateUTC FROM latestposts WHERE idsub={0} LIMIT 1'.format(idint))

    if rows:
        return db.cur.fetchone()[0]
    else:
        return 0

###################################################################################
# Les seguents funcions han estat extretes del seguent script:
#
# https://github.com/voussoir/reddit/blob/master/Prawtimestamps/timesearch.py
#
# Autor: Voussoir
###################################################################################
def b36(i):
    ''' Transforma de base 36 a base 10 i a la inversa

        :param i: Cadena o nombre sencer

        :return: El valor rebut transformat
        :rtype: int o str
    '''
    if type(i) == int:
        return base36encode(i)
    if type(i) == str:
        return base36decode(i)

    print('b36: es necessita un int per fer la conversio')
    return 0

def base36decode(number):
    ''' Converteix una cadena en base 36 a base 10

        :param number: Cadena en base 36

        :return: Retorna la cadena convertida
        :rtype: int
    '''
    return int(number, 36)

def base36encode(number, alphabet='0123456789abcdefghijklmnopqrstuvwxyz'):
    ''' Converteix un nombre sencer a una cadena en base 36

        :param number: Nombre sencer
        :param alphabet: Caracters usats en la conversio (OPCIONAL)

        :return: El nombre sencer convertit a base 36
        :rtype: str
    '''
    base36 = ''
    sign = ''
    if number < 0:
        sign = '-'
        number = -number
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign + base36

def human(timestamp):
    ''' Transforma del format de data UNIX al format retornat per
        time.time() i aquest el reformata de nou.

        Exemple:

            time.time()   -> 1459629617.0604663
            primera conv. -> 2016-04-02 20:40:17.060466
            ultima conv.  -> Apr 02 2016 20:40:17

        :param timestamp: la data i hora retornats per time.time()

        :return: la data i hora convertits
        :rtype: str
    '''
    x = datetime.datetime.utcfromtimestamp(timestamp)
    x = datetime.datetime.strftime(x, "%b %d %Y %H:%M:%S")
    return x

def smartinsert(con, cur, results, idint, MIN_SCORE, subredditSubmissions):
    ''' La funcio original ha estat modificada, per adaptar-la a les
        necessitats del projecte.

        Insereix els valors passats a la base de dades
        Si ja existeixen, actualitza el nombre de vots i de comentaris

        :param con: pymysql.connections.Connection object
        :param cur: pymysql.cursors.Cursor object
        :param results: una llista d'objectes praw.objects.Submission
        :param idint: id del subreddit en base 10
        :param MIN_SCORE: puntuacio minima de la publicacio per ser inclosa a la BBDD
        :param subredditSubmissions: nombre total de publicacions al subreddit

        :return: el nombre de publicacions noves afegides i les acualitzades
        :rtype: int, int
    '''
    newposts = 0                        # Comptabilitzen pubs noves i actualitzades
    updates = 0

    for o in results:
        cur.execute("SELECT * FROM posts WHERE idstr='{0}' LIMIT 1".format(o.id))

        if not cur.fetchone():          # Nova publicacio a la BBDD
            # Reddit te un bug, en que si l'autor d'una publicacio s'ha esborrat,
            # es produeix una excepcio al intentar recuperar-ne el nom.
            try:
                o.authorx = o.author.name
            except AttributeError:
                o.authorx = '[DELETED]'

            if (isinstance(o, praw.objects.Submission) and (o.score >= MIN_SCORE)):
                if o.is_self:
                    o.url = 'None'

                postdata = {
                    'idstr': o.id,
                    'idsub': idint,
                    'title': re.escape(o.title),
                    'author': o.authorx,
                    'subreddit': o.subreddit.display_name,
                    'score': o.score,
                    'ups': o.ups,
                    'downs': o.downs,
                    'num_comments': o.num_comments,
                    'is_self': o.is_self,
                    'domain': getDomain(o.url),
                    'url': con.escape_string(o.url),
                    'created_utc': int(o.created_utc),
                    'over18': o.over_18
                }

                try:
                    newposts += 1
                    query = """INSERT INTO posts (idstr, idsub, title, author, subreddit, score, ups, downs,
                               num_comments, is_self, domain, url, created_utc, over18)
                               VALUES('{idstr}', {idsub}, '{title}', '{author}', '{subreddit}', {score}, {ups},
                               {downs}, {num_comments},{is_self}, '{domain}', '{url}', {created_utc}, {over18})
                            """.format(**postdata)
                    cur.execute(query)
                except pymysql.MySQLError as e:
                    text = 'smartinsert:Insert. ID: {2}\nEXCEPCIo: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e), o.id)
                    storeExcept(text, cur, con)
                    pass
            #Fi if (isinstance(o, praw.objects.Submission)...

            subredditSubmissions += 1   # Nombre total de publicacions al subreddit

        #Fi if not cur.fetchone()

        else:                           # Actualitzacio d'una entrada existent
            updates += 1
            if isinstance(o, praw.objects.Submission):
                postdata = {
                    'idstr': o.id,
                    'score': o.score,
                    'num_comments': o.num_comments
                }
                try:
                    query = "UPDATE posts SET score = {score}, num_comments = {num_comments} WHERE idstr = '{idstr}' LIMIT 1".format(**postdata)
                    cur.execute(query)
                except pymysql.MySQLError as e:
                    text = 'smartinsert:Update. ID: {2}\nEXCEPCIo: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e), o.id)
                    storeExcept(text, cur, con)
                    pass
            #Fi if (isinstance(o, praw.objects.Submission)...
        #Fi else -> if not cur.fetchone()
    #Fi bucle for o in results

    # Just en aquest moment, tambe s'actualitzen el nombre de publicacions de la taula subreddits
    try:
        cur.execute("UPDATE subreddits SET submissions = {0} WHERE idint={1} LIMIT 1".format(subredditSubmissions, idint))

    except pymysql.MySQLError as e:
        text = 'smartinsert:Actualitzacio del nombre de publicacions. Nombre no guardat: {2}\nEXCEPCIo: {0}\nMISSATGE: {1}'.format(e.__doc__, str(e), subredditSubmissions)
        storeExcept(text, cur, con)

    con.commit()
    return (newposts, updates, subredditSubmissions)
