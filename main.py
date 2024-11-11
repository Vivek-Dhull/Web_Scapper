import logging, time, random
from urllib.parse import urljoin
import requests, json
from bs4 import BeautifulSoup
import pandas as pd
from robots_checker import can_scrape

def scrape_quotes(base_url):
    data = []
    url = base_url  # Start with the base URL
    while url:
        try:
            # Set up headers
            headers = {
                'User -Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Raise an error for bad responses

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract quotes
            for item in soup.find_all('div', class_='quote'):
                text = item.find('span', class_='text').text.strip()
                author = item.find('small', class_='author').text.strip()
                tags = [tag.text for tag in item.find_all('a', class_='tag')]
                data.append({'Quote': text, 'Author': author, 'Tags': ', '.join(tags)})

            # Find the link to the next page
            next_page = soup.find('li', class_='next')
            if next_page:
                relative_next_url = next_page.find('a')['href']
                url = urljoin(base_url, relative_next_url)  # Combine base URL with relative URL
            else:
                url = None  # No more pages

            # Log the progress
            logging.info(f'Scraped page: {url}')

            # Delay to prevent overwhelming the server
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            logging.error(f'Error occurred: {e}')
            break

    return data


def save_data(data, file_type):
    """
    Saves the scraped data to a file in the specified format.
    
    :param data: The data to save.
    :param file_type: The file type to save the data as ('csv' or 'json').
    """
    if file_type == 'csv':
        df = pd.DataFrame(data)
        df.to_csv('spyder/quotes.csv', index=False)
        print("Data saved to quotes.csv")
    elif file_type == 'json':
        with open('spyder/quotes.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print("Data saved to quotes.json")
    else:
        print("Unsupported file type. Please choose 'csv' or 'json'.")

def main():
    # Get user input for the URL and file type
    url = input("Enter the URL to scrape (e.g., http://quotes.toscrape.com): ")
    file_type = input("Enter the file type to save data (csv/json): ").strip().lower()
    if can_scrape(url):
        # Scrape the quotes
        quotes = scrape_quotes(url)
        # Save the data
        save_data(quotes, file_type)
    else:
        logging.info("Scraping aborted due to robots.txt restrictions.")


if __name__ == "__main__":
    main()
