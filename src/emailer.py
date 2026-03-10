import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def build_html_email(summary: str, massifs: list[str]) -> str:
    """Construit l'email HTML avec le résumé."""
    today = datetime.now().strftime("%A %d %B %Y").capitalize()
    massifs_str = ", ".join(massifs)

    # Convertit le markdown basique en HTML
    html_summary = summary
    html_summary = html_summary.replace("\n\n", "</p><p>")
    html_summary = html_summary.replace("\n", "<br>")
    # Gras **texte**
    import re
    html_summary = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html_summary)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Skitour Digest</title>
</head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:'Georgia',serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:30px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a3a5c,#2d6a9f);padding:28px 36px;">
            <p style="margin:0;color:#a8c8e8;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Skitour Digest</p>
            <h1 style="margin:6px 0 0;color:#ffffff;font-size:22px;font-weight:normal;">{today}</h1>
            <p style="margin:6px 0 0;color:#7aadcf;font-size:13px;">Massifs : {massifs_str}</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:32px 36px;">
            <p style="margin:0 0 16px;color:#2c3e50;font-size:15px;line-height:1.8;">
              {html_summary}
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f8fafc;padding:18px 36px;border-top:1px solid #e2e8f0;">
            <p style="margin:0;color:#94a3b8;font-size:12px;">
              Données issues de <a href="https://www.skitour.fr" style="color:#2d6a9f;">skitour.fr</a> · Résumé généré automatiquement · Vérifiez toujours les conditions terrain avant de partir.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_email(summary: str, massifs: list[str], config: dict) -> None:
    """
    Envoie l'email via SMTP.
    config doit contenir : smtp_host, smtp_port, smtp_user, smtp_password, from_email, to_emails
    """
    today = datetime.now().strftime("%d/%m/%Y")
    subject = f"🎿 Skitour Digest — {today}"

    html_body = build_html_email(summary, massifs)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config["from_email"]
    msg["To"] = ", ".join(config["to_emails"])

    # Partie texte plain (fallback)
    text_part = MIMEText(summary, "plain", "utf-8")
    html_part = MIMEText(html_body, "html", "utf-8")
    msg.attach(text_part)
    msg.attach(html_part)

    with smtplib.SMTP_SSL(config["smtp_host"], int(config["smtp_port"])) as server:
        server.login(config["smtp_user"], config["smtp_password"])
        server.sendmail(
            config["from_email"],
            config["to_emails"],
            msg.as_string(),
        )
    print(f"  ✓ Email envoyé à {', '.join(config['to_emails'])}")
