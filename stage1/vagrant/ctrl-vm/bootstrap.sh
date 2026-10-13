#!/usr/bin/env bash

# Print commands (-x) and exit on errors (-e)
set -xe

echo "Provisioning 5G control plane VM..."

sudo apt-get update -q

# ----- Installing usefull tools -----
echo "Installing some tools..."
sudo apt-get install -q -y \
  gcc g++ make cmake autoconf \
  git \
  vim \
  curl wget \
  iproute2 \
  net-tools \
  tcpdump \
  iperf \
  npm \
  tcpreplay


# ----- Go -----
cd ~
wget https://dl.google.com/go/go1.17.linux-amd64.tar.gz
sudo tar -C /usr/local -zxf go1.17.linux-amd64.tar.gz
mkdir -p ~/go/{bin,pkg,src}
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export GOROOT=/usr/local/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin:$GOROOT/bin' >> ~/.bashrc
echo 'export GO111MODULE=auto' >> ~/.bashrc
source ~/.bashrc
# doing export manually (source ~/.bashrc doesn't seem to work with Vagrant provisioning...)
export GOPATH=$HOME/go
export GOROOT=/usr/local/go
export PATH=$PATH:$GOPATH/bin:$GOROOT/bin
export GO111MODULE=auto
# clean up
rm go1.17.linux-amd64.tar.gz

# ---- Control-plane Supporting Packages -----
echo "Installing control-plane packages..."
sudo apt -y install mongodb wget git
sudo systemctl start mongodb

# ----- Install Control Plane Elements -----
cd ~
git clone --recursive -b v3.2.1 -j `nproc` https://github.com/free5gc/free5gc.git
cd free5gc
make amf ausf nrf nssf pcf smf udm udr n3iwf
# Apply patch to run without UPF
patch run.sh ~/tmp/run_without_upf.patch

# ----- Update free5GC config files -----
# (files have already been provisioned in $HOME/tmp by Vagrant)
cp ~/tmp/amfcfg.yaml ~/free5gc/config/
cp ~/tmp/smfcfg.yaml ~/free5gc/config/
cp -r ~/tmp/traffic_generation ~/

#  ----- Folder for traffic capturing -----
mkdir /vagrant/traffic_capture/
mkdir /vagrant/traffic_capture/benign/
mkdir /vagrant/traffic_capture/attack/

#  ---- Init the MongoDB and its prerequisites ----
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - 
sudo apt-get install -y nodejs
sudo npm install --global npm@11.8.0
sudo npm install --global yarn

cd ~/free5gc
make webconsole

# ----- Run webconsole briefly to initialize DB -----
cd ~/free5gc/webconsole
timeout 15 ./bin/webconsole || true


# ---- Register UE in the MongoDB ----

mongo free5gc <<EOF
use free5gc

// Create needed collections
db.createCollection("urilist")
db.createCollection("NfProfile")
db.createCollection("policyData.ues.smData")
db.createCollection("subscriptionData.authenticationData.authenticationStatus")
db.createCollection("subscriptionData.contextData.amf3gppAccess")

// Insert policy data AM
db.policyData.ues.amData.insertOne({
        "_id" : ObjectId("6915b1e600ad8feff0c062c9"),
        "subscCats" : [
                "free5gc"
        ],
        "ueId" : "imsi-208930000000001"
})

// Insert policy data SM
db.policyData.ues.smData.insertOne({
        "_id" : ObjectId("6915b1e600ad8feff0c062ca"),
        "smPolicySnssaiData" : {
                "01112233" : {
                        "snssai" : {
                                "sst" : 1,
                                "sd" : "112233"
                        },
                        "smPolicyDnnData" : {
                                "internet" : {
                                        "dnn" : "internet"
                                },
                                "internet2" : {
                                        "dnn" : "internet2"
                                }
                        }
                },
                "01010203" : {
                        "snssai" : {
                                "sst" : 1,
                                "sd" : "010203"
                        },
                        "smPolicyDnnData" : {
                                "internet" : {
                                        "dnn" : "internet"
                                },
                                "internet2" : {
                                        "dnn" : "internet2"
                                }
                        }
                }
        },
        "ueId" : "imsi-208930000000001"
})

// Insert authentication subscription data
db.subscriptionData.authenticationData.authenticationSubscription.insertOne({
    "ueId": "imsi-208930000000001",
    "authenticationMethod": "5G_AKA",
    "permanentKey": {
        "encryptionKey": 0,
        "permanentKeyValue": "8baf473f2f8fd09487cccbd7097c6862",
        "encryptionAlgorithm": 0
    },
    "sequenceNumber": "000000000055",
    "authenticationManagementField": "8000",
    "milenage": {
        "op": {
            "encryptionAlgorithm": 0,
            "encryptionKey": 0,
            "opValue": "8e27b6af0e692e750f32667a3b14605d"
        }
    },
    "opc": {
        "encryptionAlgorithm": 0,
        "encryptionKey": 0,
        "opcValue": ""
    }
})

