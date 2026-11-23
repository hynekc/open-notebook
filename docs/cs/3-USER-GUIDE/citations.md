# Citace – ověřování odpovědí AI

Odpovědi chatu a dotazů obsahují odkazy na položky, ze kterých vycházejí, takže můžete tvrzení ověřit ve vlastních podkladech.

---

## Na co citace odkazuje

Model má pokyn citovat položky podle ID záznamu, například `source:abc123`, `note:def456` nebo `insight:ghi789`. Citace vždy odkazuje na **celou položku**:

- **zdroj** (jeho celý vytažený text),
- **poznámku**, nebo
- **poznatek** (výstup transformace pro zdroj).

Citace nenesou čísla stránek, oddíly ani zvýrazněné pasáže. Přesné místo najdete tak, že položku otevřete a tvrzení v ní vyhledáte (pomůže hledání na stránce v prohlížeči).

## Kde je uvidíte

- **Chat se sešitem a chat se zdrojem**: čísla v textu, například **[1]**, a seznam **Odkazy** na konci odpovědi. Kliknutím na číslo nebo odkaz otevřete položku v dialogu.
- **Dotaz**: odkazy přímo v textu odpovědi; kliknutím položku otevřete.

Pokud byla citovaná položka po napsání odpovědi smazána, dialog ukáže *Tento obsah už neexistuje*.

Transformace citace nevytvářejí; poznatek je výstup transformace pro jeden známý zdroj.

---

## Ověření tvrzení

1. Klikněte na citaci u tvrzení.
2. Přečtěte otevřenou položku a najděte text, který tvrzení podporuje.
3. Pokud ho nenajdete, doptejte se v chatu se sešitem (nebo v chatu daného zdroje): „Kde přesně to v tom zdroji stojí? Ocituj pasáž.“ Na odpověď dotazu navázat nelze; přeneste otázku do chatu s citovaným zdrojem v kontextu.

Co citace zpřesní:

- **Řekněte si o ně.** Uveďte v otázce „U každého tvrzení uveď zdroj“.
- **Zařaďte do kontextu správný obsah.** V chatu se sešitem lze zdroj na úrovni *Jen poznatky* citovat jen přes jeho název a poznatky. Potřebujete-li tvrzení podložená celým textem, nastavte ho na *Celý obsah*.
- **Dávejte přednost konkrétním otázkám.** Obecná shrnutí citují méně.

Co citovat, volí model, takže citace může chybět nebo mířit na špatnou položku. Berte citace jako vodítko k ověření, ne jako důkaz.

---

## Uchování odpovědí s citacemi

- **Uložit do poznámky** (chat se sešitem) a **Uložit do sešitů** (dotaz) uloží text odpovědi včetně odkazů. Viz [Práce s poznámkami](working-with-notes.md).
- **Kopírovat do schránky** zkopíruje text odpovědi.

Export ani sdílení citací aplikace nenabízí.
