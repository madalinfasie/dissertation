from django.conf.urls import url
from django.views.generic import DetailView

from . import views
from summarymodule.models import News

urlpatterns = [
    url(r'^$', views.index),
    url(r'^search/$', views.index),
    # url(r'^(?P<pk>\d+)$', DetailView.as_view(model=News, template_name='homepage/news_page.html')),
    url(r'^(?P<pk>\d+)$', views.selected_news_page),
    url(r'^shared/(?P<pk>\d+)$', DetailView.as_view(model=News, template_name='homepage/news_page_shared.html')),
    url(r'^upvote/(?P<news_id>[0-9]+)/$', views.upvote, name='upvote'),
    url(r'^downvote/(?P<news_id>[0-9]+)/$', views.downvote, name='downvote'),
    url(r'^(?P<tag_name>(\w+\s+)+\w+)$', views.news_by_selected_tag),
]
