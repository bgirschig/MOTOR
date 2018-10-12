from bs4 import BeautifulSoup
import requests
import json
from urlparse import urljoin
import logging

ACCEPT_STATUS_CODES = [200, 201, 202]

def scrapeUrl(url, scraper_def):
    """parses a product page for useful information about that product
    
    Arguments:
        url {string} -- the url of the page to be parsed
    """
    try:
        with open(scraper_def) as f:
            scraper_def = json.load(f)

        resp = requests.get(url)

        if resp.status_code not in ACCEPT_STATUS_CODES:
            raise Exception('failed request: [{}]'.format(
                resp.status_code))

        pageContent = resp.text
        tree = BeautifulSoup(pageContent, 'html.parser') # TODO: check if lxml *parser* works and is faster
        scraped = scrape(tree, scraper_def)

        return scraped
    except Exception as err:
        errorObj = {
            'error': str(err),
            'baseUrl': url
        }
        logging.warning(errorObj)
        return errorObj
        

def scrape(tree, obj):
    if type(obj) == str or type(obj) == unicode:
        return obj
    elif type(obj) == list:
        return [scrape(tree, item) for item in obj]
    elif type(obj) == dict:
        for key in obj:
            if key.startswith('scrape_'):
                newKey = key.replace('scrape_', '')
                obj[newKey] = scrapeItem(tree, obj[key])
                del obj[key]
            else:
                obj[key] = scrape(tree, obj[key])
        return obj
    else:
        raise Exception('unexpected value type: '+type())

def scrapeItem(tree, selector):
    # handle selectors that don't have modifiers. Defaults to 'text,first'
    if ' & ' not in selector: selector += ' & text,first'

    # retrieve css selector and modifiers
    cssselector, modifiers = selector.split(' & ')
    cssselector = cssselector.strip()
    modifiers = modifiers.split(',')
    modifiers = [modifier.strip() for modifier in modifiers]

    # get elements matching the css selector
    output = tree.select(cssselector)
    if len(output) == 0 and ('required' in modifiers or
                             'first' in modifiers or
                             'last' in modifiers):
        raise KeyError('missing required data for selector {}'.format(selector))

    # apply modifiers (what to get from the html node)
    if 'text' in modifiers:
        output = [item.string for item in output]
    elif 'src' in modifiers:
        output = [item['src'] for item in output]

    # strip the text of whitespaces and newlines
    output = [item.strip() for item in output]

    # apply modifiers (select item in the returned list)
    if 'first' in modifiers:
        output = output[0]
    elif 'last' in modifiers:
        output = output[-1]

    if 'string' in modifiers:
        if type(output) is str or type(output) is unicode:
            pass
        elif type(output) is list:
            output = '&sep;'.join(output)
        elif type(output) is object or type(output) is dict:
            # The deserializer in after effects can't handle 'complex' types
            raise ValueError("html parser can't serialize complex values like objects or dicts")
        else:
            raise ValueError("html parser can't serialize values of type "+type(output))

    return output

if __name__ == '__main__':
    # scraper_def defines what data we want to extract, and how it should be
    # formatted. An element whose key is prefixed with 'scrape_' should be a
    # selector. It will be replaced by the scraped version of itself. The prefix
    # will be removed from the key.
    # This particular def mathes the pattern for a MOTOR render request (without
    # the dynamic elements, like request id, requester, etc...)
    # A selector is a css selector with a list of comma separated flags that
    # define more details on how to handle that item:
    #   - first, last, etc...: only keep the first, last, etc... item from the
    #   css selector. This is useful when you only want one element. otherwise,
    #   you get a list of items
    #   - src: get the src of the element
    #   - text: get the text content of the element
    #   - required: throw an error if the item is not found
    scraper_def = {
        "template": "chanel_test",
        "compName": "main",
        "resources": [
            {"target": "main_image.jpg", "scrape_src": ".product-details__media img & src,first,required"},
            {"target": "variants#.jpg", "scrape_src": ".tint-image & src"},
            {"target": "data.json", "data": {
                'scrape_price': '.product-details__price & text,first,required',
                'scrape_title': '.product-details__title & text,first,required',
                'scrape_description': '.product-details__description & text,first',
                'scrape_reference': '.product-details__reference & text,first',
                'scrape_flags': '.product-details__flags .flag & text',
            }}
        ],
        "encoders": [
            {"presetName": "smol_vid", "filename": "video_a"}
        ]
    }

    # a few urls to try from
    # url = 'https://www.chanel.com/us/makeup/p/168820/joues-contraste-powder-blush/'
    # url = 'https://www.chanel.com/us/makeup/p/170816/vitalumiere-aqua-ultra-light-skin-perfecting-sunscreen-makeup-spf-15/'
    url = 'http://www.google.com'

    print json.dumps(scrapeUrl(url, scraper_def), indent=3)