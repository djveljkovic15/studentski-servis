# exec(open('studserviceapp/parseTerminPolaganja.py').read())
import csv
from enum import Enum

from datetime import datetime, time

from studserviceapp import database
from studserviceapp.models import Predmet, Nastavnik, RasporedPolaganja


class ParsingError(object):

    def __init__(self) -> None:
        self.error_messages = dict()

    def add_error_msg(self, row, field, value, desc):
        msg = ErrorMessage()
        msg.field = field
        msg.description = desc
        msg.value = value
        msg.row = row

        if self.error_messages.get(row) is None:
            self.error_messages[row] = [msg]
        else:
            self.error_messages[row].append(msg)

    def is_errorles(self):
        return len(self.error_messages) == 0

    # Python ne potrzava overload metoda
    # Ovo bi trebalo da se napise kao is_errorless(self, row=None), gde je row opcioni argument
    def is_errorles(self, row):
        return self.error_messages.get(row) is None


class ErrorMessage(object):
    def __init__(self) -> None:
        self.row = None
        self.field = None
        self.value = None
        self.description = None

    def __str__(self) -> str:
        return "Red:{} Polje:{} Vrednost:{} Poruka:{}".format(self.row, self.field, self.value, self.description)

    def __repr__(self) -> str:
        return str(self)


class CSVKey(Enum):
    PREDMET = "Predmet"
    PROFESOR = "Profesor"
    UCIONICE = "Ucionice"
    VREME = "Vreme"
    DAN = "Dan"
    DATUM = "Datum"
    RASPORED_POLAGANJA = "Raspored polaganja"


class Days(object):
    supported_values = ["Ponedeljak", "Utorak", "Sreda", "Četvrtak", "Petak", "Subota", "Nedelja"]

    @staticmethod
    def supports(value):
        return any(value == item for item in Days.supported_values)


class CSVParser(object):

    def __init__(self, raspored_polaganja, file_path):
        self.file_path = file_path
        self.raspored_polaganja = raspored_polaganja
        self.parsing_error = ParsingError()

    def parse_file(self):
        with open(self.file_path, mode='r', encoding='utf8') as csv_stream:
            csv_reader = csv.DictReader(csv_stream)
            for row, content in enumerate(csv_reader):
                self._store_entry(row, content)

    def parse_subject(self, row, content):
        # PREDMET
        subject = None
        subject_name = content.get(CSVKey.PREDMET.value)
        if not subject_name:
            self.parsing_error.add_error_msg(row, CSVKey.PREDMET.value, subject_name, "Predmet je obavezno polje")
        else:
            subject = Predmet.objects.filter(naziv=subject_name).first()

            if not subject:
                self.parsing_error.add_error_msg(row, CSVKey.PREDMET.value, subject_name, "Nije moguce naci predmet")

        return subject

    def parse_teacher(self, row, content):
        # PROFESOR
        teacher = None
        full_name = content.get(CSVKey.PROFESOR.value)

        if not full_name:
            self.parsing_error.add_error_msg(row, CSVKey.PROFESOR.value, full_name, "Profesor je obavezno polje")
        else:
            name, last_name = full_name.split(" ", 1)
            teacher = Nastavnik.objects.filter(ime=name, prezime=last_name).first()

            if not teacher:
                self.parsing_error.add_error_msg(row, CSVKey.PROFESOR.value, full_name, "Nije moguce naci profesora")

        return teacher

    def parse_schedule(self, row):
        # RASPORED PREDAVANJA
        schedule = RasporedPolaganja.objects.filter(kolokvijumska_nedelja=self.raspored_polaganja).first()
        if not schedule:
            self.parsing_error.add_error_msg(row, CSVKey.RASPORED_POLAGANJA.value, self.raspored_polaganja, "Nije moguce naci raspored polaganja")

        return schedule

    def parse_classrooms(self, row, content):
        # UCIONICE
        classrooms = content.get(CSVKey.UCIONICE.value)
        if not classrooms:
            self.parsing_error.add_error_msg(row, CSVKey.UCIONICE.value, classrooms, "Ucionice je obavezno polje")

        return classrooms

    def parse_time_period(self, row, content):
        # VREME
        time_period = content.get(CSVKey.VREME.value)
        if not time_period:
            self.parsing_error.add_error_msg(row, CSVKey.VREME.value, time_period, "Vreme je obavezno polje")

        start, stop = time_period.split("-")

        if int(start) > 24:
            self.parsing_error.add_error_msg(row, CSVKey.VREME.value, start, "Pocetno vreme ne sme biti veci od 24h")

        if int(stop) > 24:
            self.parsing_error.add_error_msg(row, CSVKey.VREME.value, stop, "Zavrsno vreme ne sme biti veci od 24h")

        if int(start) > int(stop):
            self.parsing_error.add_error_msg(row, CSVKey.VREME.value, time_period, "Pocetno vreme mora biti pre zavrsnog")

        return time(hour=int(start)), time(hour=int(stop))

    def parse_date(self, row, content):
        # UCIONICE
        parsed_date = None
        date = content.get(CSVKey.DATUM.value)

        if not date:
            self.parsing_error.add_error_msg(row, CSVKey.DATUM.value, date, "Datum je obavezno polje")

        try:
            parsed_date = datetime.strptime("{}{}".format(date, str(datetime.today().year)), "%d.%m.%Y")
        except:
            self.parsing_error.add_error_msg(row, CSVKey.DATUM.value, date, "Datum nije ispravan")

        return parsed_date

    def parse_day(self, row, content):
        day = content.get(CSVKey.DAN.value)

        if not day:
            self.parsing_error.add_error_msg(row, CSVKey.DAN.value, day, "Dan je obavezno polje")

        if not Days().supports(day):
            self.parsing_error.add_error_msg(row, CSVKey.DAN.value, day, "Dan je pogresnog formata")

        return day


    #dorada
    #danas = datetime.today()
    #trenutni_datum = datetime(danas.year, danas.month, danas.day)
    #if int(trenutni_datum) >= '17.11' & int(trenutni_datum)<=25.11:
    #database.sacuvaj_raspored_polaganja(ispitni_rok=,kolokvijumska_nedelja=)




    def _store_entry(self, row, content, store=False):
        classrooms = self.parse_classrooms(row, content)
        schedule = self.parse_schedule(row)
        subject = self.parse_subject(row, content)
        teacher = self.parse_teacher(row, content)
        start, stop = self.parse_time_period(row, content)
        date = self.parse_date(row, content)
        day = self.parse_day(row, content)

        if not self.parsing_error.is_errorles(row) and store:
            database.sacuvaj_termin_polaganja(ucionice=classrooms, pocetak=start, zavrsetak=stop, datum=date,
                                              dan=day, raspored_polaganja=schedule, predmet=subject,
                                              nastavnik=teacher)
