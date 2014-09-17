#coding: utf-8
import logging

class BrieLogging:

    logger = None

    @staticmethod
    def initializeLog():
        # create logger with 'spam_application'
        BrieLogging.logger = logging.getLogger('Brie')
        BrieLogging.logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh1 = logging.FileHandler('brie.log')
        fh1.setLevel(logging.INFO)
        # create file handler which logs even debug messages
        fh2 = logging.FileHandler('brie_debug.log')
        fh2.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        #ch = logging.StreamHandler()
        #ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh1.setFormatter(formatter)
        fh2.setFormatter(formatter)
        # add the handlers to the logger
        BrieLogging.logger.addHandler(fh1)
        BrieLogging.logger.addHandler(fh2)
    #end def

    @staticmethod
    def get():
        if BrieLogging.logger is None:
            BrieLogging.initializeLog()
        #end if
        return BrieLogging.logger
    #end def

#end class
