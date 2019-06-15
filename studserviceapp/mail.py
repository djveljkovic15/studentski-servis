import base64
import mimetypes
import os
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httplib2
import oauth2client
from apiclient import errors, discovery
from oauth2client import client, tools, file

from studservice import settings
from studserviceapp.models import Predmet, IzbornaGrupa, Grupa, Student, Nastavnik


posiljaoc_za_testiranje = 'uvardic17@raf.rs'


def send_mail(form):
    primaoci_nastavnika = form.cleaned_data.get('primaoci_nastavnika')
    primaoci_administratora = form.cleaned_data.get('primaoci_administratora')
    posiljaoc = form.cleaned_data.get('posiljaoc')
    posiljaoc_mail = form.cleaned_data.get('posiljaoc_mail')
    subject = form.cleaned_data.get('subject')
    message = form.cleaned_data.get('message')
    attachment = form.cleaned_data.get('attachment')

    # print('Primaoci nastavnika = ' + str(primaoci_nastavnika))
    # print('Primaoci administratora = ' + str(primaoci_administratora))
    # print('Posiljaoc = ' + posiljaoc)
    # print('Posiljaoc mail = ' + posiljaoc_mail)
    # print('Subject = ' + subject)
    # print('Message = ' + message)
    # print('Attachment = ' + str(attachment))

    if attachment is None:
        if len(primaoci_nastavnika) > 0:
            for primaoc in nadji_primaoce_nastavnika(primaoci_nastavnika):
                mail_primaoca = primaoc.nalog.username + '@raf.rs'
                create_and_send_message(posiljaoc_za_testiranje, mail_primaoca, subject, message)

        elif len(primaoci_administratora) > 0:
            for primaoc in nadji_primaoce_administratora(primaoci_administratora):
                mail_primaoca = primaoc.nalog.username + '@raf.rs'
                create_and_send_message(posiljaoc_za_testiranje, mail_primaoca, subject, message)

    else:
        attached_file = os.path.join(settings.MEDIA_ROOT, attachment.name)

        if len(primaoci_nastavnika) > 0:
            for primaoc in nadji_primaoce_nastavnika(primaoci_nastavnika):
                mail_primaoca = primaoc.nalog.username + 'raf@.ras'
                create_and_send_message(posiljaoc_za_testiranje, mail_primaoca, subject, message, attached_file)

        elif len(primaoci_administratora) > 0:
            for primaoc in nadji_primaoce_administratora(primaoci_administratora):
                mail_primaoca = primaoc.nalog.username + 'raf@.ras'
                create_and_send_message(posiljaoc_za_testiranje, mail_primaoca, subject, message, attached_file)


def nadji_primaoce_nastavnika(primaoci_nastavnika):
    output = []
    naziv = primaoci_nastavnika.replace('_', ' ')

    if Predmet.objects.filter(naziv=naziv).exists():
        predmet = Predmet.objects.get(naziv=naziv)

        if IzbornaGrupa.objects.filter(predmeti__exact=predmet).exists():
            izborna_grupa = IzbornaGrupa.objects.get(predmeti__exact=predmet)
        else:
            raise ValueError('Predmet nema grupu')

        grupa = Grupa.objects.get(oznaka_grupe=izborna_grupa.oznaka_grupe)
        studenti = Student.objects.filter(grupa=grupa)

        for studnet in studenti:
            output.append(studnet)

    elif Grupa.objects.filter(oznaka_grupe=naziv).exists():
        grupa = Grupa.objects.get(oznaka_grupe=naziv)
        studenti = Student.objects.filter(grupa=grupa)

        for student in studenti:
            output.append(student)

    else:
        raise ValueError('Primaoci nastavnika nisu pronadjeni')

    return output


def nadji_primaoce_administratora(primaoci_administratora):
    output = []
    naziv = primaoci_administratora.replace('_', ' ')

    if naziv == 'svi':
        studenti = Student.objects.all()

        for student in studenti:
            output.append(student)

    elif naziv == 'Racunarske nauke' or naziv == 'Racunarsko inzinjerstvo' or naziv == 'Racunarski dizajn'\
            or naziv == 'Informacione tehnologije' or naziv == 'RN' or naziv == 'RI' or naziv == 'RM'\
            or naziv == 'RD' or naziv == 'IT':

        studenti = Student.objects.filter(smer=naziv)

        for student in studenti:
            output.append(student)

    elif Predmet.objects.filter(naziv=naziv).exists():
        predmet = Predmet.objects.get(naziv=naziv)

        if IzbornaGrupa.objects.filter(predmeti__exact=predmet).exists():
            izborna_grupa = IzbornaGrupa.objects.get(predmeti__exact=predmet)
        else:
            raise ValueError('Predmet nema grupu')

        grupa = Grupa.objects.get(oznaka_grupe=izborna_grupa.oznaka_grupe)
        studenti = Student.objects.filter(grupa=grupa)

        for studnet in studenti:
            output.append(studnet)

    elif Grupa.objects.filter(oznaka_grupe=naziv).exists():
        grupa = Grupa.objects.get(oznaka_grupe=naziv)
        studenti = Student.objects.filter(grupa=grupa)

        for student in studenti:
            output.append(student)

    else:
        raise ValueError('Primaoci nastavnika nisu pronadjeni')

    return output


