# Open Notebook pro více uživatelů na `arcmspark01`

Autor nasazení: **Hynek Cihlář** (Bc. Hynek Cihlář)

Open Notebook sám umí jen jednoho uživatele se sdíleným heslem. Proto má **každý uživatel vlastní instanci**: vlastní databázi, vlastní složku s nahranými soubory a vlastní šifrovací klíč. Nikdo nevidí sešity, zdroje ani poznámky ostatních. Jazykový model, embedding a Whisper jsou společné, takže na Sparku běží jen jednou.

```
prohlížeč ──HTTPS──> caddy (443) ──> oauth2-proxy ──> dex ──┬─ místní účty (uzivatele.conf)
https://notebook.cajk32.lab │                              └─ LDAP ucserver.cajk32.lab (doménové účty UCS)
                            │
                            └── podle přihlášeného e-mailu ──> on-u-<zkratka>:8502 ──> surrealdb (databáze u_<zkratka>)
                                                                     └──> vllm-qwen / vllm-embed / vllm-whisper (sdílené)
```

| Kontejner | Co dělá |
|---|---|
| `on-caddy` | HTTPS na `https://notebook.cajk32.lab` (certifikát z CA UCS), přihlášení, směrování na instanci uživatele |
| `on-oauth2-proxy` | Hlídá přihlášení (cookie `_on_sso`), po přihlášení předá Caddy e-mail uživatele |
| `on-dex` | Přihlašovací stránka: místní účty a doménové účty z UCS (LDAP) |
| `on-u-<zkratka>` | Instance Open Notebooku jednoho uživatele (nejvýš 5) |

- Uživatel z UCS se přihlašuje **uživatelským jménem a heslem z domény**. V Open Notebooku je veden jako `<jméno>@cajk32.lab`.
- Místní účet (pro lidi bez doménového účtu) se přihlašuje **e-mailem a heslem** zapsaným v `uzivatele.conf`.
- Kdo se přihlásí a v `uzivatele.conf` není, dostane stránku „není zřízena žádná instance“.
- **Vaše dosavadní data** převezme vaše instance (`puvodni=ano`). Nic se nekopíruje, jen se přepojí.
- Přihlašovací stránka Dexu je anglicky („Log in to Open Notebook“). Open Notebook za ní je česky.
- Správce arcmspark01 (`spark`, `sudo`) technicky vidí do všech databází. Oddělení platí pro uživatele aplikace.

**Paměť:** jedna instance si vezme zhruba 1,5–2 GB RAM, víc při zpracování velkých PDF. Po spuštění všech modelů zbývá na arcmspark01 asi 12 GB, takže pět instancí se vejde jen těsně. V kroku 12 se proto paměť kontroluje.

**Předpoklad:** nejdřív proveďte v [README.md](README.md) oddíl **Vyhledávání zdrojů na webu (SearXNG)**. Sestaví se v něm nová image Open Notebooku, kterou instance uživatelů používají, a do `.env` se doplní `SEARXNG_SECRET`.

**Co je potřeba od vás:** heslo uživatele `root` na `ucserver.cajk32.lab` (kroky 1–3, přes `su -`) a vaše uživatelské jméno v UCS (krok 9).

---

## Krok 1 – DNS záznamy `arcmspark01` a `notebook.cajk32.lab`

### 1a – adresa a DNS arcmspark01

**Stroj:** arcmspark01 · **Složka:** `/home/spark` · **Terminál:** SSH z Macu (`ssh spark@arcmspark01`)

```bash
cd /home/spark
hostname -I
ip -4 route get 192.168.110.250
resolvectl status | grep -E 'DNS Servers|DNS Domain'
getent hosts ucserver.cajk32.lab
```

**Očekávaný výstup:**
```
192.168.110.xxx 172.17.0.1 ...
192.168.110.250 dev <rozhraní> src 192.168.110.xxx uid 1000
       DNS Servers: 192.168.110.250
        DNS Domain: cajk32.lab
192.168.110.250  ucserver.cajk32.lab
```

