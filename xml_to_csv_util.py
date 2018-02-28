import pandas as pd
import xml, json, sys,os
import xml.etree.cElementTree as ET

all_attributes =['ROOTDOC','DBROW','STATE_ABBR','STATE_CODE','DIVISION','YEARMONTH','PCP','TAVG','PDSI','PHDI','ZNDX','PMDI','CDD','HDD','SP01','SP02','SP03','SP06','SP09','SP12','SP24','TMIN','TMAX']

def getvalueofnode(node):
    return node.text if node is not None else None

def convert_xml_to_json(xml_file_location, state_abbr):

    parsedXML = ET.parse(xml_file_location)
    df = pd.DataFrame(columns=all_attributes[2:])

    for node in parsedXML.getroot():
            state_code = node.find('STATE_CODE')
            division = node.find('DIVISION')
            yearmonth = node.find('YEARMONTH')
            pcp = node.find('PCP')
            tavg = node.find('TAVG')
            pdsi= node.find('PDSI')
            phdi = node.find('PHDI')
            zndx = node.find('ZNDX')
            pmdi= node.find('PMDI')
            cdd = node.find('CDD')
            hdd = node.find('HDD')
            sp01 = node.find('SP01')
            sp02 = node.find('SP02')
            sp03= node.find('SP03')
            sp06= node.find('SP06')
            sp09=node.find('SP09')
            sp12= node.find('SP12')
            sp24= node.find('SP24')
            tmin = node.find('TMIN')
            tmax= node.find('TMAX')

            df = df.append(
                pd.Series([state_abbr,getvalueofnode(state_code), getvalueofnode(division), getvalueofnode(yearmonth), getvalueofnode(pcp), getvalueofnode(tavg), getvalueofnode(pdsi),getvalueofnode(phdi), getvalueofnode(zndx),getvalueofnode(pmdi), getvalueofnode(cdd),getvalueofnode(hdd), getvalueofnode(sp01),getvalueofnode(sp02), getvalueofnode(sp03), getvalueofnode(sp06), getvalueofnode(sp09),getvalueofnode(sp12),getvalueofnode(sp24),getvalueofnode(tmin), getvalueofnode(tmax)], index=all_attributes[2:]),
                ignore_index=True)


    with open('climate_dataset.csv', 'a') as f:
        f.write(df.to_csv())

 
filepath = "C:/Users/Dell/PycharmProjects/Pandas/Data"
All_Files = os.listdir(filepath)
print(len(All_Files))
for i in All_Files:
    convert_xml_to_json(filepath+"/"+i,i.split(".xml")[0])
