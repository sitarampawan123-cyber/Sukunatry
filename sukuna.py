import sys
import subprocess
import os
import time
import json
import binascii
import asyncio
import re

# ================= 1. AUTO DEPENDENCY =================
def install_requirements():
    required = {'aiohttp', 'blackboxprotobuf', 'pycryptodome'}
    # Note: Protobuf alag se handle kiya gaya hai version fix ke liye
    
    C_CYAN = "\033[1;36m"
    C_YELLOW = "\033[1;33m"
    C_GREEN = "\033[1;32m"
    C_RESET = "\033[0m"
    
    
    print(f"{C_CYAN}[»] Checking requirements...{C_RESET}")

    # --- 1. SPECIAL CHECK FOR PROTOBUF VERSION (3.20.3) ---
    try:
        import pkg_resources
        try:
            proto_ver = pkg_resources.get_distribution("protobuf").version
            if proto_ver != "3.20.3":
                print(f"{C_YELLOW}[!] Found Protobuf v{proto_ver}. Fixing to v3.20.3...{C_RESET}")
                # Uninstall existing
                subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', 'protobuf', '-y'])
                # Install correct version
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'protobuf==3.20.3'])
                print(f"{C_GREEN}[✓] Protobuf fixed!{C_RESET}")
            else:
                pass # Version sahi hai, kuch mat karo
        except pkg_resources.DistributionNotFound:
            # Agar installed hi nahi hai
            print(f"{C_YELLOW}[!] Installing Protobuf v3.20.3...{C_RESET}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'protobuf==3.20.3'])
    except Exception as e:
        # Fallback agar pkg_resources fail ho jaye
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'protobuf==3.20.3'])

    # --- 2. CHECK REMAINING PACKAGES ---
    installed = set()
    try:
        import pkg_resources
        # Refresh working set after protobuf install
        pkg_resources.working_set = pkg_resources.WorkingSet()
        installed = {pkg.key for pkg in pkg_resources.working_set}
    except ImportError:
        pass

    missing = required - installed
    if missing:
        print(f"\033[1;33m[!] Installing remaining: {', '.join(missing)}{C_RESET}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
            print(f"\033[1;32m[✓] All Requirements Ready!{C_RESET}\n")
        except:
            sys.exit(1)
    else:
        print(f"\033[1;32m[✓] Requirements Satisfied.{C_RESET}\n")

install_requirements()

import aiohttp
import blackboxprotobuf
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from datetime import datetime
import my_pb2       # IMPORTANT: Ye file same folder me honi chahiye
import output_pb2   # IMPORTANT: Ye file same folder me honi chahiye

# ================= 2. CONFIG & DATABASES =================
# AES Config
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

def encrypt_data(data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(data, AES.block_size))
C_RED = "\033[1;31m"
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_CYAN = "\033[1;36m"
C_WHITE = "\033[1;37m"
C_GOLD = "\033[1;33;40m"
C_PINK  = "\033[1;95m"      # Added Bright Pink
C_RESET = "\033[0m"
C_BG_RED = "\033[1;37;41m"
# ================= 0. CREDITS & INFO =================
CREDIT_INFO = f"""
{C_PINK}╔════════════════════════════════════════════════════╗{C_RESET}
{C_PINK}║{C_GOLD}      🔥 GOJO » FIST » GROZA » SUKUNA TOOL 🔥      {C_PINK}║{C_RESET}
{C_PINK}╠════════════════════════════════════════════════════╣{C_RESET}
{C_PINK}║{C_CYAN}   👑 GOJO BUNDLE     : {C_GREEN}UNLIMITED VOID           {C_PINK}║{C_RESET}
{C_PINK}║{C_CYAN}   🥊 FIST SKIN       : {C_YELLOW}DIVERGENT FIST            {C_PINK}║{C_RESET}
{C_PINK}║{C_CYAN}   🔫 GROZA SKIN      : {C_RED}CURSED WEAPON             {C_PINK}║{C_RESET}
{C_PINK}║{C_CYAN}   😈 SUKUNA BUNDLE   : {C_PINK}KING OF CURSES            {C_PINK}║{C_RESET}
{C_PINK}╠════════════════════════════════════════════════════╣{C_RESET}
{C_PINK}║{C_GREEN}          👑 MADE BY SHAZZ 👑                        {C_PINK}║{C_RESET}
{C_PINK}║{C_YELLOW}        🚀 FAST » SAFE » POWERFUL 🚀                {C_PINK}║{C_RESET}
{C_PINK}║{C_CYAN}   📢 TELEGRAM : {C_WHITE}https://t.me/XSHAAZZ       {C_PINK}║{C_RESET}
{C_PINK}╚════════════════════════════════════════════════════╝{C_RESET}
"""


GOJO_PAYLOAD = "A3 1F 3A 86 EC 5E C8 1A F1 2D 16 4D BA 36 49 19"
FIST_PAYLOAD = "FE 95 C8 02 69 21 92 59 4A AC 5F ED 0E 6B 88 51"
GROZA_PAYLOAD = "C8 9F 80 22 56 C2 D4 92 BE A1 B7 B2 42 84 14 A6"
SUKUNA = "9c f6 24 39 e1 48 ca 17 a0 37 bb b5 50 1d 76 7a"

# Files
OUTPUT_FILE = "decoded_output.txt"
SPECIAL_FILE = "special_id.json"
SUMMARY_FILE = "summary_list.txt"
LOG_FILE = "terminal_log.txt"
# In-Memory Buffers (Speed Optimization)
LOG_BUFFER = []
OUTPUT_BUFFER = []

# Server Database (FULL LIST RESTORED)
SERVER_DB = {
    "IND": ("India", "https://client.ind.freefiremobile.com", ["ind", "india", "1"]),
    "BR":  ("Brazil", "https://client.us.freefiremobile.com", ["br", "brazil", "2"]),
    "US":  ("United States", "https://client.us.freefiremobile.com", ["us", "usa", "3"]),
    "SAC": ("South America", "https://client.us.freefiremobile.com", ["sac", "south america", "4"]),
    "NA":  ("North America", "https://client.us.freefiremobile.com", ["na", "north america", "5"]),
    "EU":  ("Europe", "https://clientbp.ggblueshark.com", ["eu", "europe", "6"]),
    "ME":  ("Middle East", "https://clientbp.ggblueshark.com", ["me", "mena", "7"]),
    "ID":  ("Indonesia", "https://clientbp.ggblueshark.com", ["id", "indonesia", "8"]),
    "TH":  ("Thailand", "https://clientbp.ggblueshark.com", ["th", "thailand", "9"]),
    "VN":  ("Vietnam", "https://clientbp.ggblueshark.com", ["vn", "vietnam", "10"]),
    "SG":  ("Singapore", "https://clientbp.ggwhitehawk.com", ["sg", "singapore", "11"]),
    "BD":  ("Bangladesh", "https://clientbp.ggwhitehawk.com", ["bd", "bangladesh", "12"]),
    "PK":  ("Pakistan", "https://clientbp.ggblueshark.com", ["pk", "pakistan", "13"]),
    "MY":  ("Malaysia", "https://clientbp.ggblueshark.com", ["my", "malaysia", "14"]),
    "PH":  ("Philippines", "https://clientbp.ggblueshark.com", ["ph", "philippines", "15"]),
    "RU":  ("Russia", "https://clientbp.ggblueshark.com", ["ru", "russia", "16"]),
}
DEFAULT_URL = "https://clientbp.ggblueshark.com"

# Internal Rare Item DB
RARE_ITEMS_DB = {
    710052004: "Satoru Gojo Bundle (Ultra Rare)",
    801052001: "Gojo Ascension Token",
    902052004: "AVATAR: Satoru Gojo",
    925052001: "BANNER: Satoru Gojo Battle Card",
    710052007: "VOICE: Satoru Gojo Pack",
    921052006: "VOICE: I'm way too strong for him",
    921052032: "VOICE: Domain Expansion Unlimited Void",
    929005202: "STICKER: Satoru Gojo",
    203052003: "CLOTH: Satoru Gojo Top",
    204052003: "CLOTH: Satoru Gojo Bottom",
    205052003: "CLOTH: Satoru Gojo Shoes",
    211052002: "ACCESSORY: Gojo's Blindfold",
    211052003: "ACCESSORY: Gojo Mask",

    # Newly Added Items
    907105202: "FIST: Divergent Fist (Ultra Rare)",
    801052006: "Divergent Fist Token (Redeemable Token)",
    907105203: "PARANG: Tozama",
    903052001: "LOOT BOX: Cathy",
    904000074: "BACKPACK: Vampire",
    904000082: "BACKPACK: The Warrior's Spirit",
    907102837: "GRENADE: Earthshaker",
    907105201: "Groza - Yuji Itadori (Ultra Rare)",
    710052002: "Ryomen Sukuna Bundle(Ultra Rate)",
    204052001: "Ryomen Sukuna Tattoo Bottom",
    211052006: "Ryomen Sukuna White Robe Mask",
    203052001: "Ryomen Sukuna Tattoo Top",
    205052001: "Ryomen Sukuna Tattoo Shoes",
    710052008: "Ryomen Sukuna Voice Pack"
}

# ================= 3. UTILS =================

def log(message):
    timestamp = time.strftime("[%H:%M:%S]")
    clean_msg = f"{timestamp} {message}"
    print(clean_msg)
    # Store in memory for saving at the end
    file_msg = re.sub(r'\033\[[0-9;]*m', '', clean_msg)
    LOG_BUFFER.append(file_msg)

def save_special_json(uid, pwd, item_id, item_name):
    """Saves with guestUid and guestPass"""
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "guestUid": uid,
        "guestPass": pwd,
        "item_id": item_id,
        "item_name": item_name
    }
    data_list = []
    if os.path.exists(SPECIAL_FILE):
        try:
            with open(SPECIAL_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content: data_list = json.loads(content)
        except: data_list = []
    
    data_list.append(entry)
    with open(SPECIAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=4)

def save_raw_output(data):
    try:
        OUTPUT_BUFFER.append(str(data) + "\n" + "-"*50)
    except: pass


def save_final_data():
    if LOG_BUFFER:
        print(f"\n{C_CYAN}[»] Saving Logs...{C_RESET}")
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(LOG_BUFFER))
            
    if OUTPUT_BUFFER:
        print(f"{C_CYAN}[»] Saving Raw Output...{C_RESET}")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(OUTPUT_BUFFER))

    print(f"\n{C_YELLOW}[File] Terminal Log : {LOG_FILE}{C_RESET}")
    print(f"{C_YELLOW}[File] Raw Output   : {OUTPUT_FILE}{C_RESET}")

