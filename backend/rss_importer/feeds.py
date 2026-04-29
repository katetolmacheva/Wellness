"""
Список RSS-источников для импорта статей о здоровье.

Чтобы отключить источник — поставь:
    "enabled": False
"""

FEEDS = [

    # Takzdorovo (Минздрав РФ)

    {
        "key": "takzdorovo",
        "title": "Takzdorovo (Минздрав РФ)",
        "site_url": "https://www.takzdorovo.ru",
        "rss_url": "https://www.takzdorovo.ru/rss/news/",
        "default_category": "Здоровье",
        "author_name": "Редакция Takzdorovo",
        "author_bio": "Официальный портал о здоровом образе жизни (Минздрав РФ)",
        "adapter": "generic",
        "trust_level": "high",
        "enabled": True,
    },


    # Zozhnik

    {
        "key": "zozhnik",
        "title": "Zozhnik",
        "site_url": "https://zozhnik.ru",
        "rss_url": "https://zozhnik.ru/feed",
        "default_category": "ЗОЖ",
        "author_name": "Редакция Zozhnik",
        "author_bio": "Материалы о здоровом образе жизни, тренировках и питании",
        "adapter": "generic",
        "trust_level": "medium",
        "enabled": True,
    },


    # Fitlabs

    {
        "key": "fitlabs",
        "title": "Fitlabs",
        "site_url": "https://fitlabs.ru",
        "rss_url": "https://fitlabs.ru/feed",
        "default_category": "Питание",
        "author_name": "Ирина Брехт",
        "author_bio": "Нутрициолог и тренер",
        "adapter": "generic",
        "trust_level": "medium",
        "enabled": True,
    },


    # Popular Nutrition

    {
        "key": "popularnutrition",
        "title": "Popular Nutrition",
        "site_url": "https://popularnutrition.ru",
        "rss_url": "https://popularnutrition.ru/feed",
        "default_category": "Нутрициология",
        "author_name": "Редакция Popular Nutrition",
        "author_bio": "Научно-популярный журнал о питании",
        "adapter": "generic",
        "trust_level": "medium",
        "enabled": True,
    },


    # Encyclopatia (Никита Жуков)

    {
        "key": "encyclopatia",
        "title": "Encyclopatia",
        "site_url": "https://encyclopatia.ru",
        "rss_url": "https://encyclopatia.ru/feed",
        "default_category": "Медицина",
        "author_name": "Никита Жуков",
        "author_bio": "Врач, автор медицинских статей",
        "adapter": "generic",
        "trust_level": "medium",
        "enabled": True,
    },


    # Medfront

    {
        "key": "medfront",
        "title": "Medfront",
        "site_url": "https://medfront.org",
        "rss_url": "https://medfront.org/feed",
        "default_category": "Доказательная медицина",
        "author_name": "Редакция Medfront",
        "author_bio": "Блог о доказательной медицине",
        "adapter": "generic",
        "trust_level": "high",
        "enabled": True,
    },


    # Health Diet

    {
        "key": "health-diet",
        "title": "Health Diet",
        "site_url": "https://health-diet.ru",
        "rss_url": "https://health-diet.ru/feed",
        "default_category": "Питание",
        "author_name": "Редакция Health Diet",
        "author_bio": "База данных продуктов и нутриентов",
        "adapter": "generic",
        "trust_level": "medium",
        "enabled": True,
    },


    # SportWiki

    {
        "key": "sportwiki",
        "title": "SportWiki",
        "site_url": "https://sportwiki.to",
        "rss_url": "https://sportwiki.to/feed",
        "default_category": "Спорт",
        "author_name": "Редакция SportWiki",
        "author_bio": "Энциклопедия бодибилдинга и спортивной науки",
        "adapter": "generic",
        "trust_level": "medium",
        "enabled": True,
    },


    # Fitness-Pro

    {
        "key": "fitness-pro",
        "title": "Fitness-Pro",
        "site_url": "https://fitness-pro.ru",
        "rss_url": "https://fitness-pro.ru/feed",
        "default_category": "Фитнес",
        "author_name": "Ассоциация профессионалов фитнеса",
        "author_bio": "Профессиональные материалы для тренеров",
        "adapter": "generic",
        "trust_level": "medium",
        "enabled": True,
    },

]