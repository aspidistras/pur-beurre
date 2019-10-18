"""urlpatterns defining module"""

from django.conf.urls import url

from . import views  # import views so we can use them in urls.


app_name = 'open_food_facts'

# declares all url patterns of the app with the linked view to use
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/$', views.get_user, name="get_new_user"),
    url(r'^thanks/$', views.thanks),
    url(r'^login/$', views.user_login, name="login"),
    url(r'^account/$', views.account, name="account"),
    url(r'^logout/$', views.user_logout),
    url(r'^search/$', views.search_products, name='search'),
    url(r'^search-substitutes/(?P<product_id>[0-9]+)/$', views.search_substitutes,
        name='search_substitutes'),
    url(r'^product/(?P<product_id>[0-9]+)/$', views.details, name='details'),
    url(r'^save-substitute/(?P<product_id>[0-9]+)/(?P<user_id>[0-9]+)/$', views.save_substitute,
        name='save_substitute'),
    url(r'^substitutes/$', views.user_products, name="user_products"),
    url(r'^legal-notices/$', views.legal_notices, name='legal_notices')
]
