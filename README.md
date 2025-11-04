# AI_parser

## Descrizione

Strumento Python per l’estrazione di dati da fatture energetiche e la generazione di XML conformi alla Fattura Elettronica. Supporta:
- Estrazione da PDF singolo tramite AI (`ai_parser.py`)
- Estrazione multi-fattura da PDF con più POD/PDR per file (`ai_parser_extended.py`)

## Requisiti
- Python 3.10+
- Chiave OpenAI (`OPENAI_API_KEY`)

## Setup ambiente
Consigliato utilizzare il virtualenv incluso:
```bash
cd /Users/ggs/Documents/Projects/AI_parser
./myenv/bin/python -V
```

Configura la chiave OpenAI (uno dei due metodi):
- File .env nel root del progetto (consigliato):
  ```
  OPENAI_API_KEY=la_tua_chiave_segreta
  ```
- Variabile d’ambiente nella shell corrente:
  ```bash
  export OPENAI_API_KEY="la_tua_chiave_segreta"
  ```

Il caricamento della chiave è gestito da `get_openai_api_key_from_env()` che legge: variabile d’ambiente, `.env` accanto agli script o `.env` nella CWD.

## Struttura cartelle
- `data/xml_files/`: XML di input per il parser base (`ai_parser.py`)
- `data/pdf_converted/`: PDF estratti dagli XML (parser base)
- `data/output/`: XML generati (parser base)

- `data/xml_multi_pod/`: XML di input contenenti allegati PDF con più fatture/POD
- `data/xml_multi_pod/output/`: output dell’esteso (per ogni XML, una sottocartella con PDF e XML per-POD)



## Utilizzo

### Parser base (un PDF → un XML)
Elabora tutti gli XML in `data/xml_files/`, estrae il PDF allegato e genera l’XML corrispondente.
```bash
./myenv/bin/python ai_parser.py
```

### Parser esteso multi-POD (`ai_parser_extended.py`)
Elabora XML in `data/xml_multi_pod/`, estrae il PDF allegato e per ogni POD/PDR rilevato nel PDF genera un XML.

Esecuzione completa (tutti gli XML):
```bash
./myenv/bin/python ai_parser_extended.py
```

Solo primo XML (test rapido) e solo primo POD (minimizza costi API):
```bash
./myenv/bin/python ai_parser_extended.py --test-one --first-pod-only
```

Pulizia opzionale prima di eseguire (solo se supportata dalla versione attuale del main):
```bash
./myenv/bin/python ai_parser_extended.py --clean
```

Output esteso:
- PDF estratto rinominato e salvato in `data/xml_multi_pod/output/<nome_xml>/<nome_pdf>_<nome_xml>.pdf`
- XML per-POD in `data/xml_multi_pod/output/<nome_xml>/<POD|PDR>_<codice>_converted.xml`

## Funzionalità principali
- Estrazione AI dei campi fattura: intestazione, periodo, servizi di vendita, servizi di rete, imposte, nota IVA
- Ricostruzione XML conforme usando i blocchi originali (header, riepilogo, pagamento, allegati)
- Multi-POD: raggruppamento delle sezioni del PDF per POD/PDR e generazione di XML separati
- Flag di test per ridurre l’uso di API (solo primo XML e/o primo POD)

## Note utili
- Il parser base salta le prime 2 pagine del PDF durante la lettura testo (impostazione conservata nell’esteso dove rilevante)
- Se non viene rilevato un POD/PDR, la sezione viene ignorata per evitare output errati
- Log di debug possono essere reindirizzati su file: `./myenv/bin/python ai_parser_extended.py --test-one > run.log 2>&1`

## Build eseguibile (opzionale)
Se necessario, consulta `setup.py`:
```bash
./myenv/bin/python setup.py
```
L’eseguibile verrà generato in `dist/`.

Il comando sopra installerà i requisiti, chiederà la tua `OPENAI_API_KEY` e costruirà due eseguibili:
- `dist/ai_parser` (parser base)
- `dist/ai_parser_extended` (parser multi-POD)

Una volta creati, puoi avviarli con doppio click (macOS potrebbe richiedere permessi) oppure da terminale:
```bash
./dist/ai_parser
./dist/ai_parser_extended
```
