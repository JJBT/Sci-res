from collections import Counter, OrderedDict
import math
import sqlite3
import json
from datetime import datetime, timedelta


def save_to_base(cursor, article):

    data = (article['text'], article['date'], article['post_id'])

    if check_post_id(cursor, article['post_id']):
        cursor.execute("INSERT INTO tf_articles (text, date, post_id) "
                       "VALUES (?, ?, ?)", data)
        print('Succesfully saved')


def check_post_id(cursor, post_id):
    """Check the existence of this article in base"""
    cursor.execute("""SELECT * FROM tf_articles WHERE post_id=?""", (post_id, ))

    if cursor.fetchone() is not None:
        return False
    return True


def compute_tfidf(corpus):
    """Corpus - matrix"""
    def compute_tf(text):
        """TF"""
        """Returns Counter object"""
        tf_text = Counter(text)
        for i in tf_text:
            tf_text[i] = tf_text[i]/len(text)
        return tf_text

    def compute_idf(word, corp):
        """IDF"""
        return math.log10(len(corp)/sum(1 for i in corp if word in i))

    articles_list = []

    for article in corpus:
        tf_idf_dict = {}
        computed_tf = compute_tf(article)
        for word in computed_tf:
            tf_idf_dict[word] = computed_tf[word]*compute_idf(word, corpus)
        articles_list.append(OrderedDict(sorted(tf_idf_dict.items(), key=lambda t: t[1], reverse=True)))

    return articles_list


def main(DATETIME):
    conn = sqlite3.connect('db.db3')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM t_articles WHERE date(date) > date(?) LIMIT 50""", (DATETIME, ))

    corpus = []
    arr_article = []

    for row in cursor.fetchall():
        wrds = json.loads(row[1])
        if len(wrds) != 0:
            article = {
                'text': wrds,
                'date': row[2],
                'post_id': row[3]
            }
            arr_article.append(article)
            corpus.append(wrds)

    res = compute_tfidf(corpus)

    for article, b in zip(arr_article, res):
        article['text'] = json.dumps(b)

        save_to_base(cursor, article)
        conn.commit()

    conn.close()


if __name__ == '__main__':
    # TODAY = "2018-05-24 12:45:49.659124"  # test
    TODAY = datetime.now() - timedelta(days=1)
    main(TODAY)
