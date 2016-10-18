address=`docker exec -it demo_cgtd curl localhost:5000/v0/address | jq -r '.address'`

echo "Deleting peer from this server to demo steward at $address"
docker exec -it cgtd curl -X DELETE localhost:5000/v0/peers/$address

echo "Deleting demo steward $address from elastic search"
docker exec -it es curl -X DELETE localhost:9200/cgt/steward/$address

echo "Removing all submissions"
docker exec demo_ipfs sh -c "echo '{\"domain\": \"kaiserpermanente.org\", \"submissions\": [], \"peers\": []}' | ipfs add -q | xargs ipfs name publish"
