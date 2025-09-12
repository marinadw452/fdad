import os

# ==================== إعدادات تليجرام ====================
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ==================== إعدادات قاعدة البيانات ====================
DATABASE_URL = os.getenv('DATABASE_URL')

# ==================== إعدادات المحل ====================
SHOP_NAME = os.getenv('SHOP_NAME')  # مثال: "محل فخامة بسبوستي"
SHOP_LOCATION = os.getenv('SHOP_LOCATION')  # مثال: "تبوك - المملكة العربية السعودية"
SHOP_WHATSAPP = os.getenv('SHOP_WHATSAPP')  
SHOP_CHAT_ID = os.getenv('SHOP_CHAT_ID')  

# ==================== إعدادات النظام ====================
DELIVERY_FEE = int(os.getenv('DELIVERY_FEE', '0'))  
MIN_ORDER_AMOUNT = int(os.getenv('MIN_ORDER_AMOUNT', '10'))
