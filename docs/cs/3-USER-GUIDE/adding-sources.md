# Přidávání zdrojů – jak dostat obsah do sešitu

Zdroje jsou materiál, se kterým AI pracuje: soubory, webové stránky a vložený text. Každý zdroj projde stejným třístupňovým průvodcem **Přidat zdroj** a zpracuje se na pozadí.

---

## Průvodce přidáním zdroje

Otevřete ho ze sešitu (**Přidat zdroj → Přidat zdroj**), ze stránky **Zdroje** (**Nový zdroj**), nebo z postranního panelu (**Nový → Zdroj**).

### Krok 1: Přidat zdroj

Zvolte kartu:

- **Přidat URL**: vložte odkaz. Více odkazů, každý na samostatném řádku, naimportujete najednou.
- **Nahrát soubor**: vyberte jeden soubor, nebo více souborů pro hromadný import.
- **Zadat text**: vložte nebo napište text. U textu je **Název** povinný.
- **Vyhledat na webu** (jen pokud má server nastavené vyhledávání, viz níže): napište hledaný výraz, zaškrtněte vhodné výsledky a klikněte na **Přidat vybrané**. Vybrané adresy se vloží do karty **Přidat URL** a dál se zpracují jako běžné odkazy. Stejnou kartu otevře v sešitu i volba **Přidat zdroj → Vyhledat na webu**.

U jedné URL nebo jednoho souboru je **Název** volitelný; pokud ho necháte prázdný, vytvoří se z obsahu. V hromadném režimu (více než jedna URL nebo soubor) se názvy vytvářejí vždy automaticky a na všechny položky se použijí stejné sešity a transformace. Jedna dávka může obsahovat až **50** URL nebo souborů.

### Krok 2: Sešity

Vyberte sešity, se kterými se má zdroj propojit (volitelné). Pokud jste průvodce otevřeli ze sešitu, je tento sešit už vybraný. Zdroj lze později propojit s dalšími sešity.

### Krok 3: Zpracování

