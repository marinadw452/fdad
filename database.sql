-- حذف الجداول الموجودة
DROP TABLE IF EXISTS orders CASCADE;

-- جدول الطلبات المبسط
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

-- دالة تحديث updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$ language 'plpgsql';

-- تطبيق المحفز
CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();هة السعودية', 'basboosa', 12, 24, NULL),
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
