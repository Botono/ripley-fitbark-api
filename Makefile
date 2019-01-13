THIS_FILE := $(lastword $(MAKEFILE_LIST))
API_TOKEN := $(shell lpass show --password 2417292719643593979)
RIPLEY_SLUG := $(shell lpass show --notes 7195172272909835495)

plan: build-scraper
	@cd _terraform ; \
	rm terraform.tfplan ; \
	terraform init -upgrade -input=false ; \
	TF_VAR_fitbark_api_token=$(API_TOKEN) TF_VAR_fitbark_ripley_slug=$(RIPLEY_SLUG) terraform plan -input=false -out=terraform.tfplan

apply:
	@cd _terraform ; \
	TF_VAR_fitbark_api_token=$(API_TOKEN) TF_VAR_fitbark_ripley_slug=$(RIPLEY_SLUG) terraform apply -input=false terraform.tfplan
	#$(MAKE) -f $(THIS_FILE) cleanup-scraper-build

build-scraper: pull-build-image
	mkdir scraper_build ; \
	cp -a scraper/. scraper_build/
	docker run --rm -v $(shell pwd):/var/task -w /var/task/scraper_build lambci/lambda:build-python3.6 pip3 install -r requirements.txt -t ./

deploy-scraper-function: build-scraper
	cd scraper_build/ ; \
	zip -r ../scraper.zip . ; \
	cd .. ; \
	aws lambda update-function-code --profile default --region us-west-1 --function-name RipleyFitbark_Scraper --zip-file fileb://scraper.zip ; \
	aws lambda invoke --function-name RipleyFitbark_Scraper --region us-west-1 --profile default outputfile.txt ; \
	cat outputfile.txt | jq '.' ; \
	rm scraper.zip outputfile.txt

invoke-scraper:
	aws lambda invoke --function-name RipleyFitbark_Scraper --region us-west-1 --profile default outputfile.txt ; \
	cat outputfile.txt | jq '.' ; \
	rm outputfile.txt

pull-build-image:
	docker image pull lambci/lambda:build-python3.6

cleanup-scraper-build:
	sudo rm -rf scraper_build