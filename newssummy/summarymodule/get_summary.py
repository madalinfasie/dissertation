from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import urllib.request
from bs4 import BeautifulSoup
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from .feed_parser import parse_rss
from .models import News, ProcedureDuplicates

language = "english"
sentence_count = 3
news_sites = ['http://www.huffingtonpost.com/feeds/verticals/world/news.xml',
              'http://feeds.bbci.co.uk/news/world/rss.xml']

#'http://rss.nytimes.com/services/xml/rss/nyt/World.xml',


def make_summary(news_sites, language, sentence_count):

    for url in news_sites:
        rss_feed = parse_rss(url)
        for mylist in rss_feed:
            summary = ''
            text = mylist[5]
            # Efectueaza sumarizarea doar daca articolele au mai mult de 250 de caractere
            if len(text) > 1500:
                parser = PlaintextParser.from_string(text, Tokenizer(language))
                stemmer = Stemmer(language)

                summarizer = Summarizer(stemmer)
                summarizer.stop_words = get_stop_words(language)

                for sentence in summarizer(parser.document, sentence_count):
                    summary += str(sentence) + '\n' + '\n'

                news_db = News(article_title=mylist[0], article_description=mylist[1], article_date=mylist[2], article_url=mylist[3], article_img_href=mylist[4], article_text=summary)
                news_db.save()

    try:
        proc = ProcedureDuplicates()
        proc.solve_duplicates()
    except:
        pass
    news = News.objects.all()
    return news