def create_and_send_message(sender, to, subject, message_text, attached_file=None):
    # Objekat za hendlovanje http zahteva
    http = httplib2.Http()
    # Ovlastimo http objekat sa kredincijalima
    http = get_credentials().authorize(http)

    service = discovery.build('gmail', 'v1', http=http)

    # Bez attachmenta
    if attached_file is None:
        message = create_message(sender, to, subject, message_text)

        return send_message(service, 'me', message, message_text)

    # Sa attachmentom
    message_with_attachment = create_message_with_attachment(sender, to, subject, message_text, attached_file)

    return send_message_with_attachment(service, 'me', message_with_attachment, message_text)


def get_credentials():
    store = oauth2client.file.Storage(get_credentials_path())
    credentials = store.get()

    # Ako kredencijali ne postoje ili nisu validi napravimo nove
    # pomocu oauth2.client
    if not credentials or credentials.invalid:
        client_secret_file = 'studserviceapp/credentials/credentials.json'
        application_name = 'studservice'
        scopes = 'https://www.googleapis.com/auth/gmail.send'

        flow = client.flow_from_clientsecrets(client_secret_file, scopes)
        flow.user_agent = application_name

        credentials = tools.run_flow(flow, store)

    return credentials


# Nalazi putanju do kredencijala ako postoji,
# inace napravi odgovarajuce direktorijume:
# Windows -> C:\Users\Me\.credentials
# Linux -> \home\Me\.credentials
def get_credentials_path():
    home_dir = os.path.expanduser('~')
    credentials_dir = os.path.join(home_dir, '.credentials')

    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)

    return os.path.join(credentials_dir, 'cred send mail.json')


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode('UTF-8')).decode('ascii')}


def send_message(service, user_id, body, message_text):
    try:
        message_sent = (service.users().messages().send(userId=user_id, body=body).execute())
        message_id = message_sent['id']
        print(f'Poruka poslata (bez attachmenta) \n\n Id poruke: {message_id}\n\n Poruka:\n\n {message_text}')
    except errors.HttpError as error:
        print(f'Greska: {error}')


def create_message_with_attachment(sender, to, subject, message_text, attached_file):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    message.attach(MIMEText(message_text, 'plain'))

    # Pokusavamo da pogodimo tip attachmenta da bi znali
    # u koje stanje funkcija treba da udje kako bi procitala file
    my_mimetype, encoding = mimetypes.guess_type(attached_file)

    # Ako tip nije prepoznat vratice (None, None)
    # Ako je npr .mp3, vratice (audio/mp3, None) - None je za encoding
    # Za neprepoznatljive tipove, postavicemo ga na 'application/octet-stream',
    # tako nece vise vracati None
    if my_mimetype is None or encoding is not None:
        my_mimetype = 'application/octet-stream'

    main_type, sub_type = my_mimetype.split('/', 1)

    attachment = read_attached_file(main_type, sub_type, attached_file)

    encoders.encode_base64(attachment)
    file_name = os.path.basename(attached_file)
    attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
    message.attach(attachment)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode('UTF-8')).decode('ascii')}


# Kada se salje attachment, mi nikad ne zakacimo ceo fajl i tako posaljemo mail,
# nego se zakaci promenljiva koja sadrzi 'binarni sadrzaj' fajla
# U zavisnosti od tipa ova funkcija zna kako da procita i skladisti attachment
def read_attached_file(main_type, sub_type, attached_file):
    if main_type == 'text':
        temp = open(attached_file, 'r')
        attachment = MIMEText(temp.read(), _subtype=sub_type)
        temp.close()

    elif main_type == 'image':
        temp = open(attached_file, 'rb')
        attachment = MIMEImage(temp.read(), _subtype=sub_type)
        temp.close()

    elif main_type == 'audio':
        temp = open(attached_file, 'rb')
        attachment = MIMEAudio(temp.read(), _subtype=sub_type)
        temp.close()

    elif main_type == 'application' and sub_type == 'pdf':
        temp = open(attached_file, 'rb')
        attachment = MIMEApplication(temp.read(), _subtype=sub_type)
        temp.close()

    else:
        attachment = MIMEBase(main_type, sub_type)
        temp = open(attached_file, 'rb')
        attachment.set_payload(temp.read())
        temp.close()

    return attachment


def send_message_with_attachment(service, user_id, message_with_attachment, message_text):
    try:
        message_sent = (service.users().messages().send(userId=user_id, body=message_with_attachment).execute())
        message_id = message_sent['id']
        print(f'Poruka poslata (bez attachmenta) \n\n Id poruke: {message_id}\n\n Poruka:\n\n {message_text}')
    except errors.HttpError as error:
        print(f'Greska: {error}')
