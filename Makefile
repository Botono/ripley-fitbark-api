THIS_FILE := $(lastword $(MAKEFILE_LIST))
API_TOKEN := $(shell lpass show --password 2417292719643593979)
RIPLEY_SLUG := $(shell lpass show --notes 7195172272909835495)

plan: build-lambdas
	@cd _terraform ; \
	rm terraform.tfplan ; \
	terraform init -upgrade -input=false ; \
	TF_VAR_fitbark_api_token=$(API_TOKEN) TF_VAR_fitbark_ripley_slug=$(RIPLEY_SLUG) terraform plan -input=false -out=terraform.tfplan

apply:
	@cd _terraform ; \
	TF_VAR_fitbark_api_token=$(API_TOKEN) TF_VAR_fitbark_ripley_slug=$(RIPLEY_SLUG) terraform apply -input=false terraform.tfplan
	#$(MAKE) -f $(THIS_FILE) cleanup-scraper-build

build-lambdas: pull-build-image build-scraper build-api

build-scraper:
	mkdir scraper_build ; \
	cp -a scraper/. scraper_build/
	docker run --rm -v $(shell pwd):/var/task -w /var/task/scraper_build lambci/lambda:build-python3.6 pip3 install -r requirements.txt -t ./

deploy-scraper-function: build-scraper
	cd scraper_build/ ; \
	zip -r ../scraper.zip . ; \
	cd .. ; \
	aws lambda update-function-code --profile ripley_api --region us-west-1 --function-name RipleyFitbark_Scraper --zip-file fileb://scraper.zip ; \
	aws lambda invoke --function-name RipleyFitbark_Scraper --region us-west-1 --profile ripley_api outputfile.txt ; \
	cat outputfile.txt | jq '.' ; \
	rm scraper.zip outputfile.txt

invoke-scraper:
	aws lambda invoke --function-name RipleyFitbark_Scraper --region us-west-1 --profile ripley_api outputfile.txt ; \
	cat outputfile.txt | jq '.' ; \
	rm outputfile.txt

build-api:
	mkdir api_build ; \
	cp -a api/. api_build/
	docker run --rm -v $(shell pwd):/var/task -w /var/task/api_build lambci/lambda:build-python3.6 pip3 install -r requirements.txt -t ./

deploy-api-function: build-api
	cd api_build/ ; \
	zip -r ../api.zip . ; \
	cd .. ; \
	aws lambda update-function-code --profile ripley_api --region us-west-1 --function-name RipleyFitbark_API --zip-file fileb://api.zip ; \
	aws lambda invoke --function-name RipleyFitbark_Scraper --region us-west-1 --profile ripley_api outputfile.txt ; \
	cat outputfile.txt | jq '.' ; \
	rm api.zip outputfile.txt

pull-build-image:
	docker image pull lambci/lambda:build-python3.6

cleanup-scraper-build:
	sudo rm -rf scraper_build