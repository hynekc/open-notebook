# Tvorba podcastů – podklady jako zvuk

Ze svých zdrojů a poznámek vytvořte zvukovou epizodu. Jak tvorba funguje a co znamenají jednotlivá nastavení, vysvětluje [Jak fungují podcasty](../2-CORE-CONCEPTS/podcasts-explained.md).

Podcasty najdete na stránce **Podcasty** (postranní panel, část **Tvořit**), která má dvě karty: **Epizody** a **Profily**.

---

## Před první epizodou: nastavení profilů

Potřebujete alespoň jeden **profil mluvčích** s hlasovým modelem (nebo **výchozí model převodu textu na řeč** nastavený ve Spravovat → Modely) a jeden **profil epizody** s modelem osnovy a scénáře.

Otevřete **Podcasty → Profily**. Nová instalace už má tři profily mluvčích a tři profily epizod, ale **žádný nemá přiřazené modely**; mají štítek **Je potřeba nastavení** (aktualizované instalace už modely mít mohou). Buď je upravte, nebo si vytvořte vlastní. Nejdřív vytvořte mluvčí: profily epizod na profil mluvčích odkazují.

Ve **Spravovat → Modely** (**Synchronizovat modely** → **Vyhledat modely** u konfigurace poskytovatele) budete potřebovat tyto modely, které pak vyberete v polích profilů níže:
- model **převodu textu na řeč** (pro hlasy). Kteří poskytovatelé TTS nabízejí, uvádí [Poskytovatelé AI](../4-AI-PROVIDERS/index.md); lokální možnost popisuje [Local TTS](../../5-CONFIGURATION/local-tts.md) (anglicky).
- **jazykový** model pro osnovu a scénář.

### Profil mluvčích

Klikněte na **Vytvořit mluvčí** (nebo **Upravit** u existujícího) a vyplňte:

| Pole | Poznámky |
|-------|-------|
| **Název profilu**, **Popis** | Pro vás |
| **Hlasový model** | V tomto formuláři povinný. Model TTS, který ve výchozím stavu používají všichni mluvčí |
| **Mluvčí** | Jeden až čtyři. Další přidáte tlačítkem **Přidat mluvčího** |
| → **Jméno** | Jméno použité ve scénáři |
| → **ID hlasu** | Název hlasu hlasového modelu, zadaný přesně (například `nova` u OpenAI). Ověřte si seznam hlasů svého poskytovatele TTS |
| → **Životní příběh**, **Osobnost** | Kdo je a jak mluví; model scénáře používá obojí |
| → **Vlastní TTS pro mluvčího (volitelné)** | Jiný hlasový model pro tohoto mluvčího, nebo **Podle profilu** |

Dodané profily používají názvy hlasů OpenAI (`nova`, `alloy`, ...). Pokud je váš hlasový model od jiného poskytovatele, změňte ID hlasů, jinak tvorba selže s chybou hlasu.

Dodané profily mluvčích nemají hlasový model. Pokud je ve Spravovat → Modely nastaven **výchozí model převodu textu na řeč**, používají ho, dokud zde nevyberete jiný.

### Profil epizody

Klikněte na **Vytvořit profil** (nebo **Upravit**) a vyplňte:

| Pole | Poznámky |
|-------|-------|
| **Název profilu**, **Popis** | Pro vás |
| **Profil mluvčích** | Které mluvčí použít |
| **Model osnovy**, **Model scénáře** | Jazykové modely; mohou být stejné |
| **Segmenty** | 3 až 20. Více segmentů znamená delší epizodu |
| **Výchozí zadání** | Povinné. Struktura, tón, publikum a cíle tohoto formátu vlastními slovy. Sem patří „ať je to neformální“, „pro začátečníky“ nebo „na konci otevřené otázky“ |
| **Jazyk** | Volitelné. Jazyk osnovy a scénáře (například čeština). Vyberte hlasy, které tímto jazykem umí mluvit |
| **Max. výstupních tokenů** | Volitelný limit pro každý krok tvorby (osnova, scénář). Prázdné = 8192. Nižší hodnotu nastavte, jen když je výstupní limit vašeho modelu pod 8192 |

