# -*- coding: utf-8 -*-

#https://www.pixiv.net/ajax/novel/{}?lang=en

class dummy():
    def __init__(self) -> None:
        pass

class Pixiv_old():
    def __init__(self):
        self.debug = True
        self.thread = True



        self.start = 1
        self.last = 100188567
        self.devide = 200000




        self.data = {}
        self.ids = []

        self.url = "https://www.pixiv.net/ajax/illust/{}?lang=en"
        self.ugoira_url = "https://www.pixiv.net/ajax/illust/{}/ugoira_meta?lang=en"


        self.modules = dummy()
        import time
        import requests
        import json
        import os
        import sqlite3
        import pathlib
        self.modules.time = time
        self.modules.requests = requests
        self.modules.json = json
        self.modules.os = os
        self.modules.sqlite3 = sqlite3
        self.modules.pathlib = pathlib
        
        #if self.thread:
        import threading
        self.modules.threading = threading
        
        files = self.modules.os.listdir(".")
        files = [i for i in files if self.modules.pathlib.Path(i).is_file()]
        files = [i for i in files if i.startswith("metadata")]
        files = [i for i in files if i.endswith(".json")]
        if len(files) > 0:
            print(files)
            files.sort()
            fl = files[-1].replace("metadata", "").replace(".json", "")
            self.jsoncount = int(fl)
            file = open("metadata{num}.json".format(num=fl), "r", encoding="utf-8")
            line = file.readlines()
            
            self.start = int(self.modules.json.loads(line[-1])["illustId"])+1
            self.jsonlines = len(line)
            file.close()

            self.jsonfile = open("metadata{num}.json".format(num=fl), "a", encoding="utf-8")
            del(files)
            del(fl)
            del(line)
            del(file)
        else:
            self.jsoncount = 0
            self.jsonlines = 0
            self.jsonfile = open("metadata{num}.json".format(num=str(self.jsoncount).zfill(8)), "a", encoding="utf-8")
        pass

    def logger(self, data):
        if self.debug:
            print(self.modules.time.strftime("%Y-%m-%d %H:%M:%S ")+data)

    def json_bulk(self):
        try:
            tmp = self.jsonfile
            if self.jsonlines == self.devide:
                self.jsonlines = 0
                self.jsonfile.close()

                self.jsoncount += 1
                self.jsonfile = open("metadata{num}.json".format(num=str(self.jsoncount).zfill(8)), "a", encoding="utf-8")
        except:
            self.jsoncount = 0
            self.jsonlines = 0
            self.jsonfile = open("metadata{num}.json".format(num=str(self.jsoncount).zfill(8)), "a", encoding="utf-8")

    def json_insert(self, data):
        self.json_bulk()
        self.jsonfile.write(self.modules.json.dumps(data, ensure_ascii=False)+"\n")
        self.jsonlines += 1        
        pass

    def insert_data(self, data: list):
        self.database.executemany("INSERT INTO images VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
        self.logger("INFO : {} images inserted".format(len(data)))
        pass

    def control(self):
        self.logger("INFO : Program Started")
        try:
            self.check_big_meta()
        except KeyboardInterrupt as e:
            self.logger("INFO : Program Stopped")
            self.logger("INFO : {e}".format(e=e))
            self.jsonfile.close()
            exit()

    def get_small_data(self, rang = None):
        if rang is None:
            rang = (self.start, self.last)
        self.logger("INFO : Loading Exist data. {rang}".format(rang=rang))
        url = "https://www.pixiv.net/ajax/user/0/illusts?"
        for i in range(rang[0], rang[1]):
            url+= "ids[]=" + str(i) + "&"
        url += "lang=en"

        data = self.modules.requests.get(url)

        if data.json()["error"]:
            self.logger("ERROR : {error}, While small data download on {rang}".format(error=data.json()["error"], rang=rang))
            exit()
        try:
            rtn = list(data.json()["body"].keys())
        except:
            rtn = []

        return rtn

    def get_big_data(self):
        url = "https://www.pixiv.net/ajax/illust/{}?lang=en"
        ugoira_url = "https://www.pixiv.net/ajax/illust/{}/ugoira_meta?lang=en"
        for i in range(self.start, self.last):
            while True:
                data = self.modules.requests.get(url.format(i))
                if data.status_code == 200:
                    if data.json()["error"]:
                        self.logger("ERROR: {id}: {message}".format(id=i, message=data.json()["message"]))
                        break
                    # Convert data.text as utf-8
                    p = data.json()["body"]
                    del(p["zoneConfig"])
                    del(p["noLoginData"])
                    del(p["userIllusts"])
                    del(p["comicPromotion"])
                    del(p["fanboxPromotion"])
                    del(p["descriptionYoutubeId"])
                    del(p["descriptionBoothId"])
                    
                    if p["illustType"] == 2:
                        while True:
                            ugoira_meta = self.modules.requests.get(ugoira_url.format(i))
                            if ugoira_meta.status_code == 200:
                                if ugoira_meta.json()["error"]:
                                    self.logger("ERROR: {id}: {message}".format(id=i, message=ugoira_meta.json()["message"]))
                                    break
                                
                                p.update({"ugoira_meta": ugoira_meta.json()["body"]}) # UPDATE META UGOIRA

                                break
                            elif ugoira_meta.status_code == 429:
                                self.logger("ERROR: {id}: Too many requests. Sleeping 1 min".format(id=i))
                                self.modules.time.sleep(60)
                            # ========================================== ERROR HANDLING ==========================================
                            else:
                                try:
                                    if ugoira_meta.json()["error"]:
                                        self.logger("ERROR: {id}: {status_code} {message}".format(id=i, status_code=ugoira_meta.status_code, message=ugoira_meta.json()["message"]))
                                        break
                                    else:
                                        self.logger("ERROR: {id}: {status_code}".format(id=i, status_code=ugoira_meta.status_code))
                                except:
                                    self.logger("ERROR: {id}: {status_code}".format(id=i, status_code=ugoira_meta.status_code))
                                break
                            # =====================================================================================================
                    self.json_insert(p)
                    del(p)

                    self.logger("INFO : {id}: {status_code}".format(id=i, status_code=data.status_code))
                    
                    #self.data.update({str(i): data})
                    break
                elif data.status_code == 429:
                    self.logger("WARNING: {id}: Too many requests. Sleeping 1 min".format(id=i))
                    self.modules.time.sleep(60)
                # ========================================== ERROR HANDLING ==========================================
                else:
                    try:
                        if data.json()["error"]:
                            self.logger("ERROR: {id}: {status_code} {message}".format(id=i, status_code=data.status_code, message=data.json()["message"]))
                            break
                        else:
                            self.logger("ERROR: {id}: {status_code}".format(id=i, status_code=data.status_code))
                    except:
                        self.logger("ERROR: {id}: {status_code}".format(id=i, status_code=data.status_code))
                    break
                # =====================================================================================================
        pass

    def check_big_meta(self):
        start = self.start
        last = self.start

        for i in range(self.start, self.last):
            if i % 100 == 0:
                smd = self.get_small_data((start, i+1))
                if smd == []:
                    start = i + 1
                    continue
                for il in smd:
                    self.down_big_meta(il)
                start = i+1
        pass

    def down_big_meta(self, i):
        while True:
            data = self.modules.requests.get(self.url.format(i))
            if data.status_code == 200:
                if data.json()["error"]:
                    self.logger("ERROR: {id}: {message}".format(id=i, message=data.json()["message"]))
                    break
                # Convert data.text as utf-8
                p = data.json()["body"]
                del(p["zoneConfig"])
                del(p["noLoginData"])
                del(p["userIllusts"])
                del(p["comicPromotion"])
                del(p["fanboxPromotion"])
                del(p["descriptionYoutubeId"])
                del(p["descriptionBoothId"])
                
                if p["illustType"] == 2:
                    while True:
                        ugoira_meta = self.modules.requests.get(self.ugoira_url.format(i))
                        if ugoira_meta.status_code == 200:
                            if ugoira_meta.json()["error"]:
                                self.logger("ERROR: {id}: {message}".format(id=i, message=ugoira_meta.json()["message"]))
                                break
                            
                            p.update({"ugoira_meta": ugoira_meta.json()["body"]}) # UPDATE META UGOIRA

                            break
                        elif ugoira_meta.status_code == 429:
                            self.logger("ERROR: {id}: Too many requests. Sleeping 1 min".format(id=i))
                            self.modules.time.sleep(60)
                        # ========================================== ERROR HANDLING ==========================================
                        else:
                            try:
                                if ugoira_meta.json()["error"]:
                                    self.logger("ERROR: {id}: {status_code} {message}".format(id=i, status_code=ugoira_meta.status_code, message=ugoira_meta.json()["message"]))
                                    break
                                else:
                                    self.logger("ERROR: {id}: {status_code}".format(id=i, status_code=ugoira_meta.status_code))
                            except:
                                self.logger("ERROR: {id}: {status_code}".format(id=i, status_code=ugoira_meta.status_code))
                            break
                        # =====================================================================================================
                self.json_insert(p)
                del(p)

                self.logger("INFO : {id}: {status_code}".format(id=i, status_code=data.status_code))
                
                #self.data.update({str(i): data})
                break
            elif data.status_code == 429:
                self.logger("WARNING: {id}: Too many requests. Sleeping 1 min".format(id=i))
                self.modules.time.sleep(60)
            # ========================================== ERROR HANDLING ==========================================
            else:
                try:
                    if data.json()["error"]:
                        self.logger("ERROR: {id}: {status_code} {message}".format(id=i, status_code=data.status_code, message=data.json()["message"]))
                        break
                    else:
                        self.logger("ERROR: {id}: {status_code}".format(id=i, status_code=data.status_code))
                except:
                    self.logger("ERROR: {id}: {status_code}".format(id=i, status_code=data.status_code))
                break
            # =====================================================================================================