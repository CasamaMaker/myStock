import requests
import json

API_KEY_MOUSER = "34e727c3-3810-4ccd-b06e-d97149772242"
# API_KEY_MOUSER= ""

def get_mouser_data(part_number, api_key=API_KEY_MOUSER):
    url = "https://api.mouser.com/api/v1/search/partnumber"
    
    # Body de la petició
    payload = {
        "SearchByPartRequest": {
            "mouserPartNumber": part_number,
            "partSearchOptions": ""
        }
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Afegir API key als params
    params = {
        "apiKey": api_key
    }
    
    # Construir URL completa per mostrar-la (sense mostrar l'API key completa)
    api_key_masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    full_url = f"{url}?apiKey={api_key_masked}"
    
    # print(f"🔍 Cercant codi: {part_number} a MOUSER\n")
    
    try:
        response = requests.post(
            url, 
            params=params,
            headers=headers, 
            json=payload,
            timeout=10
        )
  
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
    
    # Comprovar errors de l'API
    if "Errors" in data and data["Errors"]:
        print(f"❌ Error de l'API de Mouser:")
        for error in data["Errors"]:
            print(f"   {error.get('Message', 'Error desconegut')}")
        return None
    
    # Extreure resultats
    search_results = data.get("SearchResults", {})
    parts = search_results.get("Parts", [])
    
    if not parts:
        print(f"❌ No s'ha trobat cap component amb el part number: {part_number}")
        return None
    
    # Agafar el primer resultat (normalment és el més rellevant)
    product = parts[0]

    component = {}
    component["name"] = product.get('ManufacturerPartNumber')
    component["store_name"] = product.get('MouserPartNumber')
    component["description"] = product.get('Description')
    component["type2"] = product.get('Category')
    component["manufacturer"] = product.get('Manufacturer') 
    component["package"] = ""
    component["datasheet"] = product.get('DataSheetUrl')
    component["store"] = product.get('ProductDetailUrl')
    component["image"] = product.get('ImagePath')
    component["price_unit"] = product.get('PriceBreaks')
    component["store_availability"] = product.get('Availability')

    # print("✅ Component trobat!\n")
    # return product
    return component


def search_mouser_keyword(keyword, api_key, max_results=10):
    """Cerca per paraula clau (útil per trobar components similars)"""
    url = "https://api.mouser.com/api/v1/search/keyword"
    
    payload = {
        "SearchByKeywordRequest": {
            "keyword": keyword,
            "records": max_results,
            "startingRecord": 0,
            "searchOptions": "",
            "searchWithYourSignUpLanguage": ""
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    params = {"apiKey": api_key}
    
    print(f"🔍 Cercant: {keyword}")
    
    try:
        response = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        search_results = data.get("SearchResults", {})
        parts = search_results.get("Parts", [])
        
        print(f"✅ Trobats {len(parts)} resultats\n")
        
        for i, part in enumerate(parts, 1):
            print(f"{i}. {part.get('ManufacturerPartNumber', 'N/A')}")
            print(f"   Manufacturer: {part.get('Manufacturer', 'N/A')}")
            print(f"   Description: {part.get('Description', 'N/A')[:80]}...")
            print(f"   Mouser P/N: {part.get('MouserPartNumber', 'N/A')}")
            print()
        
        return parts
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# Prova
if __name__ == "__main__":
    # SUBSTITUEIX AQUÍ AMB EL TEU API KEY
    # API_KEY_MOUSER = "34e727c3-3810-4ccd-b06e-d97149772242"
    
    # Cerca per part number específic
    # print("\n" + "="*80)
    # print("CERCA PER PART NUMBER")
    # print("="*80 + "\n")
    # components = get_mouser_data("CRCW04021K65FKEE", API_KEY)
    # components = get_mouser_data("AANI-CH-0068-T", API_KEY)
    components = get_mouser_data("863-NGTB40N120FL2WG", API_KEY_MOUSER)     # AE1206BR-0710KL         815-AANI-CH-0068-T
    print(">>>>>>>>>>>")
    for key, value in components.items():
        print(f"{key}: {value}")


    # component = get_mouser_data("815-AANI-CH-0068-T", API_KEY)
    
    # O cerca per paraula clau
    # print("\n" + "="*80)
    # print("CERCA PER PARAULA CLAU")
    # print("="*80 + "\n")
    # results = search_mouser_keyword("ferrite bead 0603", API_KEY, max_results=5)