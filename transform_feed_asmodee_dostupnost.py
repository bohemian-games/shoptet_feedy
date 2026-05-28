#!/usr/bin/env python3

import os
import xml.etree.ElementTree as ET

# cesta ke složce, kde leží tento .py soubor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# vstupní XML soubor ve stejné složce
input_xml = os.path.join(BASE_DIR, "adc-dostupnost.xml")

# výstupní XML soubor
output_xml = os.path.join(BASE_DIR, "shoptet_feed_asmodee_dostupnost.xml")

# načtení XML
tree = ET.parse(input_xml)
root = tree.getroot()

# přejmenování kořenového tagu <sklad> → <SHOP> a odstranění atributů
root.tag = "SHOP"
root.attrib.clear()


def transform_products(elem):
    """Transformace struktury produktů pro Shoptet."""
    for prod in list(elem.findall(".//produkt")):

        # <produkt> → <SHOPITEM>
        prod.tag = "SHOPITEM"

        # <cislo> → <EXTERNAL_CODE>
        code = prod.find("cislo")
        if code is not None:
            code.tag = "EXTERNAL_CODE"

        # <ean> → <EAN>
        ean = prod.find("ean")
        if ean is not None:
            ean.tag = "EAN"

        # dostupnost
        dostup = prod.find("dostupnost")
        if dostup is not None:
            try:
                count = int(dostup.text.strip())
            except:
                count = 0

            prod.remove(dostup)

            out = ET.Element("AVAILABILITY_OUT_OF_STOCK")
            instock = ET.Element("AVAILABILITY_IN_STOCK")
            neg = ET.Element("NEGATIVE_AMOUNT")

            if count > 0:
                out.text = "Skladem u dodavatele"
                instock.text = "Skladem"
                neg.text = "1"   # povolit záporný stav
            else:
                out.text = "Vyprodáno"
                instock.text = "Skladem"
                neg.text = "0"   # nepovolit záporný stav

            prod.append(out)
            prod.append(instock)
            prod.append(neg)

def remove_items_without_ean(elem):
    """Odstraní celé SHOPITEM, pokud EAN chybí nebo je prázdný."""
    for parent in elem.findall(".//SHOPITEM/.."):
        for item in list(parent):
            if item.tag != "SHOPITEM":
                continue

            ean = item.find("EAN")
            if ean is None or not ean.text or not ean.text.strip():
                parent.remove(item)


def indent(elem, level=0):
    """Odsazení XML pro čitelnost."""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


# provedení transformace
transform_products(root)
remove_items_without_ean(root)
indent(root)

# uložení výsledku
tree.write(output_xml, encoding="utf-8", xml_declaration=True)

print("Hotovo – shoptet_feed_Asmodee_Dostupnost.xml vygenerován.")
