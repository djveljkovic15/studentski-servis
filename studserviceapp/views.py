from datetime import datetime

import pytz
from django.shortcuts import *

from studserviceapp import database
from studserviceapp.forms import *
from studserviceapp.mail import *
from studserviceapp.models import *
from studserviceapp.parseTerminPolaganja import CSVParser
from studserviceapp.parseRaspored import fajlZaParse


def index(request):
    return render(request, 'html/index.html')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')

            if Nalog.objects.filter(username=username).exists():
                return redirect('raspored/' + username)
            else:
                return HttpResponse('Nalog nije pronadjen')

    return HttpResponse('Greska pri popunjavanju forme')


def raspored(request, username):
    if username == 'svi':
        termini = Termin.objects.all()
        context = {'termini': termini}

        return render(request, 'html/korisnici/raspored.html', context)

    if Nalog.objects.filter(username=username).exists():
        nalog = Nalog.objects.get(username=username)

        if Nastavnik.objects.filter(nalog=nalog).exists():
            nastavnik = Nastavnik.objects.get(nalog=nalog)
            termini = Termin.objects.filter(nastavnik=nastavnik)

            context = {'termini': termini, 'nastavnik': nastavnik, 'obavestenja': vrati_obavestenja()}

            return render(request, 'html/korisnici/raspored.html', context)

        elif Student.objects.filter(nalog=nalog).exists():
            student = Student.objects.get(nalog=nalog)
            grupa = Grupa.objects.get(student=student)
            termini = Termin.objects.filter(grupe__oznaka_grupe=grupa.oznaka_grupe)

            context = {'termini': termini, 'student': student, 'obavestenja': vrati_obavestenja()}

            return render(request, 'html/korisnici/raspored.html', context)

        elif Administrator.objects.filter(nalog=nalog).exists():
            administrator = Administrator.objects.get(nalog=nalog)
            termini = Termin.objects.all()

            context = {'termini': termini, 'administrator': administrator, 'obavestenja': vrati_obavestenja()}

            return render(request, 'html/korisnici/raspored.html', context)

        elif Sekretar.objects.filter(nalog=nalog).exists():
            sekretar = Sekretar.objects.get(nalog=nalog)
            termini = Termin.objects.all()

            context = {'termini': termini, 'sekretar': sekretar, 'obavestenja': vrati_obavestenja()}

            return render(request, 'html/korisnici/raspored.html', context)

    return HttpResponse('Nalog nije pronadjen')


def vrati_obavestenja():
    return Obavestenje.objects.all().order_by('-id')[:5]


def ceo_raspored(request, username):
    if Nalog.objects.filter(username=username).exists():
        nalog = Nalog.objects.get(username=username)
        termini = Termin.objects.all()

        if Student.objects.filter(nalog=nalog):
            student = Student.objects.get(nalog=nalog)
            context = {'termini': termini, 'student': student}

        elif Nastavnik.objects.filter(nalog=nalog).exists():
            nastavnik = Nastavnik.objects.get(nalog=nalog)
            context = {'termini': termini, 'nastavnik': nastavnik}

        else:
            return HttpResponse('Nalog nije pronadjen')

        return render(request, 'html/korisnici/raspored.html', context)

    return HttpResponse('Nalog nije pronadjen')


def izabrane_grupe(request, username):
    izabrana_grupa = IzborGrupe.objects.all()
    administratori = Administrator.objects.get(nalog__username=username)
    context = {'izabranaGrupa': izabrana_grupa, 'administrator': administratori}
    return render(request, 'html/grupe/izabrane-grupe.html', context)


def formular_za_izbor(request, username):
    student = Student.objects.filter(nalog__username=username).get()
    izabranagrupa = IzborGrupe.objects.filter(student=student)
    if IzborGrupe.objects.filter(student=student).exists():
        return HttpResponse("Student je vec izabrao grupu")

    predmet = Predmet.objects.all()
    last = Semestar.objects.all().order_by('-id')[:1]  # uzima poslednji id iz tabele semestar
    # print(student.__dict__)
    context = {'student': student, 'izabranaGrupa': izabranagrupa, 'predmet': predmet, 'semestar1': last}

    return render(request, 'html/grupe/formular-za-izbor.html', context)


