docker run -d --name demo_ipfs ipfs/go-ipfs:v0.4.3
sleep 5
docker run -d --name demo_cgtd --link demo_ipfs:ipfs ga4gh/cgtd:0.1.0
docker exec demo_ipfs sh -c "echo '{\"domain\": \"kaiserpermanente.org\", \"submissions\": [], \"peers\": []}' | ipfs add -q | xargs ipfs name publish"
echo "Demo steward up at address:"
docker exec -it demo_cgtd curl localhost:5000/v0/address
docker exec -it demo_cgtd curl localhost:5000/v0/
