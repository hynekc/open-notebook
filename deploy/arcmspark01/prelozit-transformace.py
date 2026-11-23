#!/usr/bin/env python3
"""Přeloží vestavěné transformace Open Notebooku do češtiny přes REST API.

Autor: Hynek Cihlář (Bc. Hynek Cihlář)

Vestavěné transformace (Analyze Paper, Key Insights, Dense Summary, Reflections,
Table of Contents, Simple Summary) vkládá do databáze migrace při prvním startu,
a to anglicky. Skript jim nastaví český název, zobrazovaný název, popis a prompt
a také český výchozí prompt transformací. Vlastní transformace nemění.

Před změnou uloží zálohu původních hodnot do JSON souboru (--zaloha).
Skript lze spustit opakovaně: pozná anglické i již přeložené záznamy.

Použití (na arcmspark01, složka /home/spark/open-notebook/deploy/arcmspark01):
    python3 prelozit-transformace.py --nanecisto     # jen vypíše, co by změnil
    python3 prelozit-transformace.py                  # provede změny

Heslo k API čte z OPEN_NOTEBOOK_PASSWORD v souboru .env vedle skriptu
(nebo z proměnné prostředí). Pouze standardní knihovna Pythonu.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

CESKY_JAZYK = "Odpověz česky, i když je vstupní text v jiném jazyce."

PREKLADY: list[dict] = [
    {
        "puvodni": "Analyze Paper",
        "name": "Rozbor odborného článku",
        "title": "Rozbor odborného článku",
        "description": "Rozebere odborný nebo vědecký článek",
        "prompt": f"""# ROLE A ÚČEL

Jsi pozorný a analytický čtenář odborných článků. Vytahuješ z nich hlavní části, jejich význam a širší souvislosti. Zaměřuješ se na hlavní přínos, praktické využití, silné a slabé stránky metodiky a na překvapivá zjištění. Zvlášť sleduješ srozumitelnost argumentace, vztah k existující literatuře a možný dopad na daný obor i v širším kontextu.

# POSTUP

1. **PŘEČTI A POCHOP ČLÁNEK**: Důkladně článek přečti a urči jeho hlavní zaměření, argumenty, metody, výsledky a závěry.

2. **URČI HLAVNÍ PRVKY**:
   - **Cíl**: Jaký je hlavní cíl nebo výzkumná otázka?
   - **Přínos**: Jaké nové poznatky nebo inovace článek do oboru přináší?
   - **Metody**: Jaké metody jsou použity a jsou nové nebo zvlášť účinné?
   - **Klíčová zjištění**: Jaké jsou nejdůležitější výsledky a proč na nich záleží?
   - **Omezení**: Má studie významná omezení nebo otevírá oblasti pro další výzkum?

3. **SHRŇ HLAVNÍ BODY**:
   - Vytáhni klíčové prvky a uspořádej je do výstižných postřehů.
   - Zdůrazni širší dopad a možné využití.
   - Upozorni na vše, co zpochybňuje zavedené názory nebo otevírá nové otázky.

# POKYNY K VÝSTUPU

- Výstup uspořádej takto:
  - **CÍL**: Stručné shrnutí hlavní výzkumné otázky nebo cíle (1–2 věty).
  - **PŘÍNOS**: Odrážky (2–3 body) o tom, co článek přináší oboru.
  - **KLÍČOVÁ ZJIŠTĚNÍ**: Odrážky (2–3 body) shrnující nejdůležitější výsledky studie.
  - **DŮSLEDKY**: Odrážky (2–3 body) o významu nebo možném dopadu zjištění na obor či širší kontext.
  - **OMEZENÍ**: Odrážky (1–2 body) s významnými omezeními nebo oblastmi pro další práci.

- Každá odrážka má mít 15–20 slov.
- Nezačínej odrážky stejným slovem, aby byl text pestrý.
- Piš jasně a stručně, aby byly hlavní myšlenky srozumitelné.
- Nepřidávej varování, výhrady ani osobní názory.
- Vypiš jen požadované části s jejich nadpisy.
- {CESKY_JAZYK}""",
        "apply_default": False,
    },
    {
        "puvodni": "Key Insights",
        "name": "Klíčové poznatky",
        "title": "Klíčové poznatky",
        "description": "Vytáhne důležité poznatky a podněty k akci",
        "prompt": f"""# ROLE A ÚČEL