- **Transformace (volitelné)**: transformace, které se nad zdrojem spustí po vytažení textu. Každá vytvoří [poznatek](../2-CORE-CONCEPTS/notebooks-sources-notes.md#poznatky). Transformace označené *Nabízet ve výchozím stavu u nových zdrojů* jsou předvybrané (na nové instalaci je to **Dense Summary**). Viz [Transformace](transformations.md).
- **Vektorizovat pro hledání**: vektorizuje zdroj, aby ho našlo vektorové hledání a dotazy. Výchozí hodnota se řídí **Nastavení → Vektorizace a hledání → Výchozí vektorizace**: *Zeptat se* zobrazí toto zaškrtávací pole (zaškrtnuté), *Vždy* vektorizuje bez ptaní, *Nikdy* vektorizaci přeskočí.

Klikněte na **Hotovo**. Na **Hotovo** můžete kliknout v kterémkoli kroku a odeslat zdroj s aktuálními volbami.

---

## Podporovaný obsah

### Soubory

| Druh | Přípony |
|------|------------|
| Dokumenty | PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, ODT, ODS, ODP, EPUB, TXT, MD, HTML, HTM |
| Zvuk | MP3, WAV, M4A, AAC |
| Video | MP4, AVI, MOV, WMV |
| Obrázky | JPG, JPEG, PNG, TIFF (jen se zapnutým Doclingem; viz [Nástroje pro zpracování obsahu](content-processing-engines.md)) |

- **Zvuk a video se přepisují** pomocí **modelu převodu řeči na text** (nastavuje se ve **Spravovat → Modely → Výchozí přiřazení modelů**). Bez něj je nelze zpracovat. Lokální možnost popisuje [Local Speech-to-Text](../../5-CONFIGURATION/local-stt.md) (anglicky).
- **Velikost nahrávaného souboru** je ve výchozím stavu omezena na 100 MB; limit API mění `OPEN_NOTEBOOK_MAX_UPLOAD_SIZE_MB`. Ve výchozím stavu posílá prohlížeč soubory přímo do API (port 5055), takže je to jediný limit v aplikaci. Pokud vaše nasazení posílá volání API přes cestu `/api` webového rozhraní (například `API_URL` nastavené na adresu rozhraní), omezuje rozhraní velikost požadavku také na 100 MB. Vlastní limit může přidat i reverzní proxy před aplikací.
- **Skenovaná PDF** potřebují Docling s OCR, aby z nich vznikl použitelný text.

### Webové odkazy

- **Články a webové stránky**: stahují se nástrojem pro URL zvoleným v **Nastavení → Zpracování obsahu**. Stránky vykreslované JavaScriptem mohou potřebovat Firecrawl, Jina nebo Crawl4AI; viz [Nástroje pro zpracování obsahu](content-processing-engines.md).
- **Videa z YouTube**: importuje se přepis. Preferované jazyky přepisu jsou nastavení dostupné přes API (`youtube_preferred_languages` v `GET`/`PUT /api/settings`). Pokud YouTube váš server blokuje, nastavte workeru `CCORE_YOUTUBE_PROXY` nebo `CCORE_YOUTUBE_COOKIES_FILE` ([Environment Reference](../../5-CONFIGURATION/environment-reference.md), anglicky).
- **Stránky za přihlášením nebo paywallem** obvykle stáhnout nelze. Zkopírujte text a použijte **Zadat text**.

### Vyhledávání na webu

Karta **Vyhledat na webu** se zobrazí, jen když správce serveru nastaví proměnnou `OPEN_NOTEBOOK_WEB_SEARCH_URL` na vlastní instanci [SearXNG](https://docs.searxng.org/) (se zapnutým výstupem `json`). Hledaný výraz tak nejde žádné službě s API klíčem: SearXNG ho předá veřejným vyhledávačům a výsledky vrátí Open Notebooku. Zaškrtnutí **Jen výsledky v jazyce rozhraní** omezí výsledky na jazyk aplikace. Bez zaškrtnutí se hledá ve všech jazycích. Do jedné dávky lze přidat nejvýš 50 adres včetně těch, které už jsou v kartě **Přidat URL**.

### Text

Vložený text se zpracuje jako každý jiný zdroj (také na pozadí). Vložené HTML se převede na Markdown.

---

## Stav zpracování

Úloha na pozadí vytáhne text, vektorizuje ho (je-li to zapnuto) a spustí vybrané transformace. Karta zdroje ukazuje:

| Stav | Význam |
|--------|---------|
| **Ve frontě** | Čeká na worker |
| **Zpracovává se** | Právě se zpracovává (může se zobrazit ukazatel průběhu) |
| **Hotovo** | Dokončeno; štítek stavu zmizí a karta ukazuje počet poznatků, pokud nějaké jsou |
| **Selhalo** | Zpracování se zastavilo; karta nabízí **Zpracovat znovu** |

Zdroje zpracovává worker na pozadí. Pokud zdroje zůstávají navždy **Ve frontě**, worker neběží (u instalace ze zdrojového kódu `make worker-start`; v Docker image běží automaticky).

Transformace a vektorizace doběhnou až po uložení textu, takže poznatky se mohou objevit chvíli poté, co zdroj ukáže **Hotovo**.

---

<a id="when-a-source-fails"></a>
## Když zdroj selže

Neúspěšný zdroj selže jednou: automaticky se neopakuje. Karta ukazuje důvod chyby a tlačítko **Zpracovat znovu** (také v nabídce ⋮ karty).

Konkrétní důvod se ukládá s úlohou. Najdete ho na kartě zdroje, v záznamu workeru (kde je i původní chyba) nebo přes API na `GET /api/sources/{source_id}/status` (pole `processing_info.error`). Důvody jsou tyto (zprávy aplikace jsou v angličtině):

| Zpráva | Co dělat |
|---------|-----------|
| *The page was not found (it may have been removed or moved). Check the URL.* | Opravte odkaz |
| *Could not reach this address (connection, timeout or DNS error). Check the URL and try again.* | Zkontrolujte URL a přístup serveru k síti a zkuste to znovu |
| *This URL or input is not valid.* | Opravte URL |
| *This file type is not supported.* | Převeďte soubor do podporovaného formátu |
| *The file could not be read. It may be corrupted or in an unsupported format.* | Soubor znovu vyexportujte nebo stáhněte |
| *Could not extract content from this YouTube video. No transcript or subtitles are available. ...* | Video nemá přepis |
| *YouTube blocked or failed the transcript request. ...* | Nastavte `CCORE_YOUTUBE_PROXY` nebo `CCORE_YOUTUBE_COOKIES_FILE` |
| *Content extraction is not configured correctly. ...* | Zkontrolujte nástroj v **Nastavení → Zpracování obsahu** a model převodu řeči na text; podrobnosti jsou v záznamu workeru |
| *The content extraction service failed.* / *Could not extract content from this source.* | Zkuste jiný nástroj, nebo vložte text přes **Zadat text** |

---

## Správa zdrojů

- **Otevření zdroje**: kliknutím na kartu zobrazíte karty Obsah, Poznatky a Podrobnosti. Viz [Přehled rozhraní](interface-overview.md#the-source-view).
- **Přidání do dalšího sešitu**: v daném sešitu **Přidat zdroj → Přidat existující zdroje**, nebo na kartě Podrobnosti u zdroje **Spravovat sešity**.
- **Odebrat ze sešitu** (nabídka ⋮): odpojí zdroj jen od tohoto sešitu.
- **Smazat zdroj** (nabídka ⋮): smaže zdroj všude, včetně poznatků, vektorů a nahraného souboru. Nelze vrátit.
- **Obnovit obsah** (nabídka ⋮, u hotových odkazů): stránku znovu stáhne a znovu zpracuje.
- **Vektorizovat obsah** (nabídka ⋮ v zobrazení zdroje): vektorizuje zdroj, který byl přidán bez vektorizace.
- **Co uvidí chat**: ikona kontextu na každé kartě. Viz [Efektivní chat](chat-effectively.md#choosing-what-the-ai-sees).
