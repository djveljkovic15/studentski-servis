from django.core.management.base import BaseCommand
from studserviceapp.parseTerminPolaganja import CSVParser


class Command(BaseCommand):
    def handle(self, *args, **options):

        csv_parser = CSVParser("1", "resources/kol1.csv")
        csv_parser.parse_file()

        for k, v in csv_parser.parsing_error.error_messages.items():
            print(v)
