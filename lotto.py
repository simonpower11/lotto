import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==============================
# CONFIGURAZIONE
# ==============================
NUMERI_GIOCATI = {21, 52, 60, 71, 73, 39}  # i tuoi numeri
RUOTA = "Bari"

EMAIL_ADDRESS = "simo.espi1151@gmail.com"       # tua Gmail 
EMAIL_PASSWORD = "sblj omvf yfxy bkev"         # password app generata da Google 
DESTINATARIO = "simo.espi1151@gmail.com"   # a chi inviare l'email
# ==============================

def get_estrazione_bari():
    url = "https://www.lottomaticaitalia.it/lotto/estrazioni-del-lotto"
    try:
        r = requests.get(url, verify=False)  # ignora SSL per evitare errori
    except Exception as e:
        print("Errore download estrazione:", e)
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    tabelle = soup.find_all("table")
    for tab in tabelle:
        caption = tab.find("caption")
        if caption and caption.text.strip() == RUOTA:
            numeri = [int(td.text.strip()) for td in tab.find_all("td") if td.text.strip().isdigit()]
            return numeri
    return []

def check_vincita(numeri_estratti):
    return NUMERI_GIOCATI & set(numeri_estratti)

def send_email(subject, body):
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = DESTINATARIO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, DESTINATARIO, msg.as_string())
        server.quit()
        print("✅ Email inviata.")
    except Exception as e:
        print("❌ Errore invio email:", e)

if __name__ == "__main__":
    estratti = get_estrazione_bari()
    if not estratti:
        subject = "❌ Lotto - Nessuna estrazione trovata"
        body = "<p>Non sono riuscito a recuperare i numeri estratti oggi.</p>"
    else:
        vincenti = check_vincita(estratti)
        if vincenti:
            subject = "🎉 Hai vinto al Lotto!"
            body = f"<h2>Risultati Lotto - Ruota di Bari</h2>" \
                   f"<p><b>Numeri estratti:</b> {estratti}</p>" \
                   f"<p><b>I tuoi numeri giocati:</b> {sorted(NUMERI_GIOCATI)}</p>" \
                   f"<p style='color:green;'><b>Hai indovinato:</b> {sorted(vincenti)}</p>"
        else:
            subject = "📢 Esito Lotto - Nessuna vincita"
            body = f"<h2>Risultati Lotto - Ruota di Bari</h2>" \
                   f"<p><b>Numeri estratti:</b> {estratti}</p>" \
                   f"<p><b>I tuoi numeri giocati:</b> {sorted(NUMERI_GIOCATI)}</p>" \
                   f"<p style='color:red;'><b>Nessuna corrispondenza oggi.</b></p>"

    send_email(subject, body)