Adresa za `src` je adresa arcmspark01 v síti laboratoře. Budete ji potřebovat v kroku 1b.

- Pokud `DNS Servers` neobsahuje `192.168.110.250`, arcmspark01 nepoužívá DNS z UCS. Napište mi a doplníme to.
- Jsou-li v `DNS Servers` i jiné servery (např. `192.168.110.1`, `8.8.8.8`), nevadí to: Dex se ptá jen DNS z UCS (`UCS_DNS` v `.env`).
- Pokud `getent` nic nevypíše, arcmspark01 nezná `ucserver.cajk32.lab` a přihlašování přes LDAP by nefungovalo.

### 1b – záznamy v DNS UCS

Příkazy `ucr`, `udm` a `univention-certificate` potřebují uživatele **root**. Uživatel `Administrator` je nemá v cestě a do `/root` nesmí. Proto se nejdřív přepnete na roota příkazem `su -` a zadáte heslo uživatele root na ucserver.

**Stroj:** ucserver.cajk32.lab · **Složka:** `/root` · **Terminál:** SSH z Macu (`ssh Administrator@ucserver.cajk32.lab`), po `su -` jako root

```bash
su -
```

**Očekávaný výstup:** výzva `Heslo:`. Po zadání hesla roota se výzva změní na `root@ucserver:~#`.

Místo `192.168.110.xxx` napište adresu arcmspark01 z kroku 1a.

```bash
cd /root
ucr get ldap/base
udm dns/host_record create \
  --superordinate "zoneName=cajk32.lab,cn=dns,$(ucr get ldap/base)" \
  --set name=arcmspark01 \
  --set a=192.168.110.xxx
udm dns/alias create \
  --superordinate "zoneName=cajk32.lab,cn=dns,$(ucr get ldap/base)" \
  --set name=notebook \
  --set cname=arcmspark01.cajk32.lab.
sleep 5
host arcmspark01.cajk32.lab
host notebook.cajk32.lab
```

**Očekávaný výstup:**
```
dc=cajk32,dc=lab
Object created: relativeDomainName=arcmspark01,zoneName=cajk32.lab,cn=dns,dc=cajk32,dc=lab
Object created: relativeDomainName=notebook,zoneName=cajk32.lab,cn=dns,dc=cajk32,dc=lab
arcmspark01.cajk32.lab has address 192.168.110.xxx
notebook.cajk32.lab is an alias for arcmspark01.cajk32.lab.
arcmspark01.cajk32.lab has address 192.168.110.xxx
```

- Pokud `ldap/base` vypíše jinou hodnotu než `dc=cajk32,dc=lab`, použijte ji ve všech dalších krocích.
- Hláška `Object exists` u `arcmspark01` znamená, že záznam už je (např. v jiné podobě). Pokračujte, jen ověřte, že `host arcmspark01.cajk32.lab` vrací správnou adresu.
- Okno s `root@ucserver:~#` nechte otevřené, použijete ho v krocích 2 a 3.

---

## Krok 2 – certifikát pro `notebook.cajk32.lab` z CA UCS

**Stroj:** ucserver.cajk32.lab · **Složka:** `/root` · **Terminál:** SSH jako root (`su -` z kroku 1b, výzva `root@ucserver:~#`)

```bash
cd /root
univention-certificate new -name notebook.cajk32.lab -days 1825
ls /etc/univention/ssl/notebook.cajk32.lab/
openssl x509 -noout -subject -enddate -in /etc/univention/ssl/notebook.cajk32.lab/cert.pem
```

**Očekávaný výstup:**
```
cert.pem  openssl.cnf  private.key  req.pem
subject=C = CZ, ..., CN = notebook.cajk32.lab, ...
notAfter=<datum za 5 let>
```

Počítače v doméně důvěřují kořenové CA UCS, takže prohlížeč nebude varovat.

---