// Insert provisioned subscription data AM
db.subscriptionData.provisionedData.amData.insertOne({
    "ueId": "imsi-208930000000001",
    "servingPlmnId": "20893",
    "gpsis": [
        "msisdn-0900000000"
    ],
    "subscribedUeAmbr": {
        "downlink": "2 Gbps",
        "uplink": "1 Gbps"
    },
    "nssai": {
        "defaultSingleNssais": [
            {
                "sst": 1,
                "sd": "010203"
            },
            {
                "sst": 1,
                "sd": "112233"
            }
        ]
    }
})

// Insert provisioned subscription data SM, first entry
db.subscriptionData.provisionedData.smData.insertOne({
    "ueId": "imsi-208930000000001",
    "servingPlmnId": "20893",
    "singleNssai": {
        "sst": 1,
        "sd": "010203"
    },
    "dnnConfigurations": {
        "internet": {
            "sessionAmbr": {
                "uplink": "200 Mbps",
                "downlink": "100 Mbps"
            },
            "pduSessionTypes": {
                "defaultSessionType": "IPV4",
                "allowedSessionTypes": [
                    "IPV4"
                ]
            },
            "sscModes": {
                "defaultSscMode": "SSC_MODE_1",
                "allowedSscModes": [
                    "SSC_MODE_2",
                    "SSC_MODE_3"
                ]
            },
            "5gQosProfile": {
                "5qi": 9,
                "arp": {
                    "preemptCap": "",
                    "preemptVuln": "",
                    "priorityLevel": 8
                },
                "priorityLevel": 8
            }
        },
        "internet2": {
            "sessionAmbr": {
                "uplink": "200 Mbps",
                "downlink": "100 Mbps"
            },
            "pduSessionTypes": {
                "allowedSessionTypes": [
                    "IPV4"
                ],
                "defaultSessionType": "IPV4"
            },
            "sscModes": {
                "defaultSscMode": "SSC_MODE_1",
                "allowedSscModes": [
                    "SSC_MODE_2",
                    "SSC_MODE_3"
                ]
            },
            "5gQosProfile": {
                "5qi": 9,
                "arp": {
                    "preemptVuln": "",
                    "priorityLevel": 8,
                    "preemptCap": ""
                },
                "priorityLevel": 8
            }
        }
    }
})

// Insert provisioned subscription data SM, second entry
db.subscriptionData.provisionedData.smData.insertOne({
    "ueId": "imsi-208930000000001",
    "servingPlmnId": "20893",
    "singleNssai": {
        "sst": 1,
        "sd": "112233"
    },
    "dnnConfigurations": {
        "internet": {
            "sscModes": {
                "defaultSscMode": "SSC_MODE_1",
                "allowedSscModes": [
                    "SSC_MODE_2",
                    "SSC_MODE_3"
                ]
            },
            "5gQosProfile": {
                "5qi": 9,
                "arp": {
                    "priorityLevel": 8,
                    "preemptCap": "",
                    "preemptVuln": ""
                },
                "priorityLevel": 8
            },
            "sessionAmbr": {
                "uplink": "200 Mbps",
                "downlink": "100 Mbps"
            },
            "pduSessionTypes": {
                "defaultSessionType": "IPV4",
                "allowedSessionTypes": [
                    "IPV4"
                ]
            }
        },
        "internet2": {
            "5gQosProfile": {
                "5qi": 9,
                "arp": {
                    "priorityLevel": 8,
                    "preemptCap": "",
                    "preemptVuln": ""
                },
                "priorityLevel": 8
            },
            "sessionAmbr": {
                "uplink": "200 Mbps",
                "downlink": "100 Mbps"
            },
            "pduSessionTypes": {
                "defaultSessionType": "IPV4",
                "allowedSessionTypes": [
                    "IPV4"
                ]
            },
            "sscModes": {
                "defaultSscMode": "SSC_MODE_1",
                "allowedSscModes": [
                    "SSC_MODE_2",
                    "SSC_MODE_3"
                ]
            }
        }
    }
})

//  Insert provisioned subscription data SMF selection subscription data
db.subscriptionData.provisionedData.smfSelectionSubscriptionData.insertOne({
    "ueId": "imsi-208930000000001",
    "servingPlmnId": "20893",
    "subscribedSnssaiInfos": {
        "01010203": {
            "dnnInfos": [
                {
                    "dnn": "internet"
                },
                {
                    "dnn": "internet2"
                }
            ]
        },
        "01112233": {
            "dnnInfos": [
                {
                    "dnn": "internet"
                },
                {
                    "dnn": "internet2"
                }
            ]
        }
    }
})

EOF


echo "**** DONE PROVISIONING VM ****"