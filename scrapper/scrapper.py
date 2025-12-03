import requests
from bs4 import BeautifulSoup
import csv
import os
import datetime

URL = "https://www.euro-millions.com/results-history-"

def fetch_page(url: str) -> str:
    """Fetches the page of the URL

    Args:
        url (str): url of the website

    Returns:
        str: content of the response, in unicode
    """
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def parse_results(html: str) -> list:
    """Parses the data from the html content

    Args:
        html (str): content of the request

    Returns:
        results (list): list of json formatted draws
    """ 
    soup = BeautifulSoup(html, "html.parser")
    results = []
    
    for draw in soup.select("tr.resultRow"):
        #date scrapping
        link = draw.select_one("td.date a")  # the <a href="/results/28-11-2025">
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
       
def save_to_csv(data: list, upload_dir: str, exists: bool) -> None:
    """Generates the .csv file with the new data

    Args:
        data (list): list of json formatted draws
        upload_dir (str): upload folder name
        exists (bool): true if it already existed
    """
    filename = upload_dir+"/euromillions.csv"
    keys = ["date (dd-mm-yyyy)", "num_1", "num_2", "num_3", "num_4", "num_5", "star_1", "star_2", "jackpot (in EUR)"]
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if not exists: writer.writeheader()
        for draw in data:
            writer.writerow(draw) 
        
if __name__ == "__main__":
    year = str(datetime.datetime.now().year)
    html = fetch_page(URL+year)
    
    data = parse_results(html)

    exists = True
    upload_dir = "upload"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        exists = False
    save_to_csv(data, upload_dir, exists)