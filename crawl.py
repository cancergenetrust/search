#!/usr/bin/env python2.7
import argparse
import requests


def update(submissions):
    """ Add any submissions that are not already in the index """
    for multihash in submissions:
        url = "http://127.0.0.1:9200/submissions/fields/{}".format(multihash)
        r = requests.head(url)
        if r.status_code != requests.codes.ok:
            print("{} missing from index".format(multihash))
            r = requests.get("http://127.0.0.1:8080/ipfs/{}".format(multihash))
            r.raise_for_status()
            print("Got submissions data, adding to index")
            r = requests.put(url, data=r.content)
            r.raise_for_status()
            print("Added to index")
        else:
            print("{} already in index".format(multihash))


def crawl(address, crawled):
    """ Recursively crawl address and its peers """
    print("Crawling {}".format(address))
    r = requests.get("http://127.0.0.1:8080/ipns/{}".format(address))
    if r.status_code != requests.codes.ok:
        print("Error: unable to resolve address")
    else:
        index = r.json()
        print("Domain: {}".format(index["domain"]))
        update(index["submissions"])
        for p in index["peers"]:
            if p not in crawled:
                crawled.append(p)
                crawl(p, crawled)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Builds an elastic index by crawling CGT")
    parser.add_argument("address", nargs='?',
                        default="QmaWcGneeMEx6unN8iJCVCxP7Qcv4T91pjuZj9drJrdih1",
                        help="steward ipns address")
    args = parser.parse_args()
    print("Crawling starting at {}".format(args.address))
    crawl(args.address, crawled=[])
