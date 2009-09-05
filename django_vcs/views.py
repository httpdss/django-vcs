"""
Views for django_vcs

This views have group support for Pinax
"""
import os

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import get_app
from django.core.urlresolvers import reverse

from django_vcs.models import CodeRepository
from django_vcs.forms import RepositoryForm, EditRepositoryForm

try:
    notification = get_app('notification')
except ImproperlyConfigured:
    notification = None

@login_required
def repo_list(request, group_slug = None, bridge = None):
    """List of repositories 
    
    List of repositories taking into account that its has to be group-aware
    group -- group association to the repository
    bridge -- 

    """

    if bridge is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        group_base = bridge.group_base_template()
        repos = group.content_objects(CodeRepository)
    else:
        group_base = None
        #dont list repositories that belong to a group
        repos = CodeRepository.objects.filter(content_type = None)

    return render_to_response('django_vcs/repo_list.html',
                              {'group':group,
                               'group_base':group_base,
                               'repos': repos },
                              context_instance = RequestContext(request))

@login_required
def repo_add(request, group_slug = None, form_class = RepositoryForm, template_name = "django_vcs/add.html", bridge = None):
    """Add a new repository to a group or to the whole list"""
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        group_base = bridge.group_base_template()
    else:
        group_base = None

    if not request.user.is_authenticated():
        is_member = False
    else:
        if group:
            is_member = group.user_is_member(request.user)
        else:
            is_member = True

    if request.method == "POST":
        if request.user.is_authenticated():
            repository_form = form_class(request.user, group, request.POST)
            if repository_form.is_valid():
                repo = repository_form.save(commit = False)
                repo.creator = request.user
                if group:
                    group.associate(repo)
                repo.save()
                request.user.message_set.create(message = "added repository '%s'" % repo.name)
                if notification:
                    if group:
                        notify_list = group.member_queryset()
                    else:
                        notify_list = User.objects.all()
                    notify_list = notify_list.exclude(id__exact = request.user.id)
                    notification.send(notify_list, "repository_new",
                                      {"creator": request.user,
                                       "repo": repo,
                                       "group": group})
                if group:
                    redirect_to = bridge.reverse("repo_list", group)
                else:
                    redirect_to = reverse("repo_list")
                return HttpResponseRedirect(redirect_to)
    else:
        repository_form = form_class(request.user, group)

    return render_to_response(template_name, {
        "group": group,
        "is_member": is_member,
        "repository_form": repository_form,
        "group_base": group_base,
    }, context_instance = RequestContext(request))


def repo_delete(request, slug, group_slug = None, bridge = None):

    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        group_base = bridge.group_base_template()
        repos = group.content_objects(CodeRepository)
    else:
        repos = CodeRepository.objects.filter(object_id = None)
        group_base = None

    repo = get_object_or_404(repos, slug = slug)

    repo_name = repo.name

    if group:
        redirect_to = bridge.reverse("repo_list", group)
    else:
        redirect_to = reverse("repo_list")

    if repo.creator != request.user:
        request.user.message_set.create(message = "You can't delete repositories that aren't yours")
        return HttpResponseRedirect(redirect_to)

    repo.delete()
    request.user.message_set.create(message = "Successfully deleted repository '%s'" % repo_name)

    return HttpResponseRedirect(redirect_to)


def repo_edit(request, slug,
              form_class = EditRepositoryForm,
              template_name = "django_vcs/edit.html",
              group_slug = None, bridge = None):

    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        group_base = bridge.group_base_template()
        repos = group.content_objects(CodeRepository)
    else:
        repos = CodeRepository.objects.filter(object_id = None)
        group_base = None

    if not request.user.is_authenticated():
        is_member = False
    else:
        if group:
            is_member = group.user_is_member(request.user)
        else:
            is_member = True

    repo = get_object_or_404(repos, slug = slug)

    if group:
        redirect_to = bridge.reverse("repo_list", group)
    else:
        redirect_to = reverse("repo_list")

#    if repo.creator != request.user:
#        request.user.message_set.create(message = "You can't edit repositories that aren't yours")
#        return HttpResponseRedirect(redirect_to)

    if is_member and request.method == "POST":
        form = form_class(request.user, group, request.POST, instance = repo)
        if form.is_valid():
            repo = form.save()
            request.user.message_set.create(message = "Repository has been updated succesfully")
            return HttpResponseRedirect(redirect_to)
    else:
        form = form_class(request.user, group, instance = repo)

    return render_to_response(template_name, {
        "group": group,
        "is_member": is_member,
        "form": form,
        "group_base": group_base,
    }, context_instance = RequestContext(request))

@login_required
def recent_commits(request, slug, group_slug = None, bridge = None):
    """List of recent commits from a given repository
    
    Keyword Arguments:
    slug -- the repository slug
    group -- group association to the repository
    bridge -- 
    
    """

    if bridge is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        group_base = bridge.group_base_template()
        repos = group.content_objects(CodeRepository)
    else:
        repos = CodeRepository.objects.filter(object_id = None)
        group_base = None

    repo = get_object_or_404(repos, slug = slug)
    commits = repo.get_recent_commits()
    return render_to_response([
        'django_vcs/%s/recent_commits.html' % repo.name,
        'django_vcs/recent_commits.html',
    ], {'group':group, 'group_base':group_base, 'repo': repo, 'commits': commits}, context_instance = RequestContext(request))

@login_required
def code_browser(request, slug, path, group_slug = None, bridge = None):
    """Source code browser for a given repository
        
    Keyword Arguments:
    slug -- the repository slug
    path -- path inside the repository
    group -- group association to the repository
    bridge -- 
        
    """

    if bridge is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        group_base = bridge.group_base_template()
        repos = group.content_objects(CodeRepository)
    else:
        group_base = None
        repos = CodeRepository.objects.filter(object_id = None)

    repo = get_object_or_404(repos, slug = slug)
    rev = request.GET.get('rev') or None
    context = {'repo': repo, 'path': path}
    file_contents = repo.get_file_contents(path, rev)

    if file_contents is None:
        folder_contents = repo.get_folder_contents(path, rev)
        if folder_contents is None:
            raise Http404
        context['files'], context['folders'] = folder_contents
        context['files'] = [(os.path.join(path, o), o) for o in context['files']]
        context['folders'] = [(os.path.join(path, o), o) for o in context['folders']]
        return render_to_response([
            'django_vcs/%s/folder_contents.html' % repo.name,
            'django_vcs/folder_contents.html',
        ], context, context_instance = RequestContext(request))
    context['file'] = file_contents
    context['group'] = group
    context['group_base'] = group_base
    return render_to_response([
        'django_vcs/%s/file_contents.html' % repo.name,
        'django_vcs/file_contents.html',
    ], context, context_instance = RequestContext(request))

@login_required
def commit_detail(request, slug, commit_id, group_slug = None, bridge = None):
    """Get details for a given commit
        
    slug -- the repository slug
    commit_id -- identifier of the commit
    group -- group association to the repository
    bridge -- 
    
    """

    if bridge is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        group_base = bridge.group_base_template()
        repos = group.content_objects(CodeRepository)
    else:
        group_base = None
        repos = CodeRepository.objects.filter(object_id = None)

    repo = get_object_or_404(repos, slug = slug)

    commit = repo.get_commit(commit_id)
    if commit is None:
        raise Http404
    return render_to_response([
        'django_vcs/%s/commit_detail.html' % repo.name,
        'django_vcs/commit_detail.html',
    ],
    {'group':group,
     'group_base':group_base,
     'repo': repo,
     'commit': commit},
     context_instance = RequestContext(request))
