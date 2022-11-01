import sqlite3
import getpass
import collections

def initSchema(cur):
    tablesFile = open('prj-tables.txt', 'r')
    temp = tablesFile.read()
    cur.executescript(temp)

def seedSchema(cur):
    File = open('seed.txt', 'r')
    temp = File.read()
    cur.executescript(temp)

def selectArtist(cur, uid, artist_id):
    cur.execute('''SELECT songs.sid, songs.title, songs.duration FROM
        artists left outer join perform using (aid) left outer join songs using (sid)
        WHERE aid = '{}'
        group by aid;'''.format(artist_id))
    
    songlist = cur.fetchall()
    count = 1
    for song in songlist:
        print("{}. sid: {}, title: {}, duration: {}".format(count, song[0], song[1], song[2]))
    
    song_selection = input("Select a song (number): ")

    #song action


def userRuntime(cur, uid):
    while True:
        session = input("Start a session (y/n): ")
        if (session == 'y'):

            # first get all session numbers and then choose the lowest
            cur.execute("SELECT MAX(sno) FROM sessions WHERE uid = '{}';".format(uid))
            userSessions = cur.fetchall()
            sessionNum = 1 if userSessions == [(None,)] else userSessions[0][0] + 1
            print(sessionNum)

            cur.execute("INSERT INTO sessions VALUES ('{}', {}, time('now'), NULL);".format(uid, sessionNum))

            # start session
            while True:
                print("session has been started!")
                action = input("Search for Songs/Playlists (s), Search for artists (a) or End session (e): ")



                if (action == "s"):
                    song_input = input("Search for Songs/Playlists: ")
                    keywords = song_input.split()

                    song_Count = collections.defaultdict()
                    playlist_Count = collections.defaultdict()
                    for key in keywords:
                        cur.execute('''SELECT sid FROM songs WHERE title LIKE '%{}%';
                        '''.format(key))
                        res = cur.fetchall()

                        for song in res:
                            song_Count[song[0]] += 1
                        
                        cur.execute('''SELECT pid FROM playlists WHERE title LIKE '%{}%';
                        '''.format(key))
                        res = cur.fetchall()

                        for playlist in res:
                            playlist_Count[playlist[0]] += 1
                    
                    combo = []
                    for song in song_Count:
                        combo.append([song, song_Count[song], 's'])
                    for play in playlist_Count:
                        combo.append([play, playlist_Count[play], 'p'])
                    
                    ncombo = sorted(combo, key=lambda x:x[1])
                    items = len(ncombo)
                    cur_count = 1
                    while True:
                        for i in range(cur_count-1, min(cur_count+4, len(ncombo))):
                            foo = ncombo[i]
                            if foo[2] == 's':
                                cur.execute('''SELECT sid, title, duration FROM songs WHERE sid = {};
                                    '''.format(foo[0]))
                                res = cur.fetchall()[0]
                                print("{}. Song: sid: {}, title: {}, duration: {}".format(cur_count, res[0], res[1], res[2]))
                            else:
                                cur.execute('''SELECT playlists.id, playlists.title, SUM(duration) FROM
                                    playlists left outer join plinclude using (pid) left outer join songs using (sid)
                                    WHERE pid = '{}'
                                    group by pid;'''.format(foo[0]))
                                res = cur.fetchall()[0]
                                print("{}. Playlist: pid: {}, title: {}, duration: {}".format(cur_count, res[0], res[1], res[2]))
                            
                            cur_count += 1
                        
                        if (cur_count != items):
                            newaction = input("Select a result (enter num) or continue search (n)")

                            if (newaction == "n"):
                                continue
                            else:
                                findout = int(newaction)
                                # Do action
                        else:
                            newaction = input("Select a result (enter num)")
                            findout = int(newaction)







                elif (action == "a"):
                    artist_input = input("Search for Artists: ")
                    keywords = artist_input.split()

                    aid_Count = collections.defaultdict()

                    for key in keywords:
                        temp_Count = set()
                        cur.execute('''SELECT aid FROM artists WHERE name LIKE '%{}%';
                        '''.format(key))
                        res = cur.fetchall()

                        for ai in res:
                            temp_Count.add(ai[0])

                        cur.execute('''SELECT DISTINCT artists.aid FROM artists, perform, songs WHERE
                                        songs.title LIKE '%{}%' AND
                                        songs.sid = perform.sid AND
                                        perform.aid = artists.aid;'''.format(key))
                        res = cur.fetchall()
                        for ai in res:
                            temp_Count.add(ai[0])
                        
                        for ai in temp_Count:
                            aid_Count[ai] += 1


                    od = collections.OrderedDict(sorted(aid_Count.items()))
                    
                    items = len(od)
                    cur_count = 1
                    while True:
                        for i in range(cur_count-1, min(items, cur_count + 4)):
                            cur_aid = od[0][i]                            
                            cur.execute('''SELECT artists.name, artists.nationality, COUNT(*) FROM
                                    artists left outer join perform using (aid) left outer join songs using (sid)
                                    WHERE aid = '{}'
                                    group by aid;'''.format(cur_aid))
                            ans = cur.fetchall()[0]
                            print("{}. Name: {} Nationality: {} SongCount: {}".format(cur_count, ans[0], ans[1], ans[2]))
                            cur_count += 1
                        
                        if (cur_count != items):
                            newaction = input("Select a result (enter num) or continue search (n)")

                            if (newaction == "n"):
                                continue
                            else:
                                findout = int(newaction)
                                # Do action
                        else:
                            newaction = input("Select a result (enter num)")
                            findout = int(newaction)
                       
                
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

        password = getpass.getpass("Password: ")

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
