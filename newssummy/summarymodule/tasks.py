# noinspection PyUnresolvedReferences
from celery.task.schedules import crontab
# noinspection PyUnresolvedReferences
from celery.decorators import periodic_task
from . import get_summary
from celery import shared_task,current_task

#
lang = "english"
sent_count = 3
news_site = [
    'http://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    'http://www.huffingtonpost.com/feeds/verticals/world/news.xml',
    'http://feeds.bbci.co.uk/news/world/rss.xml'
]


@periodic_task(run_every=(crontab(minute='*/15')), name="get_news", ignore_result=True)
def get_news(news_sites = news_site, language = lang, sentence_count = sent_count):
    print('A inceput sumarizarea')
    get_summary.make_summary(news_sites, language, sentence_count)
    print('All set')
    return None