Profily lze také **Duplikovat** a **Smazat**. Profil mluvčích, který používá některý profil epizody, nelze smazat, dokud tento profil epizody nezměníte.

---

## Vytvoření epizody

1. Na kartě **Epizody** klikněte na **Vytvořit podcast** (nebo v postranním panelu **Nový → Podcast**, případně **Nový podcast** v Rychlých akcích).
2. V dialogu **Vytvořit epizodu podcastu** v části **Obsah** vyberte, co zahrnout. Rozbalte sešit a vyberte ho celý, nebo jednotlivé zdroje a poznámky. U každého zdroje zvolte:
   - **Shrnutí**: název a poznatky zdroje (malé; zdroj bez poznatků nepřidá téměř nic).
   - **Celý obsah**: název, poznatky a celý text.

   Dialog ukazuje počet vybraných položek a odhad počtu tokenů a znaků. Obsah můžete kombinovat z více sešitů.
3. V části **Nastavení epizody**:
   - **Profil epizody**: povinné.
   - **Název epizody**: povinné.
   - **Doplňující pokyny**: volitelné; připojí se k zadání profilu jen pro tuto epizodu (například „zaměř se na kapitolu o metodice“).
4. Klikněte na **Vytvořit**. Zobrazí se *Tvorba podcastu spuštěna*.

Tvorba běží ve workeru na pozadí, takže stránku můžete zavřít. Trvá několik minut podle množství obsahu, počtu segmentů a vašich poskytovatelů. Pokud epizody zůstávají ve stavu čekání, worker neběží.

---

## Epizody

Karta **Epizody** třídí epizody do skupin **Právě se zpracovává**, **Ve frontě / čeká**, **Hotové epizody** a **Neúspěšné epizody**, se součty nahoře.

Každá karta epizody obsahuje:
- **přehrávač zvuku** (u hotových epizod),
- **Podrobnosti** se **Shrnutím** epizody (použité profily a modely), **Osnovou** a **Scénářem**,
- **Smazat** (odstraní epizodu i její zvukový soubor),
- **Zkusit znovu** (u neúspěšných epizod): smaže neúspěšnou epizodu a odešle novou úlohu se stejným názvem, obsahem, profilem epizody a profilem mluvčích, s aktuálním nastavením profilů (takže můžete opravit profil a pak to zkusit znovu). **Doplňující pokyny** epizody se nezachovají.

Neúspěšné epizody ukazují chybu. Časté chyby a jejich řešení uvádí [Jak fungují podcasty → Když se něco pokazí](../2-CORE-CONCEPTS/podcasts-explained.md#když-se-něco-pokazí-chyby-a-opakování).

---

## Tipy pro lepší epizody

- **Vyberte méně obsahu.** Modely osnovy a scénáře čtou vše, co vyberete, pokaždé. *Shrnutí* u zdrojů na pozadí a *Celý obsah* u hlavních drží náklady dole a pozornost nahoře.
- **Směr dejte do zadání.** Tón, publikum, struktura i důrazy pocházejí z výchozího zadání a doplňujících pokynů; čím konkrétnější, tím lepší.
- **Dejte mluvčím odlišné osobnosti a hlasy.** Dva mluvčí se stejným hlasem a podobnou osobností se špatně sledují.
- **Při podivném selhání to jednou zkuste znovu.** Některé chyby (například *Invalid speaker name*) způsobí jediná špatná odpověď modelu a napodruhé projdou.
- **Náklady** tvoří volání jazykového modelu pro osnovu a scénář (která obsahují veškerý vybraný obsah) plus převod textu na řeč pro celý scénář. Ověřte si ceny svých poskytovatelů.
