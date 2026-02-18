import requests
import json

API_KEY_FARNELL = "j8ez8wawuv2ka9r2bamn499r"

def get_farnell_data(part_number, api_key, store_region="es.farnell.com"):
    """
    Cerca un component per part number (manufacturer part number)
    
    Args:
        part_number: El part number del fabricant
        api_key: API key de Farnell
        store_region: Regió de la botiga (es.farnell.com, uk.farnell.com, etc.)
    """
    url = "https://api.element14.com/catalog/products"
    
    # Paràmetres de la petició
    params = {
        "callInfo.apiKey": api_key,
        "callInfo.responseDataFormat": "JSON",
        "term": f"manuPartNum:{part_number}",
        "storeInfo.id": store_region,
        "resultsSettings.offset": 0,
        "resultsSettings.numberOfResults": 1,
        "resultsSettings.responseGroup": "large"  # large per obtenir tota la info
    }
    
    # Màscara de l'API key per mostrar
    api_key_masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"🔍 Cercant: {part_number} a {store_region}")
    print(f"📡 API Key: {api_key_masked}\n")
    
    try:
        response = requests.get(
            url,
            params=params,
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
    
    # Comprovar si hi ha resultats
    # Per manufacturer part number, la resposta ve en manufacturerPartNumberSearchReturn
    if "manufacturerPartNumberSearchReturn" in data:
        search_return = data["manufacturerPartNumberSearchReturn"]
    elif "keywordSearchReturn" in data:
        search_return = data["keywordSearchReturn"]
    else:
        print(f"❌ Resposta inesperada de l'API")
        print(f"Dades rebudes: {json.dumps(data, indent=2)[:500]}")
        return None
    
    products = search_return.get("products", [])
    
    if not products:
        print(f"❌ No s'ha trobat cap component amb el part number: {part_number}")
        # Mostrar possibles suggeriments si n'hi ha
        if "numberOfResults" in search_return:
            print(f"   Número de resultats: {search_return['numberOfResults']}")
        return None
    
    # Agafar el primer resultat
    product = products[0]
    
    # Extreure la informació rellevant
    component = {}
    component["name"] = product.get("translatedManufacturerPartNumber", 
                                    product.get("displayName", ""))
    component["store_name"] = product.get("sku", "")
    component["description"] = product.get("displayName", "")
    
    # Categoria - buscar en diferents camps
    category = product.get("translatedCategoryName", "")
    if not category:
        # Intentar altres camps
        category = product.get("categoryName", "")
    if not category and "COM_productClassification" in product:
        # Si hi ha classificació COM, agafar-la
        classification = product.get("COM_productClassification", {})
        if isinstance(classification, dict):
            category = classification.get("category", "")
    component["type2"] = category
    
    component["manufacturer"] = product.get("brandName", "")
    component["product_status"] = product.get("productStatus", "")  # STOCKED, etc.
    component["rohs"] = product.get("rohsStatusCode", "")
    
    # Package/encapsulat - buscar en els atributs del producte
    attributes = product.get("attributes", [])
    package = ""
    for attr in attributes:
        attr_label = attr.get("attributeLabel", "").lower()
        if "package" in attr_label or "case" in attr_label or "encapsulado" in attr_label:
            package = attr.get("attributeValue", "")
            break
    component["package"] = package
    
    # URLs i imatges
    component["datasheet"] = product.get("datasheets", [{}])[0].get("url", "") if product.get("datasheets") else ""
    
    # URL del producte
    component["store"] = product.get("productDetailUrl", "")
    if not component["store"] and "sku" in product:
        # Construir URL si no està present
        component["store"] = f"https://es.farnell.com/w/search?st={product['sku']}"

    
    # La imatge pot venir en diferents formats
    image_url = ""
    if "image" in product:
        if isinstance(product["image"], dict):
            image_url = product["image"].get("baseName", "")
        else:
            image_url = product.get("image", "")
    
    # Si la imatge és un path relatiu, afegir URL base
    if image_url and not image_url.startswith("http"):
        image_url = f"https://es.farnell.com/productimages/standard/es_ES{image_url}"
    component["image"] = image_url
    
    # Preus - poden venir en diferents formats
    price_breaks = []
    if "prices" in product and product["prices"]:
        for price in product["prices"]:
            price_breaks.append({
                "quantity": price.get("from", 0),
                "price": price.get("cost", 0),
                "currency": price.get("currency", "EUR")
            })
    component["price_unit"] = price_breaks
    
    # Disponibilitat - pot ser un número o un text
    if "stock" in product:
        stock = product.get("stock", {})
        if isinstance(stock, dict):
            component["store_availability"] = stock.get("level", "Unknown")
            component["stock_quantity"] = stock.get("level", 0)
        else:
            component["store_availability"] = str(stock)
            component["stock_quantity"] = stock
    else:
        component["store_availability"] = "Unknown"
        component["stock_quantity"] = 0
    
    # Informació d'empaquetat
    component["pack_size"] = product.get("packSize", 1)
    component["unit_of_measure"] = product.get("unitOfMeasure", "")
    
    print("✅ Component trobat!\n")
    return component


def get_farnell_by_sku(sku, api_key=API_KEY_FARNELL, store_region="es.farnell.com"):
    """
    Cerca un component pel SKU/Order Code de Farnell
    
    Args:
        sku: El SKU o Order Code de Farnell
        api_key: API key de Farnell
        store_region: Regió de la botiga
    """
    url = "https://api.element14.com/catalog/products"
    
    params = {
        "callInfo.apiKey": api_key,
        "callInfo.responseDataFormat": "JSON",
        "term": f"any:{sku}",  # Cerca general pel SKU
        "storeInfo.id": store_region,
        "resultsSettings.offset": 0,
        "resultsSettings.numberOfResults": 5,  # Agafar més resultats per filtrar
        "resultsSettings.responseGroup": "large"
    }
    
    # print(f"🔍 Cercant codi: {sku} a {store_region}\n")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Comprovar el tipus de resposta
        if "manufacturerPartNumberSearchReturn" in data:
            search_return = data["manufacturerPartNumberSearchReturn"]
        elif "keywordSearchReturn" in data:
            search_return = data["keywordSearchReturn"]
        else:
            print(f"❌ Resposta inesperada")
            return None
        
        products = search_return.get("products", [])
        
        if not products:
            print(f"❌ No s'ha trobat cap component amb el SKU: {sku}")
            return None
        
        # Filtrar per trobar el SKU exacte
        product = None
        for p in products:
            if p.get("sku") == sku:
                product = p
                break
        
        if not product:
            print(f"❌ No s'ha trobat una coincidència exacta per al SKU: {sku}")
            print(f"   S'han trobat {len(products)} resultats similars")
            return None
        
        # for pro, duct in product.items():
        #     print(f"{pro}: {duct}")
        # Utilitzar la mateixa estructura que get_farnell_data
        component = {}
        component["name"] = product.get("translatedManufacturerPartNumber", 
                                        product.get("displayName", ""))
        component["store_name"] = product.get("sku", "")
        component["description"] = product.get("displayName", "")
        
        # Categoria - buscar en diferents camps
        category = product.get("translatedCategoryName", "")
        if not category:
            category = product.get("categoryName", "")
        if not category and "COM_productClassification" in product:
            classification = product.get("COM_productClassification", {})
            if isinstance(classification, dict):
                category = classification.get("category", "")
        component["type2"] = category
        
        component["manufacturer"] = product.get("brandName", "")
        # component["product_status"] = product.get("productStatus", "")
        # component["rohs"] = product.get("rohsStatusCode", "")
        
        attributes = product.get("attributes", [])
        package = ""
        for attr in attributes:
            attr_label = attr.get("attributeLabel", "").lower()
            if "package" in attr_label or "case" in attr_label or "encapsulado" in attr_label:
                package = attr.get("attributeValue", "")
                break
        component["package"] = package
        
        component["datasheet"] = product.get("datasheets", [{}])[0].get("url", "") if product.get("datasheets") else ""
        
        # URL del producte
        component["store"] = product.get("productDetailUrl", "")
        if not component["store"] and "sku" in product:
            component["store"] = f"https://es.farnell.com/w/search?st={product['sku']}"

        
        # Imatge amb URL base si és necessari
        image_url = ""
        if "image" in product:
            if isinstance(product["image"], dict):
                image_url = product["image"].get("baseName", "")
            else:
                image_url = product.get("image", "")
        
        if image_url and not image_url.startswith("http"):
            image_url = f"https://es.farnell.com/productimages/standard/es_ES{image_url}"
        component["image"] = image_url
        
        price_breaks = []
        if "prices" in product and product["prices"]:
            for price in product["prices"]:
                price_breaks.append({
                    "quantity": price.get("from", 0),
                    "price": price.get("cost", 0),
                    "currency": price.get("currency", "EUR")
                })
        component["price_unit"] = price_breaks
        
        if "stock" in product:
            stock = product.get("stock", {})
            if isinstance(stock, dict):
                component["store_availability"] = stock.get("level", "Unknown")
                # component["stock_quantity"] = stock.get("level", 0)
            else:
                component["store_availability"] = str(stock)
                # component["stock_quantity"] = stock
        else:
            component["store_availability"] = "Unknown"
            # component["stock_quantity"] = 0
        
        # component["pack_size"] = product.get("packSize", 1)
        # component["unit_of_measure"] = product.get("unitOfMeasure", "")
        
        # print("✅ Component trobat!\n")
        return component
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def debug_product_fields(part_number, api_key, store_region="es.farnell.com"):
    """
    Funció de debug per veure tots els camps disponibles d'un producte
    Útil per descobrir quins camps està retornant l'API
    """
    component = get_farnell_data(part_number, api_key, store_region)
    
    if not component:
        return None
    
    url = "https://api.element14.com/catalog/products"
    params = {
        "callInfo.apiKey": api_key,
        "callInfo.responseDataFormat": "JSON",
        "term": f"manuPartNum:{part_number}",
        "storeInfo.id": store_region,
        "resultsSettings.offset": 0,
        "resultsSettings.numberOfResults": 1,
        "resultsSettings.responseGroup": "large"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "manufacturerPartNumberSearchReturn" in data:
            search_return = data["manufacturerPartNumberSearchReturn"]
        elif "keywordSearchReturn" in data:
            search_return = data["keywordSearchReturn"]
        else:
            return None
        
        products = search_return.get("products", [])
        if not products:
            return None
        
        product = products[0]
        
        print("\n" + "="*80)
        print("TOTS ELS CAMPS DISPONIBLES")
        print("="*80)
        for key in sorted(product.keys()):
            value = product[key]
            # Truncar valors llargs
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            elif isinstance(value, list) and len(value) > 3:
                value = str(value[:3]) + "..."
            print(f"{key}: {value}")
        print("="*80 + "\n")
        
        return product
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def search_farnell_keyword(keyword, api_key, store_region="es.farnell.com", max_results=10):
    """
    Cerca per paraula clau (útil per trobar components similars)
    
    Args:
        keyword: Paraula clau a cercar
        api_key: API key de Farnell
        store_region: Regió de la botiga
        max_results: Nombre màxim de resultats
    """
    url = "https://api.element14.com/catalog/products"
    
    params = {
        "callInfo.apiKey": api_key,
        "callInfo.responseDataFormat": "JSON",
        "term": f"any:{keyword}",  # Cerca per qualsevol camp
        "storeInfo.id": store_region,
        "resultsSettings.offset": 0,
        "resultsSettings.numberOfResults": max_results,
        "resultsSettings.responseGroup": "medium"
    }
    
    print(f"🔍 Cercant paraula clau: {keyword} a {store_region}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        keyword_search = data.get("keywordSearchReturn", {})
        products = keyword_search.get("products", [])
        num_results = keyword_search.get("numberOfResults", 0)
        
        print(f"✅ Trobats {len(products)} de {num_results} resultats totals\n")
        
        results = []
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.get('translatedManufacturerPartNumber', 'N/A')}")
            print(f"   Fabricant: {product.get('brandName', 'N/A')}")
            print(f"   Descripció: {product.get('displayName', 'N/A')[:80]}...")
            print(f"   Farnell SKU: {product.get('sku', 'N/A')}")
            
            # Mostrar preu si disponible
            if "prices" in product and product["prices"]:
                first_price = product["prices"][0]
                print(f"   Preu: {first_price.get('cost', 'N/A')} {first_price.get('currency', '')} (des de {first_price.get('from', 1)} unitats)")
            
            # Mostrar stock
            stock = product.get("stock", {})
            print(f"   Stock: {stock.get('level', 'N/A')}")
            print()
            
            results.append(product)
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# Prova
if __name__ == "__main__":
    # SUBSTITUEIX AQUÍ AMB EL TEU API KEY
    # API_KEY = "j8ez8wawuv2ka9r2bamn499r"
    
    # Pots canviar la regió segons necessitis:
    # "es.farnell.com" (Espanya)
    # "uk.farnell.com" (Regne Unit)
    # "de.farnell.com" (Alemanya)
    # "fr.farnell.com" (França)
    # etc.
    STORE_REGION = "es.farnell.com"
    
    # # Exemple 1: Cerca per part number del fabricant
    # print("\n" + "="*80)
    # print("CERCA PER MANUFACTURER PART NUMBER")
    # print("="*80 + "\n")
    # component = get_farnell_data("LM339ADT", API_KEY, STORE_REGION)
    # if component:
    #     print(">>>>>>>>>>>")
    #     for key, value in component.items():
    #         print(f"{key}: {value}")
    #     print()
    
    # Exemple 2: Cerca per SKU de Farnell
    print("\n" + "="*80)
    print("CERCA PER FARNELL SKU/ORDER CODE")
    print("="*80 + "\n")
    component2 = get_farnell_by_sku("2988437", API_KEY_FARNELL, STORE_REGION)       #2988437       2323924   1236670
    if component2:
        # print(">>>>>>>>>>>")
        for key, value in component2.items():
            print(f"{key}: {value}")
        print()
    
    # # Exemple 3: Cerca per paraula clau
    # print("\n" + "="*80)
    # print("CERCA PER PARAULA CLAU")
    # print("="*80 + "\n")
    # results = search_farnell_keyword("resistor 1k 0603", API_KEY, STORE_REGION, max_results=5)
    
    # # Exemple 4: Debug - veure tots els camps disponibles (descomentar per usar)
    # # print("\n" + "="*80)
    # # print("DEBUG - TOTS ELS CAMPS")
    # # print("="*80 + "\n")
    # # debug_product_fields("LM339ADT", API_KEY, STORE_REGION)