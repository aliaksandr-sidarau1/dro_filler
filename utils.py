import os
import re
import subprocess
import time
from datetime import datetime
from playwright.sync_api import expect, Playwright
from pathlib import Path
from test_data import data_sets
import config


########################## technical ###################################

# sequence_number update
last_run_date = "07.07.2026"
sequence_number = 1

def check_date_reset():
    global sequence_number, last_run_date
    current_date_str = datetime.now().strftime("%d.%m.%Y")
    if datetime.now().date() > datetime.strptime(last_run_date, "%d.%m.%Y").date():
        file_path = __file__
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'^sequence_number\s*=\s*\d+', 'sequence_number = 0', content, flags=re.MULTILINE)
        content = re.sub(r'^last_run_date\s*=\s*["\'][^"\']+["\']', f'last_run_date = "{current_date_str}"', content, flags=re.MULTILINE)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        sequence_number = 0
        last_run_date = current_date_str

def sequence_number_update():
    global sequence_number
    file_path = __file__
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'^sequence_number\s*=\s*(\d+)', content, flags=re.MULTILINE)
    current_val = int(match.group(1)) if match else sequence_number
    new_val = current_val + 1
    new_content = re.sub(r'^sequence_number\s*=\s*\d+', f'sequence_number = {new_val}', content, flags=re.MULTILINE)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    sequence_number = new_val

# script statistic
def run_info(test_name):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\n =============   {test_name}   ===   RUN #{sequence_number}   ===   {current_time}   =============\n")

def browser_launch():
    subprocess.Popen([
        os.path.normpath(config.chrome_bin),
        "--remote-debugging-port=9223",
        "--auto-open-devtools-for-tabs",
        f"--user-data-dir={config.TEMP_PROFILE}",
        "--no-first-run",
        "--no-default-browser-check"
    ])
    time.sleep(2)

# open env
def connect_env(p: Playwright):
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9223")
    context = browser.contexts[0]
    page = context.new_page()
    target_url = os.getenv("URL")
    assert target_url, "empty URL"
    print(f"connecting: {target_url}")
    page.goto(target_url)
    return context, page

# pause
def pause():
    print("\n" + "=" * 40)
    input("ENTER to continue...")

# inspector for recording
def inspector(page):
    print("opening the inspector for recording...")
    page.pause()

# creds merge
DTCO = {
    "name": os.getenv("DTCO_NAME"),
    "login": os.getenv("DTCO_LOGIN"),
    "password": os.getenv("DTCO_PASSWORD")}
DTS = {
    "name": os.getenv("DTS_NAME"),
    "login": os.getenv("DTS_LOGIN"),
    "password": os.getenv("DTS_PASSWORD")}
DTM = {
    "name": os.getenv("DTM_NAME"),
    "login": os.getenv("DTM_LOGIN"),
    "password": os.getenv("DTM_PASSWORD")}
ATS = {
    "name": os.getenv("ATS_NAME"),
    "login": os.getenv("ATS_LOGIN"),
    "password": os.getenv("ATS_PASSWORD")
}
VIP = {
    "name": os.getenv("VIP_NAME"),
    "login": os.getenv("VIP_LOGIN"),
    "password": os.getenv("VIP_PASSWORD")}

# Title generation
def get_meeting_title(seq_num, guest):
    return f"PW_AT {config.datestamp}-{seq_num} Meeting with {guest} {config.timestamp}"

# time generation
def get_time_by_sequence(seq_num):
    total_minutes = seq_num * 10
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    return f"{hours:02d}{minutes:02d}"

