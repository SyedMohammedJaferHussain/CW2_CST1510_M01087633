class Dataset:
    def __init__(self, id, name, ctgry, sizeB) -> None:
        self.__id = id
        self.__name = name
        self.__ctgry = ctgry
        self.__fileSize = sizeB
    
    def CalcSizeMB(self):
        return self.__fileSize / 1048576 #1MB = 1048576B (2^20)

    def __str__(self):
        return f"ID: {self.__id}, Name: {self.__name}, Category: {self.__ctgry}, File Size(MB): {self.CalcSizeMB()}, File Size (B): {self.__fileSize}"