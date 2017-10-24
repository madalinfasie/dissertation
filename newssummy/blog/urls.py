from django.conf.urls import url
from django.views.generic import DetailView
from .models import BlogArticles
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.index),
    url(r'^post/$', views.add_blog),
    url(r'^search$', views.index),
    url(r'^(?P<pk>\d+)$', DetailView.as_view(model=BlogArticles, template_name='blog/blog_page.html')),
    url(r'^shared/(?P<pk>\d+)$', DetailView.as_view(model=BlogArticles, template_name='blog/blog_page_shared.html')),
    url(r'^blogupvote/(?P<blog_id>[0-9]+)/$', views.blogupvote, name='blogupvote'),
    url(r'^blogdownvote/(?P<blog_id>[0-9]+)/$', views.blogdownvote, name='blogdownvote'),
    url(r'^user/posts/$', views.user_blogs),
    url(r'^user/posts/(?P<pk>\d+)/$', DetailView.as_view(model=BlogArticles, template_name='blog/blog_page.html')),
    url(r'^user/edit/(?P<id>\d+)$', views.edit_blog),
    url(r'^user/delete/(?P<id>\d+)$', views.delete_blog)
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
