import hug
import requests


@hug.get('/stewards')
def stewards():
    """ Return a list of stewards """
    r = requests.get("http://es:9200/cgt/steward/_search/?size=1000")
    return r.json()
