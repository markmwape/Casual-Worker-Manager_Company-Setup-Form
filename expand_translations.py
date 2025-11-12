"""
Expand translation files with landing page content
This script adds the missing landing page strings to all translation files
"""

import json
import os

# Landing page strings that need to be translated
LANDING_PAGE_STRINGS = {
    "75% Time Savings for Firms": {
        "en": "75% Time Savings for Firms",
        "fr": "75% D'économies de temps pour les cabinets",
        "sw": "75% Akiba ya wakati kwa Makampuni",
        "pt": "75% Economia de tempo para empresas",
        "es": "75% Ahorros de tiempo para firmas",
        "tr": "Firmalar için %75 Zaman Tasarrufu",
        "hi": "फर्मों के लिए 75% समय बचत",
        "zh": "为公司节省75%的时间",
        "ar": "توفير 75% من الوقت للشركات",
        "vi": "Tiết kiệm 75% thời gian cho các công ty"
    },
    "Professional Workforce Management": {
        "en": "Professional Workforce Management",
        "fr": "Gestion professionnelle de la main-d'œuvre",
        "sw": "Usimamizi wa kazi wa kitaalamu",
        "pt": "Gerenciamento profissional da força de trabalho",
        "es": "Gestión profesional de la fuerza laboral",
        "tr": "Profesyonel İş Gücü Yönetimi",
        "hi": "पेशेवर कार्यबल प्रबंधन",
        "zh": "专业劳动力管理",
        "ar": "إدارة القوى العاملة المتخصصة",
        "vi": "Quản lý lực lượng lao động chuyên nghiệp"
    },
    "Transform your casual workforce operations with smart attendance tracking, automated payroll, and powerful analytics that save time and reduce costs.": {
        "en": "Transform your casual workforce operations with smart attendance tracking, automated payroll, and powerful analytics that save time and reduce costs.",
        "fr": "Transformez vos opérations de main-d'œuvre temporaire grâce au suivi intelligent des présences, à la paie automatisée et à des analyses puissantes qui économisent du temps et réduisent les coûts.",
        "sw": "Badilisha shughuli zako za kazi za aji na njia mahususi ya kufuatilia mahضeri, malipo yanayojitoa, na uchambuzi wenye nguvu ambao husambaza wakati na kupunguza gharama.",
        "pt": "Transforme suas operações de força de trabalho casual com rastreamento inteligente de presença, folha de pagamento automatizada e análise poderosa que economizam tempo e reduzem custos.",
        "es": "Transforme sus operaciones de fuerza laboral ocasional con seguimiento inteligente de asistencia, nómina automatizada y análisis poderosos que ahorren tiempo y reduzcan costos.",
        "tr": "Akıllı katılım takibi, otomatik bordro ve maliyetleri azaltan güçlü analitiği ile geçici işgücü operasyonlarınızı dönüştürün.",
        "hi": "स्मार्ट उपस्थिति ट्रैकिंग, स्वचालित पेरोल, और शक्तिशाली विश्लेषण के साथ अपने आकस्मिक कार्यबल संचालन को रूपांतरित करें जो समय बचाते हैं और लागत कम करते हैं।",
        "zh": "通过智能考勤跟踪、自动工资单和强大的分析来改变您的临时劳动力运营，节省时间并降低成本。",
        "ar": "حول عمليات القوى العاملة العارضة لديك من خلال تتبع الحضور الذكي والرواتب الآلية والتحليلات القوية التي توفر الوقت وتقلل التكاليف.",
        "vi": "Chuyển đổi các hoạt động lực lượng lao động tạm thời của bạn bằng theo dõi dự án thông minh, bảng lương tự động và phân tích mạnh mẽ giúp tiết kiệm thời gian và giảm chi phí."
    },
    "Everything You Need to Manage Your Workforce": {
        "en": "Everything You Need to Manage Your Workforce",
        "fr": "Tout ce dont vous avez besoin pour gérer votre main-d'œuvre",
        "sw": "Kila kitu unachohitaji kusimamia kazi yako",
        "pt": "Tudo o que você precisa para gerenciar sua força de trabalho",
        "es": "Todo lo que necesita para administrar su fuerza laboral",
        "tr": "İş Gücünüzü Yönetmek İçin Gerekli Olan Her Şey",
        "hi": "आपके कार्यबल को प्रबंधित करने के लिए आपको सब कुछ चाहिए",
        "zh": "管理您的工作队伍所需的一切",
        "ar": "كل ما تحتاجه لإدارة قوتك العاملة",
        "vi": "Mọi thứ bạn cần để quản lý lực lượng lao động của mình"
    },
    "From attendance tracking to payroll processing, we've got you covered with enterprise-grade features.": {
        "en": "From attendance tracking to payroll processing, we've got you covered with enterprise-grade features.",
        "fr": "Du suivi des présences au traitement des salaires, nous vous couvrons avec des fonctionnalités de niveau entreprise.",
        "sw": "Kutoka kufuatilia mahضeri hadi usindikaji wa malipo, tunakusambaza na sifa za kiwango cha kuajiriwa.",
        "pt": "Do rastreamento de presença ao processamento da folha de pagamento, cobrimos você com recursos de nível corporativo.",
        "es": "Desde el seguimiento de asistencia hasta el procesamiento de nómina, lo cubrimos con funciones de nivel empresarial.",
        "tr": "Katılım takibinden bordro işlemeye kadar, sizi kurumsal düzeyde özelliklerle kapsıyoruz.",
        "hi": "उपस्थिति ट्रैकिंग से पेरोल प्रोसेसिंग तक, हम आपको एंटरप्राइज-ग्रेड सुविधाओं के साथ कवर करते हैं।",
        "zh": "从考勤跟踪到工资单处理，我们为您提供企业级功能。",
        "ar": "من تتبع الحضور إلى معالجة الرواتب، نغطيك بميزات على مستوى المؤسسات.",
        "vi": "Từ theo dõi dự án đến xử lý bảng lương, chúng tôi bao phủ bạn bằng các tính năng cấp độ doanh nghiệp."
    },
    "Attendance Tracking": {
        "en": "Attendance Tracking",
        "fr": "Suivi des présences",
        "sw": "Kufuatilia mahضeri",
        "pt": "Rastreamento de presença",
        "es": "Seguimiento de asistencia",
        "tr": "Katılım Takibi",
        "hi": "उपस्थिति ट्रैकिंग",
        "zh": "考勤跟踪",
        "ar": "تتبع الحضور",
        "vi": "Theo dõi dự án"
    },
    "Smart, real-time attendance tracking with facial recognition and QR code support for seamless worker management.": {
        "en": "Smart, real-time attendance tracking with facial recognition and QR code support for seamless worker management.",
        "fr": "Suivi intelligent et en temps réel des présences avec reconnaissance faciale et support des codes QR pour une gestion transparente des travailleurs.",
        "sw": "Kufuatilia mahضeri kwa akili, saa halisi na ujumbe wa uso na msaada wa QR kwa usimamizi mzuri wa wafanyikazi.",
        "pt": "Rastreamento inteligente e em tempo real de presença com reconhecimento facial e suporte a código QR para gerenciamento contínuo de trabalhadores.",
        "es": "Seguimiento inteligente y en tiempo real de la asistencia con reconocimiento facial y soporte de código QR para una gestión fluida de trabajadores.",
        "tr": "Yüz tanıma ve QR kod desteği ile akıllı, gerçek zamanlı katılım takibi ve sorunsuz işçi yönetimi.",
        "hi": "चेहरे की पहचान और QR कोड समर्थन के साथ स्मार्ट, वास्तविक समय की उपस्थिति ट्रैकिंग सहज कार्यकर्ता प्रबंधन के लिए।",
        "zh": "具有面部识别和二维码支持的智能实时考勤跟踪，实现无缝的工人管理。",
        "ar": "تتبع حضور ذكي وفي الوقت الفعلي مع التعرف على الوجه ودعم رمز الاستجابة السريعة لإدارة سلسة للعمال.",
        "vi": "Theo dõi dự án thông minh theo thời gian thực với nhận dạng khuôn mặt và hỗ trợ mã QR để quản lý công nhân liền mạch."
    },
    "Payroll Management": {
        "en": "Payroll Management",
        "fr": "Gestion de la paie",
        "sw": "Usimamizi wa malipo",
        "pt": "Gestão de folha de pagamento",
        "es": "Gestión de nómina",
        "tr": "Bordro Yönetimi",
        "hi": "पेरोल प्रबंधन",
        "zh": "工资单管理",
        "ar": "إدارة الرواتب",
        "vi": "Quản lý bảng lương"
    },
    "Automated payroll calculations, tax compliance, and multi-currency support for global workforce management.": {
        "en": "Automated payroll calculations, tax compliance, and multi-currency support for global workforce management.",
        "fr": "Calculs de paie automatisés, conformité fiscale et support multi-devises pour la gestion mondiale de la main-d'œuvre.",
        "sw": "Mahesabu ya malipo yanayojitoa, upatanishi wa kodi na msaada wa vipengele vingi kwa usimamizi wa kazi wa kimataifa.",
        "pt": "Cálculos de folha de pagamento automatizados, conformidade fiscal e suporte multifuncional para gerenciamento global de força de trabalho.",
        "es": "Cálculos de nómina automatizados, cumplimiento fiscal y soporte multimoneda para la gestión global de la fuerza laboral.",
        "tr": "Otomatik bordro hesaplamaları, vergi uyumluluğu ve küresel işgücü yönetimi için çok para birimi desteği.",
        "hi": "स्वचालित पेरोल गणना, कर अनुपालन, और वैश्विक कार्यबल प्रबंधन के लिए बहु-मुद्रा समर्थन।",
        "zh": "自动工资单计算、税收合规和多币种支持，用于全球劳动力管理。",
        "ar": "حسابات الرواتب الآلية والامتثال الضريبي ودعم العملات المتعددة لإدارة القوى العاملة العالمية.",
        "vi": "Tính toán bảng lương tự động, tuân thủ thuế và hỗ trợ đa tiền tệ để quản lý lực lượng lao động toàn cầu."
    },
    "Analytics & Reports": {
        "en": "Analytics & Reports",
        "fr": "Analyse et rapports",
        "sw": "Uchambuzi na ripoti",
        "pt": "Análise e relatórios",
        "es": "Análisis e informes",
        "tr": "Analitik ve Raporlar",
        "hi": "विश्लेषण और रिपोर्ट",
        "zh": "分析和报告",
        "ar": "التحليلات والتقارير",
        "vi": "Phân tích và báo cáo"
    },
    "Comprehensive dashboards and custom reports to gain insights into your workforce productivity and costs.": {
        "en": "Comprehensive dashboards and custom reports to gain insights into your workforce productivity and costs.",
        "fr": "Tableaux de bord complets et rapports personnalisés pour obtenir des informations sur la productivité et les coûts de votre main-d'œuvre.",
        "sw": "Dashibodi kamili na ripoti za kawaida kupata hoja ya uzalishaji na gharama za kazi yako.",
        "pt": "Painéis abrangentes e relatórios personalizados para obter informações sobre produtividade e custos da força de trabalho.",
        "es": "Paneles completos e informes personalizados para obtener información sobre la productividad y los costos de su fuerza laboral.",
        "tr": "İş gücü üretkenliği ve maliyetleri hakkında bilgi edinmek için kapsamlı panolar ve özel raporlar.",
        "hi": "आपके कार्यबल उत्पादकता और लागत में अंतर्दृष्टि प्राप्त करने के लिए व्यापक डैशबोर्ड और कस्टम रिपोर्ट।",
        "zh": "综合仪表板和自定义报告，以深入了解您的劳动力生产率和成本。",
        "ar": "لوحات معلومات شاملة وتقارير مخصصة للحصول على رؤى حول إنتاجية وتكاليف قوتك العاملة.",
        "vi": "Bảng điều khiển toàn diện và báo cáo tùy chỉnh để hiểu sâu về năng suất và chi phí lực lượng lao động của bạn."
    },
    "Bank-Level Security": {
        "en": "Bank-Level Security",
        "fr": "Sécurité de niveau bancaire",
        "sw": "Usalama wa kiwango cha benki",
        "pt": "Segurança de nível bancário",
        "es": "Seguridad de nivel bancario",
        "tr": "Banka Seviyesi Güvenlik",
        "hi": "बैंक-स्तरीय सुरक्षा",
        "zh": "银行级安全",
        "ar": "أمان على مستوى البنك",
        "vi": "Bảo mật cấp ngân hàng"
    },
    "99.9% Uptime": {
        "en": "99.9% Uptime",
        "fr": "99,9% de disponibilité",
        "sw": "99.9% Uptime",
        "pt": "99,9% de tempo de atividade",
        "es": "99,9% de tiempo de actividad",
        "tr": "%99,9 Çalışma Süresi",
        "hi": "99.9% अपटाइम",
        "zh": "99.9%正常运行时间",
        "ar": "99.9% وقت التشغيل",
        "vi": "99.9% thời gian hoạt động"
    },
    "24/7 Support": {
        "en": "24/7 Support",
        "fr": "Support 24h/24 et 7j/7",
        "sw": "Msaada 24/7",
        "pt": "Suporte 24/7",
        "es": "Soporte 24/7",
        "tr": "24/7 Destek",
        "hi": "24/7 सहायता",
        "zh": "24/7支持",
        "ar": "دعم 24/7",
        "vi": "Hỗ trợ 24/7"
    },
    "GDPR Compliant": {
        "en": "GDPR Compliant",
        "fr": "Conforme au RGPD",
        "sw": "GDPR Compliant",
        "pt": "Compatível com GDPR",
        "es": "Cumple con GDPR",
        "tr": "GDPR Uyumlu",
        "hi": "GDPR अनुपालन",
        "zh": "符合GDPR",
        "ar": "متوافق مع GDPR",
        "vi": "Tuân thủ GDPR"
    },
    "No Credit Card Required": {
        "en": "No Credit Card Required",
        "fr": "Aucune carte de crédit requise",
        "sw": "Hakuna kadi ya mkopo inayohitajika",
        "pt": "Nenhum cartão de crédito necessário",
        "es": "No se requiere tarjeta de crédito",
        "tr": "Kredi Kartı Gerekli Değil",
        "hi": "क्रेडिट कार्ड की आवश्यकता नहीं",
        "zh": "无需信用卡",
        "ar": "لا يلزم بطاقة ائتمان",
        "vi": "Không cần thẻ tín dụng"
    },
    "30-Day Free Trial": {
        "en": "30-Day Free Trial",
        "fr": "Essai gratuit de 30 jours",
        "sw": "Uzoefu wa bure wa siku 30",
        "pt": "Avaliação gratuita de 30 dias",
        "es": "Prueba gratuita de 30 días",
        "tr": "30 Günlük Ücretsiz Deneme",
        "hi": "30 दिन की निःशुल्क परीक्षा",
        "zh": "30天免费试用",
        "ar": "تجربة مجانية لمدة 30 يوم",
        "vi": "Bản dùng thử miễn phí 30 ngày"
    },
    "Features": {
        "en": "Features",
        "fr": "Caractéristiques",
        "sw": "Sifa",
        "pt": "Características",
        "es": "Características",
        "tr": "Özellikler",
        "hi": "विशेषताएं",
        "zh": "特征",
        "ar": "الميزات",
        "vi": "Các tính năng"
    },
    "Pricing": {
        "en": "Pricing",
        "fr": "Tarification",
        "sw": "Bei",
        "pt": "Preços",
        "es": "Precios",
        "tr": "Fiyatlandırma",
        "hi": "मूल्य निर्धारण",
        "zh": "定价",
        "ar": "التسعير",
        "vi": "Giá cả"
    },
    "Testimonials": {
        "en": "Testimonials",
        "fr": "Témoignages",
        "sw": "Ushahidi",
        "pt": "Depoimentos",
        "es": "Testimonios",
        "tr": "Testimoniler",
        "hi": "प्रशंसापत्र",
        "zh": "推荐",
        "ar": "الشهادات",
        "vi": "Chứng thực"
    },
    "Login / Sign Up": {
        "en": "Login / Sign Up",
        "fr": "Connexion / S'inscrire",
        "sw": "Ingia / Jandikishe",
        "pt": "Entrar / Inscrever-se",
        "es": "Iniciar sesión / Registrarse",
        "tr": "Giriş Yap / Kayıt Ol",
        "hi": "लॉगिन / साइन अप करें",
        "zh": "登录/注册",
        "ar": "تسجيل الدخول / التسجيل",
        "vi": "Đăng nhập / Đăng ký"
    },
    "Watch Demo": {
        "en": "Watch Demo",
        "fr": "Regarder la démo",
        "sw": "Angalia Demo",
        "pt": "Assistir demonstração",
        "es": "Ver demostración",
        "tr": "Demo'yu İzle",
        "hi": "डेमो देखें",
        "zh": "观看演示",
        "ar": "مشاهدة العرض التوضيحي",
        "vi": "Xem bản demo"
    }
}

def expand_translations():
    """Expand all translation files with landing page strings"""
    translations_dir = "static/translations"
    
    # Get all language codes
    languages = ['en', 'fr', 'sw', 'pt', 'es', 'tr', 'hi', 'zh', 'ar', 'vi']
    
    for lang in languages:
        file_path = os.path.join(translations_dir, f"{lang}.json")
        
        # Load existing translations
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        else:
            existing = {}
        
        # Add new translations
        for key, translations in LANDING_PAGE_STRINGS.items():
            if key not in existing:
                existing[key] = translations.get(lang, translations.get('en', key))
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2, sort_keys=True)
        
        print(f"✅ Updated {lang}.json with {len(LANDING_PAGE_STRINGS)} landing page strings")

if __name__ == '__main__':
    expand_translations()
    print("✅ All translation files expanded!")
