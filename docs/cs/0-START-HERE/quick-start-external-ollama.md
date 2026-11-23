# Rychlý start – externí Ollama

Spusťte Open Notebook v Dockeru a připojte ho k **Ollamě nainstalované přímo ve vašem počítači** (ne v Dockeru). Hodí se, když už Ollamu používáte nebo chcete její nativní podporu GPU bez předávání GPU do Dockeru.

Pokud Ollamu ještě nemáte a chcete mít vše v Dockeru, použijte [Rychlý start – lokálně](quick-start-local.md).

## Předpoklady

1. **Docker s Compose v2**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) na macOS a Windows; Docker Engine s pluginem Compose na Linuxu.
2. **Ollama** nainstalovaná z [ollama.com](https://ollama.com/download). Ověřte příkazem `ollama --version`.

## Krok 1: Stažení modelů (2–5 min)

Open Notebook potřebuje model pro chat a embedding model:

```bash
ollama pull qwen3
ollama pull nomic-embed-text
```

Na slabším počítači použijte místo `qwen3` model `llama3.2` nebo `gemma3:1b`.

## Krok 2: Zpřístupnění Ollamy kontejnerům

Open Notebook běží v kontejneru, kde `localhost` znamená kontejner sám. K Ollamě ve vašem počítači se dostane přes název `host.docker.internal`.

**macOS a Windows (Docker Desktop):** Docker Desktop přesměrovává `host.docker.internal` na váš počítač, takže výchozí nastavení Ollamy obvykle funguje; zkuste ho nejdřív. Pokud test připojení v kroku 5 selže, nastavte Ollamu tak, aby naslouchala na všech rozhraních: na macOS spusťte `launchctl setenv OLLAMA_HOST "0.0.0.0:11434"` a aplikaci Ollama ukončete a znovu otevřete (nastavení se po odhlášení nebo restartu ztratí, takže ho po každém přihlášení zopakujte, nebo podle FAQ Ollamy nastavte trvale); ve Windows přidejte uživatelskou proměnnou prostředí `OLLAMA_HOST` = `0.0.0.0:11434` a Ollamu ukončete a znovu spusťte. Viz [dokumentace Ollamy](https://github.com/ollama/ollama/tree/main/docs) (FAQ, „How do I configure Ollama server?“).

**Linux:** Ollama ve výchozím stavu naslouchá jen na `127.0.0.1`, kam se kontejnery nedostanou. Nastavte naslouchání na všech rozhraních. Pokud Ollama běží jako služba systemd (výchozí u linuxového instalátoru):

```bash
sudo systemctl edit ollama
```

Přidejte tyto řádky, uložte a restartujte:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

```bash
sudo systemctl restart ollama
```

Pokud Ollamu spouštíte ručně, spusťte ji příkazem `OLLAMA_HOST=0.0.0.0:11434 ollama serve`.

**Na všech platformách** `OLLAMA_HOST=0.0.0.0` zpřístupní API Ollamy, které nemá žádné ověřování, na všech síťových rozhraních. Port 11434 povolte jen z tohoto počítače a jeho sítí Dockeru (například firewallem), nikdy z nedůvěryhodných sítí.

## Krok 3: Stažení a nastavení Open Notebooku (1 min)

```bash
mkdir open-notebook
cd open-notebook
curl -o docker-compose.yml https://raw.githubusercontent.com/lfnovo/open-notebook/main/docker-compose.yml
```

(Ve Windows PowerShellu použijte `curl.exe`.)

Vedle `docker-compose.yml` vytvořte soubor `.env` a nastavte v něm `OPEN_NOTEBOOK_ENCRYPTION_KEY` na dlouhý náhodný tajný řetězec, který si sami vygenerujete, například příkazem `openssl rand -hex 32` (Windows: viz [Set your encryption key](../../1-INSTALLATION/docker-compose.md#step-2-set-your-encryption-key)). Dodaný compose soubor ho čte z `.env`. Upravit přímo tento řádek v `docker-compose.yml` je také možné. Nepoužívejte ukázkovou hodnotu. Když není nastaveno ani jedno, použije se `change-me-to-a-secret-string`.

> **Sdílená síť nebo server?** Dodaný soubor zveřejňuje rozhraní (`8502`) a API (`5055`) na všech síťových rozhraních a ve výchozím stavu není nastaveno heslo. Pokud se k tomuto počítači dostanou jiná zařízení, před spuštěním udělejte jedno z toho: změňte dva řádky s porty služby `open_notebook` na `"127.0.0.1:8502:8502"` a `"127.0.0.1:5055:5055"`, nebo nastavte `OPEN_NOTEBOOK_PASSWORD` ve stejném souboru `.env`.

Potom ve stejné složce vytvořte `docker-compose.override.yml`. Na Linuxu díky němu funguje překlad `host.docker.internal`; v Docker Desktopu nevadí:

```yaml
services:
  open_notebook:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

## Krok 4: Spuštění (1 min)

```bash
docker compose up -d
```

## Krok 5: Připojení Ollamy a chat (3 min)

Otevřete **http://localhost:8502** a projděte **[Připojení poskytovatele](../4-AI-PROVIDERS/index.md#connect-a-provider)** s těmito hodnotami:

| Pole | Hodnota |
|---|---|
| Poskytovatel | **Ollama** |
| API klíč | Nechte prázdné |
| Základní URL | `http://host.docker.internal:11434` |
| Modely k přidání | Model pro chat jako **Language** (uveden jako `qwen3:latest`), potom `nomic-embed-text:latest` jako **Embedding** |
| Výchozí modely | Klikněte na **Automaticky přiřadit výchozí** |

Poslední krok té stránky vytvoří sešit, přidá textový zdroj a odešle zprávu do chatu.

## Kontrolní seznam

- [ ] `ollama list` ukazuje model pro chat a `nomic-embed-text`
- [ ] `docker compose ps` ukazuje běžící `surrealdb` a `open_notebook`
- [ ] **Test** u konfigurace Ollamy ukazuje zelenou fajfku
- [ ] **Výchozí přiřazení modelů** obsahuje model chatu a embedding model
- [ ] Na zprávu v chatu přijde odpověď

## Řešení potíží

**Test ukazuje červený křížek.** Ověřte to zevnitř kontejneru:

```bash
docker compose exec open_notebook curl -s http://host.docker.internal:11434/api/version
```

- *Could not resolve host*: chybí override s `extra_hosts`, nebo jste po jeho přidání nespustili `docker compose up -d`.
- *Connection refused*: Ollama stále naslouchá jen na `127.0.0.1`. Zopakujte krok 2 (na macOS a ve Windows použijte nastavení `OLLAMA_HOST`). Na Linuxu ověřte příkazem `ss -ltn | grep 11434`; má ukázat `*:11434` nebo `0.0.0.0:11434`.
- Žádná odpověď: port 11434 mezi Dockerem a hostitelem blokuje firewall.

**Odpovědi jsou pomalé nebo vyprší čas.** Viz část o časových limitech v [návodu k Ollamě](../../5-CONFIGURATION/ollama.md) (anglicky).

**Přidání dalších modelů později.** Spusťte `ollama pull <model>`, pak znovu klikněte na **Modely** u konfigurace Ollamy (otevře se dialog **Vyhledat modely**) a model přidejte.

## Ollama v Dockeru, nebo na hostiteli?

| | Ollama v Dockeru ([Rychlý start – lokálně](quick-start-local.md)) | Ollama na hostiteli (tento návod) |
|---|---|---|
| GPU | Vyžaduje nastavení GPU v Dockeru | Používá GPU nativně (včetně Apple Silicon) |
| Správa modelů | `docker compose exec ollama ollama ...` | `ollama ...` |
| Síť | Funguje bez nastavování | Vyžaduje `extra_hosts`; Linux (a někdy Docker Desktop) vyžaduje `OLLAMA_HOST` |

## Další kroky

- [Návod k Ollamě](../../5-CONFIGURATION/ollama.md) (anglicky): výběr modelů, síť, časové limity
- [Docker Compose guide](../../1-INSTALLATION/docker-compose.md) (anglicky): nastavení, zálohy, aktualizace
- [Uživatelská příručka](../3-USER-GUIDE/index.md)

**Potřebujete pomoc?** Přidejte se ke [komunitě na Discordu](https://discord.gg/37XJPXfz2w) (anglicky).
