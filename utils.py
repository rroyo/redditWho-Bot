#################################################################################
#
#   Script amb diferents funcions útils i d'ús comú.
#
#   Data creació:           24/03/2016
#   Última modificació:     05/04/2016
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

from redditWhoLib import loginData
import time, datetime, praw, pymysql, re

class baseDades(object):
    ''' Classe retornada pel mètode dblogin()

        :atributtes: objecte amb dos atributs
        :atype: pymysql.connections.Connection object
        :atype: pymysql.cursors.Cursor object
    '''
    def __init__(self, connection, cursor):
        self.con = connection
        self.cur = cursor

def dblogin():
    ''' Per connectar amb la base de dades

        :return: connexió amb la BBDD
        :rtype: pymysql.connections.Connection object
        :rtype: pymysql.cursors.Cursor object
    '''
    try:
        connection = pymysql.connect(host = loginData.DB_HOST,
                                     user = loginData.DB_USER,
                                     password = loginData.DB_PASS,
                                     db = loginData.DB_NAME,
                                     use_unicode = True,
                                     charset='utf8mb4')
        
        cursor = connection.cursor()

        # S'usa la BBDD on es guarda tot el contingut
        cursor.execute('USE '+ loginData.DB_NAME +';')

        print('Connexió amb la base de dades correcta.')
        return baseDades(connection, cursor)

    except pymysql.OperationalError as e:
        print('Error connectant amb la base de dades: ' + str(e))

def oauth2():
    ''' Connecta amb l'API de Reddit. Cal tenir un token de refresc,
        generat amb el script oauth_token.py.

        :return: una connexió amb l'API de reddit
        :rtype: praw.Reddit object
    '''
    print('Connectant amb l\'API de reddit.')
    r = praw.Reddit(loginData.APP_UA)                       # Nova instància de reddit
    r.set_oauth_app_info(loginData.APP_ID,                  # OAuth2 login
                loginData.APP_SECRET, loginData.APP_URI)
    r.refresh_access_information(loginData.APP_REFRESH)     # Refresc del token
    print('Connexió amb l\'API correcta. '
          'Connectat com a ' + str(r.user) + '.')
    return r  

def rwlogin():
    ''' Connecta amb la BBDD i l'API

    :return: Connexió amb l'API de reddit i amb la BBDD
    :rtype: praw.Reddit object
    :rtype: dblogin.baseDades
    '''
    # Per assegurar que s'estableix una connexió amb l'API, es comproven 3 condicions
    # si r està definida, si r és instància de praw.Reddit i si r conté una connexió Oauth2
    while True:
        if(('r' not in locals()) or (not isinstance(r, praw.Reddit)) or (not(r.is_oauth_session()))):
            r = oauth2()                # Instància de reddit            
        else:
            break                       # es compleixen les 3 condicions, es trenca el bucle

    # Igual que l'anterior, comprovacions per assegurar una connexió correcta
    while True:
        if(('db' not in locals()) or (not isinstance(db, baseDades))):
            db = dblogin()              # Instància de la BBDD
        else:
            break
    return(r, db)

def s2hms(seconds):
    ''' Formata segons a h:mm:ss

    :param seconds: nombre de segons

    :return: hores, minuts i segons
    :rtype: str   
    '''
    if (isinstance(seconds, float)):
        seconds = int(seconds)

    if (isinstance(seconds, int)):               
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        hms = {'hours': h, 'minutes': m, 'seconds': s}

        return('{hours}h:{minutes:02d}m:{seconds:02d}s'.format(**hms))
    else:
        print('s2hms: es necessita un int o float (representant segons) per fer la conversió')
        return

def chrono(startTime):
    ''' Retorna el temps transcorregut des del temps inicial passat

    :param startTime: segons des del EPOCH

    :return: hores, minuts i segons
    :rtype: str   
    '''
    if (isinstance(startTime, (int, float))):
        interval = int(time.time()) - startTime
        return(s2hms(interval))
    else:
        print('chrono: es necessita un int o float (segons des del EPOCH) per calcular el temps transcorregut')
        return   

def printSQLStats(str, newposts, updates, time):
    ''' Imprimeix el nombre de publicacions processades

        :param str: el títol del bloc a imprimir
        :param newposts: el nombre de publicacions noves afegides a la BBDD
        :param updates: el nombre de publicacions actualitzades
        :param time: el temps de durada
    '''
    if (str != None):
        text = ' Subreddit: {0} '.format(str)
    else:
        text = ' Valors sessió '
    
    print(len(text) * '-')
    print(text)
    print(len(text) * '-')
    if(time != None):
        print('Durada total:', s2hms(time))
    print('Noves:', newposts)
    print('Actualitzades:', updates)
    print()

