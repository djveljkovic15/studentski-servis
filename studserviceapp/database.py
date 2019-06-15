import os
import django

from studserviceapp.models import *

os.environ.setdefault('DJANGO_SETTINGS_MODEL', 'studservice.settings')

django.setup()


# Pokretanje skripte sa komandom: ./manage.py shell < studserviceapp/database.py
# Takodje moze da se udje u shell sa: ./manage.py shell
# pa onda u shellu: exec(open('studserviceapp/database.py').read())
#
# https://stackoverflow.com/questions/16853649/how-to-execute-a-python-script-from-the-django-shell

def sacuvaj_semestar(semestar=None, **kwargs):
    if semestar is not None and not semestar_postoji(semestar):
        semestar.save()

    elif semestar is None and len(kwargs) >= 3:
        novi_semestar = Semestar()
        novi_semestar.vrsta = kwargs.pop("vrsta")
        novi_semestar.skolska_godina_pocetak = kwargs.pop("skolska_godina_pocetak")
        novi_semestar.skolska_godina_kraj = kwargs.pop("skolska_godina_kraj")

        if not semestar_postoji(novi_semestar):
            novi_semestar.save()


def semestar_postoji(semestar):
    return Semestar.objects.all().filter(vrsta=semestar.vrsta,
                                         skolska_godina_pocetak=semestar.skolska_godina_pocetak,
                                         skolska_godina_kraj=semestar.skolska_godina_kraj).exists()


def sacuvaj_grupu(grupa=None, **kwargs):
    if grupa is not None and not grupa_postoji(grupa):
        grupa.save()

    elif grupa is None and len(kwargs) >= 2:
        nova_grupa = Grupa()
        nova_grupa.oznaka_grupe = kwargs.pop("oznaka_grupe")

        if "smer" in kwargs:
            nova_grupa.smer = kwargs.pop("smer")

        nova_grupa.semestar = kwargs.pop("semestar")

        if not grupa_postoji(nova_grupa):
            nova_grupa.save()


def grupa_postoji(grupa):
    return Grupa.objects.all().filter(oznaka_grupe=grupa.oznaka_grupe).exists()


def sacuvaj_nalog(nalog=None, **kwargs):
    if nalog is not None and not nalog_postoji(nalog):
        nalog.save()

    # lozinka moze da bude None
    elif nalog is None and len(kwargs) >= 2:
        novi_nalog = Nalog()
        novi_nalog.username = kwargs.pop("username")

        if "lozinka" in kwargs:
            novi_nalog.lozinka = kwargs.pop("lozinka")

        novi_nalog.uloga = kwargs.pop("uloga")

        if not nalog_postoji(novi_nalog):
            novi_nalog.save()


def nalog_postoji(nalog):
    return Nalog.objects.all().filter(username=nalog.username).exists()


def sacuvaj_studenta(student=None, **kwargs):
    if student is not None and not student_postoji(student):
        student.save()

        if "grupa" in kwargs:
            student.grupa.add(kwargs.pop("grupa"))

    # nalog moze da bude None
    elif student is None and len(kwargs) >= 6:
        novi_student = Student()
        novi_student.ime = kwargs.pop("ime")
        novi_student.prezime = kwargs.pop("prezime")
        novi_student.broj_indeksa = kwargs.pop("broj_indeksa")
        novi_student.godina_upisa = kwargs.pop("godina_upisa")
        novi_student.smer = kwargs.pop("smer")

        if "nalog" in kwargs:
            novi_student.nalog = kwargs.pop("nalog")
        else:
            novi_student.nalog = napravi_studentu_nalog(novi_student)

        if not student_postoji(novi_student):
            novi_student.save()
            novi_student.grupa.add(kwargs.pop("grupa"))


def student_postoji(student):
    return Student.objects.all().filter(broj_indeksa=student.broj_indeksa, godina_upisa=student.godina_upisa,
                                        smer=student.smer).exists()


def napravi_studentu_nalog(student):
    nalog = Nalog()
    username = student.ime[0] + student.prezime + str(student.godina_upisa)[2:4]
    nalog.username = username.lower()
    nalog.uloga = "student"

    sacuvaj_nalog(nalog)

    return Nalog.objects.get(username=nalog.username)