## Krok 3 – servisní účet `svc-notebook` pro čtení LDAP

Dex se přes tento účet do LDAP jen dívá, jestli uživatel existuje, a pak ověří jeho heslo. Účet typu `users/ldap` se nemůže přihlásit k počítačům ani do UMC.

**Stroj:** ucserver.cajk32.lab · **Složka:** `/root` · **Terminál:** SSH jako root (`su -` z kroku 1b, výzva `root@ucserver:~#`)

```bash
cd /root
SVC_HESLO=$(openssl rand -hex 24)
udm users/ldap create \
  --position "cn=users,$(ucr get ldap/base)" \
  --set username=svc-notebook \
  --set lastname=Notebook \
  --set password="$SVC_HESLO"
echo "Heslo svc-notebook: $SVC_HESLO"
unset SVC_HESLO
```

**Očekávaný výstup:**
```
Object created: uid=svc-notebook,cn=users,dc=cajk32,dc=lab
Heslo svc-notebook: <48 znaků 0-9a-f>
```

Heslo si zkopírujte do správce hesel. Budete ho potřebovat v krocích 7 a 8.

---

## Krok 4 – stažení nové verze repozitáře

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook` · **Terminál:** SSH z Macu (`ssh spark@arcmspark01`)

```bash
cd /home/spark/open-notebook
git pull
git log -1 --format='%h %an %s'
ls /home/spark/open-notebook/deploy/arcmspark01
```

**Očekávaný výstup:**
```
<hash> Hynek Cihlář feat(deploy): Open Notebook pro více uživatelů …
README.md  VICE-UZIVATELU.md  docker-compose.vice-uzivatelu.yml  docker-compose.yml
generovat-vice-uzivatelu.py  kopirovat-nastaveni.py  prelozit-transformace.py
stav-stahovani.sh  uzivatele.conf.example  whisper.Dockerfile
```

---

## Krok 5 – volné porty 80 a 443

**Stroj:** arcmspark01 · **Složka:** `/home/spark` · **Terminál:** SSH

```bash
cd /home/spark
sudo -v
sudo ss -ltnp | grep -E ':(80|443)\s' || echo PORTY_VOLNE
sudo ufw status | head -1
id -u; id -g
```

**Očekávaný výstup:**
```
PORTY_VOLNE
Status: inactive
1000
1000
```

- Pokud místo `PORTY_VOLNE` vidíte proces (např. `nginx`), port obsadila jiná služba. Napište mi, co tam běží.
- Pokud `ufw` hlásí `Status: active`, povolte porty: `sudo ufw allow 80/tcp && sudo ufw allow 443/tcp`.
- Pokud `id -u` nebo `id -g` nevypíše `1000`, zapamatujte si čísla pro krok 8.

---

## Krok 6 – certifikáty na arcmspark01

Certifikát a klíč jsou tajné, proto se do gitu nedávají. Na arcmspark01 se jednorázově zkopírují ze serveru UCS.

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook-data/caddy/certs` · **Terminál:** SSH

```bash
mkdir -p /home/spark/open-notebook-data/caddy/certs /home/spark/open-notebook-data/caddy/data /home/spark/open-notebook-data/caddy/config
cd /home/spark/open-notebook-data/caddy/certs
scp root@ucserver.cajk32.lab:/etc/univention/ssl/notebook.cajk32.lab/cert.pem /home/spark/open-notebook-data/caddy/certs/notebook.crt
scp root@ucserver.cajk32.lab:/etc/univention/ssl/notebook.cajk32.lab/private.key /home/spark/open-notebook-data/caddy/certs/notebook.key
curl -fsS http://ucserver.cajk32.lab/ucs-root-ca.crt -o /home/spark/open-notebook-data/caddy/certs/ucs-root-ca.crt
chmod 600 /home/spark/open-notebook-data/caddy/certs/notebook.key
chmod 644 /home/spark/open-notebook-data/caddy/certs/notebook.crt /home/spark/open-notebook-data/caddy/certs/ucs-root-ca.crt
ls -l /home/spark/open-notebook-data/caddy/certs
openssl verify -CAfile /home/spark/open-notebook-data/caddy/certs/ucs-root-ca.crt /home/spark/open-notebook-data/caddy/certs/notebook.crt
```

