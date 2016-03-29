#################################################################################
#
#   FALTA CONDICIÖ TRENCAMENT, NO ES FARÀ SERVIR, LA VERSIÓ PRAW ÉS MÉS RÀPIDA
#
#   Script per extreure informació de la pàgina http://www.reddit.com/reddits
#   Concretament extreu una llista amb tots els subreddits i el nombre de
#   subscriptors, entre d'altres dades i ho guarda tot en una taula SQL
#   anomenada 'subreddits'.
#
#   Data creació:           27/03/2016
#   Última modificació:     29/03/2016
#
#   @ Autor: Ramon Royo
#            Treball de fi de grau (UOC)
#
#   @ Fonts consultades:
#
#   Scrapping reddit
#   https://gist.github.com/DanBrink91/8375591/
#
#   Requests: HTTP for Humans
#   http://docs.python-requests.org/en/master/
#
#   Documentació Python 3
#   https://docs.python.org/3/
#
#   UnicodeEncodeError: 'latin-1' codec can't encode character
#   http://stackoverflow.com/questions/3942888/unicodeencodeerror-latin-1-codec-cant-encode-character
#
#   @ Modificacions futures per fer-lo més robust:
#
#   Guardar l'id de l'últim subreddit capturat dels 25 que es capturen amb cada
#   petició, per si de cas es cau reddit o el servidor de l'script.
#
#################################################################################

from redditWhoLib import loginData
from time import sleep, time
import rwlogin, requests, json, pymysql, praw

#Adreça on es capturen els subreddits i agent d'usuari
URL = 'https://www.reddit.com/reddits/.json?count=25&after=t5_'
USERAGENT = {'User-agent': loginData.APP_UA}

TEMPS_ESPERA = 2                        # 1s amb Oauth2, 2s sense

(r, db) = rwlogin.login()               # connexió amb l'API i la BBDD

after = ''                              # id de l'últim subreddit capturat
subreddits = 0                          # per portar el compte dels subreddits processats

# Bucle principal (LI FALTA LA CONDICIÓ DE TRENCAMENT, QUAN ARRIBI A PROCESSAR TOTS ELS SUBREDDITS QUE HI HAN)
while True:
    # El temps d'espera entre peticions cal controlar-lo explícitament
    # ja que no s'està fent ús de la llibreria praw.
    tempsInici = time()

    # Bucle de captura de contingut, es repeteix fins aconseguir el contingut
    while True:
        # Capturo 25 subreddits, és necessari enviar l'agent d'usuari, en cas
        # contrari reddit bloqueja l'accés (codi 429, too many requests), ja que
        # s'utilitza l'agent per defecte que té un gran nombre de peticions.
        request = requests.get((URL + '%s') % after, headers = USERAGENT)
        
        codi = request.status_code      # codi de resposta a la petició HTTP

        # Condició de trencament del bucle
        if(codi == 200):                # codi 200, OK!
            break
        else:                           # codi erroni, algo ha fallat, es repeteix en 1min
            print('El codi de captura és: %s. Esperant 1 min per repetir petició.' % codi)
            sleep(60)
    # Fi While de captura de contingut

    data = request.json()               # el contingut es converteix a Json

    # Es recorre el contingut
    for child in data['data']['children']:
        if (child['data']['after'] != 'null'):
            sub_id = child['data']['id']
            display_name = child['data']['display_name']
            created_utc = child['data']['created_utc']
            description = child['data']['public_description']
            subscribers = child['data']['subscribers']
            over18 = child['data']['over18']
            after = sub_id                  # no es guarda, serveix per carregar els propers 25

            # comprova que el subreddit no existeixi ja a la base de dades
            if not (db.cur.execute("SELECT id FROM subreddits WHERE id = '%s'" % sub_id)):
                # si no existeix es crea una nova entrada amb les dades capturades
                db.cur.execute('INSERT INTO subreddits (id, display_name, created_utc,' +
                               'description, subscribers, over18) VALUES(%s, %s, %s, %s, %s, %s)'
                               ,((sub_id,),(display_name,),(created_utc,),(description,),
                               (subscribers,),(over18,)))
            # si ja existeix, s'actualitza el nombre de subscriptors
            else:
                db.cur.execute("UPDATE subreddits SET subscribers = %s WHERE id = '%s'" % (subscribers, sub_id))
        else:
            break                     # es surt del for i del while, s'han processat tots els subreddits

    db.con.commit()                     # es processen els INSERTS i UPDATES

    # es comptabilitzen els 25 subreddits processats i s'informa de l'avanç    
    subreddits += 25
    print('Últim subreddit processat: %s. Total processats: %s' % (after, subreddits))

    # Espera com a mínim 1 segon entre cada petició de contingut
    tempsFinal = time() - tempsInici

    if not (tempsFinal >=  TEMPS_ESPERA):
        sleep(TEMPS_ESPERA - tempsFinal)

# Fi WHILE principal

db.con.close();                         # es tanca la connexió amb la BBDD