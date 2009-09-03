from django.db.models import signals, get_app
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_noop as _

try:
    notification = get_app('notification')
    
    # @@@ when implemented need to add back "in a project you're a member of" or similar
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("repository_new", _("New Repository"), _("a new repository been created"), default=2)
        
    signals.post_syncdb.connect(create_notice_types, sender=notification)
except ImproperlyConfigured:
    print "Skipping creation of NoticeTypes as notification app not found"
