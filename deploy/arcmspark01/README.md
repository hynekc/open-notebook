# Open Notebook (česky) na DGX Spark `arcmspark01`

Autor nasazení: **Hynek Cihlář** (Bc. Hynek Cihlář)

Plně lokální Open Notebook s českým rozhraním a českou nápovědou na jednom DGX Sparku:

| Služba | Kontejner | Co dělá | Port |
|---|---|---|---|
| `vllm-qwen` | `on-vllm-qwen` | Jazykový model **Qwen/Qwen3.8-27B-FP8** + MTP (vLLM), název modelu `qwen3.8-27b` | jen `127.0.0.1:8010` |
| `vllm-embed` | `on-vllm-embed` | Embedding model **BAAI/bge-m3** (vícejazyčný, 1024 dimenzí), název `bge-m3` | jen `127.0.0.1:8011` |
| `vllm-whisper` | `on-vllm-whisper` | Přepis řeči **openai/whisper-large-v3** (zvukové a video zdroje), název `whisper-large-v3` | jen `127.0.0.1:8012` |
| `surrealdb` | `on-surrealdb` | Databáze Open Notebooku | nepublikuje se |
| `open_notebook` | `on-app` | Webové rozhraní, API a worker – image se staví z větve `cs-CZ` repozitáře `hynekc/open-notebook` | `8502` (UI), `5055` (API) |

Data jsou mimo repozitář v `/home/spark/open-notebook-data`, modely v `/home/spark/.cache/huggingface`.

Paměť (128 GB unified): Qwen `--gpu-memory-utilization 0.70`, bge-m3 `0.06`, Whisper `0.05`; zbytek pro systém a aplikaci. Na arcmspark01 proto nesmí současně běžet jiný velký model.

**Více uživatelů** (každý vlastní instanci, přihlášení doménovým účtem z UCS nebo místním účtem): [VICE-UZIVATELU.md](VICE-UZIVATELU.md).

Všechny příkazy níže se spouštějí na stroji **arcmspark01** pod uživatelem **spark**, v terminálu přes SSH z Macu (`Hyneks-Mac-mini`). Konfigurace v prohlížeči (krok 10) se dělá na Macu.

---

## Krok 0 – připojení na arcmspark01

**Stroj:** Hyneks-Mac-mini · **Složka:** `~` · **Terminál:** zsh

```bash
ssh spark@arcmspark01
```

Na arcmspark01 (nově otevřený terminál, složka `/home/spark`):

```bash
hostname && whoami && pwd
```

**Očekávaný výstup:**
```
arcmspark01
spark
/home/spark
```

---

## Krok 1 – kontrola předpokladů

**Stroj:** arcmspark01 · **Složka:** `/home/spark` · **Terminál:** SSH

```bash
cd /home/spark
sudo -v
sudo docker --version
sudo docker compose version
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
free -g | head -2
df -h /home/spark | tail -1
sudo docker ps --format '{{.Names}}  {{.Image}}'
sudo docker manifest inspect vllm/vllm-openai:qwen38 | grep -c '"arm64"'
```

**Očekávaný výstup:**
- `Docker version 2x.x.x` a `Docker Compose version v2.x.x`
- `NVIDIA GB10, 580.xx.xx`
- v řádku `Mem:` sloupec `available` alespoň **100** (GB) – jinak na Sparku běží jiný model; zastavte ho
- v `df` sloupec `Avail` alespoň **80G** (image ~20 GB, Qwen ~31 GB, bge-m3 ~2,3 GB, image Open Notebooku ~4 GB)
- `docker ps` neukazuje žádný běžící kontejner s vLLM (pokud ano, zastavte ho, jinak nebude dost paměti)
- poslední příkaz vypíše číslo **1 nebo vyšší** (image vLLM existuje pro ARM64). Pokud vypíše `0` nebo chybu, v kroku 4 do `.env` nastavte `VLLM_IMAGE=ghcr.io/spark-arena/dgx-vllm-eugr-nightly:latest`

---

## Krok 2 – stažení repozitáře

**Stroj:** arcmspark01 · **Složka:** `/home/spark` · **Terminál:** SSH

