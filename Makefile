build:
	docker build -t search-cgt .

up:
	docker run -it -p 9200:9200 -p 9300:9300 \
		-v /mnt/elasticsearch:/usr/share/elasticsearch/data \
		--name=es elasticsearch:latest -Des.network.host=0.0.0.0
	docker exec -it es plugin install jettro/elasticsearch-gui

down:
	docker stop es || true && docker rm es || true

reset:
	curl -X DELETE localhost:9200/stewards
	curl -X DELETE localhost:9200/submissions

crawl:
	docker run -it --rm -v `pwd`:/app:ro --link ipfs:ipfs --link es:es search-cgt $(address)
