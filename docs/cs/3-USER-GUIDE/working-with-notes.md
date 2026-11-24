# Práce s poznámkami – zachycení toho, co jste zjistili

Poznámka je kus textu v Markdownu v sešitu: něco, co jste napsali, nebo odpověď AI, kterou jste si ponechali. Každá poznámka má název, obsah a štítek, zda je od **Člověka**, nebo **Vytvořila AI**.

Poznámky se liší od **poznatků**: poznatky vytvářejí transformace a jsou připojené ke zdroji, kdežto poznámky patří sešitu. Viz [Sešity, zdroje, poznatky a poznámky](../2-CORE-CONCEPTS/notebooks-sources-notes.md).

---

## Vytváření poznámek

### Vlastní poznámka

1. Ve sloupci **Poznámky** v sešitu klikněte na **Napsat poznámku**.
2. Přidejte název (volitelné) a v editoru Markdownu napište obsah.
3. Klikněte na **Vytvořit poznámku**.

### Vygenerovaná poznámka ze zdrojů

Ve sloupci **Poznámky** klikněte na **Vygenerovat**. V okně zvolte:

- **Z dotazu**: napište otázku nebo zadání (např. „Shrň hlavní argumenty a vypiš otevřené otázky“).
- **Transformací**: vyberte transformaci, např. **Husté shrnutí** nebo **Klíčové poznatky**.

Pod tím zaškrtněte zdroje sešitu, ze kterých se má vycházet (výchozí jsou všechny), a případně vyplňte název. Model dostane celý text vybraných zdrojů a výsledek se uloží jako AI poznámka. Když název nevyplníte, vymyslí ho model. Generování trvá podle délky zdrojů desítky sekund až několik minut a okno se během něj nezavře. Pokud jsou vybrané zdroje dohromady příliš dlouhé, aplikace vás požádá o méně zdrojů (limit nastavuje správce proměnnou `OPEN_NOTEBOOK_NOTE_GENERATION_MAX_CHARS`).

### Uložení odpovědi chatu

Pod kteroukoli odpovědí chatu se sešitem klikněte na ikonu **Uložit do poznámky**. Poznámka se ihned vytvoří jako **Vytvořila AI** s názvem, který z obsahu vytvoří model transformací (nebo model chatu). Žádný dialog se neotevře; chcete-li jiný název, poznámku pak upravte.

### Uložení odpovědi dotazu

Až na stránce **Dotazy a hledání** doběhne odpověď dotazu, klikněte na **Uložit do sešitů**, vyberte jeden nebo více sešitů a klikněte na **Uložit do sešitu**. Každý vybraný sešit dostane poznámku **Vytvořila AI** s otázkou jako názvem a odpovědí jako obsahem.

<a id="turn-an-insight-into-a-note"></a>
### Poznatek jako poznámka

Otevřete poznatek z karty **Poznatky** u zdroje, dole u poznatku vyberte sešit a klikněte na **Uložit jako poznámku**. Pokud máte jen jeden sešit, je už vybraný. Poznámka dostane název *„<typ poznatku> from source <název zdroje>“*, je označena **Vytvořila AI** a objeví se ve sloupci Poznámky daného sešitu. Každé kliknutí vytvoří novou poznámku.

---

## Úpravy a mazání

- **Upravit**: kliknutím na kartu poznámku otevřete, změňte název nebo obsah a klikněte na **Uložit poznámku**.
- **Smazat**: v nabídce ⋮ karty poznámky zvolte **Smazat poznámku** a potvrďte. Nelze vrátit.
- Smazání sešitu smaže i jeho poznámky.

---

## Použití poznámek

- **V chatu se sešitem**: každá poznámka má ikonu kontextu, která ji přepíná mezi zahrnutou (celý obsah) a **Nezahrnuto do chatu**. Nabídka **Kontext** ve sloupci Poznámky zahrne nebo vyřadí všechny. Viz [Efektivní chat](chat-effectively.md#choosing-what-the-ai-sees).
- **V hledání a dotazech**: poznámky pokrývá textové hledání (názvy a obsah) a po vektorizaci i vektorové hledání a dotazy. Při nastaveném embedding modelu se poznámky vektorizují automaticky při uložení.
- **V podcastech**: poznámky lze vybrat jako obsah epizody. Viz [Tvorba podcastů](creating-podcasts.md).

Poznámky nelze použít jako vstup transformací; transformace běží jen nad zdroji. Chcete-li tak zpracovat dlouhou poznámku, přidejte její text jako zdroj přes **Zadat text**.

---

## Tipy

- **Na začátek dlouhých poznámek napište krátké shrnutí.** Pomůže vám i modelu.
- **Uložené odpovědi učešte.** Odpovědi AI často obsahují vatu; když ji odstraníte, zůstane kontext chatu malý, i když je poznámka zahrnutá.
- **Udržujte aktuální popis sešitu.** Posílá se modelu v každém chatu se sešitem a pomáhá AI pochopit, o čem vaše poznámky jsou.
