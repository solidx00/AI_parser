
# import fitz
# import sys
# import shutil
# import json
# from typing import Dict, List, Any, Optional
# import openai
# from pathlib import Path
# from lxml import etree
# import os
# from utils import estrai_pdf_from_xml


# def get_openai_api_key_from_env():
#     # 1) Usa variabile d'ambiente se presente
#     key = os.environ.get("OPENAI_API_KEY")
#     if key:
#         return key

#     # 2) Prova a leggere un file .env nella directory del file corrente
#     env_path = os.path.join(os.path.dirname(__file__), ".env")
#     if os.path.exists(env_path):
#         with open(env_path, "r") as f:
#             for line in f:
#                 if line.startswith("OPENAI_API_KEY="):
#                     return line.strip().split("=", 1)[1]

#     # 3) Prova anche nella current working directory (utile se eseguito da IDE)
#     cwd_env = os.path.join(os.getcwd(), ".env")
#     if os.path.exists(cwd_env):
#         with open(cwd_env, "r") as f:
#             for line in f:
#                 if line.startswith("OPENAI_API_KEY="):
#                     return line.strip().split("=", 1)[1]

#     print("⚠️ OPENAI_API_KEY non trovata. Imposta la variabile d'ambiente o crea un file .env nel progetto.")
#     return None

# def get_base_path():
#     if getattr(sys, 'frozen', False):
#         # Se eseguito da PyInstaller
#         return sys._MEIPASS
#     return os.path.dirname(os.path.abspath(__file__))

# class InvoiceParser:
#     def __init__(self, openai_api_key: str = None):
#         self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        
#     def extract_text_from_pdf(self, pdf_path: str) -> str:
#         """Estrae tutto il testo dal PDF, escludendo la prima e la seconda pagina"""
#         doc = fitz.open(pdf_path)
#         full_text = ""
        
#         # Salta la prima (0) e la seconda (1) pagina
#         for page_num in range(2, doc.page_count):
#             page = doc[page_num]
#             text = page.get_text()
#             full_text += f"\n--- PAGINA {page_num + 1} ---\n{text}"
            
#         doc.close()
#         return full_text
    
    
#     def extract_with_ai(self, text: str) -> Dict[str, Any]:
#         """Usa GPT per estrarre dati strutturati dal testo"""
#         if not self.openai_client:
#             raise ValueError("OpenAI API key non configurato")
            
#         prompt = f"""
#         Analizza questa fattura energetica e estrai TUTTE le informazioni seguenti:

#         DATI PRINCIPALI FATTURA:
#         - numero_fattura (string)
#         - data_emissione (formato DD/MM/YYYY)
#         - data_scadenza (formato DD/MM/YYYY) 
#         - importo_totale (numero decimale)
#         - importo_pagamento (numero decimale, spesso uguale al totale)
#         - pod o pdr (codice alfanumerico di 14-15 caratteri)
#         - causale (descrizione del pagamento)
#         - data_inizio_periodo (formato DD/MM/YYYY)
#         - data_fine_periodo (formato DD/MM/YYYY)
#         - cliente (nome/ragione sociale cliente)
#         - fornitore (nome fornitore energia)

#         DETTAGLIO SERVIZI (estrai da queste sezioni, se presenti):
#         1. "Servizi di Vendita" 
#         2. "Servizi di Rete"
#         3. "Imposte"
        
#         Per ogni voce dei servizi estrai:
#         - descrizione
#         - unità di misura  
#         - prezzo unitario
#         - quantità (almeno 4 cifre decimali, es: 0.0000)
#         - totale €
        
#         NOTA IVA:
#         Se nel testo è presente la voce “IVA 22% scissione dei pagamenti-art.17 ter DPR 633/72” tra le imposte, escludila dall’elenco delle imposte e inseriscila separatamente in un campo "nota_iva" come oggetto con "descrizione" e "importo".
        
#         REGOLE IMPORTANTI:
#         - Per i servizi di vendita, estrai la quantità solo per il "prezzo dell’energia" e non per "perdite di rete", "Dispacciamento" e "Componente CSAL" (e per il gas, solo per la Commercializzazione al dettaglio parte variabile); per gli altri servizi imposta la quantità a 0.0000.
#         - Sii preciso con numeri e date.
        
