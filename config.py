import os

# ==================== إعدادات تليجرام ====================
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ==================== إعدادات قاعدة البيانات ====================
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DB = os.getenv('PG_DB')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')

# ==================== إعدادات المحل ====================
SHOP_NAME = os.getenv('SHOP_NAME')  # مثال: "محل فخامة بسبوستي"
SHOP_LOCATION = os.getenv('SHOP_LOCATION')  # مثال: "تبوك - المملكة العربية السعودية"
SHOP_WHATSAPP = os.getenv('SHOP_WHATSAPP')  
SHOP_CHAT_ID = os.getenv('SHOP_CHAT_ID')  

# ==================== إعدادات النظام ====================
DELIVERY_FEE = int(os.getenv('DELIVERY_FEE', '0'))  
MIN_ORDER_AMOUNT = int(os.getenv('MIN_ORDER_AMOUNT', '10'))
