.PHONY: build train prompts


build:
	docker build . -t portraits/model-trainer
	
push:
	docker push portraits/model-trainer

train:
	python -m portraits.train

photos:
	python -m portraits.photos
