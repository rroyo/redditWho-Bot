#################################################################################
#
#   Script per connectar amb la base de dades.
#
#   Ús, després d'importar-lo, es crida a la funció login().
#
#   Retorna un objecte amb dos atributs:
#       con -> pymysql.connections.Connection object
#       cur -> pymysql.cursors.Cursor object
#
#   Data creació:           24/03/2016
#   Última modificació:     29/03/2016
#
#   @ Autor: Ramon Royo
#            Treball de fi de grau (UOC)
#
#   @ Fonts consultades:
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

# Definició de la classe baseDades
class baseDades(object):
    def __init__(self, connection, cursor):
        self.con = connection
        self.cur = cursor

# Connexió amb la base de dades
def login():
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