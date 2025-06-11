import smtplib
from email.mime.text import MIMEText
from config import EMAIL_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

def enviar_email(mensagem, acao):
    msg = MIMEText(mensagem)
    msg['Subject'] = f"Alerta de Trading: {acao}"
    msg['From'] = EMAIL_CONFIG['remetente']
    msg['To'] = EMAIL_CONFIG['destinatario']
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_CONFIG['remetente'], os.getenv('EMAIL_PASSWORD'))
        smtp.send_message(msg)