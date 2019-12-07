import json
import sys
import traceback

import jdatetime
from django.contrib import admin
from django import forms
from django_jalali.forms import jDateField
from django.forms import SelectDateWidget
from django.http import HttpResponse, Http404
# import JalaliDateField
from jalali_date.fields import JalaliDateField
from django.template.response import TemplateResponse
from jalali_date.widgets import AdminJalaliDateWidget

from accounts.models import Broker
from transactions.models import TopUp


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
            path('separated_report/', self.admin_view(self.my_view)),
            path('api/separated_report/', self.admin_view(self.my_view)),
        ]
        return urls

    def my_view(self, request, extra_context=None):
        # app_list = self.get_app_list(request)

        report_dictionary = {}
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

                    try:
                        broker = Broker.objects.get(user=request.user)
                    except Broker.DoesNotExist:
                        raise Http404("شما دسترسی به این گزارش را ندارید.")
                    report_dictionary = TopUp.report(broker, from_date, to_date)
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                    raise Http404("تاریخ ورودی صحیح نیست.")
            else:
                report_form = ReportForm()
        context = {
            # **self.each_context(request),
            'title': 'گزارش فروش شارژ',
            # 'app_list': app_list,
            # **(extra_context or {}),
            'form': report_form,
            'report_json_string':json.dumps(report_dictionary),
            'report_json_dict': report_dictionary,

        }
        # return TemplateResponse(request, self.index_template or 'admin/index.html', context)
        return TemplateResponse(request, 'admin/charge_report.html', context)
