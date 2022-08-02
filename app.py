# -*- coding: utf-8 -*-

class dummy():
    def __init__(self) -> None:
        pass

if __name__ == "__main__":
    from pixiv import Pixiv_old as Pixiv
    p = Pixiv()
    p.control()
    p.logger("INFO : Program Finished")
    pass