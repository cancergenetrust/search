build:
	docker build -t search-cgt .

es:
	docker run -d -p 9200:9200 -p 9300:9300 \
		-v /mnt/elasticsearch:/usr/share/elasticsearch/data \
		--name=es elasticsearch:latest -Des.network.host=0.0.0.0
	# docker exec -it es plugin install jettro/elasticsearch-gui

nginx:
	docker run -d --name nginx \
		--link cgtd:cgtd \
		--link ipfs:ipfs \
		--link es:es \
		-p 80:80 \
		-v `pwd`/default.conf:/etc/nginx/conf.d/default.conf:ro \
		-v `pwd`/www:/usr/share/nginx/html:ro \
		nginx

stop:
	docker stop crawler || true && docker rm crawler || true
	docker stop es || true && docker rm es || true
	docker stop nginx || true && docker rm nginx || true

reset:
	curl -X DELETE localhost:9200/cgt
	curl localhost:9200/_cat/indices?v

run:
	docker run -d --name crawler --link ipfs:ipfs --link es:es search-cgt -t 60 -i 5

debug:
	docker run -it --rm -v `pwd`:/app:ro --link ipfs:ipfs --link es:es search-cgt -t 60 -i 5 QmWPSzKERs6KAjb8QfSXViFqyEUn3VZYYnXjgG6hJwXWYK
