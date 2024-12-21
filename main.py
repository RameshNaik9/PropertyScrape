import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import json
import time
from selenium.webdriver.chrome.service import Service


# Function to handle cookies popup
def check_and_accept_cookies(driver):
    """Handle the cookie popup if it appears."""
    try:
        print("Checking for cookie popup...")
        time.sleep(2)  # Short wait to ensure popup appears
        popup = driver.find_element(By.ID, "onetrust-banner-sdk")
        accept_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        accept_button.click()
        print("Cookie popup accepted.")
    except Exception as e:
        print("No cookie popup found or failed to handle it:", str(e))


# Function to extract details from a property card
def extract_property_details(property_element):
    """Extract structured details from a single property card."""
    try:
        property_data = {}
        # Extract price
        try:
            price = property_element.find_element(
                By.CLASS_NAME, "propertyCard-priceValue"
            ).text
            property_data["price"] = price
        except:
            property_data["price"] = None

        # Extract price qualifier (e.g., Guide Price)
        try:
            price_qualifier = property_element.find_element(
                By.CLASS_NAME, "propertyCard-priceQualifier"
            ).text
            property_data["price_qualifier"] = price_qualifier
        except:
            property_data["price_qualifier"] = None

        # Extract address
        try:
            displayAddress = property_element.find_element(
                By.CLASS_NAME, "propertyCard-address"
            ).text
            property_data["displayAddress"] = displayAddress
        except:
            property_data["displayAddress"] = None

        # Extract summary
        try:
            summary = property_element.find_element(
                By.CLASS_NAME, "propertyCard-description"
            ).text
            property_data["summary"] = summary
        except:
            property_data["summary"] = None

        # Extract contact phone number
        try:
            phone_number = property_element.find_element(
                By.CLASS_NAME, "propertyCard-contactsPhoneNumber"
            ).text
            property_data["phone_number"] = phone_number
        except:
            property_data["phone_number"] = None

        # Extract propertySubType, bedrooms, and bathrooms
        try:
            property_info = property_element.find_element(
                By.CLASS_NAME, "property-information"
            )
            spans = property_info.find_elements(By.CLASS_NAME, "text")
            property_data["propertySubType"] = spans[0].text if len(spans) > 0 else None
            property_data["bedrooms"] = spans[1].text if len(spans) > 1 else None
            property_data["bathrooms"] = spans[2].text if len(spans) > 2 else None
        except:
            property_data["propertySubType"] = None
            property_data["bedrooms"] = None
            property_data["bathrooms"] = None

        return property_data

    except Exception as e:
        print("Error extracting property details:", str(e))
        return {}


# Function to scrape properties
def scrape_properties(driver):
    """Scrape all properties with class 'l-searchResult is-list'."""
    try:
        print("Waiting for search results to load...")
        time.sleep(5)  # Allow time for search results to load
        property_elements = driver.find_elements(By.CLASS_NAME, "l-searchResult")
        print(f"Found {len(property_elements)} properties.")
        properties = [
            extract_property_details(element) for element in property_elements
        ]
        return properties
    except Exception as e:
        print("Error scraping properties:", str(e))
        return []


# Function to save data to JSON
def save_to_json(data, file_name):
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Data saved to {file_name}")


# Function to save data to CSV
def save_to_csv(data, file_name):
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")


# Function to fetch content using Selenium
def fetch_with_selenium(url, driver_path):
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(url)
        print(f"Opened URL: {url}")
        check_and_accept_cookies(driver)
        properties = scrape_properties(driver)
        return properties
    finally:
        driver.quit()
        print("ChromeDriver closed.")


# Main function
def main(url_file, driver_path, output_json_file, output_csv_file):
    all_properties = []

    # Read URLs from the file
    with open(url_file, "r") as file:
        urls = [line.strip() for line in file if line.strip()]

    print(f"Found {len(urls)} URLs to scrape.")

    # Process each URL
    for url in urls:
        print(f"Processing {url}")
        properties = fetch_with_selenium(url, driver_path)
        all_properties.extend(properties)

    # Save all properties to JSON
    save_to_json(all_properties, output_json_file)

    # Save all properties to CSV
    save_to_csv(all_properties, output_csv_file)


if __name__ == "__main__":
    url_file = "list_of_urls1.txt"
    driver_path = "drivers/chromedriver"
    output_json_file = "properties.json"
    output_csv_file = "properties.csv"
    main(url_file, driver_path, output_json_file, output_csv_file)
