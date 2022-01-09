import ftplib
import os.path
import os
import datetime
import re
import config

import glob
from peekaboo import ftpUsername, ftpPassword # peekaboo.py is gitignored -> create it yourself
from pathlib import Path


def transferFile(fileName, ftpTargetFolder):
     
    targetUrl = None
 
    try:
 
        with ftplib.FTP(config.ftpServer) as ftp:
         
            # login
            ftp.login(ftpUsername, ftpPassword)   
 
            # change to target dir
            ftp.cwd(ftpTargetFolder)
 
            with open(fileName, 'rb') as fp:
             
                res = ftp.storbinary("STOR %s" % fileName.name, fp)
                 
                if not res.startswith('226 Transfer complete'):
                     
                    print('Upload failed')
             
            targetUrl = os.path.join(config.ftpServer, config.ftpTargetFolder, fileName)
                   
    except Exception as e:
        print('FTP error:', e)
 
    return targetUrl


def transferMultipleFiles(folderPath, searchTerm, ftpTargetDir):

    # get all files matching search term
    matchingFiles = folderPath.glob(searchTerm)

    for fileName in matchingFiles:
        print("\nTransfering file: %s" % fileName)
        transferFile(fileName, ftpTargetDir)




def dateOfYoungestFTPFile(ftpDir):

    # default answer
    datetimeOfYoungestFile = None

    with ftplib.FTP(hostname) as ftp:
        

        # login
        ftp.login(ftpUsername, ftpPassword)   

        # change to target dir
        ftp.cwd(ftpDir)

        fileList = ftp.nlst()

        # youngest file at the end of the list
        sortedFileList = sorted(fileList)

        print(sortedFileList)

        # grab youngest file
        if len(sortedFileList) > 0:
            youngestFile = sortedFileList[-1]

            # extract date from filename
            match = re.search(r'(.+)-(.+)-(.+)\..*', youngestFile)
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
    

            # create datetime
            datetimeOfYoungestFile = datetime.datetime(year=year, month=month, day=day)

    # return result
    return datetimeOfYoungestFile

def removeFile(filePath):
    os.remove(filePath)

# Main file
if __name__ == "__main__":

    fileName = Path('kjlbot.xml')
    transferFile(fileName, config.ftpTargetFolder)
