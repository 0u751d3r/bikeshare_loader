#!/bin/bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd "${SCRIPTPATH}" || exit 1  # ensuring we're in the root project dir
docker build -t bikeshare_loader .