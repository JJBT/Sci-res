import sqlite3
import json
import datetime


def get_words(DATETIME):
    conn = sqlite3.connect('db.db3')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM tf_articles WHERE date(date) > date(?) LIMIT 50""", (DATETIME,))

    words = {}

    for row in cursor.fetchall():
        counter = 0
        for k, v in json.loads(row[1]).items():
            if counter < 2:
                counter += 1
                if len(words) > 4:
                    for i in list(words):
                        if v > words[i]:
                            words[k] = v
                            del words[i]

                else:
                    words[k] = v
    return '\n'.join(words)


def get_article(DATETIME, word):
    conn = sqlite3.connect('db.db3')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM tf_articles WHERE date(date) > date(?) LIMIT 50""", (DATETIME,))
    value = 0
    post_id = 0
    for row in cursor.fetchall():
        tfidf_dict = json.loads(row[1])
        if word in tfidf_dict:
            if tfidf_dict[word] > value:
                value = tfidf_dict[word]
                post_id = row[3]

    if value != 0:
        cursor.execute("""SELECT * FROM articles WHERE post_id=?""", (post_id, ))
        link = cursor.fetchone()[8]
        return link
    return 'No such articles'

