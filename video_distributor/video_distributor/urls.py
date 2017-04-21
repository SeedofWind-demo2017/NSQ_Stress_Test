from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'video.views.home', name='home'),
    url(r'^stats/', 'video.views.stats', name='stats'),
    url(r'^update_table/', 'video.views.home', name='update_table'),
    url(r'^update_charts/', 'video.views.update_charts', name='update_charts'),
    url(r'^update_stats/', 'video.views.update_stats', name='update_stats'),
    url(r'^admin/', include(admin.site.urls)),
]