`scp` se dvakrát zeptá na heslo uživatele root na ucserver. Pokud ucserver nepovoluje přihlášení roota přes SSH (`Permission denied`), napište mi, zkopírujeme soubory přes uživatele Administrator.

**Očekávaný výstup:**
```
-rw-r--r-- 1 spark spark ... notebook.crt
-rw------- 1 spark spark ... notebook.key
-rw-r--r-- 1 spark spark ... ucs-root-ca.crt
/home/spark/open-notebook-data/caddy/certs/notebook.crt: OK
```

---

## Krok 7 – zkouška LDAP z arcmspark01

Ověří, že arcmspark01 se dostane na LDAPS serveru UCS, že CA sedí a že heslo `svc-notebook` platí. Místo `VASE_JMENO` napište svoje uživatelské jméno v UCS.

**Stroj:** arcmspark01 · **Složka:** `/home/spark` · **Terminál:** SSH

```bash
cd /home/spark
sudo docker run --rm -it \
  -v /home/spark/open-notebook-data/caddy/certs/ucs-root-ca.crt:/ca.crt:ro \
  -e LDAPTLS_CACERT=/ca.crt \
  alpine:3 sh -c "apk add -q openldap-clients && ldapsearch -LLL -H ldaps://ucserver.cajk32.lab:636 -D 'uid=svc-notebook,cn=users,dc=cajk32,dc=lab' -W -b 'cn=users,dc=cajk32,dc=lab' '(uid=VASE_JMENO)' uid displayName"
```

Na výzvu `Enter LDAP Password:` vložte heslo `svc-notebook` z kroku 3.

**Očekávaný výstup:**
```
Enter LDAP Password:
dn: uid=VASE_JMENO,cn=users,dc=cajk32,dc=lab
uid: VASE_JMENO
displayName: <vaše jméno>
```

`ldap_bind: Invalid credentials (49)` znamená špatné heslo. `Can't contact LDAP server (-1)` znamená, že nesedí DNS, port 636 nebo CA.

---

## Krok 8 – doplnění `.env`

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
cp .env /home/spark/open-notebook-data/env-zaloha-$(date +%Y%m%d-%H%M%S)
grep -q '^ON_HOSTNAME=' .env || sed -n '/VÍCE UŽIVATELŮ/,$p' .env.example >> .env
sed -i "s/^OAUTH2_CLIENT_SECRET=$/OAUTH2_CLIENT_SECRET=$(openssl rand -hex 16)/" .env
sed -i "s/^OAUTH2_COOKIE_SECRET=$/OAUTH2_COOKIE_SECRET=$(openssl rand -hex 16)/" .env
read -rs -p 'Heslo svc-notebook: ' P; echo; sed -i "s/^LDAP_BIND_PW=$/LDAP_BIND_PW=$P/" .env; unset P
awk -F= '/^(ON_HOSTNAME|TLS_REZIM|LDAP_ZAPNUTO|LDAP_HOST|LDAP_USERS_DN|LDAP_EMAIL_PRIPONA)=/{print}
         /^(OAUTH2_CLIENT_SECRET|OAUTH2_COOKIE_SECRET|LDAP_BIND_PW)=/{print $1, length($2)}' .env
