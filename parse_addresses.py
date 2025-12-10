import pandas as pd
import re
import os

INPUT_FILE = 'output_enderecos.xlsx'
OUTPUT_FILE = 'output_enderecos_tratado.xlsx'

def parse_address(addr):
    if not isinstance(addr, str) or addr == "No address found" or addr.startswith("Error") or "Mock Address" in addr:
        return pd.Series([None]*7)
    
    # Clean up whitespace
    clean_addr = addr.strip()
    
    # Initialize fields
    pais = None
    cep = None
    estado = None
    municipio = None
    bairro = None
    numero = None
    logradouro = None
    
    # 1. PEEL OFF COUNTRY (Last element or "Brazil"/"Brasil")
    # Most GMaps addresses end in ", Brazil".
    # Sometimes just "Brazil"
    if clean_addr.lower().endswith("brazil"):
        pais = "Brazil"
        # Remove safely
        clean_addr = clean_addr[:-6].strip().strip(",").strip()
    elif clean_addr.lower().endswith("brasil"):
        pais = "Brasil"
        clean_addr = clean_addr[:-6].strip().strip(",").strip()
    else:
        # Maybe it doesn't have country, assume Brazil or leave empty?
        # Let's try splitting by comma if last part looks like country
        parts = clean_addr.rsplit(',', 1)
        if len(parts) > 1:
            last_part = parts[1].strip()
            # Heuristic: if it's strictly alpha and valid country-ish length, maybe it's country?
            # But let's be careful. If we miss country, it's not critical.
            pass

    # 2. PEEL OFF ZIP CODE (CEP)
    # Regex for Zip: \d{5}-?\d{3} at the end
    # We search at end of string
    zip_match = re.search(r'(\d{5}[-\s]?\d{3})$', clean_addr)
    if zip_match:
        cep = zip_match.group(1)
        clean_addr = clean_addr[:zip_match.start()].strip().strip(",").strip("-").strip()

    # 3. PEEL OFF STATE (UF)
    # Usually " - PA" or ", PA" or "State of Pará" at the end.
    # Check for 2-letter state code first
    state_match = re.search(r'[\s,-]+([A-Z]{2})$', clean_addr)
    if state_match:
        estado = state_match.group(1)
        clean_addr = clean_addr[:state_match.start()].strip()
    else:
        # Fallback for "State of Pará"
        if "State of Pará" in clean_addr:
             estado = "PA"
             clean_addr = clean_addr.replace("State of Pará", "").strip().strip(",").strip("-").strip()

    # 4. PEEL OFF CITY (Município)
    # The part immediately preceding the State is usually the City.
    # We assume 'clean_addr' now ENDS with the City.
    # We need to find where the City starts.
    # Typically separated from previous part (Neighborhood) by comma.
    
    if ',' in clean_addr:
        rest, potential_city = clean_addr.rsplit(',', 1)
        municipio = potential_city.strip()
        clean_addr = rest.strip()
    else:
        # Dealing with cases like "Ananindeua - PA" (where PA was removed, Ananindeua remains)
        # OR "Belém" (where only city remains)
        # OR "Hood - City" with hyphen separator (rare but possible in non-standard formatting)
        
        # If no comma, check if we have " - "
        if ' - ' in clean_addr:
             # Ambiguous: "Shopping - Castanheira" (Address - Hood) vs "Hood - City".
             # GMaps standard: "Hood, City".
             # So if we see " - ", it's likely separating Address and Hood, and City was implicitly consumed or missing?
             # NO: If we parsed State (PA), then City MUST be there.
             # If string is "Shopping - Castanheira, Belém", we parsed Belém via comma.
             # If string is "Rodovia Mário Covas, 208, Ananindeua", we parsed Ananindeua via comma.
             
             # What if string is "Address - Hood - City"?
             # GMaps doesn't usually do that.
             
             # What if string is just "City"? (e.g. originally "City - State")
             # Then clean_addr is the city.
             # We can assume if the string is short/alpha, it's the city.
             pass 
        
        # Fallback: check against known cities list (Belém, Ananindeua, Marituba) to be safe
        known_cities = ["Belém", "Ananindeua", "Marituba", "Outeiro", "Icoaraci", "Mosqueiro"]
        clean_addr_lower = clean_addr.lower()
        found_city = False
        for city in known_cities:
            if clean_addr_lower.endswith(city.lower()):
                municipio = city # Use the known casing
                # Remove city from end
                # Use regex to replace from end
                clean_addr = re.sub(f'{city}$', '', clean_addr, flags=re.IGNORECASE).strip().strip(",").strip("-").strip()
                found_city = True
                break
        
        if not found_city:
             # If we haven't found a city yet, and we are left with something like "Belém", just take it.
             # But if we are left with "Rua X", and City is missing/implicit?
             # Let's leave Municipio None if we can't find separation.
             # Exception: if clean_addr is ONLY the city.
             pass

    # 5. PEEL OFF NEIGHBORHOOD (Bairro)
    # Remaining: "Street, Num - Hood" or "Street - Hood" or "Street, Num".
    # Separator: " - "
    if ' - ' in clean_addr:
        rest, potential_hood = clean_addr.rsplit(' - ', 1)
        bairro = potential_hood.strip()
        clean_addr = rest.strip()
    else:
        # No hyphen.
        # Maybe "Street, Num, Hood" (comma separated)?
        # Or missing hood.
        bairro = None

    # 6. SEPARATE STREET AND NUMBER
    # Remaining: "Street, Num" or "Street".
    # Separator: ", ".
    if ',' in clean_addr:
        rest, potential_num = clean_addr.rsplit(',', 1)
        logradouro = rest.strip()
        numero = potential_num.strip()
    else:
        # No comma. 
        # Check for specific patterns like "Quadra X N Y"
        # "AV: Tucano QUADRA: 43 N:"
        logradouro = clean_addr
        numero = None

    return pd.Series([logradouro, numero, bairro, municipio, estado, cep, pais])

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Reading {INPUT_FILE}...")
    try:
        df = pd.read_excel(INPUT_FILE)
    except Exception as e:
        print(f"Error reading excel: {e}")
        return

    feature_cols_indices = [13, 14, 15] # N, O, P
    if len(df.columns) <= max(feature_cols_indices):
        print("Error: DataFrame columns issue.")
        return

    cols_n_o_p = df.iloc[:, feature_cols_indices]
    
    addr_col_name = 'Endereço_Google'
    if addr_col_name not in df.columns:
        addr_col_name = df.columns[-1]
    
    address_series = df[addr_col_name]
    new_df = cols_n_o_p.copy()
    new_df[addr_col_name] = address_series

    print("Parsing addresses with robust logic...")
    parsed_col_names = ['Logradouro', 'Número', 'Bairro', 'Município', 'Estado', 'CEP', 'País']
    
    parsed_data = new_df[addr_col_name].apply(parse_address)
    parsed_data.columns = parsed_col_names
    
    final_df = pd.concat([new_df, parsed_data], axis=1)

    print(f"Saving to {OUTPUT_FILE}...")
    final_df.to_excel(OUTPUT_FILE, index=False)
    print("Done successfully.")

if __name__ == "__main__":
    main()
