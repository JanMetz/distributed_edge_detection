#!/bin/bash

docker login

docker tag psr-frontend janm509/psr.psr-frontend
docker push janm509/psr.psr-frontend

docker tag psr-registry janm509/psr.psr-registry
docker push janm509/psr.psr-registry

docker tag psr-backend janm509/psr.psr-backend
docker push janm509/psr.psr-backend