```

Na výzvu `Heslo svc-notebook:` vložte heslo z kroku 3. Při psaní se nezobrazuje.

**Očekávaný výstup:**
```
ON_HOSTNAME=notebook.cajk32.lab
TLS_REZIM=ucs
OAUTH2_CLIENT_SECRET 32
OAUTH2_COOKIE_SECRET 32
LDAP_ZAPNUTO=true
LDAP_HOST=ucserver.cajk32.lab:636
LDAP_BIND_PW 48
LDAP_USERS_DN=cn=users,dc=cajk32,dc=lab
LDAP_EMAIL_PRIPONA=cajk32.lab
```

Pokud v kroku 5 `id -u` / `id -g` nevypsaly `1000`, doplňte (čísla nahraďte):

```bash
echo 'ON_UID=1001' >> /home/spark/open-notebook/deploy/arcmspark01/.env
echo 'ON_GID=1001' >> /home/spark/open-notebook/deploy/arcmspark01/.env
```

---

## Krok 9 – seznam uživatelů `uzivatele.conf`

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
cp uzivatele.conf.example uzivatele.conf
chmod 600 uzivatele.conf
nano uzivatele.conf
```

V editoru upravte řádky pod hlavičkou:

- **Váš řádek:** místo `hcihlar` dejte svoje uživatelské jméno v UCS (to z kroku 7) a ponechte `puvodni=ano`. Vaše instance tak převezme dosavadní sešity a nastavení modelů.
- **Další uživatelé z domény:** `zkratka  <jméno v UCS>@cajk32.lab  ldap`.
- **Místní účet** (kdo nemá doménový účet): `zkratka  e-mail  mistni  heslo=<otisk>`. Otisk hesla vytvoříte příkazem níže.
- Řádky, které nepotřebujete, smažte. Nejvýš 5 uživatelů.

Uložení a zavření editoru: `Ctrl+O`, `Enter`, `Ctrl+X`.

Otisk hesla pro místní účet (heslo se zadá dvakrát a nikde se neuloží):

```bash
sudo docker run --rm -it caddy:2-alpine caddy hash-password
```

**Očekávaný výstup:**
```
Enter password:
Confirm password:
$2a$14$<53 znaků>
```

Celý řádek začínající `$2a$14$` vložte do `uzivatele.conf` za `heslo=`.

Vygenerování konfigurace:

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
python3 generovat-vice-uzivatelu.py
```

**Očekávaný výstup** (příklad pro tři uživatele):
```
Uživatelé (3):
  hynek        <jméno>@cajk32.lab   ldap    kontejner on-u-hynek   databáze open_notebook  API 127.0.0.1:5061  data /home/spark/open-notebook-data/notebook_data
  jana         jana.novakova@cajk32.lab  ldap  kontejner on-u-jana  databáze u_jana        API 127.0.0.1:5062  data /home/spark/open-notebook-data/uzivatele/jana
  host1        host1@notebook.local  mistni  kontejner on-u-host1   databáze u_host1        API 127.0.0.1:5063  data /home/spark/open-notebook-data/uzivatele/host1
  zapsáno: /home/spark/open-notebook-data/uzivatele/instance.json
  zapsáno: /home/spark/open-notebook/deploy/arcmspark01/vice-uzivatelu/docker-compose.uzivatele.yml
  zapsáno: /home/spark/open-notebook/deploy/arcmspark01/vice-uzivatelu/Caddyfile
  zapsáno: /home/spark/open-notebook/deploy/arcmspark01/vice-uzivatelu/dex.yaml
  vytvořena složka: /home/spark/open-notebook-data/uzivatele/jana
  vytvořena složka: /home/spark/open-notebook-data/uzivatele/host1
HOTOVO
```

Řádek začínající `CHYBA:` přesně řekne, co v `.env` nebo `uzivatele.conf` opravit. Soubor `/home/spark/open-notebook-data/uzivatele/instance.json` obsahuje šifrovací klíče instancí. **Zálohujte ho spolu s daty.**

---

## Krok 10 – zapnutí režimu více uživatelů a kontrola konfigurace

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sed -i 's/^# COMPOSE_FILE=/COMPOSE_FILE=/' .env
grep '^COMPOSE_FILE=' .env
sudo docker compose config --services | sort
sudo docker compose pull caddy oauth2-proxy dex
sudo docker compose run --rm --no-deps caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile 2>&1 | tail -1
```

