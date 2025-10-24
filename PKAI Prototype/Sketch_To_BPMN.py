from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
import os

# Disclaimer: The code presented in this work is developed solely for the purpose of facilitating automated access to the Sketch Miner tool via the chrome browser. Its use is strictly limited to scientific and academic research contexts.

def Sketch_to_BPMN(Sketch, modelpathI, modelPathO):
    # Set custom download directory (change this to your desired directory)
    download_dir = "Outputs"  
    absolute_download_dir = os.path.join(os.getcwd(), download_dir)
    print (absolute_download_dir)

    #Clear Dowload dir
    modelPath = modelpathI
    if os.path.exists(modelPath):
        os.remove(modelPath)  # Delete the file

    modelPath = modelPathO
    if os.path.exists(modelPath):
        os.remove(modelPath)  # Delete the file

    # Configure Chrome options to set the download directory
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
    "download.default_directory": absolute_download_dir,  # Set custom download directory
    "download.prompt_for_download": False,       # Disable download prompt
    "safebrowsing.enabled": False                 # Enable safe browsing for automatic download
    })

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")            # Disable GPU usage
    chrome_options.add_argument("--no-sandbox")             # Required for running as root


    # Set up Chrome WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)

    driver.set_window_size(1920, 1080)

    # Open BPMN Sketch Miner website
    driver.get('https://www.bpmn-sketch-miner.ai/')

    # Wait for the page to load
    time.sleep(3)

    # Locate the input text area for BPMN description
    input_box = driver.find_element(By.XPATH, '//*[@id="logtext"]')


    # Send the BPMN description to the text area
    input_box.clear()
    input_box.send_keys(Sketch)

    time.sleep(3)
    # Find the Export BPMN button (inspect the button to get the correct XPath/ID)
    export_button = driver.find_element(By.XPATH, '//*[@id="button-export-bpmn"]')
    export_button.click()

    export_button = driver.find_element(By.XPATH, '//*[@id="button-export-png"]')
    export_button.click()

    downloaded_files = os.listdir(download_dir)
    print("Downloaded files:")
    for file in downloaded_files:
        print(f"File: {file} | Path: {os.path.join(download_dir, file)}")

    # Wait for the download
    time.sleep(3)


    driver.quit()