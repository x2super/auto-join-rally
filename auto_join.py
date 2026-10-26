import os
import sys
import time
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://sattha.enrolljoin.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def resolve_club(target, base_url=BASE_URL):
    target_str = str(target).strip()
    if len(target_str) == 8 and target_str.isdigit():
        return target_str, "8176"
    clean = target_str.upper().replace("H", "")
    dump_path = os.path.join(os.path.dirname(__file__), "quick_dump.json")
    if os.path.exists(dump_path):
        try:
            with open(dump_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for a in data.get("activities", []):
                if a.get("code", "").upper().replace("H", "") == clean or a.get("activity_id") == target_str:
                    return a["activity_id"], a.get("category_id", "8176")
        except Exception:
            pass

    for cat in ["8176", "1647"]:
        try:
            r = requests.post(f"{base_url}/1708/7588/{cat}?q=0", data={"catalogue": "1"}, headers=HEADERS, timeout=8)
            soup = BeautifulSoup(r.text, "html.parser")
            for tr in soup.find_all("tr", class_="catalog-row"):
                aid = tr.get("data-activity-code")
                td = tr.find("td", class_="catalog-code")
                if td and aid and (td.text.strip().upper().replace("H", "") == clean or aid == target_str):
                    return aid, cat
        except Exception:
            pass

    return target_str, "8176"

def wait_until(target_time_str):
    if not target_time_str or not target_time_str.strip():
        return
    now = datetime.now()
    parts = [int(p) for p in target_time_str.strip().split(":")]
    hour = parts[0]
    minute = parts[1] if len(parts) > 1 else 0
    second = parts[2] if len(parts) > 2 else 0

    target_dt = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
    if target_dt <= now:
        return

    last_tick = 0
    while True:
        rem = (target_dt - datetime.now()).total_seconds()
        if rem <= 0.05:
            sys.stdout.write(f"\r{' ' * 50}\r")
            sys.stdout.flush()
            break
        if time.time() - last_tick >= 0.5:
            m, s = divmod(int(rem), 60)
            h, m = divmod(m, 60)
            sys.stdout.write(f"\r[T - {h:02d}:{m:02d}:{s:02d}] Waiting for {target_time_str}... ")
            sys.stdout.flush()
            last_tick = time.time()
        time.sleep(0.01 if rem <= 1.5 else 0.2)

class Sniper:
    def __init__(self, student_id, citizen_id, club_id, interval=0.2):
        self.sid = str(student_id).strip()
        self.cid = str(citizen_id).strip()
        self.raw_club = str(club_id).strip()
        self.interval = float(interval)
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.act_id, self.cat_id = resolve_club(self.raw_club)
        self.api_join = f"{BASE_URL}/1509/7401/{self.cat_id}"
        self.session_file = os.path.join(os.path.dirname(__file__), f"session_{self.sid}.json")

    def load_session(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    self.session.cookies.update(json.load(f))
                r = self.session.get(f"{BASE_URL}/activities/student", allow_redirects=False, timeout=5)
                return r.status_code == 200
            except Exception:
                pass
        return False

    def save_session(self):
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.session.cookies.get_dict(), f)
        except Exception:
            pass

    def login(self):
        url = f"{BASE_URL}/login?q={self.cat_id}"
        try:
            r = self.session.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            vs = soup.find("input", id="__VIEWSTATE")
            vsg = soup.find("input", id="__VIEWSTATEGENERATOR")
            ev = soup.find("input", id="__EVENTVALIDATION")
            if not vs:
                return False

            payload = {
                "__VIEWSTATE": vs.get("value", ""),
                "__VIEWSTATEGENERATOR": vsg.get("value", "") if vsg else "",
                "ctl00$ContentPlaceHolder_body$txtstudent_stdCode": self.sid,
                "ctl00$ContentPlaceHolder_body$txtstudent_stdCard": self.cid,
                "__EVENTTARGET": "ctl00$ContentPlaceHolder_body$btnOK",
                "__EVENTARGUMENT": ""
            }
            if ev:
                payload["__EVENTVALIDATION"] = ev.get("value", "")

            post_r = self.session.post(url, data=payload, allow_redirects=False, timeout=10)
            if post_r.status_code == 302 and "login" not in post_r.headers.get("Location", "").lower():
                self.session.get(f"{BASE_URL}{post_r.headers.get('Location')}", timeout=5)
                self.save_session()
                return True
        except Exception:
            pass
        return False

    def is_enrolled(self):
        try:
            r = self.session.get(f"{BASE_URL}/activities/student", timeout=6)
            return self.act_id in r.text or self.raw_club in r.text
        except Exception:
            return False

    def fire(self):
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{BASE_URL}/activities/{self.cat_id}"
        }
        payload = json.dumps({"_mActivities_Code": self.act_id})
        try:
            r = self.session.post(self.api_join, data=payload, headers=headers, timeout=5)
            if r.status_code in (301, 302) and "login" in r.headers.get("Location", "").lower():
                return False, "AUTH"
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                st = str(data[0].get("status", ""))
                msg = data[0].get("alert_text", "")
                return (st == "1"), msg
        except Exception:
            pass
        return False, "RETRY"

    def run(self):
        if not self.load_session():
            if not self.login():
                print(f"[{self.sid}] Login failed")
                return False
            print(f"[{self.sid}] Logged in")
        else:
            print(f"[{self.sid}] Session OK")

        if self.is_enrolled():
            print(f"[{self.sid}] Already enrolled in {self.raw_club}")
            return True

        print(f"[{self.sid}] Targeting {self.raw_club} ({self.act_id})")
        last_msg = ""
        while True:
            ok, msg = self.fire()
            if ok:
                print(f"[{self.sid}] SUCCESS: {self.raw_club} ({msg})\a")
                return True
            if msg == "AUTH":
                self.login()
                time.sleep(0.5)
                continue
            if msg != last_msg and msg != "RETRY":
                print(f"[{self.sid}] {msg}")
                last_msg = msg
            time.sleep(self.interval)

def load_config():
    path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def main():
    cfg = load_config()
    items = []
    global_start = ""

    if isinstance(cfg, dict):
        global_start = cfg.get("start_time", "")
        if "accounts" in cfg and isinstance(cfg["accounts"], list):
            items = cfg["accounts"]
        elif cfg.get("student_id") and cfg.get("club_id"):
            items = [cfg]
    elif isinstance(cfg, list):
        items = cfg

    if not items or not any(it.get("student_id") and it.get("club_id") for it in items):
        sid = input("Student ID: ").strip()
        cid = input("Citizen ID: ").strip()
        club = input("Club ID: ").strip()
        global_start = input("Start time (HH:MM or Enter for now): ").strip()
        items = [{"student_id": sid, "citizen_id": cid, "club_id": club, "start_time": global_start}]

    start_time = global_start or items[0].get("start_time", "")
    if start_time:
        wait_until(start_time)

    snipers = [
        Sniper(
            it["student_id"],
            it.get("citizen_id", ""),
            it["club_id"],
            it.get("interval", 0.2)
        )
        for it in items if it.get("student_id") and it.get("club_id")
    ]

    if not snipers:
        print("No targets.")
        return

    if len(snipers) == 1:
        snipers[0].run()
    else:
        with ThreadPoolExecutor(max_workers=len(snipers)) as ex:
            ex.map(lambda s: s.run(), snipers)

if __name__ == "__main__":
    main()
