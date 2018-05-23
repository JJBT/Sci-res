from collections import Counter
import math
import sqlite3
import json
import datetime


def compute_tfidf(corpus):
    """Принимает двумерный массив"""
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
        articles_list.append(tf_idf_dict)

    return articles_list


def main(DATETIME):
    conn = sqlite3.connect('db.db3')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM t_articles WHERE date(date) > date(?) LIMIT 50""", (DATETIME, ))

    corpus = []

    for row in cursor.fetchall():
        wrds = json.loads(row[1])
        if len(wrds) != 0:
            corpus.append(wrds)

    res = compute_tfidf(corpus)

    res_dict = {}
    for d in res:
        res_dict.update(d)

    sort_list = sorted(res_dict.items(), key=lambda i: i[1], reverse=True)

    del res_dict
    del res
    response = []
    for j in range(6):
        response.append(sort_list[j][0])
    return json.dumps(response)


if __name__ == '__main__':
    DATE = "2018-05-11 12:45:49.659124"
    main(DATE)
