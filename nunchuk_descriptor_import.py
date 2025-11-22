"""
Nunchuck Descriptor Import Tool
-------------------------------

This script converts a descriptor exported from Nunchuk into
a Bitcoin Core-compatible descriptor that contains XPRVs instead of XPUBs.

CONFIG:
    Edit config.json to define:
        - timestamp (or leave null to auto-fill with current time)
        - range
        - next_index
"""

import json
import re
import time
import sys
import hashlib
from mnemonic import Mnemonic
from bip32utils import BIP32Key
from bitcoinrpc.authproxy import AuthServiceProxy
from datetime import datetime

# ---------------------------------------------------------
# Patch ripemd160 for Python 3.10+ using pycryptodome
# ---------------------------------------------------------
try:
    hashlib.new("ripemd160")
except ValueError:
    try:
        from Crypto.Hash import RIPEMD160

        def ripemd160_new(data=b""):
            h = RIPEMD160.new()
            h.update(data)
            return h

        hashlib.new = lambda name, data=b"": ripemd160_new(data) if name.lower() == "ripemd160" else __import__('hashlib').new(name, data)
    except ImportError:
        print("❌ Python 3.10+ requires pycryptodome for ripemd160.")
        sys.exit(1)
        
# ---------------------------------------------------------
# Load Config
# ---------------------------------------------------------
def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)

    # Default timestamp = now
    if not config["descriptor"].get("timestamp"):
        config["descriptor"]["timestamp"] = int(time.time())

    # Apply safe defaults if missing
    config["descriptor"]["range"] = config["descriptor"].get("range", [0, 1000])
    config["descriptor"]["next_index"] = config["descriptor"].get("next_index", 0)

    return config

# ---------------------------------------------------------
# Bitcoin Core Descriptor Checksum Implementation
# ---------------------------------------------------------

INPUT_CHARSET = (
    "0123456789()[],'/*abcdefgh@:$%{}"
    "IJKLMNOPQRSTUVWXYZ&+-.;<=>?!^_|~"
    "ijklmnopqrstuvwxyzABCDEFGH`#\"\\ "
)

CHECKSUM_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def polymod(c, val):
    c0 = c >> 35
    c = ((c & 0x7FFFFFFFF) << 5) ^ val
    if c0 & 1:
        c ^= 0xF5DEE51989
    if c0 & 2:
        c ^= 0xA9FDCA3312
    if c0 & 4:
        c ^= 0x1BAB10E32D
    if c0 & 8:
        c ^= 0x3706B1677A
    if c0 & 16:
        c ^= 0x644D626FFD
    return c


def descriptor_checksum(desc: str) -> str:
    c = 1
    cls = 0
    clscount = 0

    for ch in desc:
        pos = INPUT_CHARSET.find(ch)
        if pos == -1:
            return ""  # Core also returns "" for invalid characters

        c = polymod(c, pos & 31)
        cls = cls * 3 + (pos >> 5)
        clscount += 1

        if clscount == 3:
            c = polymod(c, cls)
            cls = 0
            clscount = 0

    if clscount > 0:
        c = polymod(c, cls)

    # Append 8 zero symbols
    for _ in range(8):
        c = polymod(c, 0)

    c ^= 1  # Prevent appending zeroes from nullifying checksum

    # Produce final 8 chars
    return "".join(CHECKSUM_CHARSET[(c >> (5 * (7 - j))) & 31] for j in range(8))

# ---------------------------------------------------------
# Key Derivation Function
# ---------------------------------------------------------
def generate_key(seed_phrase, passphrase, derivation):
    seed = Mnemonic("english").to_seed(seed_phrase, passphrase)
    root_key = BIP32Key.fromEntropy(seed)

    path_parts = derivation.lstrip("m/").split("/")
    key = root_key

    for part in path_parts:
        if part.endswith("'"):
            index = int(part[:-1]) + 2**31
        else:
            index = int(part)
        key = key.ChildKey(index)

    return key.ExtendedKey(private=True)


# ---------------------------------------------------------
# Build importdescriptors RPC command
# ---------------------------------------------------------
def build_importdescriptors(final_descriptor, cfg):
    obj = [{
        "desc": final_descriptor,
        "timestamp": cfg["descriptor"]["timestamp"],
        "active": True,
        "range": cfg["descriptor"]["range"],
        "next_index": cfg["descriptor"]["next_index"]
    }]

    json_str = json.dumps(obj)
    escaped = json_str.replace('"', '\\"')
    final_cmd = f'importdescriptors \"{escaped}\"'

    return final_cmd

