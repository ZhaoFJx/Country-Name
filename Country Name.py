from SPARQLWrapper import SPARQLWrapper, JSON
import pycountry # type: ignore

# I used wikidata to query the name here.
def query_wikidata(country_name):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?countryLabel ?officialNameLabel WHERE {{
      ?country wdt:P31 wd:Q6256;  # Name?
              rdfs:label "{country_name}"@en.
      OPTIONAL {{
        ?country wdt:P1448 ?officialName.  # Offical Name?
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        country = result["countryLabel"]["value"]
        official_name = result.get("officialNameLabel", {}).get("value", None)
        return country, official_name
    return None, None

# In case if wikidata does not have the country name, I will use the modern ISO 3166 standard to verify the country name.
def validate_with_iso(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.name
    except LookupError:
        return None


def main():
    print("Please enter a list of country names (one country per line, press Enter twice to end input):")
    user_input = ""
    while True:
        line = input()
        if line.strip() == "":
            break
        user_input += line + "\n"

    country_list = [country.strip() for country in user_input.splitlines() if country.strip()]
    print("\nQuering the following countries:")
    print(", ".join(country_list))

    # Least, the program will write the result to a file(in the same folder as this file!)
    with open("country_status.txt", "w", encoding="utf-8") as file:
        for country in country_list:
            print(f"\Searching {country} ...")
   
            country_name, official_name = query_wikidata(country)


            if not country_name or not official_name:
                validated_name = validate_with_iso(country)
                if validated_name:
                    country_name = country if not country_name else country_name
                    official_name = f"{validated_name} (ISO 3166 Standard)"
                else:
                    country_name = country
                    official_name = "Unable to verify this country"

            result = f"{country_name}: {official_name}"
            print(result)
            file.write(result + "\n")

    print("\nDone! Saved to 'country_status.txt' .")

# Run!
if __name__ == "__main__":
    main()