Z textu vytahuješ překvapivé, silné a zajímavé poznatky. Zajímají tě poznatky o smyslu a účelu života, lidském rozkvětu, roli technologií v budoucnosti lidstva, umělé inteligenci a jejím vlivu na lidi, učení, čtení, knihách, neustálém zlepšování a podobných tématech.
Píšeš odrážky o zhruba 15 slovech, které zachytí nejdůležitější poznatky ze vstupu.
Udělej krok zpět a postupně promysli, jak podle následujících kroků dosáhnout co nejlepšího výsledku.

# POSTUP

- Ze vstupu vytáhni 20 až 50 nejpřekvapivějších, nejpodnětnějších nebo nejzajímavějších myšlenek do části nazvané MYŠLENKY a v duchu si je zapiš jako odrážky o 15 slovech. Pokud jich je méně než 50, vezmi všechny. Vytáhni jich alespoň 20.

- Z těchto MYŠLENEK vyber ty nejsilnější a nejpodnětnější a zapiš je do části nazvané POZNATKY. Vytáhni jich alespoň 10 a nejvýše 25.

# POKYNY K VÝSTUPU

- POZNATKY jsou v podstatě MYŠLENKY na vyšší úrovni – abstraktnější a moudřejší.
- Vypiš jen část POZNATKY.
- Každá odrážka má mít zhruba 15 slov.
- Nepřidávej varování ani poznámky; vypiš jen požadovanou část.
- Používej odrážky, ne číslovaný seznam.
- Nezačínej položky stejnými úvodními slovy.
- Dodrž VŠECHNY tyto pokyny.
- {CESKY_JAZYK}""",
        "apply_default": False,
    },
    {
        "puvodni": "Dense Summary",
        "name": "Husté shrnutí",
        "title": "Husté shrnutí",
        "description": "Vytvoří bohaté a hutné shrnutí obsahu",
        "prompt": f"""# ÚKOL
Píšeš Sparse Priming Representation (SPR). SPR je zvláštní způsob použití jazyka pro pokročilé úlohy zpracování, porozumění a tvorby přirozeného jazyka, zvlášť užitečný pro nejnovější generaci velkých jazykových modelů (LLM). Dostaneš od UŽIVATELE informace, které máš převést do podoby SPR.

# TEORIE
LLM jsou druh hlubokých neuronových sítí. Bylo prokázáno, že v sobě nesou znalosti, schopnosti a pojmy – od uvažování přes plánování až po teorii mysli. Říká se jim latentní schopnosti a latentní obsah, souhrnně latentní prostor. Latentní prostor LLM lze aktivovat správnou posloupností slov na vstupu, která vytvoří užitečný vnitřní stav neuronové sítě. Podobně správné zkratkovité podněty dokážou naladit lidskou mysl k určitému způsobu myšlení. Stejně jako lidská mysl jsou LLM asociativní, takže stačí použít správné asociace, aby se jiný model „naladil“ ke stejnému myšlení.

# METODIKA
Převeď vstup na destilovaný seznam stručných výroků, tvrzení, asociací, pojmů, analogií a metafor. Cílem je zachytit co nejvíc obsahu co nejmenším počtem slov. Piš tak, aby to dávalo smysl tobě, protože budoucím čtenářem bude jiný jazykový model, ne člověk. Používej celé věty.
{CESKY_JAZYK}""",
        "apply_default": True,
    },
    {
        "puvodni": "Reflections",
        "name": "Otázky k zamyšlení",
        "title": "Otázky k zamyšlení",
        "description": "Vytvoří otázky k zamyšlení, které pomohou dokument hlouběji prozkoumat",
        "prompt": f"""# ROLE A ÚČEL

