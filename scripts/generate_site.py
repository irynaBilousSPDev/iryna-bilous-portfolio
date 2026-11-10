#!/usr/bin/env python3
"""Generate PL / EN / UA static HTML for Iryna Bilous portfolio."""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

WARSAW = ZoneInfo("Europe/Warsaw")
LAST_UPDATED_ENV = "SITE_LAST_UPDATED"

MONTH_PL_GENITIVE = (
    "stycznia",
    "lutego",
    "marca",
    "kwietnia",
    "maja",
    "czerwca",
    "lipca",
    "sierpnia",
    "września",
    "października",
    "listopada",
    "grudnia",
)
MONTH_UA_GENITIVE = (
    "січня",
    "лютого",
    "березня",
    "квітня",
    "травня",
    "червня",
    "липня",
    "серпня",
    "вересня",
    "жовтня",
    "листопада",
    "грудня",
)
MONTH_EN = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from icons import (  # noqa: E402
    BLUE,
    COMP_ICON_KEYS,
    FACT_ICON_KEYS,
    PINK,
    PROOF_ICON_KEYS,
    comp_icon_color,
    stroke_icon,
)

ADN_AKADEMIA_URL = "https://www.adnakademia.pl/"

ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = ROOT / "assets/css/main.css"
SCSS_ENTRY = ROOT / "assets/scss/main.scss"
SITE = "https://irynabilousspdev.github.io/iryna-bilous-portfolio"
LINKEDIN = "https://www.linkedin.com/in/iryna-bilous-166343164/"
IT_COMMUNITY = "https://it-community.io/people/iryna-bilous-38"
EMAIL = "bilousiryna6@gmail.com"

_PROJECTS_JSON = json.loads((ROOT / "site-data/projects.json").read_text(encoding="utf-8"))
SITE_META = _PROJECTS_JSON.get("site") or {}
PROJECTS = {k: v for k, v in _PROJECTS_JSON.items() if k in ("avista", "vizja", "spdev")}

PERIOD_LABELS = {
    "pl": {
        "avista": "Avista (2024–obecnie)",
        "vizja": "VIZJA (2021–2024)",
        "spdev": "SP//DEV (2018–2021)",
    },
    "en": {
        "avista": "Avista (2024–present)",
        "vizja": "VIZJA (2021–2024)",
        "spdev": "SP//DEV (2018–2021)",
    },
    "ua": {
        "avista": "Avista (2024–донині)",
        "vizja": "VIZJA (2021–2024)",
        "spdev": "SP//DEV (2018–2021)",
    },
}


