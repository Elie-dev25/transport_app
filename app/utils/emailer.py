import smtplib
from email.mime.text import MIMEText
from flask import current_app

def send_email(subject: str, body: str, to_email: str) -> bool:
    """Envoie un email simple en texte. Retourne True si envoyé, False sinon.
    Utilise les variables de config: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_USE_TLS, SMTP_USE_SSL, MAIL_FROM.
    Si ces variables ne sont pas définies, log et retourne False sans lever d'exception.
    """
    cfg = current_app.config
    host = cfg.get('SMTP_HOST')
    port = cfg.get('SMTP_PORT')
    user = cfg.get('SMTP_USERNAME')
    pwd = cfg.get('SMTP_PASSWORD')
    use_tls = cfg.get('SMTP_USE_TLS', True)
    use_ssl = cfg.get('SMTP_USE_SSL', False)
    mail_from = cfg.get('MAIL_FROM') or user

    if not host or not port or not to_email or not mail_from:
        current_app.logger.warning('Email non envoyé: configuration SMTP incomplète.')
        return False

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = to_email

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port)
        else:
            server = smtplib.SMTP(host, port)
            if use_tls:
                server.starttls()
        if user and pwd:
            server.login(user, pwd)
        server.sendmail(mail_from, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erreur envoi email: {e}")
        return False
