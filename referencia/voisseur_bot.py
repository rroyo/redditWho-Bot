#/u/GoldenSights
import datetime
import os
import praw
import sqlite3
import sys
import time
import traceback


USERAGENT = ""
APP_ID = ""
APP_SECRET = ""
APP_URI = ""
APP_REFRESH = ""
# https://www.reddit.com/comments/3cm1p8/how_to_make_your_bot_use_oauth2/
MAXIMUM_EXPANSION_MULTIPLIER = 2
# The maximum amount by which it can multiply the interval
# when not enough posts are found.
DATABASE_FOLDER = 'databases'
if not os.path.exists(DATABASE_FOLDER):
    os.makedirs(DATABASE_FOLDER)
DATABASE_SUBREDDIT = '%s/%s.db' % (DATABASE_FOLDER, '%s')
DATABASE_USER = '%s/@%s.db' % (DATABASE_FOLDER, '%s')
try:
    import bot
    USERAGENT = bot.aPT
    APP_ID = bot.oG_id
    APP_SECRET = bot.oG_secret
    APP_URI = bot.oG_uri
    APP_REFRESH = bot.oG_scopes['all']
except ImportError:
    pass

print('Logging in.')
# http://redd.it/3cm1p8
r = praw.Reddit(USERAGENT)
r.set_oauth_app_info(APP_ID, APP_SECRET, APP_;URI)
r.refresh_access_information(APP_REFRESH)

SQL_COLUMNCOUNT = 16
SQL_IDINT = 0
SQL_IDSTR = 1
SQL_CREATED = 2
SQL_SELF = 3
SQL_NSFW = 4
SQL_AUTHOR = 5
SQL_TITLE = 6
SQL_URL = 7
SQL_SELFTEXT = 8
SQL_SCORE = 9
SQL_SUBREDDIT = 10
SQL_DISTINGUISHED = 11
SQL_TEXTLEN = 12
SQL_NUM_COMMENTS = 13
SQL_FLAIR_TEXT = 14
SQL_FLAIR_CSS_CLASS = 15



def fixint(i):
    if i == '':
        return 0
    i = int(i)
    if i < 0:
        return 0
    return i

def get_all_posts(subreddit, lower=None, maxupper=None,
                  interval=86400):
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
    offset = -time.timezone
    
    if lower == 'update':        
        # Seguirà capturant missatges, des de l'últim que hi hagi a la BBDD
        db.cur.execute('SELECT pid FROM posts ORDER BY pid DESC ' +
                       'WHERE subreddit like '%s' LIMIT 1' %s subreddit)
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
        print('\nCurrent interval:', interval, 'seconds')
        print('Lower', human(lower), lower)
        print('Upper', human(upper), upper)
        while True:
            try:
                if usermode is not False:
                    query = '(and author:"%s" (and timestamp:%d..%d))' % (
                        usermode, lower, upper)
                else:
                    query = 'timestamp:%d..%d' % (lower, upper)
                searchresults = list(r.search(query, subreddit=subreddit,
                                              sort='new', limit=100,
                                              syntax='cloudsearch'))
                break
            except:
                traceback.print_exc()
                print('resuming in 5...')
                time.sleep(5)
                continue

        searchresults.reverse()
        print([i.id for i in searchresults])

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
            smartinsert(db, cur, searchresults)
        print()

    cur.execute('SELECT COUNT(idint) FROM posts')
    itemcount = cur.fetchone()[SQL_IDINT]
    print('Ended with %d items in %s' % (itemcount, databasename))
    sql.close()
    del cur
    del sql



def human(timestamp):
    x = datetime.datetime.utcfromtimestamp(timestamp)
    x = datetime.datetime.strftime(x, "%b %d %Y %H:%M:%S")
    return x

def humannow():
    x = datetime.datetime.now(datetime.timezone.utc).timestamp()
    x = human(x)
    return x

