"""
@author: Kenneth Belitzky <kenny@belitzky.com>
"""

from django import forms
from django.utils.translation import ugettext as _

from django_vcs.models import CodeRepository

class RepositoryForm(forms.ModelForm):
    """Add new repository form"""
    def __init__(self, user, group, *args, **kwargs):
        self.user = user
        self.group = group

        super(RepositoryForm, self).__init__(*args, **kwargs)

    def save(self, commit = True):
        return super(RepositoryForm, self).save(commit)

    class Meta:
        model = CodeRepository
        fields = ('name', 'slug', 'repository_type', 'location')

    def clean(self):
        self.check_group_membership()
        return self.cleaned_data

    def check_group_membership(self):
        group = self.group
        if group and not self.group.user_is_member(self.user):
            raise forms.ValidationError(_("You must be a member to create tasks"))