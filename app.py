# -*- coding: utf-8 -*-

class dummy():
    def __init__(self) -> None:
        pass

class storage():
    def __init__(self):
        self.debug = False

        import importlib
        self.modules = dummy()

        self.modules.Thread = importlib.import_module('threading').Thread
        self.modules.os = importlib.import_module('os')
        self.modules.time = importlib.import_module('time')
        self.modules.requests = importlib.import_module('requests')
        self.modules.json = importlib.import_module('json')
        self.modules.pixiv = importlib.import_module('pixiv').Pixiv(self)
        self.Path = importlib.import_module('pathlib').Path
        self.queue = []


        self.jsoncount = 0
        self.jsonlines = 0
        self.jsonfile = None

        self.start = 1
        self.last = 100188567
        self.devide = 200000

        self.check_last_save()

    def logger(self, data):
        if self.debug:
            print(self.modules.time.strftime("%Y-%m-%d %H:%M:%S ")+data)
    
    def logger_info(self, data):
        print(self.modules.time.strftime("%Y-%m-%d %H:%M:%S ")+data)
        pass

    def check_last_save(self):
        files = self.modules.os.listdir(".")
        files = [i for i in files if self.modules.pathlib.Path(i).is_file()]
        files = [i for i in files if i.startswith("metadata")]
        files = [i for i in files if i.endswith(".json")]
        if len(files) > 0:
            files.sort()
            print(files)
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

    def json_insert(self, data):
        self.json_bulk()
        self.jsonfile.write(self.modules.json.dumps(data, ensure_ascii=False)+"\n")
        self.jsonlines += 1        
        pass

    def main(self):
        start = self.start
        smd = []
        for i in range(self.start, self.last):
            if i % 100 == 0:
                smd = self.get_small_illust_data((start, i+1))
                if smd == []:
                    start = i + 1
                    continue
                for il in smd:
                    self.down_big_meta(il)
                start = i+1
        pass



if __name__ == "__main__":
    from pixiv import Pixiv_old as Pixiv
    p = Pixiv()
    p.control()
    p.logger("INFO : Program Finished")
    pass