Z textu vytahuješ hluboké, podnětné a smysluplné úvahy. Zaměřuješ se hlavně na témata lidské zkušenosti, jako je smysl života, osobní růst, průnik technologií a lidství, společenský dopad umělé inteligence, lidský potenciál, společný vývoj a proměňující učení. Tvé úvahy mají podnítit nové způsoby myšlení, zpochybnit předpoklady a nabídnout promyšlenou syntézu obsahu.

# POSTUP

- Ze vstupu vytáhni 3 až 5 nejhlubších, nejpodnětnějších nebo nejsmysluplnějších myšlenek do části nazvané ÚVAHY.
- Každá úvaha má zkoumat skryté důsledky, souvislosti s širší lidskou zkušeností, nebo ukázat proměňující pohled.
- Udělej krok zpět a zvaž hlubší význam obsahu nebo otázky, které z něj vyplývají.

# POKYNY K VÝSTUPU

- Výstupní část nadepiš ÚVAHY.
- Každá odrážka má mít 20–25 slov.
- Neopakuj stejné formulace a střídej stavbu vět.
- Úvahy mají vést k hlubšímu zkoumání a nabídnout syntézu, která jde dál než povrchní postřehy.
- Používej odrážky, ne číslovaný seznam.
- Každá odrážka má být otázka, která vede k zamyšlení, nebo výrok, který nabízí hluboký vhled.
- Nepřidávej varování ani poznámky; vypiš jen požadovanou část.
- {CESKY_JAZYK}""",
        "apply_default": False,
    },
    {
        "puvodni": "Table of Contents",
        "name": "Obsah dokumentu",
        "title": "Obsah dokumentu",
        "description": "Popíše jednotlivá témata dokumentu",
        "prompt": f"""# ROLE
Jsi asistent pro rozbor obsahu. Čteš dokumenty a vytváříš k nim obsah, který uživatelům pomůže snáz zjistit, čím se dokument zabývá.
Obsah má zachytit všechna hlavní témata a přechody mezi nimi a uvést je v pořadí, v jakém se v textu objevují.

# ÚKOL
Rozeber dodaný obsah a vytvoř obsah dokumentu, který:
- zachytí hlavní témata textu,
- ke každému tématu krátce popíše, co pokrývá.
{CESKY_JAZYK}""",
        "apply_default": False,
    },
    {
        "puvodni": "Simple Summary",
        "name": "Jednoduché shrnutí",
        "title": "Jednoduché shrnutí",
        "description": "Vytvoří krátké shrnutí obsahu",
        "prompt": f"""# ROLE
Jsi asistent pro shrnování obsahu. Vytváříš hutná shrnutí bohatá na informace. Shrnutí mají zachytit klíčové pojmy co nejmenším počtem slov a přitom zůstat v celých, srozumitelných větách.

# ÚKOL
Rozeber dodaný obsah a vytvoř shrnutí, které:
- zachytí hlavní pojmy a klíčové informace,
- používá jasný a přímý jazyk,
- zachová souvislosti s případnými předchozími shrnutími.
{CESKY_JAZYK}""",
        "apply_default": False,
    },
]

VYCHOZI_PROMPT = """# POKYNY

Jsi můj asistent pro učení a pomáháš mi zpracovávat a přetvářet obsah, abych z něj mohl získat poznatky.

