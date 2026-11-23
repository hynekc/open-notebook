# Transformace – tvorba poznatků ze zdrojů

**Transformace** je uložený prompt, který se spustí nad jedním zdrojem. Její výstup se uloží jako **poznatek** u tohoto zdroje s názvem transformace. Poznatky se zobrazují na kartě **Poznatky** u zdroje, lze je samostatně posílat do chatu (úroveň kontextu *Jen poznatky*), používá je volba *Shrnutí* u podcastů a dají se vyhledat. Viz [Sešity, zdroje, poznatky a poznámky](../2-CORE-CONCEPTS/notebooks-sources-notes.md#poznatky).

---

## Spuštění transformace

Transformaci lze spustit na dvou místech.

**Při přidání zdroje.** Krok 3 průvodce přidáním zdroje (**Zpracování**) ukazuje vaše transformace v části **Transformace (volitelné)**. Zaškrtněte požadované; spustí se po vytažení textu. Při hromadném nahrání platí výběr pro každou položku. Takto použijete transformaci na mnoho zdrojů najednou.

**U existujícího zdroje.**

1. Otevřete zdroj (kliknutím na jeho kartu) a přejděte na kartu **Poznatky**.
2. V části **Vytvořit nový poznatek** zvolte transformaci v poli **Vyberte transformaci...**.
3. Klikněte na **Nový**. Zobrazí se *Tvorba poznatku byla spuštěna. Za chvíli se objeví.*

Transformace běží na pozadí a poznatek se po dokončení objeví na kartě. Opakované spuštění stejné transformace přidá další poznatek; nechtěné smažte (**Zobrazit poznatek** → **Smazat**, nebo ikona smazání u poznatku).

Akce pro spuštění transformace nad více existujícími zdroji najednou neexistuje.

---

## Vestavěné transformace

Nová instalace obsahuje šest transformací (jejich názvy a prompty jsou anglicky; můžete je upravit nebo si vytvořit české):

| Název | Co vytvoří |
|-------|------------------|
| **Paper Analysis** | Rozbor odborného nebo vědeckého článku |
| **Key Insights** | Důležité poznatky a doporučené kroky |
| **Dense Summary** | Bohaté, husté shrnutí. Předvybrané u nových zdrojů |
| **Reflection Questions** | Otázky pro hlubší zkoumání dokumentu |
| **Table of Contents** | Témata, kterými se dokument zabývá |
| **Simple Summary** | Krátké shrnutí |

Kteroukoli z nich můžete upravit nebo smazat.

---

## Správa transformací

Přejděte do **Spravovat → Transformace**. Karta **Transformace** je uvádí v části **Vlastní transformace**; štítek **Výchozí** označuje ty, které se nabízejí u nových zdrojů.

### Vytvoření nebo úprava

Klikněte na **Vytvořit novou** (nebo **Upravit** na kartě) a vyplňte:

| Pole | Význam |
|-------|---------|
| **Název** (identifikátor) | Jedinečný identifikátor, například `klicova_temata` |
| **Název** (zobrazovaný) | Název zobrazený v rozhraní a daný poznatkům, které transformace vytvoří (výchozí je identifikátor) |
| **Popis** | Co transformace dělá |
| **Systémový prompt** | Pokyny. Za nimi se pošle celý text zdroje |
| **Model** | Použitý model. **Výchozí systému** použije výchozí **model transformací** (nebo model chatu) |
| **Nabízet ve výchozím stavu u nových zdrojů** | Předvybere ji v průvodci přidáním zdroje |

Prompt pište s ohledem na zdroj: požádejte o shrnutí, seznam, tabulku nebo jakýkoli strukturovaný výstup. Výstup se ukládá jako Markdown. Chcete-li poznatky v češtině i z cizojazyčných zdrojů, napište to do promptu („Odpověz česky.“).

### Vyzkoušení ve Zkušebně

Karta **Zkušebna** (nebo **Zkušebna** na kartě transformace) umožní vybrat transformaci a model, vložit **Vstupní text** a kliknout na **Spustit transformaci**. Výstup se zobrazí, ale nikam se neuloží, takže je to bezpečné místo k ladění promptu.

### Výchozí prompt transformací

Pole **Výchozí prompt transformací** nahoře na kartě Transformace se připojí na začátek každého promptu transformace. Hodí se pro společné pokyny, například „Odpovídej česky.“

---

## Chyby

| Zpráva | Příčina |
|---------|-------|
| *Tento zdroj nemá žádný text, který by šlo transformovat* / *Source has no text content* | Vytažení nedalo žádný text (například neúspěšný odkaz). Nejdřív opravte zdroj |
| *The model reached its generation limit before completing the transformation...* | Výstup byl useknut. Použijte kratší prompt nebo model s větším výstupním limitem |
| *The model returned no usable text for the transformation...* | Model nevrátil nic, nebo jen obsah uvažování. Zkuste jiný model |

Když transformaci spustíte z karty Poznatky a selže, chybové hlášení ukáže důvod a žádný poznatek se neuloží. Pokud selže transformace vybraná v průvodci přidáním zdroje, selže s ní i úloha zpracování zdroje a zdroj ukáže **Selhalo** (viz [Když zdroj selže](adding-sources.md#when-a-source-fails)). Potíže s poskytovateli a modely popisuje [Řešení potíží](../6-TROUBLESHOOTING/index.md).

---

## Tipy

- **Pokud chatujete s poznatky, držte shrnutí krátká.** Zdroj na úrovni *Jen poznatky* posílá všechny své poznatky s každou zprávou chatu.
- **Jedna úloha na transformaci.** „Hlavní argumenty“ a „Otevřené otázky“ jako dvě transformace dají čistší poznatky než jeden prompt, který žádá obojí.
- **Velké zdroje** přes asi 105 000 tokenů se posílají **modelu pro velký kontext** bez ohledu na model transformace.
