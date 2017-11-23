import re
from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.views.generic import DetailView
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import SearchQuery

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
    news = News.objects.all()
    if request.GET.get('textbox_search'):
        vector = SearchVector('article_title') + \
                 SearchVector('article_description') + \
                 SearchVector('article_text') + \
                 SearchVector('newstags__id_tags__tag_name')
        news_list = News.objects.annotate(search=vector).filter(
            search=SearchQuery(request.GET.get('textbox_search'))).order_by('-article_date', 'article_title').distinct('article_date', 'article_title')
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
        return render(request, 'homepage/home.html', {'news': news, 'top_news': top_news})
    else:
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

# VOTING SYSTEM
def upvote(request, news_id):
    if request.is_ajax():
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
            return render(request, 'homepage/voting_ajax.html',{'news_id':news_id})
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
            return render(request, 'homepage/voting_ajax.html',{'news_id':news_id})
    else:
        news_id = 0
    return None


# ANALOG CA MAI SUS
def downvote(request, news_id):
    if request.method == "GET":
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
            return HttpResponse(news_id)

        if usernews.vote == 1:
            news.vote_up -= 1
            news.vote_down -= 1
            news.save()
            usernews.last_date = datetime.now()
            usernews.vote = -1
            usernews.save()
            return HttpResponse(news_id)
    else:
        news_id = 0
    return None

