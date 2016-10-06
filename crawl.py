#!/usr/bin/env python2.7
import time
import argparse
import requests
from elasticsearch import Elasticsearch


def update_submissions(es, steward, args):
    """
    Add any submissions that don't already exist in the index.

    REMIND: Adds submissions as separate doctype with a parent
    reference via "steward". This means a submission by hash
    only lives in one steward and therefore first one crawled
    will win. Alternative would be compound id, or including
    the full submission record in the steward itself...
    """
    for multihash in steward["submissions"]:
        if not es.exists(index="cgt", doc_type="submission",
                         parent=steward["address"], id=multihash):
            print("Adding submission {}".format(multihash))
            r = requests.get("http://ipfs:8080/ipfs/{}".format(multihash), timeout=args.timeout)
            assert(r.status_code == requests.codes.ok)
            submission = r.json()
            submission["steward"] = steward["address"]  # parent pointer
            es.create(index="cgt", doc_type="submission", id=multihash,
                      parent=steward["address"], body=submission)


def index_steward(es, steward, args):
    """
    Update the steward's index in elastic search
    """
    print("Indexing steward {}".format(steward["domain"]))
    if es.exists(index="cgt", doc_type="steward", id=steward["address"]):
        res = es.get(index="cgt", doc_type="steward", id=steward["address"], fields="multihash")
        if res["fields"]["multihash"][0] == steward["multihash"]:
            print("Steward {} has not changed, skipping".format(steward["domain"]))
        else:
            print("Updating steward: {}".format(steward["domain"]))
            if not args.skip_submissions:
                update_submissions(es, steward, args)
            es.index(index="cgt", doc_type="steward", id=steward["address"], body=steward)
    else:
        print("New steward: {} {}".format(steward["domain"], steward["address"]))
        if not args.skip_submissions:
            update_submissions(es, steward, args)
        es.index(index="cgt", doc_type="steward", id=steward["address"], body=steward)


def find_stewards(start, timeout):
    """
    Find the address of all stewards via breadth first search
    """
    stewards, queue = {}, [start]
    while queue:
        address = queue.pop(0)
        if address not in stewards:
            try:
                # Resolve its address
                r = requests.get("http://ipfs:5001/api/v0/name/resolve?arg={}".format(
                    address), timeout=timeout)
                assert(r.status_code == requests.codes.ok)
                multihash = r.json()["Path"].rsplit('/')[-1]
                print("Resolved to {}".format(multihash))

                # Get its index
                r = requests.get("http://ipfs:8080/ipfs/{}".format(multihash), timeout=timeout)
                assert(r.status_code == requests.codes.ok)
                steward = r.json()
                print(steward["domain"])
                steward["multihash"] = multihash  # so we can easily detect changes
                steward["address"] = address  # convenience for guis

                # Add to list of stewards
                stewards[address] = steward
                queue.extend(set(steward["peers"]) - set(stewards.keys()))
            except Exception as e:
                print("Skipping peer {} problems resolving: {}".format(address, e.message))

    return stewards


def main():
    """
    Cancer Gene Trust Crawler

    Crawls the CGT build an elastic search index of all stewards and,f.v
    submissions.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("-t", "--timeout", type=int, default=5,
                        help="Seconds to wait for IPNS to resolve a steward")
    parser.add_argument("-s", "--skip_submissions", action='store_true', default=False,
                        help="Skip submissions, only find stewards")
    parser.add_argument("-i", "--interval", type=int, default=0,
                        help="Minutes between crawls")
    parser.add_argument("address", nargs='?', default="",
                        help="Address of steward to start crawl")
    args = parser.parse_args()

    es = Elasticsearch(hosts=["es"])

    # Create parent child relationship between stewards and submissions
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

    while True:
        if args.address:
            address = args.address
        else:
            address = requests.get("http://ipfs:5001/api/v0/id").json()["ID"]
        start = time.time()
        print("Starting crawl at {} from {}".format(time.asctime(time.localtime(start)), address))
        stewards = find_stewards(address, args.timeout)
        print("Found {} stewards".format(len(stewards)))

        for address, steward in stewards.iteritems():
            try:
                index_steward(es, steward, args)
            except Exception as e:
                print("Problems indexing {}: {}".format(steward["domain"], e.message))

        end = time.time()
        print("Finished crawl at {} taking {} seconds".format(
            time.asctime(time.localtime(end)), end - start))
        if args.interval:
            print("Sleeping for {} minutes...".format(args.interval))
            time.sleep(args.interval * 60)
        else:
            break


if __name__ == '__main__':
    main()
