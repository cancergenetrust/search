build:
	docker-compose -f docker-compose-debug.yml build

debug:
	docker-compose -f docker-compose-debug.yml up

down:
	docker-compose -f docker-compose-debug.yml down

references:
	# download reference - about 3.6GB onto a docker volume
	docker exec -it searchcgt_search_1 pyensembl install --release 75 77 --species human 

shell:
	docker exec -it searchcgt_search_1 /bin/bash

crawl:
	# Manual crawl starting at search.cancergenetrust.org
	docker exec -it searchcgt_search_1 python searchcgt/crawl.py -t 60 QmWPSzKERs6KAjb8QfSXViFqyEUn3VZYYnXjgG6hJwXWYK

reset:
	# Delete the elastic search index forcing a rebuild
	docker exec -it searchcgt_es_1 curl -X DELETE localhost:9200/cgt

test:
	docker exec -it searchcgt_search_1 py.test -p no:cacheprovider -s -x

# es:
# 	docker run -d -p 9200:9200 -p 9300:9300 \
# 		-v /mnt/elasticsearch:/usr/share/elasticsearch/data \
# 		--name=es elasticsearch:latest -Des.network.host=0.0.0.0

# nginx:
# 	docker run -d --name nginx \
# 		--link cgtd:cgtd \
# 		--link ipfs:ipfs \
# 		--link es:es \
# 		-p $(nginx_port):80 \
# 		-v `pwd`/default.conf:/etc/nginx/conf.d/default.conf:ro \
# 		-v `pwd`/www:/usr/share/nginx/html:ro \
# 		nginx

# stop:
# 	docker stop crawler || true && docker rm crawler || true
# 	docker stop es || true && docker rm es || true
# 	docker stop nginx || true && docker rm nginx || true



# debug:
# 	docker run -it --rm \
# 		-v `pwd`:/usr/src/app:ro \
# 		-v `pwd`/pyensembl:/root/.cache/pyensembl \
# 		--link ipfs:ipfs --link es:es search-cgt -t 60 -i 5

# run:
# 	docker run -d --name crawler \
# 		-v `pwd`/pyensembl:/root/.cache/pyensembl \
# 		--link ipfs:ipfs --link es:es search-cgt -t 60 -i 5
