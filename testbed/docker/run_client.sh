#!/bin/sh

IP=$(ifconfig eth0 | grep 'inet' | awk '{print $2}' | sed 's/addr://')
INDEX=$(dig -x $IP +short | sed 's/[^0-9]*//g')
ACCOUNT=$(jq -r '.clients' accounts.json | jq 'keys_unsorted' | jq -r "nth($((INDEX-1)))")
PASSWORD=$(jq -r '.clients' accounts.json | jq -r ".[\"$ACCOUNT\"]")

PRVINDEX=$((INDEX % MINERS))
if [ "$PRVINDEX" -eq "0" ]; then
  PRVINDEX=$MINERS
fi
PROVIDER=$(dig bfl-geth-miner-$PRVINDEX +short)

python run_client.py \
  --provider "http://$PROVIDER:8545" \
  --abi /root/abi.json \
  --ipfs $IPFS_API \
  --account $ACCOUNT \
  --passphrase $PASSWORD \
  --contract $CONTRACT \
  --log /root/log.log \
  --train /root/dataset/train/$((INDEX-1)).npz \
  --test /root/dataset/test/$((INDEX-1)).npz \
  --scoring $SCORING

