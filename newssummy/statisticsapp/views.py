import numpy as np
from collections import Counter
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

from django.shortcuts import render
from django.db.models import Count, F, Q

from summarymodule.models import News
from summarymodule.generate_tags import get_tags
from .models import Tags, NewsTags

def index(request):
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
	tags_days_range = 30

	tags = NewsTags.objects \
			.select_related('id_tags').all() \
			.filter(create_date__gte=datetime.now()-timedelta(days=tags_days_range)) \
			.values('id_tags__tag_name', 'id_tags__tag_score', 'id_news') \
			.order_by('-id_tags__tag_name') 

	tags_name_list = [tag['id_tags__tag_name'] for tag in tags]
	tags_name_count = Counter(tags_name_list)

	final_list = []
	names_list =[]
	for tag in tags:
		if tag['id_tags__tag_name'] not in names_list:
			score = 10/(tags_name_count[tag['id_tags__tag_name']] * tag['id_tags__tag_score'])
			final_list.append((tag['id_tags__tag_name'], score, tag['id_news']))
			names_list.append(tag['id_tags__tag_name'])
	return final_list
