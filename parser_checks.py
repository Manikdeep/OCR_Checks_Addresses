import os
import zipcodes
import re
import json
import base_parser
import sys
import csv

class Check:

    def __init__(self):
        self.date = None
        self.bankname = []
        self.photo_id = None
        self.victim = None
        self.amount = []
        self.zipcode = []
        self.state = []

    def get_date_and_id_from_title(self, title):
        re1 = title.split("@")
        photo_id = re1[0].split("_")[1]
        date = re1[1].split("_")[0]
        return photo_id, date

    def check_zipcode(self,content):
        # return all the information related to zipcode too
        # libpostal to get address
        # find zipcode 5-digit and extract other into
        # get the city info
        result = set()
        for i in re.finditer(r'(?!\A)\b\d{5}(?:-\d{4})?\b', content):
            if zipcodes.is_real(i.group()):
                state  = zipcodes.matching(i.group())[0]['state']
                if state in content:
                    result.add((i.group(),state))
        return result

    def check_bankname(self, content):
        # return bank name if finds a match from the given names
        # print(Banks)
        bank_list = ["bank of america", "suntrust", "j.p.morgan", "bankozk", "hhsb", "first convenience bank", 
        "chase", "regions", "navy fed", "citibank", "usb financial services", "us bank", "pnc bank", "capital one", 
        "td bank", "wells fargo", "Citizen Bank", "fifth third bank", "first fidelity bank", "commerce bank", "us bank", 
        "first citizens bank", "capital one", "first republic bank", "u.s. century bank","active duty", "american express",
        "aspirations bank", "b&t Bank", "banco felabella", "bb&t", "barrera farms", "bmo harris bank", "burning bank",
        "chime", "choice financial group", "citi", "commerce", "cryptocurrency", "discover", "DUPACO community credit union",
        "fair financial", "Go2Bank", "green dot bank", "hancock whitney", "huntington", "IPC bank", "Indi",
        "Kabbage", "key bank", "M&T bank", "Marcus", "Navy Fedral credit union", "New York Community Bank",
        "RCB bank", "Reve", "RF bank finance", "Robin Financial", "T Mobile Money", "usaa", "varo bank", "WAFD",
        "woodforest", "5 star bank", "allegiance bank", "ally bank", "alpine bank", "amerant bank", "ann arbour",
        "ArrowPointe", "ArrowPointe federal credit union", "bancorp south", "atlantic union bank", "bank of madison",
        "bank of texas", "bank of the james", "bank of tokyo", "bank united", "bank york", "bbva", "bragg mutual",
        "c&F bank", "carotrans", "cashier's check", "cathay bank", "CBC bank", "centerstate", "charlotte metro",
        "cnb","comerica", "community bank","community credit union","county educators","county national bank",
        "crown bank", "customers bank", "Dexterous mold and tool","eagle bank", "east west bank",
        "edfed", "erie insurance group","evolution risk advisors","executive banking","federal","federal credit union",
        "federal incentive check","federal tax return","fidelity bank","financial credit union","first national bank",
        "first south bank","first state bank","floridian community bank","founders","freedom bank","frost",
        "gamebreaker","german american bank","grove bank and trust", "guilford savings bank","harford bank",
        "havensavings bank","hudson valley credit union","huntington","IBM southeast employees","ibmsecu",
        "invesco","investors bank","jeff bank","key bank","key bank national association","lncb national bank",
        "lgfcu","lindell bank","marine","merril","merrimac valley credit union","metabank","midflorida",
        "morgan stanley","motion federal credit union","NC dept of revenue","ncua","new brunswick credit union",
        "northeast family", "northern trust","northview bank","nycb","ocean bank","pacific premier bank",
        "pacific western bank","patriot bank","peoples bank","peoples bank and trust","people's united bank",
        "planters bank","popa federal credit union","popular bank","prosperity bank","professional bank",
        "roselle bank","ruth smith","santandar bank","seacoast bank","select bank and trust", "signature bank",
        "simmons bank","south atlantic bank","south state bank","sovereign bank","space coast credit union",
        "spencer savings bank","state employees credit union","state of florida","stifel bank","sun east",
        "sunshine bank","sunstate bank","td bank","texena bank","the bank of new york mellon","the family bank",
        "the merchants national bank","towne bank","treasury of illinois","tri counties bank","u.s capital advisors",
        "u.s central bank","u.s century bank","ubs","umb bank","union county savings bank","united southern bank",
        "united states treasury","valley bank","vanguard municipal money market fund","valley neational bank",
        "voya institutional trust", "walmart moneycard","webster bank", "chime"]
        re = set()
        
        ##### check bank name in text #####
        content_lower = content.lower()
        # print()
        for i in bank_list:
            if i in content_lower:
                re.add(i)
        return re

    def check_amount(self, content):
        # return the amounts present in the content
        result = set() 
        # find with digit and decimal
        for i in re.finditer(r"\d{1,3}(?:,\d{3})*(?:\.\d+)+", content):
            # print(i)
            result.add(i.group())
        #find with S digit and deciaml
        # for i in re.finditer(r"(\b[S][0-9]*\.[0-9]*)|\b[S][0-9]+", content):
        #     print(i.group())
        #     result.add(i.group()[1:])
        for i in re.finditer(r"\b[S]\d{1,3}(?:,\d{3})*(?:\.\d+)+|\b[S]\d{1,3}(?:,\d{3})*", content):
            # print(i.group())
            result.add(i.group()[1:])
        # find with $ digit and decimal
        # for i in re.finditer(r"\$\d+(?:\.\d+)?", content):
        #     print(i.group())
        #     result.add(i.group()[1:])
        for i in re.finditer(r"\$\d{1,3}(?:,\d{3})*(?:\.\d+)+|\$\d{1,3}(?:,\d{3})*", content):
            # print(i.group())
            result.add(i.group()[1:])
        # print(result)
        return result

    def data_assign_rowby(self, photo_id, date, bank, zipcodes, states, amount, writer):
        num_banks = len(bank)
        num_zip = len(zipcodes)
        num_amount = len(amount)
        # amount = [float(i) for i in amount]
        amount.sort()

        if num_banks == 0 and num_amount == 0 and num_zip == 0:
            writer.writerow([photo_id, date, "", "", "", ""])

        if len(bank) == 1:
            for i in range(0,max(num_banks,num_zip,num_amount)):
                bank_name = bank[0]
                if num_zip > 0:
                    zipcode = zipcodes.pop(0)
                    state = states.pop(0)
                    num_zip -= 1
                else:
                    zipcode = ""
                    state = ""
                if num_amount > 0:
                    amt = amount.pop()
                    num_amount -= 1
                else:
                    amt = ""
                writer.writerow([photo_id, date, bank_name, zipcode, state, amt])
        else:
            for i in range(0,max(num_banks,num_zip,num_amount)):
                if num_banks > 0:
                    bank_name = bank.pop(0)
                    num_banks -= 1
                else:
                    bank_name = ""
                if num_zip > 0:
                    zipcode = zipcodes.pop(0)
                    state = states.pop(0)
                    num_zip -= 1
                else:
                    zipcode = ""
                    state = ""
                if num_amount > 0:
                    amt = amount.pop()
                    num_amount -= 1
                else:
                    amt = ""
                writer.writerow([photo_id, date, bank_name, zipcode, state, amt])

