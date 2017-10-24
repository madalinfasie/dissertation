from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', views.contact),
    url(r'^thankyou/$', TemplateView.as_view(template_name='contact/thankyou.html')),
]

