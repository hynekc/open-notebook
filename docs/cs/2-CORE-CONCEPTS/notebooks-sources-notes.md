# Sešity, zdroje, poznatky a poznámky

Open Notebook pracuje se čtyřmi druhy obsahu. Když víte, jak spolu souvisejí, rozumíte většině aplikace.

```
SEŠIT  „Bezpečnost AI“  (název + popis)
 │
 ├── ZDROJE  (propojené; jeden zdroj může být ve více sešitech)
 │    ├── clanek_o_bezpecnosti.pdf
 │    │     └── POZNATKY  „Husté shrnutí“, „Klíčové poznatky“   ← vytvořené transformacemi
 │    └── prednaska.mp4
 │          └── POZNATKY  „Jednoduché shrnutí“
 │
 └── POZNÁMKY  (patří tomuto sešitu)
      ├── Moje poznámky z četby       (Člověk)
      └── Odpověď uložená z chatu     (Vytvořila AI)
```

---

## Sešity

**Sešit** je pracovní prostor pro jeden projekt nebo téma. Má název, volitelný popis, propojené zdroje, poznámky a relace chatu.

- **Název a popis se v chatu se sešitem posílají AI** jako informace o projektu, takže dobrý popis zlepšuje odpovědi chatu. Dotazy, hledání a transformace je nepoužívají.
- Sešity lze **archivovat** (skryjí se ze seznamu aktivních, nic se nemaže) a z archivu obnovit.
- **Smazání** sešitu trvale smaže jeho poznámky. Zdroje propojené jen s tímto sešitem můžete smazat také, nebo ponechat v knihovně; zdroje sdílené s jinými sešity se jen odpojí. Dialog mazání ukáže počty, než akci potvrdíte.

---

## Zdroje

**Zdroj** je jeden kus vstupního materiálu: nahraný soubor, webový odkaz nebo vložený text. Podporované typy popisuje [Přidávání zdrojů](../3-USER-GUIDE/adding-sources.md).

Po přidání zdroje úloha na pozadí:

1. **Vytáhne text** (rozbor dokumentu, stažení webové stránky nebo převod řeči na text u zvuku a videa; viz [Nástroje pro zpracování obsahu](../3-USER-GUIDE/content-processing-engines.md)).
2. **Vektorizuje ho**, pokud je pro zdroj vektorizace zapnutá: text se rozdělí na úseky (ve výchozím stavu asi po 400 tokenech) a každý úsek dostane vektor pro sémantické hledání.
3. **Spustí vybrané transformace**, které vytvoří poznatky.

Co je dobré vědět:

- **Zdroje jsou ve sdílené knihovně.** Stránka **Zdroje** ukazuje všechny zdroje. Zdroj může být propojen s libovolným počtem sešitů (v sešitu použijte **Přidat existující zdroje**), nebo s žádným. Odebrání zdroje ze sešitu ho jen odpojí; smazání zdroje ho odstraní všude.
- **Vytažený text se v aplikaci neupravuje.** Změněnou webovou stránku načtete znovu volbou **Obnovit obsah** u zdroje; chybně nahraný soubor přidejte znovu.
- **Rozsah hledání závisí na vektorizaci.** Textové (klíčová slova) hledání funguje u všech zdrojů. Vektorové hledání a dotazy prohledávají vektorizovaný text zdrojů a poznatky; poznatky se vektorizují samostatně, takže zdroj bez vektorizovaného textu lze stále najít přes jeho poznatky.

---

## Poznatky

**Poznatek** je výstup [transformace](../3-USER-GUIDE/transformations.md) spuštěné nad zdrojem, například shrnutí, seznam hlavních bodů nebo obsah. Poznatky lidé nejčastěji přehlédnou, přitom na nich závisí několik funkcí:

- **Jsou připojené ke zdroji**, ne k sešitu. Najdete je na kartě **Poznatky** u zdroje, označené názvem transformace.
- **Tvoří úroveň kontextu „Jen poznatky“.** V chatu se sešitem posílá zdroj nastavený na *Jen poznatky* svůj název a poznatky místo celého textu. Zdroj bez poznatků může mít jen *Celý obsah* nebo *Nezahrnuto do chatu*. Viz [Kontext AI a RAG](ai-context-rag.md#context-levels-in-notebook-chat).
- **Tvoří volbu „Shrnutí“ u podcastů.** Když vybíráte obsah epizody, *Shrnutí* pošle poznatky zdroje.
- **Dají se vyhledat.** Textové hledání, vektorové hledání i dotazy poznatky zahrnují.
- **Dají se citovat.** Odpovědi chatu mohou odkazovat na poznatek a kliknutím na odkaz ho otevřete.
- **Mohou se z nich stát poznámky.** Otevřete poznatek a kliknutím na **Uložit jako poznámku** ho zkopírujete do sešitu jako poznámku vytvořenou AI. Viz [Práce s poznámkami](../3-USER-GUIDE/working-with-notes.md#turn-an-insight-into-a-note).

Poznatky vytvoříte při přidání zdroje (krok 3 průvodce přidáním zdroje), nebo později na kartě Poznatky u zdroje tlačítkem **Vytvořit nový poznatek**.

---

## Poznámky

**Poznámka** je text, který patří sešitu. Má název a obsah v Markdownu a je označena buď jako **Člověk** (napsali jste ji vy), nebo **Vytvořila AI** (uložená z AI).

Jak ji vytvořit:

- **Napsat poznámku** ve sloupci Poznámky v sešitu.
- **Uložit do poznámky** pod odpovědí chatu se sešitem (jedno kliknutí, název se vytvoří sám).
- **Uložit do sešitů** po odpovědi na dotaz (otázka se stane názvem a můžete vybrat více sešitů).

Poznámky jsou v kontextu chatu se sešitem buď zapnuté, nebo vypnuté (nemají úroveň poznatků), dají se vyhledat a při nastaveném embedding modelu se vektorizují pro vektorové hledání. Viz [Práce s poznámkami](../3-USER-GUIDE/working-with-notes.md).

---

## Jak spolu souvisejí

```
Přidání zdroje ──► vytažení textu ──► vektorizace (volitelně) ──► transformace ──► poznatky
                                           │                                        │
                                           ▼                                        ▼
                              vektorové hledání + dotazy            kontext „Jen poznatky“ v chatu
                                                                    obsah „Shrnutí“ v podcastech

Odpověď chatu / dotazu ──► Uložit do poznámky / Uložit do sešitů ──► poznámka (Vytvořila AI)
Napsat poznámku ─────────────────────────────────────────────────► poznámka (Člověk)
```

## Shrnutí

| Pojem | Co to je | Patří k |
|---------|------------|------------|
| **Sešit** | Pracovní prostor projektu s názvem a popisem | — |
| **Zdroj** | Vstupní materiál (soubor, odkaz, text) | Knihovně; propojený s žádným nebo více sešity |
| **Poznatek** | Výstup transformace pro jeden zdroj | Jednomu zdroji |
| **Poznámka** | Text, který jste napsali nebo uložili z AI | Jednomu sešitu |
