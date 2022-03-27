ARG IMAGE_VARIANT=slim-buster
ARG OPENJDK_VERSION=8
ARG PYTHON_VERSION=3.10.4

FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT} AS py3
FROM openjdk:${OPENJDK_VERSION}-${IMAGE_VARIANT}
COPY --from=py3 / /

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y libgeos-dev

WORKDIR /opt/bikeshare_loader

COPY config/ config/
COPY src/ src/

COPY build_image.sh build_image.sh
RUN chmod +x build_image.sh

ENV PYTHONPATH "${PYTHONPATH}:/opt/bikeshare_loader/src:/opt/bikeshare_loader/src/shared:/opt/bikeshare_loader/src/tests"

RUN ./build_image.sh

EXPOSE 4040
CMD . bs_venv/bin/activate && exec python3 ./src/load_bikeshare_data.py
