import json
import sys
import traceback
import jdatetime
from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.http import HttpResponse, Http404
from jalali_date.fields import JalaliDateField
from django.template.response import TemplateResponse
from jalali_date.widgets import AdminJalaliDateWidget

from accounts.models import Broker
from transactions.models import TopUp, PackageRecord



def is_admin(user):
    (admin_group, created) = Group.objects.get_or_create(name='admin')
    if user in admin_group.user_set.all():
        return True
    return False


class ReportForm(forms.Form):
    from_date = JalaliDateField(
        widget=AdminJalaliDateWidget
    )
    to_date = JalaliDateField(
        widget=AdminJalaliDateWidget
    )


class ReportFormAdmin(forms.Form):
    from_date = JalaliDateField(
        widget=AdminJalaliDateWidget
    )
    to_date = JalaliDateField(
        widget=AdminJalaliDateWidget
    )
    broker_id = forms.CharField(label='Broker:', widget=forms.Select(choices=[]))


class MyAdminSite(admin.AdminSite):
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        urls += [
            path('separated_report/', self.admin_view(self.separated_report), name='separated_report'),
            path('api/separated_report/', self.admin_view(self.separated_report)),
        ]
        return urls

    def separated_report(self, request, extra_context=None):
        app_list = self.get_app_list(request)
        if request.user.is_superuser or is_admin(request.user):
            BROKER_CHOICES = [('none', 'ALL')]
            for i in Broker.get_brokers():
                BROKER_CHOICES.append(i)
        report_dictionary = [{}]
        report_dictionary_package_record = [{}]

        if request.method == 'GET':
            if request.GET.get('from_date') and request.GET.get('to_date') and request.GET.get('broker_id') and (request.user.is_superuser or is_admin(request.user)):
                report_form = ReportFormAdmin(
                    initial={'from_date': request.GET.get('from_date'), 'to_date': request.GET.get('to_date'),
                             'broker_id': request.GET.get('broker_id')})
                report_form.fields['broker_id'] = forms.ChoiceField(widget=forms.Select, choices=BROKER_CHOICES)

                try:
                    from_date_list = request.GET.get('from_date').split('-')
                    to_date_list = request.GET.get('to_date').split('-')
                    broker_id = request.GET.get('broker_id')
                    from_date = jdatetime.date(int(from_date_list[0]), int(from_date_list[1]),
                                               int(from_date_list[2]))
                    to_date = jdatetime.date(int(to_date_list[0]), int(to_date_list[1]), int(to_date_list[2]))
                    if broker_id != 'none':
                        try:
                            broker = Broker.objects.get(pk=broker_id)
                            report_dictionary = TopUp.report(broker.user, from_date, to_date)
                            report_dictionary_package_record = PackageRecord.report(broker.user, from_date,
                                                                                    to_date)

                        except Broker.DoesNotExist:
                            raise Http404("شما دسترسی به این گزارش را ندارید.")
                    else:
                        report_dictionary = TopUp.report(request.user, from_date, to_date)
                        report_dictionary_package_record = PackageRecord.report(request.user, from_date, to_date)
                except PermissionError as e:
                    return HttpResponse(e.__str__())
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                    raise HttpResponse("تاریخ ورودی صحیح نیست.")
            elif request.GET.get('from_date') and request.GET.get('to_date') and not (request.user.is_superuser or is_admin(request.user)):
                report_form = ReportForm(
                    initial={'from_date': request.GET.get('from_date'), 'to_date': request.GET.get('to_date')})
                try:
                    from_date_list = request.GET.get('from_date').split('-')
                    to_date_list = request.GET.get('to_date').split('-')
                    from_date = jdatetime.date(int(from_date_list[0]), int(from_date_list[1]), int(from_date_list[2]))
                    to_date = jdatetime.date(int(to_date_list[0]), int(to_date_list[1]), int(to_date_list[2]))
                    report_dictionary = TopUp.report(request.user, from_date, to_date)
                    report_dictionary_package_record = PackageRecord.report(request.user, from_date, to_date)
                # MODIFY later
                except PermissionError as e:
                    return HttpResponse(e.__str__())
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                    raise HttpResponse("تاریخ ورودی صحیح نیست.")
            elif request.user.is_superuser or is_admin(request.user):
                report_form = ReportFormAdmin()
                report_form.fields['broker_id'] = forms.ChoiceField(widget=forms.Select, choices=BROKER_CHOICES)
            else:
                report_form = ReportForm()
            context = {
                **self.each_context(request),
                'title': 'گزارش فروش شارژ',
                'app_list': app_list,
                **(extra_context or {}),
                'form': report_form,
                'report_json_string': json.dumps(report_dictionary),
                'report_json_dict': report_dictionary,
                'report_dictionary_package_record': report_dictionary_package_record

            }
            return TemplateResponse(request, 'admin/charge_report.html', context)
        else:
            raise HttpResponse("این متد تعریف نشده است.")