def t(lang: str) -> dict:
    """Localized copy (faithful to approved PL sources)."""
    if lang == "pl":
        return {
            "html_lang": "pl",
            "title": "Iryna Bilous — Frontend / WordPress Developer",
            "meta_description": (
                "Tworzę strony i sklepy na WordPressie — motywy, WooCommerce, integracje i dostępność WCAG. "
                "Warszawa · stacjonarnie i online. Portfolio Iryny Bilous."
            ),
            "nav": [
                ("O mnie", "#o-mnie"),
                ("Kompetencje", "#kompetencje"),
                ("Usługi", "#uslugi"),
                ("Doświadczenie", "#doswiadczenie"),
                ("Realizacje", "#realizacje"),
            ],
            "nav_aria": "Główne",
            "menu_open": "Otwórz menu",
            "menu_close": "Zamknij menu",
            "lang_aria": "Język strony",
            "cta_write": "Napisz do mnie",
            "cta_projects": "Zobacz realizacje",
            "badge": "Frontend / WordPress Developer · Warszawa stacjonarnie i online",
            "hello": "Cześć, jestem Iryna",
            "hero_h1": "Tworzę strony i sklepy na WordPressie",
            "hero_lead": (
                "Od ponad 10 lat tworzę serwisy dla uczelni, e-commerce i firm usługowych: własne motywy, bloki Gutenberg, "
                "WooCommerce, automatyzacje i dostępność WCAG. Łączę kod z analizą potrzeb biznesowych i logiką produktu."
            ),
            "hero_lead_short": (
                "Własne motywy, sklepy WooCommerce i integracje dla uczelni, e-commerce i firm usługowych — od ponad 10 lat."
            ),
            "loc_title": "Warszawa · od 2020",
            "loc_sub": "UA · PL · EN",
            "portrait_alt": "Czarno-biały portret Iryny Bilous",
            "proof": [
                ("10+", "lat w web developmencie", "WordPress, frontend i backend"),
                ("7+", "projektów dla uczelni", "WooCommerce, płatności, InPost, BIP"),
                ("WCAG 2.1", "certyfikat dostępności", "Zdobyty w 2022 roku"),
                ("2", "własne projekty", "Rozwijane z narzędziami AI"),
            ],
            "about_eyebrow": "O mnie",
            "about_title": "Od Kałusza do Warszawy — ponad 10 lat w web developmencie",
            "about_paras": [
                "Mam na imię Iryna. Pochodzę z Kałusza (Ukraina), a moja droga w IT zaczęła się w Iwano-Frankiwsku, gdzie w firmie "
                "SP//DEV zdobywałam praktykę i wiedzę, pracując z WordPressem, i poznałam wielu przyjaciół z branży. "
                "Od 2020 roku mieszkam i pracuję w Warszawie.",
                "Web developmentem zajmuję się od ponad 10 lat. Pracuję z WordPressem — po stronie frontendu i backendu: tworzę strony, "
                "aplikacje webowe i różnego rodzaju integracje. Realizowałam projekty w wielu branżach — od edukacji i e-commerce "
                "po inne produkty cyfrowe.",
                "Lubię się uczyć i odkrywać nowe rzeczy. Ukończyłam kurs Data Analytics, a obecnie poznaję Project Management i UI/UX Design. "
                "Szczególnie interesuje mnie sztuczna inteligencja w programowaniu — na co dzień eksperymentuję z narzędziami AI, m.in. "
                "Cursorem, a po godzinach rozwijam dwa własne projekty.",
            ],
            "facts": [
                (
                    "Lokalizacja",
                    "Warszawa · stacjonarnie, hybrydowo i online",
                ),
                ("Języki", "ukraiński — ojczysty\npolski — biegły\nangielski — średniozaawansowany"),
                ("Wykształcenie", "Magister, budownictwo przemysłowe i cywilne — Politechnika Lwowska, 2008–2013"),
                ("Poza pracą", "Góry, rower, boks, podróże i surfing w ciepłych krajach. W domu czekają na mnie dwa koty."),
            ],
            "comp_eyebrow": "Kluczowe kompetencje",
            "comp_title": "Kod, produkt i jakość w jednym procesie",
            "comp_intro": (
                "Moje doświadczenie łączy programowanie z pracą nad produktem: od wymagań biznesowych, przez logikę "
                "funkcji, po testy i utrzymanie gotowego serwisu."
            ),
            "comp_items": [
                ("Duże ekosystemy webowe", "WordPress Multisite, wielojęzyczność, e-commerce, edukacja"),
                ("Automatyzacja i integracje", "WooCommerce, systemy płatności, InPost, API i automatyzacja"),
                ("AI-assisted development", "Cursor i narzędzia AI — szybszy rozwój i eksperymenty"),
                ("Product thinking i automatyzacja", "Analiza biznesowa, logika produktów, Trello i automatyzacja procesów"),
                ("WordPress Engineering", "Gutenberg, ACF, CPT, PHP, JavaScript, SCSS, własne motywy"),
                ("Marketing i rozwój produktu", "Akcje, oferty, kalkulatory, UX i strategie marketingowe"),
                ("Koordynacja i analiza biznesowa", "Praca z zespołem, Trello, analiza wymagań, planowanie"),
                ("QA i operacje techniczne", "Testy, WCAG, SEO, Git, Plesk, audyty techniczne"),
            ],
            "serv_eyebrow": "Usługi",
            "serv_title": "W czym mogę Ci pomóc",
            "serv_intro": (
                "Pracuję z firmami, uczelniami i sklepami internetowymi — przy nowych stronach i przy rozwoju serwisów, "
                "które już działają."
            ),
            "serv_when": "Kiedy warto",
            "services": [
                (
                    "Własny motyw WordPress",
                    "Motyw zbudowany pod Twoje treści: bloki Gutenberg, pola ACF i własne typy wpisów, dzięki którym zespół edytuje stronę w panelu, bez zmian w kodzie.",
                    "Gdy gotowy szablon ogranicza, a strona ma się rozwijać.",
                ),
                (
                    "Sklep na WooCommerce",
                    "Katalog, koszyk, płatności online i InPost, a także dopasowanie procesu zamówień do sposobu pracy Twojego zespołu.",
                    "Gdy zaczynasz sprzedaż online albo rozbudowujesz istniejący sklep.",
                ),
                (
                    "Integracje i automatyzacja",
                    "Połączenie WordPressa z API i usługami zewnętrznymi oraz automatyzacje w Google Apps Script, Trello czy Power Automate.",
                    "Gdy zespół ręcznie powtarza te same czynności.",
                ),
                (
                    "Narzędzia interaktywne",
                    "Kalkulatory, formularze, filtry i interfejsy wielojęzyczne, a także mechaniki akcji i ofert przygotowywane z marketingiem.",
                    "Gdy strona ma pomagać klientom w wyborze, a nie tylko informować.",
                ),
                (
                    "Dostępność, testy i audyt",
                    "Audyt techniczny, wdrożenie standardów WCAG 2.1, SEO techniczne, optymalizacja i bieżące utrzymanie.",
                    "Gdy strona ma błędy, działa wolno lub musi spełniać wymogi dostępności.",
                ),
                (
                    "Rozbudowa dużych serwisów",
                    "WordPress Multisite, wiele wersji językowych, BIP, strony wydarzeń i konferencji — uporządkowana struktura wielu serwisów.",
                    "Gdy prowadzisz kilka stron albo organizację z wieloma działami.",
                ),
            ],
            "serv_cta": "Opowiedz mi o swoim projekcie",
            "exp_eyebrow": "Doświadczenie",
            "exp_title": "Gdzie pracowałam i czym się zajmuję",
            "exp_intro": "Od 2017 roku pracuję przy stronach i serwisach WordPress — dla firm, uczelni i klientów z kilku krajów.",
            "experience": [
                {
                    "dates": "05.2024 — obecnie",
                    "co": "Avista",
                    "role": "Frontend / WordPress Developer",
                    "mode": "Hybrydowo · pełny etat · Warszawa",
                    "intro": "Rozwój i utrzymanie serwisów dla firm z branży edukacji, e-commerce, usług i rozwiązań korporacyjnych.",
                    "bullets": [
                        "Frontend i PHP: własne motywy WordPress, bloki Gutenberg, WooCommerce, wtyczki i integracje API",
                        "Automatyzacja procesów biznesowych: Google Apps Script, Trello, Power Automate i usługi zewnętrzne",
                        "Interaktywne narzędzia: kalkulatory, formularze, filtry i interfejsy wielojęzyczne",
                        "Testy, optymalizacja, audyty techniczne, WCAG i utrzymanie stron",
                        "Współpraca z marketingiem przy ofertach, akcjach, kampaniach i scenariuszach użytkownika",
                        "Analiza potrzeb biznesowych, logika produktów i konsultacje z kierownictwem",
                        "Koordynacja zadań zespołu w Trello i usprawnianie organizacji pracy",
                        "Cursor i narzędzia AI w programowaniu oraz automatyzacji",
                    ],
                    "projects": ["akademiata.pl", "uni-munich.de", "unixedu.com", "i wiele innych serwisów"],
                },
                {
                    "dates": "03.2021 — 08.2024",
                    "co": "Uniwersytet VIZJA",
                    "role": "Frontend Developer",
                    "mode": "Warszawa",
                    "intro": "Ponad trzy lata rozwoju serwisów Akademii Ekonomiczno-Humanistycznej w Warszawie, dziś Uniwersytetu VIZJA.",
                    "bullets": [
                        "WordPress Multisite, PHP, JavaScript, HTML, CSS, ACF i WooCommerce",
                        "Własne motywy, funkcjonalności i responsywne interfejsy",
                        "Integracje systemów płatności oraz InPost",
                        "Automatyzacja procesów, wydajność, audyty i wdrażanie standardów WCAG",
                        "Planowanie struktury, UI/UX i funkcji nowych oraz istniejących serwisów",
                        "Współpraca z kierownictwem, marketingiem, rekrutacją i administracją",
                        "Przez rok frontend w projekcie unijnym realizowanym przez uczelnię",
                    ],
                    "projects": [
                        "vizja.pl",
                        "tevizja.pl",
                        "vizja.shop",
                        "vizjafood.pl",
                        "bip.vizja.pl",
                        "certyfikatpolski.vizja.pl",
                        "strony konferencji",
                    ],
                },
                {
                    "dates": "2017 — 2021",
                    "co": "SP//DEV",
                    "role": "Frontend / WordPress Developer",
                    "mode": "Klienci międzynarodowi",
                    "intro": "Realizacje WordPress dla klientów m.in. z Francji i Holandii.",
                    "bullets": [
                        "Strony usługowe, edukacyjne i e-commerce",
                        "Wdrożenia motywów i responsywne układy",
                        "Bieżące utrzymanie i rozwój stron klientów",
                    ],
                    "projects": [],
                },
            ],
            "skills_eyebrow": "Umiejętności",
            "skills_title": "Technologie i narzędzia",
            "skills": [
                ("CMS i e-commerce", ["WordPress", "Multisite", "Gutenberg", "ACF", "Custom Post Types", "WooCommerce"]),
                ("Frontend", ["HTML", "CSS / SCSS", "JavaScript", "RWD", "Interfejsy wielojęzyczne"]),
                ("Backend i integracje", ["PHP", "API", "Systemy płatności", "InPost", "Google Apps Script", "Power Automate"]),
                ("Jakość", ["WCAG 2.1", "Testy", "Audyty techniczne", "SEO", "Wydajność"]),
                ("Warsztat", ["Git", "Plesk", "Trello", "Cursor", "Narzędzia AI"]),
            ],
            "learn_certs": "Certyfikaty",
            "learn_growth": "Rozwój",
            "cert_items": [
                "WCAG 2.1 — dostępność stron, 2022",
                "Front-end Web — IT Cluster Academy, 2017",
                "JavaScript + Angular — IT Cluster Academy, 2019",
            ],
            "growth_items": [
                "Data Analytics — ukończony kurs",
                "Project Management — w trakcie nauki",
                "UI/UX Design — w trakcie nauki",
            ],
            "current_work_badge": "W toku",
            "current_work_kicker": "Obecnie pracuję nad",
            "current_work_heading": "Redesign i migracja serwisu ADN Akademia",
            "current_work_lead": (
                "Prowadzę cały projekt samodzielnie, od analizy po wdrożenie: nową wersję serwisu dużej firmy szkoleniowej "
                "projektuję, koduję i wdrażam na WordPressie. Przy pracy korzystam z Cursora i narzędzi AI, co pozwala mi "
                "zrealizować projekt w około 3 tygodnie."
            ),
            "current_work_steps": [
                (
                    "Analiza",
                    "Obecny serwis, treści, ścieżki użytkownika i potrzeby firmy.",
                ),
                (
                    "Architektura informacji",
                    "Nowa mapa serwisu, schematy zakupu, voucherów i konta klienta.",
                ),
                (
                    "Wireframe’y i projekt w Figmie",
                    "Ponad 48 plansz, m.in. strona główna, katalog, karta szkolenia, koszyk, Moje konto i wersja mobilna.",
                ),
                (
                    "Kodowanie",
                    "Własny motyw i bloki Gutenberga oparte na ACF.",
                ),
                (
                    "WooCommerce",
                    "Koszyk z opcją „Zapłać teraz” lub „Tylko rezerwacja”, a w kolejnym etapie szybki zakup.",
                ),
                (
                    "Integracja z CRM",
                    "Formularze zapisu i zapytań B2B przekazujące zgłoszenia do CRM.",
                ),
                (
                    "Migracja treści i wdrożenie",
                    "Przeniesienie całej treści serwisu i publikacja.",
                ),
            ],
            "current_work_footer_before": (
                "Projekt w trakcie realizacji. Nowa wersja nie jest jeszcze opublikowana; obecny serwis: "
            ),
            "current_work_footer_link": "adnakademia.pl",
            "work_eyebrow": "Realizacje",
            "work_title": "Strony i serwisy, przy których pracowałam",
            "work_intro": (
                "Realizacje, które kodowałam samodzielnie lub wspólnie z zespołem. Przy projektach zespołowych znajdziesz odpowiednie oznaczenie."
            ),
            "work_note": (
                "Moje doświadczenie obejmuje też inne realizacje, które nie są już dostępne lub zostały później zmienione albo przeprojektowane."
            ),
            "project_ext": "Otwiera się w nowej karcie",
            "contact_eyebrow": "Kontakt",
            "contact_h2": "Porozmawiajmy o Twojej stronie",
            "contact_p": (
                "Planujesz nową stronę, sklep albo integrację? A może potrzebujesz wsparcia przy istniejącym WordPressie? "
                "Napisz, czego potrzebujesz — odpowiem."
            ),
            "contact_direct": "Napisz bezpośrednio",
            "itcommunity": "Profil na IT.Community",
            "footer_role": "Frontend / WordPress Developer",
            "footer_location": "Warszawa · stacjonarnie i online",
            "footer_copy": "© 2026 Iryna Bilous",
        }
    if lang == "en":
        pl = t("pl")
        return {
            **pl,
            "html_lang": "en",
            "title": "Iryna Bilous — Frontend / WordPress Developer",
            "meta_description": (
                "I build WordPress websites and WooCommerce stores — custom themes, integrations, and WCAG accessibility. "
                "Warsaw · on-site & online. Portfolio of Iryna Bilous."
            ),
            "nav": [
                ("About", "#o-mnie"),
                ("Skills", "#kompetencje"),
                ("Services", "#uslugi"),
                ("Experience", "#doswiadczenie"),
                ("Projects", "#realizacje"),
            ],
            "nav_aria": "Main",
            "menu_open": "Open menu",
            "menu_close": "Close menu",
            "lang_aria": "Site language",
            "cta_write": "Get in touch",
            "cta_projects": "View projects",
            "badge": "Frontend / WordPress Developer · Warsaw · on-site & online",
            "hello": "Hi, I'm Iryna",
            "hero_h1": "I build WordPress websites and online stores",
            "hero_lead": (
                "For over 10 years I've been building sites for universities, e-commerce, and service businesses: custom themes, Gutenberg blocks, "
                "WooCommerce, automations, and WCAG accessibility. I combine code with business needs analysis and product logic."
            ),
            "hero_lead_short": (
                "Custom themes, WooCommerce stores, and integrations for universities, e-commerce, and service companies — for over 10 years."
            ),
            "loc_title": "Warsaw · since 2020",
            "loc_sub": "UA · PL · EN",
            "portrait_alt": "Black and white portrait of Iryna Bilous",
            "proof": [
                ("10+", "years in web development", "WordPress, frontend and backend"),
                ("7+", "university projects", "WooCommerce, payments, InPost, public info sites"),
                ("WCAG 2.1", "accessibility certificate", "Earned in 2022"),
                ("2", "personal projects", "Built with AI tools"),
            ],
            "about_eyebrow": "About",
            "about_title": "From Kalush to Warsaw — over 10 years in web development",
            "about_paras": [
                "My name is Iryna. I come from Kalush (Ukraine), and my path in IT began in Ivano-Frankivsk, where I gained "
                "hands-on experience and knowledge working with WordPress at SP//DEV and made many friends in the industry. "
                "Since 2020 I have been living and working in Warsaw.",
                "I've been doing web development for over 10 years. I work with WordPress on the frontend and backend: websites, web applications, and various integrations. I've delivered projects across education, e-commerce, and other digital products.",
                "I love learning and discovering new things. I completed a Data Analytics course and I'm currently studying Project Management and UI/UX Design. I'm especially interested in AI-assisted programming — I experiment with tools like Cursor daily, and after hours I maintain two personal projects.",
            ],
            "facts": [
                (
                    "Location",
                    "Warsaw · on-site, hybrid & online",
                ),
                ("Languages", "Ukrainian — native\nPolish — fluent\nEnglish — intermediate"),
                ("Education", "MEng, industrial and civil engineering — Lviv Polytechnic National University, 2008–2013"),
                ("Outside work", "Mountains, cycling, boxing, travel, and surfing in warm countries. Two cats are waiting for me at home."),
            ],
            "comp_eyebrow": "Key strengths",
            "comp_title": "Code, product, and quality in one workflow",
            "comp_intro": (
                "My experience connects engineering with product work: from business requirements through feature logic "
                "to testing and maintaining live sites."
            ),
            "comp_items": [
                ("Large web ecosystems", "WordPress Multisite, multilingual sites, e-commerce, education"),
                ("Automation and integrations", "WooCommerce, payment systems, InPost, APIs and automation"),
                ("AI-assisted development", "Cursor and AI tools — faster delivery and experiments"),
                ("Product thinking and automation", "Business analysis, product logic, Trello, process automation"),
                ("WordPress engineering", "Gutenberg, ACF, CPT, PHP, JavaScript, SCSS, custom themes"),
                ("Marketing and product growth", "Campaigns, offers, calculators, UX and marketing scenarios"),
                ("Coordination and business analysis", "Team collaboration, Trello, requirements analysis, planning"),
                ("QA and technical operations", "Testing, WCAG, SEO, Git, Plesk, technical audits"),
            ],
            "serv_eyebrow": "Services",
            "serv_title": "How I can help",
            "serv_intro": "I work with companies, universities, and online stores — on new sites and on growing existing ones.",
            "serv_when": "When it’s a good fit",
            "services": [
                (
                    "Custom WordPress theme",
                    "A theme built around your content: Gutenberg blocks, ACF fields, and custom post types so your team can edit in the dashboard without code changes.",
                    "When an off-the-shelf template limits you and the site needs to evolve.",
                ),
                (
                    "WooCommerce store",
                    "Catalog, cart, online payments and InPost, plus checkout flows tailored to how your team works.",
                    "When you're launching online sales or expanding an existing store.",
                ),
                (
                    "Integrations and automation",
                    "Connecting WordPress with APIs and external services, plus automations in Google Apps Script, Trello, or Power Automate.",
                    "When the team repeats the same manual steps.",
                ),
                (
                    "Interactive tools",
                    "Calculators, forms, filters, and multilingual interfaces, plus campaign mechanics prepared with marketing.",
                    "When the site should guide choices, not only inform.",
                ),
                (
                    "Accessibility, testing, and audit",
                    "Technical audit, WCAG 2.1 implementation, technical SEO, optimization, and ongoing maintenance.",
                    "When the site has issues, loads slowly, or must meet accessibility requirements.",
                ),
                (
                    "Large site ecosystems",
                    "WordPress Multisite, multiple languages, public information portals, events and conference sites — structured multi-site setups.",
                    "When you run several sites or an organization with many departments.",
                ),
            ],
            "serv_cta": "Tell me about your project",
            "exp_eyebrow": "Experience",
            "exp_title": "Where I've worked and what I do",
            "exp_intro": "Since 2017 I've worked on WordPress sites for companies, universities, and clients in several countries.",
            "experience": [
                {
                    **pl["experience"][0],
                    "dates": "05.2024 — present",
                    "role": "Frontend / WordPress Developer",
                    "mode": "Hybrid · full-time · Warsaw",
                    "intro": "Development and maintenance of sites for education, e-commerce, services, and corporate solutions.",
                    "bullets": [
                        "Frontend and PHP: custom WordPress themes, Gutenberg blocks, WooCommerce, plugins, and API integrations",
                        "Business process automation: Google Apps Script, Trello, Power Automate, and external services",
                        "Interactive tools: calculators, forms, filters, and multilingual interfaces",
                        "Testing, optimization, technical audits, WCAG, and site maintenance",
                        "Collaboration with marketing on offers, campaigns, and user journeys",
                        "Business needs analysis, product logic, and leadership consultations",
                        "Team task coordination in Trello and workflow improvements",
                        "Cursor and AI tools in development and automation",
                    ],
                    "projects": ["akademiata.pl", "uni-munich.de", "unixedu.com", "and many other sites"],
                },
                {
                    **pl["experience"][1],
                    "dates": "03.2021 — 08.2024",
                    "co": "VIZJA University",
                    "role": "Frontend Developer",
                    "mode": "Warsaw",
                    "intro": "Over three years developing sites for the Academy of Economic and Humanistic Sciences in Warsaw, now VIZJA University.",
                    "bullets": [
                        "WordPress Multisite, PHP, JavaScript, HTML, CSS, ACF, and WooCommerce",
                        "Custom themes, features, and responsive interfaces",
                        "Payment systems and InPost integrations",
                        "Process automation, performance, audits, and WCAG standards",
                        "Planning structure, UI/UX, and features for new and existing sites",
                        "Collaboration with leadership, marketing, admissions, and administration",
                        "One year on frontend in an EU project run by the university",
                    ],
                    "projects": pl["experience"][1]["projects"],
                },
                {
                    **pl["experience"][2],
                    "dates": "2017 — 2021",
                    "role": "Frontend / WordPress Developer",
                    "mode": "International clients",
                    "intro": "WordPress deliveries for clients in France, the Netherlands, and beyond.",
                    "bullets": [
                        "Service, education, and e-commerce websites",
                        "Theme implementation and responsive layouts",
                        "Ongoing maintenance and site evolution",
                    ],
                },
            ],
            "skills_eyebrow": "Skills",
            "skills_title": "Technologies and tools",
            "skills": [
                ("CMS & e-commerce", pl["skills"][0][1]),
                ("Frontend", ["HTML", "CSS / SCSS", "JavaScript", "Responsive design", "Multilingual interfaces"]),
                ("Backend & integrations", pl["skills"][2][1]),
                ("Quality", ["WCAG 2.1", "Testing", "Technical audits", "SEO", "Performance"]),
                ("Toolkit", pl["skills"][4][1]),
            ],
            "learn_certs": "Certificates",
            "learn_growth": "Learning",
            "cert_items": [
                "WCAG 2.1 — web accessibility, 2022",
                "Front-end Web — IT Cluster Academy, 2017",
                "JavaScript + Angular — IT Cluster Academy, 2019",
            ],
            "growth_items": [
                "Data Analytics — completed course",
                "Project Management — in progress",
                "UI/UX Design — in progress",
            ],
            "current_work_badge": "In progress",
            "current_work_kicker": "Currently working on",
            "current_work_heading": "Redesign and migration of the ADN Akademia website",
            "current_work_lead": (
                "I'm running the whole project on my own, from analysis through launch: I design, build, and implement on "
                "WordPress a new version of a major training company's website. I use Cursor and AI tools in my work, which "
                "helps me deliver the project in about three weeks."
            ),
            "current_work_steps": [
                (
                    "Analysis",
                    "The current site, content, user journeys, and the company's needs.",
                ),
                (
                    "Information architecture",
                    "A new site map and flows for purchasing, vouchers, and the customer account.",
                ),
                (
                    "Wireframes and design in Figma",
                    "More than 48 screens, including homepage, catalogue, course page, cart, My account, and the mobile version.",
                ),
                (
                    "Development",
                    "A custom theme and Gutenberg blocks built on ACF.",
                ),
                (
                    "WooCommerce",
                    "Cart checkout with “Pay now” or “Reservation only”; quick purchase in the next phase.",
                ),
                (
                    "CRM integration",
                    "Registration and B2B enquiry forms that pass submissions to the CRM.",
                ),
                (
                    "Content migration and launch",
                    "Migrating all site content and going live.",
                ),
            ],
            "current_work_footer_before": (
                "Project in progress. The new version is not published yet; current site: "
            ),
            "current_work_footer_link": "adnakademia.pl",
            "work_eyebrow": "Projects",
            "work_title": "Sites I've worked on",
            "work_intro": "Projects I coded independently or with a team. Team projects are labelled accordingly.",
            "work_note": (
                "My experience also includes other projects that are no longer available or were later changed or redesigned."
            ),
            "project_ext": "Opens in a new tab",
            "contact_eyebrow": "Contact",
            "contact_h2": "Let's talk about your website",
            "contact_p": pl["contact_p"].replace(
                "Planujesz nową stronę, sklep albo integrację? A może potrzebujesz wsparcia przy istniejącym WordPressie? Napisz, czego potrzebujesz — odpowiem.",
                "Planning a new site, store, or integration? Or need help with an existing WordPress setup? Write what you need — I'll reply.",
            ),
            "contact_direct": "Write directly",
            "itcommunity": "Profile on IT.Community",
            "footer_role": "Frontend / WordPress Developer",
            "footer_location": "Warsaw · on-site & online",
            "footer_copy": "© 2026 Iryna Bilous",
        }
    # Ukrainian
    pl = t("pl")
    return {
        **pl,
        "html_lang": "uk",
        "title": "Iryna Bilous — Frontend / WordPress Developer",
        "meta_description": (
            "Створюю сайти та інтернет-магазини на WordPress — власні теми, WooCommerce, інтеграції та доступність WCAG. "
            "Варшава · офлайн і онлайн. Портфоліо Ірини Білоус."
        ),
        "nav": [
            ("Про мене", "#o-mnie"),
            ("Компетенції", "#kompetencje"),
            ("Послуги", "#uslugi"),
            ("Досвід", "#doswiadczenie"),
            ("Реалізації", "#realizacje"),
        ],
        "nav_aria": "Головне",
        "menu_open": "Відкрити меню",
        "menu_close": "Закрити меню",
        "lang_aria": "Мова сайту",
        "cta_write": "Напишіть мені",
        "cta_projects": "Переглянути реалізації",
        "badge": "Frontend / WordPress Developer · Варшава · офлайн і онлайн",
        "hello": "Привіт, я Ірина",
        "hero_h1": "Створюю сайти та інтернет-магазини на WordPress",
        "hero_lead": (
            "Понад 10 років я розробляю сервіси для університетів, e-commerce та сервісних компаній: власні теми, блоки Gutenberg, "
            "WooCommerce, автоматизації та доступність WCAG. Поєдную код із аналізом бізнес-потреб і продуктовою логікою."
        ),
        "hero_lead_short": (
            "Власні теми, магазини WooCommerce та інтеграції для університетів, e-commerce і сервісних фірм — понад 10 років."
        ),
        "loc_title": "Варшава · з 2020",
        "loc_sub": "UA · PL · EN",
        "portrait_alt": "Чорно-білий портрет Ірини Білоус",
        "proof": [
            ("10+", "років у веброзробці", "WordPress, frontend і backend"),
            ("7+", "проєктів для університетів", "WooCommerce, платежі, InPost, BIP"),
            ("WCAG 2.1", "сертифікат доступності", "Отримано у 2022 році"),
            ("2", "власні проєкти", "Розвиваю з інструментами ШІ"),
        ],
        "about_eyebrow": "Про мене",
        "about_title": "Від Калуша до Варшави — понад 10 років у веброзробці",
        "about_paras": [
            "Мене звати Ірина. Я родом з Калуша (Україна), а мій шлях в IT почався в Івано-Франківську, "
            "де в компанії SP//DEV я здобувала практику і знання, працюючи з WordPress, і знайшла багато друзів у галузі. "
            "З 2020 року живу і працюю у Варшаві.",
            "Веброзробкою займаюся понад 10 років. Працюю з WordPress на фронтенді та бекенді: сайти, вебзастосунки та різні інтеграції. Реалізувала проєкти в освіті, e-commerce та інших цифрових продуктах.",
            "Люблю вчитися й відкривати нове. Завершила курс Data Analytics, зараз вивчаю Project Management і UI/UX Design. Особливо цікавить ШІ в програмуванні — щодня експериментую з інструментами на кшталт Cursor, а після роботи розвиваю два власні проєкти.",
        ],
        "facts": [
            (
                "Локація",
                "Варшава · офіс, гібрид і онлайн",
            ),
            ("Мови", "українська — рідна\nпольська — вільно\nанглійська — середній рівень"),
            ("Освіта", "Магістр, промислове та цивільне будівництво — Львівська політехніка, 2008–2013"),
            ("Поза роботою", "Гори, велосипед, бокс, подорожі та серфінг у теплих країнах. Вдома чекають два коти."),
        ],
        "comp_eyebrow": "Ключові компетенції",
        "comp_title": "Код, продукт і якість в одному процесі",
        "comp_intro": "Мій досвід поєднує програмування з продуктовою роботою: від бізнес-вимог через логіку функцій до тестів і підтримки готового сервісу.",
        "comp_items": [
            ("Великі вебекосистеми", "WordPress Multisite, багатомовність, e-commerce, освіта"),
            ("Автоматизація та інтеграції", "WooCommerce, платіжні системи, InPost, API та автоматизація"),
            ("Розробка з підтримкою ШІ", "Cursor і ШІ-інструменти — швидша розробка та експерименти"),
            ("Продуктове мислення та автоматизація", "Бізнес-аналіз, продуктова логіка, Trello, автоматизація процесів"),
            ("Інженерія WordPress", "Gutenberg, ACF, CPT, PHP, JavaScript, SCSS, власні теми"),
            ("Маркетинг і розвиток продукту", "Акції, пропозиції, калькулятори, UX і маркетингові сценарії"),
            ("Координація та бізнес-аналіз", "Робота з командою, Trello, аналіз вимог, планування"),
            ("QA та технічні операції", "Тести, WCAG, SEO, Git, Plesk, технічні аудити"),
        ],
        "serv_eyebrow": "Послуги",
        "serv_title": "Чим можу допомогти",
        "serv_intro": "Працюю з компаніями, університетами та інтернет-магазинами — над новими сайтами та розвитком існуючих.",
        "serv_when": "Коли це доречно",
        "services": [
            (
                "Власна тема WordPress",
                "Тема під ваш контент: блоки Gutenberg, поля ACF і власні типи записів, щоб команда редагувала в панелі без змін у коді.",
                "Коли готовий шаблон обмежує, а сайт має розвиватися.",
            ),
            (
                "Магазин на WooCommerce",
                "Каталог, кошик, онлайн-платежі та InPost, а також процес замовлення під вашу команду.",
                "Коли запускаєте онлайн-продаж або розширюєте наявний магазин.",
            ),
            (
                "Інтеграції та автоматизація",
                "Підключення WordPress до API та зовнішніх сервісів, автоматизації в Google Apps Script, Trello чи Power Automate.",
                "Коли команда вручну повторює однакові дії.",
            ),
            (
                "Інтерактивні інструменти",
                "Калькулятори, форми, фільтри та багатомовні інтерфейси, механіки акцій разом із маркетингом.",
                "Коли сайт має допомагати обирати, а не лише інформувати.",
            ),
            (
                "Доступність, тести та аудит",
                "Технічний аудит, WCAG 2.1, технічне SEO, оптимізація та поточна підтримка.",
                "Коли на сайті є помилки, він повільний або має відповідати вимогам доступності.",
            ),
            (
                "Розширення великих сервісів",
                "WordPress Multisite, кілька мов, BIP, події та конференції — впорядкована структура багатьох сайтів.",
                "Коли ведете кілька сайтів або організацію з багатьма відділами.",
            ),
        ],
        "serv_cta": "Розкажіть про свій проєкт",
        "exp_eyebrow": "Досвід",
        "exp_title": "Де працювала і чим займалася",
        "exp_intro": "З 2017 року працюю над сайтами WordPress для фірм, університетів і клієнтів з кількох країн.",
        "experience": [
            {
                **pl["experience"][0],
                "dates": "05.2024 — донині",
                "role": "Frontend / WordPress Developer",
                "mode": "Гібридно · повна зайнятість · Варшава",
                "intro": "Розвиток і підтримка сервісів для освіти, e-commerce, послуг і корпоративних рішень.",
                "bullets": [
                    "Frontend і PHP: власні теми WordPress, блоки Gutenberg, WooCommerce, плагіни та інтеграції API",
                    "Автоматизація бізнес-процесів: Google Apps Script, Trello, Power Automate та зовнішні сервіси",
                    "Інтерактивні інструменти: калькулятори, форми, фільтри та багатомовні інтерфейси",
                    "Тести, оптимізація, технічні аудити, WCAG і підтримка сайтів",
                    "Співпраця з маркетингом над пропозиціями, акціями та сценаріями користувача",
                    "Аналіз бізнес-потреб, продуктова логіка та консультації з керівництвом",
                    "Координація завдань команди в Trello та покращення робочих процесів",
                    "Cursor і ШІ-інструменти в програмуванні та автоматизації",
                ],
                "projects": ["akademiata.pl", "uni-munich.de", "unixedu.com", "та багато інших сервісів"],
            },
            {
                **pl["experience"][1],
                "dates": "03.2021 — 08.2024",
                "co": "Університет VIZJA",
                "role": "Frontend Developer",
                "mode": "Варшава",
                "intro": "Понад три роки розвитку сервісів Академії економічно-гуманітарної у Варшаві, нині Університету VIZJA.",
                "bullets": [
                    "WordPress Multisite, PHP, JavaScript, HTML, CSS, ACF і WooCommerce",
                    "Власні теми, функціональність і адаптивні інтерфейси",
                    "Інтеграції платіжних систем та InPost",
                    "Автоматизація, продуктивність, аудити та впровадження WCAG",
                    "Планування структури, UI/UX і функцій нових та наявних сервісів",
                    "Співпраця з керівництвом, маркетингом, рекрутингом і адміністрацією",
                    "Рік на фронтенді в європейському проєкті університету",
                ],
                "projects": pl["experience"][1]["projects"],
            },
            {
                **pl["experience"][2],
                "dates": "2017 — 2021",
                "role": "Frontend / WordPress Developer",
                "mode": "Міжнародні клієнти",
                "intro": "Реалізації WordPress для клієнтів зокрема з Франції та Нідерландів.",
                "bullets": [
                    "Сервісні, освітні та e-commerce сайти",
                    "Впровадження тем і адаптивні макети",
                    "Поточна підтримка та розвиток сайтів клієнтів",
                ],
            },
        ],
        "skills_eyebrow": "Навички",
        "skills_title": "Технології та інструменти",
        "skills": [
            ("CMS і e-commerce", pl["skills"][0][1]),
            ("Frontend", ["HTML", "CSS / SCSS", "JavaScript", "RWD", "Багатомовні інтерфейси"]),
            ("Backend і інтеграції", pl["skills"][2][1]),
            ("Якість", pl["skills"][3][1]),
            ("Майстерня", pl["skills"][4][1]),
        ],
        "learn_certs": "Сертифікати",
        "learn_growth": "Розвиток",
        "cert_items": [
            "WCAG 2.1 — доступність сайтів, 2022",
            "Front-end Web — IT Cluster Academy, 2017",
            "JavaScript + Angular — IT Cluster Academy, 2019",
        ],
        "growth_items": [
            "Data Analytics — завершений курс",
            "Project Management — у процесі навчання",
            "UI/UX Design — у процесі навчання",
        ],
        "current_work_badge": "У роботі",
        "current_work_kicker": "Зараз працюю над",
        "current_work_heading": "Редизайн і міграція сайту ADN Akademia",
        "current_work_lead": (
            "Веду весь проєкт самостійно, від аналізу до запуску: нову версію сайту великої навчальної компанії проєктую, "
            "кодую й впроваджую на WordPress. У роботі користуюся Cursor і ШІ-інструментами, що дозволяє реалізувати "
            "проєкт приблизно за 3 тижні."
        ),
        "current_work_steps": [
            (
                "Аналіз",
                "Поточний сайт, контент, користувацькі шляхи та потреби компанії.",
            ),
            (
                "Інформаційна архітектура",
                "Нова карта сайту, схеми покупки, ваучерів і облікового запису клієнта.",
            ),
            (
                "Вайрфрейми та дизайн у Figma",
                "Понад 48 макетів: головна, каталог, картка тренінгу, кошик, Мій обліковий запис і мобільна версія.",
            ),
            (
                "Кодування",
                "Власна тема й блоки Gutenberg на основі ACF.",
            ),
            (
                "WooCommerce",
                "Кошик з опцією «Сплатити зараз» або «Лише резервація»; на наступному етапі — швидка покупка.",
            ),
            (
                "Інтеграція з CRM",
                "Форми запису та B2B-запитів, що передають звернення в CRM.",
            ),
            (
                "Міграція контенту й запуск",
                "Перенесення всього контенту сайту та публікація.",
            ),
        ],
        "current_work_footer_before": (
            "Проєкт у процесі реалізації. Нова версія ще не опублікована; поточний сайт: "
        ),
        "current_work_footer_link": "adnakademia.pl",
        "work_eyebrow": "Реалізації",
        "work_title": "Сайти, над якими працювала",
        "work_intro": "Реалізації, які кодувала самостійно або з командою. Командні проєкти позначені відповідно.",
        "work_note": (
            "Мій досвід також охоплює інші реалізації, які вже недоступні або були пізніше змінені чи перероблені."
        ),
        "project_ext": "Відкривається в новій вкладці",
        "contact_eyebrow": "Контакт",
        "contact_h2": "Поговорімо про ваш сайт",
        "contact_p": "Плануєте новий сайт, магазин чи інтеграцію? Або потрібна підтримка наявного WordPress? Напишіть, що вам потрібно — відповім.",
        "contact_direct": "Напишіть напряму",
        "itcommunity": "Профіль на IT.Community",
        "footer_role": "Frontend / WordPress Developer",
        "footer_location": "Варшава · офлайн і онлайн",
        "footer_copy": "© 2026 Iryna Bilous",
    }


