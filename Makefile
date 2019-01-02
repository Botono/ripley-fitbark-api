THIS_FILE := $(lastword $(MAKEFILE_LIST))


terraform-plan: build-scraper
	cd _terraform ; \
	rm terraform.tfplan ; \
	terraform init -upgrade -input=false ; \
	terraform plan -input=false -out=terraform.tfplan

terraform-apply:
	cd _terraform ; \
	terraform apply -input=false terraform.tfplan
	#$(MAKE) -f $(THIS_FILE) cleanup-scraper-build

build-scraper: pull-build-image
	mkdir scraper_build ; \
	cp -a scraper/. scraper_build/
	docker run --rm -v $(shell pwd):/var/task -w /var/task/scraper_build lambci/lambda:build-python3.6 pip3 install -r requirements.txt -t ./

pull-build-image:
	docker image pull lambci/lambda:build-python3.6

cleanup-scraper-build:
	sudo rm -rf scraper_build