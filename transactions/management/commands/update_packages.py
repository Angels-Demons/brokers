
from django.core.management import BaseCommand

from interface.API import MCI
from transactions.enums import Operator
from transactions.models import Package


def update_mci_packages():
    print("************** Start Updating Packages")
    response_code, response_desc = MCI().behsa_package_query()
    if response_code == 0:
        all_mci_package = Package.objects.filter(operator=Operator.MCI.value)
        # Update current packages
        for package in all_mci_package:
            update_current_mci_package(package, response_desc)
        # Add new packages
        for res in response_desc:
            obj, created = Package.objects.get_or_create(
                package_type=int(res['Package_Type']),
                operator=Operator.MCI.value,
                defaults={'name': res['Package_Desc'], 'description': res['Package_Desc'],
                          'amount': int(res['Package_Cost'] or 999), 'system': int(res['Systems'] or 100)},
            )
            print('created: ', str(created))
    else:
        print("************* Error in updating MCCI packages!  ***********")


def update_current_mci_package(package, response):
    for res in response:
        if int(res['Package_Type']) == int(package.package_type):
            package.name = res['Package_Desc']
            package.description = res['Package_Desc']
            package.amount = int(res['Package_Cost'] or 999)
            package.system = int(res['Systems'] or 100)
            package.active = True
            package.package_duration = get_duration(res['Package_Desc'])
            package.save()
            return
    package.active = False
    package.save()

def get_duration(name):
    if name.find('1 روزه')!= -1:
        return '1'
    elif name.find('یک روزه')!= -1:
        return '1'
    elif name.find('7 روزه')!= -1:
        return '7'
    elif name.find('یک هفته') != -1:
        return '7'
    elif name.find('8 روزه')!= -1:
        return '8'
    elif name.find('30 روزه') != -1:
        return '30'
    elif name.find('سی روزه') != -1:
        return '30'
    elif name.find('یک ماهه') != -1:
        return '30'
    elif name.find('90 روزه')!= -1:
        return '90'
    elif name.find('180 روزه')!= -1:
        return '180'
    elif name.find('360 روزه')!= -1:
        return '360'
    else:
        print(name)
        return ''

class Command(BaseCommand):
    help = "Updates MCI Packages"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        update_mci_packages()