#         Restituisci un JSON valido, senza racchiuderlo in ```json o altri delimitatori di codice, con questa struttura:
#         {{
#             "dati_fattura": {{
#                 "numero_fattura": "123456",
#                 "data_emissione": "15/06/2024",
#                 "data_scadenza": "15/07/2024",
#                 "importo_totale": 125.50,
#                 "importo_pagamento": 125.50,
#                 "pod": "IT001E12345678",
#                 "causale": "Fornitura energia elettrica",
#                 "data_inizio_periodo": "01/05/2024",
#                 "data_fine_periodo": "31/05/2024",
#                 "cliente": "Nome Cliente",
#                 "fornitore": "Nome Fornitore"
#             }},
#             "servizi_vendita": [
#                 {{
#                     "descrizione": "nome servizio",
#                     "unita_misura": "€/kWh",
#                     "prezzo_unitario": 0.00,
#                     "quantita": 0.0000,
#                     "totale": 0.00
#                 }}
#             ],
#             "servizi_rete": [...],
#             "imposte": [...],
#             "nota_iva": [
#                 {{
#                     "descrizione": "IVA 22% scissione dei pagamenti-art.17 ter DPR 633/72",
#                     "importo": 35.03
#                 }}
#         }}
        
#         Se un campo non è presente, metti null.
        
#         TESTO FATTURA:
#         {text}
#         """ 
#         #print("Prompt AI:", prompt + "...")
        
#         response = self.openai_client.chat.completions.create(
#             model="gpt-4.1-mini",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0
#         )
        
#         try:
#             result = json.loads(response.choices[0].message.content)
#             print("✅ Estrazione AI completata con successo")
#             return result
#         except json.JSONDecodeError as e:
#             print(f"❌ Errore parsing JSON AI: {e}")
#             print(f"Risposta AI: {response.choices[0].message.content}...")
#             return {}


#     def parse_invoice(self, pdf_path: str) -> Dict[str, Any]:
#         """Parser principale con AI"""
        
#         # Estrai testo dal PDF
#         text = self.extract_text_from_pdf(pdf_path)
#         if not text:
#             raise ValueError("Nessun testo estratto dal PDF")
        
#         # Se i risultati regex sono scarsi e hai l'AI, usa quello
#         data_ai = self.extract_with_ai(text)
            
#         return data_ai

#     def crea_xml_fattura(self, dati_json: Dict[str, Any], campi_xml_estratti: Dict[str, Any], output_path="fattura_output.xml"):
        
#         # Campi linee descrizione
#         campi = dati_json["dati_fattura"]
#         vendite = dati_json["servizi_vendita"]
#         rete = dati_json["servizi_rete"]
#         imposte = dati_json["imposte"]
#         nota_iva = dati_json["nota_iva"]
        
#         # Campi linee xml [Header, Riepilogo, DatiGenerali, Attachment]
#         header = campi_xml_estratti["header"]
#         dati_generali = campi_xml_estratti["dati_generali"]
#         dettaglio_linee = campi_xml_estratti["dettaglio_linee"]
#         riepilogo = campi_xml_estratti["riepilogo"]
#         dati_pagamento = campi_xml_estratti["dati_pagamento"]
#         attachment = campi_xml_estratti["attachment"]

#         nsmap = {
#             "nm": "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2",
#             "prx": "urn:sap.com:proxy:PR1:/1SAI/TAS34E96A2AC5E40CADB2DF:731",
#             "soap-env": "http://schemas.xmlsoap.org/soap/envelope/"
#         }

#         root = etree.Element("FatturaElettronica", versione="FPA12", nsmap=nsmap)
        
#         # === HEADER ===
#         header_root = etree.fromstring(header)
#         root.append(header_root)

#         # Crea <FatturaElettronicaBody>
#         body = etree.SubElement(root, "FatturaElettronicaBody")
#         # Aggiungi DatiGenerali
#         dati_generali_root = etree.fromstring(dati_generali)
#         body.append(dati_generali_root)

#         # Aggiungi DatiBeniServizi
#         beni_servizi = etree.SubElement(body, "DatiBeniServizi")

#         if dettaglio_linee:
#             riga_dettaglio_linee = 1
#             dettaglio_linee_root = etree.fromstring(dettaglio_linee)
#             beni_servizi.append(dettaglio_linee_root)
        
