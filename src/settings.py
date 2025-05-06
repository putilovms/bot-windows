from dotenv import load_dotenv
import os

load_dotenv()

USER_TOKEN = os.getenv('USER_TOKEN')
PARTNER_TOKEN = os.getenv('PARTNER_TOKEN')
SALON_ID = os.getenv('SALON_ID')  # филиал
COMPANY_ID = os.getenv('COMPANY_ID')  # сеть
FORM_ID = os.getenv('FORM_ID')  # форма
BOT_TOKEN = os.getenv('BOT_TOKEN')
