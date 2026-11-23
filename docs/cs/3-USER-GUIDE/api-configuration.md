# Nastavení modelů a API

Poskytovatele AI připojíte a výchozí modely zvolíte ve **Spravovat → Modely**. API klíče se ukládají šifrovaně do databáze; po nastavení šifrovacího klíče už není potřeba upravovat žádné soubory.

Stránka má shora dolů tři části:

1. Pruh **Nalezeny proměnné prostředí** (jen pokud máte klíče poskytovatelů v proměnných prostředí; viz [Přesun z proměnných prostředí](#migrating-from-environment-variables)).
2. **Výchozí přiřazení modelů**: který model používá která funkce.
3. **Sekce poskytovatelů**: jedna pro každého poskytovatele, se stavem *Nastaveno* nebo *Nenastaveno*, jeho konfiguracemi a jejich modely.

---

<a id="encryption-setup"></a>
## Nastavení šifrování

Ukládání API klíčů vyžaduje `OPEN_NOTEBOOK_ENCRYPTION_KEY`. Dokud není nastaven, stránka Modely ukazuje **Šifrovací klíč není nastaven** a konfigurace nelze uložit.

Nastavte ho u služby `open_notebook` ve svém `docker-compose.yml` (nebo v souboru `.env` vedle něj):

```yaml
services:
  open_notebook:
    environment:
      - OPEN_NOTEBOOK_ENCRYPTION_KEY=<vas-vygenerovany-tajny-klic>
```

Nahraďte `<vas-vygenerovany-tajny-klic>` dlouhým náhodným tajným řetězcem, který si sami vygenerujete. Nekopírujte ukázkovou hodnotu z žádného návodu. Vhodnou hodnotu vypíše kterýkoli z těchto příkazů:

```bash
openssl rand -hex 32                                   # macOS, Linux
```

```powershell
[guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")   # Windows PowerShell
```

Změnu použijete novým vytvořením kontejneru (`docker compose up -d`).

> **Hodnotu uchovejte v bezpečí a neměňte ji.** Pokud se změní, uložené API klíče nepůjde dešifrovat a jejich karty budou ukazovat **Chyba dešifrování**, dokud původní hodnotu neobnovíte. Pokud je původní hodnota ztracená, uložené klíče obnovit nelze: tyto konfigurace smažte a přidejte znovu.

`OPEN_NOTEBOOK_ENCRYPTION_KEY` i `OPEN_NOTEBOOK_PASSWORD` přijímají také variantu `_FILE` (například `OPEN_NOTEBOOK_ENCRYPTION_KEY_FILE=/run/secrets/encryption_key`) pro Docker secrets. Šifrovací schéma, aktualizaci uložených klíčů a zálohy popisuje [Security](../../5-CONFIGURATION/security.md) (anglicky).

---

## Připojení poskytovatele

Postup krok za krokem (**Přidat konfiguraci** → **Otestovat připojení** → dialog **Vyhledat modely** → **Přidat (N)** → **Automaticky přiřadit výchozí** → první chat) je v části [Poskytovatelé AI → Připojení poskytovatele](../4-AI-PROVIDERS/index.md#connect-a-provider). Stručně: přidejte konfiguraci poskytovatele, otestujte ji, otevřete její dialog **Vyhledat modely** (tlačítko *Synchronizovat modely*), zvolte **Typ modelu**, zaškrtněte modely (nebo napište název, který v seznamu není) a klikněte na **Přidat (N)**. Opakujte pro každý potřebný typ modelu.

Modely se pak zobrazí pod konfigurací, každý s ikonou **Otestovat model** (pošle modelu malý požadavek) a ikonou smazání.

Kteří poskytovatelé nabízejí jaké typy modelů (jazykové, embedding, řečové), uvádí [Poskytovatelé AI](../4-AI-PROVIDERS/index.md); poznámky k nastavení jednotlivých poskytovatelů jsou v [AI Providers configuration](../../5-CONFIGURATION/ai-providers.md), [Ollama](../../5-CONFIGURATION/ollama.md), [OpenAI-compatible](../../5-CONFIGURATION/openai-compatible.md) a [oMLX](../../5-CONFIGURATION/omlx.md) (anglicky).

> Několik poskytovatelů nabízí jen jazykové modely. Dotazy a vektorové hledání potřebují i embedding model; podcasty potřebují model převodu textu na řeč; nahrané zvukové a video soubory a videa z YouTube bez přepisu potřebují model převodu řeči na text. Tyto modely mohou být od jiného poskytovatele.

### Více konfigurací jednoho poskytovatele

Poskytovatel může mít více konfigurací, například dva API klíče nebo dva servery Ollama či vLLM. Každý model je propojen s konfigurací, ze které byl přidán, a používá její klíč a URL.

---

## Výchozí přiřazení modelů

Tato část určuje, který model používá která funkce. Pole označená hvězdičkou jsou povinná.

| Přiřazení | Použití | Když není nastaveno |
|------------|----------|-----------|
| **Model chatu** * | Chat se sešitem, chat se zdrojem; dotazy, pokud není nastaven model nástrojů | Chat a dotazy selžou |
| **Embedding model** * | Vektorizace zdrojů, poznámek a poznatků; vektorové hledání; dotazy | Dotazy a vektorové hledání nejsou k dispozici |
| **Model transformací** | Transformace (poznatky), názvy poznámek vytvořených AI | Použije se model chatu |
| **Model nástrojů** | Dotazy: výchozí pro všechny tři fáze na stránce dotazů a pro požadavky API bez určených modelů | Použije se model chatu |
| **Model pro velký kontext** | Každý prompt delší než asi 105 000 tokenů | Použije se model chatu |
| **Model převodu textu na řeč** | Podcasty: hlasový model pro profily mluvčích, které nemají vlastní | Profily mluvčích bez hlasového modelu nemohou tvořit podcasty |
| **Model převodu řeči na text** | Přepis nahraných zvukových a video souborů a videí z YouTube bez přepisu | Tyto zdroje nelze přepsat (videa z YouTube s přepisem fungují dál) |

Dokud chybí model chatu nebo embedding model, upozornění nabízí **Automaticky přiřadit výchozí**, které tyto dva doplní z přidaných modelů (ostatní pozice zůstanou beze změny). Pokud se zobrazí *Nejsou k dispozici žádné modely k přiřazení*, nejdřív nějaké modely přidejte.

Podcasty berou model osnovy a scénáře z profilu epizody a hlasový model z profilu mluvčích; model převodu textu na řeč zde je jen záložní pro profily mluvčích bez vlastního hlasového modelu (viz [Tvorba podcastů](creating-podcasts.md)).

**Změna embedding modelu** otevře potvrzení: stávající vektory vytvořil starý model a nebudou odpovídat novým dotazům. Zvolte **Změnit a přejít k přestavbě** pro přechod na **Pokročilé → Znovu vytvořit vektory**, nebo **Jen změnit model** a přestavbu udělejte později.

---

<a id="migrating-from-environment-variables"></a>
## Přesun z proměnných prostředí

Pokud jsou API klíče poskytovatelů nastavené jako proměnné prostředí (starší způsob), stránka Modely ukazuje **Nalezeny proměnné prostředí**.

1. Klikněte na **Přesunout do databáze**.
2. Pro každého poskytovatele, který má klíče v prostředí a v databázi ještě **nemá** žádnou konfiguraci, se z těchto klíčů vytvoří konfigurace (šifrovaně). Poskytovatelé, kteří už konfiguraci mají, se přeskočí.
3. Proměnné prostředí se nemění. Jakmile přesunuté konfigurace fungují, můžete klíče z prostředí odstranit. `OPEN_NOTEBOOK_ENCRYPTION_KEY` ponechte.

---

## Úprava nebo smazání konfigurace

- **Upravit** (ikona tužky): změna názvu, URL nebo dalších polí. Pole **API klíč** nechte prázdné, chcete-li uložený klíč ponechat.
- **Smazat** (ikona koše): pokud má konfigurace modely, můžete v poli **Přesunout modely do** vybrat jinou konfiguraci stejného poskytovatele a kliknout na **Přesunout a smazat**, nebo kliknout na **Smazat i s modely** a smazat i modely. Pak zkontrolujte **Výchozí přiřazení modelů**, zda některé z nich smazané modely nepoužívalo.

---

## Řešení potíží

| Příznak | Co zkontrolovat |
|---------|---------------|
| Konfiguraci nelze uložit, *Šifrovací klíč není nastaven* | Nastavte `OPEN_NOTEBOOK_ENCRYPTION_KEY` a kontejner vytvořte znovu |
| **Chyba dešifrování** u konfigurace | Šifrovací klíč se změnil. Obnovte původní hodnotu; pokud je ztracená, konfiguraci smažte a přidejte znovu |
| Test připojení selže | Klíč, základní URL (z Dockeru znamená `localhost` kontejner sám), firewall nebo proxy |
| Model není ve Vyhledat modely | Napište jeho přesný název do vyhledávacího pole a přidejte ho |
| Upozornění *Chybí povinné modely* | Nastavte model chatu a embedding model, nebo klikněte na **Automaticky přiřadit výchozí** |

Více v [Řešení potíží](../6-TROUBLESHOOTING/index.md).