**Očekávaný výstup:**
```
COMPOSE_FILE=docker-compose.yml:docker-compose.vice-uzivatelu.yml:vice-uzivatelu/docker-compose.uzivatele.yml
caddy
dex
oauth2-proxy
on-u-host1
on-u-hynek
on-u-jana
searxng
surrealdb
vllm-embed
vllm-qwen
vllm-whisper
 ✔ caddy Pulled
 ✔ oauth2-proxy Pulled
 ✔ dex Pulled
Valid configuration
```

Služba `open_notebook` (původní `on-app`) v seznamu není. To je správně, v režimu více uživatelů se nespouští.

---

## Krok 11 – záloha a vypnutí původní instance

Databáze se na chvíli zastaví, aby byla záloha konzistentní. Modely vLLM běží dál.

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook-data` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook-data
sudo docker stop on-app on-surrealdb
sudo tar czf /home/spark/zaloha-pred-vice-uzivateli-$(date +%Y%m%d-%H%M).tgz -C /home/spark/open-notebook-data surreal_data notebook_data
ls -lh /home/spark/zaloha-pred-vice-uzivateli-*.tgz
sudo docker rm on-app
```

**Očekávaný výstup:**
```
on-app
on-surrealdb
-rw-r--r-- 1 root root <velikost> ... /home/spark/zaloha-pred-vice-uzivateli-<datum>.tgz
on-app
```

---

## Krok 12 – spuštění

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sudo docker compose up -d
sleep 60
sudo docker compose ps --format 'table {{.Name}}\t{{.Status}}'
for c in $(sudo docker ps --format '{{.Names}}' | grep '^on-u-'); do echo "$c: $(sudo docker logs $c 2>&1 | grep -c 'API initialization completed successfully')"; done
sudo docker logs on-dex 2>&1 | grep -E 'listening|config connector|error' | tail -5
sudo docker logs on-caddy 2>&1 | grep -iE 'error|serving' | tail -3
free -g | head -2
```

**Očekávaný výstup:**
- všechny kontejnery `Up …`, vLLM `Up … (healthy)`
- každá instance `on-u-…: 1` (pokud `0`, počkejte další minutu, první start dělá migrace databáze, a příkaz `for …` zopakujte)
- Dex: `config connector: local` a/nebo `config connector: ucs` a `listening on 0.0.0.0:5556` (`(http)`)
- Caddy: bez řádků s `"level":"error"`
- `free -g`: sloupec `available` **alespoň 4**. Pokud je nižší, napište mi. Dá se snížit `ON_INSTANCE_MEM_LIMIT` nebo přesunout instance na VM.

---

## Krok 13 – nastavení modelů v instancích nových uživatelů

Nové instance jsou prázdné. Skript do nich zkopíruje vaše nastavení modelů (Qwen, bge-m3, Whisper, výchozí modely) a pak se přeloží transformace. **Ve vaší instanci musí být nejdřív nastavený Whisper** (Nastavení → Modely, typ převod řeči na text). Jinak se nepřenese.

Porty instancí jsou ve výpisu z kroku 9. Vaše instance (`puvodni=ano`) je obvykle `5061`. Příkazy opakujte pro každou novou instanci (`5062`, `5063`, …).

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
curl -s http://127.0.0.1:5062/health; echo
python3 kopirovat-nastaveni.py --zdroj http://127.0.0.1:5061/api --cil http://127.0.0.1:5062/api
python3 prelozit-transformace.py --api http://127.0.0.1:5062/api --bez-hesla
```

**Očekávaný výstup:**
```
{"status":"healthy"}
Přístupové údaje ve zdroji: 3
  ++ openai_compatible / <název> (http://vllm-qwen:8000/v1)
  ...
Modely ve zdroji: 3
  ++ language        qwen3.8-27b
  ++ embedding       bge-m3
  ++ speech_to_text  whisper-large-v3
Výchozí modely: default_chat_model, default_embedding_model, ...
Nastavení a výchozí prompt transformací zkopírovány.
HOTOVO: nových přístupů 3, nových modelů 3
Záloha uložena: /home/spark/open-notebook-data/transformace-zaloha-<datum>.json
  ++ ... → Rozbor odborného článku
  ...
```

