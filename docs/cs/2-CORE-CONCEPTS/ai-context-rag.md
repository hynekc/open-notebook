# Kontext AI a RAG – jak Open Notebook pracuje s vašimi podklady

Model AI ví jen to, co dostane v promptu. Open Notebook má dva způsoby, jak do promptu dostat vaše podklady:

- **Chat** pošle obsah, který jste vybrali, tak jak je. Nic se nevyhledává.
- **Dotaz (Ask)** prohledá znalostní bázi a pošle jen odpovídající části. Jde o generování s podporou vyhledávání (RAG, retrieval-augmented generation).

Tato stránka vysvětluje oba způsoby, úrovně kontextu, které řídí chat, a hledání, na kterém stojí dotazy.

---

<a id="context-levels-in-notebook-chat"></a>
## Úrovně kontextu v chatu se sešitem

V sešitu má každý zdroj a poznámka úroveň kontextu, která určuje, co chat se sešitem pošle modelu.

| Úroveň | Platí pro | Co se posílá |
|-------|-----------|--------------|
| **Nezahrnuto do chatu** | Zdroje a poznámky | Nic |
| **Jen poznatky** | Zdroje, které mají poznatky | Název zdroje a jeho [poznatky](notebooks-sources-notes.md#poznatky) |
| **Celý obsah** | Zdroje a poznámky | Zdroje: název, poznatky a celý vytažený text. Poznámky: název a obsah |

Jak se to chová:

- **Jen poznatky vyžaduje poznatky.** Tato úroveň se nabízí jen u zdrojů, které už mají alespoň jeden poznatek. Zpřístupníte ji spuštěním transformace nad zdrojem.
- **Výchozí stav po otevření sešitu:** zdroje s poznatky začínají na *Jen poznatky*, zdroje bez poznatků na *Celý obsah* a všechny poznámky jsou zahrnuté.
- **Výběr se neukládá.** Platí jen na stránce a po jejím obnovení se vrátí do výchozího stavu.
- **Chat ukazuje součet.** Nad polem pro zprávu ukazuje panel chatu, kolik zdrojů a poznámek je v kontextu, a odhad počtu tokenů a znaků.

Jak úrovně měnit, popisuje [Efektivní chat](../3-USER-GUIDE/chat-effectively.md#choosing-what-the-ai-sees).

**Proč na tom záleží:**

- **Cena a rychlost.** Vše v kontextu se posílá s každou zprávou. *Jen poznatky* bývá jen zlomek velikosti celého textu.
- **Zaměření.** Když vynecháte nesouvisející zdroje, má model méně věcí, které ho mohou zmást.
- **Co dostane cloudový poskytovatel.** Zdroj nastavený na *Nezahrnuto do chatu* chat nepošle.

> **Úrovně kontextu platí jen pro chat se sešitem.** Dotazy, hledání a tvorba podcastů mají vlastní výběr (popsaný níže). Zdroj vyřazený z chatu se k modelu přesto může dostat přes dotaz, pokud je vektorizovaný a dotaz není omezen na jiné sešity.

---

## Chat: celý obsah, bez vyhledávání

Když v chatu se sešitem odešlete zprávu, Open Notebook sestaví jeden prompt z:

1. názvu a popisu sešitu,
2. všech zdrojů a poznámek v kontextu, v jejich úrovni kontextu,
3. dosavadní konverzace a vaší nové zprávy.

Žádný krok hledání tu není: model pokaždé vidí veškerý vybraný obsah. Proto se chat hodí k pozornému čtení a porovnání několika zdrojů a proto je velký výběr drahý.

Použije se výchozí **model chatu**, nebo model, který jste vybrali pro danou relaci. Pokud je prompt delší než asi 105 000 tokenů, Open Notebook místo něj přepne na výchozí **model pro velký kontext** (nebo na model chatu, není-li nastaven), i když jste pro relaci vybrali jiný model.

### Chat se zdrojem

Otevřete-li zdroj a použijete jeho chat (**Chat se zdroji** v zobrazení zdroje), jde o samostatný chat o tomto jediném zdroji. Posílá celý text zdroje a jeho poznatky, zkrácené tak, aby se vešly do rozpočtu asi 50 000 tokenů. Delší zdroje se oříznou a model dostane upozornění, že text byl zkrácen.

---

## Dotaz: vyhledávání ve znalostní bázi

Dotaz (na stránce **Dotazy a hledání**) odpoví na jednu otázku ve třech fázích:

```
Vaše otázka
    │
    ▼
1. STRATEGIE        model naplánuje až 5 hledání
    │
    ▼
2. ODPOVĚDI         každé hledání spustí vektorové hledání (10 nejlepších shod)
    │               a model z nich napíše dílčí odpověď
    ▼
3. KONEČNÁ ODPOVĚĎ  model spojí dílčí odpovědi a doplní citace
```

Co je dobré vědět:

- **Dotaz potřebuje embedding model.** Bez výchozího embedding modelu vás stránka vyzve k jeho nastavení a dotazy nejsou k dispozici.
- **Dotaz vidí jen vektorizovaný obsah.** Prohledává vektorizované úseky zdrojů, poznatky a poznámky. Poznatky se vektorizují samostatně, takže zdroj přidaný s vypnutou vektorizací lze najít přes jeho poznatky, ale ne přes celý text, dokud ho nevektorizujete.
- **Dotaz ve výchozím stavu prohledává vše.** Výběr **Sešity** nechte prázdný a prohledá se celá znalostní báze, nebo vyberte sešity a hledání omezte. Úrovně kontextu chatu se neuplatňují.
- **Tři pozice pro modely.** Strategie, Odpověď a Konečná odpověď používají výchozí model nástrojů (nebo model chatu, není-li model nástrojů nastaven), pokud je nezměníte v části **Pokročilé** na kartě dotazu.
- **Dotaz je jednorázový.** Doplňující otázky nejsou. Užitečnou odpověď uložte tlačítkem **Uložit do sešitů**, nebo téma přeneste do chatu.

---

## Hledání: textové a vektorové

Karta **Hledání** vám umožní najít obsah sami, bez odpovědi AI. Oba režimy pokrývají zdroje, poznatky a poznámky; zdroje nebo poznámky můžete vypnout a hledání omezit na konkrétní sešity.

### Textové hledání (klíčová slova)

- Fulltextové hledání s řazením BM25.
- Prohledává názvy a obsah zdrojů, poznatky a názvy a obsah poznámek.
- Funguje u každého zdroje, vektorizovaného i nevektorizovaného, a nepotřebuje žádný model AI.
- Slova se převádějí na základní tvar anglickým stemmerem (takže „running“ najde i „run“). V jiných jazycích, včetně češtiny, je shoda méně tolerantní – hledejte přesné tvary slov, nebo použijte vektorové hledání.

Použijte ho pro přesné názvy, pojmy a fráze, které si pamatujete.

### Vektorové hledání (podle významu)

- Dotaz se embedding modelem převede na vektor a porovná s uloženými vektory úseků.
- Hledá v obsahu zdrojů, poznatcích a obsahu poznámek podle podobnosti. Názvy se neprohledávají.
- Potřebuje embedding model a najde jen vektorizovaný obsah. Poznatky se vektorizují odděleně od textu zdroje, takže zdroj bez vektorizovaného textu lze najít přes jeho poznatky.

Použijte ho, když znáte myšlenku, ale ne přesné znění.

### Jak funguje vektorizace

Při vektorizaci se text zdroje rozdělí na úseky o asi 400 tokenech s 15% překryvem (nastavitelné proměnnými `OPEN_NOTEBOOK_CHUNK_SIZE` a `OPEN_NOTEBOOK_CHUNK_OVERLAP`) a každý úsek se uloží se svým vektorem. Zda se nové zdroje vektorizují, určuje **Nastavení → Vektorizace a hledání → Výchozí vektorizace** (Zeptat se, Vždy, Nikdy) a zaškrtávací pole v průvodci přidáním zdroje. Pokud změníte embedding model, vektory znovu vytvořte v **Pokročilé → Znovu vytvořit vektory**; vektory z různých modelů nelze porovnávat.

---

## Citace

Odpovědi chatu a dotazů citují použité položky podle ID záznamu, například `[source:abc123]`, `[note:def456]` nebo `[insight:ghi789]`. Aplikace je zobrazuje jako klikací odkazy, které otevřou citovaný zdroj, poznámku nebo poznatek. Citace odkazují na celou položku, ne na stránku nebo pasáž. Viz [Citace](../3-USER-GUIDE/citations.md).

---

## Soukromí: co opouští váš stroj

Obsah se posílá poskytovateli, u kterého běží model pro danou funkci. Pokud jsou všechny vaše modely lokální (například Ollama nebo vLLM na vlastním serveru), žádný obsah promptů se k cloudovému poskytovateli AI nedostane. Jiné odchozí požadavky ale probíhají dál: přidání zdroje z URL stáhne daný web a nástroje pro URL Firecrawl a Jina (pokud jsou nastavené) pošlou URL svým službám, které stránku stáhnou a vrátí její obsah. S cloudovým poskytovatelem AI:

| Funkce | Co poskytovatel dostane |
|---------|----------------------------|
| Chat se sešitem | Název a popis sešitu, zdroje a poznámky v kontextu, konverzaci |
| Chat se zdrojem | Text daného zdroje (v rámci rozpočtu) a jeho poznatky, konverzaci |
| Dotaz | Vaši otázku, pak odpovídající úseky, poznatky a poznámky z každého hledání |
| Vektorizace | Text každého vektorizovaného úseku, poznámky a poznatku |
| Transformace | Celý text transformovaného zdroje |
| Podcasty | Viz [Jak fungují podcasty](podcasts-explained.md#privacy-what-each-model-sees) |

Poskytovatele můžete kombinovat, například lokální embedding model s cloudovým modelem chatu.

---

## Shrnutí

| | Chat | Dotaz |
|---|---|---|
| **Jak se vybírá obsah** | Úrovně kontextu nastavujete u každého zdroje a poznámky | Vektorové hledání vybere odpovídající úseky |
| **Rozsah** | Aktuální sešit | Celá znalostní báze, nebo vybrané sešity |
| **Potřebuje vektory** | Ne | Ano |
| **Konverzace** | Více kol, ukládá se do relací | Jedna otázka, jedna odpověď |
| **Nejvhodnější pro** | Pozorné čtení a porovnání vybraných zdrojů | Otázky napříč velkým množstvím materiálu |
