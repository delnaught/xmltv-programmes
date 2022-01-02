import re
import sys

from lxml import etree
from datetime import date, timedelta
from pathlib import Path
from xml_diff import compare

date_glob = 'xmltv-programmes-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].html'

def filename_from_date(date):
    return f"xmltv-programmes-{date}.html"

def date_from_filename(filename):
    result = re.search(r".*xmltv-programmes-(.*)\.html", filename)
    return result.group(1)

def programmes_from_xmltv(xmltv):
    xslt = etree.parse('programmes-xslt.xml')
    xform = etree.XSLT(xslt)
    epg = etree.parse(xmltv)
    return xform(epg)

def filename_from_delta(workdir, delta):
    date_now = date.today()
    date_ref = date_now - timedelta(days = delta)
    workpath = Path(workdir)
    ref_path = workdir / filename_from_date(date_ref)
    elapsed = delta
    if not ref_path.exists():
        ref_path = sorted(workpath.glob(date_glob))[0]
        ref_date = date_from_filename(str(ref_path))
        elapsed = date_now - date.fromisoformat(ref_date)
    return elapsed, str(ref_path)

workdir = Path(sys.argv[1])
xmltv = sys.argv[2]
days = int(sys.argv[3])

date_now = date.today()
now_filename = str(workdir / filename_from_date(date_now))

programs = programmes_from_xmltv(xmltv)
programs.write(now_filename, method="html")

elapsed, ref_filename = filename_from_delta(workdir, days)
parser = etree.HTMLParser(huge_tree=True)
baseline = etree.parse(ref_filename, parser = parser)

compare(baseline.getroot(), programs.getroot())

change_xslt = etree.parse('changes-xslt.xml')
change_xform = etree.XSLT(change_xslt)
change = change_xform(programs)
change_text = str(workdir / 'xmltv-programmes-change.html')
change.write(change_text, method="html")
