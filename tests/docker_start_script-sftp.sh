#!/usr/bin/env bash
mkdir /home/tomnl/galaxy_storage
docker run -t -p 8080:80 -p 8022:22 -p 8021:21 \
      -v /home/tomnl/galaxy_storage/:/export/ \
      -e GALAXY_CONFIG_ADMIN_USERS=thomas.nigel.lawson@gmail.com \
      -e GALAXY_CONFIG_ALLOW_USER_CREATION=True \
      -e GALAXY_CONFIG_LIBRARY_IMPORT_DIR=True \
      -e GALAXY_CONFIG_USER_LIBRARY_IMPORT_DIR=True \
      -e GALAXY_CONFIG_ALLOW_LIBRARY_PATH_PASTE=True \
      -e GALAXY_CONFIG_CONDA_ENSURE_CHANNELS=tomnl,iuc,bioconda,conda-forge,defaults,r \
       workflow4metabolomics/galaxy-workflow4metabolomics
