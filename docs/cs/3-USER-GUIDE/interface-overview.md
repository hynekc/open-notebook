# Přehled rozhraní – jak se v aplikaci vyznat

## Postranní panel

Pracovní stránky mají vlevo postranní panel (lze ho sbalit na ikony). Výjimkou je vlastní stránka zdroje (otevřená tlačítkem **Chat se zdroji**), která ukazuje jen zdroj a jeho chat.

```
┌──────────────────────┐
│ Open Notebook        │
│ [+ Nový]             │  → Zdroj, Sešit, Podcast
│                      │
│ SBÍRAT               │
│   Zdroje             │
│ ZPRACOVAT            │
│   Sešity             │
│   Dotazy a hledání   │
│ TVOŘIT               │
│   Podcasty           │
│ SPRAVOVAT            │
│   Modely             │
│   Transformace       │
│   Nastavení          │
│   Pokročilé          │
│                      │
│ Rychlé akce     ⌘K   │
│ Motiv · Jazyk ·      │
│ Odhlásit se          │
└──────────────────────┘
```

| Položka | K čemu slouží |
|------|---------------|
| **Nový** | Odkudkoli vytvoří zdroj, sešit nebo epizodu podcastu |
| **Zdroje** | Knihovna zdrojů: všechny zdroje bez ohledu na to, ve kterých sešitech jsou |
| **Sešity** | Vaše sešity: nedávno zobrazené, aktivní a archivované, jako dlaždice nebo seznam |
| **Dotazy a hledání** | Otázky napříč znalostní bází nebo hledání v ní ([Hledání a dotazy](search.md)) |
| **Podcasty** | Vytvořené epizody a profily epizod/mluvčích ([Tvorba podcastů](creating-podcasts.md)) |
| **Modely** | Konfigurace poskytovatelů AI a výchozí modely ([Nastavení modelů a API](api-configuration.md)) |
| **Transformace** | Prompty transformací a Zkušebna ([Transformace](transformations.md)) |
| **Nastavení** | Zpracování obsahu, Vektorizace a hledání, Správa souborů |
| **Pokročilé** | Informace o systému (verze a kontrola aktualizací) a Znovu vytvořit vektory |
| **Rychlé akce** | Paleta příkazů: přechod na stránky a sešity, hledání nebo dotaz, vytváření položek, změna motivu |
| **Motiv / Jazyk** | Světlý, tmavý nebo systémový motiv; jazyk rozhraní (čeština je v nabídce jako „Čeština“) |

---

## Stránka sešitu

Otevřený sešit ukazuje záhlaví a tři sloupce.

```
┌────────────────────────────────────────────────────────────────────┐
│ Název sešitu   (kliknutím upravíte)       [Archivovat]   [Smazat]  │
│ Popis          (kliknutím upravíte)                                │
├──────────────────┬──────────────────┬──────────────────────────────┤
│ ZDROJE           │ POZNÁMKY         │ CHAT SE SEŠITEM              │
│ [Kontext][Přidat │ [Kontext]        │ [Relace]                     │
│           zdroj] │ [Napsat poznámku]│                              │
│                  │                  │  zprávy s číslovanými        │
│ ┌──────────────┐ │ ┌──────────────┐ │  odkazy                      │
│ │ clanek.pdf   │ │ │ Moje poznámky│ │                              │
│ │ Soubor · 2   │ │ │ Člověk       │ │  2 zdroje · 1 poznámka       │
│ │ poznatky  ◐ ⋮│ │ │            ◐ │ │  ~12 400 tokenů              │
│ └──────────────┘ │ └──────────────┘ │ [Model] [Zeptejte se...]     │
└──────────────────┴──────────────────┴──────────────────────────────┘
```

Na počítači lze sloupce Zdroje a Poznámky sbalit. Na malých obrazovkách se sloupce změní na tři karty **Zdroje**, **Poznámky** a **Chat**, přičemž jako první je vybraný Chat.

### Sloupec Zdroje

