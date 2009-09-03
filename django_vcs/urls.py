from django.conf.urls.defaults import *

from projects.models import Project

urlpatterns = patterns('django_vcs.views',
    url(r'^$', 'repo_list', name='repo_list'),
    url(r'^add/$', 'add_repo', name='add_repo'),
    url(r'^(?P<slug>[\w-]+)/$', 'recent_commits', name='recent_commits'),
    url(r'^(?P<slug>[\w-]+)/browser/(?P<path>.*)$', 'code_browser', name='code_browser'),
    url(r'^(?P<slug>[\w-]+)/commit/(?P<commit_id>.*)/$', 'commit_detail', name='commit_detail'),
)

