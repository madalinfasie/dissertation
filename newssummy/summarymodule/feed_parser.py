import feedparser
import bs4 as bs
import urllib.request
from urllib.request import Request
import re
from .models import News
from django.db.models import Max
from datetime import datetime, timedelta
import calendar
import pytz


def parse_rss(myurl):
    d = feedparser.parse(myurl)
    news_link, news_title, news_date, news_description = '', '', '', ''
    news_list, news_links = [], []

    max_db_date = News.objects.all().aggregate(Max('article_date'))['article_date__max']

    if max_db_date is not None:
        max_news_db_date = max_db_date
    else:
        max_news_db_date = datetime.now(pytz.utc) - timedelta(days=100)

    for news in d.entries:
        news_link = news.link
        news_title = news.title
        try:
            news_date = datetime.fromtimestamp(calendar.timegm(news.published_parsed), tz=pytz.utc)
        except:
            pass
        try:
            news_description = news.content[0]['value']
        except:
            news_description = news.description

        news_img = ''
        if 'media_content' in news:
            news_img = news['media_content'][0]['url']
        elif 'media_thumbnail' in news:
            news_img = news['media_thumbnail'][0]['url']

        if news_img != '' and news_description != '' and news_title != '' and news_date != '' \
                and news_date > max_news_db_date:
                # and news_title not in title_list
            news_list.append((news_title, news_description, news_date, news_link, news_img))

    news_list = list(set(news_list))
    news_links = [news_list[i][3] for i in range(len(news_list))]

    for url in news_links:
        site_name = re.compile('//www.(.*?).co').findall(url)[0]
        news_url = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(
            Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read()
        soup = bs.BeautifulSoup(news_url, 'lxml')
        text = ''

        main_div = []
        if site_name == 'bbc':
            main_div = soup.find_all('div', {'class':'story-body__inner'})
        elif site_name =='nytimes':
            main_div = soup.find_all('div', {'class':'story-body-supplemental'})

        all_p = [div.find_all('p') for div in main_div]

        footer_p = ''
        try:
            footer_p = soup.find('footer').find_all('p')
        except:
            pass

        # p-urile care nu contin articolul (am facut asta pentru ca nu toate site-urile si nici toate paginile
        # nu au aceeasi clasa pentru articole
        # MAI BINE INCERC SI VARIANTA CEALALTA!
        useless_p = [footer_p,
                     [p for header in soup.find_all('header') for p in header.find_all('p')],
                     [p for div in soup.find_all('div', {'class': 'newsletter-signup'}) for p in div.find_all('p')],
                     soup.find_all('p', {'class': 'story-print-citation'}),
                     soup.find_all('p', {'class': 'feedback-message'}),
                     [p for div in soup.find_all('div', {'class': re.compile(r'-ad-')}) for p in div.find_all('p')],
                     [p for div in soup.find_all('div', {'class': 'follow-us__form'}) for p in div.find_all('p')],
                     [p for div in soup.find_all('div', {'class': 'column--secondary'}) for p in div.find_all('p')],
                     [p for div in soup.find_all('div', {'class': 'twite__panel arrow-top'}) for p in
                      div.find_all('p')],
                     '<p>If you want to receive Breaking News alerts via email, or on a smartphone or tablet via the BBC News App then details on how to do so are available on this help page.</p>',
                     '<p>You can also follow @BBCBreaking on Twitter to get the latest alerts.</p>'
                     ]

        use_p = [item for sublist in useless_p for item in sublist]

        for ps in all_p:
            for p in ps:
                if p not in use_p:
                    text += p.text + '\n'
            
        # fac append textelor stirilor corespunzatoare url-ului.
        for i in range(len(news_list)):
            if url == news_list[i][3]:
                news_list[i] = news_list[i] + (text,)

    return news_list
