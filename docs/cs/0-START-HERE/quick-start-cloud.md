# Rychlý start – cloudoví poskytovatelé AI (5 minut)

Spusťte Open Notebook s cloudovým poskytovatelem AI, například **OpenAI, Anthropic, Google, Mistral, Groq nebo OpenRouter**. Potřebujete Docker a API klíč.

## Předpoklady

1. **Docker s Compose v2**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) na macOS a Windows; Docker Engine s pluginem Compose na Linuxu.
2. **API klíč** od poskytovatele, například:
   - [OpenAI](https://platform.openai.com/api-keys)
   - [Anthropic](https://console.anthropic.com/settings/keys)
   - [Google AI Studio](https://aistudio.google.com/app/apikey)
   - [Mistral](https://console.mistral.ai/api-keys/)
   - [Groq](https://console.groq.com/keys)
   - [OpenRouter](https://openrouter.ai/keys)

   Další poskytovatele najdete v části [Poskytovatelé AI](../4-AI-PROVIDERS/index.md#supported-providers).

> **Vyberte poskytovatele, který umí embeddingy, nebo přidejte druhého.** Open Notebook potřebuje jazykový model pro chat **a** embedding model pro hledání. OpenAI, Google AI, Mistral AI a OpenRouter nabízejí obojí. Anthropic, DeepSeek a Groq embedding modely nemají, proto je zkombinujte s poskytovatelem, který je má (například OpenAI, Google AI, Mistral AI nebo Voyage AI).

## Krok 1: Stažení a nastavení (1 min)

```bash
mkdir open-notebook
cd open-notebook
curl -o docker-compose.yml https://raw.githubusercontent.com/lfnovo/open-notebook/main/docker-compose.yml
```

(Ve Windows PowerShellu použijte `curl.exe`.)

Vedle `docker-compose.yml` vytvořte soubor `.env` a nastavte v něm `OPEN_NOTEBOOK_ENCRYPTION_KEY` na dlouhý náhodný tajný řetězec, který si sami vygenerujete, například příkazem `openssl rand -hex 32` (Windows: viz [Set your encryption key](../../1-INSTALLATION/docker-compose.md#step-2-set-your-encryption-key)). Dodaný compose soubor ho čte z `.env`. Upravit přímo tento řádek v `docker-compose.yml` je také možné. Nepoužívejte ukázkovou hodnotu. Klíč si uschovejte: když se změní, uložené API klíče už nepůjde dešifrovat. Když není nastaveno ani jedno, použije se `change-me-to-a-secret-string`.

> **Sdílená síť nebo server?** Dodaný soubor zveřejňuje rozhraní (`8502`) a API (`5055`) na všech síťových rozhraních a ve výchozím stavu není nastaveno heslo. Pokud se k tomuto počítači dostanou jiná zařízení, před spuštěním udělejte jedno z toho: změňte dva řádky s porty služby `open_notebook` na `"127.0.0.1:8502:8502"` a `"127.0.0.1:5055:5055"`, nebo nastavte `OPEN_NOTEBOOK_PASSWORD` ve stejném souboru `.env`.

## Krok 2: Spuštění (1 min)

```bash
docker compose up -d
```

Počkejte asi 30 sekund a otevřete **http://localhost:8502**.

## Krok 3: Připojení poskytovatele a chat (3 min)

Projděte **[Připojení poskytovatele](../4-AI-PROVIDERS/index.md#connect-a-provider)** s těmito hodnotami:

| Pole | Hodnota |
|---|---|
| Poskytovatel | Ten, ke kterému máte klíč (například **OpenAI**) |
| API klíč | Váš klíč |
| Základní URL | Nechte prázdné |
| Modely k přidání | Alespoň jeden model typu **Language** a jeden typu **Embedding** (od tohoto nebo druhého poskytovatele) |
| Výchozí modely | Klikněte na **Automaticky přiřadit výchozí** |

Poslední krok té stránky vytvoří sešit, přidá textový zdroj a odešle zprávu do chatu. Jakmile dostanete odpověď, je nastaveno.

## Kontrolní seznam

- [ ] `docker compose ps` ukazuje běžící `surrealdb` a `open_notebook`
- [ ] http://localhost:8502 se otevře
- [ ] **Test** u konfigurace poskytovatele ukazuje zelenou fajfku
- [ ] **Výchozí přiřazení modelů** obsahuje model chatu a embedding model
- [ ] Na zprávu v chatu přijde odpověď

## Volitelné: podcasty a zvuk

- **Podcasty** potřebují **model převodu textu na řeč**. Přidejte model TTS (nabízejí je OpenAI, Google AI, Mistral AI, xAI, MiniMax, ElevenLabs a další) a vyberte ho ve **Výchozím přiřazení modelů**. Automatické přiřazení ho nenastaví.
- **Zvukové a video zdroje** potřebují **model převodu řeči na text** (OpenAI, Google AI, Groq, Mistral AI, ElevenLabs, Deepgram a další).

## Řešení potíží

**Test ukazuje červený křížek.** Ověřte klíč na webu poskytovatele a zda má účet kredit. Klíč opravíte úpravou konfigurace.

**Požadovaný model v seznamu není.** Napište jeho přesný název do vyhledávacího pole dialogu **Vyhledat modely** a přidejte ho jako vlastní model.

**Chat selže s hláškou „No model configured…“.** Některý výchozí model je prázdný; viz [Nastavení výchozích modelů](../4-AI-PROVIDERS/index.md#4-set-default-models).

**Port 8502 je obsazený.** V `docker-compose.yml` změňte `"8502:8502"` na `"8503:8502"`, spusťte `docker compose up -d` a otevřete http://localhost:8503.

**Cokoli dalšího.** `docker compose logs -f open_notebook` ukazuje záznamy rozhraní, API i workeru. Viz [Rychlá řešení](../6-TROUBLESHOOTING/quick-fixes.md).

## Další kroky

- [Docker Compose guide](../../1-INSTALLATION/docker-compose.md) (anglicky): změna nastavení, zálohy, aktualizace, přístup z jiných počítačů
- [Uživatelská příručka](../3-USER-GUIDE/index.md): zdroje, chat, poznámky, podcasty
- Než Open Notebook zpřístupníte v síti, nastavte heslo: [Security](../../5-CONFIGURATION/security.md) (anglicky)

**Potřebujete pomoc?** Přidejte se ke [komunitě na Discordu](https://discord.gg/37XJPXfz2w) (anglicky).
