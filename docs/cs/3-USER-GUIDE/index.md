# Uživatelská příručka – jak používat Open Notebook

Postupy krok za krokem pro každou funkci. Pokud chcete nejdřív pochopit, jak věci fungují (sešity, zdroje, poznatky, úrovně kontextu), přečtěte si [Základní pojmy](../2-CORE-CONCEPTS/index.md).

---

## Než začnete

Open Notebook potřebuje alespoň jednoho poskytovatele AI a výchozí modely. Podle návodu [Poskytovatelé AI → Připojení poskytovatele](../4-AI-PROVIDERS/index.md#connect-a-provider) přidejte poskytovatele ve **Spravovat → Modely**, přidejte jeho modely a nastavte **Výchozí přiřazení modelů**. Zbytek stránky Modely popisuje [Nastavení modelů a API](api-configuration.md).

Co která funkce potřebuje:

| Funkce | Potřebné modely |
|---------|---------------|
| Chat se sešitem, chat se zdrojem | Model chatu |
| Transformace (poznatky) | Model transformací, nebo model chatu, není-li nastaven |
| Dotaz | Model chatu a embedding model |
| Vektorové hledání | Embedding model |
| Textové hledání | Žádný |
| Nahrané zvukové a video soubory, videa z YouTube bez přepisu | Model převodu řeči na text (videa z YouTube s přepisem ho nepotřebují) |
| Podcasty | Jazykové modely a modely převodu textu na řeč zvolené v profilech epizod a mluvčích |

---

## Návody

| Návod | Co pokrývá |
|-------|----------------|
| [Přehled rozhraní](interface-overview.md) | Postranní panel, stránka sešitu, zobrazení zdroje, klávesové zkratky |
| [Nastavení modelů a API](api-configuration.md) | Připojení poskytovatelů AI, synchronizace modelů, výchozí přiřazení modelů |
| [Přidávání zdrojů](adding-sources.md) | Průvodce přidáním zdroje, typy souborů, stav zpracování, chyby |
| [Nástroje pro zpracování obsahu](content-processing-engines.md) | Jak se vytahuje obsah souborů a URL (Docling, Firecrawl, Jina, Crawl4AI, OCR) |
| [Transformace](transformations.md) | Tvorba poznatků ze zdrojů, vestavěné a vlastní transformace |
| [Efektivní chat](chat-effectively.md) | Chat se sešitem, úrovně kontextu, relace, volba modelu, chat se zdrojem |
| [Citace](citations.md) | Čtení a ověřování odkazů v odpovědích AI |
| [Práce s poznámkami](working-with-notes.md) | Psaní poznámek a ukládání odpovědí AI |
| [Hledání a dotazy](search.md) | Textové a vektorové hledání a dotazy napříč znalostní bází |
| [Tvorba podcastů](creating-podcasts.md) | Tvorba epizod, profily epizod a mluvčích |

---

## Prvních 15 minut

1. **Vytvořte sešit.** V postranním panelu **Nový → Sešit** (nebo **Sešity → Nový sešit**). Zadejte název a krátký popis; popis se posílá AI v chatu se sešitem.
2. **Přidejte zdroj.** V sešitu **Přidat zdroj → Přidat zdroj**, pak zvolte **Přidat URL**, **Nahrát soubor** nebo **Zadat text**. V kroku zpracování ponechte předvybranou transformaci a vektorizaci a klikněte na **Hotovo**. Zpracování běží na pozadí; karta ukazuje **Ve frontě**, **Zpracovává se** a pak **Hotovo**. Viz [Přidávání zdrojů](adding-sources.md).
3. **Chatujte.** Ve sloupci Chat napište otázku a stiskněte **Ctrl+Enter** (**⌘+Enter** na Macu). Kliknutím na číslovaný odkaz v odpovědi otevřete citovanou položku.
4. **Uložte odpověď.** Klikněte na ikonu **Uložit do poznámky** pod odpovědí. Poznámka se objeví ve sloupci Poznámky.
5. **Zeptejte se napříč vším.** Otevřete **Dotazy a hledání**, zůstaňte na **Dotaz (beta)**, napište otázku a klikněte na **Zeptat se**. Odpověď uložte tlačítkem **Uložit do sešitů**.

---

## Která funkce na jakou úlohu?

| Úloha | Použijte |
|------|-----|
| Prozkoumat několik zdrojů s doplňujícími otázkami | [Chat se sešitem](chat-effectively.md) |
| Položit jednu otázku napříč vším | [Dotaz](search.md#ask) |
| Najít pasáž nebo pojem, který si pamatujete | [Textové hledání](search.md#search) |
| Najít obsah k myšlence bez ohledu na formulaci | [Vektorové hledání](search.md#search) |
| Získat stejné shrnutí nebo výtah z každého zdroje | [Transformace](transformations.md) |
| Poslechnout si své podklady | [Podcasty](creating-podcasts.md) |

---

## Kde hledat pomoc

- **Něco selhává nebo ukazuje chybu?** → [Řešení potíží](../6-TROUBLESHOOTING/index.md)
- **Jak to funguje?** → [Základní pojmy](../2-CORE-CONCEPTS/index.md)
- **Ještě nemáte nainstalováno?** → [Installation](../../1-INSTALLATION/index.md) (anglicky)
