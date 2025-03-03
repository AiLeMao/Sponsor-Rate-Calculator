import requests
from lxml import html

def get_ccv_30(username):
    # URL of the website
    url = f"https://sullygnome.com/channel/{username}/30"

    # Headers to mimic a real browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Send a GET request to the website with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using lxml
        tree = html.fromstring(response.content)
        
        # XPath to the average viewer number (from your IMPORTXML formula)
        xpath = "/html/body/div[2]/div[2]/div[4]/div/div[1]/div/div/div[2]/div"
        
        # Extract the text using the XPath
        average_viewer_element = tree.xpath(xpath)
        
        if average_viewer_element:
            # Extract the text, remove commas, and convert it to an integer just in case 
            average_viewer_text = average_viewer_element[0].text.strip()
            average_viewer_number = int(average_viewer_text.replace(",", "")) #just in case we go over 1k and it gets commas and schtuff
            #print(f"The average viewer number is: {average_viewer_number}") DEBUG PRINT
            return average_viewer_number
        else:
            print("Could not find the average viewer number on the page. the webscrapey is brokey, go fix it dummy")
            return None
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None