def sacuvaj_predmet(predmet=None, **kwargs):
    if predmet is not None and not predmet_postoji(predmet):
        predmet.save()

    elif predmet is None and len(kwargs) >= 1:
        novi_predmet = Predmet()
        novi_predmet.naziv = kwargs.pop("naziv")

        if "espb" in kwargs:
            novi_predmet.espb = kwargs.pop("espb")

        if "semestar_po_programu" in kwargs:
            novi_predmet.semestar_po_programu = kwargs.pop("semestar_po_programu")

        if "fond_predavanja" in kwargs:
            novi_predmet.fond_predavanja = kwargs.pop("fond_predavanja")

        if "fond_vezbe" in kwargs:
            novi_predmet.fond_vezbe = kwargs.pop("fond_vezbe")

        if not predmet_postoji(novi_predmet):
            novi_predmet.save()


def predmet_postoji(predmet):
    return Predmet.objects.all().filter(naziv=predmet.naziv).exists()


def sacuvaj_nastavnika(nastavnik=None, **kwargs):
    if nastavnik is not None and nastavnik_postoji(nastavnik):
        if "predmet" in kwargs:
            # uzimamo instancu nastavnika iz baze
            Nastavnik.objects.get(ime=nastavnik.ime, prezime=nastavnik.prezime).predmet.add(kwargs.pop("predmet"))

    if nastavnik is not None and not nastavnik_postoji(nastavnik):
        nastavnik.save()

        if "predmet" in kwargs:
            nastavnik.predmet.add(kwargs.pop("predmet"))

    elif nastavnik is None and len(kwargs) >= 2:
        novi_nastavnik = Nastavnik()
        novi_nastavnik.ime = kwargs.pop("ime")
        novi_nastavnik.prezime = kwargs.pop("prezime")

        if "titula" in kwargs:
            novi_nastavnik.titula = kwargs.pop("titula")

        if "zvanje" in kwargs:
            novi_nastavnik.zvanje = kwargs.pop("zvanje")

        if "nalog" in kwargs:
            novi_nastavnik.nalog = kwargs.pop("nalog")
        else:
            novi_nastavnik.nalog = napravi_nastavniku_nalog(novi_nastavnik)

        if not nastavnik_postoji(novi_nastavnik):
            novi_nastavnik.save()

            if "predmet" in kwargs:
                novi_nastavnik.predmet.add(kwargs.pop("predmet"))

        elif "predmet" in kwargs:
            Nastavnik.objects.get(ime=novi_nastavnik.ime,
                                  prezime=novi_nastavnik.prezime).predmet.add(kwargs.pop("predmet"))


def nastavnik_postoji(nastavnik):
    return Nastavnik.objects.all().filter(ime=nastavnik.ime, prezime=nastavnik.prezime).exists()


def sacuvaj_administratora(ime, prezime):
    administrator = Administrator()
    administrator.ime = ime
    administrator.prezime = prezime
    administrator.nalog = napravi_administatoru_nalog(administrator)

    if administrator_postoji(administrator):
        return

    administrator.save()


def administrator_postoji(admin):
    return Administrator.objects.filter(ime=admin.ime, prezime=admin.prezime, nalog=admin.nalog)


def napravi_administatoru_nalog(administrator):
    username = administrator.ime[0] + administrator.prezime

    sacuvaj_nalog(username=username.lower(), uloga="administrator")

    return Nalog.objects.get(username=username)


def napravi_nastavniku_nalog(nastavnik):
    username = nastavnik.ime[0] + nastavnik.prezime

    sacuvaj_nalog(username=username.lower(), uloga="nastavnik")

    return Nalog.objects.get(username=username)


def sacuvaj_sekretara(ime, prezime):
    sekretar = Sekretar()
    sekretar.ime = ime
    sekretar.prezime = prezime
    sekretar.nalog = napravi_sekretaru_nalog(sekretar)

    if sekretar_postoji(sekretar):
        return

    sekretar.save()


def sekretar_postoji(sekretar):
    return Sekretar.objects.filter(nalog=sekretar.nalog)


def napravi_sekretaru_nalog(sekretar):
    username = sekretar.ime[0] + sekretar.prezime

    sacuvaj_nalog(username=username.lower(), uloga='sekretar')

    return Nalog.objects.get(username=username)