def program_grupa(request, username):  # ubaciti kapacitet grupe
    # context = None
    if Nalog.objects.filter(username=username).exists():
        nalog = Student.objects.get(nalog__username=username)
        if IzbornaGrupa.objects.filter(aktivna=1).exists():
            izbornagrupa = IzbornaGrupa.objects.filter(aktivna=1)
            if IzbornaGrupa.objects.filter(smer=nalog.smer):
                izbornagrupa = izbornagrupa.filter(smer=nalog.smer)
                qs = izbornagrupa
                context = {'izbornegrupe': qs}
                return render(request, 'html/grupe/program-grupa.html', context)
        else:
            return HttpResponse("Ne postoji odgovarajuca grupa")


def studenti_iz_grupe(request, oznaka_grupe, username):
    context = {}

    if Nastavnik.objects.filter(nalog__username=username).exists():
        nastavnik = Nastavnik.objects.get(nalog__username=username)

        context['nastavnik'] = nastavnik

    elif Sekretar.objects.filter(nalog__username=username).exists():
        sekretar = Sekretar.objects.get(nalog__username=username)

        context['sekretar'] = sekretar

    elif Administrator.objects.filter(nalog__username=username).exists():
        administrator = Administrator.objects.get(nalog__username=username)

        context['administrator'] = administrator

    else:
        return HttpResponse(username + ' nema pristup ovom servisu')

    if IzbornaGrupa.objects.filter(oznaka_grupe=oznaka_grupe).exists():
        izborna_grupa = IzbornaGrupa.objects.filter(oznaka_grupe=oznaka_grupe).get()

        if Student.objects.filter(grupa__oznaka_grupe=oznaka_grupe).exists():
            studenti = Student.objects.filter(grupa__oznaka_grupe=oznaka_grupe)

            context['studenti'] = studenti
            context['igrupa'] = izborna_grupa

        return render(request, 'html/korisnici/studenti-iz-grupe.html', context)
    else:
        return HttpResponse("Grupa nije pronadjena!")


def studentpodaci_template(request, username):
    if Student.objects.filter(nalog__username=username).exists():
        student = Student.objects.filter(nalog__username=username).get()
        grupa = Grupa.objects.filter(student=student).get()
        context = {'student': student, 'grupa': grupa, 'slika': student.slika.name}
        return render(request, 'html/korisnici/studentpodaci.html', context)
    else:
        return HttpResponse("Student nije pronadjen!")


def slika_form(request, username):
    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            if 'slika' in request.FILES:
                # username = request.GET
                student = Student.objects.filter(nalog__username=username).get()
                student.slika = request.FILES['slika']
                student.save()
                # print(student.slika)
                return HttpResponse("Uspesno uploadovana slika!")

    return HttpResponse("Nije pronadjena slika!")


def pregled_grupa_profesora(request, username):
    validne_uloge = ['nastavnik', 'sekretar', 'administrator']
    nalog = Nalog.objects.get(username=username)

    if nalog.uloga not in validne_uloge:
        return HttpResponse("Korisnik " + username + " nema pristup ovom servisu!")

    if Nastavnik.objects.filter(nalog__username=username).exists():
        nastavnik = Nastavnik.objects.get(nalog__username=username)
        predmeti = Predmet.objects.filter(nastavnik__nalog__username=username)

        grupe = IzbornaGrupa.objects.filter(predmeti__in=predmeti)
        # print(nastavnik)
        # print(predmeti)
        # print(grupe)
        context = {'predmeti': predmeti, 'nastavnik': nastavnik, 'grupe': grupe}
        return render(request, 'html/korisnici/pregled-grupa-profesora.html', context)
    else:
        return HttpResponse("Korisnik" + username + " nije pronadjen!")


RAF_MAIL = '@raf.rs'


def mail_sistem(request, username):
    if not Nalog.objects.filter(username=username).exists():
        return HttpResponse("Korisnik " + username + " nije pronadjen")

    validne_uloge = ['nastavnik', 'sekretar', 'administrator']

    nalog = Nalog.objects.get(username=username)

    if nalog.uloga not in validne_uloge:
        return HttpResponse("Korisnik " + username + " nema pristup ovom servisu")

    mail = nalog.username + RAF_MAIL

    context = {'nalog': nalog, 'mail': mail, 'ime_administratora': get_ime_administratora(nalog),
               'combobox_nastavnika': napravi_combobox_nastavnika(nalog),
               'combobox_administratora': napravi_combobox_administratora(nalog)}

    if Nastavnik.objects.filter(nalog=nalog).exists():
        nastavnik = Nastavnik.objects.get(nalog=nalog)
        context['nastavnik'] = nastavnik

    elif Sekretar.objects.filter(nalog=nalog).exists():
        sekretar = Sekretar.objects.get(nalog=nalog)
        context['sekretar'] = sekretar

    elif Administrator.objects.filter(nalog=nalog).exists():
        adminisrator = Administrator.objects.get(nalog=nalog)
        context['administrator'] = adminisrator

    return render(request, 'html/mail/mail-sistem.html', context)


