# Potíže s AI a chatem – modely, přístupové údaje a chyby

Chyby poskytovatelů AI, nastavení modelů a systému přístupových údajů. Každá položka začíná zprávou, kterou vidíte (zprávy ze serveru jsou anglicky); v chatu se objeví jako červené oznámení, u úloh na pozadí (poznatky, transformace, podcasty) v chybě úlohy.

Úlohy na pozadí přechodné chyby poskytovatele (limity požadavků, výpadky) samy několikrát zopakují; chyby nastavení, příliš velký obsah a prázdné odpovědi se neopakují. Chat a dotazy se neopakují: zprávu pošlete znovu.

---

## Nastavení modelů

### "No model configured for default for type=chat"

Úplná zpráva: `No model configured for default for type=chat. Please go to Manage → Models and configure a default model for 'chat'.` Typ může být i `transformation`, `tools` nebo jiná role.

**Příčina:** k této roli není přiřazen žádný model. Nová instalace nemá žádný.

**Řešení:** **Spravovat → Modely → Výchozí přiřazení modelů**: zvolte model pro každou roli, nebo klikněte na **Automaticky přiřadit výchozí**. Pokud jsou seznamy prázdné, ještě jste nezaregistrovali modely: postupujte podle [Připojení poskytovatele](../4-AI-PROVIDERS/index.md#connect-a-provider).

### "Model is not a LanguageModel: …"

Úplná zpráva: `Model is not a LanguageModel: <model>. Please check that the model configured for '<role>' is a language model, not an embedding or speech model.`

**Příčina:** k jazykové roli (model chatu, transformací, nástrojů nebo pro velký kontext) je přiřazen embedding model, model převodu textu na řeč nebo řeči na text. Stává se to, když byl model zaregistrován s chybným **Typem modelu**.

**Řešení:** přiřaďte k roli jazykový model. Je-li model zaregistrován s chybným typem, smažte ho ve Spravovat → Modely a přidejte znovu se správným typem.

### Model, který fungoval, teď selhává s „model not found“ nebo „does not exist“

Model byl u poskytovatele odstraněn (vyřazen, nebo smazán z Ollamy či vLLM). Ve Vyhledat modely u konfigurace zjistěte, co je teď k dispozici, přidejte náhradu a znovu přiřaďte výchozí role, které používaly starý model.

---

## Chyby poskytovatelů

### "The AI provider took too long to respond"

Úplná zpráva: `The AI provider took too long to respond. Try again, use a faster model, or raise ESPERANTO_LLM_TIMEOUT (180 seconds by default).`

v1.15.0 pro stejné vypršení času ukazuje `Could not connect to the AI provider. Please check your network connection and provider URL.`; pokud se tato zpráva objeví po dlouhém čekání, a ne okamžitě, jde o vypršení času.

**Příčina:** jedno volání modelu trvalo déle než `ESPERANTO_LLM_TIMEOUT` (ve výchozím stavu 180 sekund, platí pro všechny poskytovatele včetně Ollamy). Typické u velkých lokálních modelů na CPU, u prvního požadavku během načítání modelu, u velmi velkých kontextů nebo u modelů s uvažováním, které přemýšlejí minuty.

**Řešení:**

1. Zkuste rychlejší model, nebo zahrňte méně obsahu (viz [Content too large](#content-too-large-for-the-selected-model)).
2. Zvyšte limit ve službě `open_notebook` a použijte ho příkazem `docker compose up -d` (`restart` ponechá starou hodnotu):
   ```yaml
   environment:
     - ESPERANTO_LLM_TIMEOUT=420   # držte pod 600
   ```
   Zůstaňte pod 600 sekundami: webové rozhraní přestane čekat po 10 minutách a tento limit nelze ve zveřejněném image změnit.
3. S jedním lokálním GPU nastavte také `OPEN_NOTEBOOK_WORKER_MAX_TASKS=1`, aby o něj úlohy na pozadí nesoupeřily.

Více pro Ollamu: [Ollama → Timeouts](../../5-CONFIGURATION/ollama.md#timeouts-with-slow-models) (anglicky).

### "timeout of 600000ms exceeded"

Prohlížeč to po 10 minutách vzdal. Něco je pomalejší, než rozhraní dovolí, obvykle proto, že `ESPERANTO_LLM_TIMEOUT` byl zvýšen nad 600 nebo požadavek drží reverzní proxy. Snižte `ESPERANTO_LLM_TIMEOUT` pod 600, aby server selhal dřív a se srozumitelnou zprávou, a zkontrolujte časové limity proxy ([Reverse Proxy → Timeouts](../../5-CONFIGURATION/reverse-proxy.md#timeouts), anglicky).

### "Could not connect to the AI provider. Please check your network connection and provider URL."

Zobrazí se okamžitě (ne po dlouhém čekání): poskytovatel je zcela nedostupný.

- Lokální servery (Ollama, vLLM, LM Studio, Speaches): **základní URL** konfigurace musí být dostupná zevnitř kontejneru. `localhost` je tam kontejner sám; použijte `host.docker.internal` nebo název služby v compose (např. `http://vllm-qwen:8000/v1`). Viz [Ollama](../../5-CONFIGURATION/ollama.md#which-base-url-to-use) a [OpenAI-Compatible](../../5-CONFIGURATION/openai-compatible.md#base-url-from-inside-docker) (anglicky).
- Cloudoví poskytovatelé: server nemá přístup k internetu, nebo potřebuje `HTTP_PROXY`/`HTTPS_PROXY` ([Environment Reference](../../5-CONFIGURATION/environment-reference.md#outbound-proxy), anglicky).
- Endpoint HTTPS s vlastním certifikátem: nastavte `ESPERANTO_SSL_CA_BUNDLE` ([Advanced → SSL](../../5-CONFIGURATION/advanced.md#ssl-for-self-signed-providers), anglicky).

Tlačítko **Test** u konfigurace uvede konkrétnější důvod („Cannot connect to server. Check the URL is correct.“, „Connection timed out. Check if server is accessible.“).

### "Authentication failed. Please check your API key in Manage -> Models."

**Příčina:** poskytovatel klíč odmítl (chybný, zrušený, nebo pro jiný region či projekt). v1.15.0 ukazuje stejnou zprávu se zastaralou cestou „Settings -> Credentials“.

**Řešení:** ve Spravovat → Modely klikněte u konfigurace poskytovatele na **Test**. Pokud hlásí „Invalid API key“, vytvořte u poskytovatele nový klíč a upravte konfiguraci (pole klíče nechte prázdné, chcete-li ponechat starý; napište nový, chcete-li ho nahradit). U MiniMax a SiliconFlow ověřte, že region klíče odpovídá **základní URL** ([AI Providers](../../5-CONFIGURATION/ai-providers.md#minimax), anglicky).

### "Rate limit exceeded. Please wait a moment and try again."

Poskytovatel vrátil HTTP 429: příliš mnoho požadavků, nebo účtu došla kvóta či kredit. Počkejte a zkuste to znovu, zkontrolujte vyúčtování účtu, nebo snižte `OPEN_NOTEBOOK_WORKER_MAX_TASKS`, aby hromadné zpracování posílalo méně požadavků najednou.

### "Content too large for the selected model"

Úplná zpráva: `Content too large for the selected model. Try using a smaller selection or a model with a larger context window.`

**Příčina:** prompt (zdroje v kontextu plus historie chatu) přesahuje kontextové okno modelu.

**Řešení:**

- V chatu se sešitem zahrňte méně zdrojů, nebo je přepněte z „Celý obsah“ na „Jen poznatky“.
- Použijte model s větším oknem. Open Notebook automaticky přepne na **model pro velký kontext**, když obsah přesáhne asi 105 000 tokenů, proto k této roli ve Výchozím přiřazení modelů přiřaďte model s velkým oknem.
- Začněte novou relaci chatu a zbavte se dlouhé historie.
- U vLLM zkontrolujte parametr `--max-model-len` serveru; větší okno vyžaduje víc paměti na KV cache.

**Ollama tuto chybu nehlásí.** Když prompt přesáhne **Kontextové okno (num_ctx)** konfigurace (ve výchozím stavu 8192 tokenů), Ollama potichu zahodí začátek promptu. Odpovědi pak ignorují vaše zdroje nebo dřívější zprávy. Pokud to hardware dovolí, zvyšte **Kontextové okno (num_ctx)** u konfigurace Ollamy ve Spravovat → Modely; viz [Ollama → Context window](../../5-CONFIGURATION/ollama.md#context-window-num_ctx) (anglicky).

### "The request payload is too large for the AI provider"

Poskytovatel odmítl velikost požadavku (HTTP 413). Zmenšete obsah jako výše, nebo použijte poskytovatele s vyššími limity.

### "The AI provider is temporarily unavailable. Please try again in a few minutes."

Poskytovatel vrátil chybu serveru (500, 502, 503 nebo „overloaded“). Počkejte a zkuste to znovu, nebo přepněte na jiný model či poskytovatele. Zkontrolujte stavovou stránku poskytovatele (u lokálního vLLM jeho záznam).

### "AI service error: …"

Chyba, kterou Open Notebook nerozpozná; zbytek zprávy je vlastní (zkrácený) text poskytovatele. Obvykle problém pojmenuje (nepodporovaný parametr, obsahová pravidla, přístup k modelu). Celá chyba je v záznamu: `docker compose logs open_notebook | grep -i "Unclassified LLM error"`.

### "The model returned an empty response. Try again, or pick a different model if this keeps happening."

Model odpověděl bez textu. Časté u modelů s uvažováním, které celý výstupní rozpočet spotřebují na přemýšlení, nebo u modelů s malým výstupním limitem. Zkuste to znovu, nebo pro danou roli zvolte model bez uvažování. U dotazů se stejný problém projeví jako „The strategy model returned no search terms for this question“ nebo „The final answer model returned an empty response“; zvolte jiné modely v pokročilém výběru modelů na stránce dotazů.

---

## Přístupové údaje a šifrování

<a id="encryption-key-not-configured"></a>
### „Šifrovací klíč není nastaven“

Zobrazuje se ve **Spravovat → Modely** a jako pruh: „Pro bezpečné ukládání přístupových údajů nastavte proměnnou prostředí OPEN_NOTEBOOK_ENCRYPTION_KEY.“ Uložení přístupových údajů selže se zprávou `Encryption key not configured. Set OPEN_NOTEBOOK_ENCRYPTION_KEY to enable storing API keys.` a záznam API ukazuje `OPEN_NOTEBOOK_ENCRYPTION_KEY not set. API key encryption will fail until this is configured.`

**Řešení:** nastavte klíč v souboru `.env` vedle `docker-compose.yml` (dodaný compose soubor ho čte) a spusťte `docker compose up -d`. Upravit přímo řádek `OPEN_NOTEBOOK_ENCRYPTION_KEY` v compose souboru je také možné.

```text
OPEN_NOTEBOOK_ENCRYPTION_KEY=<vygenerovany-klic>
```

Hodnotu si vygenerujte sami, například příkazem `openssl rand -hex 32` (ve Windows viz [Set your encryption key](../../1-INSTALLATION/docker-compose.md#step-2-set-your-encryption-key), anglicky). Nepoužívejte ukázkovou hodnotu.

Neponechávejte zástupnou hodnotu `change-me-to-a-secret-string`. Viz [Security](../../5-CONFIGURATION/security.md#api-key-encryption) (anglicky).

<a id="decryption-error"></a>
### „Chyba dešifrování“

U přístupových údajů ve Spravovat → Modely: „API klíč této konfigurace se nepodařilo dešifrovat. Šifrovací klíč se možná změnil. Konfiguraci smažte a vytvořte znovu se správným klíčem.“ Záznam API ukazuje `Failed to decrypt credential <id>: Decryption failed: ...`.

**Příčina:** `OPEN_NOTEBOOK_ENCRYPTION_KEY` není hodnota, se kterou byly přístupové údaje uloženy. Časté důvody: klíč byl změněn, nový kontejner byl vytvořen bez něj (například jiný compose soubor nebo překlep), nebo byla databáze obnovena do instance s jiným klíčem.

**Řešení:** pokud starý klíč máte, vraťte ho a spusťte `docker compose up -d`; přístupové údaje začnou znovu fungovat. Jinak každé dotčené přístupové údaje smažte a přidejte znovu. Test, Modely a Upravit jsou u přístupových údajů v tomto stavu neaktivní.

Přístupové údaje uložené ve v1.15.0 nebo novější nepřečtou ani starší verze. Po návratu ke starší verzi obnovte zálohu pořízenou před aktualizací ([Security → Upgrading to PBKDF2](../../5-CONFIGURATION/security.md#upgrading-to-pbkdf2-v1150), anglicky).

<a id="environment-variables-detected"></a>
### „Nalezeny proměnné prostředí“

Klíče poskytovatelů jsou nastavené jako proměnné prostředí (`OPENAI_API_KEY` apod.). Jako záloha stále fungují, ale **Přesunout do databáze** z nich udělá běžné přístupové údaje. Potom proměnné z konfigurace odstraňte. Viz [Environment Reference → Legacy](../../5-CONFIGURATION/environment-reference.md#legacy-ai-provider-variables-deprecated) (anglicky).

<a id="test-fails"></a>
### Test selže

| Zpráva | Význam |
|---------|---------|
| „Invalid API key“ | Poskytovatel klíč odmítl |
| „API key lacks required permissions“ | Klíč je platný, ale nemůže vypsat nebo používat modely (omezený klíč, oprávnění projektu) |
| „Model not found on this provider“ | Testovací model není pro tento klíč dostupný; Vyhledat modely přesto ukáže, co dostupné je |
| „Cannot connect to server. Check the URL is correct.“ | Na základní URL nic neodpovídá, nebo selhalo ověření TLS |
| „Cannot connect to Ollama. Check if Ollama server is running.“ | Viz [Ollama troubleshooting](../../5-CONFIGURATION/ollama.md#troubleshooting) (anglicky) |
| „Connection timed out. Check if server is accessible.“ | Firewall, chybná adresa, nebo vytížený server |

<a id="no-models-found-from-this-provider"></a>
### „U tohoto poskytovatele nebyly nalezeny žádné modely“

Vyhledat modely vrátilo prázdný seznam. Lokální servery: nejdřív model načtěte nebo stáhněte. Brány a kompatibilní servery, které modely nevypisují: napište ID modelu do vyhledávacího pole a klikněte na **Přidat „…“**.

---

## Kvalita odpovědí

Nejde o chyby, ale o nejčastější stížnosti.

- **Odpovědi ignorují moje zdroje.** V chatu se sešitem má každá karta zdroje nastavení kontextu, které přepíná mezi „Nezahrnuto do chatu“, „Jen poznatky“ a „Celý obsah“. Ověřte, že zdroje, na kterých vám záleží, jsou zahrnuté. U Ollamy zkontrolujte i [kontextové okno](../../5-CONFIGURATION/ollama.md#context-window-num_ctx).
- **„Jen poznatky“ dává povrchní odpovědi.** Posílá poznatky zdroje, ne jeho text. U zdrojů, kterých se otázka týká, použijte „Celý obsah“.
- **Obecné nebo chybné odpovědi.** Ptejte se konkrétně, jmenujte zdroj nebo kapitolu a pro roli modelu chatu použijte silnější model. Zkontrolujte citace: ukazují, které zdroje odpověď použila.
- **Dotaz nenajde něco, co tam je.** Dotaz prohledává vektory; zdroje bez vektorů nenajde. Viz [Potíže se zpracováním → Hledání](processing-issues.md#search-and-ask).

Více: [Efektivní chat](../3-USER-GUIDE/chat-effectively.md).

---

## Související

- [AI Providers](../../5-CONFIGURATION/ai-providers.md) (anglicky) — nastavení jednotlivých poskytovatelů
- [Potíže se zpracováním](processing-issues.md) — zdroje, hledání, podcasty
- [Potíže s připojením](connection-issues.md) — rozhraní, API a databáze
- [Environment Reference](../../5-CONFIGURATION/environment-reference.md) (anglicky)
