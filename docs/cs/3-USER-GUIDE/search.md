# Hledání a dotazy – jak najít, co potřebujete

Hledání i dotazy jsou na stránce **Dotazy a hledání** (postranní panel, část **Zpracovat**). Oba pracují napříč celou znalostní bází, nebo jen ve vybraných sešitech. Uvnitř sešitu samostatné vyhledávací pole není.

Obojí můžete spustit i z **Rychlých akcí** (**Ctrl+K** / **⌘K**): napište dotaz a zvolte *Výsledky hledání pro „...“* nebo *Zeptat se na „...“*.

| | Hledání | Dotaz (beta) |
|---|---|---|
| **Co dostanete** | Seznam odpovídajících zdrojů, poznatků a poznámek | Jednu napsanou odpověď s citacemi |
| **Používá model AI** | Vektorové hledání používá embedding model; textové žádný | Embedding model a jazykový model pro každou fázi |
| **Nejvhodnější pro** | Nalezení pasáže, pojmu nebo dokumentu | Otázky, jejichž odpověď je rozptýlená v různých zdrojích |

Jak obojí funguje uvnitř, vysvětluje [Kontext AI a RAG](../2-CORE-CONCEPTS/ai-context-rag.md#hledání-textové-a-vektorové).

---

<a id="search"></a>
## Hledání

1. Otevřete **Dotazy a hledání** a zvolte kartu **Hledání**.
2. Napište hledaný výraz a stiskněte **Enter**.
3. Případně upravte:
   - **Typ hledání**: **Textové hledání** nebo **Vektorové hledání**.
   - **Hledat v**: **Hledat ve zdrojích** a/nebo **Hledat v poznámkách**.
   - **Sešity**: vyberte sešity pro omezení hledání, nebo vše nechte nezaškrtnuté a hledejte všude.

Výsledky ukazují, kolik se jich našlo; kliknutím na výsledek otevřete zdroj, poznámku nebo poznatek. Kde je to možné, uvádí výsledek i své **Shody** (odpovídající pasáže).

### Textové a vektorové hledání

| | Textové hledání | Vektorové hledání |
|---|---|---|
| **Shoda** | Přesná slova (s anglickým převodem na základní tvar) | Význam, podle podobnosti |
| **Pokrývá** | Názvy a obsah zdrojů, poznatky, názvy a obsah poznámek | Obsah zdrojů, poznatky, obsah poznámek (ne názvy) |
| **Potřebuje** | Nic | Embedding model; najde jen vektorizovaný obsah |
| **Kdy použít** | Znáte pojem, jméno nebo frázi | Znáte myšlenku, ale ne přesné znění |

Pokud není nastaven embedding model, stránka ukáže *Vektorové hledání potřebuje embedding model. K dispozici je jen textové hledání.*

**Tipy:**
- Textové hledání funguje nejlépe s výraznými slovy: jmény, zkratkami, odbornými termíny. Převod na základní tvar funguje jen pro angličtinu, proto u českých textů zkoušejte různé tvary slova (např. „smlouva“ i „smlouvy“).
- Vektorové hledání funguje nejlépe s popisnou frází („rizika závislosti na jediném dodavateli“) místo jednoho slova.
- Zdroj, který najde textové hledání, ale ne vektorové, nejspíš není vektorizovaný. Otevřete ho a použijte **Vektorizovat obsah**.

---

<a id="ask"></a>
## Dotaz

1. Otevřete **Dotazy a hledání** a zůstaňte na kartě **Dotaz (beta)**.
2. Napište otázku.
3. Případně ji omezte na některé **Sešity** (nechte vše nezaškrtnuté pro celou znalostní bázi).
4. Stiskněte **Cmd/Ctrl+Enter** nebo klikněte na **Zeptat se**.

Během běhu uvidíte fáze, jak postupně končí:

- **Strategie**: uvažování modelu a **Hledané výrazy**, které zvolil (až pět hledání).
- **Dílčí odpovědi**: jedna dílčí odpověď na každé hledání, vycházející z nejlepších shod.
- **Konečná odpověď**: spojená odpověď s odkazy na citované položky.

Kliknutím na **Uložit do sešitů** si odpověď uchováte jako poznámku (s vaší otázkou jako názvem) v jednom nebo více sešitech.

### Požadavky

- Musí být nastaven **embedding model**. Bez něj karta dotazu hlásí *Tuto funkci nelze použít, protože není vybrán embedding model.*
- Musí být nastaven **model chatu**. Všechny tři fáze ve výchozím stavu používají **model nástrojů**, nebo model chatu, není-li model nástrojů nastaven.
- Dotaz vidí jen **vektorizovaný** obsah (zdroje přidané se zapnutou vektorizací, poznámky a poznatky).

### Volba modelů

Karta ukazuje **Používají se výchozí modely** nebo **Používají se vlastní modely**. Kliknutím na **Pokročilé** otevřete **Pokročilý výběr modelů**, zvolte **Model strategie**, **Model odpovědí** a **Model konečné odpovědi** a klikněte na **Uložit změny**. Krok strategie potřebuje model, který spolehlivě vrací strukturovaný výstup; pokud selže s hláškou *The strategy model returned no search terms for this question...*, zvolte jiný model strategie nebo otázku přeformulujte.

### Kdy použít dotaz

- Dotaz použijte, když nevíte, které zdroje odpověď obsahují.
- Dotaz je jednorázový. Chcete-li navázat, otevřete sešit a použijte [chat](chat-effectively.md) se zdroji, které dotaz citoval.
- Odpovědi vycházejí jen z nalezených úseků, takže mohou minout souvislosti roztroušené po celém dokumentu. Pro pozorné čtení použijte chat s *Celým obsahem*.

---

## Řešení potíží

| Problém | Zkuste |
|---------|-----|
| Vektorové hledání nebo dotaz nic nenajde | Ověřte, že je nastaven embedding model a zdroje jsou vektorizované; pokud jste měnili embedding model, přestavte vektory v **Pokročilé → Znovu vytvořit vektory** |
| Textové hledání nenajde slovo | Zkuste jiný tvar slova nebo synonymum; převod na základní tvar funguje jen v angličtině |
| Příliš mnoho výsledků | Omezte hledání na konkrétní sešity, nebo vypněte **Hledat ve zdrojích** či **Hledat v poznámkách** |
| Odpověď dotazu je prázdná nebo selže | Zvolte jiné modely v části **Pokročilé**; modely s uvažováním a malým výstupním limitem mohou nevrátit nic |