def recursive_find_items(data, found_list):
    if isinstance(data, dict):
        for k, v in data.items():
            recursive_find_items(v, found_list)
    elif isinstance(data, list):
        for item in data:
            recursive_find_items(item, found_list)
    elif isinstance(data, int):
        if 100000000 <= data <= 999999999:
            # ID yaha se hata diya, print me add karenge color ke sath
            name = RARE_ITEMS_DB.get(data, "Unknown Item") 
            if not any(x['id'] == data for x in found_list):
                found_list.append({"id": data, "name": name})

def select_server():
    print(f"\n{C_CYAN}[ SERVER SELECTION ]{C_RESET}")
    i = 0
    # Restore the full list loop
    for code, data in SERVER_DB.items():
        num = data[2][-1] 
        print(f" {C_YELLOW}[{num}]{C_RESET} {data[0]:<15}", end="")
        if (i + 1) % 2 == 0: print()
        i += 1
    
    print(f"\n {C_YELLOW}[0]{C_RESET} Other/Unknown (Auto)")

    choice = input(f"\n{C_CYAN}[?] Enter Region (Name, Code or Number): {C_RESET}").strip().lower()
    
    for code, data in SERVER_DB.items():
        if choice in data[2] or choice == code.lower():
            print(f"{C_GREEN}[✓] Selected: {data[0]} Server{C_RESET}")
            return data[1]
            
    print(f"{C_YELLOW}[!] Defaulting to Global (Blueshark).{C_RESET}")
    return DEFAULT_URL

