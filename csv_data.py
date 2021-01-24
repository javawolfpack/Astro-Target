import sqlite3
import json
from dateutil.parser import parse
import datetime
import sys

## Taken from stack overflow: https://stackoverflow.com/questions/55898212/user-input-from-numbered-list-and-returns-the-list/55898695
def display(li):
    #Iterate through the list using enumerate and print
    for idx, tables in enumerate(li):
        print("%s. %s" % (idx+1, tables))


## Modifed from stack overflow: https://stackoverflow.com/questions/55898212/user-input-from-numbered-list-and-returns-the-list/55898695
def get_list(li):
    choose = int(input("\nSelect DSO Target:"))-1
    #If choose is not a valid index in list, print error and return empty string
    if choose < 0 or choose > (len(li)-1):
        print('Invalid DSO selected')
        quit()
        
    #Else return chosen string
    return li[choose]

conn = sqlite3.connect('astro.db')
# https://www.devdungeon.com/content/python-sqlite3-tutorial
# Load the contents of a database file on disk to a
# transient copy in memory without modifying the file
memory_db = sqlite3.connect(':memory:')
conn.backup(memory_db)
conn.close()
c = memory_db.cursor()
# c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='astro';")
jobs = c.fetchall()
if len(jobs) <= 0:
    print("DB not generated")
    quit()

print("Available DSO Targets")
c.execute("SELECT DISTINCT json_extract( data, '$.name' ) as NAME FROM astro WHERE type=?",("dso",))
q_names = c.fetchall()
names = []
for n in q_names:
    names+=[n[0]]
display(names)
dso = get_list(names)

print(f"Generating CSV of View Data for {dso} will take a few minutes")
# print(sys.argv[1])

c.execute("SELECT DISTINCT json_extract( data, '$.month' ) as MONTH, json_extract( data, '$.day' ) as DAY, json_extract( data, '$.year' ) as YEAR FROM astro WHERE type=?",("dso",))
dates = c.fetchall()
seeing_list = []
for date in dates:
    seeing = {
        "day":date[1],
        "month": date[0],
        "year": date[2],
    }
    c.execute("SELECT * FROM astro WHERE astro.type=? AND JSON_EXTRACT(astro.data, '$.day')=? AND JSON_EXTRACT(astro.data, '$.month')=? AND JSON_EXTRACT(astro.data, '$.year')=? AND JSON_EXTRACT(astro.data, '$.name')=?;",("dso",date[1],date[0],date[2], dso))
    query = c.fetchall()
    if len(query) <= 0:
        continue
    q=query[0]
    data = json.loads(q[2])
    if len(data["seen"])>0:
        # print(q)
        start=None
        end=None
        g_start = None
        g_end = None
        m_time_start = None
        m_time_end = None
        m_frac_max = 0
        sorted(data["seen"], key = lambda i: i['time'])
        for see in data["seen"]:
            if "sun" in see.keys():
                if start == None and see["sun"]=="night":
                    if g_start == None and see["alt"]>30:
                        g_start = parse(see["time"])
                    start = parse(see["time"])
                elif see["sun"]=="night":
                    if g_start == None and see["alt"]>30:
                        g_start = parse(see["time"])
                    elif see["alt"]>30:
                        g_end = parse(see["time"])
                    end = parse(see["time"])
                c.execute("SELECT * FROM astro WHERE astro.type=? AND JSON_EXTRACT(astro.data, '$.time')=?;",("moon",see["time"]))
                m_query = c.fetchall()
                # print(m_query)
                if len(m_query) > 0:
                    m_q = m_query[0]
                    m_data = json.loads(m_q[2])
                    if m_time_start == None and m_data["moonalt"] > 0:
                        m_time_start = parse(m_data["time"])
                        if m_frac_max == None:
                            m_frac_max = m_data["moonfrac"]
                        elif m_frac_max < m_data["moonfrac"]:
                            m_frac_max = m_data["moonfrac"]
                    elif m_data["moonalt"] > 0:
                        m_time_end = parse(m_data["time"])
                        if m_frac_max == None:
                            m_frac_max = m_data["moonfrac"]
                        elif m_frac_max < m_data["moonfrac"]:
                            m_frac_max = m_data["moonfrac"]
        if start != None and end != None:
            if g_start != None and g_end != None:
                seeing["g_time"] = g_end-g_start
            else:
                seeing["g_time"] = datetime.timedelta(0, 0, 0)
            seeing["v_time"] = end-start
        else:
            seeing["g_time"] = datetime.timedelta(0, 0, 0)
            seeing["v_time"] = datetime.timedelta(0, 0, 0)
        if m_time_start != None and m_time_end != None:
            seeing["m_time"] = m_time_end - m_time_start
            seeing["m_frac"] = m_frac_max
        else:
            seeing["m_time"] = datetime.timedelta(0, 0, 0)
            seeing["m_frac"] = m_frac_max
        seeing_list+=[seeing]

print(f"Writing View Data to {dso}.csv")
f = open(dso+".csv","w+")
f.write("{}/{}/{}, {}, {}, {}, {}\n".format(
            "month",
            "day",
            "year",
            "Time Visible",
            "Time Visible above 30 degrees",
            "Time Moon is above horizon",
            "Max Visible Moon Fraction"))
for seeing in seeing_list:
    if seeing["v_time"].total_seconds() > 0:
        f.write("{}/{}/{}, {}, {}, {}, {}\n".format(
            seeing["month"],
            seeing["day"],
            seeing["year"],
            seeing["v_time"],
            seeing["g_time"],
            seeing["m_time"],
            seeing["m_frac"]))
f.close()

