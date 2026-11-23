# Jak fungují podcasty – podklady jako zvukový rozhovor

Open Notebook umí ze zdrojů a poznámek vytvořit epizodu podcastu: scénovaný rozhovor (nebo monolog) jednoho až čtyř mluvčích, namluvený převodem textu na řeč. Tato stránka vysvětluje, jak tvorba funguje a co znamenají jednotlivá nastavení. Postup krok za krokem najdete v [Tvorbě podcastů](../3-USER-GUIDE/creating-podcasts.md).

---

## Stavební bloky

**Profil mluvčích**: kdo mluví a jak zní.
- **Hlasový model** (model převodu textu na řeč, vybraný v profilu mluvčích). Pokud chybí, použije se **výchozí model převodu textu na řeč** ze Spravovat → Modely; tvorba selže jen tehdy, když není nastaveno ani jedno.
- Jeden až čtyři **mluvčí**, každý se jménem, **ID hlasu** (název hlasu daného modelu TTS), životním příběhem a osobností.
- Volitelně jiný hlasový model pro každého mluvčího (*Vlastní TTS pro mluvčího*), takže mluvčí mohou pocházet od různých poskytovatelů TTS.

**Profil epizody**: jak se epizoda píše.
- Použitý **profil mluvčích**.
- **Model osnovy** a **model scénáře** (jazykové modely).
- Počet **segmentů** (3 až 20).
- **Výchozí zadání**: volné pokyny ke struktuře, tónu a publiku.
- Volitelný **jazyk** (národní prostředí jako `cs-CZ`, `en-US` nebo `pt-BR`) pro osnovu a scénář.
- Volitelný **max. počet výstupních tokenů** pro každý krok tvorby (výchozí 8192).

**Epizoda**: jeden běh tvorby. Vyberete obsah, profil epizody, název a případně doplňující pokyny.

Open Notebook obsahuje tři profily epizod (`tech_discussion`, `solo_expert`, `business_analysis`) a tři profily mluvčích (`tech_experts`, `solo_expert`, `business_panel`). Na nové instalaci **nemají přiřazené modely**, proto mají štítek *Je potřeba nastavení*, dokud je neupravíte a nevyberete model osnovy, model scénáře a hlasový model. Profily mluvčích fungují i bez hlasového modelu, jakmile je ve Spravovat → Modely nastaven výchozí model převodu textu na řeč (štítek se ale zobrazuje dál). (Instalace aktualizované ze starších verzí už modely mít mohou, pokud byly registrovány odpovídající modely.) Jejich ID hlasů jsou názvy hlasů OpenAI (`nova`, `alloy`, ...); pokud používáte jiného poskytovatele TTS, změňte je.

---

## Jak tvorba probíhá

```
Vybraný obsah (zdroje jako Shrnutí nebo Celý obsah, poznámky)
        │
        ▼
1. OSNOVA       model osnovy + zadání → plán s N segmenty
        │
        ▼
2. SCÉNÁŘ       model scénáře píše dialog segment po segmentu
        │       podle jmen, životních příběhů a osobností mluvčích
        ▼
3. ZVUK         každá replika se namluví hlasovým modelem a ID hlasu mluvčího,
                pak se úseky spojí do jednoho zvukového souboru
```

- **Zadání**: výchozí zadání z profilu epizody, na jehož konec se připojí *Doplňující pokyny* epizody.
- **Jazyk**: je-li v profilu epizody nastaven, osnova i scénář se píší v tomto jazyce. Musí ho podporovat i hlas TTS.
- **Obsah**: u každého zdroje volíte *Shrnutí* (název a [poznatky](notebooks-sources-notes.md#poznatky)) nebo *Celý obsah* (název, poznatky a celý text). Poznámky se zahrnují celé. Zdroj bez poznatků přispěje při *Shrnutí* téměř ničím.
- **Úloha na pozadí**: tvorba běží ve workeru, takže můžete zavřít prohlížeč. Pokud worker neběží, epizody zůstávají ve stavu čekání.

---

<a id="privacy-what-each-model-sees"></a>
## Soukromí: co vidí který model

| Krok | Model | Co dostane |
|------|-------|------------------|
| Osnova | Model osnovy | Veškerý vybraný obsah, zadání, popisy mluvčích |
| Scénář | Model scénáře | Osnovu, vybraný obsah, zadání, popisy mluvčích |
| Zvuk | Hlasové modely | Text scénáře, repliku po replice |

Samotný lokální převod textu na řeč obsah lokálně neudrží: modely osnovy a scénáře vidí celý vybraný obsah. Pro plně lokální podcast použijte lokální jazykové modely **a** lokální server TTS (viz [Local TTS](../../5-CONFIGURATION/local-tts.md), anglicky).

---

## Náklady

Epizoda stojí volání jazykového modelu pro osnovu a scénář (která obsahují veškerý vybraný obsah) plus převod textu na řeč pro celý scénář. Víc obsahu, víc segmentů a delší zadání náklady zvyšují. Ověřte si aktuální ceny svých poskytovatelů; lokální modely nestojí za volání nic.

---

## Když se něco pokazí: chyby a opakování

Když tvorba selže, epizoda se přesune mezi **Neúspěšné epizody** a její karta ukazuje chybovou zprávu. U častých chyb končí zpráva poznámkou **NOTE**, která vysvětluje pravděpodobnou příčinu. Neúspěšné úlohy se automaticky neopakují.

Pro nový pokus klikněte u neúspěšné epizody na **Zkusit znovu**. Neúspěšná epizoda se smaže a odešle se nová úloha se stejným nastavením.

| Chyba | Co dělat |
|-------|-----------|
| `... has no outline model configured` / `no transcript model configured` | Upravte profil epizody a vyberte model. Dodané profily modely nemají. |
| `... has no voice model configured and no default Text-to-Speech model is set` | Vyberte hlasový model v profilu mluvčích, nebo nastavte **výchozí model převodu textu na řeč** ve Spravovat → Modely. |
| `Invalid speaker name` | Model scénáře použil jméno, které v profilu mluvčích není. Opakování obvykle pomůže. |
| `Voice name ... not supported` nebo `Requested entity was not found` (Google) | ID hlasu pro daný hlasový model neexistuje. Použijte název hlasu, který váš model TTS nabízí. |
| `Invalid json output` / `Expecting value` | Výstup modelu byl useknutý nebo prázdný. Snižte **Max. výstupních tokenů** na skutečný limit modelu, použijte méně segmentů, nebo se vyhněte modelům, které celý výstup dávají do bloků uvažování. |
| Neplatný API klíč, model nenalezen, překročen limit požadavků | Zkontrolujte přístupové údaje a modely ve **Spravovat → Modely** a zkuste to znovu. |

Nenastavené profily, které *nepoužíváte*, tvorbu neblokují; přeskočí se.
