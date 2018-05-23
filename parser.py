import sqlite3
import requests, requests.exceptions
from bs4 import BeautifulSoup
import re


def save_to_base(article):
    conn = sqlite3.connect('db.db3')
    cursor = conn.cursor()

    data = (article['title'], article['date'], article['post_id'], article['username'],
            article['user_id'], article['user_login'], article['text'], article['url'])

    if check_post_id(cursor, article['post_id']):
        cursor.execute("INSERT INTO articles (title, date, post_id, username, user_id, user_login, text, url) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
        print('Succesfully parsed')
        conn.commit()

    conn.close()


def check_post_id(cursor, post_id):
    cursor.execute("""SELECT * FROM articles WHERE post_id=?""", (post_id, ))

    if cursor.fetchone() is not None:
        return False
    return True


def check_lang(soup):
    lang = soup.find('article').get('lang')
    if lang == 'en':
        return True
    return False


def get_user_login(soup):
    href = soup.find('a', class_='ds-link ds-link--styleSubtle ui-captionStrong u-inlineBlock link '
                                 'link--darken link--darker').get('href')
    pattern = '@([\w\.])+\?'
    res = re.search(pattern, href)
    return res.group()[1:-1]


def parse_text(soup):
    content = soup.find('div', class_='section-inner sectionLayout--insetColumn')
    tags = ['p', 'a', 'h2', 'h3']
    text = ''
    for tag in content.contents:
        if tag.name in tags:
            text += tag.text + ' '
        if tag.name == 'ul' or tag.name == 'ol':
            for li in tag.contents:
                text += li.text + ' '
    return text


def parse_page(url):
    p_soup = BeautifulSoup(get_html(url), "html5lib")

    if check_lang(p_soup):

        try:
            title = p_soup.find('div', class_='section-inner sectionLayout--insetColumn').find('h1').text
        except AttributeError:
            title = ''

        date = p_soup.find('div', class_='ui-caption postMetaInline js-testPostMetaInlineSupplemental').find('time')\
            .get('datetime')
        post_id = p_soup.find('div', class_='postArticle-content js-postField js-notesSource js-trackedPost')\
            .get('data-post-id')
        user_name = p_soup.find('a', class_='ds-link ds-link--styleSubtle ui-captionStrong u-inlineBlock link '
                                            'link--darken link--darker').text
        user_id = p_soup.find('a', class_='ds-link ds-link--styleSubtle ui-captionStrong '
                                          'u-inlineBlock link link--darken link--darker').get('data-user-id')
        user_login = get_user_login(p_soup)
        text = parse_text(p_soup)

        article = {
            'title': title,
            'date': date,
            'post_id': post_id,
            'username': user_name,
            'user_id': user_id,
            'user_login': user_login,
            'text': text,
            'url': url
        }
        save_to_base(article)


def link_correct(link):
    pattern = re.compile('https://medium.com/')
    result = pattern.match(link)
    if result is None:
        return False
    return True


def get_html(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if 200 <= response.status_code < 300:
        return response.text
    else:
        print("Connection Error")
        raise SystemExit


def parse_main_page(url):
    soup = BeautifulSoup(get_html(url), "html5lib")
    table = soup.find('div', class_='js-tagStream')

    links = []

    for block in table.find_all('div', class_='postArticle postArticle--short js-postArticle js-trackedPost'):
        try:
            link = block.find('a', class_='button button--smaller button--chromeless u-baseColor--buttonNormal')\
                .get('href')
            if link_correct(link):
                links.append(link)
        except AttributeError:
            pass

    for li in links:
        print(li)
        parse_page(li)


def main(url):
    parse_main_page(url)


if __name__ == "__main__":
    LIMIT = 100
    BASE_URL = "https://medium.com/tag/blockchain/latest?limit={}".format(LIMIT)
    main(BASE_URL)
