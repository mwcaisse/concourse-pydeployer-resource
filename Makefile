DOCKER_ACCOUNT=mwcaisse
DOCKER_REPO=concourse-pydeployer-resource
VERSION=0.1.2

all: push

build:
	docker build -t $(DOCKER_ACCOUNT)/$(DOCKER_REPO):$(VERSION) .
	docker build -t $(DOCKER_ACCOUNT)/$(DOCKER_REPO) .

push: build
	docker push $(DOCKER_ACCOUNT)/$(DOCKER_REPO):$(VERSION)
	docker push $(DOCKER_ACCOUNT)/$(DOCKER_REPO):latest