# Forme ne upisuju i ne citaju nista posle razmaka, iz nekog razloga.
# Svi razmaci su zamenjeni sa '_' kod kreiranja comboboxa
def napravi_combobox_nastavnika(nalog):
    if nalog.uloga != 'nastavnik':
        return []

    data = []

    nastavnik = Nastavnik.objects.get(nalog=nalog)
    predmeti = Predmet.objects.filter(nastavnik=nastavnik)

    for predmet in predmeti:
        naziv = predmet.naziv.replace(' ', '_')
        data.append(naziv)

    grupe = IzbornaGrupa.objects.filter(predmeti__in=predmeti)

    for grupa in grupe:
        oznaka_grupe = grupa.oznaka_grupe.replace(' ', '_')

        if oznaka_grupe in data:
            continue

        data.append(oznaka_grupe)

    return data


def napravi_combobox_administratora(nalog):
    if nalog.uloga != 'administrator' and nalog.uloga != 'sekretar':
        return []

    data = ['svi', 'Racunarske_nauke', 'Racunarsko_inzinjerstvo', 'Racunarski_dizajn', 'Informacione_tehnologije']

    for predmet in Predmet.objects.all():
        naziv = predmet.naziv.replace(' ', '_')
        data.append(naziv)

    for grupa in Grupa.objects.all():
        oznaka_grupe = grupa.oznaka_grupe.replace(' ', '_')
        data.append(oznaka_grupe)

    return data


def get_ime_administratora(nalog):
    if nalog.uloga == 'sekretar':
        sekretar = Sekretar.objects.get(nalog=nalog)

        return sekretar.ime + '_' + sekretar.prezime

    elif nalog.uloga == 'administrator':
        administrator = Administrator.objects.get(nalog=nalog)

        # Razmak iz nekog razloga ne moze da se pirkaze u text fildu,
        # input zanemari sve posle razmaka
        return administrator.ime + '_' + administrator.prezime

    elif nalog.uloga == 'nastavnik':
        nastavnik = Nastavnik.objects.get(nalog=nalog)

        return nastavnik.ime + '_' + nastavnik.prezime

    else:
        raise ValueError(nalog + ' nije ispravan, dodat je novi model za administratore')


def mail_form(request):
    if request.method == 'POST':
        # Za formu su potrebni izbori comboboxa nastavnika i administratora,
        # koje mozemo dobiti funkcijama napravi_combobox_nastavnika(nalog) i
        # napravi_combobox_administratora(nalog). Uzimamo mail koji je korisnik prosledio,
        # iz njega dobijamo nalog koji je potreban kao argument.
        mail = request.POST['posiljaoc_mail']
        nalog = Nalog.objects.all().get(username=skini_podstring(mail, RAF_MAIL))

        form = MailForm(napravi_combobox_nastavnika(nalog), napravi_combobox_administratora(nalog),
                        request.POST, request.FILES)

        if form.is_valid():
            if 'attachment' in request.FILES:
                premesti_uplodovan_file(settings.MEDIA_ROOT, request.FILES['attachment'])

            send_mail(form)

            return HttpResponse('Mail je poslat')

    return HttpResponse('Greska pri popunjavanju forme')


# Skida podstring s kraja stringa
def skini_podstring(string, podstring):
    if string.endswith(podstring):
        return string[:-len(podstring)]

    raise ValueError(podstring + ' nije podstring od ' + string)


def premesti_uplodovan_file(odrediste, f):
    putanja = os.path.join(odrediste, f.name)

    with open(putanja, 'wb+') as o:
        for chunk in f.chunks():
            o.write(chunk)


def import_csv(request, raspored_polaganja):
    # if request.method == 'POST' and request.FILES['csv_file']:
    #     myfile = request.FILES['csv_file']
    #     fs = FileSystemStorage()
    #     filename = fs.save(myfile.name, myfile)
    csv_parser = CSVParser(raspored_polaganja, "resources/kol1.csv")
    csv_parser.parse_file()

    context = dict()
    context["errors"] = csv_parser.parsing_error.error_messages

    return render(request, 'html/parsiranje/csvparse.html', context)


def forma_za_ispravku_template(request):
    return render(request, 'html/parsiranje/ispravkapodataka.html')


