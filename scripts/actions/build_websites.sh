#!/bin/bash

curl -H "Accept: application/vnd.github.v3+json" -H "Authorization: token $WEB_TEAM_TOKEN" --request POST --data '{"ref": "master"}' https://api.github.com/repos/DIAGNijmegen/website-content/actions/workflows/deploy-master.yml/dispatches