def sacuvaj_raspored_nastave(raspored_nastave=None, **kwargs):
    if raspored_nastave is not None and not raspored_nastave_postoji(raspored_nastave):
        raspored_nastave.save()

    elif raspored_nastave is None and len(kwargs) >= 2:
        novi_raspored_nastave = RasporedNastave()
        novi_raspored_nastave.datum_unosa = kwargs.pop("datum_unosa")
        novi_raspored_nastave.semestar = kwargs.pop("semestar")

        if not raspored_nastave_postoji(novi_raspored_nastave):
            novi_raspored_nastave.save()


def raspored_nastave_postoji(raspored_nastave):
    return RasporedNastave.objects.all().filter(datum_unosa=raspored_nastave.datum_unosa,
                                                semestar=raspored_nastave.semestar).exists()


def sacuvaj_termin(termin=None, **kwargs):
    if termin is not None and not sacuvaj_termin(termin):
        termin.save()

        if "grupe" in kwargs:
            dodaj_grupe(termin, kwargs.get("grupe"))

    elif termin is None and len(kwargs) >= 7:
        novi_termin = Termin()
        novi_termin.oznaka_ucionice = kwargs.pop("oznaka_ucionice")
        novi_termin.pocetak = kwargs.pop("pocetak")
        novi_termin.zavrsetak = kwargs.pop("zavrsetak")
        novi_termin.dan = kwargs.pop("dan")
        novi_termin.tip_nastave = kwargs.pop("tip_nastave")
        novi_termin.nastavnik = kwargs.pop("nastavnik")
        novi_termin.predmet = kwargs.pop("predmet")
        novi_termin.raspored = kwargs.pop("raspored")

        if not termin_postoji(novi_termin):
            novi_termin.save()

            if "grupe" in kwargs:
                dodaj_grupe(novi_termin, kwargs.get("grupe"))


def termin_postoji(termin):
    return Termin.objects.all().filter(oznaka_ucionice=termin.oznaka_ucionice, pocetak=termin.pocetak,
                                       zavrsetak=termin.zavrsetak, dan=termin.dan,
                                       tip_nastave=termin.tip_nastave, nastavnik=termin.nastavnik).exists()


def dodaj_grupe(termin, grupe):
    for grupa in grupe:
        termin.grupe.add(grupa)


def dodaj_izbor_grupe(izbor_grupe=None, **kwargs):
    if izbor_grupe is not None:
        izbor_grupe.save()

    elif izbor_grupe is None and len(kwargs) >= 9:
        izbor_grupe = IzborGrupe()
        izbor_grupe.ostvarenoESPB = kwargs.pop("ostvarenoESPB")
        izbor_grupe.upisujeESPB = kwargs.pop("upisujeESPB")
        izbor_grupe.broj_polozenih_ispita = kwargs.pop("boj_polozenih_ispita")
        izbor_grupe.upisuje_semestar = kwargs.pop("upisuje_semestar")
        izbor_grupe.prvi_put_upisuje_semestar = kwargs.pop("prvi_put_upisuje_semestar")
        izbor_grupe.nacin_placanja = kwargs.pop("nacin_placanja")
        izbor_grupe.nepolozeni_predmeti = kwargs.pop("nepolozeni_predmeti")
        izbor_grupe.student = kwargs.pop("student")
        izbor_grupe.izabrana_grupa = kwargs.pop("izabrana_grupa")
        izbor_grupe.upisan = kwargs.pop("upisan")

        izbor_grupe.save()


def sacuvaj_termin_polaganja(termin_polaganja=None, **kwargs):
    if termin_polaganja is not None and not termin_polaganja_postoji(termin_polaganja):
        termin_polaganja.save()

    elif termin_polaganja is None and len(kwargs) >= 7:
        novi_termin_polaganja = TerminPolaganja()
        novi_termin_polaganja.ucionice = kwargs.pop("ucionice")
        novi_termin_polaganja.pocetak = kwargs.pop("pocetak")
        novi_termin_polaganja.zavrsetak = kwargs.pop("zavrsetak")
        novi_termin_polaganja.datum = kwargs.pop("datum")
        novi_termin_polaganja.dan = kwargs.pop("dan")
        novi_termin_polaganja.raspored_polaganja = kwargs.pop("raspored_polaganja")
        novi_termin_polaganja.predmet = kwargs.pop("predmet")
        novi_termin_polaganja.nastavnik = kwargs.pop("nastavnik")

        if not termin_polaganja_postoji(novi_termin_polaganja):
            novi_termin_polaganja.save()


