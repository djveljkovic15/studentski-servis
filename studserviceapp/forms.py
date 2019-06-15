from django import forms
from studserviceapp.models import *


class LoginForm(forms.Form):
    username = forms.CharField(label='username')


class UploadForm(forms.Form):
    attachment = forms.FileField(label='attachment')


class ProveriStudentaForm(forms.Form):
    nalog = forms.CharField(label='nalog')


class SlikaForm(forms.Form):
    slika = forms.ImageField(label="slika", required=False)


class ObavestenjeForm(forms.Form):
    postavio = forms.CharField(label='postavio')
    tekst = forms.CharField(label='tekst')
    file = forms.FileField(label='file', required=False)


class IzbornaGrupaForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        semestri = Semestar.objects.all()
        svi_predmeti = Predmet.objects.all()
        izbori_za_predmete = []

        for p in svi_predmeti:
            izbori_za_predmete.append(p.naziv)

        self.fields['semestar'] = forms.ChoiceField(label='semestar', choices=napravi_izbore(semestri))
        self.fields['predmeti'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label='predmeti',
                                                            choices=napravi_izbore(izbori_za_predmete))

    oznaka_grupe = forms.CharField(label='oznaka_grupe')
    oznaka_semestra = forms.IntegerField(label='oznaka_semestra')
    kapacitet = forms.IntegerField(label='kapacitet')
    smer = forms.CharField(label='smer')
    aktivna = forms.BooleanField(label='aktivna', required=False)


class MailForm(forms.Form):

    def __init__(self, combobox_nastavnika, combobox_administratora, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.combobox_nastavnika = combobox_nastavnika
        self.combobox_administratora = combobox_administratora

        # Atribut choices u ChoiceField formi mora da bude tuple, oblik [(A, B), (C, D)].
        #
        # Posto se combobox izbori definisu dinamicki polje primaoci ne moze da bude globalna
        # promenljiva nego mora da se deklarise u __init__ metodi. Ovo radimo da bi mogli da
        # primenimo neku potrebnu logiku za choices attribut.
        self.fields['primaoci_nastavnika'] = forms.ChoiceField(label='primaoci_nastavnika', required=False,
                                                               choices=napravi_izbore(self.combobox_nastavnika))

        self.fields['primaoci_administratora'] = forms.ChoiceField(label='primaoci_administratora', required=False,
                                                                   choices=napravi_izbore(self.combobox_administratora))

        # print(napravi_izbore(self.combobox_administratora))
        # print(napravi_izbore(self.combobox_nastavnika))

    posiljaoc = forms.CharField(label='posiljaoc', max_length=100,
                                error_messages={'required': 'Ime posiljaoca ne moze biti prazno',
                                                'invalid': 'Ime posiljaoca nije validno'})

    posiljaoc_mail = forms.EmailField(label='posiljaoc_mail', max_length=100,
                                      error_messages={'required': 'Mail posiljaoca ne moze biti prazan',
                                                      'invalid': 'Mail posiljaoca nije validan'})

    subject = forms.CharField(label='subject', max_length=100,
                              error_messages={'required': 'Subject ne moze biti prazan',
                                              'invalid': 'Subject nije validan'})

    message = forms.CharField(label='message', widget=forms.Textarea, required=False)

    attachment = forms.FileField(label='attachment', required=False)


def napravi_izbore(combobox_izbori):
    izbori = ()

    for combobox_izbor in combobox_izbori:
        tmp_tuple = ((combobox_izbor, combobox_izbor),)
        izbori = izbori + tmp_tuple

    return izbori
