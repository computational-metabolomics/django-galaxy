#!/usr/bin/env bash
mkdir /home/tomnl/galaxy_storage
docker run -d \
      --net=host \
      -v /home/tomnl/galaxy_storage/:/export/ \
      -e GALAXY_CONFIG_ADMIN_USERS=thomas.nigel.lawson@gmail.com \
      -e GALAXY_CONFIG_ALLOW_USER_CREATION=True \
      -e GALAXY_CONFIG_LIBRARY_IMPORT_DIR=True \
      -e GALAXY_CONFIG_USER_LIBRARY_IMPORT_DIR=True \
      -e GALAXY_CONFIG_ALLOW_LIBRARY_PATH_PASTE=True \
       workflow4metabolomics/galaxy-workflow4metabolomics
