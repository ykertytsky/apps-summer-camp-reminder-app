list_dict=[]
with open( "quotes.txt", "r", encoding="utf-8") as file:
    content = file.readlines()
    for line in content:
        tmp = {}
        line = line.strip().split("~")[0:-1]
        line[0]=line[0].strip()
        quote= line[0]
        author= line[1]
        print(line)
        tmp["quote"]= quote
        tmp["author"]= author

        # tmp =dict.fromkeys(quote, author)
        list_dict.append(tmp)
    print(list_dict)
