# Poskytovatelé AI

Open Notebook komunikuje s modely AI prostřednictvím poskytovatelů. Poskytovatele jednou připojíte v části **Spravovat → Modely**, vyberete, které jeho modely chcete používat, a pro každou úlohu (chat, embeddingy, přepis a další) zvolíte výchozí model.

Stránka má tři části:

1. [Připojení poskytovatele](#connect-a-provider): kroky, na které odkazují všechny instalační návody
2. [Podporovaní poskytovatelé](#supported-providers): co který poskytovatel umí
3. [Výběr poskytovatelů](#choosing-providers): jaká kombinace se hodí pro vaše nasazení

Podrobnosti k jednotlivým poskytovatelům (kde získat klíč, základní URL, regionální endpointy) jsou v [AI Providers Configuration Guide](../../5-CONFIGURATION/ai-providers.md) (anglicky).

---

<a id="connect-a-provider"></a>
## Připojení poskytovatele

Postupujte takto, jakmile Open Notebook běží a otevřete jeho rozhraní. Na konci budete mít funkční chat.

> **Než začnete:** musí být nastaveno `OPEN_NOTEBOOK_ENCRYPTION_KEY` (nastavují ho všechny instalační návody). Pokud není, stránka Modely ukazuje „Šifrovací klíč není nastaven“ a klíče neuloží.

### 1. Přidání konfigurace

1. V levém postranním panelu v části **Spravovat** klikněte na **Modely**.
2. Najděte v seznamu svého poskytovatele a klikněte na **Přidat konfiguraci**.
3. Vyplňte formulář:
   - **Název konfigurace**: libovolný popisek, například `Osobní`.
   - **API klíč**: klíč od poskytovatele. Lokální poskytovatelé jako Ollama a oMLX ho nepotřebují (pole je označeno jako volitelné).
   - **Základní URL**: u cloudových poskytovatelů nechte prázdné. Lokální a vlastní servery ji potřebují (například `http://ollama:11434` pro kontejner Ollama nebo `http://vllm-qwen:8000/v1` pro vLLM).
   - **Google Vertex AI** má jiný formulář: **ID projektu GCP** a **Region** (povinné) a volitelnou **Cestu k JSON servisního účtu** místo API klíče. Bez cesty k JSON se použijí výchozí přístupové údaje Google Cloud na serveru.
4. Klikněte na **Přidat konfiguraci**.

### 2. Test připojení

U nové konfigurace klikněte na **Test** (popisek: *Otestovat připojení*). Zelená fajfka znamená, že se Open Notebook s vaším klíčem k poskytovateli dostal. Červený křížek znamená chybný klíč, základní URL nebo síť; viz [Řešení potíží](#troubleshooting).

### 3. Přidání modelů

1. U stejné konfigurace klikněte na **Modely** (popisek: *Synchronizovat modely*). Dialog **Vyhledat modely** ukáže modely, které poskytovatel nabízí.
2. Nejdřív nastavte **Typ modelu**: `Language`, `Embedding`, `TTS` nebo `STT`. Seznam se podle typu nefiltruje, proto vyberte typ a zaškrtněte jen modely tohoto typu.
3. Zaškrtněte požadované modely (nebo napište název do vyhledávacího pole a přidejte model, který v seznamu není) a klikněte na **Přidat (N)**.
4. Pro každý další potřebný typ otevřete dialog znovu. Minimálně přidejte jeden model typu **Language** a jeden typu **Embedding**.

<a id="4-set-default-models"></a>
### 4. Nastavení výchozích modelů

Na stejné stránce sjeďte dolů k části **Výchozí přiřazení modelů**.

- Dokud chybí některý povinný výchozí model, zobrazuje se upozornění s tlačítkem **Automaticky přiřadit výchozí**. Kliknutím doplníte **Model chatu** a **Embedding model** z přidaných modelů.
- Nebo vyberte každý výchozí model v jeho rozbalovacím seznamu. Změny se ukládají okamžitě.

| Výchozí model | Povinný | K čemu slouží |
|---|---|---|
| **Model chatu** | Ano | Chat se sešitem a se zdrojem |
| **Embedding model** | Ano | Vektorové hledání a dotazy (Ask) |
| **Model převodu textu na řeč** | Ne | Zatím se nepoužívá: podcasty používají hlasový model nastavený v každém profilu mluvčích |
| **Model převodu řeči na text** | Ne | Přepis zvukových a video zdrojů |
| **Model transformací** | Ne (použije se model chatu) | Transformace a poznatky |
| **Model nástrojů** | Ne (použije se model chatu) | Dotazy (Ask): výchozí pro všechny tři fáze na stránce dotazů (modely vybrané v části **Pokročilé** ho přepíšou) a pro požadavky API bez určených modelů |
| **Model pro velký kontext** | Ne (použije se model chatu) | Sem se automaticky posílá každý prompt delší než asi 105 tisíc tokenů |

**Automaticky přiřadit výchozí** doplní jen model chatu a embedding model. Model převodu řeči na text nastavte ručně, pokud chcete přepisovat zvuk a video; pro podcasty vyberte hlasový model v každém profilu mluvčích (**Podcasty → Profily**).

### 5. Ověření, že chat funguje

1. V postranním panelu klikněte na **Sešity** → **Nový sešit**, zadejte název a klikněte na **Vytvořit nový sešit**.
2. V sešitu klikněte na tlačítko **Přidat zdroj** a v nabídce vyberte **Přidat zdroj** (druhá položka, **Přidat existující zdroje**, použije zdroje, které už máte). Zvolte **Zadat text**, vložte odstavec, zadejte název, pak tlačítkem **Další** projděte zbývající kroky a klikněte na **Hotovo**.
3. Počkejte, až se zdroj zpracuje, pak napište otázku do panelu chatu a odešlete ji klávesami **Ctrl+Enter** (**⌘+Enter** na macOS).

Pokud dostanete odpověď, je hotovo. Další poskytovatele můžete kdykoli přidat stejně; každý má vlastní konfigurace a modely.

<a id="troubleshooting"></a>
### Řešení potíží

- **Test u cloudového poskytovatele selže**: ověřte klíč na webu poskytovatele a zda má účet kredit. Klíč nahradíte úpravou konfigurace.
- **Test u lokálního poskytovatele selže**: základní URL musí být dostupná *z kontejneru Open Notebooku*, ne z vašeho prohlížeče. `localhost` uvnitř kontejneru je kontejner sám. Viz [Ollama](../../5-CONFIGURATION/ollama.md) (anglicky).
- **Chat hlásí „No model configured…“**: některý výchozí model je prázdný. Vraťte se ke kroku 4.
- **Zdroj zůstává navždy ve frontě**: neběží worker na pozadí. V Dockeru běží uvnitř kontejneru `open_notebook` (zkontrolujte `docker compose logs open_notebook`); při spuštění ze zdrojového kódu ho spouštíte sami.
- **„Chyba dešifrování“ u konfigurace**: `OPEN_NOTEBOOK_ENCRYPTION_KEY` se od uložení klíče změnil. Konfiguraci smažte a přidejte znovu.
- Další: [Potíže s AI a chatem](../6-TROUBLESHOOTING/ai-chat-issues.md).

---

<a id="supported-providers"></a>
## Podporovaní poskytovatelé

Open Notebook podporuje 24 poskytovatelů. Tabulka uvádí typy modelů, které poskytovatel nabízí při přidání konfigurace. Co skutečně přidáte, závisí na modelech dostupných ve vašem účtu u poskytovatele.

| Poskytovatel | Language | Embedding | Řeč na text | Text na řeč | Nastavení |
|---|:-:|:-:|:-:|:-:|---|
| OpenAI | ✅ | ✅ | ✅ | ✅ | [návod](../../5-CONFIGURATION/ai-providers.md#openai) |
| Anthropic | ✅ | | | | [návod](../../5-CONFIGURATION/ai-providers.md#anthropic-claude) |
| Google AI (Gemini) | ✅ | ✅ | ✅ | ✅ | [návod](../../5-CONFIGURATION/ai-providers.md#google-gemini) |
| Groq | ✅ | | ✅ | | [návod](../../5-CONFIGURATION/ai-providers.md#groq) |
| Mistral AI | ✅ | ✅ | ✅ | ✅ | |
| DeepSeek | ✅ | | | | |
| xAI (Grok) | ✅ | | | ✅ | |
| OpenRouter | ✅ | ✅ | ✅ | ✅ | [návod](../../5-CONFIGURATION/ai-providers.md#openrouter) |
| DashScope (Qwen) | ✅ | | | | [návod](../../5-CONFIGURATION/ai-providers.md#dashscope-qwen) |
| MiniMax | ✅ | | | ✅ | [návod](../../5-CONFIGURATION/ai-providers.md#minimax) |
| Novita | ✅ | | | | [návod](../../5-CONFIGURATION/ai-providers.md#novita) |
| SiliconFlow | ✅ | | | | [návod](../../5-CONFIGURATION/ai-providers.md#siliconflow) |
| Z.ai | ✅ | | | | [návod](../../5-CONFIGURATION/ai-providers.md#zai) |
| PayPerQ (PPQ) | ✅ | ✅ | ✅ | ✅ | [návod](../../5-CONFIGURATION/ai-providers.md#payperq-ppq) |
| Cohere | ✅ | ✅ | | | [návod](../../5-CONFIGURATION/ai-providers.md#cohere) |
| Voyage AI | | ✅ | | | |
| ElevenLabs | | | ✅ | ✅ | |
| Deepgram | | | ✅ | ✅ | |
| Ollama (lokální) | ✅ | ✅ | | | [návod](../../5-CONFIGURATION/ollama.md) |
| oMLX (lokální, Apple Silicon) | ✅ | ✅ | | | [návod](../../5-CONFIGURATION/omlx.md) |
| Azure OpenAI | ✅ | ✅ | ✅ | ✅ | [návod](../../5-CONFIGURATION/ai-providers.md#azure-openai) |
| Google Vertex AI | ✅ | ✅ | | ✅ | |
| OpenAI Compatible | ✅ | ✅ | ✅ | ✅ | [návod](../../5-CONFIGURATION/openai-compatible.md) |
| Anthropic Compatible | ✅ | | | | [návod](../../5-CONFIGURATION/ai-providers.md#anthropic-compatible) |

Návody k poskytovatelům jsou v angličtině.

**OpenAI Compatible** pokrývá každý server, který mluví API OpenAI: LM Studio, vLLM, LocalAI a vlastní řečové servery ([local TTS](../../5-CONFIGURATION/local-tts.md), [local STT](../../5-CONFIGURATION/local-stt.md)). LM Studio nemá vlastního poskytovatele; přidejte ho jako OpenAI Compatible.

---

<a id="choosing-providers"></a>
## Výběr poskytovatelů

Open Notebook potřebuje alespoň **jazykový** model (pro chat) a **embedding** model (pro hledání a dotazy). Podcasty navíc potřebují **převod textu na řeč**.

**Jeden poskytovatel na vše.** OpenAI, Google AI, Mistral AI, OpenRouter, PayPerQ a Azure OpenAI nabízejí pod jedním klíčem všechny čtyři typy modelů. Je to nejjednodušší nastavení.

**Poskytovatelé jen s jazykovými modely potřebují partnera.** Anthropic, DeepSeek, DashScope, Novita, SiliconFlow, Z.ai a Anthropic Compatible nabízejí jen jazykové modely. Pro embeddingy (a pro převod textu na řeč, chcete-li podcasty) přidejte druhého poskytovatele, například OpenAI, Google AI, Mistral AI, Voyage AI nebo lokální Ollamu.

**Plně lokálně.** Ollama a oMLX poskytují jazykové a embedding modely na vašem vlastním hardwaru, stejně tak vLLM připojený jako OpenAI Compatible. Pro podcasty a přepis bez cloudu přidejte lokální řečový server přes OpenAI Compatible ([local TTS](../../5-CONFIGURATION/local-tts.md), [local STT](../../5-CONFIGURATION/local-stt.md)). Lokální modely jsou na CPU pomalejší; pomůže GPU nebo Apple Silicon.

**Kombinování je běžné.** Každý výchozí model může být od jiného poskytovatele, například cloudový model chatu s lokálními embeddingy.

**Pozdější změna embedding modelu** znamená přestavbu stávajících vektorů. Rozhraní se před změnou zeptá a odkáže na přestavbu na stránce **Pokročilé**.

Ceny, kontextová okna a nabídky modelů se často mění, proto je tento návod neuvádí. Ověřte je na stránkách jednotlivých poskytovatelů.

---

## Další kroky

- [AI Providers Configuration Guide](../../5-CONFIGURATION/ai-providers.md) (anglicky): klíče, základní URL a regionální endpointy jednotlivých poskytovatelů
- [Ollama](../../5-CONFIGURATION/ollama.md) (anglicky): lokální modely, síť a časové limity
- [Uživatelská příručka](../3-USER-GUIDE/index.md): přidávání zdrojů, chat, podcasty

**Potřebujete pomoc?** Přidejte se ke [komunitě na Discordu](https://discord.gg/37XJPXfz2w) (anglicky).
