import asyncio
import json
import psycopg2
import psycopg2.extras
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import BOT_TOKEN, PG_DB, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, SHOP_WHATSAPP

# ================== قاعدة البيانات ==================
def get_conn():
    return psycopg2.connect(
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT,
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    
    # جدول المنتجات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category VARCHAR(50) NOT NULL,
        price_s INTEGER,
        price_m INTEGER, 
        price_l INTEGER,
        available BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # جدول الطلبات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        customer_id BIGINT NOT NULL,
        customer_name TEXT,
        customer_phone TEXT,
        total_amount INTEGER NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        location_lat FLOAT,
        location_lon FLOAT,
        location_address TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # جدول تفاصيل الطلبات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(id),
        product_id INTEGER REFERENCES products(id),
        quantity INTEGER NOT NULL,
        size VARCHAR(2) CHECK (size IN ('S', 'M', 'L')),
        unit_price INTEGER NOT NULL,
        total_price INTEGER NOT NULL
    )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def insert_menu_data():
    """إدراج بيانات المنيو"""
    conn = get_conn()
    cur = conn.cursor()
    
    menu_items = [
        # البسبوسة
        ('بسبوسة مشكل', 'basboosa', 18, 36, None),
        ('بسبوسة سادة', 'basboosa', 12, 24, None),
        ('بسبوسة قشطة', 'basboosa', 18, 36, None),
        ('بسبوسة توفي', 'basboosa', 18, 36, None),
        ('بسبوسة نوتيلا', 'basboosa', 18, 36, None),
        ('فلفل رد', 'basboosa', 12, 24, None),
        ('كرنشي الجبنة', 'basboosa', 12, 24, None),
        ('النكهة السعودية', 'basboosa', 12, 24, None),
        ('جبنة', 'basboosa', 12, 24, None),
        ('كندر', 'basboosa', 12, 24, None),
        ('نكهت السعادة', 'basboosa', 12, 24, None),
        ('راويو', 'basboosa', 18, 36, None),
        ('كتكات', 'basboosa', 18, 36, None),
        ('لوتس', 'basboosa', 12, 24, None),
        ('سنيكرز', 'basboosa', 12, 24, None),
        ('جلاكسي', 'basboosa', 12, 24, None),
        ('سنابون', 'basboosa', 12, 24, None),
        
        # المشروبات
        ('قهوة سعودية دلة', 'drinks', 35, None, None),
        ('كوب قهوة سعودي', 'drinks', 5, None, None),
        ('صحن توزيعات', 'drinks', 49, None, None),
        ('كيكة الدخن', 'drinks', 23, None, None)
    ]
    
    for item in menu_items:
        cur.execute("""
            INSERT INTO products (name, category, price_s, price_m, price_l)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, item)
    
    conn.commit()
    cur.close()
    conn.close()

# ================== حالات البوت ==================
class OrderStates(StatesGroup):
    viewing_menu = State()
    selecting_quantity = State()
    selecting_size = State()
    cart_review = State()
    entering_contact = State()
    entering_location = State()
    confirming_order = State()

# ================== دوال قاعدة البيانات ==================
def get_products_by_category(category):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE category=%s AND available=TRUE ORDER BY name", (category,))
    products = cur.fetchall()
    cur.close()
    conn.close()
    return products

def get_product_by_id(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cur.fetchone()
    cur.close()
    conn.close()
    return product

def create_order(customer_id, customer_name, customer_phone, total_amount, items, location_data=None):
    conn = get_conn()
    cur = conn.cursor()
    
    # إنشاء الطلب
    cur.execute("""
        INSERT INTO orders (customer_id, customer_name, customer_phone, total_amount, 
                          location_lat, location_lon, location_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
    """, (
        customer_id, customer_name, customer_phone, total_amount,
        location_data.get('lat') if location_data else None,
        location_data.get('lon') if location_data else None,
        location_data.get('address') if location_data else None
    ))
    
    order_id = cur.fetchone()['id']
    
    # إضافة العناصر
    for item in items:
        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, size, unit_price, total_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            order_id, item['product_id'], item['quantity'], 
            item['size'], item['unit_price'], item['total_price']
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    return order_id

# ================== أزرار التحكم ==================
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🧁 البسبوسة", callback_data="menu_basboosa")
    builder.button(text="☕ المشروبات", callback_data="menu_drinks")
    builder.button(text="🛒 عرض السلة", callback_data="view_cart")
    builder.button(text="📞 تواصل معنا", callback_data="contact_us")
    builder.adjust(2)
    return builder.as_markup()

def products_keyboard(products):
    builder = InlineKeyboardBuilder()
    for product in products:
        price_text = f"ر.س {product['price_s']}"
        if product['price_m']:
            price_text += f" - {product['price_m']}"
        builder.button(
            text=f"{product['name']} ({price_text})",
            callback_data=f"product_{product['id']}"
        )
    builder.button(text="🔙 القائمة الرئيسية", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def size_keyboard(product):
    builder = InlineKeyboardBuilder()
    if product['price_s']:
        builder.button(text=f"صغير - {product['price_s']} ر.س", callback_data=f"size_S_{product['id']}")
    if product['price_m']:
        builder.button(text=f"متوسط - {product['price_m']} ر.س", callback_data=f"size_M_{product['id']}")
    if product['price_l']:
        builder.button(text=f"كبير - {product['price_l']} ر.س", callback_data=f"size_L_{product['id']}")
    builder.button(text="🔙 رجوع", callback_data=f"menu_{product['category']}")
    builder.adjust(1)
    return builder.as_markup()

def quantity_keyboard(product_id, size):
    builder = InlineKeyboardBuilder()
    for i in range(1, 11):
        builder.button(text=str(i), callback_data=f"qty_{i}_{product_id}_{size}")
    builder.button(text="🔙 رجوع", callback_data=f"product_{product_id}")
    builder.adjust(5)
    return builder.as_markup()

def cart_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ تأكيد الطلب", callback_data="confirm_order")
    builder.button(text="🗑️ إفراغ السلة", callback_data="clear_cart")
    builder.button(text="➕ إضافة المزيد", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def location_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📍 إرسال موقعي", request_location=True)
    builder.button(text="💬 كتابة العنوان يدوياً")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

# ================== إعداد البوت ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================== معالجات الأحداث ==================
@dp.message(F.text == "/start")
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_data({'cart': []})
    
    welcome_text = """
🌟 أهلاً وسهلاً بك في محل فخامة بسبوستي 🌟

📍 تبوك - المملكة العربية السعودية

اختر من قائمتنا الشهية:
    """
    
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())

@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🏪 محل فخامة بسبوستي\n\nاختر القسم الذي تريده:",
        reply_markup=main_menu_keyboard()
    )

@dp.callback_query(F.data.startswith("menu_"))
async def menu_category_handler(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    products = get_products_by_category(category)
    
    category_name = "البسبوسة 🧁" if category == "basboosa" else "المشروبات ☕"
    
    if products:
        text = f"📋 قائمة {category_name}\n\nاختر المنتج الذي تريده:"
        await callback.message.edit_text(text, reply_markup=products_keyboard(products))
    else:
        await callback.message.edit_text(
            f"😔 عذراً، لا توجد منتجات متاحة في قسم {category_name}",
            reply_markup=main_menu_keyboard()
        )

@dp.callback_query(F.data.startswith("product_"))
async def product_handler(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = get_product_by_id(product_id)
    
    if not product:
        await callback.answer("❌ المنتج غير موجود", show_alert=True)
        return
    
    text = f"🧁 {product['name']}\n\nاختر الحجم:"
    await callback.message.edit_text(text, reply_markup=size_keyboard(product))

@dp.callback_query(F.data.startswith("size_"))
async def size_handler(callback: types.CallbackQuery):
    _, size, product_id = callback.data.split("_")
    product_id = int(product_id)
    product = get_product_by_id(product_id)
    
    price = getattr(product, f'price_{size.lower()}')
    
    text = f"🧁 {product['name']}\n📏 الحجم: {size}\n💰 السعر: {price} ر.س\n\nكم الكمية المطلوبة؟"
    await callback.message.edit_text(text, reply_markup=quantity_keyboard(product_id, size))

@dp.callback_query(F.data.startswith("qty_"))
async def quantity_handler(callback: types.CallbackQuery, state: FSMContext):
    _, quantity, product_id, size = callback.data.split("_")
    quantity = int(quantity)
    product_id = int(product_id)
    
    product = get_product_by_id(product_id)
    price = getattr(product, f'price_{size.lower()}')
    total_price = price * quantity
    
    # إضافة للسلة
    data = await state.get_data()
    cart = data.get('cart', [])
    
    cart.append({
        'product_id': product_id,
        'name': product['name'],
        'size': size,
        'quantity': quantity,
        'unit_price': price,
        'total_price': total_price
    })
    
    await state.update_data(cart=cart)
    
    text = f"✅ تم إضافة المنتج للسلة!\n\n🧁 {product['name']}\n📏 {size}\n🔢 الكمية: {quantity}\n💰 المجموع: {total_price} ر.س"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 عرض السلة", callback_data="view_cart")
    builder.button(text="➕ إضافة المزيد", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "view_cart")
async def view_cart_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = data.get('cart', [])
    
    if not cart:
        await callback.message.edit_text(
            "🛒 سلة المشتريات فارغة\n\nأضف بعض المنتجات الشهية!",
            reply_markup=main_menu_keyboard()
        )
        return
    
    text = "🛒 سلة المشتريات:\n\n"
    total = 0
    
    for i, item in enumerate(cart, 1):
        text += f"{i}. {item['name']} ({item['size']})\n"
        text += f"   الكمية: {item['quantity']} × {item['unit_price']} = {item['total_price']} ر.س\n\n"
        total += item['total_price']
    
    text += f"💰 المجموع الكلي: {total} ر.س"
    
    await callback.message.edit_text(text, reply_markup=cart_keyboard())

@dp.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(cart=[])
    await callback.message.edit_text(
        "🗑️ تم إفراغ سلة المشتريات",
        reply_markup=main_menu_keyboard()
    )

@dp.callback_query(F.data == "confirm_order")
async def confirm_order_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📞 معلومات التواصل\n\nالرجاء إدخال اسمك ورقم جوالك:\n\nمثال: أحمد محمد - 0501234567"
    )
    await state.set_state(OrderStates.entering_contact)

@dp.message(OrderStates.entering_contact)
async def handle_contact_info(message: types.Message, state: FSMContext):
    contact_info = message.text.strip()
    
    if " - " not in contact_info:
        await message.answer("❌ الرجاء إدخال البيانات بالشكل الصحيح:\nالاسم - رقم الجوال\n\nمثال: أحمد محمد - 0501234567")
        return
    
    try:
        name, phone = contact_info.split(" - ", 1)
        await state.update_data(customer_name=name.strip(), customer_phone=phone.strip())
        
        await message.answer(
            "📍 تحديد الموقع\n\nالرجاء تحديد موقعك للتوصيل:",
            reply_markup=location_keyboard()
        )
        await state.set_state(OrderStates.entering_location)
        
    except ValueError:
        await message.answer("❌ خطأ في التنسيق. الرجاء المحاولة مرة أخرى.")

@dp.message(OrderStates.entering_location, F.location)
async def handle_location(message: types.Message, state: FSMContext):
    location_data = {
        'lat': message.location.latitude,
        'lon': message.location.longitude,
        'address': f"📍 الموقع: {message.location.latitude}, {message.location.longitude}"
    }
    
    await state.update_data(location=location_data)
    await finalize_order(message, state)

@dp.message(OrderStates.entering_location, F.text == "💬 كتابة العنوان يدوياً")
async def manual_address_prompt(message: types.Message, state: FSMContext):
    await message.answer("📝 اكتب عنوانك التفصيلي:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(OrderStates.entering_location, F.text)
async def handle_manual_address(message: types.Message, state: FSMContext):
    if message.text == "💬 كتابة العنوان يدوياً":
        return
    
    location_data = {
        'address': message.text,
        'lat': None,
        'lon': None
    }
    
    await state.update_data(location=location_data)
    await finalize_order(message, state)

async def finalize_order(message, state: FSMContext):
    data = await state.get_data()
    cart = data['cart']
    customer_name = data['customer_name']
    customer_phone = data['customer_phone']
    location = data['location']
    
    total = sum(item['total_price'] for item in cart)
    
    # إنشاء الطلب في قاعدة البيانات
    order_id = create_order(
        message.from_user.id,
        customer_name,
        customer_phone,
        total,
        cart,
        location
    )
    
    # رسالة للعميل
    order_text = f"✅ تم استلام طلبك بنجاح!\n\n🆔 رقم الطلب: #{order_id}\n\n"
    order_text += "📋 تفاصيل الطلب:\n"
    
    for item in cart:
        order_text += f"• {item['name']} ({item['size']}) × {item['quantity']} = {item['total_price']} ر.س\n"
    
    order_text += f"\n💰 المجموع: {total} ر.س\n"
    order_text += f"👤 الاسم: {customer_name}\n"
    order_text += f"📞 الجوال: {customer_phone}\n"
    order_text += f"📍 العنوان: {location['address']}\n\n"
    order_text += "⏰ سيتم التواصل معك قريباً لتأكيد التوصيل"
    
    await message.answer(order_text, reply_markup=types.ReplyKeyboardRemove())
    
    # إشعار المحل (يرسل لقناة خاصة أو مجموعة)
    shop_notification = f"🔔 طلب جديد #{order_id}\n\n"
    shop_notification += f"👤 {customer_name}\n📞 {customer_phone}\n\n"
    shop_notification += "📋 الطلب:\n"
    
    for item in cart:
        shop_notification += f"• {item['name']} ({item['size']}) × {item['quantity']}\n"
    
    shop_notification += f"\n💰 المجموع: {total} ر.س\n"
    shop_notification += f"📍 {location['address']}\n\n"
    
    if location['lat'] and location['lon']:
        shop_notification += f"🗺️ الموقع: https://maps.google.com/?q={location['lat']},{location['lon']}"
    
    # هنا يمكن إرسال الإشعار لمجموعة المحل أو قناة
    # await bot.send_message(SHOP_CHAT_ID, shop_notification)
    
    # مسح السلة
    await state.update_data(cart=[])
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📞 تواصل مع المحل", url=f"https://wa.me/{SHOP_WHATSAPP}")
    builder.button(text="🏪 طلب جديد", callback_data="main_menu")
    
    await message.answer(
        "شكراً لاختيارك محل فخامة بسبوستي 🌟",
        reply_markup=builder.as_markup()
    )
    await state.clear()

@dp.callback_query(F.data == "contact_us")
async def contact_handler(callback: types.CallbackQuery):
    contact_text = """
📞 تواصل معنا

🏪 محل فخامة بسبوستي
📍 تبوك - المملكة العربية السعودية

للاستفسارات والطلبات:
    """
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 واتساب", url=f"https://wa.me/{SHOP_WHATSAPP}")
    builder.button(text="🔙 القائمة الرئيسية", callback_data="main_menu")
    
    await callback.message.edit_text(contact_text, reply_markup=builder.as_markup())

# ================== تشغيل البوت ==================
if __name__ == "__main__":
    print("🚀 بدء تشغيل بوت فخامة بسبوستي...")
    try:
        init_db()
        insert_menu_data()
        print("✅ تم إعداد قاعدة البيانات والمنيو")
        asyncio.run(dp.start_polling(bot))
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")