def initialize_database(sql, cur):
    cur.execute('''CREATE TABLE IF NOT EXISTS posts(
        idint INT,
        idstr TEXT,
        created INT,
        self INT,
        nsfw INT,
        author TEXT,
        title TEXT,
        url TEXT,
        selftext TEXT,
        score INT,
        subreddit TEXT,
        distinguish INT,
        textlen INT,
        num_comments INT,
        flair_text TEXT,
        flair_css_class TEXT)''')
    cur.execute('CREATE INDEX IF NOT EXISTS idstrindex ON posts(idstr)')

def livestream(subreddit=None, username=None, sleepy=30, limit=100, submissions=True, comments=False, debug=False):
    '''
    Continuously get posts from this source
    and insert them into the database
    '''
    if subreddit is None and username is None:
        print('Enter username or subreddit parameter')
        return
    if subreddit is not None and username is not None:
        print('Enter subreddit OR username, not both')
        return

    if subreddit:
        print('Getting subreddit %s' % subreddit)
        sql = sqlite3.connect(DATABASE_SUBREDDIT % subreddit)
        item = r.get_subreddit(subreddit)
        submissions = item.get_new if submissions else None
        comments = item.get_comments if comments else None
    else:
        print('Getting redditor %s' % username)
        sql = sqlite3.connect(DATABASE_USER % username)
        item = r.get_redditor(username)
        submissions = item.get_submitted if submissions else None
        comments = item.get_comments if comments else None
    
    livestreamer = lambda *a, **k: livestream_helper(submissions, comments, debug, *a, **k)

    cur = sql.cursor()
    while True:
        try:
            bot.refresh(r)  # personal use
            items = livestreamer(limit=limit)
            newitems = smartinsert(sql, cur, items)
            print('%s +%d' % (humannow(), newitems), end='')
            if newitems == 0:
                print('\r', end='')
            else:
                print()
            if debug:
                print('Loop finished.')
            time.sleep(sleepy)
        except KeyboardInterrupt:
            print()
            sql.commit()
            sql.close()
            del cur
            del sql
            return
        except Exception as e:
            traceback.print_exc()
            time.sleep(5)
hangman = lambda: livestream(username='gallowboob', sleepy=60, submissions=True, comments=True)

def livestream_helper(submissions=None, comments=None, debug=False, *a, **k):
    '''
    Given a submission-retrieving function and/or a comment-retrieving function,
    collect submissions and comments in a list together and return that.

    '''
    if (submissions, comments) == (None, None):
        raise TypeError('livestream helper got double Nones')
    results = []

    if submissions:
        if debug: print('Getting submissions', a, k)
        results += list(submissions(*a, **k))
    if comments:
        if debug: print('Getting comments', a, k)
        results += list(comments(*a, **k))
    if debug:
        print('Collected. Saving...')
    return results

def manually_replace_comments(incomments, limit=None, threshold=0, verbose=False):
    '''
    PRAW's replace_more_comments method cannot continue
    where it left off in the case of an Ow! screen.
    So I'm writing my own function to get each MoreComments item individually

    Furthermore, this function will maximize the number of retrieved comments by
    sorting the MoreComments objects and getting the big chunks before worrying
    about the tail ends.
    '''

    comments = []
    morecomments = []
    while len(incomments) > 0:
        item = incomments[0]
        if isinstance(item, praw.objects.MoreComments) and item.count >= threshold:
            morecomments.append(item)
        elif isinstance(item, praw.objects.Comment):
            comments.append(item)
        incomments = incomments[1:]

    try:
        while True:
            if limit is not None and limit <= 0:
                break
            if len(morecomments) == 0:
                break
            morecomments.sort(key=lambda x: x.count)
            mc = morecomments.pop()
            #mc = morecomments[0]
            #morecomments = morecomments[1:]
            additional = nofailrequest(mc.comments)()
            additionals = 0
            if limit is not None:
                limit -= 1
            for item in additional:
                if isinstance(item, praw.objects.MoreComments) and item.count >= threshold:
                    morecomments.append(item)
                elif isinstance(item, praw.objects.Comment):
                    comments.append(item)
                    additionals += 1
            if verbose:
                s = '\tGot %d more, %d so far.' % (additionals, len(comments))
                if limit is not None:
                    s += ' Can perform %d more replacements' % limit
                print(s)
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    return comments

