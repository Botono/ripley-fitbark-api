THIS_FILE := $(lastword $(MAKEFILE_LIST))
API_TOKEN := $(shell lpass show --password 2417292719643593979)
RIPLEY_SLUG := $(shell lpass show --notes 7195172272909835495)
GOOGLE_CREDS_NOTE_ID := 1198256837478991513

plan: build-lambdas
	@cd _terraform ; \
	rm terraform.tfplan ; \
	terraform init -upgrade -input=false ; \
	TF_VAR_fitbark_api_token=$(API_TOKEN) TF_VAR_fitbark_ripley_slug=$(RIPLEY_SLUG) terraform plan -input=false -out=terraform.tfplan

destroy:
	@cd _terraform ; \
	TF_VAR_fitbark_api_token=$(API_TOKEN) TF_VAR_fitbark_ripley_slug=$(RIPLEY_SLUG) terraform destroy

apply:
	@cd _terraform ; \
	TF_VAR_fitbark_api_token=$(API_TOKEN) TF_VAR_fitbark_ripley_slug=$(RIPLEY_SLUG) terraform apply -input=false terraform.tfplan
	$(MAKE) -f $(THIS_FILE) cleanup-secrets

build-lambdas: pull-build-image build-scraper build-api build-sheets-writer

deploy-functions: deploy-sheets-writer-function deploy-api-function deploy-scraper-function

cleanup-binaries:
	-rm scraper/main
	-rm api/apilambda

build-sheets-writer:
	mkdir -p _lambda_builds/sheets_data_writer_build ; \
	cp -a sheets_data_writer/. _lambda_builds/sheets_data_writer_build/
	docker run --rm -v $(shell pwd):/var/task -w /var/task/_lambda_builds/sheets_data_writer_build lambci/lambda:build-python3.6 pip3 install -r requirements.txt -t ./

deploy-sheets-writer-function: build-sheets-writer
	cd _lambda_builds/sheets_data_writer_build/ ; \
	zip -r ../sheets_data_writer.zip . ; \
	cd .. ; \
	aws lambda update-function-code --profile ripley_api --region us-west-2 --function-name RipleyAPI_SheetsDataWriter --zip-file fileb://sheets_data_writer.zip ; \
	rm sheets_data_writer.zip

build-scraper:
	go mod tidy ; \
	cd scraper ; \
	GOOS=linux go build -o main cmd/main.go ; \
	zip -j scraperlambda.zip main

deploy-scraper: build-scraper
	aws lambda update-function-code --profile ripley_api --region us-west-2 --function-name RipleyFitbark_Scraper --zip-file fileb://scraper/scraper.zip ; \
	aws lambda invoke --function-name RipleyFitbark_Scraper --region us-west-2 --profile ripley_api outputfile.txt ; \
	cat outputfile.txt | jq '.' ; \
	rm scraper/scraper.zip scraper/main outputfile.txt

invoke-scraper:
	aws lambda invoke --function-name RipleyFitbark_Scraper --region us-west-2 --profile ripley_api outputfile.txt ; \
	cat outputfile.txt | jq '.' ; \
	rm outputfile.txt

build-api:
	go mod tidy ; \
	cd api ; \
	GOOS=linux go build -o main cmd/main.go ; \
	zip -j apilambda.zip main

deploy-api-function: build-api
	cd api ; \
	aws lambda update-function-code --profile ripley_api --region us-west-2 --function-name RipleyFitbark_API --zip-file fileb://apilambda.zip ; \
	aws lambda invoke --function-name RipleyFitbark_Scraper --region us-west-2 --profile ripley_api outputfile.txt ; \
	cat outputfile.txt | jq '.' ; \
	rm apilambda.zip main outputfile.txt
	$(MAKE) -f $(THIS_FILE) cleanup-secrets

pull-build-image:
	docker image pull lambci/lambda:build-python3.6

cleanup-secrets:
	rm _lambda_builds/api_build/credentials.json

import-bloodwork:
	lpass show --notes $(GOOGLE_CREDS_NOTE_ID) > utils/credentials.json ; \
	cd utils ; \
	python3 google_import.py bloodwork ; \
	rm credentials.json

import-water:
	lpass show --notes $(GOOGLE_CREDS_NOTE_ID) > utils/credentials.json ; \
	cd utils ; \
	python3 google_import.py water ; \
	rm credentials.json

import-changelog:
	lpass show --notes $(GOOGLE_CREDS_NOTE_ID) > utils/credentials.json ; \
	cd utils ; \
	python3 google_import.py changelog ; \
	rm credentials.json