from django.urls import path
from django.conf.urls import url
from django.views.static import serve
from django.conf.urls.static import static

from . import views

from studservice import settings

urlpatterns = [
    path('', views.index, name='index'),

    path('login', views.login, name='login'),

    path('zadatak/<str:dan>', views.zadatak, name='zadatak'),

    path('raspored/<str:username>', views.raspored, name='raspored'),

    path('spisakstudenata/<str:username>', views.spisak_studenata, name='spisakstudenata'),

    path('ceoraspored/<str:username>', views.ceo_raspored, name='ceoraspored'),

    path('izabranegrupe/<str:username>', views.izabrane_grupe, name='izabranegrupe'),

    path('izabranegrupe', views.izabrane_grupe, name='izabranegrupe'),

    path('formular/<str:username>', views.formular_za_izbor, name='formular'),

    path('podacioupisu/<str:username>', views.podaci_o_upisu, name='podacioupisu'),

    path('podacioupisuform/<str:username>', views.podacioupisuform, name='podacioupisuform'),  # /<str:nalog>

    path('programgrupa/<str:username>', views.program_grupa, name='program grupe'),

    path('korisnici/<str:oznaka_grupe>/<str:username>', views.studenti_iz_grupe, name='korisnici'),

    path('mail/<str:username>', views.mail_sistem, name='mail sistem'),

    path('mailform', views.mail_form, name='mail-attachments form'),

    path('import/<str:raspored_polaganja>', views.import_csv, name='import'),

    path('student/<str:username>', views.studentpodaci_template, name='studentpodaci'),

    path('slika/<str:username>', views.slika_form, name='prikazslike'),

    path('pregledgrupaprofesora/<str:username>', views.pregled_grupa_profesora, name='pregledgrupaprofesora'),

    path('forma_za_ispravku', views.forma_za_ispravku_template, name='forma_za_ispravku'),

    path('unosobavestenja/<str:username>', views.unos_obavestenja, name='unosobavestenja'),

    path('unosobavestenjaform', views.unos_obavestenja_form, name='unosobavestenjaform'),

    path('uploadkolokvijumform', views.upload_Kolokvijum, name='uploadkolokvijumform'),

    path('uploadispitform', views.upload_Ispit, name='uploadispitform'),

    path('uploadrasporedform', views.upload_Raspored, name='uploadrasporedform'),

    path('uploadrasporeda/<str:username>', views.upload_Rasporeda, name='uploadrasporeda'),

    path('uploadispita/<str:username>', views.upload_Ispita, name='uploadispita'),

    path('uploadkolokvijuma/<str:username>', views.upload_Kolokvijuma, name='uploadkolokvijuma'),

    path('svaobavestenja/<str:username>', views.sva_obavestenja, name='svaobavestenja'),

    path('unosizbornegrupe/<str:username>', views.unos_izborne_grupe, name='unosizbornegrupe'),

    path('unosizbornegrupeform', views.unos_izborne_grupe_form, name='unosizbornegrupeform'),

    path('pregledizbornihgrupa/<str:username>', views.pregled_izbornih_grupa, name='pregledizbornihgrupa')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, })]