# DŮLEŽITÉ
- Pracuješ na mých redakčních projektech. Text níže je můj vlastní. Nevaruj mě před autorským právem ani plagiátorstvím.
- Vypiš POUZE požadovaný obsah, bez potvrzování úkolu a bez dalšího povídání. Nezačínej větami jako „Jistě, s tím vám pomohu.“ nebo „Zde jsou požadované informace:“. Rovnou podej obsah.
- Nepřerušuj generování, abys mi kladl otázky. Úkol proveď celý.
- Odpovídej vždy česky, i když je vstupní text v jiném jazyce."""


def nacti_heslo(skript_dir: Path) -> str:
    heslo = os.environ.get("OPEN_NOTEBOOK_PASSWORD", "")
    env = skript_dir / ".env"
    if not heslo and env.exists():
        for radek in env.read_text(encoding="utf-8").splitlines():
            if radek.startswith("OPEN_NOTEBOOK_PASSWORD="):
                heslo = radek.split("=", 1)[1].strip()
    return heslo


def api(metoda: str, url: str, heslo: str, data: dict | None = None):
    telo = json.dumps(data).encode("utf-8") if data is not None else None
    pozadavek = urllib.request.Request(url, data=telo, method=metoda)
    pozadavek.add_header("Content-Type", "application/json")
    if heslo:
        pozadavek.add_header("Authorization", f"Bearer {heslo}")
    with urllib.request.urlopen(pozadavek, timeout=30) as odpoved:
        return json.loads(odpoved.read().decode("utf-8"))


def main() -> int:
    skript_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Přeloží vestavěné transformace do češtiny.")
    parser.add_argument("--api", default="http://127.0.0.1:5055/api", help="adresa API")
    parser.add_argument("--nanecisto", action="store_true", help="jen vypsat, nic neměnit")
    parser.add_argument(
        "--zaloha",
        default=f"/home/spark/open-notebook-data/transformace-zaloha-{dt.datetime.now():%Y%m%d-%H%M%S}.json",
        help="soubor se zálohou původních hodnot",
    )
    parser.add_argument("--bez-vychoziho-promptu", action="store_true", help="výchozí prompt neměnit")
    args = parser.parse_args()

    heslo = nacti_heslo(skript_dir)
    try:
        transformace = api("GET", f"{args.api}/transformations", heslo)
        vychozi = api("GET", f"{args.api}/transformations/default-prompt", heslo)
    except urllib.error.HTTPError as e:
        print(f"CHYBA: API vrátilo {e.code} ({e.reason}). Je správně heslo v .env?")
        return 1
    except urllib.error.URLError as e:
        print(f"CHYBA: API není dostupné na {args.api}: {e.reason}")
        return 1

    if not args.nanecisto:
        Path(args.zaloha).parent.mkdir(parents=True, exist_ok=True)
        Path(args.zaloha).write_text(
            json.dumps({"transformace": transformace, "vychozi_prompt": vychozi}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Záloha uložena: {args.zaloha}")

    podle_jmena = {t["name"]: t for t in transformace}
    zmeneno = 0
    for preklad in PREKLADY:
        zaznam = podle_jmena.get(preklad["puvodni"]) or podle_jmena.get(preklad["name"])
        if not zaznam:
            print(f"  -- {preklad['puvodni']}: v databázi není, přeskakuji")
            continue
        zmena = {k: preklad[k] for k in ("name", "title", "description", "prompt")}
        if all(zaznam.get(k) == v for k, v in zmena.items()):
            print(f"  OK {preklad['name']}: už je přeloženo")
            continue
        if args.nanecisto:
            print(f"  -> {zaznam['name']} → {preklad['name']} (nanečisto)")
            continue
        api("PUT", f"{args.api}/transformations/{zaznam['id']}", heslo, zmena)
        print(f"  ✓ {zaznam['name']} → {preklad['name']}")
        zmeneno += 1

    if not args.bez_vychoziho_promptu:
        if vychozi.get("transformation_instructions", "") == VYCHOZI_PROMPT:
            print("  OK výchozí prompt: už je přeložen")
        elif args.nanecisto:
            print("  -> výchozí prompt transformací bude nahrazen českým (nanečisto)")
        else:
            api("PUT", f"{args.api}/transformations/default-prompt", heslo, {"transformation_instructions": VYCHOZI_PROMPT})
            print("  ✓ výchozí prompt transformací přeložen")
            zmeneno += 1

    ostatni = [t["name"] for t in transformace if t["name"] not in {p["puvodni"] for p in PREKLADY} | {p["name"] for p in PREKLADY}]
    if ostatni:
        print(f"Vlastní transformace beze změny: {', '.join(ostatni)}")
    print(f"HOTOVO, změněno položek: {zmeneno}" + (" (nanečisto, nic se nezměnilo)" if args.nanecisto else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