if __name__ == '__main__':
    folder_textdoc_path = sys.argv[1]
    textdoc_paths = base_parser.get_textdoc_paths(folder_textdoc_path)
    headerList = ['Pic ID', 'Date', 'Bank Name', 'Zipcode', 'State', 'Amount']
    with open('checks_october_data_revised'+'.csv','w', newline='', encoding='utf-8') as f1:
        dw = csv.DictWriter(f1, delimiter=',', fieldnames=headerList)
        dw.writeheader()
        writer=csv.writer(f1, delimiter=',')#lineterminator='\n',
    # for i in np.arange(0,9):
    #     row = data[i]
    #     writer.writerow(row)
  
        for text_doc in textdoc_paths:
            writer=csv.writer(f1, delimiter=',')
            check = Check()
            file_name = os.path.basename(text_doc)

            #### parse photo id and date
            photo_id, date = check.get_date_and_id_from_title(file_name)
            if photo_id:
                check.photo_id = photo_id
            if date:
                check.date = date

            ### parse zipcode and state
            with open(text_doc, encoding = "utf-8") as f:
                content = f.readlines()
            if content:
                text_des = content[-1]
            else:
                writer.writerow([check.photo_id, check.date, "", "", "", ""])
                continue
            print((text_des).encode('utf-8'))

            if content:
                info_zipcode = check.check_zipcode(text_des)
                check.zipcode.extend([i[0] for i in info_zipcode])
                check.state.extend([i[1] for i in info_zipcode])
                for i in check.zipcode:
                    print("zip", i)
                for i in check.state:
                    print("state", i)
 
            #### parse bankname
                info_bank = check.check_bankname(text_des)
                check.bankname.extend([i for i in info_bank])
                for i in check.bankname:
                    print("bank:",i)
                info_amount = check.check_amount(text_des)
                check.amount.extend(i for i in info_amount)

            # for i,code in enumerate(check.zipcode):
            #     writer.writerow()

            #print(check.photo_id, check.date, check.bankname, check.zipcode, check.state, check.amount)
            # writer.writerow([check.photo_id, check.date, check.bankname, check.zipcode, check.state, check.amount])
            check.data_assign_rowby(check.photo_id, check.date, check.bankname, check.zipcode, check.state, check.amount, writer)

        # exit()
        