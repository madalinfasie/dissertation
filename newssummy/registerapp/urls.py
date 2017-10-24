from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm


urlpatterns = [
    url(r'^register/$', views.register_user),
    url(r'^success/$', views.success),
    url(r'^login/$', auth_views.login, {'template_name': 'register/login.html', 'authentication_form':LoginForm}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'register/logout.html'}, name='logout'),
    # after register confirmation link is pressed
    url(r'^confirm/(?P<activation_key>(.*?))$', views.confirm),
    # for password reset
    url(r'^password/change/$', views.send_reset_pass_request),
    url(r'^password/change/(?P<pass_key>(.*?))$', views.change_password),
]
