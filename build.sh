#!/bin/bash
echo "******** BUILDING NEW DOCKER CONTAINER ********"
docker build --tag leaderboard_api_latest:leaderboard_api .
