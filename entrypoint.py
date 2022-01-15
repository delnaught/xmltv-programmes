#!/usr/bin/env python3

import re
import sys

from lxml import etree
from datetime import date, timedelta
from pathlib import Path
from xmldiff import main, formatting

date_glob = 'xmltv-programmes-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].xml'
xml_parser = etree.XMLParser(remove_blank_text=True)

def filename_from_date(date):
    return f"xmltv-programmes-{date}.xml"

def date_from_filename(filename):
    result = re.search(r".*xmltv-programmes-(.*)\.xml", filename)
    return result.group(1)

def programmes_from_xmltv(xmltv):
    xslt = etree.parse('xslt/programmes-xslt.xml', xml_parser)
    xform = etree.XSLT(xslt)
    epg = etree.parse(xmltv, parser=xml_parser)
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

current = programmes_from_xmltv(xmltv)
current.write(now_filename, pretty_print = True)

elapsed, ref_filename = filename_from_delta(workdir, days)
reference = etree.parse(ref_filename, xml_parser)

formatter = formatting.XMLFormatter(normalize=formatting.WS_BOTH)

diff_str = main.diff_trees(reference, current,
                           diff_options = {
                               'F': 1.,
                               'uniqueattrs': ['id'],
                               # 'ratio_mode': 'accurate',
                               # 'fast_match': True,
                           },
                           formatter = formatter)

diff_tree = etree.fromstring(diff_str, xml_parser)
wip = etree.ElementTree(diff_tree)
wip.write(str(workdir / 'wip.xml'), pretty_print = True)


change_xslt = etree.parse('xslt/changes-xslt.xml', xml_parser)
change_xform = etree.XSLT(change_xslt)
change = change_xform(diff_tree)
change_text = str(workdir / 'xmltv-programmes-change.html')
change.write(change_text, method="html")
