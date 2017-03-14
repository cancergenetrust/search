import hug
import requests


@hug.get("/stewards")
def stewards():
    """ Return a list of stewards """
    r = requests.get("http://es:9200/cgt/steward/_search/?size=1000")
    return r.json()


@hug.get("/submissions/search", examples="query=leukemia%20relapse%20JAK2")
def search_submissions(query: hug.types.text):
    """ Search submissions for query """
    print("query", query)
    r = requests.post("http://es:9200/cgt/submission/_search",
                      json={"query": {"match": {"_all": {"query": query, "operator": "and"}}},
                            "size": 100})
    return r.json()


@hug.get("/ipfs/{multihash}")
def ipfs(multihash):
    try:
        r = requests.get("http://ipfs:8080/ipfs/{}".format(multihash), timeout=5.0)
        return r.content
    except:
        return("unreachable", 408)
