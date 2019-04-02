appname := lipwig

all: help

help:
	@echo "$(appname) commands:"
	@echo "req       - Install requirements via PyPI."
	@echo "lint      - Run code linters."
	@echo "test      - Run pytest tests."
	@echo "coverage  - Measure code coerage."
	@echo "clean     - Remove cached artifacts."
	@echo "validate  - Validate the SAM/CloudFormation template."
	@echo "package   - Package the application for deployment. Requires env var: S3_BUCKET=deploy_bucket"
	@echo "deploy    - Deploy the application to AWS Lambda."
	@echo "publish   - test, clean, pacakge and deploy."
	@echo "tag       - git tag and push. Requires env var: TAG=1.2.3"

req:
	python3 -m pip install -r requirements-dev.txt --upgrade

lint:
	flake8
	mypy app/$(appname)

test:
	PYTHONPATH=app pytest -vv

coverage:
	PYTHONPATH=app py.test --cov=$(appname) --cov-fail-under=100 --cov-report=term --cov-report=html || open htmlcov/index.html

clean:
	@echo "Cleaning up"
	rm dist/packaged.yaml
	-find . -type f -a \( -name "*.pyc" -o -name "*$$py.class" \) | xargs rm
	-find . -type d -name "__pycache__" | xargs rm -r

validate:
	cfn-lint template.yaml
	sam validate

build:
	sam build -m requirements.txt

package:
	sam package --output-template-file dist/packaged.yaml --s3-bucket ${S3_BUCKET} --s3-prefix sam-packages/$(appname)

deploy:
	sam deploy --template-file dist/packaged.yaml --stack-name $(appname) \
	--capabilities CAPABILITY_IAM --region us-east-1

publish: lint test clean validate build package deploy

tag:
	git tag $(TAG)
	git push --tags
