import re

with open("data_sets/CACM/query.text", "r") as f:
    reg = r"\.I [0-9]+"
    reg2 = r"\.W"
    line = f.readline()
    prevLine =""
    counter = ""
    doc = ""
    while line:
        isEndQuery = re.search(reg, line)
        isStartQuery = re.search(reg2, line)
        if(isEndQuery and doc.__len__() > 0):
            with open("CACM_Clean_Query/qer_"+str(counter)+".txt", 'x') as writer:
                writer.write(doc)
                writer.close()
                print("file:CACM_Clean_Query/qer_"+str(counter)+".txt created successefully")
                doc = ""
        if isEndQuery:
            counter = line.split()[1]
        if(not isEndQuery and not isStartQuery):
            doc += line 
        # prevLine = line
        line = f.readline()