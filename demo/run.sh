address=`docker exec -it demo_cgtd curl localhost:5000/v0/address | jq -r '.address'`

echo "Adding peer from local cgtd server to $address"
docker exec -it cgtd curl -X POST localhost:5000/v0/peers/$address

echo "Adding peer from demo to nki"
docker exec -it demo_cgtd curl -X POST localhost:5000/v0/peers/Qmanw7MzPbEkd3FSkeH8NHi3d8k1nHP1mU3S8LU4NCEg7o


echo "Adding a submission every few minutes"
for i in `seq 1 10`;
do
	UUID=$(cat /proc/sys/kernel/random/uuid)
	echo $UUID
	docker exec -it demo_cgtd curl -X POST localhost:5000/v0/submissions \
		-F "SAMPLE_ID=$UUID" \
		-F files[]=@tests/ALL/ALL-US__TARGET-10-PAKMVD-09A-01D.vcf
	sleep 2
done    
