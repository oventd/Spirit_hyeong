from abc import *

class Loader(metaclass=ABCMeta):
    # @abstractmethod
    # def validate(self):
    #     pass    
    @abstractmethod
    def import_file(self):
        pass
    @abstractmethod
    def reference_file(self):
        pass