def unos_obavestenja(request, username):
    context = {}

    if Sekretar.objects.filter(nalog__username=username).exists():
        sekretar = Sekretar.objects.get(nalog__username=username)

        context['sekretar'] = sekretar

    elif Administrator.objects.filter(nalog__username=username).exists():
        admin = Administrator.objects.get(nalog__username=username)

        context['administrator'] = admin

    else:
        return HttpResponse(username + ' nema pristup ovom servisu')

    return render(request, 'html/obavestenja/unos-obavestenja.html', context)


def upload_Rasporeda(request, username):
    context = {}

    if Administrator.objects.filter(nalog__username=username).exists():
        admin = Administrator.objects.get(nalog__username=username)

        context['administrator'] = admin

    else:
        return HttpResponse(username + ' nema pristup ovom servisu')

    return render(request, 'html/upload/upload-raspored.html', context)


def upload_Kolokvijuma(request, username):
    context = {}

    if Administrator.objects.filter(nalog__username=username).exists():
        admin = Administrator.objects.get(nalog__username=username)

        context['administrator'] = admin

    else:
        return HttpResponse(username + ' nema pristup ovom servisu')

    return render(request, 'html/upload/upload-kolokvijum.html', context)


def upload_Ispita(request, username):
    context = {}

    if Administrator.objects.filter(nalog__username=username).exists():
        admin = Administrator.objects.get(nalog__username=username)

        context['administrator'] = admin

    else:
        return HttpResponse(username + ' nema pristup ovom servisu')

    return render(request, 'html/upload/upload-ispit.html', context)


