# Potíže s připojením – rozhraní, API a databáze

Když se části Open Notebooku nemohou navzájem spojit. Cesta má tři úseky:

```
Prohlížeč ──> Webové rozhraní (8502) ──> API (5055) ──> SurrealDB (8000)
```

S dodaným `docker-compose.yml` jsou služby dvě: `surrealdb` a `open_notebook`, ve které běží rozhraní, API i worker na pozadí dohromady. Příkazy na této stránce používají tyto názvy.

---

## Stránka se vůbec nenačte

Prohlížeč pro `http://localhost:8502` ukazuje vlastní chybu („Tento web není dostupný“, „connection refused“).

```bash
docker compose ps                      # je open_notebook „Up“?
docker compose logs --tail 50 open_notebook
```

- **Neběží nebo se restartuje:** přečtěte záznam. API před spuštěním rozhraní čeká na databázi, takže problém s databází může blokovat i rozhraní (viz [Připojení k databázi selhalo](#database-connection-failed)).
- **Běží, ale port není publikovaný:** `docker compose ps` musí ukazovat `0.0.0.0:8502->8502/tcp`. Pokud jste mapování změnili, použijte zvolený port hostitele.
- **„Bind for 0.0.0.0:8502 failed: port is already allocated“** při spuštění: port používá jiný program. Najdete ho příkazem `lsof -i :8502` (nebo `sudo ss -ltnp | grep 8502`), nebo namapujte jiný port hostitele (`"8503:8502"`) a spusťte `docker compose up -d`.
- **Z jiného počítače:** firewall serveru musí povolit 8502 (a 5055, viz níže).

První start po zapnutí `OPEN_NOTEBOOK_ENABLE_DOCLING` nebo `OPEN_NOTEBOOK_ENABLE_CRAWL4AI` nejdřív nainstaluje velké balíčky; záznam ukazuje `[entrypoint] Installing ...`. Počkejte, až instalace doběhne.

---

<a id="unable-to-connect-to-api-server"></a>
## „Nelze se připojit k serveru API“

Úplný text překryvného okna: **Nelze se připojit k serveru API** – „Server API aplikace Open Notebook není dostupný“. Na přihlašovací stránce se stejný problém zobrazí jako „Nelze se připojit k serveru. Zkontrolujte, zda běží API.“

Rozhraní se načetlo, ale prohlížeč se nedostane k API. V překryvném okně klikněte na **Zobrazit technické podrobnosti**: **Zkoušená URL** je adresa API, kterou prohlížeč použil.

**1. Běží API?**

```bash
curl http://localhost:5055/health
# {"status":"healthy"}
```

Žádná odpověď: hledejte chyby API v `docker compose logs open_notebook`. Problém s databází brání spuštění API (viz níže).

**2. Dostane se prohlížeč na Zkoušenou URL?**

Když není nastaveno `API_URL`, prohlížeč použije hostitele z adresního řádku a port 5055. Otevřete-li `http://192.168.1.50:8502`, volá `http://192.168.1.50:5055`. Proto:

- Port 5055 musí být publikovaný (`"5055:5055"` v dodaném souboru) a povolený firewallem serveru.
- Za reverzní proxy obvykle automaticky zjištěná adresa `https://vase-domena:5055` neexistuje. Nastavte `API_URL=https://vase-domena` (bez `/api`) v prostředí `open_notebook` a spusťte `docker compose up -d`. Viz [Reverse Proxy](../../5-CONFIGURATION/reverse-proxy.md#how-the-browser-finds-the-api) (anglicky).
- Pokud jste API publikovali na jiném portu hostitele, nastavte `API_URL` odpovídajícím způsobem (`http://<host>:<port>`).

Co kontejner dostal, ověříte příkazem `docker compose exec open_notebook printenv API_URL`. Změny vyžadují `docker compose up -d`; `docker compose restart` ponechá staré prostředí.

**3. Stránka přes HTTPS, API přes HTTP?** Prohlížeč to zablokuje jako smíšený obsah. Když je rozhraní servírováno přes HTTPS, musí `API_URL` začínat `https://`.

---

<a id="database-connection-failed"></a>
## „Připojení k databázi selhalo“

Úplný text překryvného okna: **Připojení k databázi selhalo** – „Server API běží, ale databáze není dostupná“. Zobrazí se, když se databáze stane nedostupnou za běhu API.

Pokud je databáze nedostupná při **startu** API, API se vůbec nespustí: jeho záznam během čekání ukazuje `Database is not reachable yet (attempt n/12)`, pak `Database did not become reachable after 12 attempts` a `CRITICAL: Database migration failed`. Prohlížeč se pak nedostane k API (**Nelze se připojit k serveru API**), nebo se v Docker image rozhraní vůbec nenačte, protože čeká na API. Příčiny a řešení jsou stejné.

```bash
docker compose ps surrealdb
docker compose logs --tail 50 surrealdb
docker compose exec open_notebook printenv SURREAL_URL SURREAL_USER SURREAL_NAMESPACE SURREAL_DATABASE   # bez hesel
```

| Příčina | Řešení |
|-------|-----|
| `surrealdb` neběží nebo spadl (často chyba oprávnění k `./surreal_data`) | Přečtěte jeho záznam. Dodaná služba běží jako `user: root`, aby mohla zapisovat do připojené složky |
| `SURREAL_URL` uvnitř Dockeru používá `localhost` | Použijte název služby: `ws://surrealdb:8000/rpc` |
| Chybný uživatel nebo heslo | `SURREAL_USER`/`SURREAL_PASSWORD` musí odpovídat `--user`/`--pass`, se kterými SurrealDB startoval. S dodaným souborem nastavte obojí v `.env`, aby se obě služby shodly |
| Spuštění ze zdrojového kódu s URL pro Docker | V `.env` použijte `ws://localhost:8000/rpc` |
| Firemní proxy, záznam API ukazuje HTTP 403 na websocketu databáze | Přidejte `surrealdb` a `localhost` do `NO_PROXY` ([Environment Reference → Outbound proxy](../../5-CONFIGURATION/environment-reference.md#outbound-proxy), anglicky) |

Více: [Database](../../5-CONFIGURATION/database.md) (anglicky).

---

## Úlohy na pozadí se nikdy nespustí

Zdroje zůstávají **Ve frontě**, podcasty **Čeká**, vektorizace nikdy nedoběhne. Worker neběží, nebo používá jiný jmenný prostor databáze. Viz [Potíže se zpracováním → Zdroje zůstávají „Ve frontě“](processing-issues.md#sources-stay-queued-waiting-to-be-processed).

---

## Pomalé stránky, 502 nebo 504 za proxy

- `502 Bad Gateway`: proxy se nedostane na port 8502 (kontejner neběží, nebo není v síti proxy).
- `504 Gateway Timeout` nebo `socket hang up` u dlouhých chatů a transformací: časový limit čtení proxy je kratší než požadavek. Nastavte ho alespoň na 600 sekund.

Viz [Reverse Proxy → Troubleshooting](../../5-CONFIGURATION/reverse-proxy.md#troubleshooting) (anglicky).

---

<a id="cors-errors-in-the-browser-console"></a>
## Chyby CORS v konzoli prohlížeče

`Cross-Origin Request Blocked` nebo `has been blocked by CORS policy`. Bez nastaveného hesla a `CORS_ORIGINS` přijímá API požadavky z `localhost` a ze stránek na stejném hostiteli; s heslem z jakéhokoli původu. Na výchozí instalaci chyba CORS proto skoro vždy skrývá jiný problém:

- **Stav 413:** nahrávání narazilo na limit velikosti ve vaší reverzní proxy ([Upload size](../../5-CONFIGURATION/reverse-proxy.md#upload-size-413-errors), anglicky).
- **502/504 nebo žádný stav:** proxy vrátila vlastní chybovou stránku, která nemá hlavičky CORS. Opravte původní chybu.
- **Rozhraní a API na různých názvech hostitele bez hesla:** nastavte heslo, nebo původ rozhraní uveďte v `CORS_ORIGINS`.
- **Nastavili jste `CORS_ORIGINS`:** původ z adresního řádku prohlížeče (schéma, hostitel a port) musí být v seznamu přesně. Viz [Security → CORS Origins](../../5-CONFIGURATION/security.md#cors-origins) (anglicky).

---

<a id="login-problems"></a>
## Potíže s přihlášením

- **„Neplatné heslo“**: heslo neodpovídá `OPEN_NOTEBOOK_PASSWORD`. Pokud jste ho právě změnili v `.env` nebo `docker-compose.yml`, použijte změnu příkazem `docker compose up -d`.
- **Odhlášení nebo „Neoprávněný přístup, zkontrolujte heslo“** po změně hesla: prohlížeč má stále staré. Odhlaste se a přihlaste znovu.

Viz [Security](../../5-CONFIGURATION/security.md#password-protection) (anglicky).

---

## Připojení k poskytovatelům (Test připojení)

„Cannot connect to server. Check the URL is correct.“ a „Cannot connect to Ollama. Check if Ollama server is running.“ pocházejí z tlačítka **Test** ve Spravovat → Modely. Týkají se adresy poskytovatele AI, ne vlastního API Open Notebooku. Viz [Potíže s AI a chatem → Test selže](ai-chat-issues.md#test-fails).

<a id="ssl-errors-with-a-provider"></a>
### Chyby SSL u poskytovatele

`[SSL: CERTIFICATE_VERIFY_FAILED]` v záznamu, nebo Test selhává jen se základní URL `https://`: poskytovatel používá certifikát, kterému kontejner nedůvěřuje (typicky vlastní certifikační autorita v laboratoři nebo firmě). Připojte do kontejneru soubor s certifikáty CA a nastavte `ESPERANTO_SSL_CA_BUNDLE`; platí pro volání modelů, Test i vyhledání modelů. Viz [Advanced → SSL](../../5-CONFIGURATION/advanced.md#ssl-for-self-signed-providers) (anglicky).

---

## Úplná kontrola

```bash
docker compose ps                                  # obě služby Up
curl -s http://localhost:5055/health               # {"status":"healthy"}
curl -s http://localhost:5055/api/config           # "dbStatus": "online"
docker compose logs --since 10m open_notebook | grep -iE "error|warning|critical"
```

---

## Související

- [Reverse Proxy](../../5-CONFIGURATION/reverse-proxy.md) (anglicky)
- [Database](../../5-CONFIGURATION/database.md) (anglicky)
- [Potíže se zpracováním](processing-issues.md)
- [Potíže s AI a chatem](ai-chat-issues.md)
