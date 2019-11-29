# encoding: utf-8
# from django.core.urlresolvers import reverse
import datetime
import json
from django.template import Context
from django.utils import translation
from jet import settings
from jet.models import PinnedApplication

try:
    from django.apps.registry import apps
except ImportError:
    try:
        from django.apps import apps  # Fix Django 1.7 import issue
    except ImportError:
        pass
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

try:
    from django.core.urlresolvers import reverse, resolve, NoReverseMatch
except ImportError:  # Django 1.11
    from django.urls import reverse, resolve, NoReverseMatch

from django.contrib.admin import AdminSite
from django.utils.encoding import smart_text
from django.utils.text import capfirst
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

try:
    from collections import OrderedDict
except ImportError:
    pass
from django.contrib.admin.models import LogEntry

from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard
from django.db.models import Q

# from jet.utils import get_admin_site_name
# from jet.dashboard.dashboard_modules import google_analytics


# class CustomIndexDashboard(Dashboard):
#     columns = 3
#
#     def init_with_context(self, context):
#         self.available_children.append(modules.LinkList)
#         self.available_children.append(modules.Feed)
#
#         self.available_children.append(google_analytics.GoogleAnalyticsVisitorsTotals)
#         self.available_children.append(google_analytics.GoogleAnalyticsVisitorsChart)
#         self.available_children.append(google_analytics.GoogleAnalyticsPeriodVisitors)
#
#         site_name = get_admin_site_name(context)
#         # append a link list module for "quick links"
#         self.children.append(modules.LinkList(
#             _('Quick links'),
#             layout='inline',
#             draggable=False,
#             deletable=False,
#             collapsible=False,
#             children=[
#                 [_('Return to site'), '/'],
#                 [_('Change password'),
#                  reverse('%s:password_change' % site_name)],
#                 [_('Log out'), reverse('%s:logout' % site_name)],
#             ],
#             column=0,
#             order=0
#         ))
#
#         # append an app list module for "Applications"
#         self.children.append(modules.AppList(
#             _('Applications'),
#             exclude=('auth.*',),
#             column=1,
#             order=0
#         ))
#
#         # append an app list module for "Administration"
#         self.children.append(modules.AppList(
#             _('Administration'),
#             models=('auth.*',),
#             column=2,
#             order=0
#         ))
#
#         # append a recent actions module
#         self.children.append(modules.RecentActions(
#             _('Recent Actions'),
#             10,
#             column=0,
#             order=1
#         ))
#
#         # append a feed module
#         self.children.append(modules.Feed(
#             _('Latest Django News'),
#             feed_url='http://www.djangoproject.com/rss/weblog/',
#             limit=5,
#             column=1,
#             order=1
#         ))
#
#         # append another link list module for "support".
#         self.children.append(modules.LinkList(
#             _('Support'),
#             children=[
#                 {
#                     'title': _('Django documentation'),
#                     'url': 'http://docs.djangoproject.com/',
#                     'external': True,
#                 },
#                 {
#                     'title': _('Django "django-users" mailing list'),
#                     'url': 'http://groups.google.com/group/django-users',
#                     'external': True,
#                 },
#                 {
#                     'title': _('Django irc channel'),
#                     'url': 'irc://irc.freenode.net/django',
#                     'external': True,
#                 },
#             ],
#             column=2,
#             order=1
#         ))
#
#
# class CustomAppIndexDashboard(AppIndexDashboard):
#     def init_with_context(self, context):
#         self.available_children.append(modules.LinkList)
#
#         self.children.append(modules.ModelList(
#             title=_('Application models'),
#             models=self.models(),
#             column=0,
#             order=0
#         ))
#         self.children.append(modules.RecentActions(
#             include_list=self.get_app_content_types(),
#             column=1,
#             order=0
#         ))
from jet.dashboard.modules import AppList, ModelList
from jet.utils import get_admin_site


