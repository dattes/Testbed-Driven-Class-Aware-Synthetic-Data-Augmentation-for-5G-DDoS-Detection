# VM & Jupyter Usage Guide

This document explains how to start the virtual machine (VM), open Jupyter notebooks locally via an SSH tunnel, and run long jobs safely without keeping your laptop or SSH session open.

---

## 1️⃣ Start and Connect to the VM

Start the VM via your cloud provider or hypervisor.

Connect via SSH:

```bash
ssh ubuntu@<VM_IP>
```

Activate the Python virtual environment:

```bash
source ~/ganenv/bin/activate
```

---

## 2️⃣ Open Jupyter Notebook in Local Browser (SSH Tunnel)

This allows you to edit notebooks locally while they execute on the VM.

### 2.1 Start Jupyter on the VM (no browser)

On the VM:

```bash
cd ~/5g-nidd   # adjust to your project directory
jupyter notebook --no-browser --port=8888
```

Copy the displayed token.

---

### 2.2 Create SSH tunnel from local machine

Open a **new local terminal**:

```bash
ssh -N -L 8888:localhost:8888 ubuntu@<VM_IP>
```

Keep this terminal open.

---

### 2.3 Open Jupyter in browser

On your local computer, open:

```
http://localhost:8888
```

Paste the token from step 2.1.

You can now edit and run notebooks locally while using the VM’s resources.

---

## 3️⃣ Run Notebooks Safely in the Background (Recommended for Long Jobs)

For long preprocessing or training runs, use `screen` so jobs continue even if the connection drops.

### 3.1 Start a screen session

On the VM:

```bash
screen -S run_job
```

Activate environment:

```bash
source ~/ganenv/bin/activate
```

---

### 3.2 Convert notebook to script and run it

Convert to script
```bash
jupyter nbconvert --to script 5G_NIDD_Augmentation_Training-2.ipynb --output train_ctgan.py
```

Run Script
```bash
python train_ctgan.py | tee train.log
```

---

### 3.3 Detach screen (safe)

Press:

```
Ctrl + A, then D
```

The job continues even if:
- SSH disconnects
- Laptop sleeps or shuts down

---

## 4️⃣ Check Progress

### Reattach to screen:

```bash
screen -r run_job
```

---

### Check GPU usage:

```bash
watch -n 2 nvidia-smi
```

---

## 5️⃣ Stop or Clean Up

List running screen sessions:

```bash
screen -ls
```

Kill a screen session if needed:

```bash
screen -X -S run_job quit
```

Kill all sessions
```bash
killall screen
```

---
