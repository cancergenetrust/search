build:
	docker build -t search-cgt .

es:
	docker run -it -p 9200:9200 -p 9300:9300 \
		-v /mnt/elasticsearch:/usr/share/elasticsearch/data \
		--name=es elasticsearch:latest -Des.network.host=0.0.0.0
	docker exec -it es plugin install jettro/elasticsearch-gui

nginx:
	docker stop nginx || true && docker rm nginx || true
	docker run -it --rm --name nginx \
		--link cgtd:cgtd \
		--link ipfs:ipfs \
		--link es:es \
		-p 5282:80 \
		-v `pwd`/default.conf:/etc/nginx/conf.d/default.conf:ro \
		-v `pwd`/www:/usr/share/nginx/html:ro \
		nginx

stop:
	docker stop es || true && docker rm es || true
	docker stop nginx || true && docker rm nginx || true

reset:
	curl -X DELETE localhost:9200/cgt
	curl localhost:9200/_cat/indices?v

crawl:
	docker run -it --rm -v `pwd`:/app:ro --link ipfs:ipfs --link es:es search-cgt $(address) -d 4 -t 10
