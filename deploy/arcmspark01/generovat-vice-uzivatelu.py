#!/usr/bin/env python3
"""Vygeneruje konfiguraci Open Notebooku pro více uživatelů (arcmspark01).

Autor: Hynek Cihlář (Bc. Hynek Cihlář)

Čte:
  .env              – společné nastavení (ON_HOSTNAME, LDAP_*, OAUTH2_*, ...)
  uzivatele.conf    – seznam uživatelů (vzor: uzivatele.conf.example)

Zapisuje do složky vice-uzivatelu/ (není v gitu, práva 600):
  docker-compose.uzivatele.yml – jedna instance Open Notebooku na uživatele
  Caddyfile                    – HTTPS, přihlášení a směrování podle e-mailu
  dex.yaml                     – místní účty a/nebo napojení na LDAP (UCS)

Tajné hodnoty instancí (šifrovací klíč, port API) se vytvoří jen jednou
a uloží do ON_DATA_DIR/uzivatele/instance.json. Při dalším spuštění se
použijí znovu – po změně klíče by instance neuměla přečíst uložené
přístupové údaje k modelům. Soubor zálohujte spolu s daty.

Jen standardní knihovna Pythonu. Spuštění:
  python3 generovat-vice-uzivatelu.py [--nanecisto]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
import uuid
from pathlib import Path

MAX_UZIVATELU = 5
PRVNI_PORT_API = 5061
ZKRATKA_RE = re.compile(r"^[a-z][a-z0-9-]{1,19}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+$")
BCRYPT_RE = re.compile(r"^\$2[aby]\$\d\d\$[./A-Za-z0-9]{53}$")


class ChybaKonfigurace(Exception):
    pass


def nacti_env(soubor: Path) -> dict[str, str]:
    """Jednoduchý čtenář .env (KLIC=hodnota, # komentáře, volitelné uvozovky)."""
    hodnoty: dict[str, str] = {}
    if not soubor.exists():
        raise ChybaKonfigurace(f"Chybí soubor {soubor}")
    for radek in soubor.read_text(encoding="utf-8").splitlines():
        radek = radek.strip()
        if not radek or radek.startswith("#") or "=" not in radek:
            continue
        klic, hodnota = radek.split("=", 1)
        hodnota = hodnota.strip()
        if len(hodnota) >= 2 and hodnota[0] == hodnota[-1] and hodnota[0] in "'\"":
            hodnota = hodnota[1:-1]
        hodnoty[klic.strip()] = hodnota
    return hodnoty


def ano(hodnota: str | None) -> bool:
    return (hodnota or "").strip().lower() in {"1", "true", "ano", "yes"}


def nacti_uzivatele(soubor: Path, env: dict[str, str]) -> list[dict]:
    if not soubor.exists():
        raise ChybaKonfigurace(
            f"Chybí soubor {soubor} – zkopírujte uzivatele.conf.example a doplňte."
        )
    ldap_zapnuto = ano(env.get("LDAP_ZAPNUTO"))
    pripona = env.get("LDAP_EMAIL_PRIPONA", "").strip().lower()
    uzivatele: list[dict] = []
    for cislo, radek in enumerate(soubor.read_text(encoding="utf-8").splitlines(), 1):
        # bcrypt otisk znak # neobsahuje, komentář lze uříznout bezpečně
        radek = radek.split("#", 1)[0].strip()
        if not radek:
            continue
        casti = radek.split()
        if len(casti) < 3:
            raise ChybaKonfigurace(
                f"uzivatele.conf řádek {cislo}: čekám „zkratka e-mail zdroj …“"
            )
        zkratka, email, zdroj = casti[0], casti[1].lower(), casti[2].lower()
        volby: dict[str, str] = {}
        for cast in casti[3:]:
            if "=" not in cast:
                raise ChybaKonfigurace(
                    f"uzivatele.conf řádek {cislo}: „{cast}“ není ve tvaru klic=hodnota"
                )
            k, v = cast.split("=", 1)
            volby[k.lower()] = v
        if not ZKRATKA_RE.match(zkratka):
            raise ChybaKonfigurace(
                f"uzivatele.conf řádek {cislo}: zkratka „{zkratka}“ – jen malá písmena bez diakritiky, "
                "číslice a pomlčka, 2–20 znaků, začíná písmenem"
            )
        if not EMAIL_RE.match(email):
            raise ChybaKonfigurace(
                f"uzivatele.conf řádek {cislo}: „{email}“ není e-mail"
            )
        if zdroj not in {"ldap", "mistni"}:
            raise ChybaKonfigurace(
                f"uzivatele.conf řádek {cislo}: zdroj musí být „ldap“ nebo „mistni“"
            )
        if zdroj == "ldap":
            if not ldap_zapnuto:
                raise ChybaKonfigurace(
                    f"uzivatele.conf řádek {cislo}: uživatel z LDAP, ale v .env není LDAP_ZAPNUTO=true"
                )
            if not email.endswith("@" + pripona):
                raise ChybaKonfigurace(
                    f"uzivatele.conf řádek {cislo}: uživatel z LDAP musí mít e-mail "
                    f"<uživatelské jméno v UCS>@{pripona}"
                )
        heslo = volby.get("heslo", "")
        if zdroj == "mistni" and not BCRYPT_RE.match(heslo):
            raise ChybaKonfigurace(
                f"uzivatele.conf řádek {cislo}: místní účet potřebuje heslo=<bcrypt otisk> "
                "(vytvoříte příkazem z VICE-UZIVATELU.md)"
            )
        uzivatele.append(
            {
                "zkratka": zkratka,
                "email": email,
                "zdroj": zdroj,
                "heslo": heslo,
                "puvodni": ano(volby.get("puvodni")),
            }
        )

    if not uzivatele:
        raise ChybaKonfigurace("uzivatele.conf neobsahuje žádného uživatele")
    if len(uzivatele) > MAX_UZIVATELU:
        raise ChybaKonfigurace(
            f"uzivatele.conf: {len(uzivatele)} uživatelů, na arcmspark01 je počítáno nejvýš s {MAX_UZIVATELU}"
        )
    for klic in ("zkratka", "email"):
        hodnoty = [u[klic] for u in uzivatele]
        duplicity = sorted({h for h in hodnoty if hodnoty.count(h) > 1})
        if duplicity:
            raise ChybaKonfigurace(
                f"uzivatele.conf: opakuje se {klic}: {', '.join(duplicity)}"
            )
    if sum(u["puvodni"] for u in uzivatele) > 1:
        raise ChybaKonfigurace(
            "uzivatele.conf: „puvodni=ano“ smí mít nejvýš jeden uživatel"
        )
    return uzivatele


def nacti_instance(
    soubor: Path, uzivatele: list[dict], env: dict[str, str]
) -> tuple[dict, bool]:
    """Vrátí trvalé údaje instancí (klíč, port); nové doplní, nic nepřepíše."""
    instance: dict = {}
    if soubor.exists():
        instance = json.loads(soubor.read_text(encoding="utf-8"))
    zmena = False
    pouzite_porty = {v["port_api"] for v in instance.values()}
    for u in uzivatele:
        if u["zkratka"] in instance:
            continue
        port = PRVNI_PORT_API
        while port in pouzite_porty:
            port += 1
        pouzite_porty.add(port)
        if u["puvodni"]:
            klic = env.get("OPEN_NOTEBOOK_ENCRYPTION_KEY", "")
            if not klic:
                raise ChybaKonfigurace(
                    "„puvodni=ano“ potřebuje OPEN_NOTEBOOK_ENCRYPTION_KEY v .env"
                )
        else:
            klic = secrets.token_hex(32)
        instance[u["zkratka"]] = {"sifrovaci_klic": klic, "port_api": port}
        zmena = True
    return instance, zmena


def nazev_databaze(u: dict) -> str:
    return "open_notebook" if u["puvodni"] else "u_" + u["zkratka"].replace("-", "_")


def slozka_dat(u: dict, data_dir: str) -> str:
    if u["puvodni"]:
        return f"{data_dir}/notebook_data"
    return f"{data_dir}/uzivatele/{u['zkratka']}"


def compose_uzivatelu(
    uzivatele: list[dict], instance: dict, env: dict[str, str]
) -> str:
    data_dir = env.get("ON_DATA_DIR", "/home/spark/open-notebook-data")
    host = env["ON_HOSTNAME"]
    radky = [
        "# VYGENEROVÁNO skriptem generovat-vice-uzivatelu.py – neupravujte ručně.",
        "# Obsahuje šifrovací klíče instancí. Necommitovat.",
        "",
        "x-open-notebook: &open-notebook",
        "  image: open-notebook-cs:${ON_IMAGE_TAG:-local}",
        "  restart: unless-stopped",
        "  mem_limit: ${ON_INSTANCE_MEM_LIMIT:-4g}",
        "  depends_on:",
        "    - surrealdb",
        "",
        "x-open-notebook-env: &open-notebook-env",
        f"  API_URL: {json.dumps('https://' + host)}",
        f"  CORS_ORIGINS: {json.dumps('https://' + host)}",
        "  SURREAL_URL: ws://surrealdb:8000/rpc",
        "  SURREAL_USER: ${SURREAL_USER:-root}",
        "  SURREAL_PASSWORD: ${SURREAL_PASSWORD:-root}",
        "  SURREAL_NAMESPACE: open_notebook",
        "  ESPERANTO_LLM_TIMEOUT: ${ESPERANTO_LLM_TIMEOUT:-420}",
        "  OPEN_NOTEBOOK_WORKER_MAX_TASKS: ${ON_INSTANCE_WORKER_MAX_TASKS:-1}",
        "  OPEN_NOTEBOOK_ENABLE_DOCLING: ${ENABLE_DOCLING:-false}",
        "  CCORE_AUDIO_CONCURRENCY: ${CCORE_AUDIO_CONCURRENCY:-2}",
        "",
        "services:",
    ]
    for u in uzivatele:
        i = instance[u["zkratka"]]
        radky += [
            f"  on-u-{u['zkratka']}:",
            "    <<: *open-notebook",
            f"    container_name: on-u-{u['zkratka']}",
            "    ports:",
            f'      - "127.0.0.1:{i["port_api"]}:5055"   # API jen pro správce na arcmspark01',
            "    environment:",
            "      <<: *open-notebook-env",
            f"      SURREAL_DATABASE: {nazev_databaze(u)}",
            f"      OPEN_NOTEBOOK_ENCRYPTION_KEY: {json.dumps(i['sifrovaci_klic'])}",
            "    volumes:",
            f"      - {slozka_dat(u, data_dir)}:/app/data",
            "",
        ]
    return "\n".join(radky)


def caddyfile(uzivatele: list[dict], env: dict[str, str]) -> str:
    host = env["ON_HOSTNAME"]
    rezim = env.get("TLS_REZIM", "ucs").strip().lower()
    if rezim == "ucs":
        tls = "tls /certs/notebook.crt /certs/notebook.key"
    elif rezim == "interni":
        tls = "tls internal"
    else:
        raise ChybaKonfigurace("TLS_REZIM v .env musí být „ucs“ nebo „interni“")
    mapa = "\n".join(
        f"\t\t\t\t{u['email']}\ton-u-{u['zkratka']}:8502" for u in uzivatele
    )
    max_mb = env.get("ON_MAX_UPLOAD_MB", "100")
    return f"""# VYGENEROVÁNO skriptem generovat-vice-uzivatelu.py – neupravujte ručně.
{{
\tadmin off
}}

http://{host} {{
\tredir https://{host}{{uri}} permanent
}}

{host} {{
\t{tls}

\trequest_body {{
\t\tmax_size {max_mb}MB
\t}}

\t# Přihlašovací server (místní účty a LDAP UCS) – bez kontroly přihlášení
\thandle /dex/* {{
\t\treverse_proxy dex:5556
\t}}

\t# Přihlášení, odhlášení a návrat z Dexu
\thandle /oauth2/* {{
\t\treverse_proxy oauth2-proxy:4180 {{
\t\t\theader_up X-Real-IP {{remote_host}}
\t\t\theader_up X-Forwarded-Uri {{uri}}
\t\t}}
\t}}

\thandle {{
\t\troute {{
\t\t\t# Hlavičky s identitou smí nastavit jen oauth2-proxy, nikdy prohlížeč
\t\t\trequest_header -X-Auth-Request-Email
\t\t\trequest_header -X-Auth-Request-User
\t\t\trequest_header -X-Auth-Request-Preferred-Username

\t\t\tforward_auth oauth2-proxy:4180 {{
\t\t\t\turi /oauth2/auth
\t\t\t\theader_up X-Real-IP {{remote_host}}
\t\t\t\tcopy_headers X-Auth-Request-Email X-Auth-Request-User
\t\t\t\t@neprihlasen status 401
\t\t\t\thandle_response @neprihlasen {{
\t\t\t\t\tredir * /oauth2/sign_in?rd={{scheme}}://{{host}}{{uri}}
\t\t\t\t}}
\t\t\t}}

\t\t\t# Přihlášený e-mail -> instance uživatele (uzivatele.conf)
\t\t\tmap {{http.request.header.X-Auth-Request-Email}} {{on_instance}} {{
{mapa}
\t\t\t\tdefault\tzadna
\t\t\t}}

\t\t\t@bez_instance vars {{on_instance}} zadna
\t\t\trespond @bez_instance "Pro účet {{http.request.header.X-Auth-Request-Email}} není zřízena žádná instance Open Notebooku. Obraťte se na správce. Odhlásit: https://{host}/oauth2/sign_out" 403

\t\t\treverse_proxy {{on_instance}} {{
\t\t\t\theader_up -X-Auth-Request-User
\t\t\t\tflush_interval -1
\t\t\t\ttransport http {{
\t\t\t\t\tread_timeout 600s
\t\t\t\t\twrite_timeout 600s
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t}}
}}
"""


def dex_yaml(uzivatele: list[dict], env: dict[str, str]) -> str:
    host = env["ON_HOSTNAME"]
    mistni = [u for u in uzivatele if u["zdroj"] == "mistni"]
    konfigurace: dict = {
        "issuer": f"https://{host}/dex",
        "storage": {"type": "memory"},
        "web": {"http": "0.0.0.0:5556"},
        "frontend": {"issuer": "Open Notebook", "theme": "light"},
        "oauth2": {"skipApprovalScreen": True},
        "expiry": {"idTokens": "1h"},
        "logger": {"level": "info"},
        "staticClients": [
            {
                "id": "open-notebook",
                "name": "Open Notebook",
                "secret": env["OAUTH2_CLIENT_SECRET"],
                "redirectURIs": [f"https://{host}/oauth2/callback"],
            }
        ],
        "enablePasswordDB": bool(mistni),
    }
    if mistni:
        konfigurace["staticPasswords"] = [
            {
                "email": u["email"],
                "hash": u["heslo"],
                "username": u["zkratka"],
                "userID": str(
                    uuid.uuid5(uuid.NAMESPACE_URL, "open-notebook:" + u["email"])
                ),
            }
            for u in mistni
        ]
    if ano(env.get("LDAP_ZAPNUTO")):
        for klic in (
            "LDAP_HOST",
            "LDAP_BIND_DN",
            "LDAP_BIND_PW",
            "LDAP_USERS_DN",
            "LDAP_EMAIL_PRIPONA",
        ):
            if not env.get(klic):
                raise ChybaKonfigurace(f"LDAP_ZAPNUTO=true, ale v .env chybí {klic}")
        konfigurace["connectors"] = [
            {
                "type": "ldap",
                "id": "ucs",
                "name": env.get("LDAP_NAZEV", "Doménový účet (UCS)"),
                "config": {
                    "host": env["LDAP_HOST"],
                    "rootCA": "/etc/dex/ucs-root-ca.crt",
                    "bindDN": env["LDAP_BIND_DN"],
                    "bindPW": env["LDAP_BIND_PW"],
                    "usernamePrompt": "Uživatelské jméno (UCS)",
                    "userSearch": {
                        "baseDN": env["LDAP_USERS_DN"],
                        "filter": env.get("LDAP_FILTR") or "(objectClass=person)",
                        "username": "uid",
                        "idAttr": "uid",
                        # e-mail = <uid>@<LDAP_EMAIL_PRIPONA> (Dex skládá z nameAttr)
                        "nameAttr": "uid",
                        "emailAttr": "mailPrimaryAddress",
                        "emailSuffix": env["LDAP_EMAIL_PRIPONA"],
                        "preferredUsernameAttr": "uid",
                    },
                },
            }
        ]
    if not mistni and not ano(env.get("LDAP_ZAPNUTO")):
        raise ChybaKonfigurace("Není zapnuté LDAP ani zadaný žádný místní účet")
    # JSON je platný YAML a bezpečně ošetří všechny znaky v heslech a otiscích
    return (
        "# VYGENEROVÁNO skriptem generovat-vice-uzivatelu.py – neupravujte ručně.\n"
        + json.dumps(konfigurace, ensure_ascii=False, indent=2)
        + "\n"
    )


def zapis(soubor: Path, obsah: str, nanecisto: bool) -> None:
    if nanecisto:
        print(f"--- {soubor} (nanečisto, nezapsáno) ---")
        return
    soubor.parent.mkdir(parents=True, exist_ok=True)
    docasny = soubor.with_suffix(soubor.suffix + ".novy")
    docasny.write_text(obsah, encoding="utf-8")
    os.chmod(docasny, 0o600)
    docasny.replace(soubor)
    print(f"  zapsáno: {soubor}")


def main() -> int:
    skript_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Konfigurace Open Notebooku pro více uživatelů."
    )
    parser.add_argument("--env", default=str(skript_dir / ".env"))
    parser.add_argument("--uzivatele", default=str(skript_dir / "uzivatele.conf"))
    parser.add_argument("--vystup", default=str(skript_dir / "vice-uzivatelu"))
    parser.add_argument(
        "--nanecisto", action="store_true", help="jen zkontrolovat, nic nezapisovat"
    )
    args = parser.parse_args()

    try:
        env = nacti_env(Path(args.env))
        for klic in ("ON_HOSTNAME", "OAUTH2_CLIENT_SECRET", "OAUTH2_COOKIE_SECRET"):
            if not env.get(klic):
                raise ChybaKonfigurace(f"V .env chybí {klic}")
        uzivatele = nacti_uzivatele(Path(args.uzivatele), env)
        data_dir = env.get("ON_DATA_DIR", "/home/spark/open-notebook-data")
        soubor_instanci = Path(data_dir) / "uzivatele" / "instance.json"
        instance, zmena = nacti_instance(soubor_instanci, uzivatele, env)

        vystup = Path(args.vystup)
        print(f"Uživatelé ({len(uzivatele)}):")
        for u in uzivatele:
            i = instance[u["zkratka"]]
            print(
                f"  {u['zkratka']:<12} {u['email']:<32} {u['zdroj']:<7} "
                f"kontejner on-u-{u['zkratka']:<12} databáze {nazev_databaze(u):<16} "
                f"API 127.0.0.1:{i['port_api']}  data {slozka_dat(u, data_dir)}"
            )
        obsahy = {
            vystup / "docker-compose.uzivatele.yml": compose_uzivatelu(
                uzivatele, instance, env
            ),
            vystup / "Caddyfile": caddyfile(uzivatele, env),
            vystup / "dex.yaml": dex_yaml(uzivatele, env),
        }
        if zmena:
            zapis(
                soubor_instanci, json.dumps(instance, indent=2) + "\n", args.nanecisto
            )
        for soubor, obsah in obsahy.items():
            zapis(soubor, obsah, args.nanecisto)
        uid = str(os.getuid())
        if not args.nanecisto and uid != env.get("ON_UID", "1000"):
            print(
                f"  POZOR: běžíte pod UID {uid}, Dex čte dex.yaml pod UID {env.get('ON_UID', '1000')} – "
                f"doplňte do .env ON_UID={uid} a ON_GID={os.getgid()}"
            )
        if not args.nanecisto:
            for u in uzivatele:
                slozka = Path(slozka_dat(u, data_dir))
                if not slozka.exists():
                    slozka.mkdir(parents=True)
                    print(f"  vytvořena složka: {slozka}")
    except ChybaKonfigurace as e:
        print(f"CHYBA: {e}", file=sys.stderr)
        return 1
    print("HOTOVO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