#         # === Righe Vendite ===
#         if vendite:
#             for i, riga in enumerate(vendite, start=riga_dettaglio_linee + 1):
#                 linea = etree.SubElement(beni_servizi, "DettaglioLinee")
#                 etree.SubElement(linea, "NumeroLinea").text = str(i)
#                 etree.SubElement(linea, "Descrizione").text = riga["descrizione"]
#                 etree.SubElement(linea, "Quantita").text = str(riga["quantita"])
#                 etree.SubElement(linea, "UnitaMisura").text = riga["unita_misura"]
#                 etree.SubElement(linea, "DataInizioPeriodo").text = campi["data_inizio_periodo"]
#                 etree.SubElement(linea, "DataFinePeriodo").text = campi["data_fine_periodo"]
#                 etree.SubElement(linea, "PrezzoUnitario").text = str(riga["prezzo_unitario"])
#                 etree.SubElement(linea, "PrezzoTotale").text = str(riga["totale"])
#                 etree.SubElement(linea, "AliquotaIVA").text = "0.00"

#         # === Righe Rete ===
#         if rete:
#             for i, riga in enumerate(rete, start=len(vendite) + 1):
#                 linea = etree.SubElement(beni_servizi, "DettaglioLinee")
#                 etree.SubElement(linea, "NumeroLinea").text = str(i)
#                 etree.SubElement(linea, "Descrizione").text = riga["descrizione"]
#                 etree.SubElement(linea, "Quantita").text = "0.0000"#str(riga["quantita"])
#                 etree.SubElement(linea, "UnitaMisura").text = riga["unita_misura"]
#                 etree.SubElement(linea, "DataInizioPeriodo").text = campi["data_inizio_periodo"]
#                 etree.SubElement(linea, "DataFinePeriodo").text = campi["data_fine_periodo"]
#                 etree.SubElement(linea, "PrezzoUnitario").text = str(riga["prezzo_unitario"])
#                 etree.SubElement(linea, "PrezzoTotale").text = str(riga["totale"])
#                 etree.SubElement(linea, "AliquotaIVA").text = "0.00"

#         # === Righe Imposte ===
#         if imposte:
#             for i, riga in enumerate(imposte, start=len(vendite) + len(rete) + 1):
#                 linea = etree.SubElement(beni_servizi, "DettaglioLinee")
#                 etree.SubElement(linea, "NumeroLinea").text = str(i)
#                 etree.SubElement(linea, "Descrizione").text = riga["descrizione"]
#                 etree.SubElement(linea, "Quantita").text = "0.0000" #str(riga["quantita"])
#                 etree.SubElement(linea, "UnitaMisura").text = riga["unita_misura"]
#                 etree.SubElement(linea, "DataInizioPeriodo").text = campi["data_inizio_periodo"]
#                 etree.SubElement(linea, "DataFinePeriodo").text = campi["data_fine_periodo"]
#                 etree.SubElement(linea, "PrezzoUnitario").text = str(riga["prezzo_unitario"])
#                 etree.SubElement(linea, "PrezzoTotale").text = str(riga["totale"])
#                 etree.SubElement(linea, "AliquotaIVA").text = "0.00"
        
#         # === Righe Nota Iva ===
#         if nota_iva:
#             for i, riga in enumerate(nota_iva, start=len(vendite) + len(rete) + len(imposte) + 1):
#                 linea = etree.SubElement(beni_servizi, "DettaglioLinee")
#                 etree.SubElement(linea, "NumeroLinea").text = str(i)
#                 etree.SubElement(linea, "Descrizione").text = riga["descrizione"]
#                 etree.SubElement(linea, "DataInizioPeriodo").text = campi["data_inizio_periodo"]
#                 etree.SubElement(linea, "DataFinePeriodo").text = campi["data_fine_periodo"]
#                 etree.SubElement(linea, "PrezzoUnitario").text = "0.00"
#                 etree.SubElement(linea, "PrezzoTotale").text = str(riga["importo"])
#                 etree.SubElement(linea, "AliquotaIVA").text = "0.00"

#         # === Dati Riepilogo ===
#         riepilogo_root = etree.fromstring(riepilogo)
#         beni_servizi.append(riepilogo_root)
        
#         # Dati Pagamento
#         dati_pagamento_root = etree.fromstring(dati_pagamento)
#         body.append(dati_pagamento_root)

#         # Aggiungi Attachment
#         attachment_root = etree.fromstring(attachment)
#         body.append(attachment_root)

