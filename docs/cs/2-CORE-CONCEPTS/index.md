# Základní pojmy – jak aplikace funguje

Tyto stránky vysvětlují, jak je Open Notebook uspořádaný a podle čeho jeho funkce AI rozhodují, jaký obsah použijí. Stačí je jednou přečíst a zbytek aplikace bude dávat smysl. Postupy krok za krokem najdete v [Uživatelské příručce](../3-USER-GUIDE/index.md).

## Stránky

### 1. [Sešity, zdroje, poznatky a poznámky](notebooks-sources-notes.md)
Čtyři věci, se kterými pracujete.

**Hlavní myšlenka**: Sešit sdružuje zdroje a poznámky k jednomu projektu. Zdroje jsou vstupní materiál a mohou patřit do více sešitů. Transformace ze zdroje vytvářejí **poznatky**, které zůstávají připojené ke zdroji. Poznámky jsou to, co napíšete vy nebo co uložíte z odpovědí AI.

---

### 2. [Kontext AI a RAG](ai-context-rag.md)
Jak se jednotlivé funkce AI dostanou k vašemu obsahu a jak to řídíte.

**Hlavní myšlenka**: **Chat** posílá zdroje a poznámky, které zařadíte do kontextu, bez jakéhokoli hledání. **Dotaz (Ask)** prohledá znalostní bázi (vektorovým hledáním) a odpoví z toho, co najde. Každý zdroj v sešitu má pro chat tři úrovně kontextu: *Nezahrnuto do chatu*, *Jen poznatky* a *Celý obsah*.

---

### 3. [Chat, dotazy a transformace](chat-vs-transformations.md)
Který nástroj použít na jakou práci.

**Hlavní myšlenka**: Chat je konverzace nad obsahem, který vyberete. Dotaz je jednorázová otázka nad vším (nebo nad vybranými sešity). Transformace spustí uložený prompt nad jedním zdrojem a výsledek uloží jako poznatek.

---

### 4. [Jak fungují podcasty](podcasts-explained.md)
Jak vzniká epizoda podcastu z vašeho obsahu.

**Hlavní myšlenka**: Model osnovy a model scénáře napíší z vybraného obsahu scénář a model převodu textu na řeč ho namluví. Nastavení drží profily epizod a profily mluvčích.

---

## Celkový obraz

- **Poskytovatele volíte vy.** Open Notebook pracuje s cloudovými i lokálními poskytovateli AI. Cloudový poskytovatel dostane obsah, který mu jednotlivé funkce pošlou (popsáno na stránkách výše); s lokálními modely zůstávají prompty na vašem stroji. Přidání webového odkazu ho ale stále stahuje z internetu a nástroje pro URL Firecrawl a Jina, pokud jsou nastavené, stahují stránky přes své služby.
- **Co AI uvidí, určujete vy.** V chatu nastavujete kontext pro každý zdroj a poznámku. Dotazy a hledání lze omezit na konkrétní sešity.
- **Data zůstávají ve vašem nasazení.** Zdroje, poznatky, poznámky a záznamy podcastů jsou v databázi SurrealDB. Nahrané soubory, vytvořený zvuk podcastů a historie chatu (soubor checkpointu) jsou v datové složce aplikace. Zálohujte obojí.

## Další kroky

- **Chcete začít pracovat?** Přejděte do [Uživatelské příručky](../3-USER-GUIDE/index.md)
- **Ještě nemáte nainstalováno?** Přejděte na [Installation](../../1-INSTALLATION/index.md) (anglicky)
