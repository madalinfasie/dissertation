from datetime import datetime, timedelta

from django.shortcuts import render
from django.db.models import Count, F, Q

from summarymodule.models import News
from summarymodule.generate_tags import get_tags
from .models import Tags, NewsTags
from homepage.views import normalize_query, get_query

def index(request):
	news_article_text = News.objects.filter(article_date__gte=datetime.now()-timedelta(days=7)).values()

	tags_list = get_best_tags()

	return render(request, \
		'statisticsapp/statistics.html', \
		{'nbar': 'statistics','best_bigrams': tags_list})

def news_by_selected_tag(request, tag_name):
	top_news = News.objects.filter(article_date__gte=datetime.now()-timedelta(days=7)).order_by(F('vote_up') - F('vote_down'))[::-1][:3]

	tag_id = Tags.objects.get(tag_name=tag_name)
	news = News.objects.filter(newstags__id_tags=tag_id).order_by('-article_date')
	return render(request, 'homepage/home.html', {'news': news, 'top_news': top_news})

def get_best_tags():
	tags_days_range = 7

	tags = Tags.objects \
			.filter(create_date__gte=datetime.now()-timedelta(days=tags_days_range)) \
			.annotate(tag_count = Count('tag_name')) \
			.order_by('-tag_count') \
			.values('tag_name', 'tag_score', 'newstags__id_news', 'tag_count') \
	
	return [(tag['tag_name'], tag['tag_count'], tag['newstags__id_news']) for tag in tags]
