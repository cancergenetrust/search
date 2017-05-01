build:
	docker-compose -f docker-compose-debug.yml build

debug:
	docker-compose -f docker-compose-debug.yml up

run:
	docker-compose up -d
	docker-compose logs -f

down:
	docker-compose -f docker-compose-debug.yml down

references:
	# download reference - about 3.6GB onto a docker volume
	docker exec -it searchcgt_search_1 pyensembl install --release 75 77 --species human 

shell:
	docker exec -it searchcgt_search_1 /bin/bash

crawl:
	# Manual crawl starting at search.cancergenetrust.org
	# docker exec -it searchcgt_search_1 python searchcgt/crawl.py -t 60 QmWPSzKERs6KAjb8QfSXViFqyEUn3VZYYnXjgG6hJwXWYK
	# Manual crawl starting at 
	docker exec -it searchcgt_search_1 python searchcgt/crawl.py -d -t 60 QmWPSzKERs6KAjb8QfSXViFqyEUn3VZYYnXjgG6hJwXWYK

reset:
	# Delete the elastic search index forcing a rebuild
	docker exec -it searchcgt_es_1 curl -X DELETE localhost:9200/cgt

test:
	docker exec -it searchcgt_search_1 py.test -p no:cacheprovider -s -x
