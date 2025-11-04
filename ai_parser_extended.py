import os
import fitz
import re
import shutil
import json
from pathlib import Path
from copy import deepcopy
from typing import Dict, List, Any, Tuple
from lxml import etree

from ai_parser import InvoiceParser, get_base_path, get_openai_api_key_from_env
from utils import estrai_pdf_from_xml


def aggiorna_pod_pdr_in_field_xml(field_xml: Dict[str, Any], codice: str) -> Dict[str, Any]:
    """
    Aggiorna solo il campo <RiferimentoTesto> relativo al Pod/Pdr
    senza modificare altri tipi di dato (es. ODA) nel dettaglio_linee.
    """
    updated_xml = deepcopy(field_xml)  # Non modificare l'originale
    
    dettaglio_linee = updated_xml.get("dettaglio_linee", "")
    
    # Regex per trovare <AltriDatiGestionali> con TipoDato Pod/Pdr
    pattern = r"(<AltriDatiGestionali>\s*<TipoDato>Pod/Pdr</TipoDato>\s*<RiferimentoTesto>)(.*?)(</RiferimentoTesto>\s*</AltriDatiGestionali>)"
    
    # Sostituisce solo il valore del Pod/Pdr
    dettaglio_linee = re.sub(pattern, fr"\1{codice}\3", dettaglio_linee, flags=re.DOTALL)
    
    updated_xml["dettaglio_linee"] = dettaglio_linee
    return updated_xml

class MultiPODInvoiceParser(InvoiceParser):

    def group_pages_by_pod(self, pdf_path: str) -> List[Tuple[str, str]]:
        """
        Raggruppa le sezioni del PDF corrispondenti a ciascun POD o PDR.
        Ogni sezione inizia da 'Numero fattura elettronica valida ai fini fiscali'
        e contiene almeno un POD (energia elettrica) o PDR (gas naturale).

        Ritorna una lista di tuple (codice, testo_della_fattura).
        """
        pod_pattern = r"POD\s*\(Punto\s+di\s+prelievo\)\s*:\s*(IT[0-9A-Z]{12,15})"
        pdr_pattern = r"PDR\s*\(Punto\s+di\s+riconsegna\)\s*:\s*([0-9]{11,14})"
        factura_start_pattern = r"Numero fattura elettronica valida ai fini fiscali"

        print(f"\n📄 Analisi del file PDF: {Path(pdf_path).name}")

        doc = fitz.open(pdf_path)
        try:
            full_text = ""
            for page_num in range(doc.page_count):
                text = doc[page_num].get_text("text")
                full_text += f"\n--- PAGINA {page_num + 1} ---\n{text}"

            print(f"📑 Documento con {doc.page_count} pagine analizzato.")

            sections = re.split(factura_start_pattern, full_text)
            results = []

            for i in range(1, len(sections)):
                section_text = (
                    "Numero fattura elettronica valida ai fini fiscali" + sections[i]
                )

                pod_match = re.search(pod_pattern, section_text)
                pdr_match = re.search(pdr_pattern, section_text)

                if pod_match:
                    code = pod_match.group(1)
                    code_type = "POD"
                elif pdr_match:
                    code = pdr_match.group(1)
                    code_type = "PDR"
                else:
                    alt_match = re.search(r"\b(IT[0-9A-Z]{12,15}|[0-9]{11,14})\b", section_text)
                    code = alt_match.group(1) if alt_match else f"UNKNOWN_{i}"
                    code_type = "UNKNOWN"

                results.append((f"{code_type}_{code}", section_text.strip()))

            if not results:
                print("⚠️ Nessuna sezione POD/PDR individuata.")
                return [("UNKNOWN", full_text)]

            print(f"✅ Trovate {len(results)} sezioni: {', '.join(p for p, _ in results)}")
            return results
        finally:
            doc.close()


    def parse_and_generate_per_pod(
        self, pdf_path: str, field_xml: Dict[str, Any], output_dir: str, xml_name: str
    ) -> List[str]:
        """
        Estrae e genera un XML per ogni POD/PDR trovato nel PDF, salvandolo subito.
        """
        pod_sections = self.group_pages_by_pod(pdf_path)
        generated_files = []

        for idx, (pod_code, pod_text) in enumerate(pod_sections, start=1):
            print(f"\n🔍 [{idx}/{len(pod_sections)}] Rilevato: {pod_code}")

            try:
                print(f"🧠 Estrazione AI per {pod_code}...")
                if pod_code.startswith("POD_"):
                    pod_corrente = pod_code.replace("POD_", "")
                    field_xml = aggiorna_pod_pdr_in_field_xml(field_xml, pod_corrente)
                elif pod_code.startswith("PDR_"):
                    pdr_corrente = pod_code.replace("PDR_", "")
                    field_xml = aggiorna_pod_pdr_in_field_xml(field_xml, pdr_corrente)
                else:
                    pod_corrente = None
                    pdr_corrente = None
                    print(f"❌ Errore durante l'aggiustamento del numero di POD/PDR")
                
                ##DEBUG CAMBIO DEL POD/PDR OGNI ITERAZIONE

                # debug_dir = os.path.join(output_dir, "_debug")
                # os.makedirs(debug_dir, exist_ok=True)
                # with open(os.path.join(debug_dir, "field_xml.json"), "w", encoding="utf-8") as f:
                #     json.dump(field_xml, f, indent=2, ensure_ascii=False)
                
                # print("DEBUG salvato")
                    
                data_ai = self.extract_with_ai(pod_text)

                # Stampa dei dati estratti
                print("🔹 Dati estratti AI:")
                print(json.dumps(data_ai, indent=2, ensure_ascii=False))
                # Mantieni l'identificativo per riferimento interno
                if isinstance(data_ai, dict) and data_ai.get("dati_fattura"):
                    data_ai["dati_fattura"]["identificativo"] = pod_code

                safe_pod = re.sub(r"[^A-Za-z0-9]+", "_", pod_code)
                xml_out_path = os.path.join(output_dir, f"{safe_pod}_converted.xml")  #---> {xml_name}_{safe_pod}_converted.xml  (per avere anche l'xml di riferimento)

                print(f"💾 Generazione XML per {pod_code} → {Path(xml_out_path).name}")
                self.crea_xml_fattura(data_ai, field_xml, xml_out_path)
                generated_files.append(xml_out_path)

                print(f"✅ XML generato con successo per {pod_code}")
            except Exception as exc:
                print(f"❌ Errore durante la generazione per {pod_code}: {exc}")

        return generated_files

