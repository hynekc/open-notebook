# Rychlá řešení – nejčastější problémy

Problémy, na které lidé narážejí nejčastěji, s krátkým řešením a odkazem na úplný popis. Příkazy předpokládají dodaný `docker-compose.yml` (služby `surrealdb` a `open_notebook`).

Pro každé řešení, které mění nastavení, platí dvě pravidla:

- Nastavení patří do bloku `environment:` služby `open_notebook`. Proměnná, která je jen v `.env`, se do kontejneru nedostane (výjimkou jsou `OPEN_NOTEBOOK_ENCRYPTION_KEY`, `OPEN_NOTEBOOK_PASSWORD`, `SURREAL_USER` a `SURREAL_PASSWORD`, které compose soubor z `.env` čte).
- Změny použijte příkazem `docker compose up -d`. `docker compose restart` ponechá staré prostředí.

---

## Č. 1: „Nelze se připojit k serveru API“

Rozhraní se načte, ale nedostane se k API.

```bash
curl http://localhost:5055/health     # očekáváno {"status":"healthy"}
docker compose ps                     # open_notebook musí být Up
```

Pokud API odpovídá lokálně, ale ne z prohlížeče: port 5055 musí být z vašeho počítače dostupný, nebo za reverzní proxy musí být `API_URL` nastavené na veřejnou URL. → [Potíže s připojením](connection-issues.md#unable-to-connect-to-api-server)

---

## Č. 2: Chat selže s „No model configured for default for type=chat“

Ještě nejsou přiřazené modely. Projděte [Připojení poskytovatele](../4-AI-PROVIDERS/index.md#connect-a-provider) ve **Spravovat → Modely** až po krok 4 (**Automaticky přiřadit výchozí** ve Výchozím přiřazení modelů). → [Potíže s AI a chatem](ai-chat-issues.md#no-model-configured-for-default-for-typechat)

---

## Č. 3: „Šifrovací klíč není nastaven“

Přístupové údaje poskytovatelů nelze uložit, dokud není v prostředí `open_notebook` nastaveno `OPEN_NOTEBOOK_ENCRYPTION_KEY`. → [Potíže s AI a chatem](ai-chat-issues.md#encryption-key-not-configured)

---

## Č. 4: „Cannot process file“ nebo „Unsupported format“

- Odmítnuto při nahrání se zprávou „… (detected type: …)“: z tohoto typu souboru nelze vytáhnout text. Převeďte ho (PDF, DOCX, TXT…). Obrázky a skenovaná PDF potřebují `OPEN_NOTEBOOK_ENABLE_DOCLING=true`.
- Odmítnuto se zprávou „Request body exceeds the maximum allowed upload size“: soubor je větší než `OPEN_NOTEBOOK_MAX_UPLOAD_SIZE_MB` (výchozí 100 MB). Limit zvyšte; pokud `API_URL` míří na adresu rozhraní, omezuje nahrávání na 100 MB i proxy rozhraní.
- Nahráno, pak **Selhalo**: důvod je v záznamu workeru a ve stavu zdroje. → [Potíže se zpracováním → Neúspěšné zdroje](processing-issues.md#failed-sources)

---

## Č. 5: Zdroje zůstávají „Ve frontě“

Worker na pozadí nezpracovává úlohy. → [Potíže se zpracováním](processing-issues.md#sources-stay-queued-waiting-to-be-processed)

---

## Č. 6: „The AI provider took too long to respond“

Volání modelu trvalo déle než `ESPERANTO_LLM_TIMEOUT` (ve výchozím stavu 180 sekund). Použijte rychlejší model nebo menší kontext, nebo limit zvyšte (pod 600):

```yaml
services:
  open_notebook:
    environment:
      - ESPERANTO_LLM_TIMEOUT=420
```

Ve v1.15.0 se stejné vypršení času po dlouhém čekání zobrazí jako „Could not connect to the AI provider…“. → [Potíže s AI a chatem](ai-chat-issues.md#the-ai-provider-took-too-long-to-respond)

---

## Č. 7: Hledání nic nenajde

- „Vektorové hledání potřebuje embedding model. K dispozici je jen textové hledání.“: přiřaďte **embedding model** ve Spravovat → Modely.
- Embedding model je přiřazen, a stále nic: zdroje přidané před jeho nastavením (nebo po jeho změně) nemají odpovídající vektory. Přestavte je na stránce **Pokročilé**.

→ [Potíže se zpracováním → Hledání](processing-issues.md#search-and-ask)

---

## Č. 8: „Tvorba podcastu selhala“

Otevřete **Podcasty → Epizody**; neúspěšná epizoda ukazuje chybu a tlačítko **Zkusit znovu**.

- „Speaker profile 'X' has no voice model configured“: profily mluvčích dodané s Open Notebookem nemají model převodu textu na řeč. Upravte je v **Podcasty → Profily** a některý vyberte.
- `Voice name ... not supported` nebo `Requested entity was not found`: ID hlasu v profilu není platné pro jeho model TTS (dodané profily používají názvy hlasů OpenAI).
- Zprávy s `NOTE:` vysvětlují příčinu.

→ [Potíže se zpracováním → Selhání podcastů](processing-issues.md#podcast-failures)

---

## Č. 9: Změny nastavení nemají žádný účinek

Upravili jste `.env` (kontejner ho nečte), nebo jste spustili `docker compose restart` (ponechá staré prostředí). Dejte proměnnou do `open_notebook` → `environment:` a spusťte `docker compose up -d`. Co kontejner vidí, ověříte takto:

```bash
# Jen názvy, aby se na obrazovce neobjevila tajemství
docker compose exec open_notebook sh -c 'printenv | cut -d= -f1 | grep -E "OPEN_NOTEBOOK|API_URL|ESPERANTO"'
docker compose exec open_notebook printenv API_URL ESPERANTO_LLM_TIMEOUT   # hodnoty netajných nastavení
```

---

## Č. 10: Ollama není dostupná

Test ukazuje „Cannot connect to Ollama. Check if Ollama server is running.“ Z Dockeru musí být základní URL `http://host.docker.internal:11434` (Linux potřebuje i `extra_hosts`) a na Linuxu musí Ollama naslouchat na `0.0.0.0`. Tím se její API bez ověřování zpřístupní na všech rozhraních, proto port 11434 povolte jen z tohoto hostitele a jeho sítí Dockeru. → [Ollama](../../5-CONFIGURATION/ollama.md#which-base-url-to-use) (anglicky)

---

<a id="11-slow-first-start-or-download-timeouts"></a>
## Č. 11: Pomalý první start nebo vypršení času při stahování

Zveřejněný image má závislosti Pythonu nainstalované. Stahování při startu probíhá, jen když je nastaveno `OPEN_NOTEBOOK_ENABLE_DOCLING` nebo `OPEN_NOTEBOOK_ENABLE_CRAWL4AI`; záznam pak ukazuje `[entrypoint] Installing ...`. Na pomalé síti může první start trvat dlouho. Pokud instalace selže, záznam hlásí `[entrypoint] WARNING: ... install FAILED` a aplikace se spustí bez daného nástroje; restartem to zkusíte znovu. Balíčky Pythonu se instalují nástrojem `uv`, takže v prostředí `open_notebook` fungují jeho standardní proměnné: `UV_HTTP_TIMEOUT` (sekundy na jedno stažení) pro pomalá připojení a `UV_DEFAULT_INDEX` pro použití zrcadla PyPI.

---

## Obnovení do výchozího stavu

- **Aktualizace:** `docker compose pull && docker compose up -d` (u vlastního buildu `git pull` a `docker compose build`). Předtím zálohujte ([Advanced → Backup & Restore](../../5-CONFIGURATION/advanced.md#backup--restore), anglicky).
- **Začít od nuly:** `docker compose down`, pak smažte `./notebook_data` a `./surreal_data`. `docker compose down -v` je nesmaže: jsou to připojené složky (bind mounts), ne svazky.

---

## Stále nevíte?

- Vyhledejte přesné znění zprávy v [přehledu řešení potíží](index.md).
- Zeptejte se na [Discordu](https://discord.gg/37XJPXfz2w) nebo v [GitHub Discussions](https://github.com/lfnovo/open-notebook/discussions/categories/q-a) (anglicky).
