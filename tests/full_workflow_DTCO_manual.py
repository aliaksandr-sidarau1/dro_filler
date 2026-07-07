"""
FULL SHORT flow from meeting creation to closing
1. DRO Scheduler
2. DRO Supervisor (verify)
3. VIP (approve)
4. DRO Scheduler
5. DRO Team
6. DRO Supervisor (verify)
- Meeting (end time) has passed
8. Agenda supervisor
9. DRO Scheduler
10. DRO Supervisor (verify)
"""


import os
from playwright.sync_api import sync_playwright

import config
from test_data import data_sets
import utils

########### start ############################
#resetting sequence counter
utils.check_date_reset()
# info
utils.run_info(os.path.basename(__file__))
# Launching an isolated browser
utils.browser_launch()

## 0. connecting
with sync_playwright() as p:
    try:
        #open env
        context, page = utils.connect_env(p)

## 1. DRO Scheduler (Creation)
        print(f"\n 1 ", end=" ")
        utils.login(page, utils.DTCO)
        utils.open_manual_creation(page)
        print("filling in fields...")
        current_title = utils.fill_common_fields(page, config.mr_date_today)
        utils.fill_extra_fields(page)
        print("The data is filled in. waiting for generation...")
        utils.create_button(page, current_title)
        utils.verification(page, current_title, data_sets)
        #increase sequence
        utils.sequence_number_update()
        #logout
        page.locator(".cursor-pointer").first.click()

## 2. DRO Supervisor (verify)
        print(f"\n 2 ", end=" ")
        utils.login(page, utils.DTS)
        utils.open_mr(page, current_title)
        utils.verify_button(page, current_title)
        utils.verification(page, current_title, data_sets)
        #logout
        page.locator(".cursor-pointer").first.click()

# 3. VIP (approve)
        print(f"\n 3 ", end=" ")
        utils.login_vip(page, utils.VIP)

        # TODO: move  parts to utils
        page.get_by_role("button", name="All Requests").click()
        page.get_by_text(f"{current_title}").click()
        print("approve...")
        page.get_by_role("button", name="Approve").click(force=True)
        page.get_by_role("button", name="Yes").click()
        page.locator(".animate-pulse").first.wait_for(state="hidden")
        page.wait_for_timeout(5000)

        # logout
        context.clear_cookies()
        page.reload()

## 4. DRO Scheduler
        print(f"\n 4 ", end=" ")
        utils.login(page, utils.DTCO)
        utils.open_mr(page, current_title)
        utils.submit_button(page, current_title)
        utils.verification(page, current_title, data_sets)
        #logout
        page.locator(".cursor-pointer").first.click()

## 5. DRO Team member
        print(f"\n 5 ", end=" ")
        utils.login(page, utils.DTM)
        utils.open_mr(page, current_title)
        utils.submit_button(page, current_title)
        utils.verification(page, current_title, data_sets)
        #logout
        page.locator(".cursor-pointer").first.click()

## 6. DRO Supervisor (verify)
        print(f"\n 6 ", end=" ")
        utils.login(page, utils.DTS)
        utils.open_mr(page, current_title)
        utils.verify_button(page, current_title)
        utils.verification(page, current_title, data_sets)

##  Waiting PMR   ####################
        print(" ==== Waiting PMR ...====")
        premeeting_tab = page.get_by_role("button", name="Pre-Meeting Information", exact=True)
        premeeting_tab.wait_for(state="visible", timeout=600000)

        #logout
        page.locator(".cursor-pointer").first.click()


## 8. Agenda supervisor
        print(f"\n 8 ", end=" ")
        utils.login(page, utils.ATS)
        utils.open_mr(page, current_title)
        utils.submit_button(page, current_title)
        utils.verification(page, current_title, data_sets)
        #logout
        page.locator(".cursor-pointer").first.click()

# 9. DRO Scheduler
        print(f"\n 9 ", end=" ")
        utils.login(page, utils.DTCO)
        utils.open_mr(page, current_title)
        utils.submit_button(page, current_title)
        utils.verification(page, current_title, data_sets)
        #logout
        page.locator(".cursor-pointer").first.click()

## 10. DRO Supervisor (verify)
        print(f"\n 10 ", end=" ")
        utils.login(page, utils.DTS)
        utils.open_mr(page, current_title)

        #Notes
        print("filling in fields...")
        summary_wrapper = page.locator("div.uui-label-top").filter(has_text="Write your meeting notes here")
        summary_editor = summary_wrapper.locator('[data-slate-editor="true"]')
        summary_editor.click()
        page.keyboard.type(data_sets.summary, delay=5)

        #action items
        actions_wrapper = page.locator("div.uui-label-top").filter(has_text="Write your action items here")
        actions_editor = actions_wrapper.locator('[data-slate-editor="true"]')
        actions_editor.click()
        page.keyboard.type(data_sets.action_items, delay=5)

        utils.verify_button(page, current_title)
        utils.verification(page, current_title, data_sets)

        #end time
        utils.run_info(os.path.basename(__file__))

        # # ============================= pause =========================================================##
        # utils.pause()
        # # ============================= inspector =========================================================##
        # utils.inspector(page)

    except Exception as e:
        print(f"\nError: {e}")
        input("ENTER to exit...")
        