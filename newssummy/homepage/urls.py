from django.conf.urls import url
from . import views
from django.views.generic import DetailView
from summarymodule.models import News

urlpatterns = [
    url(r'^$', views.index),
    url(r'^search/$', views.index),
    url(r'^(?P<pk>\d+)$', DetailView.as_view(model=News, template_name='homepage/news_page.html')),
    url(r'^shared/(?P<pk>\d+)$', DetailView.as_view(model=News, template_name='homepage/news_page_shared.html')),
    url(r'^upvote/(?P<news_id>[0-9]+)/$', views.upvote, name='upvote'),
    url(r'^downvote/(?P<news_id>[0-9]+)/$', views.downvote, name='downvote'),
]