def nofailrequest(function):
    '''
    Creates a function that will retry until it succeeds.
    This function accepts 1 parameter, a function, and returns a modified
    version of that function that will try-catch, sleep, and loop until it
    finally returns.
    '''
    def a(*args, **kwargs):
        while True:
            try:
                try:
                    result = function(*args, **kwargs)
                    return result
                except AssertionError:
                    # Strange PRAW bug causes certain MoreComments
                    # To throw assertion error, so just ignore it
                    # And get onto the next one.
                    return []
            except:
                traceback.print_exc()
                print('Retrying in 2...')
                time.sleep(2)
    return a

def smartinsert(sql, cur, results, delaysave=False, nosave=False):
    '''
    Insert the data into the database
    Or update the listing if it already exists
    `results` is a list of submissions
    `delaysave` commits after all inserts
    `nosave` does not commit

    returns the number of posts that were new.
    '''
    newposts = 0
    for o in results:
        cur.execute('SELECT * FROM posts WHERE idstr=?', [o.fullname])
        if not cur.fetchone():
            newposts += 1
            try:
                o.authorx = o.author.name
            except AttributeError:
                o.authorx = '[DELETED]'

            postdata = [None] * SQL_COLUMNCOUNT

            if isinstance(o, praw.objects.Submission):
                if o.is_self:
                    o.url = None
                postdata[SQL_IDINT] = b36(o.id)
                postdata[SQL_IDSTR] = o.fullname
                postdata[SQL_CREATED] = o.created_utc
                postdata[SQL_SELF] = o.is_self
                postdata[SQL_NSFW] = o.over_18
                postdata[SQL_AUTHOR] = o.authorx
                postdata[SQL_TITLE] = o.title
                postdata[SQL_URL] = o.url
                postdata[SQL_SELFTEXT] = o.selftext
                postdata[SQL_SCORE] = o.score
                postdata[SQL_SUBREDDIT] = o.subreddit.display_name
                postdata[SQL_DISTINGUISHED] = o.distinguished
                postdata[SQL_TEXTLEN] = len(o.selftext)
                postdata[SQL_NUM_COMMENTS] = o.num_comments
                postdata[SQL_FLAIR_TEXT] = o.link_flair_text
                postdata[SQL_FLAIR_CSS_CLASS] = o.link_flair_css_class

            if isinstance(o, praw.objects.Comment):
                postdata[SQL_IDINT] = b36(o.id)
                postdata[SQL_IDSTR] = o.fullname
                postdata[SQL_CREATED] = o.created_utc
                postdata[SQL_SELF] = None
                postdata[SQL_NSFW] = None
                postdata[SQL_AUTHOR] = o.authorx
                postdata[SQL_TITLE] = o.parent_id
                postdata[SQL_URL] = o.link_id
                postdata[SQL_SELFTEXT] = o.body
                postdata[SQL_SCORE] = o.score
                postdata[SQL_SUBREDDIT] = o.subreddit.display_name
                postdata[SQL_DISTINGUISHED] = o.distinguished
                postdata[SQL_TEXTLEN] = len(o.body)
                postdata[SQL_NUM_COMMENTS] = None
                postdata[SQL_FLAIR_TEXT] = None
                postdata[SQL_FLAIR_CSS_CLASS] = None

            cur.execute('''INSERT INTO posts VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', postdata)
        else:
            postdata = [None] * 5
            
            if isinstance(o, praw.objects.Submission):
                postdata[0] = o.score
                postdata[1] = o.num_comments
                postdata[2] = o.selftext
                postdata[3] = o.distinguished
            
            if isinstance(o, praw.objects.Comment):
                postdata[0] = o.score
                postdata[1] = None
                postdata[2] = o.body
                postdata[3] = o.distinguished

            postdata[-1] = o.fullname

            cur.execute('UPDATE posts SET score=?, num_comments=?, selftext=?, distinguish=? WHERE idstr=?', postdata)

        if not delaysave and not nosave:
            sql.commit()
    if delaysave and not nosave:
        sql.commit()
    return newposts

prompt_ts_subreddit = '''
- Subreddit
  Leave blank to get username instead
  /r/'''
prompt_ts_username = '''
- Get posts from user
  /u/'''
prompt_ts_lowerbound = '''
- Lower bound
  Leave blank to get ALL POSTS
  Enter "update" to use last entry
  ]: '''
prompt_ts_startinginterval = '''
- Starting interval
  Leave blank for standard
  ]: '''
def timesearch_prompt():
    while True:
        usermode = False
        maxupper = None
        interval = 86400
        print(prompt_ts_subreddit, end='')
        sub = input()
        if sub == '':
            print(prompt_ts_username, end='')
            usermode = input()
            sub = 'all'
        if usermode:
            p = DATABASE_USER % usermode
        else:
            p = DATABASE_SUBREDDIT % sub
        if os.path.exists(p):
            print('Found %s' % p)
        print(prompt_ts_lowerbound, end='')
        lower  = input().lower()
        if lower == '':
            lower = None
        if lower not in [None, 'update']:
            print('- Maximum upper bound\n]: ', end='')
            maxupper = input()
            if maxupper == '':
                maxupper = datetime.datetime.now(datetime.timezone.utc)
                maxupper = maxupper.timestamp()
            print(prompt_ts_startinginterval, end='')
            interval = input()
            if interval == '':
                interval = 84600
            try:
                maxupper = int(maxupper)
                lower = int(lower)
                interval = int(interval)
            except ValueError:
                print("lower and upper bounds must be unix timestamps")
                input()
                quit()
        get_all_posts(sub, lower, maxupper, interval, usermode)
        print('\nDone. Press Enter to close window or type "restart"')
        if input().lower() != 'restart':
            break

def updatescores(databasename, submissions=True, comments=False):
    '''
    Get all submissions or comments from the database, and update
    them with the current scores.
    '''

    databasename = databasename.replace('.db', '')
    databasename = DATABASE_SUBREDDIT % databasename
    sql = sqlite3.connect(databasename)
    cur = sql.cursor()
    cur2 = sql.cursor()
    
    if submissions and comments:
        cur2.execute('SELECT COUNT(*) FROM posts')
        cur.execute('SELECT * FROM posts')

    elif submissions:
        cur2.execute('SELECT COUNT(*) FROM posts WHERE idstr LIKE "t3_%"')
        cur.execute('SELECT * FROM posts WHERE idstr LIKE "t3_%"')

    elif comments:
        cur2.execute('SELECT COUNT(*) FROM posts WHERE idstr LIKE "t1_%"')
        cur.execute('SELECT * FROM posts WHERE idstr LIKE "t1_%"')
    
    totalitems = cur2.fetchone()[0]
    itemcount = 0
    while True:
        f = []
        for x in range(100):
            x = cur.fetchone()
            if x is not None:
                f.append(x[SQL_IDSTR])
        if len(f) == 0:
            break
        posts = r.get_info(thing_id=f)
        itemcount += len(f)
        print('%d / %d updated' % (itemcount, totalitems))
        smartinsert(sql, cur2, posts, nosave=True)
    sql.commit()
    sql.close()
    del cur
    del sql

if __name__ == '__main__':
    if len(sys.argv) > 1:
        c = sys.argv[1]
        exec(c)
    else:
        timesearch_prompt()


