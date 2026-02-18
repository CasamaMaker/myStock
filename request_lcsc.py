import requests
import json

def get_lcsc_data(part_number):
    # url = "https://wmsc.lcsc.com/wmsc/product/detail"
    url = "https://wmsc.lcsc.com/ftps/wm/product/detail"
    params = {"productCode": part_number}
    
    # Headers més complets per simular un navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,ca;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.lcsc.com/",
        "Origin": "https://www.lcsc.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    
    # Construir URL completa per mostrar-la
    full_url = f"{url}?productCode={part_number}"

    # print(f"🔍 Cercant codi: {part_number} a LCSC\n")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        # print(f"📡 RESPOSTA HTTP:")
        # print(f"   Status Code: {response.status_code}")
        # print(f"   Reason: {response.reason}")
        # print(f"   Headers: {dict(response.headers)}")
        # print("="*80)
        # print()
        
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de connexió: {e}")
        return None
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"❌ Error descodificant JSON: {e}")
        print(f"Contingut rebut: {response.text[:500]}")
        return None
    
    if data.get("code") != 200 or not data.get("result"):
        print(f"❌ Resposta no vàlida:")
        print(f"   Code: {data.get('code')}")
        print(f"   Message: {data.get('msg', 'Error desconegut')}")
        print(f"   OK: {data.get('ok')}")
        return None
    
    product = data["result"]

    component = {}
    component["name"] = product.get('productModel')
    component["store_name"] = product.get('productCode')
    component["description"] = product.get('productNameEn')
    component["type2"] = product.get('catalogName')
    component["manufacturer"] = product.get('brandNameEn') 
    component["package"] = product.get('encapStandard') 
    component["datasheet"] = product.get('pdfUrl')
    component["store"] = f"https://www.lcsc.com/product-detail/{part_number}.html"
    component["image"] = product.get('productImages')
    # component["price_unit"] = product.get('productPriceList')
    component["store_availability"] = product.get('stockNumber')

    price_list = product.get("productPriceList", [])
    filtered_prices = []

    for price_tier in price_list:
        qty = price_tier.get("ladder")
        if isinstance(qty, (int, float)) and qty <= 100:
        # if qty <= 100:  # Només fins a 100 unitats
            filtered_prices.append({
                "quantity": qty,
                "price": price_tier.get("productPrice")
            })

    component["price_unit"] = filtered_prices
    
    # print("✅ Component trobat!\n")
    # return product
    return component


def search_by_mpn(mpn):
    
    url = "https://wmsc.lcsc.com/ftps/wm/search/global"
    params = {
        "keyword": mpn,
        "currentPage": 1,
        "pageSize": 10
    }

    response = requests.get(url, params=params, headers=headers, timeout=10)
    data = response.json()

    if data.get("code") != 200:
        return None

    result_list = data.get("result", {}).get("productList", [])

    if not result_list:
        print("No trobat")
        return None

    # Agafem el primer resultat
    product = result_list[0]

    print("MPN trobat:", product.get("productModel"))
    print("LCSC Part Number:", product.get("productCode"))

    return product.get("productCode")


# Prova
if __name__ == "__main__":
    components = get_lcsc_data("C17902")      #C17902         C2980306
    print(">>>>>>>>>>>")
    for key, value in components.items():
        print(f"{key}: {value}")


    # lcsc_code = search_by_mpn("STM32F103C8T6")
    # if lcsc_code:
    #     get_lcsc_data(lcsc_code)






















# import requests
# import json

# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Accept": "application/json, text/plain, */*",
#     "Accept-Language": "en-US,en;q=0.9,ca;q=0.8",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Referer": "https://www.lcsc.com/",
#     "Origin": "https://www.lcsc.com",
#     "Connection": "keep-alive",
#     "Sec-Fetch-Dest": "empty",
#     "Sec-Fetch-Mode": "cors",
#     "Sec-Fetch-Site": "same-site",
#     "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": '"Windows"'
# }

# def search_lcsc(code_or_mpn):
#     """
#     Accepta un LCSC Part Number (Cxxxx) o un MPN i retorna el LCSC Part Number corresponent
#     """
#     # Si ja és un Cxxxx, el retornem directament
#     if code_or_mpn.upper().startswith("C"):
#         return code_or_mpn.upper()

#     # Si és un MPN, fem cerca global
#     url = "https://wmsc.lcsc.com/ftps/wm/search/global"
#     params = {
#         "keyword": code_or_mpn,
#         "currentPage": 1,
#         "pageSize": 10
#     }

#     try:
#         response = requests.get(url, params=params, headers=HEADERS, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#     except Exception as e:
#         print(f"❌ Error cercant MPN: {e}")
#         return None

#     products = data.get("result", {}).get("productList", [])
#     if not products:
#         print("❌ No s'ha trobat cap producte per aquest MPN")
#         return None

#     # Retornem el primer producte trobat
#     return products[0].get("productCode")

# def get_lcsc_data(code_or_mpn):
#     lcsc_code = search_lcsc(code_or_mpn)
#     if not lcsc_code:
#         return None

#     url = "https://wmsc.lcsc.com/ftps/wm/product/detail"
#     params = {"productCode": lcsc_code}

#     try:
#         response = requests.get(url, params=params, headers=HEADERS, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#     except Exception as e:
#         print(f"❌ Error carregant dades: {e}")
#         return None

#     if data.get("code") != 200 or not data.get("result"):
#         print(f"❌ Resposta no vàlida de LCSC")
#         return None

#     product = data["result"]

#     print("="*80)
#     print(f"✅ LCSC Part Number: {lcsc_code}")
#     print(f"MPN: {product.get('productModel', 'N/A')}")
#     print(f"Product Name: {product.get('productNameEn', 'N/A')}")
#     print(f"Manufacturer: {product.get('brandNameEn', 'N/A')}")
#     print(f"Category: {product.get('catalogName', 'N/A')}")
#     print(f"Package: {product.get('encapStandard', 'N/A')}")
#     print(f"Description: {product.get('productDescEn', 'N/A')}")

#     # Datasheet
#     if product.get('pdfUrl'):
#         print(f"\n📄 Datasheet: {product['pdfUrl']}")

#     # Stock
#     print(f"\n📦 Stock disponible: {product.get('stockNumber', 0):,}")

#     # Link de compra
#     buy_link = f"https://www.lcsc.com/product-detail/{lcsc_code}.html"
#     print(f"🔗 Link de compra: {buy_link}")

#     # Preus (només fins a 100 unitats)
#     print(f"\n💰 Preus (només fins a 100 unitats):")
#     for price_tier in product.get('productPriceList', []):
#         qty = price_tier.get('ladder')
#         if qty <= 100:
#             price = price_tier.get('productPrice')
#             print(f"   {qty:>7,} unitats → {price} $/u")

#     # Imatges
#     if product.get('productImages'):
#         images = product.get('productImages')
#         for i, img in enumerate(images, start=1):
#             print(f"🖼️ Imatge {i}: {img}")

#     print("="*80)
#     return product

# # Exemple d'ús
# if __name__ == "__main__":
#     # Funciona amb Cxxxx o MPN
#     get_lcsc_data("C85824")
#     # get_lcsc_data("STM32F103C8T6")      #no es pot
