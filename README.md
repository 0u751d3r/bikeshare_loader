# Bikeshare Loader
## Project Description
Bikeshare loader flattens out bikeshare trips, to/from station info, and weather data in a single structure
for ML workflow analysis.  
It uses PySpark for data processing, and pytest for unit tests.  

To make it easy for project dependencies, you don't need to have anything except Docker installed.

Copyright (C) 2022 David Vas - see LICENSE for details

## Prerequisites
- You need to have [Docker](https://www.docker.com/products/personal/) installed.
- You need to have a Linux-like environment. This has been tested on Ubuntu 21.10.  
    If you are on Windows, you can use [WSL](https://docs.microsoft.com/en-us/windows/wsl/install) 
    or [Cygwin](https://www.cygwin.com/)
- You need to place input files in the [landing/](landing) directory.
    Then, configure your input files in [config/config.yaml](config/config.yaml). 
    Please place each dataset in a separate subdirectory, and 
    you only need to specify the subdirectory in the config.yaml  
    Currently, trip and station data needs to be in avro format with snappy compression,
    weather and zipcode data needs to be in CSV with headers.  
    If multiple sources are used, their signature needs to match.  
    An example with San Francisco data has been provided for you. 
- Spark is configured currently to use 15GB for the Java Heap, so total memory usage will be around ~22GB
    while running. Though it will work if you have less RAM than that, the OS will have to page it out.
    In this case it is recommended to set the "memory" parameter in `config.yaml` to something lower.  
    A setting less than 4GB is not recommended.

## Build
Run `./build.sh` from the project's directory. 
You might need to give it execute permission first with `chmod +x build.sh`  
Do not run `build_image.sh`, that is executed by build within the docker container.

## Run
Execute `./run.sh` from the project's directory. It starts the loader, and outputs the log to stdout.  
You can connect to the Spark UI (while it's running) via [localhost:4040](http://localhost:4040).
If port 4040 is not available, remap it by editing `run.sh`, for example `-p 4041:4040`  

## Deploy
If you want to deploy this as a productionalized workload, the pyspark code needs to be used directly.  
Currently, the code is not packaged for deployment. The docker container is mostly there to make it easier to run
locally.

## TODO
- Unit tests for `load_bikeshare_data` 
    See the [relevant file](src/tests/test_load_bikeshare_data.py) in tests for details.

- More verbose DEBUG messages for logging
