import sqlite3


def initSchema(cur):
    tablesFile = open('prj-tables.txt', 'r')
    temp = tablesFile.read()
    cur.executescript(temp)

def seedSchema(cur):
    File = open('seed.txt', 'r')
    temp = File.read()
    cur.executescript(temp)

def userRuntime(cur, uid):
    while True:
        session = input("Start a session (y/n): ")
        if (session == 'y'):

            # first get all session numbers and then choose the lowest
            cur.execute("SELECT MAX(sno) FROM sessions WHERE uid = '{}';".format(uid))
            userSessions = cur.fetchall()
            sessionNum = 1 if userSessions == [] else userSessions[0][0] + 1
            print(sessionNum)

            cur.execute("INSERT INTO sessions VALUES ('{}', {}, time('now'), NULL);".format(uid, sessionNum))

            # start session
            while True:
                print("session has been started!")
                action = input("Search for Songs/Playlists (s), Search for artists (a) or End session (e): ")

                if (action == "s"):
                    print("songs/playlist")
                elif (action == "a"):
                    print("artists")
                
                else:
                    cur.execute("UPDATE sessions set end = time('now') WHERE sno = {};".format(sessionNum))
                    break

        else:
            break








def main():
    conn = sqlite3.connect('miniproj.db')
    cur = conn.cursor()
    initSchema(cur)
    seedSchema(cur)

    # login
    validId = input("Valid ID: ")

    # if id not in db. new user
    cur.execute("SELECT * FROM users WHERE uid = '{}';".format(validId))
    uid = cur.fetchall()

    cur.execute("SELECT * FROM artists WHERE aid = '{}';".format(validId))
    aid = cur.fetchall()

    if (uid == [] and aid == []):
        # new user
        print("Hello new user\n")
        userName = input("What is your name?: ")
        password = input("Create a Password: ")

        # create user
        cur.execute("INSERT INTO users VALUES ('{}', '{}', '{}')".format(validId, userName, password))

        userRuntime(cur, validId)
    else:

        password = input("Password: ")

        # check if valid password
        cur.execute("SELECT * FROM users WHERE pwd = '{}'".format(password))
        uidPassword = cur.fetchall()

        cur.execute("SELECT * FROM artists WHERE aid = '{}'".format(password))
        aidPassword = cur.fetchall() 

        # if a valid password
        if (uidPassword or aidPassword):
            if (uid and aid):
                decision = input("Login as User (u) or Artist (a)")
                if (decision == 'a'):
                    # artistlogin
                    print('b')
                else: 
                    print('b')
            elif (uid):
                # user login
                userRuntime(cur, validId)
            else:
                # artist login
                print('b')
        else:
            #invalid pwd
            print('t')

    conn.commit()
    conn.close()
if __name__ == "__main__":
    main()
