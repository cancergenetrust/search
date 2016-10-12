address=`docker exec -it demo_cgtd curl localhost:5000/v0/address | jq -r '.address'`

echo "Deleting peer from this server to demo steward at $address"
docker exec -it cgtd curl -X DELETE localhost:5000/v0/peers/$address

echo "Deleting peer from demo steward to nki"
docker exec -it demo_cgtd curl -X DELETE localhost:5000/v0/peers/Qmanw7MzPbEkd3FSkeH8NHi3d8k1nHP1mU3S8LU4NCEg7o

echo "Deleting demo steward $address from elastic search"
docker exec -it es curl -X DELETE localhost:9200/cgt/steward/$address