def e(s: str) -> str:
    return html.escape(s, quote=True)


def compile_css() -> None:
    """Compile SCSS → CSS (source of truth for Pages)."""
    subprocess.run(
        [
            "npx",
            "sass",
            str(SCSS_ENTRY),
            str(CSS_PATH),
            "--style=compressed",
        ],
        cwd=ROOT,
        check=True,
    )


def css_cache_bust() -> str:
    digest = hashlib.sha256(CSS_PATH.read_bytes()).hexdigest()
    return digest[:10]


def verify_html_classes_in_css() -> None:
    css = CSS_PATH.read_text(encoding="utf-8")
    classes: set[str] = set()
    for rel in ("index.html", "en/index.html", "ua/index.html"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for m in re.finditer(r'\bclass="([^"]*)"', text):
            classes.update(m.group(1).split())
    missing = []
    for name in sorted(classes):
        if not re.search(r"\." + re.escape(name) + r"(?:[,\s\.#\[{>+~:_-]|$)", css):
            missing.append(name)
    if missing:
        raise RuntimeError(f"CSS missing classes used in HTML: {', '.join(missing)}")


def parse_last_updated(value: str) -> date:
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return date.fromisoformat(value)
    raise ValueError(f"Invalid date (use YYYY-MM-DD): {value!r}")


def resolve_last_updated() -> date:
    env_val = os.environ.get(LAST_UPDATED_ENV, "").strip()
    if env_val:
        return parse_last_updated(env_val)
    meta_val = (SITE_META.get("last_updated") or "").strip()
    if meta_val:
        return parse_last_updated(meta_val)
    return datetime.now(WARSAW).date()


def format_last_updated_human(lang: str, d: date) -> str:
    day, month, year = d.day, d.month, d.year
    if lang == "pl":
        return f"{day} {MONTH_PL_GENITIVE[month - 1]} {year}"
    if lang == "ua":
        return f"{day} {MONTH_UA_GENITIVE[month - 1]} {year}"
    return f"{day} {MONTH_EN[month - 1]} {year}"


def last_updated_footer_html(lang: str, d: date) -> str:
    labels = {
        "pl": "Ostatnia aktualizacja:",
        "en": "Last updated:",
        "ua": "Останнє оновлення:",
    }
    human = format_last_updated_human(lang, d)
    return (
        f'{e(labels[lang])} <time datetime="{d.isoformat()}">{e(human)}</time>'
    )


def asset_prefix(lang: str) -> str:
    return "../" if lang in ("en", "ua") else ""


def page_paths(lang: str) -> dict[str, str]:
    if lang == "pl":
        return {"pl": "./", "en": "en/", "ua": "ua/", "canonical": f"{SITE}/"}
    if lang == "en":
        return {"pl": "../", "en": "./", "ua": "../ua/", "canonical": f"{SITE}/en/"}
    return {"pl": "../", "en": "../en/", "ua": "./", "canonical": f"{SITE}/ua/"}


TEAM_I18N = {
    "Projekt zespołowy": {"en": "Team project", "ua": "Командний проєкт"},
}

CARD_NOTE_I18N = {
    "not_launched": {
        "pl": "Projekt nie wystartował",
        "en": "Project not launched",
        "ua": "Проєкт не запущено",
    },
}


def team_label(team: str | None, lang: str) -> str | None:
    if not team:
        return None
    if lang == "pl":
        return team
    return TEAM_I18N.get(team, {}).get(lang, team)


def card_note_label(note: str | None, lang: str) -> str | None:
    if not note:
        return None
    return CARD_NOTE_I18N.get(note, {}).get(lang if lang != "ua" else "ua")


def gallery_html(lang: str, ap: str, copy: dict) -> str:
    chunks = []
    for period in ("avista", "vizja", "spdev"):
        chunks.append(f'<h3 class="period-heading">{e(PERIOD_LABELS[lang][period])}</h3>')
        chunks.append('<div class="gallery-grid">')
        for p in PROJECTS[period]:
            thumb = f'{ap}assets/img/previews/{e(p["host"])}.webp'
            title = e(p["title"])
            host = e(p["host"])
            url = e(p["url"])
            team = team_label(p.get("team"), lang)
            note = card_note_label(p.get("card_note"), lang)
            badge_html = ""
            if team:
                badge_html += f'<span class="team">{e(team)}</span>'
            if note:
                badge_html += f'<span class="team">{e(note)}</span>'
            alt = e(f'{p["title"]} — podgląd strony {p["host"]}' if lang == 'pl' else (
                f'{p["title"]} — preview of {p["host"]}' if lang == 'en' else f'{p["title"]} — перегляд {p["host"]}'
            ))
            chunks.append(
                f'<a class="project-card" href="{url}" target="_blank" rel="noopener noreferrer">'
                f'<motion aria-hidden="true" class="thumb">'
                f'<img src="{thumb}" alt="{alt}" width="640" height="357" loading="lazy" decoding="async">'
                f"</motion>"
                f"<h3>{title}</h3>"
                f'<p class="host">{host}</p>{badge_html}'
                f'<span class="sr-only"> — {e(copy["project_ext"])}</span>'
                f"</a>"
            )
        chunks.append("</div>")
    return "\n".join(chunks).replace("<motion", "<div").replace("</motion>", "</div>")


def lang_switch_html(paths: dict[str, str], current: str) -> str:
    chunks = []
    for code, label in (("pl", "PL"), ("en", "EN"), ("ua", "UA")):
        href = paths[code]
        if code == current:
            chunks.append(f'<span aria-current="page">{label}</span>')
        else:
            chunks.append(
                f'<a href="{e(href)}" hreflang="{code if code != "ua" else "uk"}" '
                f'lang="{code if code != "ua" else "uk"}">{label}</a>'
            )
    return "".join(chunks)


def page(lang: str, css_ver: str, last_updated: date) -> str:
    copy = t(lang)
    ap = asset_prefix(lang)
    paths = page_paths(lang)
    current = {"pl": "pl", "en": "en", "ua": "ua"}[lang]

    nav_items = "".join(f'<li><a href="{e(h)}">{e(l)}</a></li>' for l, h in copy["nav"])
    nav_desktop = "".join(f'<a href="{e(h)}">{e(l)}</a>' for l, h in copy["nav"])
    nav_mobile = "".join(f'<a href="{e(h)}">{e(l)}</a>' for l, h in copy["nav"])

    lang_links = lang_switch_html(paths, current)

    proof_cards = ""
    for i, (n, label, sub) in enumerate(copy["proof"]):
        tile = "sky" if i % 2 == 0 else "pink"
        color = BLUE if tile == "sky" else PINK
        icon = stroke_icon(PROOF_ICON_KEYS[i], color=color, size=22)
        proof_cards += f"""<article class="proof-card">
          <div class="proof-head">
            <span class="proof-tile proof-tile--{tile}" aria-hidden="true">{icon}</span>
            <p class="num">{e(n)}</p>
          </div>
          <p class="label">{e(label)}</p>
          <p class="sub">{e(sub)}</p>
        </article>"""

    about_paras = ""
    for i, p in enumerate(copy["about_paras"]):
        cls = "lead-para" if i == 0 else "muted-para"
        about_paras += f'<p class="{cls}">{e(p)}</p>'

    facts = ""
    for fi, (label, val) in enumerate(copy["facts"]):
        icon = stroke_icon(FACT_ICON_KEYS[fi], color=PINK, size=22)
        facts += f"""<article class="fact"><div class="ico">{icon}</div>
          <p class="label">{e(label)}</p>
          <p class="value">{e(val).replace(chr(10), "<br>")}</p></article>"""

    comp_items = ""
    for i, (title, desc) in enumerate(copy["comp_items"]):
        icon = stroke_icon(COMP_ICON_KEYS[i], color=comp_icon_color(i), size=26)
        comp_items += f"""<article class="item"><div class="ico">{icon}</div>
          <div><h3>{e(title)}</h3><p>{e(desc)}</p></div></article>"""

    current_work_steps = ""
    for i, (title, desc) in enumerate(copy["current_work_steps"], 1):
        num = f"{i:02d}"
        current_work_steps += f"""<li class="current-work-step">
          <span class="step-num" aria-hidden="true">{num}</span>
          <div class="step-body">
            <h3 class="step-title">{e(title)}</h3>
            <p class="step-desc">{e(desc)}</p>
          </div>
        </li>"""

    services = ""
    for i, (title, desc, when) in enumerate(copy["services"], 1):
        bg = "bg-pink-soft" if i % 2 else "bg-sky-soft"
        services += f"""<article class="service-card">
          <motion class="top"><div class="ico {bg}" aria-hidden="true">{i:02d}</div><span class="num">{i:02d}</span></motion>
          <h3>{e(title)}</h3>
          <p class="desc">{e(desc)}</p>
          <p class="when-label">{e(copy["serv_when"])}</p>
          <p class="when">{e(when)}</p>
        </article>"""

    exp_cards = ""
    for job in copy["experience"]:
        bullets = "".join(f"<li>{e(b)}</li>" for b in job["bullets"])
        tags = ""
        if job.get("projects"):
            tags = '<div class="project-tags">' + "".join(f"<span>{e(pr)}</span>" for pr in job["projects"]) + "</div>"
        exp_cards += f"""<article class="exp-card">
          <motion>
            <span class="dates">{e(job["dates"])}</span>
            <h3 class="company">{e(job["co"])}</h3>
            <p class="role">{e(job["role"])}</p>
            <p class="mode">{e(job["mode"])}</p>
          </motion>
          <motion>
            <p>{e(job["intro"])}</p>
            <ul>{bullets}</ul>{tags}
          </motion>
        </article>"""

    skill_rows = ""
    for cat, items in copy["skills"]:
        tags = "".join(f"<span>{e(it)}</span>" for it in items)
        skill_rows += f'<div class="skill-row"><p class="cat">{e(cat)}</p><div class="tags">{tags}</div></div>'

    cert_li = "".join(f"<li><span aria-hidden=\"true\">✓</span> {e(c)}</li>" for c in copy["cert_items"])
    growth_li = "".join(f"<li><span aria-hidden=\"true\">✓</span> {e(g)}</li>" for g in copy["growth_items"])

    portrait_src = f"{ap}assets/img/portraits/iryna-bw.webp"
    portrait_srcset = (
        f'{ap}assets/img/portraits/iryna-bw-456.webp 456w, '
        f'{ap}assets/img/portraits/iryna-bw-912.webp 912w'
    )

    hreflang = f"""
  <link rel="alternate" hreflang="pl" href="{SITE}/">
  <link rel="alternate" hreflang="en" href="{SITE}/en/">
  <link rel="alternate" hreflang="uk" href="{SITE}/ua/">
  <link rel="alternate" hreflang="x-default" href="{SITE}/">"""

    return f"""<!DOCTYPE html>
<html lang="{copy['html_lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{e(copy['meta_description'])}">
  <title>{e(copy['title'])}</title>
  <link rel="canonical" href="{paths['canonical']}">
{hreflang}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&family=Syne:wght@600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{ap}assets/css/main.css?v={css_ver}">
</head>
<body>
  <a class="skip-link" href="#main">{e('Przejdź do treści' if lang=='pl' else ('Skip to content' if lang=='en' else 'Перейти до змісту'))}</a>
  <header class="site-header" id="top">
    <div class="container header-inner">
      <a class="logo" href="{ap if lang!='pl' else './'}#top">Iryna Bilous</a>
      <nav class="nav-desktop" aria-label="{e(copy['nav_aria'])}">{nav_desktop}</nav>
      <div class="header-actions">
        <nav aria-label="{e(copy['lang_aria'])}"><ul class="lang-switch">{lang_links}</ul></nav>
        <a class="btn btn--primary btn-header" href="#kontakt">{e(copy['cta_write'])}</a>
        <button type="button" class="menu-toggle" aria-expanded="false" aria-controls="nav-mobile" data-menu-toggle>
          <span class="sr-only" data-open="{e(copy['menu_open'])}" data-close="{e(copy['menu_close'])}">{e(copy['menu_open'])}</span>
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
    <div class="nav-mobile-wrap" id="nav-mobile" data-nav-mobile hidden>
      <button type="button" class="nav-mobile-backdrop" data-menu-backdrop aria-label="{e(copy['menu_close'])}"></button>
      <div class="nav-mobile-panel">
        <nav class="nav-mobile" aria-label="{e(copy['nav_aria'])} mobile">{nav_mobile}</nav>
        <div class="nav-mobile-footer">
          <nav aria-label="{e(copy['lang_aria'])}"><ul class="lang-switch lang-switch--menu">{lang_links}</ul></nav>
          <a class="btn btn--primary nav-mobile-cta" href="#kontakt">{e(copy['cta_write'])}</a>
        </div>
      </div>
    </div>
  </header>
  <main id="main">
    <section class="section section--hero" id="hero" aria-labelledby="hero-title">
      <div class="container">
        <motion class="hero-grid">
          <motion class="hero-main">
            <p class="badge-pill"><span class="dot" aria-hidden="true"></span>{e(copy['badge'])}</p>
            <p class="hero-greeting">{e(copy['hello'])}</p>
            <h1 class="hero-title" id="hero-title">{e(copy['hero_h1'])}</h1>
            <p class="hero-lead"><span class="lead-full">{e(copy['hero_lead'])}</span><span class="lead-short">{e(copy['hero_lead_short'])}</span></p>
            <div class="hero-ctas">
              <a class="btn btn--primary" href="mailto:{EMAIL}">{e(copy['cta_write'])} <span aria-hidden="true">→</span></a>
              <a class="btn btn--ghost" href="#realizacje">{e(copy['cta_projects'])}</a>
            </div>
            <motion class="hero-contacts">
              <a class="email" href="mailto:{EMAIL}"><span class="icon text-pink" aria-hidden="true">✉</span>{EMAIL}</a>
              <a class="linkedin" href="{LINKEDIN}" target="_blank" rel="noopener noreferrer"><span class="icon" aria-hidden="true">in</span> LinkedIn</a>
            </motion>
          </motion>
          <div class="hero-portrait">
            <motion class="frame">
              <div class="portrait-wrap">
                <img src="{portrait_src}" srcset="{portrait_srcset}" sizes="(max-width: 899px) 100vw, 456px" width="456" height="536" alt="{e(copy['portrait_alt'])}" fetchpriority="high" decoding="async">
              </motion>
              <motion class="loc-card">
                <p class="title"><span class="pin" aria-hidden="true">📍</span>{e(copy['loc_title'])}</p>
                <p class="sub">{e(copy['loc_sub'])}</p>
              </motion>
            </div>
          </div>
        </div>
        <div class="proof-grid" aria-label="Highlights">{proof_cards}</div>
      </div>
    </section>

    <section class="section" id="o-mnie" aria-labelledby="about-title">
      <div class="container">
        <span class="eyebrow">{e(copy['about_eyebrow'])}</span>
        <h2 class="section-title" id="about-title">{e(copy['about_title'])}</h2>
        <div class="about-layout">
          <div class="about-copy">{about_paras}</div>
          <aside class="facts-panel" aria-label="Facts">{facts}</aside>
        </div>
      </div>
    </section>

    <section class="section section--tint" id="kompetencje" aria-labelledby="comp-title">
      <div class="container">
        <span class="eyebrow">{e(copy['comp_eyebrow'])}</span>
        <h2 class="section-title" id="comp-title">{e(copy['comp_title'])}</h2>
        <p class="section-intro">{e(copy['comp_intro'])}</p>
        <div class="comp-list">{comp_items}</div>
      </div>
    </section>

    <section class="section" id="uslugi" aria-labelledby="serv-title">
      <h2 class="sr-only" id="serv-title">{e(copy['serv_title'])}</h2>
      <motion class="container">
        <span class="eyebrow">{e(copy['serv_eyebrow'])}</span>
        <h2 class="section-title">{e(copy['serv_title'])}</h2>
        <p class="section-intro">{e(copy['serv_intro'])}</p>
        <div class="services-grid" style="margin-top:40px">{services}</div>
        <p class="services-cta"><a class="btn btn--primary" href="#kontakt">{e(copy['serv_cta'])}</a></p>
      </motion>
    </section>

    <section class="section section--sky" id="doswiadczenie" aria-labelledby="exp-title">
      <div class="container">
        <span class="eyebrow">{e(copy['exp_eyebrow'])}</span>
        <h2 class="section-title" id="exp-title">{e(copy['exp_title'])}</h2>
        <p class="section-intro">{e(copy['exp_intro'])}</p>
        <motion class="exp-stack" style="margin-top:40px">{exp_cards}</div>
      </motion>
    </section>

    <section class="section" id="umiejetnosci" aria-labelledby="skills-title">
      <div class="container skills-layout">
        <motion>
          <span class="eyebrow">{e(copy['skills_eyebrow'])}</span>
          <h2 class="section-title" id="skills-title">{e(copy['skills_title'])}</h2>
          {skill_rows}
        </motion>
        <div class="learn-cards">
          <article class="learn-card">
            <h3>{e(copy['learn_certs'])}</h3>
            <ul>{cert_li}</ul>
          </article>
          <article class="learn-card">
            <h3>{e(copy['learn_growth'])}</h3>
            <ul>{growth_li}</ul>
          </article>
        </div>
      </div>
    </section>

    <section class="section section--sky" id="w-toku" aria-labelledby="current-work-heading">
      <div class="container">
        <article class="current-work-card">
          <span class="current-work-badge">{e(copy['current_work_badge'])}</span>
          <p class="current-work-kicker">{e(copy['current_work_kicker'])}</p>
          <h2 class="current-work-title" id="current-work-heading">{e(copy['current_work_heading'])}</h2>
          <p class="current-work-lead">{e(copy['current_work_lead'])}</p>
          <ol class="current-work-steps">{current_work_steps}</ol>
          <p class="current-work-footer">
            {e(copy['current_work_footer_before'])}
            <a href="{ADN_AKADEMIA_URL}" target="_blank" rel="noopener noreferrer">{e(copy['current_work_footer_link'])}</a>
          </p>
        </article>
      </div>
    </section>

    <section class="section section--tint" id="realizacje" aria-labelledby="work-title">
      <div class="container">
        <span class="eyebrow">{e(copy['work_eyebrow'])}</span>
        <h2 class="section-title" id="work-title">{e(copy['work_title'])}</h2>
        <p class="section-intro">{e(copy['work_intro'])}</p>
        {gallery_html(lang if lang != 'ua' else 'ua', ap, copy)}
        <aside class="work-note" role="note">
          <span class="icon text-pink" aria-hidden="true">ℹ</span>
          <p>{e(copy['work_note'])}</p>
        </aside>
      </div>
    </section>

    <section class="section" id="kontakt" aria-labelledby="contact-title">
      <div class="container contact-section">
        <motion>
          <span class="eyebrow" style="color:#fff;opacity:.85">{e(copy['contact_eyebrow'])}</span>
          <h2 id="contact-title">{e(copy['contact_h2'])}</h2>
          <p>{e(copy['contact_p'])}</p>
        </motion>
        <motion class="contact-actions">
          <p class="direct-label">{e(copy['contact_direct'])}</p>
          <a class="email-lg" href="mailto:{EMAIL}">{EMAIL}</a>
          <a class="btn btn--on-pink" href="mailto:{EMAIL}">{e(copy['cta_write'])}</a>
          <a class="btn btn--ghost-light" href="{IT_COMMUNITY}" target="_blank" rel="noopener noreferrer">{e(copy['itcommunity'])}</a>
          <a class="btn btn--ghost-light" href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
        </motion>
      </motion>
    </section>
  </main>
  <footer class="site-footer">
    <div class="container footer-inner">
      <p class="name">Iryna Bilous</p>
      <p class="meta">{e(copy['footer_role'])}</p>
      <p class="meta">{e(copy['footer_location'])}</p>
      <motion class="footer-end">
        <p class="copy">{e(copy['footer_copy'])} · <a href="mailto:{EMAIL}">{EMAIL}</a></p>
        <p class="copy footer-updated">{last_updated_footer_html(lang, last_updated)}</p>
      </motion>
    </div>
  </footer>
  <script src="{ap}assets/js/main.js" defer></script>
</body>
</html>""".replace("<motion", "<div").replace("</motion>", "</div>")


def main():
    compile_css()
    css_ver = css_cache_bust()
    last_updated = resolve_last_updated()
    (ROOT / "index.html").write_text(page("pl", css_ver, last_updated), encoding="utf-8")
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "ua").mkdir(exist_ok=True)
    (ROOT / "en/index.html").write_text(page("en", css_ver, last_updated), encoding="utf-8")
    (ROOT / "ua/index.html").write_text(page("ua", css_ver, last_updated), encoding="utf-8")
    verify_html_classes_in_css()
    print(f"Generated HTML (main.css?v={css_ver}, {CSS_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
