#################################################################################
#
#   Script per connectar amb la base de dades.
#
#   Data creació:           24/03/2016
#   Última modificació:     27/03/2016
#
#   Autor: Ramon Royo
#          Treball de fi de grau (UOC)
#
#   Fonts consultades:
#
#   PyMySQL documentation
#   https://github.com/PyMySQL/PyMySQL#pymysql
#    
#   PyMySQL error handling
#   http://stackoverflow.com/a/25026333/1067293
#   Error genèric: pymysql.MySQLError
#
#   How do you return multiple values in Python?
#   http://stackoverflow.com/questions/354883/how-do-you-return-multiple-values-in-python
#
#################################################################################

from redditWhoLib import loginData
import pymysql

# Definició de la classe baseDades, per retornar un objecte amb dos atributs
# el cursor i la connexió
class baseDades(object):
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

# Connexió amb la base de dades
def login():
    try:
        connection = pymysql.connect(host = loginData.DB_HOST,
                                     user = loginData.DB_USER,
                                     password = loginData.DB_PASS,
                                     db = loginData.DB_NAME)
        cursor = connection.cursor()
        print('Connexió amb la base de dades correcta.')        
        return baseDades(connection, cursor)
    except pymysql.OperationalError as e:
        print('Error connectant amb la base de dades: ' + str(e))