def upload_Raspored(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['attachment']
            premesti_uplodovan_file(settings.RESOURCE_ROOT, f)
            fajlZaParse(f.name)
            return HttpResponse('Uspesno uploadovan raspored')
        else:
            return HttpResponse('Greska pri popunjavanju forme')
    return HttpResponse('Greska pri slanju podataka')


def upload_Kolokvijum(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['attachment']
            premesti_uplodovan_file(settings.RESOURCE_ROOT, f)
            csv_parser = CSVParser('1', 'resources/' + f.name)
            csv_parser.parse_file()
            for k, v in csv_parser.parsing_error.error_messages.items():
                print(v)
            return HttpResponse('Uspesno uploadovan raspored')
        else:
            return HttpResponse('Greska pri popunjavanju forme')
    return HttpResponse('Greska pri slanju podataka')


def upload_Ispit(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            return HttpResponse('Uspesno uploadovan raspored')
        else:
            return HttpResponse('Greska pri popunjavanju forme')
    return HttpResponse('Greska pri slanju podataka')


def unos_obavestenja_form(request):
    if request.method == 'POST':
        form = ObavestenjeForm(request.POST, request.FILES)

        if form.is_valid():
            postavio = Nalog.objects.get(username=form.cleaned_data.pop('postavio'))
            obavestenje = Obavestenje(postavio=postavio, tekst=form.cleaned_data.pop('tekst'),
                                      datum_postavljanja=datetime.now(pytz.UTC))

            if 'file' in request.FILES:
                obavestenje.fajl = request.FILES['file']

            database.sacuvaj_obavestenje(obavestenje)

            return HttpResponse('Uspesno uneto obavestenje')

        else:
            return HttpResponse('Greska pri popunjavanju forme')

    return HttpResponse('Greska pri slanju podataka')


def sva_obavestenja(request, username):
    context = {'meni': True, 'obavestenja': Obavestenje.objects.all().order_by('-id')}

    if Sekretar.objects.filter(nalog__username=username):
        sekretar = Sekretar.objects.get(nalog__username=username)

        context['sekretar'] = sekretar

    elif Administrator.objects.filter(nalog__username=username):
        admnistrator = Administrator.objects.get(nalog__username=username)

        context['administrator'] = admnistrator

    else:
        return HttpResponse(username + ' nema pristup ovom servisu')

    return render(request, 'html/obavestenja/obavestenja.html', context)


def unos_izborne_grupe(request, username):
    context = {'semestri': Semestar.objects.all(), 'predmeti': Predmet.objects.all()}

    if Sekretar.objects.filter(nalog__username=username).exists():
        sekretar = Sekretar.objects.get(nalog__username=username)

        context['sekretar'] = sekretar

    elif Administrator.objects.filter(nalog__username=username).exists():
        administrator = Administrator.objects.get(nalog__username=username)

        context['administrator'] = administrator

    else:
        return HttpResponse(username + ' nema pristup ovom servisu')

    return render(request, 'html/grupe/unos-izborne-grupe.html', context)


def unos_izborne_grupe_form(request):
    if request.method == 'POST':
        form = IzbornaGrupaForm(request.POST)

        if form.is_valid():
            oznake_grupa = form.cleaned_data.get('oznaka_grupe').split(' ')

            for oznaka_grupe in oznake_grupa:
                semestar_string = form.cleaned_data.get('semestar')
                semestar_vrsta = semestar_string.split(' ', 1)[0]
                semestar_godina = semestar_string.split(' ', 1)[1]
                pocetak = semestar_godina.split('/', 1)[0]
                kraj = semestar_godina.split('/', 1)[1]

                database.sacuvaj_izbornu_grupu(oznaka_grupe=oznaka_grupe,
                                               oznaka_semestra=form.cleaned_data.get('oznaka_semestra'),
                                               kapacitet=form.cleaned_data.get('kapacitet'),
                                               smer=form.cleaned_data.get('smer'),
                                               aktivna=form.cleaned_data.get('aktivna'),
                                               za_semestar=Semestar.objects.get(vrsta=semestar_vrsta,
                                                                                skolska_godina_kraj=kraj,
                                                                                skolska_godina_pocetak=pocetak),
                                               predmeti=form.cleaned_data.get('predmeti'))

            return HttpResponse('Uspesno uneta grupa')

        else:
            return HttpResponse('Greska pri popunjavanju forme')

    return HttpResponse('Greska pri slanju podataka')


def pregled_izbornih_grupa(request, username):
    context = {'izbornegrupe': IzbornaGrupa.objects.all()}

    if Sekretar.objects.filter(nalog__username=username).exists():
        sekretar = Sekretar.objects.get(nalog__username=username)

        context['sekretar'] = sekretar

    elif Administrator.objects.filter(nalog__username=username).exists():
        administrator = Administrator.objects.get(nalog__username=username)

        context['administrator'] = administrator

    else:
        return HttpResponse(username + ' nema pristup ovom servisu')

    return render(request, 'html/grupe/izborna-grupa.html', context)


def spisak_studenata(request, username):
    studenti = Student.objects.all()

    if Administrator.objects.filter(nalog__username=username).exists():
        administratori = Administrator.objects.get(nalog__username=username)
        context = {'studenti': studenti, 'administrator': administratori}

    elif Sekretar.objects.filter(nalog__username=username).exists():
        sekretar = Sekretar.objects.get(nalog__username=username)
        context = {'studenti': studenti, 'sekretar': sekretar}

    return render(request, 'html/korisnici/spisak-studenata.html', context)


def podaci_o_upisu(request, username):
    if Student.objects.filter(nalog__username=username).exists():
        student = Student.objects.get(nalog__username=username)
        izabrana_grupa = IzborGrupe.objects.filter(student__nalog__username=username)
        context = {'student': student, 'izabrana_grupa': izabrana_grupa}  # student
        # print(context)
        return render(request, 'html/korisnici/podaci-o-upisu.html', context)
    elif Administrator.objects.filter(nalog__username=username).exists():
        administratori = Administrator.objects.get(nalog__username=username)
        context = {'administrator': administratori}
        # print(context)
        return render(request, 'html/korisnici/podaci-o-upisu.html', context)
    elif Sekretar.objects.filter(nalog__username=username).exists():
        sekretar = Sekretar.objects.get(nalog__username=username)
        context = {'sekretar': sekretar}
        return render(request, 'html/korisnici/podaci-o-upisu.html', context)
    return HttpResponse("Greska pri otvaranju stranice.")


def podacioupisuform(request, username):
    if request.method == 'POST':
        form = ProveriStudentaForm(request.POST)
        if form.is_valid():
            nalog = form.cleaned_data.get('nalog')
            if Student.objects.filter(nalog__username=nalog).exists():
                admin = Administrator.objects.get(nalog__username=username)
                izabrana_grupa = IzborGrupe.objects.filter(student__nalog__username=nalog)
                context = {'administrator': admin, 'izabrana_grupa': izabrana_grupa}
                return render(request, 'html/korisnici/podaci-o-upisu-admin.html', context)
            else:
                return HttpResponse('Nalog nije pronadjen')
    return HttpResponse("ne radi")


def zadatak(request, dan):
    if Termin.objects.filter(dan=dan).exists():
        # termin = Termin.objects.filter(dan=dan)
        nastavnik = Nastavnik.objects.filter(termin__dan=dan)
        context = {'nastavnik': nastavnik}
        return render(request, 'html/zadatak.html', context)
    return HttpResponse("nesto si pogresio!")

