#!/usr/bin/env python3

import collections
import datetime
import glob
import re
import sys

TSYBULSKY_LABEL = 'tsybulsky'
TSYBULSKY = 'sources/tsybulsky.txt'
TSYBULSKY_START = datetime.date(1851, 10, 25)
GREG_RE = re.compile("^\d{4}-\d{2}-\d{2}$", re.ASCII)

database = {}
source_data = collections.defaultdict(set)
starred_set = set()

def add_to_database(hyear, hmonth, starred, gregorian, name):
  key = (hyear, hmonth)
  value = gregorian.isoformat()
  if key in database:
    if database[key] != value:
      if name == TSYBULSKY_LABEL:
        # Skip this
        return
      print(key)
      print("Existing:", database[key], source_data[key])
      print("New:", value, name)
      sys.exit(1)
  else:
    database[key] = value
  source_data[key].add(name)
  if starred:
    starred_set.add(key)


def check_sanity():
  for key in database:
    hyear, hmonth = key
    this_greg = datetime.date.fromisoformat(database[key])

    if hmonth == 12:
      next_month = (hyear + 1, 1)
    else:
      next_month = (hyear, hmonth + 1)
    if next_month in database:
      next_month_greg = datetime.date.fromisoformat(database[next_month])
      days = (next_month_greg - this_greg).days
      assert days in [29, 30]
    
    if hmonth == 1:
      next_year = (hyear + 1, 1)
      if next_year in database:
        next_year_greg = datetime.date.fromisoformat(database[next_year])
        days = (next_year_greg - this_greg).days
        assert(days in [353, 354, 355])


def dump_database():
  with open("consolidated.txt", "wt") as output_file:
    for key in sorted(database.keys()):
      hyear, hmonth = key
      gregorian = database[key]
      starred = key in starred_set
      sources = ', '.join(sorted(source_data[key]))
      
      output_file.write("%s%d/%d %s # %s\n" % (
        "*" if starred else "",
        hyear,
        hmonth,
        gregorian,
        sources))


def read_sources():
  for filename in glob.glob('sources/*.txt'):
    if filename == TSYBULSKY:
      continue
    name = filename[filename.index('/')+1:-4]
    with open(filename, "rt") as source_file:
      for line in source_file:
        if '#' in line:
          line = line[:line.index('#')]
        line = line.strip()
        if not line:
          continue
        line = line.split()
        assert len(line) == 2
        hijri = line[0]
        starred = hijri.startswith('*')
        if starred:
          hijri = hijri[1:]
        hyear, hmonth = hijri.split('/')
        hyear = int(hyear)
        hmonth = int(hmonth)
        assert GREG_RE.match(line[1])
        gregorian = datetime.date.fromisoformat(line[1])
        add_to_database(hyear, hmonth, starred, gregorian, name)


def read_tsybulsky():
  with open(TSYBULSKY, "rt") as tsybulsky_file:
    date = TSYBULSKY_START
    for line in tsybulsky_file:
      if '#' in line:
        line = line[:line.index('#')]
      line = line.strip()
      if not line:
        continue
      line = line.split()
      hyear = int(line[0])
      months = [int(l) for l in line[1:13]]
      if len(line) >= 14:
        assert len(line) == 14
        year_length = int(line[13])
      else:
        year_length = None
      for month in range(1, min(len(months), 12) + 1):
        add_to_database(hyear, month, False, date, TSYBULSKY_LABEL)
        month_length = months[month-1]
        date = date + datetime.timedelta(days=month_length)

      
read_sources()
read_tsybulsky()
check_sanity()
dump_database()
