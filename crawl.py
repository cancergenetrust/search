#!/usr/bin/env python2.7
import argparse
import traceback
import requests
from elasticsearch import Elasticsearch


def update_submissions(es, steward, timeout):
    """
    Add any submissions that don't already exist in the index.

    REMIND: Adds submissions as separate doctype with a parent
    reference via "steward". This means a submission by hash
    only lives in one steward and therefore first one crawled
    will win. Alternative would be compound id, or including
    the full submission record in the steward itself...
    """
    for multihash in steward["submissions"]:
        if es.exists(index="cgt", doc_type="submission", parent=steward["address"], id=multihash):
            print("Submission already exists {}".format(multihash))
        else:
            print("Adding submission {}".format(multihash))
            r = requests.get("http://ipfs:8080/ipfs/{}".format(multihash), timeout=timeout)
            if r.status_code == requests.codes.ok:
                submission = r.json()
                submission["steward"] = steward["address"]  # parent pointer
                es.create(index="cgt", doc_type="submission", id=multihash,
                          parent=steward["address"], body=submission)
            else:
                print("Problems getting submission {} : {}".format(multihash, r.status_code))


def update_steward(es, address, timeout):
    """
    Resolve and update the steward and submissions documents and
    return its peer list.
    """
    print("Updating steward {}".format(address))
    try:
        r = requests.get("http://ipfs:5001/api/v0/name/resolve?arg={}".format(
            address), timeout=timeout)
        assert(r.status_code == requests.codes.ok)
        multihash = r.json()["Path"].rsplit('/')[-1]
        print("Resolved to {}".format(multihash))
        r = requests.get("http://ipfs:8080/ipfs/{}".format(multihash), timeout=timeout)
        assert(r.status_code == requests.codes.ok)
        steward = r.json()
        steward["multihash"] = multihash  # so we can easily detect changes in submission list
        steward["address"] = address  # convenience for guis
        print("Found {} Submissions".format(len(steward["submissions"])))

        if es.exists(index="cgt", doc_type="steward", id=address):
            res = es.get(index="cgt", doc_type="steward", id=address, fields="multihash")
            if res["fields"]["multihash"][0] == multihash:
                print("Steward {} {} has not changed, skipping".format(steward["domain"], address))
            else:
                print("Updating steward {} {}".format(steward["domain"], address))
                es.index(index="cgt", doc_type="steward", id=address, body=steward)
                update_submissions(es, steward, timeout)
        else:
            es.index(index="cgt", doc_type="steward", id=address, body=steward)
            update_submissions(es, steward, timeout)

        return steward["peers"]
    except Exception as e:
        traceback.print_exc()
        print("Skipping peer {} problems resolving: {}".format(
            address, e.message))


def crawl(es, address, timeout, depth):
    if depth == 0:
        return

    try:
        print("Crawling {} depth = {}".format(address, depth))
        peers = update_steward(es, address, timeout)
        for address in peers:
            crawl(es, address, timeout, depth-1)
    except Exception as e:
        traceback.print_exc()
        print("Skipping peer {} problems resolving: {}".format(address, e.message))


def main():
    """
    Cancer Gene Trust Crawler

    Crawls the CGT build an elastic search index of all stewards and,f.v
    submissions.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("-t", "--timeout", type=int, default=5,
                        help="Seconds to wait for IPNS to resolve a steward")
    parser.add_argument("-d", "--depth", type=int, default=2,
                        help="How deep to follow the peer graph")
    parser.add_argument("address", nargs='?', default="",
                        help="Address of steward to start crawl")
    args = parser.parse_args()

    es = Elasticsearch(hosts=["es"])
    es.indices.create(index="cgt", ignore=400, body={
        "mappings": {
            "steward": {},
            "submission": {
                "_parent": {
                    "type": "steward"
                }
            }
        }
    })

    if args.address:
        crawl(es, args.address, args.timeout, args.depth)
    else:
        # Default to crawling the steward attached to the linked ipfs
        crawl(es, requests.get("http://ipfs:5001/api/v0/id").json()["ID"], args.timeout, args.depth)


if __name__ == '__main__':
    main()
