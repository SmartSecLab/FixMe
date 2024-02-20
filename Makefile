# Makefile for syncing folder from remote to local with exclusions

# Define variables
# REMOTE_USER = username
REMOTE_HOST = kristiania
REMOTE_FOLDER = /cluster/home/guru/research/FixMe/
LOCAL_FOLDER = .
EXCLUDE = --exclude=.git --exclude=.DS_Store

# Define sync command
sync:
	rsync -avz $(EXCLUDE) $(LOCAL_FOLDER) $(REMOTE_HOST):$(REMOTE_FOLDER) 
