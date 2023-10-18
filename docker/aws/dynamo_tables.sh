#!/bin/bash
awslocal dynamodb create-table \
   --table-name radio_programs \
   --attribute-definitions AttributeName=id,AttributeType=S \
   --key-schema AttributeName=id,KeyType=HASH \
   --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
   --region ${AWS_DEFAULT_REGION}
