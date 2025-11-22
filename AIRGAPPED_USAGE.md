# AIRGAPPED_USAGE.md

# 🔐 Running Nunchuk Descriptor Importer on an Air‑Gapped Device

This document explains how to safely prepare and use the **Nunchuk Descriptor Importer** on a fully **offline, air‑gapped machine**.

> ⚠️ WARNING: Using real wallet material on a network-connected machine can compromise all funds.
> Always follow these steps when testing with real seeds or XPRVs.

---

## 1️⃣ Download Dependencies on an Online Computer

On a secure, network-connected machine:

```bash
# Create a folder to store offline packages
mkdir offline_packages
cd offline_packages

# Download all required Python packages for offline use
pip download -r ../NunchukDescriptorImporter/requirements.txt
```

This produces a folder containing all `.whl` and `.tar.gz` packages needed to install the tool offline.

---

## 2️⃣ Transfer Files to the Air‑Gapped Device

Copy the following via secure media (USB drive, encrypted storage, etc.):

* `NunchukDescriptorImporter/` project directory
* `offline_packages/` folder
* Python installer (if not already installed on the air‑gapped machine)

> Ensure that the transfer media is scanned and handled according to your organization’s security policy.

---

## 3️⃣ Install Dependencies Offline

On the air-gapped machine:

```bash
cd NunchukDescriptorImporter

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate    # Linux / macOS
# venv\Scripts\activate     # Windows

# Install the downloaded packages offline
pip install --no-index --find-links=../offline_packages -r requirements.txt
```

> The `--no-index` flag ensures **no internet connection is used**. Only the provided packages are installed.

---

## 4️⃣ Run the Tool Safely

Once dependencies are installed:

```bash
python nunchuk_descriptor_import.py
```

You can now safely:

* Paste descriptors exported from Nunchuk
* Enter seed phrases (dummy or real, if offline)
* Generate XPRVs and import commands

All operations are fully offline.

---

## 5️⃣ Security Reminders

* ✅ Only use **real wallet material on a fully offline, air‑gapped device**
* ✅ Never connect the air‑gapped device to the internet while testing
* ✅ Always verify the integrity of the Python environment and dependencies
* ✅ Use dummy/test seeds whenever possible

---
