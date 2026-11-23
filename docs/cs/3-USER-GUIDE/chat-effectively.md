# Efektivní chat – rozhovory s vašimi podklady

Chat se sešitem je rozhovor s modelem AI o zdrojích a poznámkách, které zařadíte do kontextu. Tato stránka popisuje, jak ho používat. Jak se kontext sestavuje a čím se chat liší od dotazu, vysvětluje [Kontext AI a RAG](../2-CORE-CONCEPTS/ai-context-rag.md).

---

## Rychlý start

1. Otevřete sešit. Sloupec **Chat se sešitem** je vpravo (na telefonu karta **Chat**).
2. Zkontrolujte, co je v kontextu: panel nad polem pro zprávu ukazuje, kolik zdrojů a poznámek je zahrnuto, a odhad počtu tokenů.
3. Napište otázku do pole **Zeptejte se na cokoli ze svých zdrojů...** a stiskněte **Ctrl+Enter** (**⌘+Enter** na Macu). Samotný **Enter** přidá nový řádek.
4. Kliknutím na číslovaný odkaz v odpovědi otevřete citovaný zdroj, poznámku nebo poznatek.

První zpráva automaticky vytvoří relaci chatu.

---

<a id="choosing-what-the-ai-sees"></a>
## Co AI uvidí

Každý zdroj a poznámka v sešitu má úroveň kontextu. Chat posílá vybraný obsah s **každou** zprávou, takže tady řídíte kvalitu, náklady i to, co dostane cloudový poskytovatel.

**U jednotlivých položek:** kliknutím na **ikonu kontextu** na kartě zdroje nebo poznámky přepínáte její úrovně. Po najetí myší uvidíte aktuální úroveň.

| Úroveň | Zdroje | Poznámky |
|-------|---------|-------|
| **Nezahrnuto do chatu** | Neposílá se | Neposílá se |
| **Jen poznatky** | Název a poznatky (nabízí se, jen když zdroj poznatky má) | — |
| **Celý obsah** | Název, poznatky a celý text | Název a obsah |

**Vše najednou:** nabídka **Kontext** v záhlaví každého sloupce.
- Zdroje: **Zahrnout vše (jen poznatky)** (zdroje bez poznatků se vynechají), **Zahrnout vše (celý obsah)**, **Vyřadit vše z kontextu**.
- Poznámky: **Zahrnout vše do kontextu**, **Vyřadit vše z kontextu**.

Co je dobré vědět:

- Po otevření sešitu začínají zdroje s poznatky na *Jen poznatky*, ostatní zdroje na *Celý obsah* a poznámky jsou zahrnuté.
- Vaše volby se **neukládají**. Obnovení stránky je vrátí do výchozího stavu.
- Aby byla u zdroje k dispozici úroveň *Jen poznatky*, vytvořte pro něj poznatek ([Transformace](transformations.md)).

**Jak úrovně volit:**

- *Celý obsah* použijte u několika zdrojů, které pozorně čtete nebo citujete.
- *Jen poznatky* použijte u zdrojů na pozadí. Je mnohem menší a pro orientaci obvykle stačí.
- Vyřaďte vše, co s aktuální otázkou nesouvisí. Méně šumu znamená lepší odpovědi.
- Pokud je kontext velmi velký (přes asi 105 000 tokenů), Open Notebook přepne na váš **model pro velký kontext**.

---

## Relace

Relace je jedna konverzace; její zprávy se ukládají a po návratu znovu načtou. Kliknutím na **Relace** otevřete **Relace chatu**, kde můžete relaci vytvořit (zadat název), přepnout na jinou, přejmenovat ji nebo smazat. Každá relace si pamatuje konverzaci, ne výběr kontextu.

## Volba modelu

Tlačítko modelu vedle pole pro zprávu otevře **Nastavení modelu**. Vyberte model, který se v této relaci použije místo výchozího **modelu chatu**, nebo klikněte na **Obnovit výchozí**. Nabízejí se jen jazykové modely přidané ve **Spravovat → Modely**.

---

## Práce s odpověďmi

Pod každou odpovědí AI:

- **Kopírovat do schránky** zkopíruje text odpovědi.
- **Uložit do poznámky** ji uloží jako poznámku **Vytvořila AI** v tomto sešitu s automaticky vytvořeným názvem. Žádný dialog se neotevře; poznámka se objeví ve sloupci Poznámky.

**Odkazy** jsou číslované odkazy v odpovědi. Míří na celé položky (zdroj, poznámku nebo poznatek), ne na stránky nebo pasáže. Jak je ověřit, popisují [Citace](citations.md).

---

## Jak se dobře ptát

- **Buďte konkrétní.** „Jakou velikost vzorku a metodu použil průzkum z roku 2024?“ dá lepší odpověď než „Řekni mi o průzkumu.“
- **Jmenujte zdroje**, když je jich v kontextu víc: „Porovnej, jak definují produktivitu článek Smithe a zpráva OECD.“
- **Řekněte si o formát:** tabulka, odrážky, krátký odstavec.
- **Řekněte si o odkazy**, když chcete ověřovat: „U každého tvrzení uveď zdroj.“
- **Doptávejte se.** Model vidí celou relaci, takže „Rozveď druhý bod“ funguje.
- **Jazyk odpovědi** se řídí jazykem otázky; když chcete odpověď česky z anglických zdrojů, ptejte se česky, případně to výslovně uveďte.

---

## Chat se zdrojem

Každý zdroj má i vlastní chat. Otevřete zdroj a klikněte na **Chat se zdroji**: stránka zdroje ukazuje obsah vlevo a chat vpravo, s vlastními relacemi a volbou modelu.

Chat se zdrojem vždy používá celý text a poznatky tohoto zdroje; úrovně kontextu tu nejsou. Dlouhé zdroje se zkrátí, aby se vešly do asi 50 000 tokenů, takže na otázky k pozdějším částem velmi dlouhého dokumentu tam odpověď nemusíte dostat; použijte místo toho chat se sešitem se zdrojem na *Celý obsah* (velké kontexty přepnou na model pro velký kontext). **Uložit do poznámky** v chatu se zdrojem není k dispozici (zdroj není vázán na jeden sešit); použijte **Kopírovat do schránky**.

---

## Když se něco pokazí

| Příznak | Co dělat |
|---------|-----------|
| *The model returned an empty response...* | Zkuste to znovu, nebo zvolte jiný model. Modely s uvažováním a malým výstupním limitem mohou vše spotřebovat na přemýšlení. Neúspěšná otázka se v relaci neuchová, takže opakování ji nezdvojí |
| Odpovědi ignorují zdroj | Zkontrolujte jeho ikonu kontextu; může být vyřazený, nebo na *Jen poznatky* s chudými poznatky |
| Pomalé nebo drahé | Zmenšete kontext: vyřaďte zdroje, použijte *Jen poznatky*, nebo začněte novou relaci (posílá se i celá historie relace) |
| *The AI provider took too long to respond...* | Požadavek narazil na časový limit backendu (`ESPERANTO_LLM_TIMEOUT`, ve výchozím stavu 180 sekund). Zkuste to znovu, použijte rychlejší model, zmenšete kontext, nebo limit zvyšte |
| *No model configured...* | Nastavte model chatu ve **Spravovat → Modely → Výchozí přiřazení modelů** |

Více v [Potížích s AI a chatem](../6-TROUBLESHOOTING/ai-chat-issues.md).
