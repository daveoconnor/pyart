build: Dockerfile ## Create the build and runtime images
	docker build -t pyart .

extractdist: ## copy the dist out of a running container
	@docker create --name pyart pyart
	@docker cp pyart:/tmp/pyart/dist .

up:	## run the docker container to allow extracting the dist or to testing
	@docker run --name pyart pyart

down: ## stop the running docker container
	@docker stop pyart
	@docker rm pyart

clean: ## remove the docker image
	@docker rmi pyart

help: ## This help.
	@awk 'BEGIN 	{ FS = ":.*##"; target="";printf "\nUsage:\n  make \033[36m<target>\033[33m\n\nTargets:\033[0m\n" } \
		/^[a-zA-Z_-]+:.*?##/ { if(target=="")print ""; target=$$1; printf " \033[36m%-10s\033[0m %s\n\n", $$1, $$2 } \
		/^([a-zA-Z_-]+):/ {if(target=="")print "";match($$0, "(.*):"); target=substr($$0,RSTART,RLENGTH) } \
		/^\t## (.*)/ { match($$0, "[^\t#:\\\\]+"); txt=substr($$0,RSTART,RLENGTH);printf " \033[36m%-10s\033[0m", target; printf " %s\n", txt ; target=""} \
		/^## .*/ {match($$0, "## (.+)$$"); txt=substr($$0,4,RLENGTH);printf "\n\033[33m%s\033[0m\n", txt ; target=""} \
	' $(MAKEFILE_LIST)

test:  ## Run the PyTests for the Django Application
	@docker-compose exec pytest


.PHONY: help build clean down up test

.DEFAULT_GOAL := help
