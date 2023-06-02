import os
import requests
import csv
from dotenv import load_dotenv
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


load_dotenv()

# Load API key from .env file
api_key = os.getenv("API_KEY")

# Function to get BTC price
def get_btc_price():
    url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
    response = requests.get(url).json()
    return response["bpi"]["USD"]["rate_float"]

# Function to get BTC RSI (using public API from alternative.me)
def get_btc_rsi():
    url = "https://api.alternative.me/fng/?limit=1"
    response = requests.get(url).json()
    return float(response["data"][0]["value"])  # Convert the value to float


# Function to get Puell Multiple
def get_puell_multiple():
    headers = {'Authorization': 'Bearer ' + api_key}
    url = "https://api.cryptoquant.com/v1/btc/network-indicator/puell-multiple?window=day&limit=1"
    response = requests.get(url, headers=headers).json()
    return response['result']['data'][0]['puell_multiple']

# Function to get NUPL
def get_nupl():
    headers = {'Authorization': 'Bearer ' + api_key}
    url = "https://api.cryptoquant.com/v1/btc/network-indicator/nupl?window=day&limit=1"
    response = requests.get(url, headers=headers).json()
    return response['result']['data'][0]['nupl']

# Function to get MVRV
def get_mvrv():
    headers = {'Authorization': 'Bearer ' + api_key}
    url = "https://api.cryptoquant.com/v1/btc/market-indicator/mvrv?window=day&limit=1"
    response = requests.get(url, headers=headers).json()
    return response['result']['data'][0]['mvrv']

# Function to get BTC UPDI short, medium, and long using Selenium
def get_btc_updi():
    url = "https://www.polaritydigital.io/"

    # Set up WebDriver with WebDriver Manager and run in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    try:
        # Wait for the table to load
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.ant-table-row.ant-table-row-level-0'))
        )

        updi_short = driver.find_element(By.CSS_SELECTOR, 'tr.ant-table-row.ant-table-row-level-0 > td:nth-child(5) a').text
        updi_medium = driver.find_element(By.CSS_SELECTOR, 'tr.ant-table-row.ant-table-row-level-0 > td:nth-child(6) a').text
        updi_long = driver.find_element(By.CSS_SELECTOR, 'tr.ant-table-row.ant-table-row-level-0 > td:nth-child(7) a').text

        return updi_short, updi_medium, updi_long

    finally:
        driver.quit()

def calculate_onchain_index(btc_rsi, puell_multiple, nupl, mvrv, updi_short):
    onchain_index = (
        (btc_rsi - 0) / (100 - 0)
        + (puell_multiple - 0) / (3.5 - 0)
        + (nupl - (-0.8)) / (0.8 - (-0.8))
        + (mvrv - 0) / (5 - 0)
        + (updi_short - (-4)) / (4 - (-4))
    ) / 5

    return onchain_index


if __name__ == "__main__":
    updi_short, updi_medium, updi_long = get_btc_updi()

    btc_price = round(get_btc_price(), 2)
    btc_rsi = round(get_btc_rsi(), 2)
    puell_multiple = round(get_puell_multiple(), 2)
    nupl = round(get_nupl(), 2)
    mvrv = round(get_mvrv(), 2)
    updi_short = round(float(updi_short), 2)

    onchain_index = round(calculate_onchain_index(btc_rsi, puell_multiple, nupl, mvrv, updi_short), 2)

    table_data = [
        ["BTC Price", btc_price],
        ["BTC RSI", btc_rsi],
        ["Puell Multiple", puell_multiple],
        ["NUPL", nupl],
        ["MVRV", mvrv],
        ["BTC UPDI Short", updi_short],
        ["BTC UPDI Medium", updi_medium],
        ["BTC UPDI Long", updi_long],
        ["On-Chain Index", onchain_index],
    ]

    print(tabulate(table_data, headers=["Indicator", "Value"], tablefmt="csv"))

 
# Transpose table_data
transposed_table_data = list(zip(*table_data))

with open('output.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(transposed_table_data[0])  # Write metrics (Indicator)
    csv_writer.writerow(transposed_table_data[1])  # Write values