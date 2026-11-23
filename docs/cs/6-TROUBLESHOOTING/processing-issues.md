# Potíže se zpracováním – zdroje, hledání a podcasty

Problémy s prací na pozadí: zdroje, které nedoběhnou, odmítnuté nahrání, hledání bez výsledků, neúspěšné podcasty. Každá položka začíná tím, co vidíte.

Zpracování zdrojů, vektorizace, poznatky, transformace a podcasty běží ve **workeru**, procesu na pozadí. Kontroly nahrávání a hledání běží v API. V Dockeru běží worker v kontejneru `open_notebook` vedle API; při spuštění ze zdrojového kódu ho spouštíte sami příkazem `make worker-start`.

---

<a id="sources-stay-queued-waiting-to-be-processed"></a>
## Zdroje zůstávají „Ve frontě“ („Čeká na zpracování“)

**Příčina:** worker neběží, nebo se nedostane k frontě úloh. Úlohy se ukládají do databáze a čekají tam, dokud si je worker nevyzvedne. Stejně čekají vektorizace, poznatky a podcasty.

**Ze zdrojového kódu:**

```bash
make status          # „Background Worker: ❌ Not running“?
make worker-start
```

**Docker:** worker v kontejneru spouští a restartuje supervisord. Jeho stav zjistíte ze záznamu:

```bash
docker compose logs open_notebook | grep -E "spawned: 'worker'|worker entered|exited: worker"
```

- `success: worker entered RUNNING state` → běží; viz další kontrolu.
- Opakující se `exited: worker` nebo `gave up: worker entered FATAL state` → padá při startu. Řádky těsně před tím ukazují proč; častou příčinou je chybné nastavení `SURREAL_*`.
- Řádky před tím říkají `to be serialized string contained a null byte` → textový zdroj s bajtem NUL, přidaný ve starší verzi, zanechal poškozenou úlohu. Smažte ji v `surreal sql` (jmenný prostor/databáze `open_notebook`) a restartujte kontejner: `DELETE command WHERE status = 'new' AND name = 'process_source' AND !record::exists(type::thing(args.source_id));`

**Běží, a stále se nic neděje:** API a worker musí používat stejnou databázi. Ověřte, že všech pět proměnných `SURREAL_*` je výslovně nastaveno (dodaný compose soubor to dělá) a že API i worker dostávají stejné hodnoty. Viz [Database](../../5-CONFIGURATION/database.md) (anglicky).

**Mnoho zdrojů najednou:** worker zpracovává současně `OPEN_NOTEBOOK_WORKER_MAX_TASKS` úloh (výchozí 5); ostatní zůstávají Ve frontě, dokud se neuvolní místo. To je v pořádku.

---

<a id="failed-sources"></a>
## Neúspěšné zdroje

**Co vidíte:** karta zdroje ukazuje **Selhalo** a důvod chyby. V nabídce karty použijte **Zpracovat znovu** a zařaďte ho znovu do fronty; neúspěšný zdroj se automaticky neopakuje.

**Kde najít podrobnosti:** důvod se ukládá s úlohou a kromě karty se objeví na dvou místech:

```bash
# Záznam workeru s úplnou původní chybou
docker compose logs open_notebook | grep -iE "content-core extraction failed|Source processing|process_source"

# API: processing_info.error obsahuje důvod z tabulky níže
curl -s http://localhost:5055/api/sources/<source_id>/status
```

(Je-li nastaveno heslo, přidejte `-H "Authorization: Bearer <heslo>"`.) ID zdroje je v adresním řádku prohlížeče, když zdroj otevřete.