- **Přidat zdroj** otevře nabídku: **Přidat zdroj** (průvodce pro nový obsah) nebo **Přidat existující zdroje** (propojení zdrojů z knihovny). Viz [Přidávání zdrojů](adding-sources.md).
- **Kontext** nastaví všechny zdroje najednou: **Zahrnout vše (jen poznatky)**, **Zahrnout vše (celý obsah)** nebo **Vyřadit vše z kontextu**.
- Každá **karta zdroje** ukazuje název, typ (Přidat URL, Nahrát soubor nebo Zadat text), stav zpracování, dokud není hotovo, a počet poznatků (pokud nějaké jsou). **Ikona kontextu** po kliknutí přepíná [úroveň kontextu](../2-CORE-CONCEPTS/ai-context-rag.md#context-levels-in-notebook-chat) zdroje. **Nabídka ⋮** obsahuje **Odebrat ze sešitu**, **Zpracovat znovu** (u neúspěšných zdrojů), **Obnovit obsah** (u hotových odkazů) a **Smazat zdroj**.
- Kliknutím na kartu otevřete zobrazení zdroje.

### Sloupec Poznámky

- **Napsat poznámku** vytvoří poznámku.
- **Kontext** nabízí **Zahrnout vše do kontextu** a **Vyřadit vše z kontextu**.
- Každá **karta poznámky** ukazuje název, štítek **Vytvořila AI** nebo **Člověk** a ikonu kontextu (zapnuto nebo vypnuto). Kliknutím na kartu poznámku upravíte. Viz [Práce s poznámkami](working-with-notes.md).

### Sloupec Chat

Chat se sešitem nad zdroji a poznámkami v kontextu. **Relace** otevře uložené relace chatu, tlačítko modelu vybere model pro relaci a panel ukazuje, kolik obsahu je v kontextu. Odešlete klávesami **Ctrl+Enter** (**⌘+Enter** na Macu). Viz [Efektivní chat](chat-effectively.md).

---

<a id="the-source-view"></a>
## Zobrazení zdroje

Kliknutím na zdroj ho otevřete se třemi kartami:

- **Obsah**: vytažený text a u odkazů na YouTube vložené video.
- **Poznatky**: poznatky vytvořené transformacemi a tlačítko **Vytvořit nový poznatek** pro spuštění další. Viz [Transformace](transformations.md).
- **Podrobnosti**: témata, stav vektorizace, datum vytvoření a úpravy a sešity, do kterých zdroj patří (**Spravovat sešity**).

**Chat se zdroji** otevře vlastní stránku zdroje se zdrojem vlevo a chatem o něm vpravo. **Nabídka ⋮** obsahuje **Stáhnout soubor** (u nahraných souborů, dokud je soubor uložen), **Vektorizovat obsah** (pokud zdroj ještě není vektorizovaný) a **Smazat zdroj**.

---

## Další stránky

- **Zdroje** (knihovna): tabulka všech zdrojů s typem, počtem poznatků a stavem vektorizace. **Nový zdroj** přidá zdroj bez otevírání sešitu.
- **Sešity**: **Nový sešit**, vyhledávací pole, **Nedávno zobrazené** a seznamy **Aktivní sešity** a **Archivované sešity**.
- **Nastavení**: Zpracování obsahu (nástroje pro dokumenty a URL, OCR a další volby Doclingu; viz [Nástroje pro zpracování obsahu](content-processing-engines.md)), Vektorizace a hledání (**Výchozí vektorizace**: Zeptat se, Vždy nebo Nikdy) a Správa souborů (**Automaticky mazat soubory**: zda se nahrané soubory po zpracování mažou).
- **Pokročilé**: **Informace o systému** ukazují vaši verzi a zda je k dispozici aktualizace. **Znovu vytvořit vektory** znovu vektorizuje obsah po změně embedding modelu (režim *Stávající* nebo *Vše*); běží na pozadí.

---

## Klávesové zkratky

| Zkratka | Kde | Akce |
|----------|-------|--------|
| **Ctrl+K** / **⌘K** | Kdekoli | Otevře Rychlé akce (paletu příkazů) |
| **Ctrl+Enter** / **⌘+Enter** | Pole pro zprávu v chatu | Odeslat |
| **Enter** | Pole pro zprávu v chatu | Nový řádek |
| **Ctrl+Enter** / **⌘+Enter** | Pole pro otázku dotazu | Zeptat se |
| **Enter** | Vyhledávací pole | Hledat |
