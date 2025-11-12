"""
Complete Landing Page Translation Expansion
Adds ALL user-facing text from landing page to translation files
"""

import json
import os

# Complete landing page translations
LANDING_TRANSLATIONS = {
    # Already added (keeping for completeness)
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
        "sw": "Usimamizi wa Wafanyikazi wa Kitaaluma",
        "pt": "Gerenciamento Profissional da Força de Trabalho",
        "es": "Gestión Profesional de la Fuerza Laboral",
        "tr": "Profesyonel İş Gücü Yönetimi",
        "hi": "पेशेवर कार्यबल प्रबंधन",
        "zh": "专业劳动力管理",
        "ar": "إدارة القوى العاملة المهنية",
        "vi": "Quản lý Lực lượng Lao động Chuyên nghiệp"
    },
    "Transform your casual workforce operations with smart attendance tracking, automated payroll, and powerful analytics that save time and reduce costs.": {
        "en": "Transform your casual workforce operations with smart attendance tracking, automated payroll, and powerful analytics that save time and reduce costs.",
        "fr": "Transformez vos opérations de main-d'œuvre temporaire avec un suivi intelligent des présences, une paie automatisée et des analyses puissantes qui économisent du temps et réduisent les coûts.",
        "sw": "Badilisha shughuli zako za wafanyikazi wa muda kwa ufuatiliaji mahiri wa mahضeri, malipo ya kiotomatiki, na uchambuzi wenye nguvu unaookoa muda na kupunguza gharama.",
        "pt": "Transforme suas operações de força de trabalho casual com rastreamento inteligente de presença, folha de pagamento automatizada e análises poderosas que economizam tempo e reduzem custos.",
        "es": "Transforme sus operaciones de fuerza laboral casual con seguimiento inteligente de asistencia, nómina automatizada y análisis potentes que ahorran tiempo y reducen costos.",
        "tr": "Akıllı devam takibi, otomatik bordro ve maliyetleri azaltan güçlü analizlerle geçici işgücü operasyonlarınızı dönüştürün.",
        "hi": "स्मार्ट उपस्थिति ट्रैकिंग, स्वचालित पेरोल और शक्तिशाली विश्लेषण के साथ अपने आकस्मिक कार्यबल संचालन को बदलें जो समय बचाते हैं और लागत कम करते हैं।",
        "zh": "通过智能考勤跟踪、自动工资单和强大的分析来改变您的临时劳动力运营，节省时间并降低成本。",
        "ar": "حوّل عمليات القوى العاملة العرضية مع تتبع الحضور الذكي والرواتب الآلية والتحليلات القوية التي توفر الوقت وتقلل التكاليف.",
        "vi": "Chuyển đổi hoạt động lực lượng lao động thời vụ của bạn với theo dõi chuyên cần thông minh, bảng lương tự động và phân tích mạnh mẽ giúp tiết kiệm thời gian và giảm chi phí."
    },
    
    # Feature Cards
    "Worker Management": {
        "en": "Worker Management",
        "fr": "Gestion des Travailleurs",
        "sw": "Usimamizi wa Wafanyikazi",
        "pt": "Gestão de Trabalhadores",
        "es": "Gestión de Trabajadores",
        "tr": "İşçi Yönetimi",
        "hi": "कार्यकर्ता प्रबंधन",
        "zh": "工人管理",
        "ar": "إدارة العمال",
        "vi": "Quản lý Công nhân"
    },
    "Organize and track your casual workforce with detailed worker profiles and employment records.": {
        "en": "Organize and track your casual workforce with detailed worker profiles and employment records.",
        "fr": "Organisez et suivez votre main-d'œuvre temporaire avec des profils détaillés des travailleurs et des dossiers d'emploi.",
        "sw": "Panga na fuatilia wafanyikazi wako wa muda kwa wasifu wa kina wa wafanyikazi na rekodi za ajira.",
        "pt": "Organize e acompanhe sua força de trabalho casual com perfis detalhados de trabalhadores e registros de emprego.",
        "es": "Organice y rastree su fuerza laboral casual con perfiles detallados de trabajadores y registros de empleo.",
        "tr": "Detaylı işçi profilleri ve istihdam kayıtları ile geçici işgücünüzü organize edin ve takip edin.",
        "hi": "विस्तृत कार्यकर्ता प्रोफाइल और रोजगार रिकॉर्ड के साथ अपने आकस्मिक कार्यबल को व्यवस्थित और ट्रैक करें।",
        "zh": "通过详细的工人档案和就业记录来组织和跟踪您的临时劳动力。",
        "ar": "نظم وتتبع قوتك العاملة العرضية مع ملفات تعريف العمال التفصيلية وسجلات التوظيف.",
        "vi": "Tổ chức và theo dõi lực lượng lao động thời vụ của bạn với hồ sơ công nhân chi tiết và hồ sơ tuyển dụng."
    },
    "Task Assignment": {
        "en": "Task Assignment",
        "fr": "Affectation des Tâches",
        "sw": "Ugawaji wa Kazi",
        "pt": "Atribuição de Tarefas",
        "es": "Asignación de Tareas",
        "tr": "Görev Ataması",
        "hi": "कार्य असाइनमेंट",
        "zh": "任务分配",
        "ar": "تعيين المهام",
        "vi": "Phân công Nhiệm vụ"
    },
    "Create, assign, and track tasks with deadlines, ensuring your workforce stays organized and productive.": {
        "en": "Create, assign, and track tasks with deadlines, ensuring your workforce stays organized and productive.",
        "fr": "Créez, attribuez et suivez les tâches avec des délais, en veillant à ce que votre main-d'œuvre reste organisée et productive.",
        "sw": "Unda, gawa, na fuatilia kazi zenye tarehe za mwisho, kuhakikisha wafanyikazi wako wanabaki wamepangwa na wazalishaji.",
        "pt": "Crie, atribua e acompanhe tarefas com prazos, garantindo que sua força de trabalho permaneça organizada e produtiva.",
        "es": "Cree, asigne y rastree tareas con plazos, asegurando que su fuerza laboral se mantenga organizada y productiva.",
        "tr": "Son tarihlerle görevler oluşturun, atayın ve takip edin, işgücünüzün organize ve üretken kalmasını sağlayın.",
        "hi": "समय सीमा के साथ कार्य बनाएं, असाइन करें और ट्रैक करें, यह सुनिश्चित करते हुए कि आपका कार्यबल संगठित और उत्पादक बना रहे।",
        "zh": "创建、分配和跟踪有截止日期的任务，确保您的劳动力保持有组织和高效。",
        "ar": "أنشئ وعيّن وتتبع المهام مع المواعيد النهائية، مما يضمن بقاء قوتك العاملة منظمة ومنتجة.",
        "vi": "Tạo, phân công và theo dõi nhiệm vụ với thời hạn, đảm bảo lực lượng lao động của bạn luôn có tổ chức và năng suất."
    },
    "Monitor attendance and work hours for accurate payroll and performance management.": {
        "en": "Monitor attendance and work hours for accurate payroll and performance management.",
        "fr": "Surveillez la présence et les heures de travail pour une gestion précise de la paie et des performances.",
        "sw": "Fuatilia mahضeri na masaa ya kazi kwa usimamizi sahihi wa malipo na utendaji.",
        "pt": "Monitore a presença e as horas de trabalho para uma gestão precisa da folha de pagamento e desempenho.",
        "es": "Supervise la asistencia y las horas de trabajo para una gestión precisa de nómina y rendimiento.",
        "tr": "Doğru bordro ve performans yönetimi için devam ve çalışma saatlerini izleyin.",
        "hi": "सटीक पेरोल और प्रदर्शन प्रबंधन के लिए उपस्थिति और कार्य घंटों की निगरानी करें।",
        "zh": "监控考勤和工作时间，以实现准确的工资单和绩效管理。",
        "ar": "راقب الحضور وساعات العمل لإدارة دقيقة للرواتب والأداء.",
        "vi": "Giám sát chuyên cần và giờ làm việc để quản lý bảng lương và hiệu suất chính xác."
    },
    "Comprehensive Reports": {
        "en": "Comprehensive Reports",
        "fr": "Rapports Complets",
        "sw": "Ripoti Kamili",
        "pt": "Relatórios Abrangentes",
        "es": "Informes Completos",
        "tr": "Kapsamlı Raporlar",
        "hi": "व्यापक रिपोर्ट",
        "zh": "综合报告",
        "ar": "تقارير شاملة",
        "vi": "Báo cáo Toàn diện"
    },
    "Generate detailed workforce reports for clients, including attendance, task completion, and performance metrics.": {
        "en": "Generate detailed workforce reports for clients, including attendance, task completion, and performance metrics.",
        "fr": "Générez des rapports détaillés sur la main-d'œuvre pour les clients, y compris la présence, l'achèvement des tâches et les mesures de performance.",
        "sw": "Zalisha ripoti za kina za wafanyikazi kwa wateja, ikijumuisha mahضeri, ukamilishaji wa kazi, na vipimo vya utendaji.",
        "pt": "Gere relatórios detalhados da força de trabalho para clientes, incluindo presença, conclusão de tarefas e métricas de desempenho.",
        "es": "Genere informes detallados de la fuerza laboral para clientes, incluida la asistencia, finalización de tareas y métricas de rendimiento.",
        "tr": "Müşteriler için devam, görev tamamlama ve performans ölçümleri dahil olmak üzere detaylı işgücü raporları oluşturun.",
        "hi": "ग्राहकों के लिए विस्तृत कार्यबल रिपोर्ट तैयार करें, जिसमें उपस्थिति, कार्य पूर्णता और प्रदर्शन मेट्रिक्स शामिल हैं।",
        "zh": "为客户生成详细的劳动力报告，包括考勤、任务完成和绩效指标。",
        "ar": "أنشئ تقارير مفصلة عن القوى العاملة للعملاء، بما في ذلك الحضور وإنجاز المهام ومقاييس الأداء.",
        "vi": "Tạo báo cáo lực lượng lao động chi tiết cho khách hàng, bao gồm chuyên cần, hoàn thành nhiệm vụ và chỉ số hiệu suất."
    },
    "Multi-Company": {
        "en": "Multi-Company",
        "fr": "Multi-Entreprise",
        "sw": "Kampuni Nyingi",
        "pt": "Multi-Empresa",
        "es": "Multi-Empresa",
        "tr": "Çoklu Şirket",
        "hi": "बहु-कंपनी",
        "zh": "多公司",
        "ar": "متعدد الشركات",
        "vi": "Đa Công ty"
    },
    "Manage multiple companies with separate workspaces and role-based access.": {
        "en": "Manage multiple companies with separate workspaces and role-based access.",
        "fr": "Gérez plusieurs entreprises avec des espaces de travail séparés et un accès basé sur les rôles.",
        "sw": "Simamia makampuni mengi na nafasi za kazi tofauti na ufikiaji kulingana na majukumu.",
        "pt": "Gerencie várias empresas com espaços de trabalho separados e acesso baseado em funções.",
        "es": "Administre múltiples empresas con espacios de trabajo separados y acceso basado en roles.",
        "tr": "Ayrı çalışma alanları ve rol tabanlı erişim ile birden fazla şirketi yönetin.",
        "hi": "अलग कार्यक्षेत्रों और भूमिका-आधारित पहुंच के साथ कई कंपनियों का प्रबंधन करें।",
        "zh": "使用独立的工作空间和基于角色的访问来管理多家公司。",
        "ar": "إدارة شركات متعددة بمساحات عمل منفصلة ووصول قائم على الأدوار.",
        "vi": "Quản lý nhiều công ty với không gian làm việc riêng biệt và truy cập dựa trên vai trò."
    },
    "Export & Integrate": {
        "en": "Export & Integrate",
        "fr": "Exporter et Intégrer",
        "sw": "Hamisha na Unganisha",
        "pt": "Exportar e Integrar",
        "es": "Exportar e Integrar",
        "tr": "Dışa Aktar ve Entegre Et",
        "hi": "निर्यात और एकीकृत करें",
        "zh": "导出和集成",
        "ar": "التصدير والتكامل",
        "vi": "Xuất và Tích hợp"
    },
    "Export data to Excel, PDF, or integrate with your existing systems via API.": {
        "en": "Export data to Excel, PDF, or integrate with your existing systems via API.",
        "fr": "Exportez des données vers Excel, PDF ou intégrez-les à vos systèmes existants via l'API.",
        "sw": "Hamisha data kwa Excel, PDF, au unganisha na mifumo yako iliyopo kupitia API.",
        "pt": "Exporte dados para Excel, PDF ou integre com seus sistemas existentes via API.",
        "es": "Exporte datos a Excel, PDF o integre con sus sistemas existentes a través de API.",
        "tr": "Verileri Excel, PDF'ye aktarın veya API aracılığıyla mevcut sistemlerinizle entegre edin.",
        "hi": "एक्सेल, पीडीएफ में डेटा निर्यात करें या एपीआई के माध्यम से अपने मौजूदा सिस्टम के साथ एकीकृत करें।",
        "zh": "将数据导出到Excel、PDF，或通过API与现有系统集成。",
        "ar": "صدّر البيانات إلى Excel أو PDF أو ادمجها مع أنظمتك الحالية عبر API.",
        "vi": "Xuất dữ liệu sang Excel, PDF hoặc tích hợp với hệ thống hiện có của bạn qua API."
    },
    
    # Pricing Section
    "Simple, Transparent Pricing": {
        "en": "Simple, Transparent Pricing",
        "fr": "Tarification Simple et Transparente",
        "sw": "Bei Rahisi na Wazi",
        "pt": "Preços Simples e Transparentes",
        "es": "Precios Simples y Transparentes",
        "tr": "Basit, Şeffaf Fiyatlandırma",
        "hi": "सरल, पारदर्शी मूल्य निर्धारण",
        "zh": "简单、透明的定价",
        "ar": "تسعير بسيط وشفاف",
        "vi": "Giá cả Đơn giản, Minh bạch"
    },
    "Choose the plan that fits your business needs. All plans include our core features.": {
        "en": "Choose the plan that fits your business needs. All plans include our core features.",
        "fr": "Choisissez le forfait qui correspond aux besoins de votre entreprise. Tous les forfaits incluent nos fonctionnalités principales.",
        "sw": "Chagua mpango unaofaa mahitaji ya biashara yako. Mipango yote inajumuisha vipengele vyetu vikuu.",
        "pt": "Escolha o plano que atende às necessidades do seu negócio. Todos os planos incluem nossos recursos principais.",
        "es": "Elija el plan que se ajuste a las necesidades de su negocio. Todos los planes incluyen nuestras características principales.",
        "tr": "İşletme ihtiyaçlarınıza uygun planı seçin. Tüm planlar temel özelliklerimizi içerir.",
        "hi": "अपने व्यवसाय की जरूरतों के अनुरूप योजना चुनें। सभी योजनाओं में हमारी मुख्य सुविधाएँ शामिल हैं।",
        "zh": "选择适合您业务需求的计划。所有计划都包含我们的核心功能。",
        "ar": "اختر الخطة التي تناسب احتياجات عملك. تتضمن جميع الخطط ميزاتنا الأساسية.",
        "vi": "Chọn gói phù hợp với nhu cầu doanh nghiệp của bạn. Tất cả các gói đều bao gồm các tính năng cốt lõi của chúng tôi."
    },
    
    # Testimonials Section
    "Loved by Accounting Professionals": {
        "en": "Loved by Accounting Professionals",
        "fr": "Apprécié par les Professionnels de la Comptabilité",
        "sw": "Inapendwa na Wataalamu wa Uhasibu",
        "pt": "Amado por Profissionais de Contabilidade",
        "es": "Amado por Profesionales de la Contabilidad",
        "tr": "Muhasebe Uzmanları Tarafından Seviliyor",
        "hi": "लेखा पेशेवरों द्वारा पसंद किया गया",
        "zh": "受到会计专业人士的喜爱",
        "ar": "محبوب من قبل المحترفين المحاسبيين",
        "vi": "Được Yêu thích bởi Các Chuyên gia Kế toán"
    },
    "Join dozens of accountants who've transformed their workforce management workflow": {
        "en": "Join dozens of accountants who've transformed their workforce management workflow",
        "fr": "Rejoignez des dizaines de comptables qui ont transformé leur flux de travail de gestion de la main-d'œuvre",
        "sw": "Jiunge na wahasibu kadhaa ambao wamebadilisha mtiririko wa kazi wa usimamizi wa wafanyikazi",
        "pt": "Junte-se a dezenas de contadores que transformaram seu fluxo de trabalho de gerenciamento de força de trabalho",
        "es": "Únase a docenas de contadores que han transformado su flujo de trabajo de gestión de fuerza laboral",
        "tr": "İşgücü yönetimi iş akışlarını dönüştüren düzinelerce muhasebeciye katılın",
        "hi": "उन दर्जनों लेखाकारों में शामिल हों जिन्होंने अपने कार्यबल प्रबंधन कार्यप्रवाह को बदल दिया है",
        "zh": "加入数十位已经改变其劳动力管理工作流程的会计师",
        "ar": "انضم إلى العشرات من المحاسبين الذين حولوا سير عمل إدارة القوى العاملة",
        "vi": "Tham gia cùng hàng chục kế toán viên đã chuyển đổi quy trình quản lý lực lượng lao động của họ"
    },
    "Real Results from Real Users": {
        "en": "Real Results from Real Users",
        "fr": "Résultats Réels d'Utilisateurs Réels",
        "sw": "Matokeo Halisi kutoka kwa Watumiaji Halisi",
        "pt": "Resultados Reais de Usuários Reais",
        "es": "Resultados Reales de Usuarios Reales",
        "tr": "Gerçek Kullanıcılardan Gerçek Sonuçlar",
        "hi": "वास्तविक उपयोगकर्ताओं से वास्तविक परिणाम",
        "zh": "来自真实用户的真实结果",
        "ar": "نتائج حقيقية من مستخدمين حقيقيين",
        "vi": "Kết quả Thực từ Người dùng Thực"
    },
    "Accounting Firms": {
        "en": "Accounting Firms",
        "fr": "Cabinets Comptables",
        "sw": "Makampuni ya Uhasibu",
        "pt": "Empresas de Contabilidade",
        "es": "Empresas de Contabilidad",
        "tr": "Muhasebe Firmaları",
        "hi": "लेखा फर्म",
        "zh": "会计事务所",
        "ar": "شركات المحاسبة",
        "vi": "Công ty Kế toán"
    },
    "Time Savings": {
        "en": "Time Savings",
        "fr": "Économies de Temps",
        "sw": "Akiba ya Wakati",
        "pt": "Economia de Tempo",
        "es": "Ahorros de Tiempo",
        "tr": "Zaman Tasarrufu",
        "hi": "समय बचत",
        "zh": "时间节省",
        "ar": "توفير الوقت",
        "vi": "Tiết kiệm Thời gian"
    },
    "Saved Per Week": {
        "en": "Saved Per Week",
        "fr": "Économisé par Semaine",
        "sw": "Imehifadhiwa kwa Wiki",
        "pt": "Economizado por Semana",
        "es": "Ahorrado por Semana",
        "tr": "Haftalık Tasarruf",
        "hi": "प्रति सप्ताह बचाया",
        "zh": "每周节省",
        "ar": "تم توفيره أسبوعياً",
        "vi": "Tiết kiệm Mỗi tuần"
    },
    "Would Recommend": {
        "en": "Would Recommend",
        "fr": "Recommanderaient",
        "sw": "Wangependekeza",
        "pt": "Recomendariam",
        "es": "Recomendarían",
        "tr": "Tavsiye Eder",
        "hi": "अनुशंसा करेंगे",
        "zh": "会推荐",
        "ar": "سيوصي",
        "vi": "Sẽ Giới thiệu"
    },
    "85% Faster Data Entry": {
        "en": "85% Faster Data Entry",
        "fr": "85% Plus Rapide pour la Saisie des Données",
        "sw": "85% Haraka Zaidi kwa Uingizaji wa Data",
        "pt": "85% Mais Rápido para Entrada de Dados",
        "es": "85% Más Rápido para Entrada de Datos",
        "tr": "Veri Girişi %85 Daha Hızlı",
        "hi": "डेटा प्रविष्टि 85% तेज़",
        "zh": "数据录入速度提高85%",
        "ar": "إدخال البيانات أسرع بنسبة 85%",
        "vi": "Nhập Dữ liệu Nhanh hơn 85%"
    },
    "Automated time tracking and payroll calculations eliminate manual data entry, letting accountants focus on strategic work instead of repetitive tasks.": {
        "en": "Automated time tracking and payroll calculations eliminate manual data entry, letting accountants focus on strategic work instead of repetitive tasks.",
        "fr": "Le suivi automatique du temps et les calculs de paie éliminent la saisie manuelle des données, permettant aux comptables de se concentrer sur le travail stratégique plutôt que sur les tâches répétitives.",
        "sw": "Ufuatiliaji wa muda wa kiotomatiki na mahesabu ya malipo huondoa uingizaji wa mikono wa data, kuwaruhusu wahasibu kuzingatia kazi ya kimkakati badala ya kazi zinazojiri rudia.",
        "pt": "O rastreamento automatizado de tempo e cálculos de folha de pagamento eliminam a entrada manual de dados, permitindo que contadores se concentrem em trabalho estratégico em vez de tarefas repetitivas.",
        "es": "El seguimiento automatizado del tiempo y los cálculos de nómina eliminan la entrada manual de datos, permitiendo que los contadores se centren en el trabajo estratégico en lugar de tareas repetitivas.",
        "tr": "Otomatik zaman takibi ve bordro hesaplamaları manuel veri girişini ortadan kaldırır, muhasebecilerin tekrarlayan görevler yerine stratejik işlere odaklanmasını sağlar.",
        "hi": "स्वचालित समय ट्रैकिंग और पेरोल गणना मैनुअल डेटा प्रविष्टि को समाप्त करती है, लेखाकारों को दोहराए जाने वाले कार्यों के बजाय रणनीतिक कार्य पर ध्यान केंद्रित करने देती है।",
        "zh": "自动时间跟踪和工资单计算消除了手动数据录入，让会计师专注于战略工作而不是重复性任务。",
        "ar": "يلغي تتبع الوقت التلقائي وحسابات الرواتب إدخال البيانات يدوياً، مما يتيح للمحاسبين التركيز على العمل الاستراتيجي بدلاً من المهام المتكررة.",
        "vi": "Theo dõi thời gian tự động và tính toán bảng lương loại bỏ nhập dữ liệu thủ công, cho phép kế toán tập trung vào công việc chiến lược thay vì các công việc lặp đi lặp lại."
    },
    "Seamless Client Reporting": {
        "en": "Seamless Client Reporting",
        "fr": "Rapport Client Transparent",
        "sw": "Ripoti ya Mteja bila Kikwazo",
        "pt": "Relatórios de Clientes Sem Interrupções",
        "es": "Informes de Clientes Sin Interrupciones",
        "tr": "Sorunsuz Müşteri Raporlaması",
        "hi": "सहज ग्राहक रिपोर्टिंग",
        "zh": "无缝客户报告",
        "ar": "تقارير العملاء السلسة",
        "vi": "Báo cáo Khách hàng Liền mạch"
    },
    "Generate comprehensive workforce reports in seconds. Our platform transforms complex attendance data into clear, professional reports that clients love.": {
        "en": "Generate comprehensive workforce reports in seconds. Our platform transforms complex attendance data into clear, professional reports that clients love.",
        "fr": "Générez des rapports complets sur la main-d'œuvre en quelques secondes. Notre plateforme transforme les données de présence complexes en rapports clairs et professionnels que les clients adorent.",
        "sw": "Zalisha ripoti kamili za wafanyikazi kwa sekunde chache. Jukwaa letu linabadilisha data ngumu za mahضeri kuwa ripoti wazi na za kitaalamu ambazo wateja hupenda.",
        "pt": "Gere relatórios abrangentes da força de trabalho em segundos. Nossa plataforma transforma dados complexos de presença em relatórios claros e profissionais que os clientes adoram.",
        "es": "Genere informes completos de la fuerza laboral en segundos. Nuestra plataforma transforma datos complejos de asistencia en informes claros y profesionales que los clientes aman.",
        "tr": "Saniyeler içinde kapsamlı işgücü raporları oluşturun. Platformumuz karmaşık devam verilerini müşterilerin sevdiği net, profesyonel raporlara dönüştürür.",
        "hi": "सेकंडों में व्यापक कार्यबल रिपोर्ट तैयार करें। हमारा प्लेटफॉर्म जटिल उपस्थिति डेटा को स्पष्ट, पेशेवर रिपोर्ट में बदल देता है जिसे ग्राहक पसंद करते हैं।",
        "zh": "在几秒钟内生成全面的劳动力报告。我们的平台将复杂的考勤数据转化为客户喜爱的清晰、专业的报告。",
        "ar": "أنشئ تقارير شاملة عن القوى العاملة في ثوانٍ. تحول منصتنا بيانات الحضور المعقدة إلى تقارير واضحة واحترافية يحبها العملاء.",
        "vi": "Tạo báo cáo lực lượng lao động toàn diện trong vài giây. Nền tảng của chúng tôi biến đổi dữ liệu chuyên cần phức tạp thành báo cáo rõ ràng, chuyên nghiệp mà khách hàng yêu thích."
    },
    "Error-Free Calculations": {
        "en": "Error-Free Calculations",
        "fr": "Calculs Sans Erreur",
        "sw": "Mahesabu Bila Makosa",
        "pt": "Cálculos Sem Erros",
        "es": "Cálculos Sin Errores",
        "tr": "Hatasız Hesaplamalar",
        "hi": "त्रुटि-मुक्त गणना",
        "zh": "无错误计算",
        "ar": "حسابات خالية من الأخطاء",
        "vi": "Tính toán Không có Lỗi"
    },
    "Eliminate calculation errors with automated payroll processing. Built-in compliance checks ensure accuracy and reduce liability for accounting firms.": {
        "en": "Eliminate calculation errors with automated payroll processing. Built-in compliance checks ensure accuracy and reduce liability for accounting firms.",
        "fr": "Éliminez les erreurs de calcul avec le traitement automatisé de la paie. Les contrôles de conformité intégrés garantissent la précision et réduisent la responsabilité des cabinets comptables.",
        "sw": "Ondoa makosa ya mahesabu kwa usindikaji wa kiotomatiki wa malipo. Ukaguzi wa kufuata sheria uliojengewa hunahakikisha usahihi na kupunguza dhima kwa makampuni ya uhasibu.",
        "pt": "Elimine erros de cálculo com processamento automatizado de folha de pagamento. Verificações de conformidade integradas garantem precisão e reduzem a responsabilidade para empresas de contabilidade.",
        "es": "Elimine errores de cálculo con procesamiento automatizado de nómina. Las verificaciones de cumplimiento integradas garantizan la precisión y reducen la responsabilidad para las empresas de contabilidad.",
        "tr": "Otomatik bordro işleme ile hesaplama hatalarını ortadan kaldırın. Yerleşik uyumluluk kontrolleri doğruluğu sağlar ve muhasebe firmaları için sorumluluğu azaltır.",
        "hi": "स्वचालित पेरोल प्रोसेसिंग के साथ गणना त्रुटियों को समाप्त करें। अंतर्निहित अनुपालन जांच सटीकता सुनिश्चित करती है और लेखा फर्मों के लिए देनदारी को कम करती है।",
        "zh": "通过自动工资单处理消除计算错误。内置的合规检查确保准确性并降低会计事务所的责任。",
        "ar": "قضِ على أخطاء الحساب مع معالجة الرواتب الآلية. تضمن فحوصات الامتثال المدمجة الدقة وتقلل من المسؤولية لشركات المحاسبة.",
        "vi": "Loại bỏ lỗi tính toán với xử lý bảng lương tự động. Kiểm tra tuân thủ tích hợp đảm bảo độ chính xác và giảm trách nhiệm pháp lý cho các công ty kế toán."
    },
    
    # Privacy & Legal
    "Your Data, Your Control": {
        "en": "Your Data, Your Control",
        "fr": "Vos Données, Votre Contrôle",
        "sw": "Data Yako, Udhibiti Wako",
        "pt": "Seus Dados, Seu Controle",
        "es": "Sus Datos, Su Control",
        "tr": "Verileriniz, Kontrolünüz",
        "hi": "आपका डेटा, आपका नियंत्रण",
        "zh": "您的数据，您的控制",
        "ar": "بياناتك، تحكمك",
        "vi": "Dữ liệu của Bạn, Quyền Kiểm soát của Bạn"
    },
    "We're committed to protecting your privacy and maintaining transparency in how we handle your data.": {
        "en": "We're committed to protecting your privacy and maintaining transparency in how we handle your data.",
        "fr": "Nous nous engageons à protéger votre vie privée et à maintenir la transparence dans la manière dont nous traitons vos données.",
        "sw": "Tumejitolea kulinda faragha yako na kudumisha uwazi katika jinsi tunavyoshughulikia data yako.",
        "pt": "Estamos comprometidos em proteger sua privacidade e manter a transparência em como lidamos com seus dados.",
        "es": "Estamos comprometidos a proteger su privacidad y mantener la transparencia en cómo manejamos sus datos.",
        "tr": "Gizliliğinizi korumaya ve verilerinizi nasıl ele aldığımız konusunda şeffaflığı sürdürmeye kararlıyız.",
        "hi": "हम आपकी गोपनीयता की रक्षा करने और आपके डेटा को संभालने में पारदर्शिता बनाए रखने के लिए प्रतिबद्ध हैं।",
        "zh": "我们致力于保护您的隐私并保持处理您数据的透明度。",
        "ar": "نحن ملتزمون بحماية خصوصيتك والحفاظ على الشفافية في كيفية التعامل مع بياناتك.",
        "vi": "Chúng tôi cam kết bảo vệ quyền riêng tư của bạn và duy trì tính minh bạch trong cách chúng tôi xử lý dữ liệu của bạn."
    },
    "Privacy Policy": {
        "en": "Privacy Policy",
        "fr": "Politique de Confidentialité",
        "sw": "Sera ya Faragha",
        "pt": "Política de Privacidade",
        "es": "Política de Privacidad",
        "tr": "Gizlilik Politikası",
        "hi": "गोपनीयता नीति",
        "zh": "隐私政策",
        "ar": "سياسة الخصوصية",
        "vi": "Chính sách Bảo mật"
    },
    "Terms of Use": {
        "en": "Terms of Use",
        "fr": "Conditions d'Utilisation",
        "sw": "Masharti ya Matumizi",
        "pt": "Termos de Uso",
        "es": "Términos de Uso",
        "tr": "Kullanım Şartları",
        "hi": "उपयोग की शर्तें",
        "zh": "使用条款",
        "ar": "شروط الاستخدام",
        "vi": "Điều khoản Sử dụng"
    },
    
    # CTA Section
    "Ready to Transform Your Workforce Management?": {
        "en": "Ready to Transform Your Workforce Management?",
        "fr": "Prêt à Transformer Votre Gestion de la Main-d'œuvre?",
        "sw": "Uko Tayari Kubadilisha Usimamizi wa Wafanyikazi Wako?",
        "pt": "Pronto para Transformar Seu Gerenciamento de Força de Trabalho?",
        "es": "¿Listo para Transformar Su Gestión de Fuerza Laboral?",
        "tr": "İş Gücü Yönetiminizi Dönüştürmeye Hazır mısınız?",
        "hi": "अपने कार्यबल प्रबंधन को बदलने के लिए तैयार हैं?",
        "zh": "准备好改变您的劳动力管理了吗？",
        "ar": "هل أنت مستعد لتحويل إدارة القوى العاملة الخاصة بك؟",
        "vi": "Sẵn sàng Chuyển đổi Quản lý Lực lượng Lao động của Bạn?"
    },
    "Join thousands of companies that trust us with their workforce management needs.": {
        "en": "Join thousands of companies that trust us with their workforce management needs.",
        "fr": "Rejoignez des milliers d'entreprises qui nous font confiance pour leurs besoins en gestion de la main-d'œuvre.",
        "sw": "Jiunge na makampuni elfu ambayo yanatuamini na mahitaji yao ya usimamizi wa wafanyikazi.",
        "pt": "Junte-se a milhares de empresas que confiam em nós com suas necessidades de gerenciamento de força de trabalho.",
        "es": "Únase a miles de empresas que confían en nosotros con sus necesidades de gestión de fuerza laboral.",
        "tr": "İşgücü yönetimi ihtiyaçları için bize güvenen binlerce şirkete katılın.",
        "hi": "उन हजारों कंपनियों में शामिल हों जो अपनी कार्यबल प्रबंधन जरूरतों के लिए हम पर भरोसा करती हैं।",
        "zh": "加入数千家信任我们的公司，满足他们的劳动力管理需求。",
        "ar": "انضم إلى آلاف الشركات التي تثق بنا في احتياجات إدارة القوى العاملة.",
        "vi": "Tham gia cùng hàng nghìn công ty tin tưởng chúng tôi với nhu cầu quản lý lực lượng lao động của họ."
    },
    "Contact Sales": {
        "en": "Contact Sales",
        "fr": "Contacter les Ventes",
        "sw": "Wasiliana na Mauzo",
        "pt": "Contatar Vendas",
        "es": "Contactar Ventas",
        "tr": "Satış ile İletişime Geçin",
        "hi": "बिक्री से संपर्क करें",
        "zh": "联系销售",
        "ar": "اتصل بالمبيعات",
        "vi": "Liên hệ Bán hàng"
    },
    
    # Footer
    "Professional workforce management for modern businesses.": {
        "en": "Professional workforce management for modern businesses.",
        "fr": "Gestion professionnelle de la main-d'œuvre pour les entreprises modernes.",
        "sw": "Usimamizi wa kitaalamu wa wafanyikazi kwa biashara za kisasa.",
        "pt": "Gerenciamento profissional da força de trabalho para empresas modernas.",
        "es": "Gestión profesional de la fuerza laboral para empresas modernas.",
        "tr": "Modern işletmeler için profesyonel işgücü yönetimi.",
        "hi": "आधुनिक व्यवसायों के लिए पेशेवर कार्यबल प्रबंधन।",
        "zh": "为现代企业提供专业的劳动力管理。",
        "ar": "إدارة القوى العاملة المهنية للشركات الحديثة.",
        "vi": "Quản lý lực lượng lao động chuyên nghiệp cho các doanh nghiệp hiện đại."
    },
    "Product": {
        "en": "Product",
        "fr": "Produit",
        "sw": "Bidhaa",
        "pt": "Produto",
        "es": "Producto",
        "tr": "Ürün",
        "hi": "उत्पाद",
        "zh": "产品",
        "ar": "المنتج",
        "vi": "Sản phẩm"
    },
    "API": {
        "en": "API",
        "fr": "API",
        "sw": "API",
        "pt": "API",
        "es": "API",
        "tr": "API",
        "hi": "API",
        "zh": "API",
        "ar": "API",
        "vi": "API"
    },
    "Integrations": {
        "en": "Integrations",
        "fr": "Intégrations",
        "sw": "Michanganyiko",
        "pt": "Integrações",
        "es": "Integraciones",
        "tr": "Entegrasyonlar",
        "hi": "एकीकरण",
        "zh": "集成",
        "ar": "التكاملات",
        "vi": "Tích hợp"
    },
    "Support": {
        "en": "Support",
        "fr": "Support",
        "sw": "Msaada",
        "pt": "Suporte",
        "es": "Soporte",
        "tr": "Destek",
        "hi": "समर्थन",
        "zh": "支持",
        "ar": "الدعم",
        "vi": "Hỗ trợ"
    },
    "Help Center": {
        "en": "Help Center",
        "fr": "Centre d'Aide",
        "sw": "Kituo cha Msaada",
        "pt": "Centro de Ajuda",
        "es": "Centro de Ayuda",
        "tr": "Yardım Merkezi",
        "hi": "सहायता केंद्र",
        "zh": "帮助中心",
        "ar": "مركز المساعدة",
        "vi": "Trung tâm Trợ giúp"
    },
    "Contact Us": {
        "en": "Contact Us",
        "fr": "Nous Contacter",
        "sw": "Wasiliana Nasi",
        "pt": "Entre em Contato",
        "es": "Contáctenos",
        "tr": "Bize Ulaşın",
        "hi": "हमसे संपर्क करें",
        "zh": "联系我们",
        "ar": "اتصل بنا",
        "vi": "Liên hệ với Chúng tôi"
    },
    "Status": {
        "en": "Status",
        "fr": "Statut",
        "sw": "Hali",
        "pt": "Status",
        "es": "Estado",
        "tr": "Durum",
        "hi": "स्थिति",
        "zh": "状态",
        "ar": "الحالة",
        "vi": "Trạng thái"
    },
    "Documentation": {
        "en": "Documentation",
        "fr": "Documentation",
        "sw": "Nyaraka",
        "pt": "Documentação",
        "es": "Documentación",
        "tr": "Dokümantasyon",
        "hi": "प्रलेखन",
        "zh": "文档",
        "ar": "التوثيق",
        "vi": "Tài liệu"
    },
    "Legal": {
        "en": "Legal",
        "fr": "Juridique",
        "sw": "Kisheria",
        "pt": "Legal",
        "es": "Legal",
        "tr": "Yasal",
        "hi": "कानूनी",
        "zh": "法律",
        "ar": "القانونية",
        "vi": "Pháp lý"
    },
    "Compliance": {
        "en": "Compliance",
        "fr": "Conformité",
        "sw": "Kufuata Sheria",
        "pt": "Conformidade",
        "es": "Cumplimiento",
        "tr": "Uyumluluk",
        "hi": "अनुपालन",
        "zh": "合规性",
        "ar": "الامتثال",
        "vi": "Tuân thủ"
    },
    "Security": {
        "en": "Security",
        "fr": "Sécurité",
        "sw": "Usalama",
        "pt": "Segurança",
        "es": "Seguridad",
        "tr": "Güvenlik",
        "hi": "सुरक्षा",
        "zh": "安全",
        "ar": "الأمان",
        "vi": "Bảo mật"
    },
    "Company": {
        "en": "Company",
        "fr": "Entreprise",
        "sw": "Kampuni",
        "pt": "Empresa",
        "es": "Empresa",
        "tr": "Şirket",
        "hi": "कंपनी",
        "zh": "公司",
        "ar": "الشركة",
        "vi": "Công ty"
    },
    "About": {
        "en": "About",
        "fr": "À propos",
        "sw": "Kuhusu",
        "pt": "Sobre",
        "es": "Acerca de",
        "tr": "Hakkında",
        "hi": "के बारे में",
        "zh": "关于",
        "ar": "حول",
        "vi": "Về chúng tôi"
    },
    "Blog": {
        "en": "Blog",
        "fr": "Blog",
        "sw": "Blogu",
        "pt": "Blog",
        "es": "Blog",
        "tr": "Blog",
        "hi": "ब्लॉग",
        "zh": "博客",
        "ar": "المدونة",
        "vi": "Blog"
    },
    "Careers": {
        "en": "Careers",
        "fr": "Carrières",
        "sw": "Kazi",
        "pt": "Carreiras",
        "es": "Carreras",
        "tr": "Kariyer",
        "hi": "करियर",
        "zh": "职业",
        "ar": "الوظائف",
        "vi": "Nghề nghiệp"
    },
    "Press": {
        "en": "Press",
        "fr": "Presse",
        "sw": "Habari",
        "pt": "Imprensa",
        "es": "Prensa",
        "tr": "Basın",
        "hi": "प्रेस",
        "zh": "新闻",
        "ar": "الصحافة",
        "vi": "Báo chí"
    },
    "All rights reserved.": {
        "en": "All rights reserved.",
        "fr": "Tous droits réservés.",
        "sw": "Haki zote zimehifadhiwa.",
        "pt": "Todos os direitos reservados.",
        "es": "Todos los derechos reservados.",
        "tr": "Tüm hakları saklıdır.",
        "hi": "सर्वाधिकार सुरक्षित।",
        "zh": "保留所有权利。",
        "ar": "كل الحقوق محفوظة.",
        "vi": "Đã đăng ký Bản quyền."
    },
    "Legal Compliance": {
        "en": "Legal Compliance",
        "fr": "Conformité Légale",
        "sw": "Kufuata Sheria",
        "pt": "Conformidade Legal",
        "es": "Cumplimiento Legal",
        "tr": "Yasal Uyumluluk",
        "hi": "कानूनी अनुपालन",
        "zh": "法律合规",
        "ar": "الامتثال القانوني",
        "vi": "Tuân thủ Pháp luật"
    }
}

def expand_translations():
    """Expand all translation files with complete landing page strings"""
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
        new_count = 0
        for key, translations in LANDING_TRANSLATIONS.items():
            if key not in existing:
                existing[key] = translations.get(lang, translations.get('en', key))
                new_count += 1
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2, sort_keys=True)
        
        print(f"✅ Updated {lang}.json - Added {new_count} new strings, Total: {len(existing)} strings")

if __name__ == '__main__':
    expand_translations()
    print(f"\n✅ All translation files expanded with {len(LANDING_TRANSLATIONS)} complete landing page strings!")
