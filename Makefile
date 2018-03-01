# docker dynamodump service makefile
APP_NAME = "dynamodump"
WORKDIR_NAME = "/root/dynamobackups"

# Volume base path based on OS
ifeq ($(OS),Windows_NT)
	WORK_DIR = $(CURDIR)
else
	WORK_DIR = $(PWD)
endif

.PHONY: build
build:
	docker build \
	--tag $(APP_NAME) \
	--file ./Dockerfile .

.PHONY: ssh-source
ssh-source:
	docker run -it \
	--name "$(APP_NAME)_app_source" \
	--workdir $(WORKDIR_NAME) \
	--volume $(VOLUME_BASE)/dynamobackups:$(WORKDIR_NAME) \
	$(APP_NAME):latest \
	sh -c "cp -f /root/.aws/credentials.source /root/.aws/credentials && sh"

.PHONY: ssh-dest
ssh-dest:
	docker run -it \
	--name "$(APP_NAME)_app_dest" \
	--workdir $(WORKDIR_NAME) \
	--volume $(VOLUME_BASE)/dynamobackups:$(WORKDIR_NAME) \
	$(APP_NAME):latest \
	sh -c "cp -f /root/.aws/credentials.destination /root/.aws/credentials && sh"

.PHONY: rm
rm:
	docker stop "$(APP_NAME)_app_source"
	docker stop "$(APP_NAME)_app_dest"
	docker rm "$(APP_NAME)_app_source"
	docker rm "$(APP_NAME)_app_dest"