# Chat, dotazy a transformace – který nástroj na jakou práci?

Open Notebook nabízí několik způsobů, jak nechat AI pracovat s vaším obsahem. Liší se tím, jaký obsah používají, zda se můžete doptávat a kam se výsledek uloží.

| | Chat se sešitem | Chat se zdrojem | Dotaz | Transformace |
|---|---|---|---|---|
| **Kde** | Stránka sešitu, sloupec Chat | Stránka zdroje | Dotazy a hledání → Dotaz (beta) | Průvodce přidáním zdroje, nebo karta Poznatky u zdroje |
| **Vstup** | Zdroje a poznámky zařazené do kontextu | Jeden zdroj (text + poznatky) | Vektorové hledání ve vektorizovaném obsahu | Celý text jednoho zdroje |
| **Doplňující otázky** | Ano, v uložených relacích | Ano, v uložených relacích | Ne | Ne |
| **Výstup** | Odpověď chatu s citacemi | Odpověď chatu s citacemi | Odpověď s citacemi | Poznatek připojený ke zdroji |
| **Uložení** | **Uložit do poznámky** | Kopírovat do schránky | **Uložit do sešitů** | Už uloženo jako poznatek |
| **Potřebuje vektory** | Ne | Ne | Ano | Ne |
| **Výchozí model** | Model chatu | Model chatu | Model chatu (tři fáze) | Model transformací, nebo vlastní model transformace |

Jak se jednotlivé nástroje dostanou k obsahu, vysvětluje [Kontext AI a RAG](ai-context-rag.md).

---

## Chat se sešitem – zkoumání s doplňujícími otázkami

Chat použijte, když chcete konverzaci o konkrétním materiálu: porozumět článku, porovnat dvě zprávy, psát návrh ze zdrojů. Co je v kontextu, určujete [úrovněmi kontextu](ai-context-rag.md#context-levels-in-notebook-chat) pro jednotlivé zdroje a poznámky a každá zpráva tento obsah posílá znovu.

Vhodné pro: pozorné čtení, porovnání několika zdrojů, postupné vylepšování odpovědi.
Nevhodné pro: otázky napříč stovkami zdrojů (kontext je příliš velký) nebo hledání, který zdroj něco zmiňuje (použijte hledání nebo dotaz).

→ [Efektivní chat](../3-USER-GUIDE/chat-effectively.md)

## Chat se zdrojem – rozhovor s jedním zdrojem

Každý zdroj má na své stránce vlastní chat. Vždy používá text a poznatky tohoto zdroje, takže není co nastavovat. Dlouhé zdroje se zkrátí, aby se vešly do asi 50 000 tokenů.

## Dotaz – jedna otázka napříč vším

Dotaz použijte, když nevíte, které zdroje obsahují odpověď. Model strategie naplánuje hledání, každé hledání najde odpovídající úseky a konečný model napíše jednu odpověď s citacemi. Prohledává celou znalostní bázi, pokud ho neomezíte na konkrétní sešity, a vidí jen vektorizovaný obsah.

Vhodné pro: otázky napříč mnoha zdroji, „co říkají moje zdroje o X“.
Nevhodné pro: navazující konverzaci nebo obsah, který není vektorizovaný.

→ [Hledání a dotazy](../3-USER-GUIDE/search.md)

## Transformace – stejný prompt uložený jako poznatek

Transformace je uložený prompt (například „Husté shrnutí“ nebo „Obsah“), který se spustí nad jedním zdrojem a výsledek uloží jako **poznatek** u tohoto zdroje. Transformace vybíráte při přidávání zdrojů, nebo je spustíte později na kartě Poznatky u zdroje. Poznatky pak slouží úrovni *Jen poznatky* v chatu a volbě *Shrnutí* u podcastů.

Pro existující zdroje v rozhraní není hromadná akce: chcete-li transformaci použít na mnoho zdrojů, vyberte ji v průvodci přidáním zdroje při jejich přidávání (hromadné nahrání použije stejné transformace na každou položku), nebo ji spusťte u každého zdroje.

Vhodné pro: jednotná shrnutí nebo výtahy napříč zdroji, levnější chat se zdroji.
Nevhodné pro: jednorázové otázky (použijte chat nebo dotaz).

→ [Transformace](../3-USER-GUIDE/transformations.md)

---

## Rozhodovací průvodce

```
Víte, na kterých zdrojích záleží?
├─ Ano → Chcete konverzaci?
│        ├─ Ano → Chat se sešitem (nebo chat se zdrojem pro jeden zdroj)
│        └─ Ne → jednorázová otázka: chat se sešitem;
│               stejný výtah z každého zdroje: transformace
└─ Ne  → Chcete odpověď AI?
         ├─ Ano → Dotaz
         └─ Ne, jen najít pasáže → Hledání (textové nebo vektorové)
```

## Kombinování

Běžný postup:

1. Přidejte zdroje s vybranou transformací pro shrnutí (u nových instalací je předvybrané Dense Summary).
2. **Dotazem** zjistěte, které zdroje se vaší otázkou zabývají.
3. Otevřete sešit a **chatujte** s těmito zdroji: u zdrojů na pozadí použijte *Jen poznatky*, u těch, které čtete pozorně, *Celý obsah*.
4. Odpovědi, které stojí za to, uložte tlačítkem **Uložit do poznámky**.
