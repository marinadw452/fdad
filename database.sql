-- حذف الجداول الموجودة
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- جدول المنتجات
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    price_s INTEGER,
    price_m INTEGER,
    price_l INTEGER,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول الطلبات
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    customer_name TEXT,
    customer_phone TEXT,
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

-- جدول تفاصيل الطلبات
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    size VARCHAR(2) CHECK (size IN ('S', 'M', 'L')),
    unit_price INTEGER NOT NULL,
    total_price INTEGER NOT NULL
);

-- فهارس للأداء
CREATE INDEX idx_orders_status ON orders (status, created_at);
CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_products_category ON products (category, available);

-- دالة تحديث updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- تطبيق المحفز
CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- إدراج بيانات المنيو
INSERT INTO products (name, category, price_s, price_m, price_l) VALUES
-- البسبوسة
('بسبوسة مشكل', 'basboosa', 18, 36, NULL),
('بسبوسة سادة', 'basboosa', 12, 24, NULL),
('بسبوسة قشطة', 'basboosa', 18, 36, NULL),
('بسبوسة توفي', 'basboosa', 18, 36, NULL),
('بسبوسة نوتيلا', 'basboosa', 18, 36, NULL),
('فلفل رد', 'basboosa', 12, 24, NULL),
('كرنشي الجبنة', 'basboosa', 12, 24, NULL),
('النكهة السعودية', 'basboosa', 12, 24, NULL),
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