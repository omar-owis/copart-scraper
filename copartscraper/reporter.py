import datetime
import os
from typing import List

from .config import IMAGE_PATH, REPORTS_PATH

def generate_html(changed_cars: List[dict]) -> None:
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{timestamp}.html"

    rows = ""
    for car in changed_cars:
        rows += f"""
        <tr>
            <td><img src="../{IMAGE_PATH}{car['image_id']}" height="116" /></td>
            <td>{car['name']}</td>
            <td>{car['conditions']}</td>
            <td>{car['current_bid']}</td>
            <td>{car['buy_now']}</td>
            <td>{car['start_date']}</td>
            <td>{car['auction']}</td>
            <td><a href="{car['lot_url']}">View</a></td>
            <td>{car['event']}</td>
        </tr>
        """

    html = f"""
    <html>
    <body>
        <h1>Copart Auction Updates</h1>
        <table border="1">
            <tr>
                <th>Image</th><th>Name</th><th>Conditions</th>
                <th>Bid</th><th>Buy Now</th><th>Date</th>
                <th>Auction</th><th>URL</th><th>Event</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """

    with open(os.path.join(REPORTS_PATH, filename), "w") as f:
        f.write(html)