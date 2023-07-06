import requests
from bs4 import BeautifulSoup


from srai_gpt_function.function.gpt_function import GptFunction


class GetContactInfo(GptFunction):
    """Create a function"""

    def __init__(self):
        super().__init__("get_contact_info")

    def get_descriptor(self) -> dict:
        return {"name": "get_contact_info", "description": "This function takes a URL as input and returns the contact information found on the website.\n\nParameters:\n    url (str): The URL of the website to scrape.\n\n", "parameters": {"type": "object", "properties": {"url": {"type": "str", "description": "The python code that should consitute the function"}}, "required": ["url"]}}

    def run(url: str) -> str:
        """
        This function takes a URL as input and returns the contact information found on the website.
    
        Parameters:
            url (str): The URL of the website to scrape.
    
        Returns:
            str: The contact information found on the website.
    
        """
        # Make a GET request to the website
        response = requests.get(url)
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the contact information
        contact_info = soup.find('contact-info').get_text()
        
        return contact_info