def printGetSubredditsStats(startTime, new, updated):
    ''' Imprimeix el nombre de subreddits afegits a la BBDD
        i el temps que s'ha tardat.

        :param startime: el temps en que s'ha iniciat el procés, format UNIX
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
    ''' Guarda l'excepció passada a la base de dades

        :param e: el text amb la descripció de l'excepció
    '''
    try:
        error = re.escape(str(e))
        query = 'INSERT INTO excepts (description) VALUES("{0}")'.format(error)        
        cur.execute(query)
        con.commit()
    except pymysql.MySQLError as e:
        return

def updateWait(wait, waitFraction):
    ''' Espera un temps determinat i ho anuncia cada x minuts.

        :param wait: El temps total a esperar, en format UNIX.
        :param waitFraction: El temps que passa entre cada anunci.
    '''
    while wait >= 0:                
        print('Falten {0} per la propera iteració'.format(s2hms(wait)))
        wait -= waitFraction
        time.sleep(waitFraction)
    print()
###################################################################################
# Les següents funcions han estat extretes del següent script:
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

    print('b36: es necessita un int per fer la conversió')
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
        :param alphabet: Caràcters usats en la conversió (OPCIONAL)

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
            última conv.  -> Apr 02 2016 20:40:17

        :param timestamp: la data i hora retornats per time.time()

        :return: la data i hora convertits
        :rtype: str 
    '''
    x = datetime.datetime.utcfromtimestamp(timestamp)
    x = datetime.datetime.strftime(x, "%b %d %Y %H:%M:%S")
    return x

def smartinsert(con, cur, results, MIN_SCORE):
    ''' La funció original ha estat modificada, per adaptar-la a les
        necessitats del projecte.

        Insereix els valors passats a la base de dades
        Si ja existeixen, actualitza el nombre de vots i de comentaris

        :param con: pymysql.connections.Connection object
        :param cur: pymysql.cursors.Cursor object
        :param results: una llista d'objectes praw.objects.Submission

        :return: el nombre de publicacions noves afegides i les acualitzades
        :rtype: int, int
    '''
    newposts = 0                        # Comptabilitzen pubs noves i actualitzades
    updates = 0

    for o in results:     
        cur.execute("SELECT * FROM posts WHERE idstr='%s' LIMIT 1;" % o.id)

        if not cur.fetchone():          # Nova fila a la BBDD            
            # Reddit té un bug, en que si l'autor d'una publicació s'ha esborrat,
            # es produeix una excepció al intentar recuperar-ne el nom.
            try:                
                o.authorx = o.author.name
            except AttributeError:
                o.authorx = '[DELETED]'            

            if (isinstance(o, praw.objects.Submission) and (o.score >= MIN_SCORE)):
                if o.is_self:
                    o.url = 'None'

                postdata = {
                    'idstr': o.id,
                    'idint': b36(o.id),
                    'title': re.escape(o.title),
                    'author': o.authorx,
                    'subreddit': o.subreddit.display_name,
                    'score': o.score,
                    'ups': o.ups,
                    'downs': o.downs,
                    'num_comments': o.num_comments,
                    'is_self': o.is_self,                    
                    'url': o.url,
                    'created_utc': o.created_utc,
                    'over18': o.over_18
                }
            
                try:
                    newposts += 1
                    query = "INSERT INTO posts VALUES('{idstr}', {idint}, '{title}', '{author}', '{subreddit}', {score}, {ups}, {downs}, {num_comments}, {is_self}, '{url}', {created_utc}, {over18})".format(**postdata)
                    cur.execute(query)
                except pymysql.MySQLError as e:
                    text = 'smartinsert:Insert. ID: {0}. Excepció: {1}'.format(o.id, str(e))
                    storeExcept(text, cur, con)
                    pass
            #Fi if (isinstance(o, praw.objects.Submission)...
        #Fi if not cur.fetchone()

        else:                           # Actualització d'una entrada existent
            updates += 1
            if isinstance(o, praw.objects.Submission):
                postdata = {
                    'idstr': o.id,
                    'score': o.score,
                    'num_comments': o.num_comments, 
                }
                try:
                    query = "UPDATE posts SET score = {score}, num_comments = {num_comments} WHERE idstr = '{idstr}' LIMIT 1".format(**postdata)
                    cur.execute(query)
                except pymysql.MySQLError as e:
                    text = 'smartinsert:Update. ID: {0}. Excepció: {1}'.format(o.id, str(e))
                    storeExcept(text, cur, con)
                    pass
            #Fi if (isinstance(o, praw.objects.Submission)...
        #Fi else -> if not cur.fetchone()
    #Fi bucle for o in results

    con.commit()
    return (newposts, updates)
