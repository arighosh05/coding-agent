### code

```
def fetch_website_data(urls):
    results = []
    
    # Missing imports for 'requests' and 'BeautifulSoup'
    
    for url in urls:
        # Synchronous HTTP requests that block execution
        response = requests.get(url, timeout=10)
        
        # Processing done synchronously in sequence
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title').text
        paragraphs = [p.text for p in soup.find_all('p')]
        
        results.append({
            'url': url,
            'title': title,
            'paragraph_count': len(paragraphs)
        })
    
    return results

# Using the function
website_list = [
    'https://example.com',
    'https://example.org',
    'https://example.net',
    'https://example.edu',
    'https://example.io'
]

# This will take a long time as each request happens one after another
data = fetch_website_data(website_list)

# Process results
for item in data:
    print(f"Website: {item['url']}")
    print(f"Title: {item['title']}")
    print(f"Paragraph count: {item['paragraph_count']}")
    print("---")
```

### context

```
a python web scraping script
```