#         # Scrivi su file
#         tree = etree.ElementTree(root)
        
#         tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    
    
#     def process_batch(self, data_folder: str, output_folder: str) -> List[str]:
#         """
#         Processa tutti i file PDF in una cartella e genera XML per ciascuno.
        
#         Args:
#             data_folder (str): Cartella contenente i file PDF.
#             output_folder (str): Cartella dove salvare gli XML generati.
        
#         Returns:
#             List[str]: Lista dei percorsi dei file XML generati.
#         """
#         xml_folder = os.path.join(data_folder, "xml_files")
#         pdf_folder = os.path.join(data_folder, "pdf_converted")
        
#         if not os.path.exists(xml_folder):
#             raise FileNotFoundError(f"Cartella XML non trovata: {xml_folder}")
#         os.makedirs(output_folder, exist_ok=True)
        
#         xml_files = list(Path(xml_folder).glob("*.xml"))
#         if not xml_files:
#             raise ValueError("Nessun file XML trovato nella cartella specificata.")
#         print(f"📂 Trovati {len(xml_files)} file XML da elaborare nella cartella: {xml_folder}")
#         total_files = len(xml_files)
#         for idx, xml_file in enumerate(xml_files, start=1):
#             print(f"🔄 [{idx}/{total_files}] Elaborazione file: {xml_file.name}")
#             field_xml, path_pdf = estrai_pdf_from_xml(str(xml_file), pdf_folder)
#             data = parser.parse_invoice(path_pdf)
#             output_path = f"{output_folder}/{xml_file.stem}_{Path(path_pdf).stem}_converted.xml"
#             parser.crea_xml_fattura(data, field_xml, str(output_path))
#             print(f"✅ [{idx}/{total_files}] Fattura elettronica XML generata con successo: {output_path}")
     
# '''
# if __name__ == "__main__":
#     DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
#     #XML_DIR = os.path.join(DATA_DIR, "xml_files")
#     PDF_CONVERTED_DIR = os.path.join(DATA_DIR, "pdf_converted")
#     OUTPUT_DIR = os.path.join(DATA_DIR, "output")

#     # Elimina le cartelle pdf_converted e output se esistono
#     for folder in [PDF_CONVERTED_DIR, OUTPUT_DIR]:
#         if os.path.exists(folder):
#             shutil.rmtree(folder)
#         os.makedirs(folder, exist_ok=True)
    
#     field_xml, path_pdf = estrai_pdf_from_xml("/Users/francescociteroni/Documents/Progetti/AI_parser/data/xml_files/IT02221101203_kBuOH.xml", PDF_CONVERTED_DIR)
    
#     api_key = get_openai_api_key_from_env()
#     parser = InvoiceParser(openai_api_key=api_key)
    
#     print(f"🧪 Sto elaborando la fattura {path_pdf} ")
#     data = parser.parse_invoice(path_pdf)
#     print(json.dumps(data, indent=2, ensure_ascii=False))

#     output_folder = f"{OUTPUT_DIR}/{Path(path_pdf).stem}_converted.xml"

#     parser.crea_xml_fattura(data, field_xml, output_folder)
# '''

# if __name__ == "__main__":
#     BASE_DIR = get_base_path()
#     DATA_DIR = os.path.join(BASE_DIR, "data")
#     XML_DIR = os.path.join(DATA_DIR, "xml_files")
#     PDF_CONVERTED_DIR = os.path.join(DATA_DIR, "pdf_converted")
#     OUTPUT_DIR = os.path.join(DATA_DIR, "output")

#     # Elimina le cartelle pdf_converted e output se esistono
#     for folder in [PDF_CONVERTED_DIR, OUTPUT_DIR]:
#         if os.path.exists(folder):
#             shutil.rmtree(folder)
#         os.makedirs(folder, exist_ok=True)

#     api_key = get_openai_api_key_from_env()
#     parser = InvoiceParser(openai_api_key=api_key)
    
#     parser.process_batch(DATA_DIR, OUTPUT_DIR)


import fitz
import sys
import shutil
import json
from typing import Dict, List, Any, Optional
import openai
from pathlib import Path
from lxml import etree
import os
from utils import estrai_pdf_from_xml


