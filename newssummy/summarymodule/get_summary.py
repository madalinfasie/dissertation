from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import urllib.request
from bs4 import BeautifulSoup
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
#from sumy.summarizers.luhn import LuhnSummarizer as Summarizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
#from sumy.summarizers.lex_rank import LexRankSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from .feed_parser import parse_rss
from .models import News, ProcedureDuplicates, Tags, NewsTags
from .generate_tags import get_tags


# language = "english"
# sentence_count = 3
# news_sites = ['http://www.huffingtonpost.com/feeds/verticals/world/news.xml',
#               'http://feeds.bbci.co.uk/news/world/rss.xml']

#'http://rss.nytimes.com/services/xml/rss/nyt/World.xml',

def get_summary(text, sentence_count=3):
    language = 'english'
    summary = ''
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    stemmer = Stemmer(language)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)

    for sentence in summarizer(parser.document, sentence_count):
        summary += str(sentence) + '\n' + '\n'
        
    return summary

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
                tags = get_tags(text)
                # remove tags that are substrings of other tags (e.g. Mohamed bin Salam, bin Salam, Mohamed bin)
                tags.sort(key=lambda tup: len(tup[0]))
                tags = [tag_tuple for index, tag_tuple in enumerate(tags) if all(tag_tuple[0] not in k[0] for k in tags[index + 1:])]

                tags_db = Tags.objects.values("tag_name")
                tags_db = [tag['tag_name'] for tag in tags_db]

                for tag_pair in tags:
                    if tag_pair[0] not in tags_db:
                        tag_db = Tags(tag_name=tag_pair[0], tag_score=tag_pair[1])
                        tag_db.save()
                        tagnews_db = NewsTags(id_tags=tag_db, id_news=news_db)
                        tagnews_db.save()
                    else:
                        tagnews_db = NewsTags(id_tags=Tags.objects.get(tag_name=tag_pair[0]), id_news=news_db)
                        tagnews_db.save()

    for row in News.objects.all():
        if News.objects.filter(article_title=row.article_title).count() > 1:
            row.delete()

    news = News.objects.all()
    return news
