#!/bin/sh

IP=$(ifconfig eth0 | grep 'inet' | awk '{print $2}' | sed 's/addr://')
INDEX=$(dig -x $IP +short | sed 's/[^0-9]*//g')
INDEX=$((INDEX-1))
ACCOUNT=$(jq -r '.miners' accounts.json | jq 'keys_unsorted' | jq -r "nth($INDEX)")
PASSWORD=$(jq -r '.miners' accounts.json | jq -r ".[\"$ACCOUNT\"]")

cp /root/.ethereum/_geth/nodekey_${INDEX} /root/.ethereum/geth/nodekey
echo $PASSWORD > ./password.txt

geth --networkid=${NETWORK_ID} --miner.etherbase=${ACCOUNT} --unlock=${ACCOUNT} --syncmode=full --password=./password.txt "$@"
