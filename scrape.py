import requests
import json
import pandas as pd


def extract_and_save_json_model(url, output_file_json, output_file_csv):
    """
    Fetch the page source from the URL, extract the 'window.jsonModel' string,
    save it to a JSON file, and save the 'properties' part as a CSV.
    """
    try:
        # Fetch the page source
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        page_source = response.text
        print("Page source fetched successfully.")

        # Locate and extract 'window.jsonModel'
        start_marker = "window.jsonModel = "
        end_marker = "</script>"

        if start_marker in page_source:
            print("Found 'window.jsonModel' in the page source.")
            # Extract the JSON string
            start_index = page_source.index(start_marker) + len(start_marker)
            end_index = page_source.index(end_marker, start_index)
            json_model = page_source[start_index:end_index].strip().rstrip(";")

            # Save the extracted JSON string to a file
            with open(output_file_json, "w", encoding="utf-8") as json_file:
                json_file.write(json_model)
            print(f"'window.jsonModel' extracted and saved to {output_file_json}.")

            # Parse the JSON string
            json_data = json.loads(json_model)

            # Extract the 'properties' part and save as CSV
            properties = json_data.get("properties", [])
            if not properties:
                print("No 'properties' found in the JSON data.")
                return

            # Normalize the properties into a DataFrame and save to CSV
            df = pd.json_normalize(properties)
            df.to_csv(output_file_csv, index=False)
            print(f"'properties' saved to {output_file_csv}.")
        else:
            print("'window.jsonModel' not found in the page source.")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Example URL
    url = "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=OUTCODE%5E1360&numberOfPropertiesPerPage=500&propertyTypes=&includeSSTC=true&mustHave=&dontShow=&furnishTypes=&keywords="

    # Output file names
    output_file_json = "resultstring.json"
    output_file_csv = "finalresultsales.csv"

    # Extract and save the JSON model
    extract_and_save_json_model(url, output_file_json, output_file_csv)
