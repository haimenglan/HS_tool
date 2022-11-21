import csv
import random

rows = [
    ['','','','','','','','','','','','','Parametric'],
    ['Site', 'Product','SerialNumber','Special Build Name',
    'Special Build Description','Unit Number','Station ID',
    'Test Pass/Fail Status','StartTime','EndTime','Version','List of Failing Tests','AC_CP'],
    ['Display Name ----->','','','','','','','','','','','','na'],
    ['PDCA Priority ----->','','','','','','','','','','','','na'],
    ['Upper Limit ----->','','','','','','','','','','','','39'],
    ['Lower Limit ----->','','','','','','','','','','','','8'],
    ['Measurement Unit ----->','','','','','','','','','','','','pF'],
    ['ITJS','LB1','SN1','CFG1','CHILD_cfg1','num1','STATION1','PASS','2022/08/26 09:00',
    '2022/08/26 09:10','VERSION1','cap failed limit','20'],   
]

for i in range(100):
    sn='SN'+str(random.randint(0,5))
    station='STATION'+str(random.randint(0,2))
    version='VERSION'+str(random.randint(0,1))
    cap=str(random.randint(8,39))
    data = rows[-1][:]
    data[2]=sn
    data[6]=station
    data[10]=version
    data[12]=cap
    rows.append(data)
#print(rows)
    
with open('/storage/0123-4567/qpython/insight.csv', 'w') as f:
    csvobj = csv.writer(f)
    for row in rows:
        csvobj.writerow(row)

with open('/storage/0123-4567/qpython/insight.csv', 'r') as f:
    csvobj = csv.reader(f)
    for row in csvobj:
        print(row)




