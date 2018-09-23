from bs4 import BeautifulSoup
import requests

def parseUrl(url):
    """parses a product page for useful information about that product
    
    Arguments:
        url {string} -- the url of the page to be parsed
    """

    resp = requests.get(url)
    return parse(resp.text)

def parse(html_doc):
    """parses a product page for useful information about that product
    
    Arguments:
        html_doc {string} -- the raw contents of the html page
    
    Returns:
        Dictionnary -- a dictionnary containing the parsed values
    """

    # get page doc tree
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    # get 'list' items (images, flags, variants, etc)
    variants = set(soup.find_all(class_='tint-image'))
    variants = [variant['src'] for variant in variants]
    
    flags = soup.select('.product-details__flags .flag')
    flags = [flag.string for flag in flags]

    images = soup.select('.product-details__media img')
    images = [image['src'] for image in images]

    # combine all elements in a single object
    output = {
        'title': soup.find(class_='product-details__title').string,
        'description': soup.find(class_='product-details__description').string,
        'ref': soup.find(class_='product-details__reference').string,
        'price': soup.find(class_='product-details__price').string,
        'flags': flags,
        'variants': variants,
        'images': images
    }

    return output

if __name__ == '__main__':
    print parseUrl('https://www.chanel.com/us/makeup/p/168820/joues-contraste-powder-blush/')