```bash
cd /home/spark
git clone -b cs-CZ https://github.com/hynekc/open-notebook.git /home/spark/open-notebook
git -C /home/spark/open-notebook log -1 --format='%h %an %s'
ls /home/spark/open-notebook/deploy/arcmspark01
```

**Očekávaný výstup:**
```
Cloning into '/home/spark/open-notebook'...
<hash> Hynek Cihlář <zpráva posledního commitu>
README.md  docker-compose.yml
```
(`.env.example` je skrytý soubor; ověříte ho příkazem `ls -a`.)

---

## Krok 3 – složky pro data a modely

**Stroj:** arcmspark01 · **Složka:** `/home/spark` · **Terminál:** SSH

```bash
mkdir -p /home/spark/open-notebook-data/surreal_data /home/spark/open-notebook-data/notebook_data /home/spark/.cache/huggingface
ls -ld /home/spark/open-notebook-data/surreal_data /home/spark/open-notebook-data/notebook_data /home/spark/.cache/huggingface
```

**Očekávaný výstup:** tři řádky `drwxr-xr-x ... spark spark ...` s uvedenými cestami.

---

## Krok 4 – soubor `.env` s hesly

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
cp .env.example .env
sed -i "s/^OPEN_NOTEBOOK_ENCRYPTION_KEY=$/OPEN_NOTEBOOK_ENCRYPTION_KEY=$(openssl rand -hex 32)/" .env
sed -i "s/^OPEN_NOTEBOOK_PASSWORD=$/OPEN_NOTEBOOK_PASSWORD=$(openssl rand -hex 16)/" .env
sed -i "s/^SURREAL_PASSWORD=$/SURREAL_PASSWORD=$(openssl rand -hex 16)/" .env
chmod 600 .env
awk -F= '/^(OPEN_NOTEBOOK_ENCRYPTION_KEY|OPEN_NOTEBOOK_PASSWORD|SURREAL_PASSWORD)=/{print $1, length($2)}' .env
sudo docker compose config --quiet && echo KONFIGURACE_OK
```

**Očekávaný výstup:**
```
OPEN_NOTEBOOK_ENCRYPTION_KEY 64
OPEN_NOTEBOOK_PASSWORD 32
SURREAL_PASSWORD 32
KONFIGURACE_OK
```

Heslo do aplikace si uložte do správce hesel. Vypíšete ho takto (spouštějte jen ve vlastním terminálu):

```bash
grep '^OPEN_NOTEBOOK_PASSWORD=' /home/spark/open-notebook/deploy/arcmspark01/.env
```

Šifrovací klíč (`OPEN_NOTEBOOK_ENCRYPTION_KEY`) uschovejte také: bez něj nepůjde po obnově ze zálohy dešifrovat nastavení modelů.

---

## Krok 5 – stažení image vLLM a SurrealDB (na pozadí)

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sudo -v
nohup sudo -n docker compose pull vllm-qwen vllm-embed surrealdb > /home/spark/open-notebook-data/pull.log 2>&1 &
echo "PID: $!"
```

**Průběh:**

```bash
tail -5 /home/spark/open-notebook-data/pull.log
```

**Jak poznat, že doběhlo:** příkaz

```bash
pgrep -f "docker compose pull" || echo DOBEHLO
```

vypíše `DOBEHLO`. **Úspěšně**, pokud

```bash
grep -cE "Pulled|Error" /home/spark/open-notebook-data/pull.log
sudo docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -E "vllm-openai:qwen38|surrealdb:v2"
```

ukazuje řádky `vllm/vllm-openai:qwen38` a `surrealdb/surrealdb:v2` a v logu není `Error`.

---