def termin_polaganja_postoji(termin_polaganja):
    return TerminPolaganja.objects.all().filter(ucionice=termin_polaganja.ucionice, pocetak=termin_polaganja.pocetak,
                                                zavrsetak=termin_polaganja.zavrsetak, dan=termin_polaganja.dan).exists()


def sacuvaj_raspored_polaganja(raspored_polaganja=None, **kwargs):
    if raspored_polaganja is not None and not raspored_polaganja_postoji(raspored_polaganja):
        raspored_polaganja.save()

    elif raspored_polaganja is None and len(kwargs) >= 1:
        novi_raspored_polaganja = RasporedPolaganja()
        novi_raspored_polaganja.ispitni_rok = kwargs.pop("ispitni_rok")
        novi_raspored_polaganja.kolokvijumska_nedelja = kwargs.pop("kolokvijumska_nedelja")

        if not raspored_polaganja_postoji(novi_raspored_polaganja):
            novi_raspored_polaganja.save()


def raspored_polaganja_postoji(raspored_polaganja):
    return RasporedPolaganja.objects.all().filter(ispitni_rok=raspored_polaganja.ispitni_rok,
                                                  kolokvijumska_nedelja=raspored_polaganja.kolokvijumska_nedelja)\
                                                                                          .exists()


def sacuvaj_obavestenje(obavestenje=None, **kwargs):
    if obavestenje and not obavestenje_postoji(obavestenje):
        obavestenje.save()

    elif obavestenje is None:
        novo_obavestenje = Obavestenje()
        novo_obavestenje.postavio = kwargs.pop('postavio')
        novo_obavestenje.datum_postavljanja = kwargs.pop('datum_postavljanja')
        novo_obavestenje.tekst = kwargs.pop('tekst')

        if 'fajl' in kwargs:
            novo_obavestenje.fajl = kwargs.pop('fajl')

        if not obavestenje_postoji(novo_obavestenje):
            novo_obavestenje.save()


def obavestenje_postoji(obavestenje):
    return Obavestenje.objects.filter(postavio=obavestenje.postavio, datum_postavljanja=obavestenje.datum_postavljanja)


def sacuvaj_izbornu_grupu(izborna_grupa=None, **kwargs):
    if izborna_grupa and not izborna_grupa_postoji(izborna_grupa):
        izborna_grupa.save()

    elif izborna_grupa is None:
        nova_izborna_grupa = IzbornaGrupa()
        nova_izborna_grupa.oznaka_grupe = kwargs.pop('oznaka_grupe')
        nova_izborna_grupa.oznaka_semestra = kwargs.pop('oznaka_semestra')
        nova_izborna_grupa.kapacitet = kwargs.pop('kapacitet')
        nova_izborna_grupa.smer = kwargs.pop('smer')
        nova_izborna_grupa.aktivna = kwargs.pop('aktivna')
        nova_izborna_grupa.za_semestar = kwargs.pop('za_semestar')

        if not izborna_grupa_postoji(nova_izborna_grupa):
            nova_izborna_grupa.save()

            imena_predmeta = kwargs.pop('predmeti')

            for ime in imena_predmeta:
                predmet = Predmet.objects.get(naziv=ime)
                nova_izborna_grupa.predmeti.add(predmet)

        elif 'predmeti' in kwargs:
            ig = IzbornaGrupa.objects.get(oznaka_grupe=nova_izborna_grupa.oznaka_grupe,
                                          oznaka_semestra=nova_izborna_grupa.oznaka_semestra,
                                          smer=nova_izborna_grupa.smer)

            imena_predmeta = kwargs.pop('predmeti')

            for ime in imena_predmeta:
                predmet = Predmet.objects.get(naziv=ime)
                ig.predmeti.add(predmet)


def izborna_grupa_postoji(izborna_grupa):
    return IzbornaGrupa.objects.filter(oznaka_grupe=izborna_grupa.oznaka_grupe,
                                       oznaka_semestra=izborna_grupa.oznaka_semestra,
                                       smer=izborna_grupa.smer).exists()
