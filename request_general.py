from request_farnell import get_farnell_by_sku
from request_lcsc import get_lcsc_data
from request_mouser import get_mouser_data

# print("="*80 + "\n")
# component_mouser = get_mouser_data("AE1206BR-0710KL")     # AE1206BR-0710KL         815-AANI-CH-0068-T
# # for key, value in component_mouser.items():
# #     print(f"{key}: {value}")
# print(f"> {component_mouser['name']}: {component_mouser['description']}")

# # print("="*80 + "\n")
# component_farnell = get_farnell_by_sku("2988437")       #2988437       2323924   1236670
# # for key, value in component_farnell.items():
# #     print(f"{key}: {value}")
# print(f"> {component_farnell['name']}: {component_farnell['description']}")

# # print("="*80 + "\n")
# component_lcsc = get_lcsc_data("C17902")      #C17902         C2980306
# # for key, value in component_lcsc.items():
# #     print(f"{key}: {value}")
# print(f"> {component_lcsc['name']}: {component_lcsc['description']}")





import re
import time


def detect_supplier(code: str) -> str:
    code = code.strip().upper()

    # LCSC → C + números
    if re.fullmatch(r"C\d+", code):
        return "lcsc"

    # Farnell → només números (6-8 dígits habitualment)
    if re.fullmatch(r"\d{6,8}", code):
        return "farnell"

    # Mouser → la resta (MPN o format amb guions)
    return "mouser"

def get_component(code: str):
    supplier = detect_supplier(code)

    if supplier == "mouser":
        return get_mouser_data(code)

    elif supplier == "farnell":
        return get_farnell_by_sku(code)

    elif supplier == "lcsc":
        return get_lcsc_data(code)

    else:
        raise ValueError("Proveïdor desconegut")


# component = get_component("2988437")
# print(f"> {component['name']}: {component['description']}")


# for codi in part_numbers:
#     component = get_component(codi)

#     if component is not None:
#         print(f"> {component['name']}: {component['store_name']}")
#     # else:
#     #     print(f"> {codi}: NO TROBAT")


def parse_barcode(data: str) -> dict:
    data = data.strip()
    
    # -------- LCSC --------
    if data.startswith("{") and "pbn:" in data:
        # Eliminem claus {}
        content = data.strip("{}")
        fields = content.split(",")

        result = {"supplier": "LCSC"}
        for field in fields:
            if ":" in field:
                key, value = field.split(":", 1)
                result[key.strip()] = value.strip()

        return {
            "supplier": "LCSC",
            "order_number": result.get("on"),
            "part_number": result.get("pm"),
            "sku": result.get("pc"),
            "quantity": result.get("qty"),
        }

    # -------- Mouser --------
    if data.startswith(">[)>"):
        parts = data.split("\x1d")

        result = {"supplier": "Mouser"}

        for part in parts:
            if part.startswith("K"):          # Mouser order
                result["order_number"] = part[1:]
            elif part.startswith("1P"):       # Part number
                result["part_number"] = part[2:]
            elif part.startswith("Q"):        # Quantity
                result["quantity"] = part[1:]
            elif part.startswith("4L"):       # Lot / location
                result["lot"] = part[2:]

        return result

    return {"supplier": "Unknown", "raw": data}


# print("="*80 + "\n")
# codi1 = parse_barcode(">[)>06K1167277914K0151PRN60D3920FB14Q411K0434158114LUS")
# for key, value in codi1.items():
#     # print(f"{key}: {value}")
#     if key == "part_number":
#         component_mouser = get_mouser_data(value)     # AE1206BR-0710KL         815-AANI-CH-0068-T
#         # for key, value in component_mouser.items():
#         #     print(f"{key}: {value}")
#         print(f"> {component_mouser['name']} [{component_mouser['store_name']}]: {component_mouser['description']}")

# print("="*80 + "\n")
# codi2 = parse_barcode("{pbn:PICK2107030009,on:SO2106299988,pc:C621425,pm:LAN8742AI-CZ-TR,qty:200,mc:,cc:1,pdi:44710295}")
# for key, value in codi2.items():
#     # print(f"{key}: {value}")
#     if key == "sku":
#         component_lcsc = get_lcsc_data(value)      #C17902         C2980306
#         # for key, value in component_lcsc.items():
#         #     print(f"{key}: {value}")
#         print(f"> {component_lcsc['name']} [{component_lcsc['store_name']}]: {component_lcsc['description']}")








