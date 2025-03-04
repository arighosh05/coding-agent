import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch(session, url):
    """Fetch data asynchronously from a given URL."""
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                return {'url': url, 'error': f'HTTP {response.status}'}
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else "No Title"
            
            paragraphs = [p.text for p in soup.find_all('p')]
            
            return {
                'url': url,
                'title': title,
                'paragraph_count': len(paragraphs)
            }
    
    except Exception as e:
        return {'url': url, 'error': str(e)}

async def fetch_all(urls):
    """Fetch multiple websites concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# Using the function
website_list = [
    'https://example.com',
    'https://example.org',
    'https://example.net',
    'https://example.edu',
    'https://example.io'
]

# Run the async event loop
data = asyncio.run(fetch_all(website_list))

# Process results
for item in data:
    print(f"Website: {item['url']}")
    if 'error' in item:
        print(f"Error: {item['error']}")
    else:
        print(f"Title: {item['title']}")
        print(f"Paragraph count: {item['paragraph_count']}")
    print("---")
