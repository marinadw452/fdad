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

ADMIN_IDS = [
    123456789,  # ضع معرف التلقرام للمدير الأول
    987654321,  # ضع معرف التلقرام للمدير الثاني
]

# إعدادات متقدمة
DEBUG = False
LOG_LEVEL = "INFO"
MAX_CART_ITEMS = 50
SESSION_TIMEOUT = 3600  # ساعة واحدة بالثواني

# إعدادات الويب (للمستقبل)
WEBHOOK_URL = None  # ضع رابط الويب هوك إذا أردت استخدامه
WEBAPP_HOST = "localhost"
WEBAPP_PORT = 8080

# رسائل مخصصة
WELCOME_MESSAGE = """🌟 مرحباً بك في محل فخامة بسبوستي 🌟

أهلاً وسهلاً! نحن متخصصون في تقديم أفضل أنواع البسبوسة الطازجة والقهوة العربية الأصيلة"""

SHOP_INFO = {
    "name": "فخامة بسبوستي",
    "location": "تبوك - المملكة العربية السعودية", 
    "working_hours": "9 صباحاً - 12 منتصف الليل",
    "delivery_time": "20-35 دقيقة"
}"
