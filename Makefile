up:
	docker run -it -p 9200:9200 -p 9300:9300 --name=es elasticsearch:latest -Des.network.host=0.0.0.0

down:
	docker stop es || true && docker rm es || true