def get_openai_api_key_from_env():
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.strip().split("=", 1)[1]

    cwd_env = os.path.join(os.getcwd(), ".env")
    if os.path.exists(cwd_env):
        with open(cwd_env, "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.strip().split("=", 1)[1]

    print("⚠️ OPENAI_API_KEY non trovata. Imposta la variabile d'ambiente o crea un file .env nel progetto.")
    return None


def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


class InvoiceParser:
    def __init__(self, openai_api_key: str = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Estrae tutto il testo dal PDF, escludendo la prima e la seconda pagina"""
        doc = fitz.open(pdf_path)
        full_text = ""
        for page_num in range(2, doc.page_count):
            text = doc[page_num].get_text()
            full_text += f"\n--- PAGINA {page_num + 1} ---\n{text}"
        doc.close()
        return full_text

    def extract_with_ai(self, text: str) -> Dict[str, Any]:
        """Usa GPT per estrarre dati strutturati dal testo"""
        if not self.openai_client:
            raise ValueError("OpenAI API key non configurato")

        prompt = f"""
        Analizza questa fattura energetica e estrai tutte le informazioni richieste.

        ### DATI PRINCIPALI
        - numero_fattura
        - data_emissione (DD/MM/YYYY)
        - data_scadenza (DD/MM/YYYY)
        - importo_totale
        - importo_pagamento
        - pod o pdr
        - causale
        - data_inizio_periodo
        - data_fine_periodo
        - cliente
        - fornitore

        ### DETTAGLIO SERVIZI (sezioni da estrarre)
        1. Servizi di Vendita
        2. Servizi di Rete
        3. Oneri e Maggiorazioni (includendo sottosezioni come "Componenti variabili")
        4. Imposte

        Per ogni voce estrai:
        - descrizione (testo della voce)
        - unità di misura (es. €/kWh, €/Smc)
        - prezzo_unitario (numero)
        - quantita (numero, almeno 4 cifre decimali)
        - totale (numero)

        ### NOTA IVA
        Se nel testo è presente la voce “IVA 22% scissione dei pagamenti-art.17 ter DPR 633/72”,
        escludila dalle imposte e inseriscila in un campo separato "nota_iva".

        ### REGOLE
        - Inserisci i valori numerici come numeri (non stringhe).
        - Se un campo manca, metti null.
        - Includi i valori di "Oneri e Maggiorazioni" e delle loro sottosezioni (es. Componenti Variabili) in un unico array "oneri_maggiorazioni".

        Restituisci un JSON valido, senza delimitatori di codice, con questa struttura:
        {{
            "dati_fattura": {{
                "numero_fattura": null,
                "data_emissione": null,
                "data_scadenza": null,
                "importo_totale": null,
                "importo_pagamento": null,
                "pod": null,
                "pdr": null,
                "causale": null,
                "data_inizio_periodo": null,
                "data_fine_periodo": null,
                "cliente": null,
                "fornitore": null
            }},
            "servizi_vendita": [],
            "servizi_rete": [],
            "oneri_maggiorazioni": [],
            "imposte": [],
            "nota_iva": []
        }}

        TESTO FATTURA:
        {text}
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        try:
            result = json.loads(response.choices[0].message.content)
            print("✅ Estrazione AI completata con successo")
            return result
        except json.JSONDecodeError as e:
            print(f"❌ Errore parsing JSON AI: {e}")
            print(f"Risposta AI: {response.choices[0].message.content[:300]}...")
            return {}

    def parse_invoice(self, pdf_path: str) -> Dict[str, Any]:
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            raise ValueError("Nessun testo estratto dal PDF")
        return self.extract_with_ai(text)

    def crea_xml_fattura(self, dati_json: Dict[str, Any], campi_xml_estratti: Dict[str, Any], output_path="fattura_output.xml"):
        campi = dati_json["dati_fattura"]
        vendite = dati_json.get("servizi_vendita", [])
        rete = dati_json.get("servizi_rete", [])
        oneri = dati_json.get("oneri_maggiorazioni", [])
        imposte = dati_json.get("imposte", [])
        nota_iva = dati_json.get("nota_iva", [])

        header = campi_xml_estratti["header"]
        dati_generali = campi_xml_estratti["dati_generali"]
        dettaglio_linee = campi_xml_estratti["dettaglio_linee"]
        riepilogo = campi_xml_estratti["riepilogo"]
        dati_pagamento = campi_xml_estratti["dati_pagamento"]
        attachment = campi_xml_estratti["attachment"]

        nsmap = {
            "nm": "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2",
            "prx": "urn:sap.com:proxy:PR1:/1SAI/TAS34E96A2AC5E40CADB2DF:731",
            "soap-env": "http://schemas.xmlsoap.org/soap/envelope/"
        }

        root = etree.Element("FatturaElettronica", versione="FPA12", nsmap=nsmap)
        header_root = etree.fromstring(header)
        root.append(header_root)

        body = etree.SubElement(root, "FatturaElettronicaBody")
        dati_generali_root = etree.fromstring(dati_generali)
        body.append(dati_generali_root)

        beni_servizi = etree.SubElement(body, "DatiBeniServizi")

        if dettaglio_linee:
            dettaglio_linee_root = etree.fromstring(dettaglio_linee)
            beni_servizi.append(dettaglio_linee_root)

        line_counter = 1

        def add_linea(riga, descrizione_sezione):
            nonlocal line_counter
            linea = etree.SubElement(beni_servizi, "DettaglioLinee")
            etree.SubElement(linea, "NumeroLinea").text = str(line_counter)
            etree.SubElement(linea, "Descrizione").text = riga.get("descrizione", descrizione_sezione)
            etree.SubElement(linea, "Quantita").text = str(riga.get("quantita", "0.0000"))
            etree.SubElement(linea, "UnitaMisura").text = riga.get("unita_misura", "")
            etree.SubElement(linea, "DataInizioPeriodo").text = campi.get("data_inizio_periodo", "")
            etree.SubElement(linea, "DataFinePeriodo").text = campi.get("data_fine_periodo", "")
            etree.SubElement(linea, "PrezzoUnitario").text = str(riga.get("prezzo_unitario", 0.0))
            etree.SubElement(linea, "PrezzoTotale").text = str(riga.get("totale", 0.0))
            etree.SubElement(linea, "AliquotaIVA").text = "0.00"
            line_counter += 1

        for gruppo, nome in [(vendite, "Servizi di Vendita"), (rete, "Servizi di Rete"), (oneri, "Oneri e Maggiorazioni"), (imposte, "Imposte")]:
            for riga in gruppo:
                add_linea(riga, nome)

        for riga in nota_iva:
            add_linea(riga, "Nota IVA")

        riepilogo_root = etree.fromstring(riepilogo)
        beni_servizi.append(riepilogo_root)

        dati_pagamento_root = etree.fromstring(dati_pagamento)
        body.append(dati_pagamento_root)

        attachment_root = etree.fromstring(attachment)
        body.append(attachment_root)

        etree.ElementTree(root).write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    def process_batch(self, data_folder: str, output_folder: str) -> List[str]:
        xml_folder = os.path.join(data_folder, "xml_files")
        pdf_folder = os.path.join(data_folder, "pdf_converted")

        if not os.path.exists(xml_folder):
            raise FileNotFoundError(f"Cartella XML non trovata: {xml_folder}")
        os.makedirs(output_folder, exist_ok=True)

        xml_files = list(Path(xml_folder).glob("*.xml"))
        if not xml_files:
            raise ValueError("Nessun file XML trovato nella cartella specificata.")
        print(f"📂 Trovati {len(xml_files)} file XML da elaborare nella cartella: {xml_folder}")

        total_files = len(xml_files)
        for idx, xml_file in enumerate(xml_files, start=1):
            print(f"🔄 [{idx}/{total_files}] Elaborazione file: {xml_file.name}")
            field_xml, path_pdf = estrai_pdf_from_xml(str(xml_file), pdf_folder)
            data = parser.parse_invoice(path_pdf)
            output_path = f"{output_folder}/{xml_file.stem}_{Path(path_pdf).stem}_converted.xml"
            parser.crea_xml_fattura(data, field_xml, str(output_path))
            print(f"✅ [{idx}/{total_files}] XML generato: {output_path}")


if __name__ == "__main__":
    BASE_DIR = get_base_path()
    DATA_DIR = os.path.join(BASE_DIR, "data")
    PDF_CONVERTED_DIR = os.path.join(DATA_DIR, "pdf_converted")
    OUTPUT_DIR = os.path.join(DATA_DIR, "output")

    for folder in [PDF_CONVERTED_DIR, OUTPUT_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

    api_key = get_openai_api_key_from_env()
    parser = InvoiceParser(openai_api_key=api_key)
    parser.process_batch(DATA_DIR, OUTPUT_DIR)