###################### app functions #################################
# LOGIN
def login(page, user_obj: dict):
    page.context.clear_cookies()
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    page.reload()
    print(f"===== Login: {user_obj["name"]} =====")
    target_url = os.getenv("URL")
    assert target_url, "'URL' empty"
    page.goto(target_url, wait_until="domcontentloaded")
    page.wait_for_selector("input", timeout=10000)
    user_xpath = "//input[not(@type='password') and not(@type='checkbox') and not(@type='hidden')]"
    pass_xpath = "//input[@type='password']"
    user_input = page.locator(user_xpath).first
    pass_input = page.locator(pass_xpath).first
    user_input.click()
    user_input.type(user_obj["login"], delay=1)
    pass_input.click()
    pass_input.type(user_obj["password"], delay=1)
    page.wait_for_timeout(500)
    page.keyboard.press("Enter")
    page.wait_for_function("() => !window.location.href.includes('/login')", timeout=25000)
    print(f" Authorized: {user_obj['login']} ")

def login_vip(page, user_obj: dict):
    page.context.clear_cookies()
    page.reload()
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    page.reload()
    print(f"===== Login: {user_obj["name"]} =====")
    page.goto(os.getenv("URL_VIP"), wait_until="domcontentloaded")
    try:
        page.wait_for_selector("input", timeout=10000)
        user_xpath = "//input[not(@type='password') and not(@type='checkbox') and not(@type='hidden')]"
        pass_xpath = "//input[@type='password']"
        user_input = page.locator(user_xpath).first
        pass_input = page.locator(pass_xpath).first
        user_input.click()
        user_input.type(user_obj["login"], delay=2)
        pass_input.click()
        pass_input.type(user_obj["password"], delay=2)
        page.wait_for_timeout(500)
        page.keyboard.press("Enter")
        page.wait_for_function("() => !window.location.href.includes('/login')", timeout=15000)
    except Exception:
        pass
    print(f" Authorized: {user_obj['login']} ")

# MR CREATION
def open_manual_creation(page):
    print("opening the mr form...")
    page.get_by_role("button", name="Create Meeting Request").click()
    page.get_by_role("button", name="Skip").wait_for(state="visible", timeout=5000)
    page.get_by_role("button", name="Skip").click()

def fill_common_fields(page, mr_date):
    # Title
    current_title = get_meeting_title(sequence_number, data_sets.guest_name)
    page.get_by_role("textbox", name="Title", exact=True).fill(current_title)
    # Guest name
    page.get_by_role("textbox", name="Guest name").fill(data_sets.guest_name)
    page.get_by_role("textbox", name="Guest name").press("Enter")
    target = page.locator("li").get_by_text(data_sets.guest_name, exact=True).first
    target.wait_for(state="visible", timeout=160000)
    target.evaluate("node => node.click()")
    # Guest organization
    page.get_by_role("textbox", name="Guest organization").fill(data_sets.org_name)
    page.get_by_role("textbox", name="Guest organization").press("Enter")
    target = page.locator("li").get_by_text(data_sets.org_name, exact=True).first
    target.wait_for(state="visible", timeout=160000)
    target.evaluate("node => node.click()")
    # dates
    target = page.get_by_role("textbox", name="Arrival date")
    target.click()
    target.press_sequentially(mr_date, delay=50)
    target = page.get_by_role("textbox", name="Departure date")
    target.click()
    target.press_sequentially(mr_date, delay=50)
    target = page.get_by_role("textbox", name="Tentative date")
    target.click()
    target.press_sequentially(mr_date, delay=50)
    # time
    time_from = get_time_by_sequence(sequence_number)
    time_to = get_time_by_sequence(sequence_number + 1)
    target = page.get_by_placeholder("from").first
    target.click()
    page.wait_for_timeout(100)
    target.press("Control+A")
    page.wait_for_timeout(100)
    target.press_sequentially(time_from, delay=100)
    target.press("Enter")
    target = page.get_by_placeholder("to").first
    target.click()
    page.wait_for_timeout(100)
    target.press("Control+A")
    page.wait_for_timeout(100)
    target.press_sequentially(time_to, delay=100)
    target.press("Enter")
    # location
    page.get_by_role("textbox", name="Meeting location").click()
    page.get_by_role("textbox", name="Meeting location").fill("Online")
    # agenda
    field_wrapper = page.locator("div.uui-label-top").filter(has_text="Proposed meeting agenda")
    agenda_editor = field_wrapper.locator('[data-slate-editor="true"]')
    agenda_editor.click()
    page.keyboard.type(data_sets.agenda, delay=1)
    # External Attendees
    current_card = page.locator("div.shadow-meeting-card").filter(has=page.get_by_role("textbox", name="Name", exact=True))
    current_card.get_by_role("textbox", name="Name", exact=True).fill(data_sets.external_name)
    current_card.get_by_role("textbox", name="Position", exact=True).fill(data_sets.external_position)
    current_card.get_by_role("textbox", name="Organization", exact=True).fill(data_sets.external_organization)
    current_card.get_by_role("button", name="Add", exact=True).click()
    # attachments
    project_root = Path(__file__).resolve().parent
    file_path = str(project_root / 'test_data' / 'attachments' / 'AT_Profit_Report.docx')
    page.get_by_test_id("file-input").last.set_input_files(file_path)
    page.get_by_text("AT_Profit_Report").wait_for(state="visible", timeout=15000)
    return current_title

