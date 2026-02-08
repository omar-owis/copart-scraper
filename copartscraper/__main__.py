from copartscraper.scraper import CopartScraper
from copartscraper.database import CopartDatabase
from copartscraper.reporter import generate_html
from copartscraper.config import IMAGE_PATH, REPORTS_PATH

import datetime
import os
import argparse

def parse_args():
    p = argparse.ArgumentParser(description="Copart Manuel Car Webscraper")
    
    p.add_argument('-s', '--show-browser', dest='headless', action='store_false',
                   help="Run Selenium in headless mode")
    return p.parse_args()

def main():
    args = parse_args()

    os.makedirs(IMAGE_PATH, exist_ok=True)
    os.makedirs(REPORTS_PATH, exist_ok=True)
    db = CopartDatabase()
    scraper = CopartScraper(args.headless)

    existing_ids = db.fetch_all_ids()
    changed_cars = []

    scraper.run(existing_ids, db, changed_cars)

    generate_html(changed_cars)
    db.close()

if __name__ == "__main__":
    main()