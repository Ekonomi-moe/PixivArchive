# -*- coding: utf-8 -*-

class dummy():
    def __init__(self) -> None:
        pass

class storage():
    def __init__(self):
        self.debug = False
        self.exit = False

        import importlib
        self.modules = dummy()

        self.modules.Thread = importlib.import_module('threading').Thread
        self.modules.os = importlib.import_module('os')
        self.modules.time = importlib.import_module('time')
        self.modules.requests = importlib.import_module('requests')
        self.modules.json = importlib.import_module('json')
        self.modules.pixiv = importlib.import_module('pixiv').Pixiv(self)
        self.Path = importlib.import_module('pathlib').Path
        self.thr = {}
        self.downdata = {}
        self.logpath = "./log"
        self.workpath = "./download/"


        self.jsoncount = 0
        self.jsonlines = 0
        self.jsonfile = None
        self.thread = 100

        self.start = 1
        self.last = 100188567
        self.devide = 200000
        self.insert = ""

        self.logpath = self.Path(self.logpath) / "pixiv.log"
        self.logpath.touch()
        self.logpath = open(self.logpath, "a", encoding="utf-8")
        self.workpath = self.Path(self.workpath)
        self.workpath.mkdir(exist_ok=True)

        self.modules.os.chdir(self.workpath)

        self.check_last_save()

    def logger_debug(self, data):
        if self.debug:
            print(self.modules.time.strftime("%Y-%m-%d %H:%M:%S ")+data)
            self.logpath.write(self.modules.time.strftime("%Y-%m-%d %H:%M:%S ")+data+"\n")
    
    def logger(self, data):
        print(self.modules.time.strftime("%Y-%m-%d %H:%M:%S ")+data)
        self.logpath.write(self.modules.time.strftime("%Y-%m-%d %H:%M:%S ")+data+"\n")
        pass

    def check_last_save(self):
        files = self.modules.os.listdir(".")
        files = [i for i in files if self.Path(i).is_file()]
        files = [i for i in files if i.startswith("metadata")]
        files = [i for i in files if i.endswith(".json")]
        if len(files) > 0:
            files.sort()
            print(files)
            fl = files[-1].replace("metadata", "").replace(".json", "")
            self.jsoncount = int(fl)
            file = open("metadata{num}.json".format(num=fl), "r", encoding="utf-8")
            line = file.readlines()
            
            try:
                self.start = int(self.modules.json.loads(line[-1])["illustId"])+1
            except IndexError:
                pass
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
    
    def json_bulk(self):
        try:
            tmp = self.jsonfile
            if self.jsonlines == self.devide:
                if self.insert != "":
                    self.jsonfile.write(self.insert)
                    self.insert = ""
                self.jsonlines = 0
                self.jsonfile.close()

                self.jsoncount += 1
                self.jsonfile = open("metadata{num}.json".format(num=str(self.jsoncount).zfill(8)), "a", encoding="utf-8")
        except:
            self.jsoncount = 0
            self.jsonlines = 0
            self.jsonfile = open("metadata{num}.json".format(num=str(self.jsoncount).zfill(8)), "a", encoding="utf-8")

    def json_close(self):
        try:
            tmp = self.jsonfile
            if self.insert != "":
                self.jsonfile.write(self.insert)
            self.jsonfile.close()
        except:
            pass

    def json_insert(self, lst):
        for i in lst:
            self.json_bulk()
            self.insert += self.modules.json.dumps(self.downdata[i], ensure_ascii=False)+"\n"
            self.logger("INFO:STORE: {id} OK".format(id=i))
            self.jsonlines += 1
        self.jsonfile.write(self.insert)
        self.insert = ""
        pass

    def big_thread(self, illustId):
        rtn = self.modules.pixiv.get_illust_data(illustId)
        self.downdata.update({illustId: rtn["data"]})
        self.thr.pop(illustId)

    def download_illust_meta(self):
        start = self.start
        smd = []
        for i in range(self.start, self.last):
            if self.exit: return
            if i % 100 == 0:
                self.logger("INFO:MAIN: Loading {start} - {end}".format(start=start, end=i+1))
                smd = self.modules.pixiv.get_small_illust_data(start, i+1)
                if smd["status"] != 200:
                    self.logger("WARNING:MAIN: RELoading {start} - {end}".format(start=start, end=i+1))
                    smd = self.modules.pixiv.get_small_illust_data(start, i+1)
                    if smd["status"] != 200:
                        self.logger("Error: {status} Error while download range {start}-{end}".format(status=smd["status"], start=start, end=i+1))
                        start = i+1
                        continue
                if smd["data"] == []:
                    start = i + 1
                    continue

                smd = list(smd["data"].keys())
                
                if smd == []:
                    start = i + 1
                    continue
                
                for illustId in smd:
                    while True:
                        if len(self.thr) < self.thread:
                            t = self.modules.Thread(target=self.big_thread, args=(illustId,))
                            t.daemon = True
                            t.start()
                            self.thr.update({illustId:t})
                            break
                        else:
                            self.modules.time.sleep(0.1)
                
                while True:
                    if len(self.thr) == 0: break
                    self.modules.time.sleep(0.3)
                
                self.json_insert(smd)
                
                start = i+1



if __name__ == "__main__":
    storage = storage()
    storage.download_illust_meta()
    storage.json_close()