def fill_extra_fields(page      ):
    # Eval framework
    page.get_by_role("button", name="Referral *").click()
    page.get_by_role("listitem").filter(has_text=re.compile(r"^High$")).click()
    page.get_by_role("button", name="Relevance to Pillars *").click()
    page.get_by_role("listitem").filter(has_text=re.compile(r"^High$")).click()
    page.get_by_role("button", name="Abu Dhabi exposure *").click()
    page.get_by_role("listitem").filter(has_text=re.compile(r"^High$")).click()
    # Recommendations
    recommendations_card = page.locator("div.shadow-meeting-card").filter(has_text="Recommendations")
    recommendations_card.get_by_role("textbox", name="Enter referral").fill("AT_Referral")
    recommendations_card.get_by_role("textbox", name="Enter recommendation").fill("AT_Recommend")
    recommendations_card.get_by_role("button", name="Add", exact=True).click()

def create_button(page, current_title):
    button = page.get_by_role("button", name="Create", exact=True)
    button.wait_for(state="visible", timeout=1000)
    button.and_(page.locator("button:not([disabled])")).wait_for(timeout=160000)
    print("saving...")
    page.wait_for_timeout(2000)
    button.click(force=True)
    page.locator(".animate-pulse").first.wait_for(state="hidden")
    page.get_by_role("button", name="All", exact=True).click(timeout=60000)
    page.get_by_text(f"{current_title}").click(timeout=60000)

#  VERIFICATION
def verification(page, title: str, data_set):
    expected = {
        "title": title,
        "guest_name": data_set.guest_name,
        "org_name": data_set.org_name
    }
    card = page.locator("div.w-full.flex-col").filter(has_text=expected['title']).filter(has_text=expected['org_name'])
    expect(card.locator("div.text-2xl").first).to_contain_text(expected['title'], timeout=30000)
    expect(card.locator("div.text-base.font-normal").filter(has_text=expected["org_name"]).first).to_have_text(expected["org_name"], timeout=10000)
    expect(card.locator("div.text-xl.font-semibold").filter(has_text=expected["guest_name"]).first).to_have_text(expected["guest_name"], timeout=10000)
    print(f"verification passed for ({expected['title']})---")

# MR ACTIONS
def open_mr(page, current_title):
    print("open mr...")
    page.get_by_role("button", name="All", exact=True).click()
    page.get_by_text(f"{current_title}").click()

def verify_button(page, current_title):
    print("saving (Verify)...")
    page.wait_for_timeout(3000)
    page.get_by_role("button", name="Verify").click(force=True)
    page.locator(".animate-pulse").first.wait_for(state="hidden")
    page.get_by_role("button", name="All", exact=True).click(timeout=120000)
    page.get_by_text(f"{current_title}").click()

def submit_button(page, current_title):
    print("saving (Submit)...")
    page.wait_for_timeout(3000)
    page.get_by_role("button", name="Submit").click(force=True)
    page.locator(".animate-pulse").first.wait_for(state="hidden")
    page.get_by_role("button", name="All", exact=True).click(timeout=30000)
    page.get_by_text(f"{current_title}").click()