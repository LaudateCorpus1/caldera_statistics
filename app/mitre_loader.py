#!/usr/bin/env python3

# Mitre file to use is here: https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json
# The database project is https://github.com/mitre/cti

import json
from pprint import pprint
import requests


def extract_tdd(data):
    """ Extracts MITRE tdds from data"""

    res = []
    for ob in data["objects"]:
        if "revoked" in ob and ob["revoked"]:
            continue
        if "external_references" in ob:
            for er in ob["external_references"]:
                if er["source_name"] == "mitre-attack" and er["external_id"].startswith("T") and not er["external_id"].startswith("TA"):
                    new = {"teid": er["external_id"],
                                "url": er["url"],
                                "name": ob["name"],
                                "windows": False,
                                "linux": False,
                                "darwin": False}
                    if "x_mitre_platforms" in ob:
                        if "Linux" in ob["x_mitre_platforms"]:
                            new["linux"] = True
                        if "Windows" in ob["x_mitre_platforms"]:
                            new["windows"] = True
                        if "macOS" in ob["x_mitre_platforms"]:
                            new["darwin"] = True
                    res.append(new)
    return res


def tdds_from_file(filename="../../../cti/enterprise-attack/enterprise-attack.json"):
    """ Get MITRE tdss from a file """

    with open(filename, "rt") as fh:
        data = json.load(fh)
        return extract_tdd(data)

def tdds_from_url(url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"):
    """ Get MITRE tdss from a url """
    r = requests.get(url)
    return extract_tdd(r.json())


if __name__ == "__main__":
    ex = tdds_from_url()
    pprint(ex)
    print(len(ex))