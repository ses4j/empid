GROUPS = {
    "FW": {
        "code": "FW",
        "name": "Confusing Fall Warblers (Eastern)",
        "media_filter_params": {
            "bmo": 8,
            "emo": 10,
        },
        "choices": [
            {"name": "Pine Warbler", "taxonCode": "pinwar"},
            {"name": "Bay-breasted Warbler", "taxonCode": "babwar"},
            {"name": "Tennessee Warbler", "taxonCode": "tenwar"},
            {"name": "Orange-Crowned Warbler", "taxonCode": "orcwar"},
            {"name": "Nashville Warbler", "taxonCode": "naswar"},
            {"name": "Connecticut Warbler", "taxonCode": "conwar"},
            {"name": "Cape May Warbler", "taxonCode": "camwar"},
            {"name": "Blackpoll Warbler", "taxonCode": "bkpwar"},
            {"name": "Chestnut-Sided Warbler", "taxonCode": "chswar"},
            {"name": "Blackburnian Warbler", "taxonCode": "bkbwar"},
            {"name": "Prairie Warbler", "taxonCode": "prawar"},
        ],
    },

    "EE": {
        "code": "EE",
        "name": "Eastern Empids",
        "media_filter_params": {
            "regionCode": "US",
        },
        "choices": [
            {"name": "Alder Flycatcher", "taxonCode": "aldfly"},
            {"name": "Willow Flycatcher", "taxonCode": "wilfly"},
            {"name": "Least Flycatcher", "taxonCode": "leafly"},
            {"name": "Yellow-bellied Flycatcher", "taxonCode": "yebfly"},
            {"name": "Acadian Flycatcher", "taxonCode": "acafly"},
            {"name": "Eastern Wood-Pewee", "taxonCode": "eawpew"},
            # {'name': "Eastern Phoebe", "taxonCode": ""},
        ],
    }
}


CONFIDENCES = [
    {"name": "Low", "abbrev": "L", "value": 1},
    {"name": "Medium", "abbrev": "M", "value": 5},
    {"name": "High", "abbrev": "H", "value": 10},
]

