#!/usr/bin/env python2.7
import argparse
import requests
from elasticsearch import Elasticsearch


def crawl(es, address, depth=2, stewards={}):
    if depth == 0:
        return stewards

    try:
        print("Crawling {} depth = {}".format(address, depth))
        r = requests.get("http://ipfs:8080/ipns/{}".format(address), timeout=5.0)
        print(r.status_code)
        assert(r.status_code == requests.codes.ok)
        steward = r.json()
        print("{} Submissions".format(len(steward["submissions"])))
        if es.exists(index="stewards", doc_type="indexes", id=address):
            es.delete(index="stewards", doc_type="indexes", id=address)
        es.create(index="stewards", doc_type="indexes", id=address, body=steward)
        stewards[address] = steward
        for multihash in steward["submissions"]:
            r = requests.get("http://ipfs:8080/ipfs/{}".format(multihash), timeout=5.0)
            if r.status_code == requests.codes.ok:
                submission = r.json()
                if not es.exists(index="submissions", doc_type="fields", id=multihash):
                    print("Adding submission {}".format(multihash))
                    es.create(index="submissions", doc_type="fields", id=multihash,
                              body=submission)
            else:
                print("Problems getting submission {} : {}".format(multihash,
                                                                   r.status_code))
        for address in steward["peers"]:
            if address in stewards:
                print("Skipping {}, already resolved".format(address))
            else:
                crawl(es, address, depth-1, stewards)
    except Exception as e:
        stewards[address] = {"domain": "unreachable",
                             "peers": [], "submissions": []}
        print("Skipping peer {} problems resolving: {}".format(
            address, e.message))

    # if es.exists(index="stewards", doc_type="indexes", id=address):
    #     print("Existing steward record already in es")
    #     res = es.get(index="stewards", doc_type="indexes", id=address)
    #     saved = res["_source"]

    # peers = None
    # if not latest and not saved:
    #     print("ERROR: Unable to resolve or find anything in es")
    #     return
    # elif not latest and saved:
    #     print("ERROR: Unable to resolve steward but have saved, will crawl")
    #     peers = saved["peers"]
    # elif latest and not saved:
    #     print("Found new steward: {} {}".format(latest["domain"], address))
    #     es.create(index="stewards", doc_type="indexes", id=address, body=latest)
    #     peers = latest["peers"]
    #     for multihash in latest["submissions"]:
    #         submission = json.loads(ipfs.cat(multihash))
    #         if not es.exists(index="submissions", doc_type="fields", id=multihash):
    #             print("Adding submission {}".format(multihash))
    #             es.create(index="submissions", doc_type="fields", id=multihash,
    #                       body=submission)
    # else:
    #     if latest["multihash"] == saved["multihash"]:
    #         print("Nothing changed")
    #         peers = latest["peers"]
    #     else:
    #         print("Stewared updated")
    #         es.create(index="stewards", doc_type="indexes", id=address, body=latest)
    #         for multihash in latest["submissions"]:
    #             submission = json.loads(ipfs.cat(multihash))
    #             if not es.exists(index="submissions", doc_type="fields", id=multihash):
    #                 print("Adding submission {}".format(multihash))
    #                 es.create(index="submissions", doc_type="fields",
    #                           id=multihash, body=submission)
    #         peers = latest["peers"]

    # if depth > 0:
    #     for peer in peers:
    #         crawl(ipfs, es, peer, depth - 1)


def main():
    """
    Cancer Gene Trust Crawler

    Crawls the CGT build an elastic search index of all stewards and,f.v
    submissions.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("address", nargs='?', default="",
                        help="Address of steward to start")
    args = parser.parse_args()

    es = Elasticsearch(hosts=["es"])

    if not args.address:
        crawl(es, requests.get("http://ipfs:5001/api/v0/id").json()["ID"], 3)
    else:
        crawl(es, args.address)


if __name__ == '__main__':
    main()