# ================= 4. CORE REQUESTS =================


EXTERNAL_API_URL = "https://ob52jwt-rho.vercel.app/token"

async def get_token_external(session, uid, password, retries):
    params = {'uid': uid, 'password': password}
    for _ in range(retries):
        try:
            async with session.get(EXTERNAL_API_URL, params=params, ssl=False, timeout=8) as res:
                if res.status == 200:
                    data = await res.json()
                    return data.get("token", data)
        except:
            await asyncio.sleep(0.2)
    return None




async def get_token(session, uid, password, retries):
    # 1. Garena OAuth (Get Access Token)
    oauth_url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    payload = {
        'uid': uid,
        'password': password,
        'response_type': "token",
        'client_type': "2",
        'client_secret': "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        'client_id': "100067"
    }
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(SM-M526B ;Android 13;pt;BR;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip"
    }

    access_token = None
    open_id = None

    # OAuth Retry Loop
    for _ in range(retries):
        try:
            async with session.post(oauth_url, data=payload, headers=headers, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    access_token = data.get('access_token')
                    open_id = data.get('open_id')
                    break
        except:
            await asyncio.sleep(0.5)
    
    if not access_token or not open_id:
        return None

    # 2. Major Login (Try Multiple Platforms like app.py)
    login_url = "https://loginbp.ggblueshark.com/MajorLogin"
    login_headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Content-Type": "application/octet-stream",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB52"
    }

    # Platforms to try (Guest/Google/etc) - Same as app.py
    platforms = [8, 3, 4, 6]

    for platform in platforms:
        try:
            # Prepare Protobuf Data using my_pb2 (Safe Encoding)
            game_data = my_pb2.GameData()
            game_data.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            game_data.game_name = "free fire"
            game_data.game_version = 1
            game_data.version_code = "1.111.1"
            game_data.os_info = "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)"
            game_data.device_type = "Handheld"
            game_data.network_provider = "Verizon Wireless"
            game_data.connection_type = "WIFI"
            game_data.screen_width = 1280
            game_data.screen_height = 960
            game_data.dpi = "240"
            game_data.cpu_info = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
            game_data.total_ram = 5951
            game_data.gpu_name = "Adreno (TM) 640"
            game_data.gpu_version = "OpenGL ES 3.0"
            game_data.user_id = "Google|74b585a9-0268-4ad3-8f36-ef41d2e53610"
            game_data.ip_address = "172.190.111.97"
            game_data.language = "en"
            game_data.open_id = open_id
            game_data.access_token = access_token
            game_data.platform_type = platform  # Dynamic Platform
            game_data.field_99 = str(platform)
            game_data.field_100 = str(platform)

            # Encrypt
            encrypted_body = encrypt_data(game_data.SerializeToString())

            # Request
            async with session.post(login_url, data=encrypted_body, headers=login_headers, ssl=False, timeout=6) as r:
                if r.status == 200:
                    resp_data = await r.read()
                    
                    # Decode using output_pb2 (Reliable Parsing)
                    try:
                        response_proto = output_pb2.Garena_420()
                        response_proto.ParseFromString(resp_data)
                        
                        # Check if token exists
                        if response_proto.token:
                            return response_proto.token
                    except:
                        # Fallback: Try manual search if proto parsing fails
                        decoded_msg, _ = blackboxprotobuf.decode_message(resp_data)
                        def find_token(d):
                            if isinstance(d, dict):
                                for k, v in d.items():
                                    res = find_token(v)
                                    if res: return res
                            elif isinstance(d, str) and d.startswith("eyJ"):
                                return d
                            return None
                        found = find_token(decoded_msg)
                        if found: return found

        except Exception:
            pass
        
        # Small delay before trying next platform
        await asyncio.sleep(0.1)

    return None

