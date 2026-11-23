# Open Notebook – Začínáme

**Open Notebook** je AI asistent pro práci s podklady a výzkum, který provozujete sami a který chrání vaše data. Přidáte dokumenty, webové stránky, zvuk i video, ptáte se na ně AI a dostáváte odpovědi s citacemi, píšete poznámky a z podkladů vytváříte podcasty – vše s poskytovateli AI, které si sami zvolíte.

## Zvolte si cestu

Každý rychlý start nainstaluje Open Notebook přes Docker Compose a skončí funkčním chatem.

### Mám API klíč ke cloudovému poskytovateli AI
OpenAI, Anthropic, Google, Mistral, Groq, OpenRouter a další.

→ [Rychlý start s cloudovým poskytovatelem](quick-start-cloud.md) (asi 5 minut)

### Chci vše provozovat lokálně
Ollama v Dockeru vedle Open Notebooku. Žádné API klíče, nic neopouští váš počítač.

→ [Rychlý start – lokálně](quick-start-local.md) (asi 10 minut plus stažení modelů)

**Už máte Ollamu nainstalovanou v počítači?** → [Rychlý start s externí Ollamou](quick-start-external-ollama.md)

### Něco jiného
Spuštění ze zdrojového kódu, Windows bez Dockeru nebo hostingová platforma → [Installation Guide](../../1-INSTALLATION/index.md) (anglicky)

---

## Co můžete dělat

- **Přidávat obsah**: PDF, soubory Office a OpenDocument, webové stránky, YouTube, zvuk, video, prostý text
- **Chatovat**: ptát se na zdroje v sešitu, dostávat odpovědi s citacemi a určovat, co který zdroj AI poskytne
- **Ptát se a hledat**: fulltextové a sémantické hledání napříč vším
- **Transformovat**: spouštět nad zdroji prompty pro shrnutí a vytažení informací a získávat tak poznatky
- **Psát poznámky**: vlastní, nebo uložené odpovědi AI
- **Tvořit podcasty**: 1 až 4 mluvčí s nastavitelnými profily

## Open Notebook a Google NotebookLM

| | Open Notebook | Google NotebookLM |
|---|---|---|
| **Kde běží** | Na vašem počítači nebo serveru | V cloudu Googlu |
| **Modely AI** | 20+ poskytovatelů, cloudových i lokálních | Modely Googlu |
| **Mluvčí v podcastu** | 1–4, nastavitelné profily | Formáty Googlu |
| **Cena** | Software zdarma; platíte poskytovateli AI (s lokálními modely nic) | Bezplatná úroveň a předplatné |
| **Bez internetu** | Ano, s lokálními modely | Ne |

## Předpoklady

- **Docker** pro rychlé starty. Instalace [ze zdrojového kódu](../../1-INSTALLATION/from-source.md) a [nativně ve Windows](../../1-INSTALLATION/windows-native.md) Docker pro samotnou aplikaci nepotřebují.
- **Poskytovatel AI**: cloudový API klíč, nebo lokální server s modely, například Ollama či vLLM.

---

**Potřebujete pomoc?** Přidejte se ke [komunitě na Discordu](https://discord.gg/37XJPXfz2w) (anglicky) nebo projděte [celou dokumentaci](../index.md).
