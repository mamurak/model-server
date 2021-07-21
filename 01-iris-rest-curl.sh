#!/bin/bash

URL=http://model-server-model-server.apps.ocp.3f4e.sandbox1385.opentlc.com
curl -X POST -H "Content-Type: application/json" --data '{"sl": 5.9, "sw": 3.0, "pl": 5.1, "pw": 1.8}' $URL