# ---------------------------------------------------------
# Main Program
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "="*70)
    print(" ⚠️  SECURITY WARNING  ⚠️ ")
    print("="*70)
    print("This script is intended ONLY for:")
    print("  • Development")
    print("  • Testing")
    print("  • Local experiments with DUMMY / FAKE seeds")
    print("")
    print("❗ NEVER enter real wallet material:")
    print("  ✘ Real seed phrases")
    print("  ✘ Real private keys")
    print("  ✘ Any other sensitive wallet information")
    print("")
    print("✔️ If real wallet data is ever used, this tool MUST run on:")
    print("  • A fully OFFLINE, AIR-GAPPED device")
    print("  • With all network interfaces disabled")
    print("")
    print("="*70 + "\n")

    # Load configuration
    cfg = load_config()

    print("\n" + "-"*70)
    print(" STEP 1: Provide your Nunchuk descriptor ")
    print("-"*70)
    descriptor = input("Enter the descriptor provided from Nunchuk: ")

    derivation_paths = re.findall(r'\[[0-9a-fA-F]+(/(?:[0-9]+\'/?)*)\]', descriptor)
    derivation_paths = [p.split("/", 1)[1] for p in derivation_paths]

    xpubs = re.findall(r'xpub[0-9A-Za-z]+', descriptor)
    print(f"\nNumber of keys detected: {len(xpubs)}")

    keys_info = []

    # Collect seed phrases
    for i, (derivation, xpub) in enumerate(zip(derivation_paths, xpubs), start=1):
        print("\n" + "-"*50)
        print(f" 🔑 Key #{i} Information")
        print("-"*50)
        print(f"Xpub: {xpub}")
        print(f"Derivation path: {derivation}")
        seed_phrase = input("Enter seed phrase: ")
        passphrase = input("Enter passphrase (leave empty if none): ")

        if not Mnemonic("english").check(seed_phrase):
            print("⚠️ Invalid seed phrase! Exiting...")
            input("\nPress ENTER to exit...")
            exit()

        keys_info.append({
            "derivation": derivation,
            "xpub": xpub,
            "seed_phrase": seed_phrase,
            "passphrase": passphrase
        })

    print("\n" + "-"*70)
    print(" STEP 2: Generating XPRVs from provided seed phrases ")
    print("-"*70)

    for i, key in enumerate(keys_info, start=1):
        xprv = generate_key(key["seed_phrase"], key["passphrase"], key["derivation"])
        key["xprv"] = xprv
        print(f"Key #{i}: {key['xpub'][:15]}... → Xprv: {xprv}")

    # Replace xpubs with xprvs
    updated_descriptor = descriptor.split("#")[0]
    for key in keys_info:
        updated_descriptor = updated_descriptor.replace(key["xpub"], key["xprv"])

    print("\n" + "-"*70)
    print(" STEP 3: Updated Descriptor with XPRV")
    print("-"*70)
    print(updated_descriptor)

    new_checksum = descriptor_checksum(updated_descriptor)
    if not new_checksum:
        print("❌ Invalid descriptor characters — cannot compute checksum.")
        exit()

    final_descriptor = f"{updated_descriptor}#{new_checksum}"

    
    #print("\n" + "-"*70)
    #print(" STEP 4: Descriptor Info from Bitcoin Core RPC ")
    #print("-"*70)
    #print(json.dumps(descriptor_info, indent=4))

    # Final descriptor with checksum
    #new_checksum = descriptor_info["checksum"]
    #final_descriptor = f"{updated_descriptor}#{new_checksum}"
    print("\n" + "-"*70)
    print(" STEP 4: Descriptor with XPRV and new Checksum ")
    print("-"*70)
    print(final_descriptor)

    result = build_importdescriptors(final_descriptor, cfg)

    print("\n" + "="*70)
    print(" STEP 5: Bitcoin Core Wallet Import Instructions ")
    print("="*70)
    
    print("\n1) Create wallet:")
    wallet_name = input("Enter desired wallet name: ")
    print(f"createwallet \"{wallet_name}\" false false \"\" false true")
    
    print("\n2) Import descriptor:")
    print(result)
    
    input("\n✅ Process Completed. Press ENTER to exit...")
