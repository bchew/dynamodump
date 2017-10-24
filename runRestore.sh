#!/bin/bash

`aws ecr get-login --no-include-email --region us-east-1`

sudo docker pull 169614562534.dkr.ecr.us-east-1.amazonaws.com/dynamodumper

sudo docker run -i 169614562534.dkr.ecr.us-east-1.amazonaws.com/dynamodumper bash /scripts/localrestore.sh
