# Časté otázky

Otázky, které se netýkají chybové zprávy. Chyby najdete v [přehledu řešení potíží](index.md).

---

## Obecně

### Co je Open Notebook?

Open-source asistent pro práci s podklady, který provozujete sami, v duchu Google NotebookLM: zdroje shromažďujete do sešitů, chatujete s nimi, hledáte v nich, spouštíte transformace, které z nich vytahují poznatky, a tvoříte podcasty. Poskytovatele AI volíte sami, včetně plně lokálních.

### Čím se liší od Google NotebookLM?

- **Provozujete ho sami.** Sešity, zdroje a poznámky zůstávají ve vaší vlastní databázi.
- **Modely volíte vy.** Podporováno je 24 poskytovatelů, od OpenAI a Anthropicu po Ollamu nebo vLLM na vašem vlastním stroji. Viz [AI Providers](../../5-CONFIGURATION/ai-providers.md) (anglicky).
- **Je open source.** Můžete ho číst, měnit a rozšiřovat.

Váš stroj opouští to, co posíláte nastaveným poskytovatelům AI: když chatujete, transformujete nebo tvoříte podcast, příslušný obsah zdrojů jde danému poskytovateli. Když Ollama, vLLM, LM Studio nebo Speaches běží na vašem vlastním hardwaru, obsah zůstává tam; vzdálený endpoint ho dostane jako kterýkoli jiný poskytovatel.

### Lze ho používat bez internetu?

Ano, s lokálními modely pro vše: Ollama, vLLM, LM Studio nebo oMLX pro chat a embeddingy a [Speaches](../../5-CONFIGURATION/local-tts.md) pro řeč. Přidávání webových stránek a videí z YouTube samozřejmě internet potřebuje.

### Co mohu přidat jako zdroj?

Soubory (PDF, Word, PowerPoint, Excel, EPUB, OpenDocument, HTML, prostý text a Markdown; zvuk a video jako MP3, WAV, M4A a MP4), webové stránky, videa z YouTube a vložený text. Obrázky a skenované dokumenty potřebují volitelný nástroj Docling (`OPEN_NOTEBOOK_ENABLE_DOCLING=true`). Zvuk, video a videa z YouTube bez titulků potřebují model převodu řeči na text. Viz [Přidávání zdrojů](../3-USER-GUIDE/adding-sources.md).

### Kolik to stojí?

Software je zdarma. Použití AI účtují poskytovatelé za tokeny, znaky nebo minuty podle svých cen; lokální modely nestojí nic kromě hardwaru. Náklady nejvíc ovlivňuje velikost posílaného kontextu (kolik zdrojů je v chatu a zda jako „Celý obsah“, nebo „Jen poznatky“), vektorizace velkých knihoven a zvuk podcastů.

---

## Modely AI

### Se kterým poskytovatelem začít?

- **Nejjednodušší:** jeden poskytovatel, který pokryje jazykové modely, embeddingy i řeč, například OpenAI nebo Google AI.
- **Mnoho modelů pod jedním klíčem:** OpenRouter.
- **Soukromě a zdarma:** Ollama nebo vLLM, plus Speaches pro řeč.