## Krok 6 – sestavení image Open Notebooku s češtinou (na pozadí, 10–25 min)

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sudo -v
nohup sudo -n docker compose build open_notebook > /home/spark/open-notebook-data/build.log 2>&1 &
echo "PID: $!"
```

**Průběh:**

```bash
tail -5 /home/spark/open-notebook-data/build.log
```

**Jak poznat, že doběhlo:**

```bash
pgrep -f "docker compose build" || echo DOBEHLO
```

**Úspěšně**, pokud:

```bash
tail -3 /home/spark/open-notebook-data/build.log
sudo docker image ls open-notebook-cs
```

ukazuje v logu `open_notebook  Built` (nebo `naming to docker.io/library/open-notebook-cs:local`) a v seznamu image řádek `open-notebook-cs   local`. Pokud log končí `ERROR` nebo `failed to solve`, pošlete mi posledních 40 řádků (`tail -40 /home/spark/open-notebook-data/build.log`).

---

## Krok 7 – spuštění modelů (první start stahuje ~33 GB)

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sudo docker compose up -d vllm-qwen vllm-embed
```

**Očekávaný výstup:**
```
 ✔ Network open-notebook_default  Created
 ✔ Container on-vllm-embed        Started
 ✔ Container on-vllm-qwen         Started
```

**Průběh** (stahování vah a načítání; Qwen typicky 15–40 min podle linky):

```bash
sudo docker logs --tail 5 on-vllm-qwen
sudo docker logs --tail 5 on-vllm-embed
```

**Jak poznat, že doběhlo a zda úspěšně:**

```bash
sudo docker inspect --format '{{.Name}} {{.State.Health.Status}}' on-vllm-qwen on-vllm-embed
```

- `starting` = ještě se stahuje / načítá, počkejte a opakujte
- **`healthy` u obou = hotovo a úspěšně**
- `unhealthy` nebo kontejner se restartuje = chyba; pošlete mi `sudo docker logs --tail 60 on-vllm-qwen`

---

## Krok 8 – test modelů

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
curl -s http://127.0.0.1:8010/v1/models | python3 -c 'import sys,json; print([m["id"] for m in json.load(sys.stdin)["data"]])'
curl -s http://127.0.0.1:8011/v1/models | python3 -c 'import sys,json; print([m["id"] for m in json.load(sys.stdin)["data"]])'
```

**Očekávaný výstup:**
```
['qwen3.8-27b']
['bge-m3']
```

Chat česky a kontrola, že je uvažování vypnuté:

```bash
curl -s http://127.0.0.1:8010/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"qwen3.8-27b","messages":[{"role":"user","content":"Odpověz jednou větou česky: k čemu slouží znalostní báze?"}],"max_tokens":120}' \
  | python3 -c 'import sys,json; r=json.load(sys.stdin); m=r["choices"][0]["message"]; print(m.get("content")); print("uvazovani:", bool(m.get("reasoning_content") or m.get("reasoning"))); print("tokenu:", r["usage"]["completion_tokens"])'
```

**Očekávaný výstup:** jedna česká věta, `uvazovani: False` a `tokenu:` řádově desítky.

Embedding:

```bash
curl -s http://127.0.0.1:8011/v1/embeddings -H 'Content-Type: application/json' \
  -d '{"model":"bge-m3","input":"Dobrý den, toto je test."}' \
  | python3 -c 'import sys,json; print(len(json.load(sys.stdin)["data"][0]["embedding"]))'
free -g | head -2
```

**Očekávaný výstup:** `1024`; v `free` je `available` ještě alespoň **15** (GB).

---

## Krok 9 – spuštění Open Notebooku

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sudo docker compose up -d
sleep 60
sudo docker compose ps --format '{{.Name}}  {{.Status}}'
curl -s http://127.0.0.1:5055/health; echo
curl -s -H "Authorization: Bearer $(grep '^OPEN_NOTEBOOK_PASSWORD=' .env | cut -d= -f2)" http://127.0.0.1:5055/api/config | python3 -c 'import sys,json; c=json.load(sys.stdin); print(c.get("version"), c.get("dbStatus"))'
sudo docker logs on-app 2>&1 | grep -E "entered RUNNING state" 
```

**Očekávaný výstup:**
```
on-app  Up About a minute
on-surrealdb  Up About a minute
on-vllm-embed  Up 20 minutes (healthy)
on-vllm-qwen  Up 20 minutes (healthy)
{"status":"healthy"}
1.15.1 online
INFO success: api entered RUNNING state ...
INFO success: worker entered RUNNING state ...
INFO success: frontend entered RUNNING state ...
```

---

## Krok 10 – nastavení modelů v aplikaci

