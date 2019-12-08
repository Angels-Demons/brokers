import json
import sys
import traceback

import jdatetime
import pandas as pd
from django.contrib import admin
from django import forms
from django.shortcuts import redirect
from django.urls import reverse
from django_jalali.forms import jDateField
from django.forms import SelectDateWidget
from django.http import HttpResponse, Http404
# import JalaliDateField
from jalali_date.fields import JalaliDateField
from django.template.response import TemplateResponse
from jalali_date.widgets import AdminJalaliDateWidget

from accounts.models import Broker
from transactions.models import TopUp, PackageRecord


class ReportForm(forms.Form):
    from_date = JalaliDateField(
        widget=AdminJalaliDateWidget
        # widget=SelectDateWidget("Choose Year", "Choose Month", "Choose Day")
    )
    to_date = JalaliDateField(
        widget=AdminJalaliDateWidget
        # widget=SelectDateWidget("Choose Year", "Choose Month", "Choose Day")
    )


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

        report_dictionary = [{}]
        report_dictionary_package_record = [{}]
        if request.method == 'GET':
            if request.GET.get('from_date') and request.GET.get('to_date'):
                report_form = ReportForm(initial={'from_date': request.GET.get('from_date'), 'to_date':request.GET.get('to_date')})
                try:
                    print(request.GET.get('from_date'))
                    from_date_list = request.GET.get('from_date').split('-')
                    to_date_list = request.GET.get('to_date').split('-')
                    print(request.GET.get('to_date'))

                    # from_date = jdatetime.date(int(from_date_list[0]), int(from_date_list[1]), int(from_date_list[
                    # 2]), locale='fa_IR') to_date = jdatetime.date(int(to_date_list[0]), int(to_date_list[1]),
                    # int(to_date_list[2]), locale='fa_IR')
                    from_date = jdatetime.date(int(from_date_list[0]), int(from_date_list[1]), int(from_date_list[2]))
                    to_date = jdatetime.date(int(to_date_list[0]), int(to_date_list[1]), int(to_date_list[2]))

                    # try:
                    #     broker = Broker.objects.get(user=request.user)
                    # except Broker.DoesNotExist:
                    #     raise Http404("شما دسترسی به این گزارش را ندارید.")
                    report_dictionary = TopUp.report(request.user, from_date, to_date)
                    report_dictionary_package_record = PackageRecord.report(request.user, from_date, to_date)
                    # for i in report_dictionary_package_record:
                    #     report_dictionary.append(i)
                    # if 'xlsx' in request.GET:
                    #     return redirect(reverse('ChargeSaleReport'), from_date=from_date, to_date=to_date )
                        # return redirect(reverse('transactions.views.report_view'), from_date=from_date, to_date=to_date)
                        # return pd.DataFrame.from_dict(data=report_dictionary)
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                    raise Http404("تاریخ ورودی صحیح نیست.")
            else:
                report_form = ReportForm()
        context = {
            **self.each_context(request),
            'title': 'گزارش فروش شارژ',
            'app_list': app_list,
            **(extra_context or {}),
            'form': report_form,
            'report_json_string':json.dumps(report_dictionary),
            'report_json_dict': report_dictionary,
            'report_dictionary_package_record': report_dictionary_package_record

        }
        # return TemplateResponse(request, self.index_template or 'admin/index.html', context)
        return TemplateResponse(request, 'admin/charge_report.html', context)
