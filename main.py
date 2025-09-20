import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg2
import psycopg2.extras
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove, BotCommand
from dataclasses import dataclass
from enum import Enum

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================== إعدادات البوت ==================
try:
    from config import BOT_TOKEN, PG_DB, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, SHOP_WHATSAPP
except ImportError:
    logger.error("يرجى إنشاء ملف config.py مع الإعدادات المطلوبة")
    exit(1)

# ================== بيانات المنتجات المحدثة ==================
MENU_DATA = {
    'basboosa': [
        {
            'id': 'basboosa_normal',
            'name': 'بسبوسة عادية',
            'description': 'بسبوسة لذيذة بالطعم التقليدي الأصيل',
            'emoji': '🧁',
            'sizes': {
                'small': {'name': 'صغير', 'price': 12, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 24, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_nutella',
            'name': 'بسبوسة نوتيلا',
            'description': 'بسبوسة محشوة بكريمة النوتيلا الشهية',
            'emoji': '🍫',
            'sizes': {
                'small': {'name': 'صغير', 'price': 15, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 28, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_chocolate_saudi',
            'name': 'بسبوسة شوكولاتة السعودية',
            'description': 'بسبوسة بنكهة الشوكولاتة السعودية الفاخرة',
            'emoji': '🍩',
            'sizes': {
                'small': {'name': 'صغير', 'price': 14, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 26, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_cheese',
            'name': 'بسبوسة جبنة',
            'description': 'بسبوسة حلوة مع طعم الجبنة المميز',
            'emoji': '🧀',
            'sizes': {
                'small': {'name': 'صغير', 'price': 13, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 25, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_kinder',
            'name': 'بسبوسة كندر',
            'description': 'بسبوسة بنكهة الكندر اللذيذة',
            'emoji': '🎂',
            'sizes': {
                'small': {'name': 'صغير', 'price': 16, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 30, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_happiness',
            'name': 'بسبوسة نكهة السعادة',
            'description': 'بسبوسة بنكهة خاصة تجلب السعادة',
            'emoji': '😊',
            'sizes': {
                'small': {'name': 'صغير', 'price': 14, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 27, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_oreo',
            'name': 'بسبوسة أوريو',
            'description': 'بسبوسة محشوة بقطع الأوريو المقرمشة',
            'emoji': '🖤',
            'sizes': {
                'small': {'name': 'صغير', 'price': 18, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 35, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_kitkat',
            'name': 'بسبوسة كت كات',
            'description': 'بسبوسة بنكهة الكت كات المقرمش',
            'emoji': '🍫',
            'sizes': {
                'small': {'name': 'صغير', 'price': 18, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 35, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_lotus',
            'name': 'بسبوسة لوتس',
            'description': 'بسبوسة بنكهة اللوتس الكراميل',
            'emoji': '🍪',
            'sizes': {
                'small': {'name': 'صغير', 'price': 15, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 28, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_snickers',
            'name': 'بسبوسة سنيكرز',
            'description': 'بسبوسة بنكهة السنيكرز بالفول السوداني',
            'emoji': '🥜',
            'sizes': {
                'small': {'name': 'صغير', 'price': 17, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 32, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_galaxy',
            'name': 'بسبوسة جلاكسي',
            'description': 'بسبوسة بطعم شوكولاتة جلاكسي الكريمية',
            'emoji': '🌌',
            'sizes': {
                'small': {'name': 'صغير', 'price': 16, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 30, 'emoji': '🍽️'},
            }
        },
        {
            'id': 'basboosa_cinnamon',
            'name': 'بسبوسة سنابون',
            'description': 'بسبوسة بنكهة القرفة العربية الأصيلة',
            'emoji': '🌿',
            'sizes': {
                'small': {'name': 'صغير', 'price': 13, 'emoji': '🥄'},
                'medium': {'name': 'متوسط', 'price': 24, 'emoji': '🍽️'},
            }
        }
    ],
    'drinks': [
        {
            'id': 'saudi_coffee_pot',
            'name': 'قهوة سعودية دلة',
            'description': 'قهوة عربية أصيلة في دلة تقليدية',
            'emoji': '☕',
            'sizes': {
                'single': {'name': 'دلة واحدة', 'price': 35, 'emoji': '🫖'}
            }
        },
        {
            'id': 'saudi_coffee_cup',
            'name': 'كوب قهوة سعودي',
            'description': 'كوب قهوة عربية تقليدية',
            'emoji': '☕',
            'sizes': {
                'single': {'name': 'كوب واحد', 'price': 5, 'emoji': '🥃'}
            }
        },
        {
            'id': 'distribution_plate',
            'name': 'صحن توزيعات',
            'description': 'صحن مكس من أفضل الحلويات للضيافة',
            'emoji': '🍽️',
            'sizes': {
                'single': {'name': 'صحن واحد', 'price': 49, 'emoji': '🍽️'}
            }
        },
        {
            'id': 'millet_cake',
            'name': 'كيكة الدخن',
            'description': 'كيكة صحية من الدخن الطبيعي',
            'emoji': '🍰',
            'sizes': {
                'single': {'name': 'قطعة واحدة', 'price': 23, 'emoji': '🍰'}
            }
        }
    ]
}

# ================== كلاسات إدارة البيانات ==================
class DatabaseManager:
    """مدير قاعدة البيانات المتطور"""
    
    def __init__(self):
        self.connection_params = {
            'dbname': PG_DB,
            'user': PG_USER,
            'password': PG_PASSWORD,
            'host': PG_HOST,
            'port': PG_PORT
        }
    
    @asynccontextmanager
    async def get_connection(self):
        """الحصول على اتصال قاعدة البيانات مع إدارة الموارد"""
        conn = None
        try:
            conn = psycopg2.connect(
                **self.connection_params,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            yield conn
        except Exception as e:
            logger.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    async def init_database(self):
        """تهيئة قاعدة البيانات"""
        try:
            async with self.get_connection() as conn:
                cur = conn.cursor()
                
                # إنشاء جدول الطلبات المحدث
                cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    order_uuid UUID DEFAULT gen_random_uuid(),
                    customer_id BIGINT NOT NULL,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    items JSONB NOT NULL,
                    total_amount INTEGER NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    location_lat FLOAT,
                    location_lon FLOAT,
                    location_address TEXT,
                    delivery_notes TEXT,
                    estimated_time INTEGER DEFAULT 30,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # إنشاء جدول تقييم العملاء
                cur.execute("""
                CREATE TABLE IF NOT EXISTS customer_reviews (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id),
                    customer_id BIGINT NOT NULL,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # إنشاء جدول الإحصائيات
                cur.execute("""
                CREATE TABLE IF NOT EXISTS bot_analytics (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # إنشاء فهارس للأداء
                cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status, created_at)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_analytics_action ON bot_analytics (action, timestamp)")
                
                conn.commit()
                logger.info("✅ تم إعداد قاعدة البيانات بنجاح")
                
        except Exception as e:
            logger.error(f"خطأ في إعداد قاعدة البيانات: {e}")
            raise
    
    async def create_order(self, customer_id: int, customer_name: str, customer_phone: str, 
                          items: List[Dict], total_amount: int, location_data: Dict = None) -> int:
        """إنشاء طلب جديد"""
        try:
            async with self.get_connection() as conn:
                cur = conn.cursor()
                
                cur.execute("""
                    INSERT INTO orders (customer_id, customer_name, customer_phone, items, 
                                      total_amount, location_lat, location_lon, location_address)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, order_uuid
                """, (
                    customer_id, customer_name, customer_phone, json.dumps(items), 
                    total_amount,
                    location_data.get('lat') if location_data else None,
                    location_data.get('lon') if location_data else None,
                    location_data.get('address') if location_data else None
                ))
                
                result = cur.fetchone()
                conn.commit()
                
                logger.info(f"تم إنشاء الطلب رقم {result['id']} للعميل {customer_id}")
                return result['id']
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء الطلب: {e}")
            raise
    
    async def log_analytics(self, user_id: int, action: str, data: Dict = None):
        """تسجيل الإحصائيات"""
        try:
            async with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO bot_analytics (user_id, action, data)
                    VALUES (%s, %s, %s)
                """, (user_id, action, json.dumps(data) if data else None))
                conn.commit()
        except Exception as e:
            logger.error(f"خطأ في تسجيل الإحصائيات: {e}")

# ================== حالات البوت ==================
class OrderStates(StatesGroup):
    choosing_category = State()
    choosing_product = State()
    choosing_size = State()
    choosing_quantity = State()
    entering_contact = State()
    entering_location = State()
    adding_notes = State()
    confirming_order = State()

# ================== مدير المنتجات ==================
class ProductManager:
    """مدير المنتجات المتطور"""
    
    @staticmethod
    def get_categories():
        """الحصول على فئات المنتجات"""
        return {
            'basboosa': {'name': 'البسبوسة', 'emoji': '🧁', 'description': 'تشكيلة متنوعة من البسبوسة الشهية'},
            'drinks': {'name': 'المشروبات والإضافات', 'emoji': '☕', 'description': 'قهوة عربية وحلويات إضافية'}
        }
    
    @staticmethod
    def get_products_by_category(category: str):
        """الحصول على المنتجات حسب الفئة"""
        return MENU_DATA.get(category, [])
    
    @staticmethod
    def get_product_by_id(product_id: str):
        """البحث عن منتج بالمعرف"""
        for category_products in MENU_DATA.values():
            for product in category_products:
                if product['id'] == product_id:
                    return product
        return None

# ================== مدير السلة المتطور ==================
class CartManager:
    """مدير السلة المتطور"""
    
    @staticmethod
    async def add_item(state: FSMContext, product_id: str, size: str, quantity: int):
        """إضافة عنصر للسلة"""
        data = await state.get_data()
        cart = data.get('cart', [])
        
        product = ProductManager.get_product_by_id(product_id)
        if not product:
            return False
        
        size_info = product['sizes'].get(size)
        if not size_info:
            return False
        
        # البحث عن عنصر مشابه في السلة
        existing_item = None
        for item in cart:
            if item['product_id'] == product_id and item['size'] == size:
                existing_item = item
                break
        
        if existing_item:
            existing_item['quantity'] += quantity
            existing_item['total_price'] = existing_item['quantity'] * existing_item['unit_price']
        else:
            cart.append({
                'product_id': product_id,
                'product_name': product['name'],
                'product_emoji': product['emoji'],
                'size': size,
                'size_name': size_info['name'],
                'size_emoji': size_info['emoji'],
                'quantity': quantity,
                'unit_price': size_info['price'],
                'total_price': quantity * size_info['price']
            })
        
        await state.update_data(cart=cart)
        return True
    
    @staticmethod
    async def get_cart_total(state: FSMContext):
        """حساب إجمالي السلة"""
        data = await state.get_data()
        cart = data.get('cart', [])
        return sum(item['total_price'] for item in cart)
    
    @staticmethod
    async def get_cart_items_count(state: FSMContext):
        """عدد العناصر في السلة"""
        data = await state.get_data()
        cart = data.get('cart', [])
        return sum(item['quantity'] for item in cart)
    
    @staticmethod
    async def clear_cart(state: FSMContext):
        """مسح السلة"""
        await state.update_data(cart=[])

# ================== أزرار التحكم المتطورة ==================
class KeyboardManager:
    """مدير الأزرار المتطور"""
    
    @staticmethod
    def main_menu():
        """القائمة الرئيسية المتطورة"""
        builder = InlineKeyboardBuilder()
        
        categories = ProductManager.get_categories()
        for category_id, category_info in categories.items():
            builder.button(
                text=f"{category_info['emoji']} {category_info['name']}",
                callback_data=f"category:{category_id}"
            )
        
        builder.button(text="🛒 السلة", callback_data="cart:view")
        builder.button(text="📊 طلباتي", callback_data="orders:my")
        builder.button(text="📞 تواصل معنا", callback_data="contact:us")
        builder.button(text="ℹ️ عن المحل", callback_data="about:shop")
        
        builder.adjust(1, 2, 2)
        return builder.as_markup()
    
    @staticmethod
    def category_products(category: str):
        """عرض منتجات الفئة"""
        builder = InlineKeyboardBuilder()
        products = ProductManager.get_products_by_category(category)
        
        for product in products:
            builder.button(
                text=f"{product['emoji']} {product['name']}",
                callback_data=f"product:{product['id']}"
            )
        
        builder.button(text="🔙 القائمة الرئيسية", callback_data="main:menu")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def product_sizes(product_id: str):
        """اختيار أحجام المنتج"""
        builder = InlineKeyboardBuilder()
        product = ProductManager.get_product_by_id(product_id)
        
        if not product:
            return None
        
        for size_id, size_info in product['sizes'].items():
            builder.button(
                text=f"{size_info['emoji']} {size_info['name']} - {size_info['price']} ر.س",
                callback_data=f"size:{product_id}:{size_id}"
            )
        
        builder.button(text="🔙 رجوع", callback_data=f"category:{product_id.split('_')[0]}")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def quantity_selector(product_id: str, size: str):
        """اختيار الكمية"""
        builder = InlineKeyboardBuilder()
        
        # أزرار الكمية السريعة
        for qty in [1, 2, 3, 5, 10]:
            builder.button(
                text=f"{qty}",
                callback_data=f"quantity:{product_id}:{size}:{qty}"
            )
        
        builder.button(text="🔙 رجوع", callback_data=f"product:{product_id}")
        builder.adjust(5, 1)
        return builder.as_markup()
    
    @staticmethod
    def cart_actions():
        """أزرار السلة"""
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ تأكيد الطلب", callback_data="order:confirm")
        builder.button(text="🗑️ إفراغ السلة", callback_data="cart:clear")
        builder.button(text="➕ إضافة المزيد", callback_data="main:menu")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def location_input():
        """إدخال الموقع"""
        builder = ReplyKeyboardBuilder()
        builder.button(text="📍 مشاركة موقعي", request_location=True)
        builder.button(text="✍️ كتابة العنوان")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

# ================== إعداد البوت المتطور ==================
db_manager = DatabaseManager()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================== معالجات الأحداث المتطورة ==================

@dp.message(F.text == "/start")
async def start_handler(message: types.Message, state: FSMContext):
    """معالج البداية المتطور"""
    await state.clear()
    await state.set_data({'cart': []})
    
    # تسجيل الإحصائيات
    await db_manager.log_analytics(message.from_user.id, 'start_command')
    
    welcome_text = f"""🌟 مرحباً بك في محل فخامة بسبوستي 🌟

👋 أهلاً {message.from_user.first_name}!

🏪 محلنا متخصص في تقديم أفضل أنواع البسبوسة الطازجة والقهوة العربية الأصيلة

📍 الموقع: تبوك، المملكة العربية السعودية

✨ استمتع بتجربة طلب سهلة ومريحة"""
    
    await message.answer(
        welcome_text, 
        reply_markup=KeyboardManager.main_menu()
    )

@dp.callback_query(F.data == "main:menu")
async def main_menu_handler(callback: types.CallbackQuery):
    """العودة للقائمة الرئيسية"""
    await callback.message.edit_text(
        "🏪 محل فخامة بسبوستي\n\nاختر ما تريده من القائمة:",
        reply_markup=KeyboardManager.main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("category:"))
async def category_handler(callback: types.CallbackQuery):
    """معالج فئات المنتجات"""
    category = callback.data.split(":")[1]
    
    # تسجيل الإحصائيات
    await db_manager.log_analytics(
        callback.from_user.id, 
        'category_selected', 
        {'category': category}
    )
    
    categories = ProductManager.get_categories()
    category_info = categories.get(category)
    
    if not category_info:
        await callback.answer("❌ فئة غير موجودة", show_alert=True)
        return
    
    text = f"{category_info['emoji']} {category_info['name']}\n\n"
    text += f"📝 {category_info['description']}\n\n"
    text += "اختر المنتج المطلوب:"
    
    await callback.message.edit_text(
        text,
        reply_markup=KeyboardManager.category_products(category)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("product:"))
async def product_handler(callback: types.CallbackQuery):
    """معالج عرض المنتج"""
    product_id = callback.data.split(":")[1]
    product = ProductManager.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("❌ المنتج غير موجود", show_alert=True)
        return
    
    # تسجيل الإحصائيات
    await db_manager.log_analytics(
        callback.from_user.id,
        'product_viewed',
        {'product_id': product_id}
    )
    
    text = f"{product['emoji']} {product['name']}\n\n"
    text += f"📄 {product['description']}\n\n"
    text += "🎯 اختر الحجم المطلوب:"
    
    keyboard = KeyboardManager.product_sizes(product_id)
    if keyboard:
        await callback.message.edit_text(text, reply_markup=keyboard)
    else:
        await callback.answer("❌ لا توجد أحجام متاحة", show_alert=True)
    
    await callback.answer()

@dp.callback_query(F.data.startswith("size:"))
async def size_handler(callback: types.CallbackQuery):
    """معالج اختيار الحجم"""
    _, product_id, size = callback.data.split(":")
    
    product = ProductManager.get_product_by_id(product_id)
    if not product:
        await callback.answer("❌ المنتج غير موجود", show_alert=True)
        return
    
    size_info = product['sizes'].get(size)
    if not size_info:
        await callback.answer("❌ الحجم غير متاح", show_alert=True)
        return
    
    text = f"{product['emoji']} {product['name']}\n"
    text += f"{size_info['emoji']} الحجم: {size_info['name']}\n"
    text += f"💰 السعر: {size_info['price']} ر.س\n\n"
    text += "🔢 اختر الكمية:"
    
    await callback.message.edit_text(
        text,
        reply_markup=KeyboardManager.quantity_selector(product_id, size)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("quantity:"))
async def quantity_handler(callback: types.CallbackQuery, state: FSMContext):
    """معالج اختيار الكمية"""
    _, product_id, size, quantity = callback.data.split(":")
    quantity = int(quantity)
    
    # إضافة للسلة
    success = await CartManager.add_item(state, product_id, size, quantity)
    
    if not success:
        await callback.answer("❌ خطأ في إضافة المنتج", show_alert=True)
        return
    
    product = ProductManager.get_product_by_id(product_id)
    size_info = product['sizes'][size]
    total_price = quantity * size_info['price']
    
    # تسجيل الإحصائيات
    await db_manager.log_analytics(
        callback.from_user.id,
        'item_added_to_cart',
        {
            'product_id': product_id,
            'size': size,
            'quantity': quantity,
            'price': total_price
        }
    )
    
    cart_count = await CartManager.get_cart_items_count(state)
    
    text = f"✅ تم إضافة المنتج للسلة!\n\n
