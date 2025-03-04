import asyncio
import aiohttp
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from urllib.parse import urlparse

async def fetch_url(session: ClientSession, url: str) -> dict:
    """Fetches the webpage content from the url using an asynchronous request."""
    try:
        async with session.get(url, timeout=10) as response:
            # Raise for any HTTP errors
            response.raise_for_status()
            content = await response.text()
            return {'url': url, 'content': content}
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return {'url': url, 'content': None}

def parse_html(html: str) -> dict:
    """Parses HTML content using BeautifulSoup and extracts title and paragraph count."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        title = title_tag.text if title_tag else "No Title"
        paragraphs = [p.text for p in soup.find_all('p')]
        return {'title': title, 'paragraph_count': len(paragraphs)}
    except Exception as e:
        print(f"Error parsing HTML: {str(e)}")
        return {'title': "No Title", 'paragraph_count': 0}

async def fetch_website_data_async(urls: list) -> list:
    """Fetch website data asynchronously for a list of URLs."""
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(fetch_url(session, url))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response['content']:
                parsed_data = parse_html(response['content'])
                results.append({
                    'url': response['url'],
                    **parsed_data
                })
    
    return results

async def main():
    # List of URLs to scrape
    website_list = [
        'https://example.com',
        'https://example.org',
        'https://example.net',
        'https://example.edu',
        'https://example.io'
    ]
    
    # Fetch and process data
    data = await fetch_website_data_async(website_list)
    
    # Display results
    for item in data:
        print(f"Website: {item['url']}")
        print(f"Title: {item['title']}")
        print(f"Paragraph count: {item['paragraph_count']}")
        print("---")

# Run the main function using asyncio
if __name__ == '__main__':
    asyncio.run(main())
