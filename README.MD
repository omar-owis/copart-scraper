# Copart Manual Car Scraper

Web scraper that monitors Copart auctions for manual transmission vehicles.
It detects new listings, updates, and removed listings, stores results in a local SQLite database, and sends Windows toast notifications with an HTML report when changes are found.

## Features

- Scrapes Copart for manual transmission cars 
- Detects:
    - New listings
    - Updated listings
    - Removed listings
- Persistent storage using SQLite
- Generates HTML reports
- Windows toast notifications via winotify
- Selenium browser automation (headless by default)
- Setup windows task scheduler to automatically run scraper


## Requirements

- **Windows**
- **Python 3.11+**
- **Google Chrome**

## Python Dependencies

- **Selenium>=4.40.0**
- **Winotify**

## Installation

### 1. Clone the repository

```
git clone https://github.com/omar-owis/copart-scraper.git
cd copartscraper
```


### 2. Run setup

```
setup.bat
```

 **Note:**
This script installs required dependencies and registers a Windows Task Scheduler job for the scraper.

## Configuring Auctions

Edit `copartscraper/config.py`:
```
AUCTION_NAMES = [
    "OK - OKLAHOMA CITY",
    "KS - WICHITA",
]
```

Add or remove auction names to control which Copart locations are scraped.

**Important:** Auction names must match Copart exactly (case, spacing, and formatting). If the name does not match exactly, no listings will be scraped.

## Running the Scraper Manually

Run the scraper via the module entry point:

``` 
python -m copartscraper
```

## CLI Arguments
| Flag | Description | 
| --- | --- |
| -s, --show-browser | Show the Chrome browser (disables headless mode) |

**Default behavior:**

Selenium runs in headless mode

**Example (show browser UI):**

```
python -m copartscraper --show-browser
```

## Removing the Scheduled Task

To remove the Windows Task Scheduler job:

```
remove_task.bat
```

## Architecture Overview
### High-Level Flow

1. Parse CLI arguments
2. Create required directories:
   - `images/`
   - `reports/`
3. Load existing lot IDs from the SQLite database
4. Launch the Selenium scraper
5. Scrape all pages containing manual transmission listings
6. Detect listing changes:
   - New lots
   - Updated lots
   - Removed lots
7. Update the database with the latest results
8. Generate an HTML report (only if changes are detected)
9. Send a Windows toast notification


## Reports & Notifications

- Reports are saved as HTML files

- Notifications are delivered using Windows toast notifications

- Clicking the notification opens the generated report (if changes exist)

## Notes

- This project relies on Copart’s website structure and may break if the site changes
- Intended for personal use
- Be mindful of Copart’s Terms of Service

## License

**MIT License**
See [LICENSE](LICENSE) for more information
