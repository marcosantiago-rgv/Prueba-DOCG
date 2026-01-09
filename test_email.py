import smtplib
import os
from dotenv import load_dotenv

load_dotenv()  # Esto carga tu archivo .env

usuario = os.getenv("EMAIL_USUARIO")
contraseña = os.getenv("EMAIL_CONTRASEÑA")

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(usuario, contraseña)
        print("Conexión exitosa")
except Exception as e:
    print("Error:", e)
