#!/bin/sh

cp /root/.ethereum/_geth/nodekey_owner /root/.ethereum/geth/nodekey
geth --networkid=${NETWORK_ID} "$@"
