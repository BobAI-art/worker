#!/usr/bin/env bash

service ssh restart

export AWS_ACCESS_KEY_ID="AKIA5TUL5XFHCKNSZZU3"
export AWS_SECRET_ACCESS_KEY="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"
export HUGGINGFACE_TOKEN="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"
export PORTRAITS_BASE_URL="https://portraits.vercel.app/"

/app/filebeat -e 2>&1 > /dev/null &

python $@  2>&1 | tee -a /tmp/output.log
