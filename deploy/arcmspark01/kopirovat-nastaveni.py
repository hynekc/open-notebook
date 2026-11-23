#!/usr/bin/env python3
"""Zkopíruje nastavení modelů z jedné instance Open Notebooku do jiné.

Autor: Hynek Cihlář (Bc. Hynek Cihlář)

Použití na arcmspark01 při zakládání nového uživatele: hotové nastavení
z vaší instance (přístupy k vLLM, modely Qwen / bge-m3 / Whisper, výchozí
modely, nastavení zpracování obsahu, výchozí prompt transformací) se
přenese do čisté instance nového uživatele.

Kopíruje se:
  - přístupové údaje (credentials) – bez API klíčů, ty API nikdy nevrací;
    lokální vLLM klíč nepotřebuje. Má-li zdroj klíč, cíl dostane hodnotu
    z --api-klic a skript na to upozorní.
  - modely a jejich vazba na přístupové údaje
  - výchozí modely (chat, transformace, nástroje, velký kontext, embedding, STT, TTS)
  - nastavení (/api/settings)
  - výchozí prompt transformací
Názvy a texty vestavěných transformací přeloží prelozit-transformace.py.

Co v cíli už existuje (stejný název a poskytovatel), se nevytváří znovu.

Spuštění (jen standardní knihovna Pythonu):
  python3 kopirovat-nastaveni.py --zdroj http://127.0.0.1:5061/api \
                                 --cil   http://127.0.0.1:5062/api [--nanecisto]
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

POLE_PRISTUPU = (
    "name",
    "provider",
    "modalities",
    "base_url",
    "endpoint",
    "api_version",
    "endpoint_llm",
    "endpoint_embedding",
    "endpoint_stt",
    "endpoint_tts",
    "project",
    "location",
    "credentials_path",
    "num_ctx",
)
POLE_NASTAVENI = (
    "default_content_processing_engine_doc",
    "default_content_processing_engine_url",
    "default_embedding_option",
    "auto_delete_files",
    "docling_ocr",
    "docling_formulas",
    "docling_vision",
    "docling_vision_url",
    "docling_vision_model",
    "docling_vision_prompt",
    "youtube_preferred_languages",
)


class Api:
    def __init__(self, zaklad: str, heslo: str = "") -> None:
        self.zaklad = zaklad.rstrip("/")
        self.heslo = heslo

    def __call__(self, metoda: str, cesta: str, data: dict | None = None):
        telo = json.dumps(data).encode("utf-8") if data is not None else None
        pozadavek = urllib.request.Request(
            self.zaklad + cesta, data=telo, method=metoda
        )
        pozadavek.add_header("Content-Type", "application/json")
        if self.heslo:
            pozadavek.add_header("Authorization", f"Bearer {self.heslo}")
        with urllib.request.urlopen(pozadavek, timeout=60) as odpoved:
            obsah = odpoved.read().decode("utf-8")
            return json.loads(obsah) if obsah else None


def klic_pristupu(p: dict) -> tuple:
    return (p.get("provider"), p.get("name"))


def klic_modelu(m: dict) -> tuple:
    return (m.get("provider"), m.get("name"), m.get("type"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Zkopíruje nastavení modelů mezi instancemi."
    )
    parser.add_argument(
        "--zdroj",
        required=True,
        help="API zdrojové instance, např. http://127.0.0.1:5061/api",
    )
    parser.add_argument(
        "--cil",
        required=True,
        help="API cílové instance, např. http://127.0.0.1:5062/api",
    )
    parser.add_argument(
        "--zdroj-heslo", default="", help="heslo zdrojové instance (je-li nastavené)"
    )
    parser.add_argument(
        "--cil-heslo", default="", help="heslo cílové instance (je-li nastavené)"
    )
    parser.add_argument(
        "--api-klic",
        default="nepouzito",
        help="API klíč pro přístupy, které ho ve zdroji mají",
    )
    parser.add_argument(
        "--nanecisto", action="store_true", help="jen vypsat, nic neměnit"
    )
    args = parser.parse_args()

    if args.zdroj.rstrip("/") == args.cil.rstrip("/"):
        print("CHYBA: zdroj a cíl jsou stejná instance")
        return 1
    zdroj = Api(args.zdroj, args.zdroj_heslo)
    cil = Api(args.cil, args.cil_heslo)

    try:
        z_pristupy = zdroj("GET", "/credentials")
        z_modely = zdroj("GET", "/models")
        z_vychozi = zdroj("GET", "/models/defaults")
        z_nastaveni = zdroj("GET", "/settings")
        z_prompt = zdroj("GET", "/transformations/default-prompt")
        c_pristupy = cil("GET", "/credentials")
        c_modely = cil("GET", "/models")
    except urllib.error.HTTPError as e:
        print(f"CHYBA: API vrátilo {e.code} ({e.reason}) – {e.url}")
        return 1
    except urllib.error.URLError as e:
        print(f"CHYBA: API není dostupné: {e.reason}")
        return 1

    pocty = {"pristupy": 0, "modely": 0}
    mapa_pristupu: dict[str, str] = {}
    existujici_pristupy = {klic_pristupu(p): p["id"] for p in c_pristupy}
    print(f"Přístupové údaje ve zdroji: {len(z_pristupy)}")
    for p in z_pristupy:
        if p.get("decryption_error"):
            print(
                f"  !! {p['name']}: ve zdroji nejde dešifrovat ({p['decryption_error']}), přeskakuji"
            )
            continue
        if klic_pristupu(p) in existujici_pristupy:
            mapa_pristupu[p["id"]] = existujici_pristupy[klic_pristupu(p)]
            print(f"  OK {p['provider']} / {p['name']}: v cíli už je")
            continue
        novy = {k: p[k] for k in POLE_PRISTUPU if p.get(k) not in (None, "")}
        if p.get("has_api_key"):
            novy["api_key"] = args.api_klic
            print(
                f"  !! {p['name']}: zdroj má API klíč, cíl dostane hodnotu z --api-klic"
            )
        if args.nanecisto:
            print(
                f"  -> {p['provider']} / {p['name']} ({p.get('base_url') or ''}) (nanečisto)"
            )
            mapa_pristupu[p["id"]] = "nanecisto"
            continue
        vytvoreny = cil("POST", "/credentials", novy)
        mapa_pristupu[p["id"]] = vytvoreny["id"]
        pocty["pristupy"] += 1
        print(f"  ++ {p['provider']} / {p['name']} ({p.get('base_url') or ''})")

    mapa_modelu: dict[str, str] = {}
    existujici_modely = {klic_modelu(m): m["id"] for m in c_modely}
    print(f"Modely ve zdroji: {len(z_modely)}")
    for m in z_modely:
        if klic_modelu(m) in existujici_modely:
            mapa_modelu[m["id"]] = existujici_modely[klic_modelu(m)]
            print(f"  OK {m['type']:<15} {m['name']}: v cíli už je")
            continue
        novy = {"name": m["name"], "provider": m["provider"], "type": m["type"]}
        if m.get("credential"):
            if m["credential"] not in mapa_pristupu:
                print(
                    f"  !! {m['name']}: přístup {m['credential']} se nepřenesl, přeskakuji"
                )
                continue
            novy["credential"] = mapa_pristupu[m["credential"]]
        if args.nanecisto:
            print(f"  -> {m['type']:<15} {m['name']} (nanečisto)")
            mapa_modelu[m["id"]] = "nanecisto"
            continue
        vytvoreny = cil("POST", "/models", novy)
        mapa_modelu[m["id"]] = vytvoreny["id"]
        pocty["modely"] += 1
        print(f"  ++ {m['type']:<15} {m['name']}")

    vychozi = {}
    for pole, hodnota in z_vychozi.items():
        if hodnota and hodnota in mapa_modelu:
            vychozi[pole] = mapa_modelu[hodnota]
    print(f"Výchozí modely: {', '.join(sorted(vychozi)) or 'žádné'}")
    nastaveni = {
        k: z_nastaveni[k]
        for k in POLE_NASTAVENI
        if k in z_nastaveni and z_nastaveni[k] is not None
    }

    if args.nanecisto:
        print("Nastavení a výchozí prompt transformací by se zkopírovaly (nanečisto).")
        print("HOTOVO (nanečisto, nic nezměněno)")
        return 0

    try:
        if vychozi:
            cil("PUT", "/models/defaults", vychozi)
        cil("PUT", "/settings", nastaveni)
        cil(
            "PUT",
            "/transformations/default-prompt",
            {
                "transformation_instructions": z_prompt.get(
                    "transformation_instructions", ""
                )
            },
        )
    except urllib.error.HTTPError as e:
        print(
            f"CHYBA při ukládání: API vrátilo {e.code} ({e.reason}) – {e.read().decode('utf-8', 'replace')[:300]}"
        )
        return 1
    print("Nastavení a výchozí prompt transformací zkopírovány.")
    print(
        f"HOTOVO: nových přístupů {pocty['pristupy']}, nových modelů {pocty['modely']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
