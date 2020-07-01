"""twitterDemo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.conf.urls import url

from mvc.views import signup, signin, index_page, \
    index_user_self, index, detail, index_user,friend_remove

urlpatterns = [
    #    path('admin/', admin.site.urls),
    # login/ register
    url(r'^signup/$', signup),
    url(r'^signin/$', signin),
    url(r'^p/(?P<_page_index>\d+)/$', index_page),
    url(r'^user/$', index_user_self),
    url(r'^$', index),
    url(r'^message/(?P<_id>\d+)/$', detail, name="tmitter-mvc-views-detail"),
    url(r'^user/(?P<_username>[a-zA-Z\-_\d]+)/$',index_user,name="tmitter-mvc-views-index_user"),
    url(r'^friend/remove/(?P<_username>[a-zA-Z\-_\d]+)',friend_remove, name='tmitter-mvc-views-friend_remove'),
]