# part_numbers = [
#     "NGT B40N120FL2WG",
#     "2SK1317-E",
#     "STB37N60DM2AG",
#     "TIP32C",
#     "TIP31C",
#     "SBC856BWT1G",
#     "PIC12F683",
#     "PIC12F675",
#     "PIC18F4550",
#     "PIC16F628",
#     "ATMEGA8A",
#     "ATMEGA328P-AU",
#     "LM317",
#     "TL785",
#     "1N4148",
#     "MCP4726A0T-E/CH",
#     "RD-1205D",
#     "AFGB30T65SQDN",
#     "L293",
#     "ISO7720QDWRQ1",
#     "ADUM5402WCRWZ-1",
#     "SI8235BD-C-IS",
#     "LM2904YST",
#     "SQS460EN-T1_GE3",
#     "UCC27424QDGNRQ1",
#     "SQ7414AEN-T1_GE3",
#     "ASSR-601JT-000E",
#     "ADC128S022CIMT/NOPB",
#     "MAX15006AASA+",
#     "STY145N65M5",
#     "XP3N5R0M",
#     "TPS40210QDGQRQ1",
#     "MAX11080GUU/V+",
#     "SQ4840EY-T1-GE3",
#     "IE0512D",
#     "IK0515SA",
#     "NCS3S1212SC",
#     "SI2312BDS-T1-GE3",
#     "MSS1210-103MEB",
#     "NR6045T1R0N",
#     "SBC856BWT1G",
#     " ",
#     "1N4148",
#     "815-PRO-OB-536",
#     "UCC27524AQDGNRQ1",
#     " ",
#     "BZX84C18-HE3-08",
#     "VS-25TTS12SLHM3",
#     "AUIPS2031R",
#     "93LC46B-I/SN",
#     "SBC856BWT1G",
#     "SQ2318AES-T1_GE3",
#     "LM2904BAQDRQ1",
#     "DCP020515DP",
#     "IRS2302SPBF",
#     "AUIPS1011R",
#     "BZX84-A20,215",
#     "MMBZ27VALT1G",
#     "SMBJ33CAHE3_A/H",
#     "SMBJ36CAHE3_A/",
#     "TPS3813K33QDBVRQ1",
#     "TPS3808G33QDBVRQ1",
#     "RSS070P05HZGTB",
#     "SSM3K15F,LF",
#     "QS6K1FRATR",
#     "SSM3J15FU,LF",
#     "IRFS7437TRLPBF",
#     "NVHL082N65S3F",
#     "IPD50P04P4L-11",
#     "ESP32-C3-MINI-1-H4",
#     "DRV8300NPWR",
#     "IPD90N04S403ATMA1",
#     " ",
#     "IZB0312S15"
# ]

# print(">> BUSCA SUPPLIER NAME en Mouser << "+"="*80 + "\n")
# for part in part_numbers:

#     if part.strip() == "":
#         print("")
#         time.sleep(2)
#         continue
#     component_mouser = get_mouser_data(part)
#     if component_mouser is None:
#         continue


#     for key, value in component_mouser.items():
#         if key == "store_name":
#             print(value)
#             time.sleep(2)

# print("="*80 + "\n")





part_numbers = [
    "1175073",
    "2164804",
    "1459052",
    "1902435",
    "2576227",
    "3581533",
    "2083914",
    "1209558",
    "2777520",
    "2575185",
    "2463634",
    "1773494",
    "1793830",
    "1256513",
    "1256511",
    "1011407",
    "1011408",
    "1011410"
]

print(">> BUSCA DESCRIPTION en farnell << "+"="*80 + "\n")
for part in part_numbers:

    if part.strip() == "":
        print("")
        time.sleep(2)
        continue
    component_farnell = get_farnell_by_sku(part)
    if component_farnell is None:
        continue
# OEG - TE CONNECTIVITY - PCH-112D2H,000 - RELÉ, SPDT, 250VAC, 30VDC, 5A
# NXP - NCX2200GW,125 - Comparador Analógico, Raíl a Raíl, Bajo Voltaje, 1 Canales, 0.8 µs, 1.3V a 5.5V, TSSOP, 5 Pines

    for key, value in component_farnell.items():
        if key == "description":
            # print(value)
            if "-" in part:
                print("".join(value.split("-")[5:]))
            else:
                print("".join(value.split("-")[2:]))
            time.sleep(2)


print("="*80 + "\n")