| Důvod | Příčina | Řešení |
|--------|-------|-----|
| „Could not reach this address (connection, timeout or DNS error). Check the URL and try again.“ | Web neběží, blokuje server, nebo kontejner nemá přístup k internetu | Otevřete URL ze serveru (`docker compose exec open_notebook curl -I <url>`). Za firemní proxy nastavte `HTTP_PROXY`/`HTTPS_PROXY` |
| „The page was not found (it may have been removed or moved). Check the URL.“ | HTTP 404 | Opravte URL |
| „This URL or input is not valid.“ | Chybně zapsaná URL nebo vstup | Zkontrolujte, co jste vložili |
| „Could not extract content from this YouTube video. No transcript or subtitles are available. Try configuring a Speech-to-Text model in Settings to transcribe the audio instead.“ | Video nemá titulky | Přiřaďte **model převodu řeči na text** ve Spravovat → Modely a zkuste to znovu |
| „YouTube blocked or failed the transcript request. If this keeps happening, set CCORE_YOUTUBE_PROXY (a residential proxy) or CCORE_YOUTUBE_COOKIES_FILE for the worker.“ | YouTube blokuje IP serveru (časté u cloudových hostitelů) | Nastavte jednu z těchto proměnných v prostředí `open_notebook`, `docker compose up -d`, zkuste znovu. Viz [Environment Reference](../../5-CONFIGURATION/environment-reference.md#content-extraction) (anglicky) |
| „This file type is not supported.“ | content-core pro soubor nemá extraktor | Převeďte soubor (do PDF, DOCX, prostého textu…). Obrázky potřebují `OPEN_NOTEBOOK_ENABLE_DOCLING=true` |
| „The file could not be read. It may be corrupted or in an unsupported format.“ | Poškozený, šifrovaný nebo chybně označený soubor | Znovu ho vyexportujte nebo stáhněte |
| „Content extraction is not configured correctly. Check the content processing engine and speech-to-text settings; the worker log has the details.“ | Chybně nastavený nástroj nebo převod řeči na text: chybí API klíč pro zvolený nástroj (Firecrawl), nečitelný `CCORE_YOUTUBE_COOKIES_FILE`, nefunkční model převodu řeči na text | Přečtěte záznam workeru, pak opravte **Nastavení → Zpracování obsahu** nebo model převodu řeči na text |
| „The content extraction service failed.“ | Selhala externí služba: Firecrawl, Jina, Crawl4AI nebo poskytovatel převodu řeči na text | Zkontrolujte danou službu, nebo přepněte nástroj na `auto` v **Nastavení → Zpracování obsahu** |
| „Could not extract any text content from this source. The content may be empty, inaccessible, or in an unsupported format.“ | Vytažení proběhlo, ale nedalo žádný text: skenované PDF bez OCR, stránka vykreslovaná JavaScriptem, přihlašovací zeď | U skenů zapněte Docling (OCR); u stránek s JavaScriptem použijte nástroj Crawl4AI nebo Firecrawl |
| „Could not extract content from this source.“ | Jakákoli jiná chyba vytažení | Viz záznam workeru |

Tato selhání jsou konečná: opakování beze změny selže stejně.

<a id="the-selected-engine-isnt-used"></a>
### Vybraný nástroj se nepoužije

Záznam workeru ukazuje `Configured url engine 'crawl4ai' is selected in Content Settings but its runtime is not available in this container; falling back to 'auto'. Set OPEN_NOTEBOOK_ENABLE_CRAWL4AI=true to enable it`. Nástroj je v Nastavení vybraný, ale jeho volitelné prostředí není nainstalované (nebo instalace při startu selhala). Nastavte uvedenou proměnnou, spusťte `docker compose up -d` a v záznamu hledejte řádky `[entrypoint]`. Viz [Nástroje pro zpracování obsahu](../3-USER-GUIDE/content-processing-engines.md).

### Přepis zvuku nebo videa selže

U lokálních serverů viz [Local Speech-to-Text → When transcription fails](../../5-CONFIGURATION/local-stt.md#when-transcription-fails) (anglicky). U cloudového převodu řeči na text ověřte, že je přiřazen **model převodu řeči na text** a klíč jeho poskytovatele funguje (**Test** ve Spravovat → Modely).

---

<a id="uploads-rejected"></a>
## Odmítnuté nahrání

### „Request body exceeds the maximum allowed upload size“ (413)

Soubor je větší než `OPEN_NOTEBOOK_MAX_UPLOAD_SIZE_MB` (výchozí 100). Ve výchozím stavu prohlížeč nahrává přímo do API, takže stačí tuto proměnnou zvýšit. Pokud `API_URL` míří na adresu rozhraní, jde nahrávání přes proxy rozhraní, která je omezena na 100 MB bez ohledu na tuto proměnnou. Za reverzní proxy platí nejdřív její vlastní limit a prohlížeč může hlásit chybu CORS se stavem 413. Viz [Reverse Proxy → Upload size](../../5-CONFIGURATION/reverse-proxy.md#upload-size-413-errors) (anglicky).

### „… (detected type: …)“ (415)

Nahrání bylo odmítnuto před zpracováním, protože content-core z tohoto typu souboru neumí vytáhnout text. Zpráva uvádí důvod a zjištěný typ. Soubor převeďte, nebo pro obrázky a skenované dokumenty zapněte Docling.

---

<a id="search-and-ask"></a>
## Hledání a dotazy

### „Tato funkce potřebuje embedding model. Nastavte ho v části Modely.“

Na stránce hledání se zobrazí také jako „Vektorové hledání potřebuje embedding model. K dispozici je jen textové hledání.“ Není přiřazen žádný **embedding model**. Přidejte ho ve Spravovat → Modely (Vyhledat modely s **Typem modelu** Embedding) a přiřaďte ho ve Výchozím přiřazení modelů. Poskytovatelé jen s jazykovými modely, například Anthropic, embedding modely nemají; přidejte druhého poskytovatele.

### Vektorové hledání nic nenajde

- Zdroje přidané před přiřazením embedding modelu, nebo s vypnutou vektorizací, nemají vektory. Přestavte je na stránce **Pokročilé**.
- Po změně embedding modelu staré a nové vektory neodpovídají. **Spravovat → Modely** na to upozorní („Důležité: je nutná přestavba“); přestavbu spusťte na stránce **Pokročilé**.
- Ověřte, že zdroje jsou **Hotovo**, ne Ve frontě nebo Selhalo.

<a id="ask-fails-with-the-strategy-model-returned-no-search-terms-for-this-question"></a>
### Dotaz selže s „The strategy model returned no search terms for this question.“

Model zvolený pro krok strategie nevrátil nic použitelného, obvykle proto, že model s uvažováním spotřeboval výstupní rozpočet na přemýšlení. Zvolte jiný model strategie v pokročilém výběru modelů na stránce dotazů, nebo otázku přeformulujte. „The final answer model returned an empty response.“ má stejnou příčinu u posledního kroku.

---

## Transformace a poznatky

<a id="this-source-has-no-text-content-to-transform"></a>
### „Tento zdroj nemá žádný text, který by šlo transformovat“

Zdroj nemá vytažený text (selhal, nebo se ještě zpracovává). Nejdřív opravte zdroj; viz [Neúspěšné zdroje](#failed-sources).

### Poznatky se nikdy neobjeví

Poznatky vytváří úloha na pozadí. Pokud je zdroj Hotovo, ale jeho poznatky se neobjeví, ověřte, že běží worker ([výše](#sources-stay-queued-waiting-to-be-processed)). Chyby modelů popisují [Potíže s AI a chatem](ai-chat-issues.md).

---

<a id="podcast-failures"></a>
## Selhání podcastů

Neúspěšná epizoda ukazuje na své kartě v **Podcasty → Epizody** stav **Selhalo** s chybovou zprávou a tlačítko **Zkusit znovu**. Tvorba podcastu se zkouší jednou; po odstranění příčiny použijte Zkusit znovu. Když Open Notebook chybu rozpozná, zpráva končí poznámkou `NOTE:`, která ji vysvětluje.

### Chyby profilů (tvorba se zastaví dřív, než se zavolá jakýkoli model)

| Zpráva | Řešení |
|---------|-----|
| „Episode profile 'X' has no speaker profile configured. Please update the profile to select a speaker profile.“ | Upravte profil epizody v **Podcasty → Profily** a vyberte profil mluvčích |
| „Episode profile 'X' references a speaker profile that no longer exists. Please update the profile to select a speaker profile.“ | Profil mluvčích byl smazán; vyberte jiný |
| „Episode profile 'X' has no outline model configured. Please update the profile to select an outline model.“ (stejně pro „transcript model“) | Vyberte modely v profilu epizody |
| „Speaker profile 'X' has no voice model configured. Please update the profile to select a voice model.“ | Upravte profil mluvčích a zvolte model převodu textu na řeč. Profily mluvčích dodané s Open Notebookem hlasový model nemají, dokud ho nenastavíte |

Pokud není přiřazen žádný model převodu textu na řeč, ukazuje **Spravovat → Modely** u modelu převodu textu na řeč „Nenastaveno – tvorba zvuku není dostupná, dokud model nenastavíte“. Přidejte poskytovatele s TTS (OpenAI, Google, ElevenLabs, MiniMax, lokální server [Speaches](../../5-CONFIGURATION/local-tts.md)…).

### Chyby s poznámkou NOTE

| Chyba obsahuje | Co vysvětluje NOTE | Řešení |
|----------------|------------------------|-----|
| `Invalid speaker name` | Model scénáře napsal jméno mluvčího, které v profilu mluvčích není, obvykle zástupný text jako `...` | Zkuste to znovu; každý pokus je nový vzorek. Pokud se to opakuje, použijte silnější model scénáře |
| `Voice name ... not supported` | **ID hlasu** v profilu mluvčích není platné pro jeho model TTS. Dodané profily používají názvy hlasů OpenAI (`alloy`, `nova`…) | Nastavte ID hlasů, které váš poskytovatel TTS nabízí |
| `Requested entity was not found` | Obecné „nenalezeno“ od Googlu: obvykle název hlasu OpenAI poslaný hlasovému modelu Gemini, jinak neexistující ID modelu | Opravte ID hlasu, nebo model v profilu epizody. Pokud scénář doběhl a selhal zvuk, jde o hlas |
| `Invalid json output` nebo `Expecting value` | Odpověď pro osnovu nebo scénář nebyla platný JSON: buď useknutá (tvorba podcastu žádá až 8192 výstupních tokenů na krok, pokud profil epizody nenastaví jinak), nebo model s uvažováním dal vše do značek `<think>` | Nastavte max. tokenů na limit modelu nebo použijte méně kratších segmentů; nebo pro osnovu a scénář použijte model bez uvažování |

### Další chyby podcastů

- Vypršení času v kroku osnovy nebo scénáře: viz [Potíže s AI a chatem → časové limity](ai-chat-issues.md#the-ai-provider-took-too-long-to-respond).
- Zvuk selže v půlce u lokálního serveru TTS nebo serveru s omezením požadavků: snižte `TTS_BATCH_SIZE` a zvyšte `ESPERANTO_TTS_TIMEOUT` ([Environment Reference](../../5-CONFIGURATION/environment-reference.md#worker-and-background-jobs), anglicky).
- Epizoda zůstává ve stavu Čeká: worker neběží ([výše](#sources-stay-queued-waiting-to-be-processed)).

Více o nastavení podcastů: [Tvorba podcastů](../3-USER-GUIDE/creating-podcasts.md).

---

## Související

- [Potíže s AI a chatem](ai-chat-issues.md) — chyby modelů, přístupových údajů a časových limitů
- [Potíže s připojením](connection-issues.md) — spojení rozhraní, API a databáze
- [Environment Reference](../../5-CONFIGURATION/environment-reference.md) (anglicky)
