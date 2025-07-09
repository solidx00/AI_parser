import base64
from lxml import etree
import os
import re

def estrai_pdf_from_xml(xml_file: str, output_dir: str) -> dict:
    """
    Estrae PDF e porzioni specifiche del contenuto XML:
    - Tutto fino a </FatturaElettronicaHeader>
    - Tutto da <DatiRiepilogo> in poi, incluso Allegati

    Args:
        xml_file (str): path to the XML file.
        output_dir (str): path where the PDF attachment will be saved.

    Returns:
        Dict: Un dizionario contenente le sezioni estratte
    """
    
    field = {}
    
    with open(xml_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Estrai la parte <FatturaElettronicaHeader>
    match_header = re.search(r"(<FatturaElettronicaHeader>.*?</FatturaElettronicaHeader>)", content, re.DOTALL)
    header = match_header.group(1) if match_header else ""
    
    # Estrai la parte fino al tag di chiusura <DatiGenerali>
    match_generali = re.search(r"(<DatiGenerali>.*?</DatiGenerali>)", content, re.DOTALL)
    dati_generali = match_generali.group(1) if match_generali else ""

    # Trova la sezione <DettaglioLinee>
    match_dettaglio_linee = re.search(r"(<DettaglioLinee>.*?</DettaglioLinee>)", content, re.DOTALL)
    dettaglio_linee = match_dettaglio_linee.group(1) if match_dettaglio_linee else ""

    # Sostituisci i valori di <PrezzoUnitario> e <PrezzoTotale> con 0
    if dettaglio_linee:
        dettaglio_linee = re.sub(r"<PrezzoUnitario>.*?</PrezzoUnitario>", "<PrezzoUnitario>0</PrezzoUnitario>", dettaglio_linee)
        dettaglio_linee = re.sub(r"<PrezzoTotale>.*?</PrezzoTotale>", "<PrezzoTotale>0</PrezzoTotale>", dettaglio_linee)

    # Estrai la parte da <DatiRiepilogo> fino alla fine
    match_riepilogo = re.search(r"(<DatiRiepilogo>.*?</DatiRiepilogo>)", content, re.DOTALL)
    riepilogo = match_riepilogo.group(1) if match_riepilogo else ""
    
    # Estrai la parte da <DatiPagamento> fino alla fine
    match_pagamento = re.search(r"(<DatiPagamento>.*?</DatiPagamento>)", content, re.DOTALL)
    dati_pagamento = match_pagamento.group(1) if match_pagamento else ""
    
    # Estrai la parte <Allegati> e tutto il suo contenuto
    match_allegato = re.search(r"(<Allegati>.*?</Allegati>)", content, re.DOTALL)
    attachment = match_allegato.group(1) if match_allegato else ""

    # Parsing XML per estrazione e salvataggio attachment
    tree = etree.parse(xml_file)
    allegati = tree.findall(".//Allegati")
    for i, allegato in enumerate(allegati):
        nome = allegato.findtext("NomeAttachment") or f"attachment_{i + 1}.pdf"
        contenuto_base64 = allegato.findtext("Attachment")
        if contenuto_base64:
            numero_fattura = nome.split("_")[0]
            nuovo_nome = f"{numero_fattura}.pdf"
            output_path = os.path.join(output_dir, nuovo_nome)
            print(f"📄 Elaborazione allegato: {nuovo_nome}")
            with open(output_path, "wb") as f_out:
                f_out.write(base64.b64decode(contenuto_base64))
            print(f"✅ Salvato allegato: {output_path}")
        else:
            print(f"❌ Attachment non trovato o vuoto in {xml_file}.")

    # Combinazione dei dati estratti
    field["header"] = header
    field["dati_generali"] = dati_generali
    field["dettaglio_linee"] = dettaglio_linee
    field["riepilogo"] = riepilogo
    field["dati_pagamento"] = dati_pagamento
    field["attachment"] = attachment

    return field, output_path

if __name__ == "__main__":
    xml_path = "/Users/francescociteroni/Documents/Progetti/AI_parser/data/xml_files/IT02221101203_kBuOH.xml"
    output_dir = "/Users/francescociteroni/Documents/Progetti/AI_parser/output"
    result, pdf_path = estrai_pdf_from_xml(xml_path, output_dir)
    print("Sezioni estratte:")
    for k, v in result.items():
        print(f"{k}: {v[:500]}...")  # Mostra solo i primi 500 caratteri per brevità
    print(f"PDF salvato in: {pdf_path}")