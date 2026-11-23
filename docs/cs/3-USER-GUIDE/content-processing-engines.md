# Nástroje pro zpracování obsahu – jak se vytahuje obsah

Když přidáte zdroj, Open Notebook z něj vytáhne text a teprve pak ho rozdělí na úseky, vektorizuje a zaindexuje. Jak se text vytahuje, určuje **nástroj pro zpracování**. Obvykle na nic sahat nemusíte – výchozí nastavení zvládne většinu obsahu –, ale znalost možností pomůže, když se dokument vytáhne špatně nebo URL vrátí prázdný výsledek.

Vše se nastavuje v **Nastavení → Zpracování obsahu**.

> **Některé nástroje jsou volitelné.** Výchozí image je štíhlý, takže těžší
> **Docling** (rozbor rozvržení + OCR + obrázkové zdroje) a **lokální Crawl4AI**
> (vykreslování JavaScriptu) se **zapínají volitelně** – povolíte je proměnnou
> prostředí a nainstalují se při prvním spuštění. Do té doby jsou v Nastavení
> **neaktivní**. Viz [Volitelné nástroje](#optional-engines-docling--crawl4ai) níže.

---

## Kde nastavit

```
Nastavení → Zpracování obsahu:
  - Nástroj pro zpracování dokumentů   (nahrané soubory)
  - Nástroj pro zpracování URL         (webové odkazy)
  - Zapnout OCR                        (skenovaná PDF a obrázky, jen Docling)
  - Rozpoznávat vzorce                 (jen Docling)
  - Popisovat obrázky a grafy          (jen Docling)
```

Po změně klikněte na **Uložit**. Změny platí pro zdroje zpracované **po** uložení. Chcete-li existující webový odkaz vytáhnout znovu s novým nastavením, použijte **Obnovit obsah** v nabídce jeho karty; soubor přidejte znovu (neúspěšný zdroj lze také znovu zpracovat tlačítkem **Zpracovat znovu**).

---

## Nástroje pro zpracování dokumentů

Určují, jak se nahrané soubory (PDF, Word, PowerPoint, EPUB atd.) převádějí na text.

| Nástroj | Co dělá | Kompromis |
|--------|--------------|-----------|
| **Automaticky (doporučeno)** (výchozí) | Zkusí Docling (je-li zapnutý) a jinak použije jednoduché vytažení. | Vyvážené. Dobrá výchozí volba téměř pro každého. |
| **Docling** | Vytahování s ohledem na rozvržení: rozumí sloupcům, tabulkám, nadpisům a pořadí čtení. Při zapnutém OCR rozpozná text na skenovaných stránkách. **Volitelný – musí se zapnout** (viz níže). | Nejpřesnější, ale pomalejší a náročnější. |
| **Jednoduchý** | Rychlé, nenáročné vytažení textu. Docling úplně vynechá. | Nejrychlejší, ale ztrácí strukturu tabulek a rozvržení; bez OCR. |

**Kdy co zvolit:**

- **Automaticky** – nechte, pokud nemáte důvod jinak.
- **Docling** – vynuťte ho, když záleží na tabulkách, vícesloupcovém rozvržení nebo skenovaných PDF a Automaticky nedává čisté výsledky. Docling musí být zapnutý.
- **Jednoduchý** – pro velké dávky čistých textových dokumentů, kde je rychlost důležitější než věrnost rozvržení.

---

## Nástroje pro zpracování URL

Určují, jak se webové odkazy stahují a převádějí na text. Weby se velmi liší – některé jsou statické HTML, jiné vše vykreslují JavaScriptem, jiné jsou za ochranou proti robotům –, proto Open Notebook nabízí několik nástrojů s různými schopnostmi.

| Nástroj | Co dělá | Potřebuje |
|--------|--------------|-------|
| **Automaticky (doporučeno)** (výchozí) | Zkouší nástroje postupně, dokud některý neuspěje (viz řetězec níže). | Nic; použije, co je nastaveno. |
| **Firecrawl** | Spravovaná služba pro stahování webů. Dobře zvládá JavaScript, ochranu proti robotům a proxy. | `FIRECRAWL_API_KEY` (nebo vlastní instanci). |
| **Jina** | Jina AI Reader. Dobře převádí články na čistý text. | `JINA_API_KEY`. |
| **Crawl4AI** | Vykresluje stránky s JavaScriptem v lokálním prohlížeči Chromium. Nepotřebuje API klíč. **Volitelný – musí se zapnout** (viz níže). | `OPEN_NOTEBOOK_ENABLE_CRAWL4AI=true` (nainstaluje se při prvním spuštění), nebo vzdálený server přes `CRAWL4AI_API_URL`. |
| **Jednoduchý** | Základní stažení přes HTTP a rozbor knihovnou BeautifulSoup. | Nic. |

### Jak funguje záložní řetězec v režimu Automaticky

V režimu Automaticky Open Notebook zkouší nástroje v tomto pořadí a zastaví se u prvního, který vrátí použitelný obsah:

```
Firecrawl  →  Jina  →  Crawl4AI  →  jednoduchý (bs4)
```

- Nenastavené nástroje (např. bez klíče Firecrawl) nebo nezapnuté (Crawl4AI) se přeskočí.
- Firecrawl a Jina jsou první, protože si nejlépe poradí s obtížnými weby.
- Crawl4AI zachytí stránky postavené na JavaScriptu, které API služby nezvládnou, pomocí lokálního Chromia – **pokud je zapnutý**.
- `jednoduchý` je poslední možnost – obyčejný požadavek HTTP. Je rychlý a nic nepotřebuje, ale **nezachytí nic, co vykresluje JavaScript**, takže jednostránkové aplikace a dynamické weby často vrátí prázdný nebo neúplný obsah.

**Kdy vynutit konkrétní nástroj:**

- **Firecrawl** / **Jina** – máte klíč a chcete stabilní, kvalitní vytahování bez nákladů na lokální vykreslování.
- **Crawl4AI** – web potřebuje skutečný prohlížeč (obsah vykreslovaný JavaScriptem), ale nechcete placené API. Crawl4AI musí být zapnutý.
- **Jednoduchý** – web je čisté HTML a chcete nejrychlejší cestu bez závislostí.

API klíče a ladicí proměnné (`FIRECRAWL_API_URL`, `CCORE_FIRECRAWL_PROXY`, `CCORE_FIRECRAWL_WAIT_FOR`, `CRAWL4AI_API_URL`, `CRAWL4AI_API_TOKEN`) popisuje [Environment Reference](../../5-CONFIGURATION/environment-reference.md#content-extraction) (anglicky).

---

## Přepínač OCR

**Nastavení → Zpracování obsahu → Zapnout OCR** (ve výchozím stavu zapnuto, ale účinné až se zapnutým Doclingem).

OCR čte text z obrázků. Uplatní se, když nástroj Docling zpracovává:

- **Skenovaná PDF** – stránky, které jsou obrázkem textu, ne skutečným textem.
- **Obrázkové zdroje** – PNG, JPEG, TIFF.

OCR běží jen přes Docling, takže dokud **Docling není zapnutý** (viz níže), nedělá nic. S vypnutým Doclingem je přepínač v Nastavení neaktivní, skenovaná PDF se zpracují prostým vytažením textu (které u stránek tvořených jen obrázky dá málo) a obrázkové zdroje se odmítnou jako nepodporované.

**Nechte ho zapnutý**, pokud pracujete se skenovanými dokumenty nebo obrázky. **Vypněte ho** pro rychlejší zpracování, když jsou všechny dokumenty textové – OCR tam přidává zbytečnou zátěž.

---

## Vzorce a popisy obrázků

Další dvě volby Doclingu v **Nastavení → Zpracování obsahu**, obě ve výchozím stavu vypnuté:

- **Rozpoznávat vzorce** – zachová matematické vzorce jako strukturovaný zápis místo zkomoleného textu. Prodlužuje zpracování. Hodí se pro články plné matematiky.
- **Popisovat obrázky a grafy** – pomocí vizuálního modelu popíše obrázky a vytáhne data z grafů, takže se z tohoto obsahu stane prohledávatelný text. Výrazně pomalejší a může volat vizuální model.

Stejně jako OCR se obě uplatní, jen když dokument zpracovává Docling.

Ve výchozím stavu popisy obrázků vytváří malý vestavěný model Doclingu, který je rychlý, ale na skutečné grafy a obrázky často nestačí. Chcete-li použít silnější vizuální model, který už provozujete (Qwen2.5-VL, Pixtral, Gemma vision a podobné, servírované přes vLLM, Ollamu, LM Studio nebo hostované API), zadejte jeho endpoint kompatibilní s OpenAI u volby **Popisovat obrázky a grafy**: při zapnuté volbě se objeví **URL vizuálního endpointu**, **Vizuální model** a volitelný **Prompt pro popis obrázků**. Prázdné pole použije proměnnou workeru `CCORE_DOCLING_VISION_URL`, `CCORE_DOCLING_VISION_MODEL` nebo `CCORE_DOCLING_VISION_PROMPT`. API klíč není nastavení: nastavte ho v `CCORE_DOCLING_VISION_API_KEY`, protože nastavení se ukládají nešifrovaně. Hostovaný endpoint dostane každý popisovaný obrázek, proto pro udržení dokumentů lokálně použijte model na vlastním hardwaru ([Environment Reference](../../5-CONFIGURATION/environment-reference.md#content-extraction), anglicky). Vytahování dat z grafů dál používá vlastní model Doclingu.

---

<a id="optional-engines-docling--crawl4ai"></a>
## Volitelné nástroje (Docling a Crawl4AI)

Docling a lokální Crawl4AI jsou náročné: Docling stahuje sadu pro strojové učení o velikosti stovek MB až jednotek GB a Crawl4AI obsahuje prohlížeč Chromium. Aby výchozí image zůstal malý, **ve výchozím stavu se neinstalují**. Zapnete je proměnnou prostředí; prostředí se pak automaticky nainstaluje **při prvním spuštění kontejneru** a stažené soubory se uloží do mezipaměti na datovém svazku, takže další starty jsou rychlé.

| Zapněte | Získáte |
|-------------|-----------|
| `OPEN_NOTEBOOK_ENABLE_DOCLING=true` | Nástroj Docling pro dokumenty, přepínače OCR, vzorců a popisu obrázků a obrázkové zdroje (PNG/JPEG/TIFF). |
| `OPEN_NOTEBOOK_ENABLE_CRAWL4AI=true` | Lokální nástroj pro URL `crawl4ai` (vykreslování JavaScriptu přes Chromium). |
| `CRAWL4AI_API_URL=…` | Nástroj `crawl4ai` proti **vzdálenému** serveru Crawl4AI – bez lokální instalace. Pokud server vyžaduje bearer token (Crawl4AI Docker ≥ 0.9.0 ve výchozím stavu ano), přidejte `CRAWL4AI_API_TOKEN=…`. |

Poznámky:

- **První start je pomalejší.** Zapnutí Doclingu stáhne velkou sadu pro strojové učení (při prvním startu několik minut). Průběh se výrazně loguje. Další starty použijí mezipaměť na svazku `/app/data`.
- **Omezit, ne spadnout.** Pokud instalace při startu selže (např. bez sítě), aplikace se přesto spustí – nástroj je jen hlášen jako nedostupný a jeho volba zůstane v Nastavení neaktivní.
- **Rozhraní odpovídá skutečnosti.** Nastavení ukazuje Docling, Crawl4AI a OCR jako neaktivní, dokud prostředí není skutečně nainstalované a importovatelné, takže během instalace při prvním startu správně hlásí „nedostupné“.
- **Nasazení bez internetu / izolovaná síť:** instalace při startu potřebuje při prvním spuštění přístup k síti. Pokud se nedostanete na PyPI, nechte tyto nástroje vypnuté.

Proměnné nastavte stejně jako kteroukoli jinou proměnnou prostředí Open Notebooku (viz [Environment Reference](../../5-CONFIGURATION/environment-reference.md), anglicky, a váš `docker-compose.yml`).

---

## Rychlý přehled

```
Dokument se vytáhne špatně (tabulky a sloupce jsou zkomolené)
  → Zapněte Docling a nastavte Nástroj pro zpracování dokumentů na „Docling“

Skenované PDF nebo obrázek vyjde prázdný
  → Zapněte Docling a OCR (nástroj Automaticky nebo Docling)

Webový odkaz vrátí prázdný nebo neúplný obsah
  → Web nejspíš stojí na JavaScriptu
  → V režimu Automaticky přidejte klíč Firecrawl nebo Jina, nebo zapněte Crawl4AI
  → Nebo jako Nástroj pro zpracování URL zvolte „Crawl4AI“ / „Firecrawl“

Zpracování čistých dokumentů je pomalé
  → Nastavte Nástroj pro zpracování dokumentů na „Jednoduchý“ a/nebo vypněte OCR
```

---

## Související

- [Přidávání zdrojů](adding-sources.md) – podporované typy souborů a postup nahrání
- [Environment Reference](../../5-CONFIGURATION/environment-reference.md) (anglicky) – API klíče pro vytahování a ladicí proměnné
- [Advanced Configuration](../../5-CONFIGURATION/advanced.md) (anglicky) – nastavení stahování webů a vytahování obsahu
