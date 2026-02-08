import os
import time
from winotify import Notification, audio


def notifiy_report(text: str, report_filepath: str) -> None:

    notification = Notification(
        app_id="CopartScraper",
        title="Updates",
        msg=text,
        duration="short"
    )

    notification.set_audio(audio.Default, loop=False)

    if report_filepath:
        report_filepath = os.path.abspath(report_filepath)
        notification.add_actions(
            label="Open report",
            launch=f'file:///{report_filepath}'
        )

    notification.show()