Pro jistotu přeložte transformace i ve své instanci. Pokud už přeložené jsou, skript jen vypíše `už je přeloženo`:

```bash
python3 /home/spark/open-notebook/deploy/arcmspark01/prelozit-transformace.py --api http://127.0.0.1:5061/api --bez-hesla
```

---

## Krok 14 – zkouška v prohlížeči a kontrola zabezpečení

**Stroj:** Hyneks-Mac-mini · **Složka:** `~` · **Terminál:** zsh

```bash
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' https://notebook.cajk32.lab/
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' -H 'X-Auth-Request-Email: hcihlar@cajk32.lab' https://notebook.cajk32.lab/api/notebooks
curl -s -o /dev/null -w '%{http_code}\n' http://arcmspark01.cajk32.lab:8502/
```

**Očekávaný výstup:**
```
302 https://notebook.cajk32.lab/oauth2/sign_in?rd=https://notebook.cajk32.lab/
302 https://notebook.cajk32.lab/oauth2/sign_in?rd=https://notebook.cajk32.lab/api/notebooks
000
```

Druhý řádek ověřuje, že podvržená hlavička s cizím e-mailem nikam nepustí. Třetí ověřuje, že starý port 8502 už není dostupný. Pokud `curl` hlásí chybu certifikátu, Mac nedůvěřuje CA UCS. Kořenový certifikát `http://ucserver.cajk32.lab/ucs-root-ca.crt` je pak potřeba přidat do Klíčenky jako důvěryhodný.

V prohlížeči otevřete **https://notebook.cajk32.lab**:

1. Objeví se přihlášení Dexu. Pokud jsou zapnuté místní účty i LDAP, vyberte **„Doménový účet (UCS)“**.
2. Zadejte uživatelské jméno a heslo z UCS.
3. Otevře se váš Open Notebook s dosavadními sešity, bez dalšího hesla.
4. Odhlášení: **https://notebook.cajk32.lab/oauth2/sign_out**

Stejně vyzkoušejte jiného uživatele, nejlépe v anonymním okně. Měl by vidět prázdný Open Notebook s nastavenými modely.

---

## Přidání, změna a odebrání uživatele

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
nano uzivatele.conf
python3 generovat-vice-uzivatelu.py
sudo docker compose up -d --remove-orphans
sudo docker compose restart caddy dex
sudo docker compose ps --format 'table {{.Name}}\t{{.Status}}'
```

**Očekávaný výstup:** výpis uživatelů a `HOTOVO`, potom nová instance `on-u-<zkratka>` ve stavu `Up`. U nového uživatele pokračujte krokem 13 s jeho portem.

- **Odebraný uživatel:** jeho kontejner zmizí (`--remove-orphans`), data zůstanou v `/home/spark/open-notebook-data/uzivatele/<zkratka>` a v databázi `u_<zkratka>`. Když ho vrátíte se stejnou zkratkou, dostane svá data zpět.
- **Změna hesla místního účtu:** nový otisk (`caddy hash-password` z kroku 9) do `uzivatele.conf`, pak `generovat-vice-uzivatelu.py` a `restart caddy dex`.
- **Doménový účet:** heslo se mění v UCS. V Open Notebooku se nic nedělá.

## Aktualizace na novou verzi

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook
git pull
cd /home/spark/open-notebook/deploy/arcmspark01
sudo -v
nohup sudo -n docker compose --profile jedna-instance build open_notebook > /home/spark/open-notebook-data/build-$(date +%Y%m%d-%H%M).log 2>&1 &
```