**Stroj:** Hyneks-Mac-mini · **Program:** prohlížeč

1. Otevřete **http://arcmspark01:8502** a přihlaste se heslem z kroku 4.
2. Pokud je rozhraní anglicky: v levém panelu dole **Language** → **Čeština**.
3. **Spravovat → Modely** → v sekci **OpenAI Compatible** klikněte na **Přidat konfiguraci**:
   - Název konfigurace: `vLLM Qwen3.8 (arcmspark01)`
   - API klíč: prázdné
   - Základní URL: `http://vllm-qwen:8000/v1`
   - **Přidat konfiguraci**
4. U nové konfigurace klikněte na **Test** → **zelená fajfka**.
5. Klikněte na **Modely** → Typ modelu **Language** → zaškrtněte `qwen3.8-27b` → **Přidat (1)**.
6. Znovu **Přidat konfiguraci** v sekci **OpenAI Compatible**:
   - Název konfigurace: `vLLM bge-m3 (arcmspark01)`
   - Základní URL: `http://vllm-embed:8000/v1`
   - **Přidat konfiguraci** → **Test** → zelená fajfka
7. U ní **Modely** → Typ modelu **Embedding** → zaškrtněte `bge-m3` → **Přidat (1)**.
8. Sjeďte na **Výchozí přiřazení modelů** → **Automaticky přiřadit výchozí**.
   **Kontrola:** Model chatu = `qwen3.8-27b`, Embedding model = `bge-m3`. Model transformací, nástrojů a pro velký kontext nastavte také na `qwen3.8-27b` (jinak se použije model chatu – výsledek je stejný).
9. **Spravovat → Transformace** → **Výchozí prompt transformací**: `Odpovídej vždy česky.` → uložit. Poznatky z anglických zdrojů pak budou česky.
10. **Test celého řetězce:** **Sešity → Nový sešit** (název `Test`) → **Přidat zdroj → Přidat zdroj → Zadat text** → vložte odstavec, název `Test` → **Hotovo**. Až karta ukáže, že je zdroj hotový, napište do chatu `Shrň zdroj ve dvou větách.` a odešlete **⌘+Enter**.
    **Kontrola:** česká odpověď s odkazem **[1]** na zdroj; v **Dotazy a hledání → Hledání → Vektorové hledání** najde slovo ze zdroje.

---

## Aktualizace na novou verzi

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

Nejdřív záloha (viz níže), pak:

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
git -C /home/spark/open-notebook pull
git -C /home/spark/open-notebook log -1 --format='%h %s'
sudo -v
nohup sudo -n docker compose build open_notebook > /home/spark/open-notebook-data/build.log 2>&1 &
```

Doběhnutí a úspěch ověřte stejně jako v kroku 6, pak:

```bash
sudo docker compose up -d open_notebook
sleep 60
curl -s http://127.0.0.1:5055/health; echo
```

**Očekávaný výstup:** `Container on-app Started` a `{"status":"healthy"}`. Migrace databáze proběhnou při startu samy.

## Záloha

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sudo docker compose stop open_notebook surrealdb
sudo tar czf /home/spark/open-notebook-backup-$(date +%Y%m%d-%H%M).tar.gz -C /home/spark open-notebook-data/surreal_data open-notebook-data/notebook_data open-notebook/deploy/arcmspark01/.env
sudo docker compose start surrealdb open_notebook
ls -lh /home/spark/open-notebook-backup-*.tar.gz | tail -1
```

**Očekávaný výstup:** `Container on-surrealdb Stopped`, `Container on-app Stopped`, pak `Started` a řádek s archivem `open-notebook-backup-RRRRMMDD-HHMM.tar.gz`. Archiv obsahuje i `.env` s klíči – ukládejte ho jen na bezpečné místo.

## Řešení potíží

