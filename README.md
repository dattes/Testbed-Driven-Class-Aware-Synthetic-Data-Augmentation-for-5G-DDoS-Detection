# Testbed-Driven-Class-Aware-Synthetic-Data-Augmentation-for-5G-DDoS-Detection

## Stage 1: 5G testbed and traffic generation
 
Folder: [`stage1/`](stage1/)
 
- Two virtual machines provisioned with Vagrant and VirtualBox
  - **Ctrl VM** with all 5G core control-plane functions (free5GC v3.2.1)
  - **Data VM** with a Mininet network hosting the UE and gNB (UERANSIM), the UPF, the data network and an adversary host
- Strict control-plane and user-plane separation, since the UPF runs on the data VM
- Benign traffic scenarios: mobile gaming, web browsing, video and audio streaming, ping
- Four single-vector floods, one per interface: N2 (SCTP/NGAP), N3 (GTP-U with UDP, TCP or ICMP), N4 (PFCP) and N6 (TCP)
- Packet capture at three points: r0 (inside the GTP-U tunnel), r1 (N6, decapsulated) and the ctrl VM (N4)

See [`stage1/README.md`](stage1/README.md) for requirements, setup and how to run the scenarios.
 
## Stage 2: machine learning pipeline
 
Folder: [`stage2/`](stage2/)
 
The pipeline is organized in five work packages, implemented as Jupyter notebooks.
 
| Work package | Purpose |
|---|---|
| WP1 | Ingest 5G-NIDD and CEDI-NIDD |
| WP2 | Clean features and create a stratified 80/20 split |
| WP3 | Build the non-augmented references (Raw, Dirty, Balanced) |
| WP4 | Generate synthetic data with CTGAN and TabDDPM, balanced and per class |
| WP5 | Train and evaluate XGBoost, LightGBM and CatBoost |
 
See [`stage2/README.md`](stage2/README.md) for the environment, notebook order and expected outputs.
