#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import of software.o.o downloads log in PIWIK

import argparse
import cPickle
import datetime
import md5
import os.path
import re

import bsddb3

import dblist


# Used to filter only the lines that actually reference a download
RE_ISO = re.compile(r'/distribution/[^/]*/iso/[^ "]')


def week_dbname(date_):
    """Name the weekly db. Return YYYYWW string."""

    # Group the date at the end of the week, so some dates can appears
    # in a different year. For example, 32/12/2012 will appear as a
    # 201301, the first week of 2013.

    delta = datetime.timedelta(days=6-date_.weekday())
    week_date = date_ + delta
    return '%04d%02d'%(week_date.year, week_date.isocalendar()[2])


def month_dbname(date_):
    """Name of the monthly db. Return YYYYMM string."""
    return '%04d%02d'%(date_.year, date_.month)


def count_analysis(key, dics):
    """Perform count analysis"""
    for d in dics:
        c = d.get(key, 0)
        d[key] = c + 1


def set_analysis(key, item, dics):
    """Perform set analysis."""
    for d in dics:
        items = d.get(key, set())
        if item not in items:
            items.add(item)
            d[key] = items


class PDict(dict):
    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(PDict, self).__init__(*args, **kwargs)
        try:
            _dict = cPickle.load(open(path, 'rb'))
        except:
            _dict = {}
        self.update(_dict)

    def save(self):
        cPickle.dump(self, open(self.path, 'wb'), cPickle.HIGHEST_PROTOCOL)


def analyze(dbenv, dbname, day):
    """Read every line and analize the data (D/W/M)."""

    # Create / open the accumulators. Use picke objects for performance
    results = os.path.join(dbenv, 'results')
    # download_dicts = [PDict(os.path.join(results, '%s_download_%s.pkl'%(dbname, period)))
    #                   for period in ('day',)] # 'week', 'month')]

    download_ip_dicts = [PDict(os.path.join(results, '%s_download_ip_%s.pkl'%(dbname, period)))
                         for period in ('day',)] # 'week', 'month')]

    # uuid_dicts = [PDict(os.path.join(results, '%s_uuid_%s.pkl'%(dbname, period)))
    #               for period in ('day',)] # 'week', 'month')]

    # ip_dicts = [PDict(os.path.join(results, '%s_ip_%s.pkl'%(dbname, period)))
    #             for period in ('day',)] # 'week', 'month')]

    # medium_dicts = [PDict(os.path.join(results, '%s_medium_%s.pkl'%(dbname, period)))
    #                 for period in ('day',)] # 'week', 'month')]

    # arch_dicts = [PDict(os.path.join(results, '%s_arch_%s.pkl'%(dbname, period)))
    #               for period in ('day',)] # 'week', 'month')]

    # Open lines databases
    lines = dblist.open(None, os.path.join(dbenv, dbname), flags=bsddb3.db.DB_RDONLY)
    lines_path = dblist.open(None, os.path.join(dbenv, dbname+'_paths'), flags=bsddb3.db.DB_RDONLY)
    # lines_uuid = dblist.open(None, os.path.join(dbenv, dbname+'_uuids'), flags=bsddb3.db.DB_RDONLY)

    # Read the bots file
    bots = set(l.strip() for l in open('bots.txt'))

    # Recover the path information
    paths = { md5.new(path).digest(): path for path in lines_path }

    for line in lines:
        # A line is a tuple with this schema:
        #   ip, hour, minute, second, md5_path, status, size,
        #   referrer, user_agent, md5_uuid, medium, version, arch
        (ip, _, _, _, md5_path, status, _, _, user_agent, md5_uuid, medium, version, arch) = line

        if user_agent in bots:
            continue

        path = paths[md5_path]
        if RE_ISO.match(path) and status != 404:
            # count_analysis(path, download_dicts)
            set_analysis(path, ip, download_ip_dicts)
        # if medium:
        #     count_analysis(medium, medium_dicts)
        # if arch:
        #     count_analysis(arch, arch_dicts)
        # if version:
        #     set_analysis(version, md5_uuid, uuid_dicts)
        #     set_analysis(version, ip, ip_dicts)


    for dicts in (download_ip_dicts,): #(download_dicts, download_ip_dicts, uuid_dicts, ip_dicts, medium_dicts, arch_dicts):
        for d in dicts:
            d.save()

    lines.close()
    lines_path.close()
    # lines_uuid.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze a single bdb log file into bdb')
    parser.add_argument('--dbenv', default='dbenv', help='Database environment')
    parser.add_argument('--db', help='Name of the database to read the information')

    args = parser.parse_args()

    # dbenv = bsddb3.db.DBEnv()
    # dbenv.open(args.dbenv,
    #            bsddb3.db.DB_INIT_MPOOL
    #            |bsddb3.db.DB_CREATE)

    year, month, day = (int(x) for x in (args.db[:4], args.db[4:6], args.db[6:]))
    day = datetime.datetime(year=year, month=month, day=day)

    analyze(args.dbenv, args.db, day)

    # dbenv.close()
