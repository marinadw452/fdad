# بيانات منيو محل فخامة بسبوستي

MENU_ITEMS = [
    # البسبوسة
    {
        'name': 'بسبوسة مشكل',
        'category': 'basboosa',
        'price_s': 18,
        'price_m': 36,
        'price_l': None
    },
    {
        'name': 'بسبوسة سادة',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'بسبوسة قشطة',
        'category': 'basboosa',
        'price_s': 18,
        'price_m': 36,
        'price_l': None
    },
    {
        'name': 'بسبوسة توفي',
        'category': 'basboosa',
        'price_s': 18,
        'price_m': 36,
        'price_l': None
    },
    {
        'name': 'بسبوسة نوتيلا',
        'category': 'basboosa',
        'price_s': 18,
        'price_m': 36,
        'price_l': None
    },
    {
        'name': 'فلفل رد',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'كرنشي الجبنة',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'النكهة السعودية',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'جبنة',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'كندر',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'نكهت السعادة',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'راويو',
        'category': 'basboosa',
        'price_s': 18,
        'price_m': 36,
        'price_l': None
    },
    {
        'name': 'كتكات',
        'category': 'basboosa',
        'price_s': 18,
        'price_m': 36,
        'price_l': None
    },
    {
        'name': 'لوتس',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'سنيكرز',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'جلاكسي',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    {
        'name': 'سنابون',
        'category': 'basboosa',
        'price_s': 12,
        'price_m': 24,
        'price_l': None
    },
    
    # المشروبات والإضافات
    {
        'name': 'قهوة سعودية دلة',
        'category': 'drinks',
        'price_s': 35,
        'price_m': None,
        'price_l': None
    },
    {
        'name': 'كوب قهوة سعودي',
        'category': 'drinks',
        'price_s': 5,
        'price_m': None,
        'price_l': None
    },
    {
        'name': 'صحن توزيعات',
        'category': 'drinks',
        'price_s': 49,
        'price_m': None,
        'price_l': None
    },
    {
        'name': 'كيكة الدخن',
        'category': 'drinks',
        'price_s': 23,
        'price_m': None,
        'price_l': None
    }
]

def get_menu_by_category(category):
    """جلب المنتجات حسب التصنيف"""
    return [item for item in MENU_ITEMS if item['category'] == category]

def get_product_by_name(name):
    """جلب المنتج بالاسم"""
    for item in MENU_ITEMS:
        if item['name'] == name:
            return item
    return None
