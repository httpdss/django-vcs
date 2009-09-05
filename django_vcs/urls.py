from django.conf.urls.defaults import *

from projects.models import Project
from groups.bridge import ContentBridge

bridge = ContentBridge(Project, 'projects')

urlpatterns = patterns('django_vcs.views',
    url(r'^$', 'repo_list', name = 'repo_list'),
    url(r'^add/$', 'repo_add', name = 'repo_add'),
    url(r'^edit/(?P<slug>[\w-]+)/$', 'repo_edit', name = 'repo_edit'),
    url(r'^delete/(?P<slug>[\w-]+)/$', 'repo_delete', name = 'repo_delete'),
    url(r'^(?P<slug>[\w-]+)/$', 'recent_commits', name = 'recent_commits'),
    url(r'^(?P<slug>[\w-]+)/browser/(?P<path>.*)$', 'code_browser', name = 'code_browser'),
    url(r'^(?P<slug>[\w-]+)/commit/(?P<commit_id>.*)/$', 'commit_detail', name = 'commit_detail'),
)

urlpatterns += bridge.include_urls('django_vcs.urls', r'^project/(?P<group_slug>[-\w]+)/repositories/')