async def gacha_req(session, token, payload, url, max_retries):
    if not url.endswith("/PurchaseGacha"):
        url = f"{url}/PurchaseGacha"

    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Authorization': f"Bearer {token}",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB52"
    }
    
    last_status = 0
    
    for attempt in range(1, max_retries + 1):
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with session.post(url, headers=headers, data=payload, ssl=False, timeout=timeout) as res:
                last_status = res.status
                if res.status == 200:
                    return 200, await res.read()
                elif res.status in [401, 403]:
                    # Bad Token/Forbidden - No Retry
                    return res.status, None
                else:
                    # Server Error - Retry
                    await asyncio.sleep(0.2)
        except:
            last_status = 999
            await asyncio.sleep(0.3)
            
    return last_status, None

# ================= 5. MAIN LOGIC =================

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    for c in CREDIT_INFO:
        print(c, end="", flush=True)
        time.sleep(0.0005)
    print()
    open(LOG_FILE, 'w').close()

    # 1. FILE INPUT
    while True:
        p = input(f"{C_YELLOW}[?] Enter path of UID file (e.g. /sdcard/guestAcc.json): {C_RESET}").strip()
        p = p.replace('"', '').replace("'", "")
        if os.path.exists(p): break
        print(f"{C_RED}[!] File not found.{C_RESET}")

    # Load Accounts
    try:
        with open(p, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        print(f"{C_GREEN}[+] Loaded {len(accounts)} Accounts{C_RESET}")
    except:
        print(f"{C_RED}[!] Invalid JSON Format.{C_RESET}")
        return

    # 2. SERVER SELECTION (LIST RESTORED)
    target_url = select_server()

    # 3. SPIN ITEM SELECTION (NEW)
    print(f"\n{C_CYAN}[ CHOOSE ITEM TO SPIN ]{C_RESET}")
    print(f" {C_YELLOW}[1]{C_RESET} Satoru Gojo Bundle")
    print(f" {C_YELLOW}[2]{C_RESET} Divergent Fist")
    print(f" {C_YELLOW}[3]{C_RESET} GROZA SKIN")
    print(f" {C_YELLOW}[4]{C_RESET} SUKUNA")
    
    item_choice = input(f"\n{C_CYAN}[?] Enter Choice (1, 2 or 3): {C_RESET}").strip()
    
    if item_choice == "2":
        target_payload_str = FIST_PAYLOAD
        print(f"{C_GREEN}[✓] Selected: Divergent Fist{C_RESET}")
    elif item_choice == "3":
        target_payload_str = GROZA_PAYLOAD
        print(f"{C_GREEN}[✓] Selected: GROZA SKIN{C_RESET}")
    elif item_choice == "4":
        target_payload_str = SUKUNA
        print(f"{C_GREEN}[✓] Selected: SUKUNA{C_RESET}")
    else:
        target_payload_str = GOJO_PAYLOAD
        print(f"{C_GREEN}[✓] Selected: Satoru Gojo Bundle{C_RESET}")

    # 4. INPUTS
    try:
        login_retry = int(input(f"{C_CYAN}[?] Account Login Retry Count (Default 3): {C_RESET}") or "3")
        # Spin retry removed from input, hardcoded to 3
        spin_retry  = 3 
        
        # New: Start Index Input
        start_from = int(input(f"{C_CYAN}[?] Start from Account Number (Default 1): {C_RESET}") or "1") - 1
        if start_from < 0: start_from = 0
    except:
        login_retry = 3
        spin_retry = 3
        start_from = 0

    payload = binascii.unhexlify(target_payload_str.replace(" ", ""))
    FINAL_HITS = []
    total_rare_found = 0  # Counter start

    print(f"\n{C_GREEN}[*] Hunting Started from Account {start_from + 1}...{C_RESET}\n")

    # Logic vars for switching
    consecutive_internal_fails = 0
    external_mode_counter = 0

    async with aiohttp.ClientSession() as session:
        # Loop accounts list starting from 'start_from' index
        for i, acc in enumerate(accounts[start_from:], start=start_from):
            uid = str(acc.get("uid", "Unknown"))
            pwd = acc.get("password", "Unknown")
            
            # Updated: Yellow for Info, Cyan for UID + Live TOTAL Count
            mode_msg = f"{C_PINK}[EXT]{C_YELLOW}" if external_mode_counter > 0 else ""
            log(f"{C_GOLD}➤ Account [{i+1}/{len(accounts)}] {mode_msg}» UID: {C_CYAN}{uid}{C_RESET} {C_GREEN}[Total: {total_rare_found}]{C_RESET}")

            token = None

            # --- HYBRID LOGIN LOGIC ---
            if external_mode_counter > 0:
                # Use External API
                token = await get_token_external(session, uid, pwd, login_retry)
                external_mode_counter -= 1
                if external_mode_counter == 0:
                    log(f"{C_CYAN}   [!] Switching back to Internal Method.{C_RESET}")
            else:
                # Use Internal Method
                token = await get_token(session, uid, pwd, login_retry)
                if not token:
                    consecutive_internal_fails += 1
                    # Agar 3 baar fail hua, to next 5 accounts ke liye External set karo
                    if consecutive_internal_fails >= 3:
                        log(f"{C_PINK}   [!] Internal Failed 3 times. Switching to External for next 5 accounts.{C_RESET}")
                        external_mode_counter = 5
                        consecutive_internal_fails = 0
                else:
                    # Success hua to fail counter reset
                    consecutive_internal_fails = 0
            # --------------------------

            if not token:
                log(f"{C_RED}   [✗] Token Failed (After {login_retry} retries){C_RESET}")
                continue

            # 2. Spin
            status_code, resp = await gacha_req(session, token, payload, target_url, spin_retry)
            
            if status_code == 200 and resp:
                try:
                    # --- GZIP/ZLIB AUTO DETECTION FIX ---
                    # Agar server compressed data bhejta hai to pehle decompress karo
                    import zlib
                    if resp.startswith(b'\x1f\x8b'): # GZIP Signature
                        try:
                            resp = zlib.decompress(resp, 16+zlib.MAX_WBITS)
                        except: pass
                    
                    # --- DECODING ---
                    try:
                        data, _ = blackboxprotobuf.decode_message(resp)
                    except ValueError:
                        # Agar "could not convert string to float" aya to ignore karo
                        log(f"{C_RED}   [!] Server sent garbage data (Ignored){C_RESET}")
                        continue
                    except Exception:
                        # Koi aur decode error
                        log(f"{C_RED}   [!] Invalid Protobuf Response{C_RESET}")
                        continue

                    save_raw_output(data)
                    
                    found_items = []
                    recursive_find_items(data, found_items)
                    
                    if found_items:
                        for item in found_items:
                            name = item['name']
                            iid = item['id']
                            
                            # Logic: Agar "Unknown" nahi hai tabhi Rare maano
                            is_rare = "Unknown" not in name
                            
                            if is_rare:
                                # Counter Update
                                total_rare_found += 1
                                
                                # === RARE ITEM FOUND (With Live Count) ===
                                log(f"   {C_GOLD}★ FOUND: {name} {C_PINK}({iid}){C_RESET} {C_BG_RED} [Total: {total_rare_found}] {C_RESET}")
                                
                                # 2. Save to special_id.json (Real-time)
                                save_special_json(uid, pwd, iid, name)
                                
                                # 3. Add to Final Summary List
                                FINAL_HITS.append(f"UID: {uid} » Pass: {pwd} » Item: {name}")
                                
                            else:
                                # === UNKNOWN ITEM ===
                                # Sirf Console me dikhao (Green + Pink ID)
                                # NOTE: Ye na JSON me jayega, na Final List me
                                log(f"   {C_GREEN}» {name} {C_PINK}({iid}){C_RESET}")
                    else:
                        log(f"{C_GREEN}   [✓] Decoded (No valid items){C_RESET}")

                except Exception as e:
                    log(f"{C_RED}   [!] Decode Error: {e}{C_RESET}")
            else:
                err_msg = f"HTTP {status_code}" if status_code != 999 else "Connection Fail"
                log(f"{C_RED}   [✗] Error: {err_msg}{C_RESET}")

            # Speed badhane ke liye sleep kam kar diya (0.1s fast but safe)
            await asyncio.sleep(0)

    # ================= FINAL SUMMARY =================
    print(f"\n{C_CYAN}=========================================={C_RESET}")
    print(f"{C_WHITE}           FINAL HUNT REPORT             {C_RESET}")
    print(f"{C_CYAN}=========================================={C_RESET}")
    
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("=== HITS SUMMARY ===\n")
        if FINAL_HITS:
            for hit in FINAL_HITS:
                print(f"{C_GREEN}>> {hit}{C_RESET}")
                f.write(hit + "\n")
        else:
            print(f"{C_WHITE}No special items found in this session.{C_RESET}")
            f.write("No special items found.")
            
    print(f"\n{C_YELLOW}[File] Special JSON : {SPECIAL_FILE}{C_RESET}")
    print(f"{C_YELLOW}[File] Final List   : {SUMMARY_FILE}{C_RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{C_RED}[!] Script Stopped by User (CTRL+C).{C_RESET}")
    finally:
        # Ye hamesha chalega (Chahe Complete ho ya Stop kiya jaye)
        save_final_data()