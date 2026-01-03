import requests
from bs4 import BeautifulSoup
import csv
import os
import datetime
import kaggle
import pandas as pd
import json

URL = "https://www.euro-millions.com/results-history-"
METADATA_FILENAME = "dataset-metadata.json"
DATASET_ID = "duartepereiradacruz/euromillions-historical-data"
UPLOAD_DIR = "upload"

def fetch_page(year: int) -> str:
    """
    Fetches the page of the URL
    
    Args:
        year (str): the year to append in the url
        
    Returns:
        str: content of the response, in unicode
    """
    resp = requests.get(URL+str(year))
    resp.raise_for_status()
    return resp.text

def parse_results(html: str) -> list:
    """
    Parses the data from the html content

    Args:
        html (str): content of the request

    Returns:
        results (list): list of json formatted draws
    """ 
    soup = BeautifulSoup(html, "html.parser")
    results = []
    
    for draw in soup.select("tr.resultRow"):
        #date scrapping
        link = draw.select_one("td.date a")  #the <a href="/results/28-11-2025">
        specific_url = link.get("href")
        date = specific_url.replace("/results/","")
        
        #nums and stars scrapping
        balls = [li.get_text(strip=True) for li in draw.select("ul.balls li")]
        nums = balls[:5]
        stars = balls[5:]
        
        #jackpot scrapping
        jackpot_element = draw.select_one('td[data-title="Jackpot"] strong')
        jackpot = jackpot_element.get_text(strip=True) if jackpot_element else None
        
        results.append({
            "date (dd-mm-yyyy)": date,
            "num_1": int(nums[0]),
            "num_2": int(nums[1]),
            "num_3": int(nums[2]),
            "num_4": int(nums[3]),
            "num_5": int(nums[4]),
            "star_1": int(stars[0]),
            "star_2": int(stars[1]),
            "jackpot (in EUR)": int(jackpot[1:].replace(",",""))
        })
    return results[::-1]
       
def save_to_csv(data: list) -> None:
    """
    Generates the .csv file with the data from the website

    Args:
        data (list): list of json formatted draws
    """
    filename = UPLOAD_DIR+"/euromillions_website.csv"
    keys = ["date (dd-mm-yyyy)", "num_1", "num_2", "num_3", "num_4", "num_5", "star_1", "star_2", "jackpot (in EUR)"]
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if not file_exists:
            writer.writeheader()
        for draw in data:
            writer.writerow(draw) 
        
def check_and_append_missing_data():
    """
    Fetch and append from euromillions_website.csv the missing data of euromillions.csv
    """
    existing_file = UPLOAD_DIR + "/euromillions.csv"
    website_file = UPLOAD_DIR + "/euromillions_website.csv"
    
    #get the latest date in the existing file
    df_existing = pd.read_csv(existing_file)
    df_existing['date'] = pd.to_datetime(df_existing['date (dd-mm-yyyy)'], format='%d-%m-%Y')
    last_date_existing = df_existing['date'].max()
 
    df_website = pd.read_csv(website_file)    
    #ensure the date column exists and convert it to datetime
    df_website['date'] = pd.to_datetime(df_website['date (dd-mm-yyyy)'], format='%d-%m-%Y')
    
    #get the missing data (dates strictly after the last existing date)
    df_missing = df_website[df_website['date'] > last_date_existing].copy()
    
    if df_missing.empty:
        #no missing data
        print("found no missing data")
        return
    
    #drop the temporary 'date' column before merging
    df_missing = df_missing.drop(columns=['date'])
    
    #print missing draws -> stays on github action's history
    print(f"found {len(df_missing)} new draws:")
    cols = ['num_1', 'num_2', 'num_3', 'num_4', 'num_5', 'star_1', 'star_2']
    for _, draw in df_missing.iterrows():
        print(*draw[cols].tolist())
    
    #append missing data to the existing DataFrame
    #the temporary 'date' column in df_missing.
    df_new = pd.concat([df_existing.drop(columns=['date']), df_missing], ignore_index=True)

    #save the updated DataFrame back to the original file
    #ensure you are saving without the 'date' column and without the DataFrame index
    df_new.to_csv(existing_file, index=False)
    
def create_metadata_file():
    """
    Creates the dataset-metadata.json file required by the Kaggle CLI version command.
    """
    metadata_path = os.path.join(UPLOAD_DIR, METADATA_FILENAME)
    
    metadata = {
        "title": "EuroMillions Historical Data",
        # THIS ID IS CRITICAL for updating the existing dataset
        "id": DATASET_ID, 
        "licenses": [{"name": "CC BY-NC-SA 4.0"}]
    }

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Generated metadata file at: {metadata_path}")
    
if __name__ == "__main__":  
    #ensure the 'upload/' directory exists
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
          
    #Step 1: Download the latest dataset and metadata from Kaggle    
    kaggle.api.dataset_download_files(DATASET_ID, UPLOAD_DIR, unzip=True)
    
    #Step 2: Download the latest draws from the EuroMillions official website
    year = datetime.datetime.now().year
    html = fetch_page(year)
    data = parse_results(html)
    save_to_csv(data)
    
    if datetime.datetime.now().month == 1:
        #january might be an edge case
        html = fetch_page(year-1)
        data = parse_results(html)
        save_to_csv(data)
    
    #Step 3: Check and append what is missing in the Kaggle dataset
    check_and_append_missing_data()
    
    # Clean-up
    website_file = UPLOAD_DIR+"/euromillions_website.csv"
    if os.path.exists(website_file):
        os.remove(website_file)
        print(f"Removed temporary file: {website_file}")
    
    #Step 4: Create the metadata file needed for the Kaggle upload
    create_metadata_file()