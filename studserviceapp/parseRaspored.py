from datetime import datetime

import pytz

from studserviceapp import database
from studserviceapp.models import *


# exec(open('studserviceapp/parseRaspored.py').read())


def poziv(unos, br):
    if br % 8 == 0:
        pass
    elif br % 8 == 1:
        nastavnik(unos, br)
    elif br % 8 == 2:
        sifra(unos)
    elif br % 8 == 3:
        odeljenje(unos)
    elif br % 8 == 4:
        nedelja(unos)
    elif br % 8 == 5:
        dan(unos)
    elif br % 8 == 6:
        cas(unos)
    elif br % 8 == 7:
        ucionica(unos)
    else:
        raise ValueError


trenutni_predmet = None

trenutni_nastavnik = None

trenutni_tip_nastave = None

trenutna_odeljenja = []

trenutni_dan = None

trenutni_cas = None


def predmet(unos):
    database.sacuvaj_predmet(naziv=unos)

    global trenutni_predmet
    trenutni_predmet = Predmet.objects.get(naziv=unos)


def nastavnik(unos, brojac):
    prezime = unos[0:unos.find(' ')]
    ime = unos[unos.find(' ') + 1:len(unos)]

    database.sacuvaj_nastavnika(ime=ime, prezime=prezime, predmet=trenutni_predmet)

    global trenutni_tip_nastave, trenutni_nastavnik

    trenutni_tip_nastave = nivo_nastave(brojac)
    trenutni_nastavnik = Nastavnik.objects.get(ime=ime, prezime=prezime)


def nivo_nastave(brojac):
    if brojac == 1:
        tip_nastave = 'Predavanje'
    elif brojac == 9:
        tip_nastave = 'Praktikum'
    elif brojac == 17:
        tip_nastave = 'Vezbe'
    elif brojac == 25:
        tip_nastave = 'pred i vezb'
    else:
        raise ValueError

    return tip_nastave


def sifra(unos):
    pass


def odeljenje(unos):
    duzina_unosa = unos.count(',') + 1
    lista_odeljenja = list(range(duzina_unosa))

    for brojac in range(0, duzina_unosa):

        if brojac == duzina_unosa - 1:
            lista_odeljenja[brojac] = unos
            continue

        lista_odeljenja[brojac] = unos[0:unos.find(',')]
        unos = unos[unos.find(' ') + 1:len(unos)]

    database.sacuvaj_semestar(vrsta="neparni", skolska_godina_pocetak=2018, skolska_godina_kraj=2019)
    database.sacuvaj_semestar(vrsta="parni", skolska_godina_pocetak=2018, skolska_godina_kraj=2019)

    neparni_semestar = Semestar.objects.get(vrsta="neparni", skolska_godina_pocetak=2018, skolska_godina_kraj=2019)

    global trenutna_odeljenja

    for grupa in lista_odeljenja:
        database.sacuvaj_grupu(oznaka_grupe=grupa, semestar=neparni_semestar)
        trenutna_odeljenja.append(Grupa.objects.get(oznaka_grupe=grupa))


def nedelja(unos):
    pass


def dan(unos):
    unos = unos.replace('ÈET', 'ČET')

    global trenutni_dan
    trenutni_dan = unos


def cas(unos):
    global trenutni_cas
    trenutni_cas = unos


def ucionica(unos):
    tokeni = trenutni_cas.split("-")
    pocetak_string = tokeni[0]
    zavrsetak_string = tokeni[1] + ":00"

    pocetak = datetime.strptime(pocetak_string, "%H:%M")
    zavrsetak = datetime.strptime(zavrsetak_string, "%H:%M")

    neparni_semestar = Semestar.objects.get(vrsta="neparni", skolska_godina_pocetak=2018, skolska_godina_kraj=2019)

    database.sacuvaj_raspored_nastave(datum_unosa="2018-10-29 10:58:20.610014+00:00", semestar=neparni_semestar)

    raspored_nastave = RasporedNastave.objects.get(datum_unosa="2018-10-29 10:58:20.610014+00:00",
                                                   semestar=neparni_semestar)

    global trenutna_odeljenja

    database.sacuvaj_termin(oznaka_ucionice=unos, pocetak=pocetak, zavrsetak=zavrsetak, dan=trenutni_dan,
                            tip_nastave=trenutni_tip_nastave, nastavnik=trenutni_nastavnik,
                            predmet=trenutni_predmet, raspored=raspored_nastave, grupe=trenutna_odeljenja)

    trenutna_odeljenja = []

    print("Dodavanje termina za ucionicu: " + unos)


def fajlZaParse(putanja):
    i = 0

    f = open('resources/' + putanja, 'r')

    for s in f:
        # br = 0
        if i < 3:
            i = i + 1
            # Moze da se ubaci IF za i=3 gde ce da prodje kroz red,
            # uzme pojmove i njih koristi za nivoNastave,
            # u nasem slucaju to su Predavanja, Praktikum, Vezbe i Predavanja i vezbe
        elif s[0] == '"':
            u = s[1:len(s) - 3]
            predmet(u)
            continue
            # print(unos)
        elif s.__contains__('Nastavnik') or s[0] == '\n':
            continue
        elif s[0] == ';':
            # br moze da bude count od ; u s, u nasem slucaju je 33
            for br in range(0, 33):
                u = s[0:s.find(';')]
                u = u[1:len(u) - 1]
                s = s[s.find(';') + 1:len(s)]
                if u != '':
                    poziv(u, br)
        else:
            pass

    f.close()
    dodaj_podatke()


def dodaj_podatke():
    grupa_303 = Grupa.objects.get(oznaka_grupe="303")

    database.sacuvaj_studenta(ime="Uros", prezime="Vardic", broj_indeksa=73,
                              godina_upisa=2017, smer="RN", grupa=grupa_303)

    database.sacuvaj_studenta(ime="Alen", prezime="Akif", broj_indeksa=45,
                              godina_upisa=2015, smer="RN", grupa=grupa_303)

    database.sacuvaj_studenta(ime="Jovan", prezime="Gavrilovic",
                              broj_indeksa=81, godina_upisa=2016, smer="RN", grupa=grupa_303)

    database.sacuvaj_studenta(ime="Djordje", prezime="Veljkovic",
                              broj_indeksa=46, godina_upisa=2015, smer="RN", grupa=grupa_303)

    database.sacuvaj_sekretara(ime='Mara', prezime='Arbutina')

    database.sacuvaj_administratora(ime='A', prezime='dmin')

    for j in range(0, 5):
        database.sacuvaj_obavestenje(postavio=Nalog.objects.get(username='admin'),
                                     datum_postavljanja=datetime.now(pytz.UTC), tekst='Neki tekst')


# fajlZaParse(open('resources/rasporedCSV.csv', 'r'))