def my_get_app_list(context, order=True):
    admin_site = get_admin_site(context)
    request = context['request']

    app_dict = {}
    for model, model_admin in admin_site._registry.items():
        app_label = model._meta.app_label
        try:
            has_module_perms = model_admin.has_module_permission(request)
        except AttributeError:
            has_module_perms = request.user.has_module_perms(app_label)  # Fix Django < 1.8 issue

        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                info = (app_label, model._meta.model_name)
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'object_name': model._meta.object_name,
                    'perms': perms,
                    'model_name': model._meta.model_name
                }
                if perms.get('change', False):
                    try:
                        model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=admin_site.name)
                    except NoReverseMatch:
                        pass
                if perms.get('add', False):
                    try:
                        model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=admin_site.name)
                    except NoReverseMatch:
                        pass
                if perms.get('view', False):
                    try:
                        model_dict['view_url'] = reverse('admin:%s_%s_changelist' % info, current_app=admin_site.name)
                    except NoReverseMatch:
                        pass
                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    try:
                        name = apps.get_app_config(app_label).verbose_name
                    except NameError:
                        name = app_label.title()
                    app_dict[app_label] = {
                        'name': name,
                        'app_label': app_label,
                        'app_url': reverse(
                            'admin:app_list',
                            kwargs={'app_label': app_label},
                            current_app=admin_site.name,
                        ),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }

    # Sort the apps alphabetically.
    app_list = list(app_dict.values())

    if order:
        app_list.sort(key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

    return app_list


class MyModelList(ModelList):
    def init_with_context(self, context):
        app_list = my_get_app_list(context)
        models = []

        for app in app_list:
            app_name = app.get('app_label', app.get('name', ''))
            app['models'] = filter(
                lambda model: self.models is None or ('%s.%s' % (app_name, model['object_name'])) in self.models or ('%s.*' % app_name) in self.models,
                app['models']
            )
            app['models'] = filter(
                lambda model: self.exclude is None or (('%s.%s' % (app_name, model['object_name'])) not in self.exclude and ('%s.*' % app_name) not in self.exclude),
                app['models']
            )
            app['models'] = list(app['models'])

            models.extend(app['models'])

        self.children = models


class MyAppList(AppList):
    def init_with_context(self, context):
        # changed
        app_list = my_get_app_list(context)
        app_to_remove = []

        for app in app_list:
            app_name = app.get('app_label', app.get('name', ''))
            app['models'] = filter(
                lambda model: self.models is None or ('%s.%s' % (app_name, model['object_name'])) in self.models or (
                            '%s.*' % app_name) in self.models,
                app['models']
            )
            app['models'] = filter(
                lambda model: self.exclude is None or (
                            ('%s.%s' % (app_name, model['object_name'])) not in self.exclude and (
                                '%s.*' % app_name) not in self.exclude),
                app['models']
            )
            app['models'] = list(app['models'])

            if self.hide_empty and len(list(app['models'])) == 0:
                app_to_remove.append(app)

        for app in app_to_remove:
            app_list.remove(app)

        self.children = app_list


class MyRecentActions(modules.RecentActions):

    def __init__(self, title=None, limit=10, **kwargs):
        # self.user = user
        kwargs.update({'limit': limit})
        # kwargs.update({'user': user})
        super(MyRecentActions, self).__init__(title, **kwargs)

    # def load_settings(self, settings):
    #     self.limit = settings.get('limit', self.limit)
    #     self.include_list = settings.get('include_list')
    #     self.exclude_list = settings.get('exclude_list')
    #     self.user = settings.get('user', self.user)

    def init_with_context(self, context):

        def get_qset(list):
            qset = None
            for contenttype in list:
                try:
                    app_label, model = contenttype.split('.')

                    if model == '*':
                        current_qset = Q(
                            content_type__app_label=app_label
                        )
                    else:
                        current_qset = Q(
                            content_type__app_label=app_label,
                            content_type__model=model
                        )
                except:
                    raise ValueError('Invalid contenttype: "%s"' % contenttype)

                if qset is None:
                    qset = current_qset
                else:
                    qset = qset | current_qset
            return qset

        qs = LogEntry.objects
        if self.user:
            qs = qs.filter(
                user__pk=int(self.user)
            )

        if self.include_list:
            qs = qs.filter(get_qset(self.include_list))
        if self.exclude_list:
            qs = qs.exclude(get_qset(self.exclude_list))

        self.children = qs.select_related('content_type', 'user')[:int(self.limit)]


class CustomIndexDashboard(Dashboard):
    columns = 2

    def init_with_context(self, context):
        request = context['request']
        # print(context['user'].pk)

        # self.available_children.append(modules.LinkList)
        # self.children.append(modules.LinkList(_('Support'),
        #                                       children=[
        #                                           {
        #                                               'title': _('Django documentation'),
        #                                               'url': 'http://docs.djangoproject.com/',
        #                                               'external': True,
        #                                           },
        #                                           {
        #                                               'title': _('Django "django-users" mailing list'),
        #                                               'url': 'http://groups.google.com/group/django-users',
        #                                               'external': True,
        #                                           },
        #                                           {
        #                                               'title': _('Django irc channel'),
        #                                               'url': 'irc://irc.freenode.net/django',
        #                                               'external': True,
        #                                           },
        #                                       ],
        #                                       column=0,
        #                                       order=0
        #                                       ))
        # append an app list module for "Applications"
        self.children.append(MyAppList(
            _('Applications'),
            exclude=('auth.*',),
            # draggable=False,
            # collapsible=False,
            # deletable=False,
            column=0,
            order=0,
            # enabled=False,
        ))

        #         # append an app list module for "Administration"
        self.children.append(MyAppList(
            _('Administration'),
            models=('auth.*',),
            column=0,
            order=1,
            # draggable=False,
            # collapsible=False,
            # deletable=False,
            # enabled=False,
        ))

        self.children.append(MyRecentActions(
            title=_('Recent Actions'),
            limit=10,
            user=context['request'].user.pk,
            column=1,
            order=1,
            # draggable=False,
            # collapsible=False,
            # deletable=False,

        ))


class CustomAppIndexDashboard(AppIndexDashboard):
    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)

        self.children.append(MyModelList(
            title=_('Application models'),
            models=self.models(),
            column=0,
            order=0
        ))
        self.children.append(modules.RecentActions(
            include_list=self.get_app_content_types(),
            column=1,
            order=0,
            user=context['request'].user.pk,
        ))
