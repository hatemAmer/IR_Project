import re



with open("data_sets/CISI/CISI.ALL", "r") as f:
    reg = r"\.I [0-9]+"
    line = f.readline()
    counter =0
    doc = ""
    while line:
        isNewDoc = re.search(reg, line)
        if(isNewDoc and doc.__len__() > 0):
            counter+=1
            with open("CISI_Clean/doc_"+str(counter)+".txt", 'x') as writer:
                writer.write(doc)
                writer.close()
                doc = ""
        doc += line 
        line = f.readline()