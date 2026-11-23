# Rychlý start – lokálně a soukromě (10 minut)

Spusťte Open Notebook a **Ollamu** společně v Dockeru. Žádné cloudové API klíče: obsah zpracují modely na vašem počítači a nic se neposílá poskytovateli AI. Aby zůstala soukromá i samotná aplikace, zajistěte, že se k ní nedostanou jiná zařízení (viz poznámka v kroku 1).

**Máte Ollamu už nainstalovanou v tomto počítači?** Použijte místo toho [návod s externí Ollamou](quick-start-external-ollama.md).

## Předpoklady

- **Docker s Compose v2**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) na macOS a Windows; Docker Engine s pluginem Compose na Linuxu.
- **8 GB RAM nebo více.** Lokální modely běží na CPU, pokud nenastavíte přístup ke GPU, a malé modely jsou znatelně pomalejší než cloudové.
- Několik GB místa na disku pro modely.

## Krok 1: Stažení a nastavení (1 min)

```bash
mkdir open-notebook
cd open-notebook
curl -o docker-compose.yml https://raw.githubusercontent.com/lfnovo/open-notebook/main/docker-compose.yml
```

(Ve Windows PowerShellu použijte `curl.exe`.)

Vedle `docker-compose.yml` vytvořte soubor `.env` a nastavte v něm `OPEN_NOTEBOOK_ENCRYPTION_KEY` na dlouhý náhodný tajný řetězec, který si sami vygenerujete, například příkazem `openssl rand -hex 32` (Windows: viz [Set your encryption key](../../1-INSTALLATION/docker-compose.md#step-2-set-your-encryption-key)). Dodaný compose soubor ho čte z `.env`. Upravit přímo tento řádek v `docker-compose.yml` je také možné. Nepoužívejte ukázkovou hodnotu. Když není nastaveno ani jedno, použije se `change-me-to-a-secret-string`.

> **Sdílená síť nebo server?** Dodaný soubor zveřejňuje rozhraní (`8502`) a API (`5055`) na všech síťových rozhraních a ve výchozím stavu není nastaveno heslo. Pokud se k tomuto počítači dostanou jiná zařízení, před spuštěním udělejte jedno z toho: změňte dva řádky s porty služby `open_notebook` na `"127.0.0.1:8502:8502"` a `"127.0.0.1:5055:5055"`, nebo nastavte `OPEN_NOTEBOOK_PASSWORD` ve stejném souboru `.env`.

## Krok 2: Přidání služby Ollama (1 min)

Ve stejné složce vytvořte soubor `docker-compose.override.yml`. Docker Compose ho automaticky sloučí s `docker-compose.yml`:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ./ollama_models:/root/.ollama
    restart: always
```

Přístup ke GPU NVIDIA popisuje [GPU acceleration](../../5-CONFIGURATION/ollama.md#gpu-acceleration) v návodu k Ollamě (anglicky).

## Krok 3: Spuštění (1 min)

```bash
docker compose up -d
```

## Krok 4: Stažení modelů (2–5 min)

Open Notebook potřebuje **model pro chat** a **embedding model**. Nic je nestáhne automaticky:

```bash
docker compose exec ollama ollama pull qwen3
docker compose exec ollama ollama pull nomic-embed-text
```

`qwen3` je schopný obecný model o velikosti asi 5 GB. Na slabším počítači zkuste `llama3.2` (asi 2 GB) nebo `gemma3:1b`. Další najdete na [ollama.com/library](https://ollama.com/library).

Co je nainstalované, zjistíte příkazem `docker compose exec ollama ollama list`.

## Krok 5: Připojení Ollamy a chat (3 min)

Otevřete **http://localhost:8502** a projděte **[Připojení poskytovatele](../4-AI-PROVIDERS/index.md#connect-a-provider)** s těmito hodnotami:

| Pole | Hodnota |
|---|---|
| Poskytovatel | **Ollama** |
| API klíč | Nechte prázdné |
| Základní URL | `http://ollama:11434` |
| Modely k přidání | Model pro chat jako **Language** (Ollama ho uvádí jako `qwen3:latest`), potom `nomic-embed-text:latest` jako **Embedding** |
| Výchozí modely | Klikněte na **Automaticky přiřadit výchozí** |

Poslední krok té stránky vytvoří sešit, přidá textový zdroj a odešle zprávu do chatu. První odpověď může chvíli trvat, než Ollama načte model.

## Kontrolní seznam

- [ ] `docker compose ps` ukazuje běžící `surrealdb`, `open_notebook` a `ollama`
- [ ] `docker compose exec ollama ollama list` ukazuje model pro chat a `nomic-embed-text`
- [ ] **Test** u konfigurace Ollamy ukazuje zelenou fajfku
- [ ] **Výchozí přiřazení modelů** obsahuje model chatu a embedding model
- [ ] Na zprávu v chatu přijde odpověď

## Řešení potíží

**Test ukazuje červený křížek.** Základní URL musí být `http://ollama:11434` (název služby), ne `localhost`: uvnitř kontejneru Open Notebooku je `localhost` kontejner sám. Zkontrolujte také, že jste stáhli alespoň jeden model; test ho používá.

**Odpovědi jsou velmi pomalé nebo vyprší čas.** Malé modely na CPU jsou pomalé. Zkuste menší model, zapněte přístup ke GPU, nebo nastavte `OPEN_NOTEBOOK_WORKER_MAX_TASKS=1`, aby úlohy na pozadí nesoupeřily s chatem. Časové limity popisuje [návod k Ollamě](../../5-CONFIGURATION/ollama.md) (anglicky).

**Přidání dalších modelů později.** Spusťte `docker compose exec ollama ollama pull <model>`, pak znovu klikněte na **Modely** u konfigurace Ollamy (otevře se dialog **Vyhledat modely**) a model přidejte.

**Cokoli dalšího.** `docker compose logs -f open_notebook` a `docker compose logs -f ollama`. Viz [Rychlá řešení](../6-TROUBLESHOOTING/quick-fixes.md).

## Podcasty a zvuk lokálně

Ollama poskytuje jen modely pro chat a embedding. Pro podcasty (převod textu na řeč) a přepis zvuku a videa (převod řeči na text) bez cloudu spusťte lokální řečový server a přidejte ho jako **OpenAI Compatible**: viz [Local TTS](../../5-CONFIGURATION/local-tts.md) a [Local STT](../../5-CONFIGURATION/local-stt.md) (anglicky). Můžete je i kombinovat: lokální chat s cloudovým poskytovatelem TTS.

## LM Studio místo Ollamy

LM Studio běží ve vašem počítači mimo Docker:

1. V LM Studiu stáhněte model pro chat a embedding model a spusťte lokální server (výchozí port 1234).
2. Kroky 2 a 4 výše vynechte. Na Linuxu přidejte do `docker-compose.override.yml` toto, aby se kontejner dostal k vašemu počítači:

   ```yaml
   services:
     open_notebook:
       extra_hosts:
         - "host.docker.internal:host-gateway"
   ```

3. [Připojte poskytovatele](../4-AI-PROVIDERS/index.md#connect-a-provider) typu **OpenAI Compatible** se základní URL `http://host.docker.internal:1234/v1`.

Více v [OpenAI-Compatible Providers](../../5-CONFIGURATION/openai-compatible.md) (anglicky).

## Další kroky

- [Návod k Ollamě](../../5-CONFIGURATION/ollama.md) (anglicky): výběr modelů, GPU, síť, časové limity
- [Docker Compose guide](../../1-INSTALLATION/docker-compose.md) (anglicky): nastavení, zálohy, aktualizace
- [Uživatelská příručka](../3-USER-GUIDE/index.md)

**Potřebujete pomoc?** Přidejte se ke [komunitě na Discordu](https://discord.gg/37XJPXfz2w) (anglicky).
