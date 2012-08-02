from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'spur.views.home', name='home'),
    # url(r'^spur/', include('spur.foo.urls')),
    (r'^$','ncm.views.redirect_to_admin'),
    (r'^admin/ncm/node/import$','ncm.views.import_node'),
    (r'^admin/ncm/job/(?P<job_id>\d+)/run/$','ncm.views.run_job'),
    (r'^admin/ncm/change/(?P<change_id>\d+)/full_diff/$','ncm.views.diff'),
    (r'admin/ncm/node/(?P<node_id>\d+)/ping/$','ncm.views.ping'),
    (r'admin/ncm/node/(?P<node_id>\d+)/test_login/$','ncm.views.test_login'),
    url(r'^admin/', include(admin.site.urls)),
)

