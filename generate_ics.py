import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
import re

def escape_ical(text):
    return text.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')

rss_url = "https://www.outdoorlads.com/events-rss.xml?event_type%5B22%5D=22&event_type%5B23%5D=23&event_type%5B24%5D=24&event_type%5B25%5D=25&event_type%5B26%5D=26&event_type%5B27%5D=27&event_type%5B8%5D=8&event_type%5B61%5D=61&event_type%5B76%5D=76&event_type%5B64%5D=64&event_type%5B65%5D=65&event_type%5B66%5D=66&event_type%5B135%5D=135&event_type%5B11%5D=11&event_type%5B12%5D=12&event_type%5B13%5D=13&event_type%5B15%5D=15&event_type%5B14%5D=14&event_type%5B16%5D=16&event_type%5B77%5D=77&event_type%5B130%5D=130&event_type%5B17%5D=17&event_type%5B32%5D=32&event_type%5B33%5D=33&event_type%5B34%5D=34&event_type%5B35%5D=35&event_type%5B18%5D=18&event_type%5B123%5D=123&event_type%5B19%5D=19&event_type%5B20%5D=20&event_type%5B136%5D=136&event_type%5B21%5D=21&region%5B51%5D=51"

response = requests.get(rss_url)
response.raise_for_status()

root = ET.fromstring(response.content)

ical_lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//OutdoorLads RSS to iCal//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH"
]

for item in root.findall('./channel/item'):
    title = item.findtext('title') or "No Title"
    link = item.findtext('link') or ""
    pub_date = item.findtext('pubDate') or ""
    description = item.findtext('description') or ""

    try:
        dt = parsedate_to_datetime(pub_date)
        dt_utc = dt.strftime('%Y%m%dT%H%M%SZ')
    except Exception:
        continue

    clean_description = escape_ical(re.sub(r'<[^>]+>', '', description))

    ical_lines.extend([
        "BEGIN:VEVENT",
        f"UID:{link}",
        f"DTSTAMP:{dt_utc}",
        f"DTSTART:{dt_utc}",
        f"DTEND:{dt_utc}",
        f"SUMMARY:{escape_ical(title)}",
        f"DESCRIPTION:{clean_description}",
        f"URL:{link}",
        "STATUS:CONFIRMED",
        "SEQUENCE:0",
        "TRANSP:OPAQUE",
        "END:VEVENT"
    ])

ical_lines.append("END:VCALENDAR")

with open("outdoorlads.ics", "w", newline="\r\n") as f:
    f.write("\r\n".join(ical_lines))
