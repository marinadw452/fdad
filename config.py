import os

# ==================== إعدادات تليجرام ====================
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# ==================== إعدادات قاعدة البيانات ====================
PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_DB = os.getenv('PG_DB', 'basboosa_db')
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'your_password')

# ==================== إعدادات المحل ====================
SHOP_NAME = "محل فخامة بسبوستي"
SHOP_LOCATION = "تبوك - المملكة العربية السعودية"
SHOP_WHATSAPP = os.getenv('SHOP_WHATSAPP', '966501234567')  # رقم المحل بدون +
SHOP_CHAT_ID = os.getenv('SHOP_CHAT_ID', None)  # معرف مجموعة المحل

# ==================== إعدادات النظام ====================
DELIVERY_FEE = int(os.getenv('DELIVERY_FEE', '0'))  # رسوم التوصيل
MIN_ORDER_AMOUNT = int(os.getenv('MIN_ORDER_AMOUNT', '10'))  # أقل مبلغ طلب