| Příznak | Kontrola na arcmspark01 (složka `/home/spark/open-notebook/deploy/arcmspark01`) |
|---|---|
| `on-vllm-qwen` padá s „out of memory“ / „insufficient memory“ | `free -g`; zastavte jiné modely (`sudo docker ps`), případně v `.env` snižte `QWEN_GPU_MEM=0.65` nebo `QWEN_MAX_MODEL_LEN=131072` a `sudo docker compose up -d vllm-qwen` |
| vLLM nezná `--default-chat-template-kwargs` nebo `--runner` | Starší image vLLM; v `.env` nastavte novější `VLLM_IMAGE` a `sudo docker compose up -d vllm-qwen vllm-embed` |
| Odpovědi v aplikaci vyprší po 420 s | Dlouhý kontext; zmenšete výběr zdrojů nebo zvyšte `ESPERANTO_LLM_TIMEOUT` (max. 590) v `.env` a `sudo docker compose up -d open_notebook` |
| Zdroje zůstávají „Ve frontě“ | `sudo docker logs on-app 2>&1 \| grep -E "worker entered\|exited: worker"` |
| Test konfigurace v aplikaci selže | `sudo docker exec on-app curl -s http://vllm-qwen:8000/v1/models` musí vrátit JSON s `qwen3.8-27b` |

## České transformace

Vestavěné transformace (Analyze Paper, Key Insights, Dense Summary, Reflections, Table of Contents, Simple Summary) a výchozí prompt transformací vkládá databáze při prvním startu anglicky. Skript `prelozit-transformace.py` je přes REST API přepíše na české verze (název, popis, prompt; vlastní transformace nemění) a před změnou uloží zálohu do `/home/spark/open-notebook-data/transformace-zaloha-*.json`. Spouští se na arcmspark01 ve složce `/home/spark/open-notebook/deploy/arcmspark01`:

```bash
python3 prelozit-transformace.py --nanecisto
python3 prelozit-transformace.py
```

## Přepis řeči (Whisper)

Převod textu na řeč (podcasty) se zatím nenasazuje. Převod řeči na text zajišťuje služba `vllm-whisper`. Běží offline (`HF_HUB_OFFLINE=1`), protože repozitář modelu obsahuje i varianty vah, které by vLLM stáhl navíc (přes 10 GB). Potřebné soubory (~3 GB) se stáhnou předem na arcmspark01, složka `/home/spark/open-notebook/deploy/arcmspark01`:

```bash
sudo docker run --rm -v /home/spark/.cache/huggingface:/root/.cache/huggingface --entrypoint python3 vllm/vllm-openai:qwen38 -c "from huggingface_hub import snapshot_download; print(snapshot_download('openai/whisper-large-v3', allow_patterns=['*.json', '*.txt', 'model.safetensors']))"
```

Image `vllm/vllm-openai:qwen38` nemá knihovny pro čtení zvuku, proto se pro Whisper staví vlastní image `vllm-openai-audio:local` ze souboru `whisper.Dockerfile` (doplní `librosa`, `soundfile`, `av`): `sudo docker compose build vllm-whisper`.

V aplikaci službu přidáte jako konfiguraci **OpenAI Compatible** se základní URL `http://vllm-whisper:8000/v1`, modelem `whisper-large-v3` typu **STT** a vyberete ji jako **Model převodu řeči na text**.

## Vyhledávání zdrojů na webu (SearXNG)

Služba `searxng` (kontejner `on-searxng`) je vlastní vyhledávač: dotazy předává veřejným vyhledávačům bez API klíčů a výsledky vrací Open Notebooku ve formátu JSON. V aplikaci pak přibude v dialogu **Přidat zdroj** karta **Vyhledat na webu** a v nabídce sešitu **Přidat zdroj → Vyhledat na webu**. Nastavení je v `searxng/settings.yml`, tajný klíč v `.env` (`SEARXNG_SECRET`). Vypnutí: `WEB_SEARCH_URL=` (prázdné) v `.env` a `sudo docker compose up -d`.

Platí pro režim jednoho uživatele (kontejner `on-app`). V režimu více uživatelů je postup v [VICE-UZIVATELU.md](VICE-UZIVATELU.md), kde se image sestavuje s `--profile jedna-instance`.

