#!/bin/bash

docker build -t mwcaisse/concourse-pydeployer-resource .

docker push mwcaisse/concourse-pydeployer-resource