def process_batch_multi(data_folder: str, output_root: str) -> List[str]:
    """
    Elabora tutti gli XML presenti in `data/xml_multi_pod`,
    estrae il PDF allegato e genera un file XML per ciascun POD/PDR trovato nel PDF.
    """
    xml_files = list(Path(data_folder).glob("*.xml"))
    if not xml_files:
        raise ValueError(f"Nessun file XML trovato in: {data_folder}")

    api_key = get_openai_api_key_from_env()
    parser = MultiPODInvoiceParser(openai_api_key=api_key)
    generated_paths: List[str] = []

    print(f"\n📂 Trovati {len(xml_files)} file XML nella cartella {data_folder}")

    for idx, xml_file in enumerate(xml_files, start=1):
        print(f"\n============================")
        print(f"🔄 [{idx}/{len(xml_files)}] Elaborazione: {xml_file.name}")
        print(f"============================")

        # Estrai PDF associato a questo XML
        field_xml, path_pdf = estrai_pdf_from_xml(str(xml_file), output_root)

        xml_name = Path(xml_file).stem
        pdf_name = Path(path_pdf).stem
        xml_output_dir = os.path.join(output_root, xml_name)
        os.makedirs(xml_output_dir, exist_ok=True)

        # Sposta e rinomina PDF accanto agli XML generati
        pdf_final_name = f"{pdf_name}_{xml_name}.pdf"
        pdf_final_path = os.path.join(xml_output_dir, pdf_final_name)
        shutil.move(path_pdf, pdf_final_path)
        print(f"📎 PDF estratto e salvato come: {pdf_final_path}")

        # Parsing e generazione XML per ogni POD/PDR
        pod_generated = parser.parse_and_generate_per_pod(
            pdf_final_path, field_xml, xml_output_dir, xml_name
        )

        generated_paths.extend(pod_generated)

    print(f"\n📦 Completato! Totale XML generati: {len(generated_paths)}")
    return generated_paths


if __name__ == "__main__":
    BASE_DIR = get_base_path()
    DATA_DIR = os.path.join(BASE_DIR, "data", "xml_multi_pod")
    OUTPUT_DIR = os.path.join(DATA_DIR, "output")

    # Pulizia cartella output
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("🚀 Avvio elaborazione multipod completa...")
    generated = process_batch_multi(DATA_DIR, OUTPUT_DIR)
    print(json.dumps({"generated": generated}, indent=2, ensure_ascii=False))
    print("🏁 Fine elaborazione.")


