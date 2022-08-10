# -*- coding: utf-8 -*-

class dummy():
    def __init__(self) -> None:
        pass

class Pixiv():
    def __init__(self, storage = None):
        import importlib
        self.debug = False
        self.ajax_url = dummy()

        if storage is None:
            self.storage = None
            self.modules = dummy()
        else:
            self.storage = storage
            try:
                self.logger = self.storage.logger
            except:
                pass
            try:
                self.logger_debug = self.storage.logger_debug
            except:
                pass
            try:
                self.modules = self.storage.modules
            except:
                self.modules = dummy()


        
        self.modules.requests = importlib.import_module('requests')
        self.modules.time = importlib.import_module('time')


        self.ajax_url_setup()
        pass

    def logger_debug(self, data):
        if self.debug:
            print(self.modules.time.strftime("%Y-%m-%d %H:%M:%S ")+data)
    
    def logger(self, data):
        print(self.modules.time.strftime("%Y-%m-%d %H:%M:%S ")+data)
        pass

    def ajax_url_setup(self):
        self.ajax_url.illust = "https://www.pixiv.net/ajax/illust/{}?lang=en"
        self.ajax_url.uigora_url = "https://www.pixiv.net/ajax/illust/{}/ugoira_meta?lang=en"
        self.ajax_url.novel = "https://www.pixiv.net/ajax/novel/{}?lang=en"
        self.ajax_url.illust_small = "https://www.pixiv.net/ajax/user/0/illusts?lang=en"

    def get_small_illust_data(self, range_start, range_end):
        if range_end < range_start:
            self.logger("ERROR:IF: range_end cannot be less than range_start")
            return {"stauts": 400, "message": "range_end cannot be less than range_start", "data": {}}
        if range_end - range_start > 100:
            self.logger("ERROR:IF: range count cannot be greater than 100")
            return {"stauts": 400, "message": "range count cannot be greater than 100", "data": {}}
        
        url = self.ajax_url.illust_small
        for i in range(range_start, range_end): 
            url += "&ids[]=" + str(i)
        
        data = self.modules.requests.get(url)
        
        if data.json()["error"]:
            self.logger("ERROR:GET: {status_code} {message}".format(status_code=data.status_code, message=data.json()["message"]))
            return {"stauts": data.status_code, "message": data.json()["message"]}
        else:
            return {"status": 200, "data": data.json()["body"], "message": data.json()["message"]}

    def get_illust_data(self, illust_id):
        while True:
            data = self.modules.requests.get(self.ajax_url.illust.format(illust_id))
            if data.status_code == 200:
                if data.json()["error"]:
                    self.logger("ERROR:GET: {id}: {message}".format(id=illust_id, message=data.json()["message"]))
                    break
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
                        ugoira_meta = self.modules.requests.get(self.ajax_url.uigora_url.format(illust_id))
                        if ugoira_meta.status_code == 200:
                            if ugoira_meta.json()["error"]:
                                self.logger("ERROR:GET: {id}: {message}".format(id=illust_id, message=ugoira_meta.json()["message"]))
                                break
                            p.update({"ugoira_meta": ugoira_meta.json()["body"]}) # UPDATE META UGOIRA
                            break
                        elif ugoira_meta.status_code == 429:
                            self.logger("WARNING:GET: {id}: Too many requests. Sleeping 1 min".format(id=illust_id))
                            self.modules.time.sleep(60)
                        else: # on ERROR
                            try:
                                if ugoira_meta.json()["error"]:
                                    self.logger("ERROR:GET: Ugoira {id}: {status_code} {message}".format(id=illust_id, status_code=ugoira_meta.status_code, message=ugoira_meta.json()["message"]))
                                    break
                                else:
                                    self.logger("ERROR:GET: Ugoira {id}: {status_code}".format(id=illust_id, status_code=ugoira_meta.status_code))
                            except:
                                self.logger("ERROR:GET: Ugoira {id}: {status_code}".format(id=illust_id, status_code=ugoira_meta.status_code))
                            break # Error handling end
                self.logger_debug("DEBUG:GET: {id} - {status_code}".format(id=illust_id, status_code=data.status_code))
                break
            elif data.status_code == 429:
                self.logger("WARNING:GET: {id}: Too many requests. Sleeping 1 min".format(id=illust_id))
                self.modules.time.sleep(60)
            else: # on ERROR
                try:
                    if data.json()["error"]:
                        self.logger("ERROR:GET: {id}: {status_code} {message}".format(id=illust_id, status_code=data.status_code, message=data.json()["message"]))
                        return {"stauts": data.status_code, "message": data.json()["message"]}
                    else:
                        self.logger("ERROR:GET: {id}: {status_code}".format(id=illust_id, status_code=data.status_code))
                        return {"stauts": data.status_code, "message": "Unknown error"}
                except:
                    self.logger("ERROR:GET: {id}: {status_code}".format(id=illust_id, status_code=data.status_code))
                    return {"stauts": data.status_code, "message": "Unknown error"}
                # Error handling end
        return {"stauts": 200, "data": p}

    def get_novel_data(self, novel_id):
        while True:
            data = self.modules.requests.get(self.ajax_url.novel.format(novel_id))
            if data.status_code == 200:
                if data.json()["error"]:
                    self.logger("ERROR:GET: {id}: {message}".format(id=novel_id, message=data.json()["message"]))
                    break
                p = data.json()["body"]
                del(p["zoneConfig"])
                del(p["noLoginData"])
                del(p["userNovels"])
                self.logger("DEBUG:GET: {id} - {status_code}".format(id=novel_id, status_code=data.status_code))
                break
            elif data.status_code == 429:
                self.logger("WARNING: {id}: Too many requests. Sleeping 1 min".format(id=novel_id))
                self.modules.time.sleep(60)
            else: # on ERROR
                try:
                    if data.json()["error"]:
                        self.logger("ERROR: {id}: {status_code} {message}".format(id=novel_id, status_code=data.status_code, message=data.json()["message"]))
                        return {"stauts": data.status_code, "message": data.json()["message"]}
                    else:
                        self.logger("ERROR: {id}: {status_code}".format(id=novel_id, status_code=data.status_code))
                        return {"stauts": data.status_code, "message": "Unknown error"}
                except:
                    self.logger("ERROR: {id}: {status_code}".format(id=novel_id, status_code=data.status_code))
                    return {"stauts": data.status_code, "message": "Unknown error"}
                # Error handling end
        return {"stauts": 200, "data": p}