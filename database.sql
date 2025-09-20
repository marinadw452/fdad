-- سكريبت إعداد قاعدة بيانات بوت فخامة بسبوستي
-- database_setup.sql

-- حذف الجداول الموجودة (إذا كانت موجودة)
DROP TABLE IF EXISTS orders CASCADE;

-- جدول الطلبات
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    customer_name TEXT,
    customer_phone TEXT,
    items JSONB NOT NULL,
    total_amount INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (
        status IN ('pending', 'preparing', 'ready', 'delivering', 'completed', 'cancelled')
    ),
    location_lat FLOAT,
    location_lon FLOAT,
    location_address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- فهارس للأداء
CREATE INDEX idx_orders_status ON orders (status, created_at);
CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_date ON orders (created_at DESC);

-- دالة تحديث updated_at تلقائياً
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- محفز لتحديث updated_at
CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- جدول المنتجات (اختياري - للمستقبل)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price_small INTEGER,
    price_medium INTEGER, 
    price_large INTEGER,
    is_available BOOLEAN DEFAULT true,
    description TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- إدراج بيانات المنتجات الأساسية
INSERT INTO products (name, category, price_small, price_medium, price_large) VALUES
-- البسبوسة
('عادية', 'basboosa', 12, 24, NULL),
('نوتيلا', 'basboosa', 12, 24, NULL),
('شوكولاتة السعودية', 'basboosa', 12, 24, NULL),
('جبنة', 'basboosa', 12, 24, NULL),
('كندر', 'basboosa', 12, 24, NULL),
('نكهت السعادة', 'basboosa', 12, 24, NULL),
('راويو', 'basboosa', 18, 36, NULL),
('كتكات', 'basboosa', 18, 36, NULL),
('لوتس', 'basboosa', 12, 24, NULL),
('سنيكرز', 'basboosa', 12, 24, NULL),
('جلاكسي', 'basboosa', 12, 24, NULL),
('سنابون', 'basboosa', 12, 24, NULL),

-- المشروبات والإضافات
('قهوة سعودية دلة', 'drinks', 35, NULL, NULL),
('كوب قهوة سعودي', 'drinks', 5, NULL, NULL),
('صحن توزيعات', 'drinks', 49, NULL, NULL),
('كيكة الدخن', 'drinks', 23, NULL, NULL);

-- فهرس على اسم المنتج
CREATE INDEX idx_products_name ON products (name);
CREATE INDEX idx_products_category ON products (category, is_available);

-- عرض إحصائيات
SELECT 'تم إنشاء قاعدة البيانات بنجاح!' as message;
SELECT 'عدد المنتجات المُدرجة: ' || COUNT(*) as products_count FROM products;

-- منح صلاحيات للمستخدم (تأكد من تغيير اسم المستخدم)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bot_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bot_user;
