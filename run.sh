#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd "${SCRIPTPATH}" || exit 1

CONTAINERPATH="/opt/bikeshare_loader"

docker run -t \
           -p 4040:4040 \
           -v "${SCRIPTPATH}/landing:${CONTAINERPATH}/landing" \
           -v "${SCRIPTPATH}/output:${CONTAINERPATH}/output" \
           bikeshare_loader