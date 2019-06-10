from django.conf.urls import url

from . import views  # import views so we can use them in urls.


urlpatterns = [
    url(r'^$', views.index),  # "/store" will call the method "index" in "views.py"
    url(r'^user/$', views.get_user),
    url(r'^thanks/$', views.thanks),
    url(r'^login/$', views.user_login),
    url(r'^product/$', views.product),
    url(r'^account/$', views.account),
    url(r'^logout/$', views.user_logout),
]
