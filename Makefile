build:
	docker-compose -f docker-compose-debug.yml build

debug:
	docker-compose -f docker-compose-debug.yml up -d
	docker-compose logs -f

up:
	docker-compose up -d
	docker-compose logs -f

down:
	docker-compose -f docker-compose-debug.yml down

filter:
	# Add filters for non-routable addresses so we are not accused of running netscan
	docker exec -it searchcgt_ipfs_1 ipfs swarm filters add /ip4/10.0.0.0/ipcidr/8 /ip4/172.16.0.0/ipcidr/12 /ip4/192.168.0.0/ipcidr/16 /ip4/100.64.0.0/ipcidr/10

references:
	# download reference - about 3.6GB onto a docker volume
	docker exec -it searchcgt_search_1 pyensembl install --release 75 77 --species human 

shell:
	docker exec -it searchcgt_search_1 /bin/bash

crawl:
	# Manual crawl starting at search.cancergenetrust.org
	# docker exec -it searchcgt_search_1 python searchcgt/crawl.py -t 60 QmWPSzKERs6KAjb8QfSXViFqyEUn3VZYYnXjgG6hJwXWYK
	# Manual crawl starting at 
	docker exec -it search_crawl_1 python searchcgt/crawl.py -d -t 300 QmWPSzKERs6KAjb8QfSXViFqyEUn3VZYYnXjgG6hJwXWYK

reset:
	# Delete the elastic search index forcing a rebuild
	docker exec -it searchcgt_es_1 curl -X DELETE localhost:9200/cgt

test:
	docker exec -it searchcgt_search_1 py.test -p no:cacheprovider -s -x

backup:
	docker run --rm -it -v search_es:/search_es:ro -v `pwd`:/backup ubuntu tar -zcvf /backup/search_es.tar /search_es
