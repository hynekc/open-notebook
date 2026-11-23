# Řešení potíží

Najděte svůj problém podle zprávy, kterou vidíte, a pokračujte odkazem. Pokud žádnou zprávu nemáte, začněte [Rychlými řešeními](quick-fixes.md).

Zprávy jsou uvedeny tak, jak je aplikace zobrazuje: zprávy rozhraní česky, zprávy ze serveru a ze záznamů (logů) anglicky.

---

## Podle zprávy

### V prohlížeči

| Zpráva | Kde hledat |
|---------|---------------|
| „Nelze se připojit k serveru API“ („Unable to Connect to API Server“) | [Potíže s připojením](connection-issues.md#unable-to-connect-to-api-server) |
| „Nelze se připojit k serveru. Zkontrolujte, zda běží API.“ (přihlašovací stránka) | [Potíže s připojením](connection-issues.md#unable-to-connect-to-api-server) |
| „Připojení k databázi selhalo“ („Database Connection Failed“) | [Potíže s připojením](connection-issues.md#database-connection-failed) |
| „Neplatné heslo“ („Invalid password“) | [Potíže s připojením → Potíže s přihlášením](connection-issues.md#login-problems) |
| „Šifrovací klíč není nastaven“ | [Potíže s AI a chatem](ai-chat-issues.md#encryption-key-not-configured) |
| „Chyba dešifrování“ u přístupových údajů | [Potíže s AI a chatem](ai-chat-issues.md#decryption-error) |
| „Nalezeny proměnné prostředí“ | [Potíže s AI a chatem](ai-chat-issues.md#environment-variables-detected) |
| „No model configured for default for type=…“ | [Potíže s AI a chatem](ai-chat-issues.md#no-model-configured-for-default-for-typechat) |
| „Model is not a LanguageModel: …“ | [Potíže s AI a chatem](ai-chat-issues.md#model-is-not-a-languagemodel-) |
| „The AI provider took too long to respond…“ | [Potíže s AI a chatem](ai-chat-issues.md#the-ai-provider-took-too-long-to-respond) |
| „Could not connect to the AI provider…“ | [Potíže s AI a chatem](ai-chat-issues.md#could-not-connect-to-the-ai-provider-please-check-your-network-connection-and-provider-url) (ve v1.15.0 to může být i vypršení času) |
| „Authentication failed. Please check your API key…“ | [Potíže s AI a chatem](ai-chat-issues.md#authentication-failed-please-check-your-api-key-in-manage---models) |
| „Rate limit exceeded…“ | [Potíže s AI a chatem](ai-chat-issues.md#rate-limit-exceeded-please-wait-a-moment-and-try-again) |
| „Content too large for the selected model…“ | [Potíže s AI a chatem](ai-chat-issues.md#content-too-large-for-the-selected-model) |
| „The AI provider is temporarily unavailable…“ | [Potíže s AI a chatem](ai-chat-issues.md#the-ai-provider-is-temporarily-unavailable-please-try-again-in-a-few-minutes) |
| „The model returned an empty response…“ | [Potíže s AI a chatem](ai-chat-issues.md#the-model-returned-an-empty-response-try-again-or-pick-a-different-model-if-this-keeps-happening) |
| „AI service error: …“ | [Potíže s AI a chatem](ai-chat-issues.md#ai-service-error-) |
| „timeout of 600000ms exceeded“ | [Potíže s AI a chatem](ai-chat-issues.md#timeout-of-600000ms-exceeded) |
| „Cannot connect to server. Check the URL is correct.“ (tlačítko Test) | [Potíže s AI a chatem → Test selže](ai-chat-issues.md#test-fails) |
| „Cannot connect to Ollama. Check if Ollama server is running.“ | [Ollama](../../5-CONFIGURATION/ollama.md#troubleshooting) (anglicky) |
| „U tohoto poskytovatele nebyly nalezeny žádné modely“ | [Potíže s AI a chatem](ai-chat-issues.md#no-models-found-from-this-provider) |
| Zdroj zůstává „Ve frontě“ | [Potíže se zpracováním](processing-issues.md#sources-stay-queued-waiting-to-be-processed) |
| Zdroj ukazuje „Selhalo“ | [Potíže se zpracováním → Neúspěšné zdroje](processing-issues.md#failed-sources) |
| „Request body exceeds the maximum allowed upload size“ | [Potíže se zpracováním → Nahrávání](processing-issues.md#uploads-rejected) |
| „… (detected type: …)“ při nahrávání | [Potíže se zpracováním → Nahrávání](processing-issues.md#uploads-rejected) |
| „Tato funkce potřebuje embedding model…“ / „Vektorové hledání potřebuje embedding model…“ | [Potíže se zpracováním → Hledání](processing-issues.md#search-and-ask) |
| „The strategy model returned no search terms…“ (dotaz) | [Potíže se zpracováním → Hledání](processing-issues.md#ask-fails-with-the-strategy-model-returned-no-search-terms-for-this-question) |
| „Tento zdroj nemá žádný text, který by šlo transformovat“ | [Potíže se zpracováním](processing-issues.md#this-source-has-no-text-content-to-transform) |
| Epizoda podcastu „Selhalo“ | [Potíže se zpracováním → Selhání podcastů](processing-issues.md#podcast-failures) |
| Chyba CORS v konzoli prohlížeče | [Potíže s připojením](connection-issues.md#cors-errors-in-the-browser-console) |
| `502 Bad Gateway` / `504 Gateway Timeout` | [Reverse Proxy](../../5-CONFIGURATION/reverse-proxy.md#troubleshooting) (anglicky) |

### Ve záznamech (logech)

Záznamy přečtete příkazy `docker compose logs open_notebook` (API, worker a rozhraní dohromady) a `docker compose logs surrealdb`.

| Řádek záznamu | Kde hledat |
|----------|---------------|
| `Database is not reachable yet (attempt n/12)` | [Potíže s připojením](connection-issues.md#database-connection-failed) |
| `OPEN_NOTEBOOK_ENCRYPTION_KEY not set. API key encryption will fail…` | [Potíže s AI a chatem](ai-chat-issues.md#encryption-key-not-configured) |
| `Failed to decrypt credential …` | [Potíže s AI a chatem](ai-chat-issues.md#decryption-error) |
| `content-core extraction failed (…)` | [Potíže se zpracováním → Neúspěšné zdroje](processing-issues.md#failed-sources) |
| `Configured … engine '…' is selected in Content Settings but its runtime is not available` | [Potíže se zpracováním](processing-issues.md#the-selected-engine-isnt-used) |
| `gave up: worker entered FATAL state` / `exited: worker` | [Potíže se zpracováním](processing-issues.md#sources-stay-queued-waiting-to-be-processed) |
| `[entrypoint] WARNING: ... install FAILED` | [Rychlá řešení č. 11](quick-fixes.md#11-slow-first-start-or-download-timeouts) |
| `CORS_ORIGINS is not set — API accepts cross-origin requests from any origin` | Připomínka, ne chyba. Viz [Security → CORS Origins](../../5-CONFIGURATION/security.md#cors-origins) (anglicky) |
| `[SSL: CERTIFICATE_VERIFY_FAILED]` | [Potíže s připojením → Chyby SSL](connection-issues.md#ssl-errors-with-a-provider) |

---

## Návody

| Návod | Co pokrývá |
|-------|--------|
| [Rychlá řešení](quick-fixes.md) | Nejčastější problémy, krátké odpovědi |
| [Potíže s připojením](connection-issues.md) | Rozhraní se nedostane k API, API se nedostane k databázi, přihlášení, CORS, proxy |
| [Potíže s AI a chatem](ai-chat-issues.md) | Nastavení modelů, chyby poskytovatelů, časové limity, přístupové údaje a šifrovací klíč, kvalita odpovědí |
| [Potíže se zpracováním](processing-issues.md) | Zdroje ve frontě a neúspěšné zdroje, nahrávání, hledání a vektory, transformace, podcasty |
| [Časté otázky](faq.md) | Otázky, které nejsou chybami: umístění dat, zálohy, náklady, provoz bez internetu |

---

## První kontroly

```bash
docker compose ps                                  # běží surrealdb i open_notebook (Up)?
curl -s http://localhost:5055/health               # {"status":"healthy"}
curl -s http://localhost:5055/api/config           # "dbStatus": "online"
docker compose logs --since 10m open_notebook | grep -iE "error|warning|critical"
docker compose exec open_notebook sh -c 'printenv | cut -d= -f1 | grep -E "OPEN_NOTEBOOK|SURREAL|API_URL|ESPERANTO"'   # jen názvy
```

Když výstup sdílíte v hlášení nebo chatu, nikdy neuvádějte hodnoty `OPEN_NOTEBOOK_ENCRYPTION_KEY`, `OPEN_NOTEBOOK_PASSWORD` ani `SURREAL_PASSWORD`.

Nastavení patří do bloku `environment:` služby `open_notebook` a projeví se po `docker compose up -d`; `docker compose restart` ponechá staré prostředí a proměnná, která je jen v `.env` (kromě čtyř proměnných, které compose soubor z `.env` výslovně čte), se do kontejneru nedostane. Všechny proměnné: [Environment Reference](../../5-CONFIGURATION/environment-reference.md) (anglicky).

---

## Kde získat pomoc

1. Vyhledejte přesné znění zprávy v [GitHub Issues](https://github.com/lfnovo/open-notebook/issues).
2. Zeptejte se na [Discordu](https://discord.gg/37XJPXfz2w) nebo v [GitHub Discussions](https://github.com/lfnovo/open-notebook/discussions/categories/q-a) (anglicky).
3. U reprodukovatelné chyby založte issue s: přesným zněním zprávy, postupem reprodukce, příslušnou částí `docker compose logs open_notebook` (bez klíčů a hesel), verzí Open Notebooku, způsobem provozu (Docker, jeden kontejner, ze zdrojového kódu) a použitým poskytovatelem.

Bezpečnostní problémy: nezakládejte veřejné issue, viz [SECURITY.md](../../../SECURITY.md).
