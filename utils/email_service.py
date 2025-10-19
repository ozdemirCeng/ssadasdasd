"""
utils/email_service.py
Production-Ready SMTP Email Service
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import logger


class EmailService:
    """SMTP Email gönderme servisi"""

    def __init__(self):
        # .env'den al
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "Kocaeli Üniversitesi")

        # Email aktif mi?
        self.enabled = bool(self.smtp_user and self.smtp_password)

        if not self.enabled:
            logger.warning("⚠️  Email servisi devre dışı (SMTP ayarları eksik)")

    def send_password_reset_email(self, to_email, recipient_name, reset_link, expires_minutes=15):
        """
        Şifre sıfırlama emaili gönder

        Args:
            to_email (str): Alıcı email
            recipient_name (str): Alıcı adı
            reset_link (str): Sıfırlama linki
            expires_minutes (int): Token geçerlilik süresi (dakika)

        Returns:
            bool: Başarılı mı?
        """
        if not self.enabled:
            logger.warning("Email gönderilemedi: SMTP devre dışı")
            return False

        subject = "Şifre Sıfırlama Talebi - Kocaeli Üniversitesi"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8fafc; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 30px; text-align: center; background: linear-gradient(135deg, #00A651 0%, #008F47 100%); border-radius: 16px 16px 0 0;">
                                    <h1 style="margin: 0; color: white; font-size: 28px; font-weight: bold;">
                                        🎓 Kocaeli Üniversitesi
                                    </h1>
                                    <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">
                                        Sınav Takvimi Yönetim Sistemi
                                    </p>
                                </td>
                            </tr>

                            <!-- Body -->
                            <tr>
                                <td style="padding: 40px;">
                                    <h2 style="margin: 0 0 20px; color: #0f172a; font-size: 22px;">
                                        Merhaba {recipient_name},
                                    </h2>

                                    <p style="margin: 0 0 20px; color: #475569; font-size: 15px; line-height: 1.6;">
                                        Hesabınız için şifre sıfırlama talebinde bulundunuz. 
                                        Şifrenizi sıfırlamak için aşağıdaki butona tıklayın:
                                    </p>

                                    <!-- Button -->
                                    <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                        <tr>
                                            <td align="center">
                                                <a href="{reset_link}" 
                                                   style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #00A651 0%, #00C75F 100%); color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 12px rgba(0,166,81,0.3);">
                                                    Şifremi Sıfırla
                                                </a>
                                            </td>
                                        </tr>
                                    </table>

                                    <p style="margin: 20px 0; color: #64748b; font-size: 14px; line-height: 1.6;">
                                        Buton çalışmıyorsa aşağıdaki linki tarayıcınıza kopyalayın:
                                    </p>

                                    <p style="margin: 0 0 20px; padding: 12px; background: #f1f5f9; border-radius: 8px; color: #475569; font-size: 13px; word-break: break-all;">
                                        {reset_link}
                                    </p>

                                    <!-- Warning Box -->
                                    <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0; background: #fef2f2; border-left: 4px solid #dc2626; border-radius: 8px;">
                                        <tr>
                                            <td style="padding: 16px;">
                                                <p style="margin: 0; color: #991b1b; font-size: 14px; font-weight: bold;">
                                                    ⚠️ Önemli Güvenlik Uyarısı
                                                </p>
                                                <p style="margin: 8px 0 0; color: #dc2626; font-size: 13px; line-height: 1.5;">
                                                    Bu link <strong>{expires_minutes} dakika</strong> içinde geçerliliğini yitirecektir.<br>
                                                    Bu talebi siz yapmadıysanız, bu emaili görmezden gelin.
                                                </p>
                                            </td>
                                        </tr>
                                    </table>

                                    <p style="margin: 20px 0 0; color: #94a3b8; font-size: 13px;">
                                        Saygılarımızla,<br>
                                        <strong style="color: #475569;">Kocaeli Üniversitesi IT Destek</strong>
                                    </p>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px; background: #f8fafc; border-radius: 0 0 16px 16px; text-align: center;">
                                    <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                        © {datetime.now().year} Kocaeli Üniversitesi<br>
                                        Tüm hakları saklıdır.
                                    </p>
                                    <p style="margin: 10px 0 0; color: #cbd5e0; font-size: 11px;">
                                        Bu otomatik bir emaildir, lütfen yanıtlamayın.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        text_body = f"""
        Merhaba {recipient_name},

        Hesabınız için şifre sıfırlama talebinde bulundunuz.

        Şifrenizi sıfırlamak için aşağıdaki linke tıklayın:
        {reset_link}

        Bu link {expires_minutes} dakika içinde geçerliliğini yitirecektir.

        Bu talebi siz yapmadıysanız, bu emaili görmezden gelin.

        Saygılarımızla,
        Kocaeli Üniversitesi IT Destek
        """

        return self._send_email(to_email, subject, html_body, text_body)

    def send_welcome_email(self, to_email, recipient_name, role):
        """
        Hoş geldin emaili (yeni kullanıcı için)
        """
        if not self.enabled:
            return False

        subject = "Hoş Geldiniz - Sınav Takvimi Sistemi"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; background: #f8fafc; padding: 40px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; padding: 40px;">
                <h1 style="color: #00A651; text-align: center;">🎓 Hoş Geldiniz!</h1>

                <p style="font-size: 16px; color: #475569;">
                    Merhaba {recipient_name},
                </p>

                <p style="font-size: 15px; color: #475569; line-height: 1.6;">
                    Kocaeli Üniversitesi Sınav Takvimi Yönetim Sistemi'ne hoş geldiniz!
                </p>

                <div style="background: #f1f5f9; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <p style="margin: 0; color: #0f172a;"><strong>Rolünüz:</strong> {role}</p>
                    <p style="margin: 10px 0 0; color: #0f172a;"><strong>Email:</strong> {to_email}</p>
                </div>

                <p style="font-size: 14px; color: #64748b;">
                    Sisteme giriş yaparak tüm özelliklere erişebilirsiniz.
                </p>

                <p style="margin-top: 30px; font-size: 13px; color: #94a3b8; text-align: center;">
                    © {datetime.now().year} Kocaeli Üniversitesi
                </p>
            </div>
        </body>
        </html>
        """

        return self._send_email(to_email, subject, html_body)

    def _send_email(self, to_email, subject, html_body, text_body=None):
        """
        Email gönder (core function)

        Args:
            to_email (str): Alıcı
            subject (str): Konu
            html_body (str): HTML içerik
            text_body (str): Plain text içerik

        Returns:
            bool: Başarılı mı?
        """
        if not self.enabled:
            logger.warning("Email servisi devre dışı")
            return False

        try:
            # Email oluştur
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = to_email
            msg['Subject'] = subject

            # Plain text part (fallback)
            if text_body:
                msg.attach(MIMEText(text_body, 'plain', 'utf-8'))

            # HTML part
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # SMTP bağlantısı
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"✓ Email gönderildi: {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication hatası - Kullanıcı adı/şifre yanlış")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP hatası: {e}")
            return False
        except Exception as e:
            logger.error(f"Email gönderme hatası: {e}")
            return False

    def test_connection(self):
        """SMTP bağlantısını test et"""
        if not self.enabled:
            return False, "SMTP ayarları eksik"

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)

            logger.info("✓ SMTP bağlantısı başarılı")
            return True, "Bağlantı başarılı"

        except Exception as e:
            logger.error(f"SMTP test hatası: {e}")
            return False, str(e)