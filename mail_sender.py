import imaplib
import smtplib

def send():
    #try:
    mail = imaplib.IMAP4_SSL('imap.yandex.ru')
    mail.login('d.bondarev.86@yandex.ru', 'kpwoltwjqpsboxde')
    mail.sendmail("justkiddingboat@gmail.com", "d.bondarev.86@yandex.ru", "go to bed!")


send()