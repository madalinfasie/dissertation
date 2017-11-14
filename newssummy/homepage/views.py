import re
from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.views.generic import DetailView

from summarymodule import tasks
from summarymodule.models import News, UserNews
from summarymodule import get_summary
from statisticsapp.models import Tags, NewsTags

language = "english"
sentence_count = 3
news_sites = [#'http://rss.nytimes.com/services/xml/rss/nyt/World.xml',
              'http://www.huffingtonpost.com/feeds/verticals/world/news.xml',
              'http://feeds.bbci.co.uk/news/world/rss.xml',]


# MAIN FUNCTION TO RENDER HOMEPAGE
def index(request):
    # get all news ordered desc by article_date
    #get_summary.make_summary(news_sites, language, sentence_count)
    news_list = News.objects.all().order_by('-article_date')[:500]
    # Paginator {
    page = request.GET.get('page',1)
    paginator = Paginator(news_list, 10)
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    # }

    # get most popular news
    top_news = News.objects.filter(article_date__gte=datetime.now()-timedelta(days=7)).order_by(F('vote_up') - F('vote_down'))[::-1][:3]

    # lista stirilor votate -- o folosesc ca sa imi dau seama ce este disabled si ce e enabled
    if request.user.is_anonymous:
        voted_up_list = []
        voted_down_list = []
    else:
        # iau id-urile stirilor care au fost votate pozitiv/negativ de userul care este conectat in momentul asta
        voted_up_list = UserNews.objects.filter(vote=1, id_user_id=request.user).values_list('id_news_id', flat=True)
        voted_down_list = UserNews.objects.filter(vote=-1, id_user_id=request.user).values_list('id_news_id', flat=True)

    # start the task that gets the news
    tasks.get_news.delay(news_sites=news_sites, language=language, sentence_count=sentence_count)

    # make the search {
    if request.GET.get('textbox_search'):
        query_string = ''
        # found_entries = None
        if ('textbox_search' in request.GET) and request.GET['textbox_search'].strip():
            query_string = request.GET['textbox_search']
            entry_query = get_query(query_string, ['article_title', 'article_description', 'article_text' ])

            if query_string == '':
                news = News.objects.all().order_by('-article_date')
            else:
                news = News.objects.filter(entry_query).order_by('-article_date')
        return render(request, 'homepage/home.html', {'news': news, 'top_news': top_news})
    # }
    # render the page
    return render(request, 'homepage/home.html', {'news': news,
                                                  'top_news': top_news,
                                                  'voted_up_list': voted_up_list,
                                                  'voted_down_list': voted_down_list,
                                                  'currpage':'home'})

# Render the page containing the selected news
def selected_news_page(request, pk):
    news = News.objects.get(id=pk)
    tags = Tags.objects.filter(newstags__id_news=news.id).values_list('tag_name')

    return render(request, 'homepage/news_page.html', {'news': news, 'tags':tags})

# Render the page with news by tag_name selected
def news_by_selected_tag(request, tag_name):
    top_news = News.objects.filter(article_date__gte=datetime.now()-timedelta(days=7)).order_by(F('vote_up') - F('vote_down'))[::-1][:3]

    tag_id = Tags.objects.get(tag_name=tag_name)
    news = News.objects.filter(newstags__id_tags=tag_id).order_by('-article_date')
    return render(request, 'homepage/home.html', {'news': news, 'top_news': top_news})

# SEARCH ALGORITHM
# credits: http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


# Doesn't work every time
# from django.contrib.postgres.search import SearchVector
# from django.contrib.postgres.search import SearchQuery
# def search(request):
#     if request.GET.get('textbox_search'):
#         results = News.objects.annotate(search=SearchVector('article_title')).filter(
#             search=SearchQuery(request.GET.get('textbox_search'))).order_by('article_title')
#     else:
#         results = News.objects.all()
#     return render(request, 'homepage/search_results.html', {'results': results})
#

# VOTING SYSTEM
def upvote(request, news_id):
    user = request.user
    news = News.objects.get(pk=news_id)
    try:
        usernews = UserNews.objects.get(id_user=user, id_news=news)
    except:
        usernews = None

    if usernews is None:
        # adaug votul
        news.vote_up += 1
        news.save()
        # daca userul nu a votat stirea respectiva niciodata, se creaza inregistrare noua in UserNews
        usernews_add = UserNews(id_user=user, id_news=news, vote=1)
        usernews_add.save()
        usernews_add.save()
        return HttpResponseRedirect('/')
    if usernews.vote == -1:
        # daca userul a mai adaugat in trecut un vot, dar s-a razgandit si il schimba, atunci il anulez si incrementez
        # votul opus
        # IN VARIANTA ASTA USERUL NU ARE POSIBILITATEA DE A ANULA DEFINITIV VOTUL
        news.vote_down += 1
        news.vote_up += 1
        news.save()
        # schimb data la care s-a inregistrat votul ultima data
        usernews.last_date = datetime.now()
        usernews.vote = 1
        usernews.save()
        return HttpResponseRedirect('/')

    return None


# ANALOG CA MAI SUS
def downvote(request, news_id):
    user = request.user
    news = News.objects.get(pk=news_id)
    try:
        usernews = UserNews.objects.get(id_user=user, id_news=news)
    except:
        usernews = None

    if usernews is None:
        news.vote_down -= 1
        news.save()
        usernews_add = UserNews(id_user = user, id_news = news, vote = -1)
        usernews_add.save()
        return HttpResponseRedirect('/')

    if usernews.vote == 1:
        news.vote_up -= 1
        news.vote_down -= 1
        news.save()
        usernews.last_date = datetime.now()
        usernews.vote = -1
        usernews.save()
        return HttpResponseRedirect('/')

    return None

