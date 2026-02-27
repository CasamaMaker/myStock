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








part_numbers = [
    "863-NGTB40N120FL2WG",
    "968-2SK1317-E",
    "511-STB37N60DM2AG",
    "511-TIP32C",
    "511-TIP31C",
    "863-SBC856BWT1G",
    "579-PIC12F683-E/MF",
    "579-PIC12F675-I/SN",
    "579-PIC18F4550T-I/ML",
    "579-PIC16F628-04E/SO",
    "556-ATMEGA328P-AU",
    "926-LM317MDT/NOPB",
    "512-1N4148",
    "579-MCP4726A0TECH",
    "919-RD-1205D",
    "863-AFGB30T65SQDN",
    "595-L293NEE4",
    "595-ISO7720QDWRQ1",
    "584-ADUM5402WCRWZ-1",
    "634-SI8235BD-C-IS",
    "511-LM2904YST",
    "78-SQS460EN-T1_GE3",
    "595-UCC27424QDGNRQ1",
    "78-SQ7414AEN-T1_GE3",
    "630-ASSR-601JT-000E",
    "926-C128S022CIMTNOPB",
    "700-MAX15006AASA",
    "511-STY145N65M5",
    "603-XP3N5R0M",
    "595-TPS40210QDGQRQ1",
    "700-MAX11080GUU/V+",
    "781-SQ4840EY-GE3",
    "209-IE0512D",
    "209-IK0515SA",
    "580-NCS3S1212SC",
    "781-SI2312BDS-T1-GE3",
    "994-MSS1210-103MEB",
    "963-NR6045T1R0N",
    "863-SBC856BWT1G",
    "179-SLW-913535-2ASMT",
    "512-1N4148",
    "815-PRO-OB-536",
    "595-UCC27524AQDGNRQ1",
    "81-LQP03TN2N7C02D",
    "78-BZX84C18-HE3-08",
    "78-VS-25TTS12SLHM3",
    "942-AUIPS2031R",
    "579-93LC46BISN",
    "863-SBC856BWT1G",
    "78-SQ2318AES-T1_GE3",
    "595-LM2904BAQDRQ1",
    "595-DCP020515DP",
    "942-IRS2302SPBF",
    "942-AUIPS1011R",
    "771-BZX84-A20,215",
    "863-MMBZ27VALT1G",
    "78-SMBJ33CAHE3_A/H",
    "78-SMBJ36CAHE3_A/H",
    "595-PS3813K33QDBVRQ1",
    "595-PS3808G33QDBVRQ1",
    "755-RSS070P05HZGTB",
    "757-SSM3K15FLF",
    "755-QS6K1FRATR",
    "757-SSM3J15FULF",
    "942-IRFS7437TRLPBF",
    "863-NVHL082N65S3F",
    "726-IPD50P04P4L-11",
    "356-ESP32-C3-MINI1H4",
    "595-DRV8300NPWR",
    "726-IPD90N04S403ATMA",
    "209-IZB0312S15"
]

print(">> BUSCA en Mouser << "+"="*80 + "\n")
for part in part_numbers:

    if part.strip() == "":
        print("")
        time.sleep(2)
        continue
    component_mouser = get_mouser_data(part)
    if component_mouser is None:
        continue


    for key, value in component_mouser.items():
        if key == "manufacturer":
            print(value)
            time.sleep(2)

print("="*80 + "\n")










# part_numbers = [
#     "1175073",
#     "2164804",
#     "1459052",
#     "1902435",
#     "2576227",
#     "3581533",
#     "2083914",
#     "1209558",
#     "2777520",
#     "2575185",
#     "2463634",
#     "1773494",
#     "1793830",
#     "1256513",
#     "1256511",
#     "1011407",
#     "1011408",
#     "1011410"
# ]

# print(">> BUSCA en farnell << "+"="*80 + "\n")
# for part in part_numbers:

#     if part.strip() == "":
#         print("")
#         time.sleep(2.4)
#         continue
#     component_farnell = get_farnell_by_sku(part)
#     if component_farnell is None:
#         continue
# # OEG - TE CONNECTIVITY - PCH-112D2H,000 - RELÉ, SPDT, 250VAC, 30VDC, 5A
# # NXP - NCX2200GW,125 - Comparador Analógico, Raíl a Raíl, Bajo Voltaje, 1 Canales, 0.8 µs, 1.3V a 5.5V, TSSOP, 5 Pines

#     for key, value in component_farnell.items():
#         if key == "store":
#             print(value)
#             # if "-" in part:
#             #     print("".join(value.split("-")[5:]))
#             # else:
#             #     print("".join(value.split("-")[2:]))
#             time.sleep(2.4)


