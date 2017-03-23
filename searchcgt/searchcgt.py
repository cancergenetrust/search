import requests
from falcon import HTTP_404
import hug


@hug.get("/stewards")
def stewards():
    """ Return all stewards indexes keyed by address from the last crawl """
    r = requests.get("http://es:9200/cgt/steward/_search/?size=1000")
    return {"stewards": {s["_source"]["address"]: s["_source"] for s in r.json()["hits"]["hits"]}}


@hug.get("/stewards/{address}")
def steward(address, response):
    """ Return a stewards index """
    r = requests.post("http://es:9200/cgt/steward/_search",
                      json={"query": {"match": {"_id": address}}})
    match = r.json()["hits"]["hits"]
    if match:
        return {"steward": match[0]["_source"]}
    else:
        response.status = HTTP_404
        return {"message": "No steward found with address {}".format(address)}


@hug.get("/submissions/search", examples="query=leukemia%20relapse%20JAK2")
def search_submissions(query: hug.types.text):
    """ Search submissions for query """
    print("query", query)
    r = requests.post("http://es:9200/cgt/submission/_search",
                      json={"query": {"match": {"_all": {"query": query, "operator": "and"}}},
                            "size": 100})
    return r.json()


@hug.get("/submissions/{multihash}")
def submission(multihash, response):
    """ Return a submission """
    r = requests.post("http://es:9200/cgt/submission/_search",
                      json={"query": {"match": {"_id": multihash}}})
    match = r.json()["hits"]["hits"]
    if match:
        return {"submission": match[0]["_source"]}
    else:
        response.status = HTTP_404
        return {"message": "No submission found with multihash {}".format(multihash)}
