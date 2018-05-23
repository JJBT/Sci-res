from nltk import WordNetLemmatizer, word_tokenize
import sqlite3
import json


def save_to_base(cursor, article):

    data = (article['text'], article['date'], article['post_id'])

    if check_post_id(cursor, article['post_id']):
        cursor.execute("INSERT INTO t_articles (text, date, post_id) "
                       "VALUES (?, ?, ?)", data)
        print('Succesfully saved')


def check_post_id(cursor, post_id):
    """Check the existence of this article in base"""
    cursor.execute("""SELECT * FROM t_articles WHERE post_id=?""", (post_id, ))

    if cursor.fetchone() is not None:
        return False
    return True


def lemmatize(quote):
    # punct = ['.', ',', '(', ')', '{', '}', ';', ':', '?', '!', '@', '"', '/', '”', '’', '[', ']', '$', '#', '*', '$',
    #          '_', '-', '\\', 'http', 'https', '“', '—', '‘', '»', '•', '|']

    quote = word_tokenize(quote)
    quote = [w.lower() for w in quote]
    wnl = WordNetLemmatizer()
    quote = [wnl.lemmatize(w) for w in quote]

    i = 0
    while i < len(quote):
        if not quote[i].isalpha():
            quote.remove(quote[i])
        else:
            i += 1

    return json.dumps(quote)


def main(limit):
    conn = sqlite3.connect('db.db3')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM articles ORDER BY id_articles DESC LIMIT ?""", (limit,))

    for row in cursor.fetchall():
        text = lemmatize(row[7])

        article = {
            'text': text,
            'date': row[2][:-5],
            'post_id': row[3]
        }
        save_to_base(cursor, article)

        conn.commit()

    conn.close()


if __name__ == '__main__':
    limit = 100
    main(limit)