# print("="*80 + "\n")








# part_numbers = [
#     "C24497",
#     "C12891",
#     "C125975",
#     "C1848",
#     "C316025",
#     "C364262",
#     "C8062",
#     "C8678",
#     "C68434",
#     "C169385",
#     "C83438",
#     "C434439",
#     "C351397",
#     "C351399",
#     "C2831713",
#     "C189606",
#     "C123399",
#     "C273567",
#     "C908270",
#     "C474932",
#     "C370899",
#     "C192046",
#     "C668208",
#     "C66649",
#     "C61299",
#     "C9220",
#     "C2586",
#     "C189617",
#     "C118173",
#     "C474892",
#     "C527089",
#     "C2681245",
#     "C474906",
#     "C2838500",
#     "C13585",
#     "C1883",
#     "C492011",
#     "C344010",
#     "C221666",
#     "C352826",
#     "C2932326",
#     "C469386",
#     "C2912101",
#     "C2927038",
#     "C2933016",
#     "C424093",
#     "C621388",
#     "C965555",
#     "C293767",
#     "C2858491",
#     "C92755",
#     "C466623",
#     "C237172",
#     "C161520",
#     "C2892576",
#     "C2885781",
#     "C2927799",
#     "C3029469",
#     "C248765",
#     "C351421",
#     "C332100",
#     "C181151",
#     "C175347",
#     "C3021093",
#     "C16581",
#     "C72522",
#     "C3029467",
#     "C40958",
#     "C2901097",
#     "C112239",
#     "C2040",
#     "C97521",
#     "C1846",
#     "C94790",
#     "C1912",
#     "C2890597",
#     "C369108",
#     "C2561",
#     "C96093",
#     "C492610",
#     "C526013",
#     "C2847576",
#     "C97244",
#     "C338756",
#     "C2843949",
#     "C2693628",
#     "C10681",
#     "C9932",
#     "C2915633",
#     "C918114",
#     "C2960",
#     "C193969",
#     "C73332",
#     "C9055",
#     "C2345",
#     "C5186847",
#     "C26032",
#     "C2907531",
#     "C17944",
#     "C75582",
#     "C5189823",
#     "C86061",
#     "C1565",
#     "C5884119",
#     "C910991",
#     "C90191",
#     "C2933019",
#     "C137860",
#     "C60491",
#     "C91145",
#     "C79140",
#     "C33149",
#     "C108901",
#     "C99395",
#     "C25782",
#     "C60133",
#     "C77020",
#     "C106201",
#     "C1518208",
#     "C106862",
#     "C6119813",
#     "C107174",
#     "C143789",
#     "C383211",
#     "C1974234",
#     "C5128191",
#     "C25762",
#     "C137934",
#     "C137992",
#     "C114764",
#     "C163478",
#     "C5581335",
#     "C60488",
#     "C51205",
#     "C14663",
#     "C114928",
#     "C434068",
#     "C2942490",
#     "C66886",
#     "C82544",
#     "C118141",
#     "C2913198",
#     "C964632",
#     "C32346",
#     "C9010",
#     "C82601",
#     "C49851",
#     "C7470",
#     "C2864583",
#     "C22463851",
#     "C2933103",
#     "C7418879",
#     "C304572",
#     "C2909320",
#     "C321557",
#     "C2906920",
#     "C273341",
#     "C163489",
#     "C2906952",
#     "C2906901",
#     "C9807",
#     "C29266",
#     "C7432791",
#     "C249849",
#     "C6119795",
#     "C77177",
#     "C106208",
#     "C114425",
#     "C41368784",
#     "C46956580",
#     "C6916223",
#     "C18623826",
#     "C7431441",
#     "C152364",
#     "C393074",
#     "C46961752",
#     "C393070",
#     "C2933087",
#     "C25765",
#     "C2909315",
#     "C393949",
#     "C404027",
#     "C7519"
# ]

# print(">> BUSCA en lcsc << "+"="*80 + "\n")
# for part in part_numbers:

#     if part.strip() == "":
#         print("")
#         # time.sleep(0.1)
#         continue
#     component_lcsc = get_lcsc_data(part)
#     if component_lcsc is None:
#         continue
# # OEG - TE CONNECTIVITY - PCH-112D2H,000 - RELÉ, SPDT, 250VAC, 30VDC, 5A
# # NXP - NCX2200GW,125 - Comparador Analógico, Raíl a Raíl, Bajo Voltaje, 1 Canales, 0.8 µs, 1.3V a 5.5V, TSSOP, 5 Pines

#     for key, value in component_lcsc.items():
#         if key == "store":
#             print(value)
#             # time.sleep(0.1)


# print("="*80 + "\n")