### 1. Nová verze repozitáře a tajný klíč SearXNG

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
git -C /home/spark/open-notebook pull
git -C /home/spark/open-notebook log -1 --format='%h %an %s'
grep -q '^SEARXNG_SECRET=' .env || sed -n '/VYHLEDÁVÁNÍ ZDROJŮ NA WEBU/,/^WEB_SEARCH_URL=/p' .env.example >> .env
sed -i "s/^SEARXNG_SECRET=$/SEARXNG_SECRET=$(openssl rand -hex 32)/" .env
awk -F= '/^SEARXNG_SECRET=/{print $1, length($2)} /^(WEB_SEARCH_URL|SEARXNG_HOST_PORT)=/{print}' .env
sudo docker compose config --quiet && echo KONFIGURACE_OK
```

**Očekávaný výstup:**
```
<hash> Hynek Cihlář feat(sources): …
SEARXNG_SECRET 64
SEARXNG_HOST_PORT=8013
WEB_SEARCH_URL=http://searxng:8080
KONFIGURACE_OK
```

### 2. Sestavení image Open Notebooku (na pozadí, 10–25 min)

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sudo -v
nohup sudo -n docker compose build open_notebook > /home/spark/open-notebook-data/build.log 2>&1 &
echo "PID: $!"
```

Průběh: `tail -5 /home/spark/open-notebook-data/build.log`. Doběhlo, když `pgrep -f "docker compose build" || echo DOBEHLO` vypíše `DOBEHLO`. **Úspěšně**, pokud `tail -3 /home/spark/open-notebook-data/build.log` ukazuje `open_notebook  Built` (nebo `naming to docker.io/library/open-notebook-cs:local`). Pokud log končí `ERROR` nebo `failed to solve`, pošlete mi `tail -40 /home/spark/open-notebook-data/build.log`.

### 3. Spuštění SearXNG a nové verze aplikace

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sudo docker compose up -d searxng open_notebook
sleep 60
sudo docker compose ps searxng open_notebook --format 'table {{.Name}}\t{{.Status}}'
curl -s 'http://127.0.0.1:8013/search?q=rybn%C3%ADk&format=json&language=cs' | python3 -c "import sys,json; d=json.load(sys.stdin); print('SEARXNG výsledků:', len(d['results'])); print(d['results'][0]['url'])"
H="Authorization: Bearer $(grep '^OPEN_NOTEBOOK_PASSWORD=' .env | cut -d= -f2)"
curl -s -H "$H" http://127.0.0.1:5055/api/capabilities; echo
curl -s -H "$H" 'http://127.0.0.1:5055/api/web-search?q=rybn%C3%ADk&language=cs&limit=5' | python3 -c "import sys,json; d=json.load(sys.stdin); print('API výsledků:', len(d['results'])); [print(' -', r['title'][:70]) for r in d['results']]"
```

**Očekávaný výstup:**
```
NAME          STATUS
on-app        Up About a minute
on-searxng    Up About a minute
SEARXNG výsledků: <číslo větší než 0>
https://cs.wikipedia.org/wiki/Rybn%C3%ADk   (nebo jiná česká stránka)
{"docling_available":false,"crawl4ai_available":false,"crawl4ai_remote_configured":false,"web_search_available":true}
API výsledků: 5
 - Rybník – Wikipedie
 - …
```

- `SEARXNG výsledků: 0` nebo chyba `json`: podívejte se do `sudo docker logs on-searxng 2>&1 | tail -20`. Hlášky `timeout` nebo `access denied` u jednotlivých vyhledávačů jsou běžné, SearXNG je přeskočí. Pokud selžou všechny, arcmspark01 nemá přístup na internet.
- `"web_search_available":false`: v `.env` je prázdné `WEB_SEARCH_URL`, nebo běží stará image (zopakujte krok 2).

### 4. Zkouška v prohlížeči

**Stroj:** Hyneks-Mac-mini · **Prohlížeč**

V sešitu klikněte na **Přidat zdroj → Vyhledat na webu**, zadejte výraz, zaškrtněte dva výsledky a klikněte na **Přidat vybrané (2)**. Otevře se karta **Přidat URL** s oběma adresami. Pak **Další** / **Hotovo** jako u běžných odkazů. Pokud se volba v nabídce nezobrazí, obnovte stránku (`Cmd+Shift+R`).

Podrobná česká nápověda: [docs/cs](../../docs/cs/index.md).
