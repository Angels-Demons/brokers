
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
            search_mci_package(package, response_desc)
        # Add new packages
        for res in response_desc:
            obj, created = Package.objects.get_or_create(
                package_type=int(res['Package_Type']),
                operator=Operator.MCI.value,
                defaults={'name': res['Package_Desc'], 'description': res['Package_Desc'],
                          'amount': int(res['Package_Cost'] or 999), 'system': int(res['Systems'] or 100)},
            )
        else:
            print("************* Error in updating MCCI packages!  ***********")


def search_mci_package(package, response):
    for res in response:
        if int(res['Package_Type']) == int(package.package_type):
            package.name = res['Package_Desc']
            package.description = res['Package_Desc']
            package.amount = int(res['Package_Cost'] or 999)
            package.system = int(res['Systems'] or 100)
            package.active = True
            package.save()
            return
    package.active = False
    package.save()


class Command(BaseCommand):
    help = "Updates MCI Packages"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        update_mci_packages()