Poskytovatelé jako Anthropic nabízejí jen jazykové modely, takže pro embeddingy přidáte druhého. Tabulka modalit je v [AI Providers](../../5-CONFIGURATION/ai-providers.md#providers-and-what-they-offer) (anglicky).

### Lze poskytovatele kombinovat?

Ano. Každá role modelu se přiřazuje zvlášť ve **Spravovat → Modely → Výchozí přiřazení modelů**: chat, transformace, nástroje, velký kontext, embedding, převod textu na řeč a převod řeči na text. Model můžete přepsat i pro jednu relaci chatu.

### Co se stane, když změním embedding model?

Stávající vektory vytvořil starý model a nebudou odpovídat novým hledáním. Open Notebook vás upozorní a nabídne přechod na stránku **Pokročilé**, kde je přestavíte. Než se začnete spoléhat na hledání nebo dotazy, přestavbu proveďte.

---

## Data

### Kde jsou moje data?

S dodaným `docker-compose.yml` ve dvou složkách vedle něj:

- `./surreal_data`: databáze SurrealDB (sešity, text zdrojů, poznámky, chaty, nastavení, šifrované přístupové údaje)
- `./notebook_data`: nahrané soubory, zvuk podcastů a mezipaměti

Varianta s jedním kontejnerem používá pro databázi `./surreal_single_data`.

### Jak zálohovat?

Zastavte aplikaci, zabalte obě složky do archivu a znovu ji spusťte. Uschovejte také `OPEN_NOTEBOOK_ENCRYPTION_KEY`: bez něj nepůjde v obnovené databázi dešifrovat klíče poskytovatelů. Postup krok za krokem: [Advanced → Backup & Restore](../../5-CONFIGURATION/advanced.md#backup--restore) (anglicky).

Před každou aktualizací zálohujte. Některé aktualizace bez zálohy vrátit nelze, například změnu šifrování přístupových údajů ve v1.15.0.

### Lze data synchronizovat mezi zařízeními?

Vestavěná synchronizace není. Provozujte jednu instanci, ke které se všechna zařízení připojují po síti, nebo data přenášejte zálohou a obnovou.

### Co se stane při smazání sešitu?

Smazání je trvalé („Tuto akci nelze vrátit.“). Poznámky sešitu se smažou vždy; můžete zvolit, zda smazat i zdroje, které patří jen tomuto sešitu. Zdroje sdílené s jinými sešity zůstanou. Chcete-li sešit odložit bez ztráty, použijte místo toho **Archivovat**.

---

## Provoz

### Mohu používat API přímo?

Ano. Interaktivní dokumentace je na `http://localhost:5055/docs`. Pokud je nastaveno heslo, posílejte ho jako `Authorization: Bearer <heslo>`. Viz [Security → API client examples](../../5-CONFIGURATION/security.md#api-client-examples) a [API Reference](../../7-DEVELOPMENT/api-reference.md) (anglicky).

### Je připraven pro nasazení dostupné z internetu?

Na serveru běžet může, ale jeho vestavěná ochrana je základní: jedno sdílené heslo, žádné uživatelské účty, žádné omezení počtu požadavků. Provozujte ho za HTTPS, nastavte heslo, omezte `CORS_ORIGINS` a databázi držte neveřejnou. Viz [Security](../../5-CONFIGURATION/security.md) a [Reverse Proxy](../../5-CONFIGURATION/reverse-proxy.md) (anglicky).

### Jak změním nastavení?

Nastavení infrastruktury jsou proměnné prostředí v bloku `environment:` služby `open_notebook`, které použijete příkazem `docker compose up -d`. Vše ostatní je v rozhraní. Viz [Configuration](../../5-CONFIGURATION/index.md) (anglicky).

### Jak aktualizovat?

Zálohujte, pak `docker compose pull && docker compose up -d` (u vlastního buildu z repozitáře `git pull`, `docker compose build` a `docker compose up -d`). Migrace databáze se spustí automaticky při startu API.

---

## Kde získat pomoc

- **Discord** (anglicky): https://discord.gg/37XJPXfz2w
- **GitHub Discussions:** otázky a nápady, https://github.com/lfnovo/open-notebook/discussions
- **GitHub Issues:** reprodukovatelné chyby, https://github.com/lfnovo/open-notebook/issues

Při hlášení chyby uveďte přesné znění chybové zprávy, postup reprodukce, příslušné záznamy (bez klíčů a hesel), verzi a způsob provozu Open Notebooku.

---

## Související

- [Rychlá řešení](quick-fixes.md)
- [Potíže s AI a chatem](ai-chat-issues.md)
- [Potíže se zpracováním](processing-issues.md)
- [Potíže s připojením](connection-issues.md)
