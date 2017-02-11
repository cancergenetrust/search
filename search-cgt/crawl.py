#!/usr/bin/env python3
import sys
import time
import datetime
import logging
import argparse
import requests
import traceback
from elasticsearch import Elasticsearch

from annotate import vcf2genes


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
                logging.info("Resolved to {}".format(multihash))

                # Get its index
                r = requests.get("http://ipfs:8080/ipfs/{}".format(multihash), timeout=timeout)
                assert(r.status_code == requests.codes.ok)
                steward = r.json()
                logging.info(steward["domain"])
                steward["multihash"] = multihash  # so we can easily detect changes
                steward["address"] = address  # convenience for guis
                steward["resolved"] = datetime.datetime.utcnow().isoformat()

                # Add to list of stewards
                stewards[address] = steward
                queue.extend(set(steward["peers"]) - set(stewards.keys()))
            except Exception as e:
                logging.error("Skipping peer {} problems resolving: {}".format(address, e))

    return stewards


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
            logging.info("Adding submission {}".format(multihash))
            r = requests.get("http://ipfs:8080/ipfs/{}".format(multihash), timeout=args.timeout)
            assert(r.status_code == requests.codes.ok)
            submission = r.json()
            submission["steward"] = steward["address"]  # parent pointer

            # Annotate based on files
            genes = set()
            for f in submission["files"]:
                if f["name"].endswith(".vcf"):
                    logging.info("Annotating {}".format(f["name"]))
                    try:
                        r = requests.get("http://ipfs:8080/ipfs/{}".format(f["multihash"]),
                                         timeout=args.timeout)
                        assert(r.status_code == requests.codes.ok)
                        genes.update(vcf2genes(r.content))
                    except:
                        logging.error("Problems summarizing vcf file: {} {}".format(
                            f["name"], f["multihash"]))
                        traceback.print_exc()
            if genes:
                submission["_genes"] = list(genes)  # _ so we don't clash with field
                logging.info("Added annotation {}".format(submission["_genes"]))
            es.create(index="cgt", doc_type="submission", id=multihash,
                      parent=steward["address"], body=submission)


def index_steward(es, steward, args):
    """
    Update the steward's index in elastic search
    """
    logging.info("Indexing steward {}".format(steward["domain"]))
    if es.exists(index="cgt", doc_type="steward", id=steward["address"]):
        res = es.get(index="cgt", doc_type="steward", id=steward["address"], fields="multihash")
        if res["fields"]["multihash"][0] == steward["multihash"]:
            logging.info("Steward {} has not changed, skipping".format(steward["domain"]))
        else:
            logging.info("Updating steward: {}".format(steward["domain"]))
            if not args.skip_submissions:
                update_submissions(es, steward, args)
            es.index(index="cgt", doc_type="steward", id=steward["address"], body=steward)
    else:
        logging.info("New steward: {} {}".format(steward["domain"], steward["address"]))
        if not args.skip_submissions:
            update_submissions(es, steward, args)
        es.index(index="cgt", doc_type="steward", id=steward["address"], body=steward)


def main():
    """
    Cancer Gene Trust Crawler

    Crawls the CGT build an elastic search index stewards and submissions
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("-t", "--timeout", type=int, default=20,
                        help="Seconds to wait for IPNS to resolve a steward")
    parser.add_argument("-s", "--skip_submissions", action='store_true', default=False,
                        help="Skip submissions, only find stewards")
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

    start = time.time()
    logging.info("Starting crawl at {}".format(time.asctime(time.localtime(start))))

    if args.address:
        address = args.address
    else:
        # Default to starting with the local cgtd
        address = requests.get("http://ipfs:5001/api/v0/id").json()["ID"]
    logging.info("Starting at {}".format(address))
    stewards = find_stewards(address, args.timeout)
    logging.info("Found {} stewards".format(len(stewards)))

    for address, steward in stewards.items():
        try:
            index_steward(es, steward, args)
        except Exception as e:
            logging.error("Problems indexing {}: {}".format(steward["domain"], e))

    end = time.time()
    logging.info("Finished crawl at {} taking {} seconds".format(
        time.asctime(time.localtime(end)), end - start))


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
