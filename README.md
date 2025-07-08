# AI_parser

## Descrizione

**AI_parser** è uno strumento Python che estrae dati strutturati da fatture energetiche in PDF e genera file XML conformi al formato della Fattura Elettronica italiana. Utilizza l’intelligenza artificiale (OpenAI GPT) per l’estrazione dei dati e supporta l’elaborazione batch di più fatture.

---

## Requisiti

- Python 3.8 o superiore
- OpenAI API Key

---

## Installazione

1. **Clona il repository**
    ```bash
    git clone https://github.com/tuo-utente/AI_parser.git
    cd AI_parser
    ```

2. **Configura l'eseguibile**
    ```bash
    python setup.py
    ```
    Segui le istruzioni per inserire la tua API Key.

---

## Struttura delle cartelle
- data/ xml_files/ -> XML delle fatture di input 
- pdf_converted/ -> PDF estratti dagli XML 
- output/ -> XML generati in output 

---

## Utilizzo

### Esecuzione da sorgente

```bash
python ai_parser.py
```

### Generazione dell’eseguibile standalone

```bash
python setup.py
```

L’eseguibile verrà creato nella cartella dist.

## Funzionalità principali
- Estrazione automatica dei dati da PDF di fatture energetiche tramite AI
- Conversione in XML conforme alla Fattura Elettronica
- Elaborazione batch di più file XML
- Gestione allegati PDF contenuti negli XML

## Personalizzazione
- Inserisci i tuoi file XML nella cartella xml_files.
- I PDF estratti verranno salvati in pdf_converted.
- Gli XML generati saranno disponibili in output.