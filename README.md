# Nunchuk Descriptor Importer


This tool is designed for **development and testing only**, using **dummy seed phrases,
dummy XPRVs, and non-sensitive descriptors**.

**Do NOT use real seed phrases, real XPRVs, or any live wallet data on an online machine.**

If real wallet material must be used for evaluation purposes, this tool should be run **exclusively
on an OFFLINE, AIR-GAPPED DEVICE** with all network connectivity disabled.

For detailed instructions on preparing and running this tool on an offline device, see [AIRGAPPED_USAGE.md](AIRGAPPED_USAGE.md).


Using this tool with real keys on an internet-connected system may compromise wallet security.

---

##  Clone the Repository

```bash
# Clone the repo
git clone https://github.com/SaniExp/NunchukDescriptorImporter.git

# Enter the project directory
cd NunchukDescriptorImporter

# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate    # Linux / macOS
# venv\Scripts\activate     # Windows

# Install required dependencies
pip install -r requirements.txt
```

---



##  Features

- Parses Nunchuk-exported descriptors
- Extracts XPUBs + derivation paths
- Derives matching **XPRVs** (from test seeds)
- Replaces XPUBs → XPRVs inside the descriptor
- Calculates the new checksum
- Generates a ready-to-execute `importdescriptors` JSON payload
- Customizable through `config.json`

---

##  Descriptor configuration

Edit `bitcoin.conf` with the desired values, leave as it is for defaults:
```json
{
    "descriptor": {
        "timestamp": null,
        "range": [0, 1000],
        "next_index": 0
    }
}
```

---

## ️ Usage

```bash
python nunchuk_descriptor_import.py
```

You will be prompted to:
1. Paste Nunchuk descriptor  
2. Enter seed phrases (**TEST SEEDS ONLY**)  
3. Enter passphrases  

The script outputs:
- `createwallet` command  
- `importdescriptors` command  


---

##  Example Output

### Create a wallet

```bash
createwallet "WALLET_NAME" false false "" false true
```

### Import descriptors

```bash
importdescriptors "[{ ... }]"
```
---

## Donations

If this tool has been helpful and you would like to support continued development, donations are greatly appreciated.

###  Lightning

* **[sani@blink.sv](mailto:sani@blink.sv)**
* **[sani@walletofsatoshi.com](mailto:sani@walletofsatoshi.com)**

###  On‑Chain

![Bitcoin Donation QR Code](donation.png)

```bash
bc1qsmq2tkxhdpugdrsf5egc536hdqu0tqcdr57njr
```


---


## ️ License

This tool is released under the terms of the MIT license. See LICENSE for more information or see https://opensource.org/licenses/MIT.

---