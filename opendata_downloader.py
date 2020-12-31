#!/usr/bin/env python
# coding: utf-8

import csv
import io
import os
import re
import sqlite3
from pathlib import Path

import py7zr
import requests


def _get_col_datatypes(fin, nullvalue, ignore_empty_cols):
    dr = csv.DictReader(fin, delimiter=';')
    field_types = {}
    for entry in dr:
        fields_left = [f for f in dr.fieldnames if f not in field_types.keys()]
        if not fields_left:
            break
        for field in fields_left:
            data = entry[field]
            if len(data) == 0 or data == nullvalue:
                continue
            if data.isdigit():
                field_types[field] = "INTEGER"
            elif re.match(r'^\d+[\.,]\d*$', data):  # using comma as a float separator is a weird shit
                field_types[field] = "REAL"         # but unfortunately is common in post-soviet countries 
            else:
                field_types[field] = "TEXT"

    if len(fields_left) > 0:
        if ignore_empty_cols:
            for field in fields_left:
                field_types[field] = "TEXT"
        else:
            raise Exception("Failed to find all the columns data types - Maybe some are empty?")

    return field_types


def csv_to_SQLite(database, table_name, csv_file, encoding, nullvalue="null", header=0, ignore_empty_cols=False):
    # TODO check variables types before executing
    with open(csv_file, mode='r', encoding=encoding) as fin:
        dt = _get_col_datatypes(fin, nullvalue, ignore_empty_cols)

        fin.seek(0)
        reader = csv.DictReader(fin, delimiter=';')

        # Keep the order of the columns name just as in the CSV
        fields = reader.fieldnames
        cols = []
        for f in fields:
            cols.append("%s %s" % (f, dt[f]))

        create_statement = "CREATE TABLE %s (%s)" % (table_name, ",".join(cols))
        con = sqlite3.connect(database)
        cur = con.cursor()
        cur.execute(create_statement)

        fin.seek(0)
        reader = csv.reader(fin, delimiter=';')
        for _ in range(header):
            next(reader)

        insert_statement = "INSERT INTO %s VALUES(%s);" % (table_name, ','.join('?' * len(cols)))
        for row in reader:
            if len(row) == 0:
                continue
            row = [x.replace(',','.') if re.match(r'^\d+,\d*$', x)
                   else x if x != 'null'
                   else None
                   for x in row
                   ] # slow because of this. Any other options to replace "null" with actual None?
            
            cur.execute(insert_statement, row)
        con.commit()

    return con


def download_data():
    Path("data").mkdir(parents=True, exist_ok=True)
    filter_pattern = re.compile(r'.*\.csv$')  # .csv files can have a different names
    for year in range(2016, 2021):
        r = requests.get("https://zno.testportal.com.ua/yearstat/uploads/OpenDataZNO{}.7z".format(year))
        with r, py7zr.SevenZipFile(io.BytesIO(r.content)) as archive:
            allfiles = archive.getnames()
            target = [f for f in allfiles if filter_pattern.match(f)][0]
            archive.extract(r'data', target)
            os.rename(r'data/{}'.format(target), r'data/{}.csv'.format(year))


def create_database():
    for year in range(2016, 2021):
        enc = 'cp1251'  # they cannot choose the encoding they like to use
        if year in (2017, 2018):
            enc = 'UTF-8'

        csv_to_SQLite("data/opendata.sqlite3", "data{}".format(year),
                      r"data/{}.csv".format(year),
                      encoding=enc, nullvalue="null",
                      header=1, ignore_empty_cols=True
                      )
        os.remove(r"data/{}.csv".format(year))
        print("%d is finished" % year)


if __name__ == '__main__':
    download_data()
    create_database()
