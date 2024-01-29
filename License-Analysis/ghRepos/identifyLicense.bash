#!/bin/bash

# bundle exec licensee detect $1 --json | jq .licenses[0].key
scancode -l $1 --json $2
