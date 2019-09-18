import logging
import requests, pprint

logger = logging.getLogger(__name__)

def get_image_urls(species, taxonCode='', count=50, sort_by="rating_rank_desc", regionCode='', mr='MCUSTOM', bmo=1, emo=12, yr='YPAST10'):
    # taxonCode = "aldfly"

    # https://ebird.org/media/catalog.json?searchField=user&
    # q=&taxonCode=&hotspotCode=&regionCode=US&customRegionCode=&userId=&_mediaType=&mediaType=p&species=&
    # region=United+States+(US)&hotspot=&customRegion=&mr=M8TO11&bmo=1&emo=12&yr=YALL&by=1900&ey=2019&user=&
    # view=Gallery&sort=upload_date_desc&includeUnconfirmed=T&_req=&subId=&catId=&_spec=&specId=&collectionCatalogId=&
    # dsu=-1&initialCursorMark=AoJ4vt%2BcmO0CKTE3NzA3NjQ5MQ%3D%3D&count=50&_=1568490511079

    # https://ebird.org/media/catalog.json?searchField=user&q=&taxonCode=&hotspotCode=&regionCode=US&customRegionCode=
    # &userId=&_mediaType=&mediaType=p&species=&region=United+States+(US)&hotspot=&customRegion=
    # &mr=M8TO11&bmo=1&emo=12&yr=YALL&by=1900&ey=2019&user=&view=Gallery&sort=upload_date_desc
    # &includeUnconfirmed=T&_req=&subId=&catId=&_spec=&specId=&collectionCatalogId=
    # &dsu=-1&initialCursorMark=AoJwp9WbmO0CKTE3NzA3NTM0MQ%3D%3D&count=50&_=1568490511080

    # sort_by = "upload_date_desc"
    url = (f"https://ebird.org/media/catalog.json?searchField=species&q={species}"
           f"&taxonCode={taxonCode}&&mediaType=p&regionCode={regionCode}&view=Gallery&sort={sort_by}"
           f"&mr={mr}&bmo={bmo}&emo={emo}&yr={yr}"
           f"&count={count}")

    r = requests.get(url)
    assert r.status_code == 200, str(r.json())
    logger.info(f"Fetched new urls for {taxonCode}...\n{url}\nreturn status={r.status_code}")
    data = r.json()
    # image_urls = [_['largeUrl'] for _ in ]

    # return image_urls
    # import pdb; pdb.set_trace()
    return data['results']['content']
    
# get_image(species="Alder Flycatcher - Empidonax alnorum", taxonCode="aldfly")