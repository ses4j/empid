import logging
import requests, pprint

logger = logging.getLogger(__name__)

def get_image_urls(species, taxonCode='', count=50, sort_by="rating_rank_desc"):
    # taxonCode = "aldfly"

    # sort_by = "upload_date_desc"
    url = (f"https://ebird.org/media/catalog.json?searchField=species&q={species}"
           f"&taxonCode={taxonCode}&&mediaType=p&view=Gallery&sort={sort_by}"
           f"&count={count}")

    r = requests.get(url)
    logger.info(f"Fetched new urls for {taxonCode}...")
    data = r.json()
    # image_urls = [_['largeUrl'] for _ in ]

    # return image_urls
    # import pdb; pdb.set_trace()
    return data['results']['content']
    
# get_image(species="Alder Flycatcher - Empidonax alnorum", taxonCode="aldfly")