Sestavení trvá 10–25 minut. Doběhlo, když `pgrep -f "docker compose" || echo DOBEHLO` vypíše `DOBEHLO`. Úspěšně, pokud log ukazuje `open_notebook  Built` (nebo `naming to docker.io/library/open-notebook-cs:local`):

```bash
tail -3 $(ls -t /home/spark/open-notebook-data/build-*.log | head -1)
```

Potom vygenerujte konfiguraci a restartujte instance (vLLM zůstanou běžet):

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
python3 generovat-vice-uzivatelu.py
sudo docker compose up -d --remove-orphans
sudo docker compose ps --format 'table {{.Name}}\t{{.Status}}'
```

## Záloha

Zálohujte celou složku `/home/spark/open-notebook-data`. Obsahuje databázi (`surreal_data`), soubory všech uživatelů (`notebook_data`, `uzivatele/`), **šifrovací klíče instancí** (`uzivatele/instance.json`) a certifikáty (`caddy/certs`). Navíc zálohujte `/home/spark/open-notebook/deploy/arcmspark01/.env` a `uzivatele.conf`.

## Návrat do režimu jednoho uživatele

**Stroj:** arcmspark01 · **Složka:** `/home/spark/open-notebook/deploy/arcmspark01` · **Terminál:** SSH

```bash
cd /home/spark/open-notebook/deploy/arcmspark01
sudo docker compose down caddy oauth2-proxy dex
sudo docker ps --format '{{.Names}}' | grep '^on-u-' | xargs -r sudo docker rm -f
sed -i 's/^COMPOSE_FILE=/# COMPOSE_FILE=/' .env
sudo docker compose up -d open_notebook
```

Původní `on-app` (porty 8502/5055, sdílené heslo) má vaše data (databáze `open_notebook`). Data ostatních uživatelů zůstanou uložená.

## Řešení potíží

| Příznak | Příčina a řešení |
|---|---|
| Prohlížeč hlásí nedůvěryhodný certifikát | Počítač nedůvěřuje CA UCS. Importujte `http://ucserver.cajk32.lab/ucs-root-ca.crt`. Dočasně lze v `.env` nastavit `TLS_REZIM=interni`, pak `generovat-vice-uzivatelu.py` a `sudo docker compose restart caddy`. |
| Dex: „Internal Server Error“ / „Login error“ po zadání hesla | `sudo docker logs on-dex 2>&1 \| tail -20`. `Invalid credentials` znamená špatné heslo `svc-notebook` v `.env` (zopakujte krok 7). `no such host` znamená problém s DNS. `x509` znamená, že chybí `ucs-root-ca.crt` (krok 6). |
| Dex: „Invalid username and password“ | Špatné heslo uživatele. U doménových účtů se zadává uživatelské jméno (ne e-mail), u místních e-mail. |
| „Pro účet … není zřízena žádná instance“ | E-mail ve zprávě se neshoduje s `uzivatele.conf`. Opravte řádek (u LDAP `<jméno v UCS>@cajk32.lab`, malými písmeny), pak `generovat-vice-uzivatelu.py` a `sudo docker compose restart caddy`. |
| Smyčka přesměrování / „Unable to find a valid CSRF token“ | Smažte v prohlížeči cookies pro `notebook.cajk32.lab`. Zkontrolujte, že `OAUTH2_COOKIE_SECRET` má 32 znaků (krok 8). |
| `on-dex` se restartuje, v logu `permission denied` u `config.yaml` | UID ve `.env` (`ON_UID`, `ON_GID`) neodpovídá vlastníkovi souboru `vice-uzivatelu/dex.yaml` (`ls -ln vice-uzivatelu/dex.yaml`). |
| Instance `on-u-…` skončila (`Exited (137)`) | Došla paměť. Ověřte `free -g` a `sudo docker stats --no-stream`. Snižte počet instancí nebo `ON_INSTANCE_MEM_LIMIT`. |
| V nové instanci nejsou modely | Krok 13 neproběhl nebo hlásil chybu. Spusťte ho znovu, je bezpečné ho opakovat. |
