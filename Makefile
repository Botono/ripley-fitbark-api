THIS_FILE := $(lastword $(MAKEFILE_LIST))
API_TOKEN := $(shell lpass show --password 2417292719643593979)

plan: build-scraper
	cd _terraform ; \
	rm terraform.tfplan ; \
	terraform init -upgrade -input=false ; \
	TF_VAR_fitbark_api_token=$(API_TOKEN) terraform plan -input=false -out=terraform.tfplan

apply:
	cd _terraform ; \
	TF_VAR_fitbark_api_token=$(API_TOKEN) terraform apply -input=false terraform.tfplan
	#$(MAKE) -f $(THIS_FILE) cleanup-scraper-build

build-scraper: pull-build-image
	mkdir scraper_build ; \
	cp -a scraper/. scraper_build/
	docker run --rm -v $(shell pwd):/var/task -w /var/task/scraper_build lambci/lambda:build-python3.6 pip3 install -r requirements.txt -t ./

pull-build-image:
	docker image pull lambci/lambda:build-python3.6

cleanup-scraper-build:
	sudo rm -rf scraper_build