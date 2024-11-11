import requests
import logging
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)

def can_scrape(url, user_agent='*'):
    """
    Check if the website's robots.txt allows scraping for the specified user-agent.
    
    :param url: The URL of the website to check.
    :param user_agent: The user-agent string to check permissions for.
    :return: True if scraping is allowed, False otherwise.
    """
    # Parse the base URL to get the domain
    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # Fetch the robots.txt file
    robots_url = f"{domain}/robots.txt"
    try:
        response = requests.get(robots_url)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.RequestException as e:
        logging.error(f"Failed to fetch robots.txt: {e}")
        # Ask the user if they want to continue scraping
        user_input = input("robots.txt not found or inaccessible. Do you want to continue scraping? (yes/no): ").strip().lower()
        if user_input in ['yes', 'y']:
            logging.info("User  chose to continue scraping despite missing robots.txt.")
            return True
        else:
            logging.info("User  chose to abort scraping.")
            return False

    # Parse the robots.txt file
    lines = response.text.splitlines()
    user_agent_found = False
    disallow_paths = []

    for line in lines:
        line = line.strip()
        if line.lower().startswith('user-agent:'):
            if user_agent in line or user_agent == '*':
                user_agent_found = True
            else:
                user_agent_found = False  # Reset if we encounter a different user-agent

        if user_agent_found and line.lower().startswith('disallow:'):
            path = line.split(':', 1)[1].strip()
            disallow_paths.append(path)

    # Check if scraping is allowed
    if disallow_paths:
        logging.info(f"Scraping is not allowed for user-agent '{user_agent}'. Disallowed paths: {disallow_paths}")
        return False

    logging.info(f"Scraping is allowed for user-agent '{user_agent}'.")
    return True
