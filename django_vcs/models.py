from itertools import count

from django.db import models
from django.conf import settings

#for groups support
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _



from pyvcs.backends import AVAILABLE_BACKENDS, get_backend
from pyvcs.exceptions import CommitDoesNotExist, FileDoesNotExist, FolderDoesNotExist

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

REPOSITORY_TYPES = zip(count(), AVAILABLE_BACKENDS.keys())

class CodeRepository(models.Model):
    name = models.CharField(max_length = 255)
    slug = models.SlugField()

    repository_type = models.IntegerField(choices = REPOSITORY_TYPES)

    location = models.CharField(max_length = 255)

    creator = models.ForeignKey(User, related_name = "created_repositories", verbose_name = _('creator'))
    object_id = models.IntegerField(null = True)
    content_type = models.ForeignKey(ContentType, null = True)
    group = generic.GenericForeignKey("object_id", "content_type")

    class Meta:
        verbose_name_plural = "Code Repositories"

    def __unicode__(self):
        return "%s: %s" % (self.get_repository_type_display(), self.name)

    @models.permalink
    def get_absolute_url(self, group = None):
        kwargs = {"slug": self.slug}
        if group:
            return group.content_bridge.reverse("recent_commits", group, kwargs)
        return reverse("recent_commits", kwargs = kwargs)

    @property
    def repo(self):
        if hasattr(self, '_repo'):
            return self._repo
        self._repo = get_backend(self.get_repository_type_display()).Repository(self.location)
        return self._repo

    def get_commit(self, commit_id):
        try:
            return self.repo.get_commit_by_id(str(commit_id))
        except CommitDoesNotExist:
            return None

    def get_recent_commits(self, since = None):
        return self.repo.get_recent_commits(since = since)

    def get_folder_contents(self, path, rev = None):
        try:
            if rev is not None:
                rev = str(rev)
            return self.repo.list_directory(path, rev)
        except FolderDoesNotExist:
            return None

    def get_file_contents(self, path, rev = None):
        try:
            if rev is not None:
                rev = str(rev)
            return self.repo.file_contents(path, rev)
        except FileDoesNotExist:
            return None
