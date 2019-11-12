#!/usr/bin/env bash

dir=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

echo "$dir"

echo "##############################################"
echo "##############################################"

echo "Starting BSS.."
cd "$dir/son-bss"
echo "$(pwd)"

sudo docker stop son-bss
sudo docker rm son-bss
# sudo docker build -t son-bss -f Dockerfile .

sudo docker run -d --name son-bss --net=son-sp --network-alias=son-bss -p 25001:1337 -p 25002:1338 -v $(pwd)/code/app/modules:/usr/local/bss/code/app/modules son-bss grunt serve:integration --gkApiUrl=http://$1/api/v2 --hostname=0.0.0.0 --userManagementEnabled=true --licenseManagementEnabled=true --debug


echo "##############################################"
echo "##############################################"

cd "$dir/son-mano-framework"
echo "$(pwd)"

echo "Starting Scramble SLM.."

# Stop Original SLM and start pishahang changes 
sudo docker stop servicelifecyclemanagement
sudo docker rm servicelifecyclemanagement
# sudo docker build -t servicelifecyclemanagement -f plugins/son-mano-service-lifecycle-management/Dockerfile-dev .
sudo docker run -d --name servicelifecyclemanagement --net=son-sp --network-alias=servicelifecyclemanagement -v $(pwd)/plugins/son-mano-service-lifecycle-management:/plugins/son-mano-service-lifecycle-management servicelifecyclemanagement

echo "##############################################"
echo "##############################################"

cd "$dir/son-mano-framework"
echo "$(pwd)"

echo "Starting Scramble MV Plugin.."

sudo docker stop placementplugin
sudo docker stop mvplugin
sudo docker rm mvplugin
# sudo docker build -t mvplugin -f plugins/son-mano-mv/Dockerfile-dev .
sudo docker run -d --name mvplugin --net=son-sp --network-alias=mvplugin -v $(pwd)/plugins/son-mano-mv:/plugins/son-mano-mv mvplugin


echo "##############################################"
echo "##############################################"

cd "$dir/son-mano-framework"
echo "$(pwd)"

echo "Starting FLM.."

# Stop Original FLM and start pishahang changes 
sudo docker stop functionlifecyclemanagement
sudo docker rm functionlifecyclemanagement
# sudo docker build -t functionlifecyclemanagement -f plugins/son-mano-function-lifecycle-management/Dockerfile-dev .
sudo docker run -d --name functionlifecyclemanagement --net=son-sp --network-alias=functionlifecyclemanagement -v $(pwd)/plugins/son-mano-function-lifecycle-management:/plugins/son-mano-function-lifecycle-management functionlifecyclemanagement

echo "##############################################"
echo "##############################################"

cd "$dir/son-mano-framework"
echo "$(pwd)"

echo "Starting CSLM.."

# Stop Original FLM and start pishahang changes 
sudo docker stop cloudservicelifecyclemanagement
sudo docker rm cloudservicelifecyclemanagement
# sudo docker build -t cloudservicelifecyclemanagement -f plugins/son-mano-cloud-service-lifecycle-management/Dockerfile-dev .
sudo docker run -d --name cloudservicelifecyclemanagement --net=son-sp --network-alias=cloudservicelifecyclemanagement -v $(pwd)/plugins/son-mano-cloud-service-lifecycle-management:/plugins/son-mano-cloud-service-lifecycle-management cloudservicelifecyclemanagement