from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import datetime
import time
import uuid
import re
import urllib
import json
import os

from .models import LotData, CarCondition
from .config import TIMEOUT, STATIC_WAIT, AUCTION_NAMES, IMAGE_PATH

class CopartScraper:
    """
    Handles all Selenium browser automation and page-level data extraction.
    """

    def __init__(self, headless: bool = False):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.page_load_strategy = "eager"

        if headless:
            chrome_options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(options=chrome_options)

    def run(self, existing_ids: list[int], db, changed_cars: list[dict]):
        """
        Main scraping workflow. Takes:
        - existing_ids: list of IDs already in the database
        - db: database connection
        - changed_cars: list to store new/updated/removed cars
        """
        self.db = db
        self.navigate_to_first_page()

        # Track IDs found during this scrape
        current_ids = []

        while True:
            lots = self.extract_page_lots()
            
            for lot in lots:
                current_ids.append(lot.id)
                old_data = db.fetch_lot(lot.id)
                if old_data:
                    # Update if anything changed
                    if self._has_changed(lot, old_data):
                        changed_cars.append(self._lot_to_dict(lot, "Updated"))
                        db.delete_lot(lot.id)
                        db.insert_lot(lot)
                else:
                    changed_cars.append(self._lot_to_dict(lot, "New"))
                    db.insert_lot(lot)
                    
            if not self.next_page():
                break

        # Check for removed cars
        removed_ids = set(existing_ids) - set(current_ids)
        for lot_id in removed_ids:
            old_data = db.fetch_lot(lot_id)
            if old_data:
                changed_cars.append(self._lot_to_dict(
                    LotData(
                        image_id=old_data[0],
                        lot_url=old_data[1],
                        id=old_data[2],
                        name=old_data[3],
                        odometer=old_data[4],
                        conditions=CarCondition(*old_data[5].split('|')),
                        auction=old_data[6],
                        start_date=old_data[7],
                        last_check=None,
                        current_bid=old_data[8],
                        buy_now=old_data[9]
                    ),
                    "Removed"
                ))
            db.delete_lot(lot_id)

    def _has_changed(self, lot: LotData, old_lot: LotData) -> bool:
        """Check if a lot has any meaningful changes."""
        return (
            lot.name != old_lot.name
            or lot.odometer != old_lot.odometer
            or lot.conditions != old_lot.conditions
            or lot.current_bid != old_lot.current_bid
            or lot.buy_now != old_lot.buy_now
        )

    def _get_image_id(self, lot_id: int) -> str:
        lot = self.db.fetch_lot(lot_id)
        return lot.image_id if lot and lot.image_id else ""

    def _lot_to_dict(self, lot, event: str) -> dict:
        return {
            "image_id": lot.image_id,
            "lot_url": lot.lot_url,
            "name": lot.name,
            "conditions": str(lot.conditions),
            "current_bid": lot.current_bid,
            "buy_now": lot.buy_now,
            "start_date": lot.start_date,
            "auction": lot.auction,
            "event": event
        }


    def navigate_to_first_page(self) -> None:
        self.driver.maximize_window()

        self.driver.get("https://www.copart.com")
        time.sleep(2)  # allow app + cookies to initialize

        search_criteria = {
            "query": ["*"],
            "filter": {
                "TMTP": [
                    "transmission_type:\"MANUAL\""
                ],
                "SLOC": [
                    f"auction_host_name:\"{name}\""
                    for name in AUCTION_NAMES
                ],
            },
            "searchName": "",
            "watchListOnly": False,
            "freeFormSearch": False,
        }

        encoded_criteria = urllib.parse.quote(
            json.dumps(search_criteria, separators=(",", ":"))
        )

        url = (
            "https://www.copart.com/lotSearchResults"
            "?free=true"
            "&query="
            "&searchCriteria=" + encoded_criteria
        )

        self.driver.get(url)

    
    def extract_page_lots(self) -> list[LotData]:
        time.sleep(STATIC_WAIT)

        rows = self.driver.find_elements(
            By.XPATH,
            "//table[contains(@id, '-table')]//tbody/tr"
        )

        lots: list[LotData] = []

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 5:
                continue

            image_cell = cells[0]
            link = image_cell.find_element(By.XPATH, ".//a[@href]")
            lot_url = link.get_attribute("href")

            lot = LotData(
                image_id="",
                lot_url=lot_url,
                id=0,
                name="",
                odometer="",
                conditions=None,
                auction="",
                start_date=None,
                last_check=None,
                current_bid="",
                buy_now=""
            )

            text = cells[1].text
            lines = [l for l in text.split("\n") if l.strip()]
            lot.name = lines[0] if lines else ""

            match = re.search(r"#\s*(\d+)", text)
            if not match:
                raise ValueError(f"Could not find lot number in text: {text}")

            lot_id = match.group(1)
            lot.id = int(lot_id)

            existing_image_id = self._get_image_id(lot_id)

            if existing_image_id:
                lot.image_id = existing_image_id
            else:
                image_id = f"{uuid.uuid4()}.png"
                lot.image_id = image_id

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    image_cell
                )

                img = image_cell.find_element(By.XPATH, ".//img")
                img.screenshot(os.path.join(IMAGE_PATH, image_id))

            if len(cells) > 2:
                lines = cells[2].text.split("\n")
                lot.odometer = " ".join(lines[1:]) if len(lines) > 1 else cells[2].text

            if len(cells) > 3:
                parts = cells[3].text.split("\n")
                parts = [""] * max(0, 3 - len(parts)) + parts
                lot.conditions = CarCondition(*parts[-3:])

            if len(cells) > 4:
                parts = cells[4].text.split("\n")
                lot.auction = parts[0] if parts else ""

                date_text = parts[-1] if len(parts) > 1 else ""
                if "Live Now" in date_text:
                    lot.start_date = datetime.datetime.now()
                else:
                    match = re.search(r"Auction in (\d+)D (\d+)H (\d+)min", date_text)
                    if match:
                        d, h, m = map(int, match.groups())
                        lot.start_date = datetime.datetime.now() + datetime.timedelta(
                            days=d, hours=h, minutes=m
                        )

            if len(cells) > 5:
                parts = cells[5].text.split("\n")
                lot.current_bid = parts[1] if len(parts) > 1 else ""
                lot.buy_now = parts[-1] if "Buy Now" in cells[5].text else ""

            lot.last_check = datetime.datetime.now()
            lots.append(lot)

        return lots



    def next_page(self) -> bool:
        time.sleep(STATIC_WAIT)

        buttons = self.driver.find_elements(
            By.XPATH, "//button[contains(@class,'p-paginator-next')]"
        )

        if not buttons:
            return False

        next_btn = buttons[0]

        if "p-disabled" in next_btn.get_attribute("class"):
            return False

        next_btn.click()
        return True

    def close(self) -> None:
        self.driver.quit()