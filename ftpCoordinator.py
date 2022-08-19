import ftplib
import pysftp
import os.path
import os
import datetime
import re
import config

import glob
import peekaboo # peekaboo.py is gitignored -> create it yourself
from pathlib import Path

# regular FTP
def transferFileViaFTP(fileName, ftpTargetFolder):

    targetUrl = None

    try:

        with ftplib.FTP(config.ftpServer) as ftp:

            # login
            ftp.login(peekaboo.ftpUsername, peekaboo.ftpPassword)

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

# used for KJL Bot Server
def transferFileViaFTP_SSL(fileName, ftpSSLTargetDir):

    ftpSSLHostName = config.kjlFtpSSLHostName
    ftpSSLPort = config.kjlFtpSSLPort
    ftpSSLUsername = peekaboo.kjlFtpSSLUsername
    ftpSSLPassword = peekaboo.kjlFtpSSLPassword

    client = ftplib.FTP_TLS(timeout=10)
    client.connect(ftpSSLHostName, ftpSSLPort)

    # enable TLS
    client.auth()
    client.prot_p()

    client.login(ftpSSLUsername,ftpSSLPassword)

    targetUrl = None

    try:

        with ftplib.FTP_TLS(timeout=10) as ftp:

            ftp.connect(ftpSSLHostName, ftpSSLPort)

            # enable TLS
            ftp.auth()
            ftp.prot_p()

            # login
            ftp.login(ftpSSLUsername,ftpSSLPassword)

            # change to target dir
            ftp.cwd(ftpSSLTargetDir)

            with open(fileName, 'rb') as fp:

                res = ftp.storbinary("STOR %s" % fileName.name, fp)

            targetUrl = os.path.join(ftpSSLHostName, ftpSSLTargetDir, fileName)

    except Exception as e:
        print('FTP error:', e)

    return targetUrl

# not used for KJL Bot
def transferFileViaSFTP(fileName, sftpHostName, sftpPort, sftpUsername, sftpPassword, sftpTargetDir):

    # early return if file does not exist
    if not os.path.exists(fileName):
        print(f"Local file {fileName} does not exist any more. Skipping transfer.")
        return


    # do not check host key
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(host = sftpHostName, username=sftpUsername, password=sftpPassword, port=sftpPort, cnopts=cnopts) as sftp:

        with sftp.cd(sftpTargetDir):
            sftp.put(fileName)





# Main file
if __name__ == "__main__":

    # transfer to Artistic Engines FTP Server
    # fileName = Path('kjlbot.xml')
    # transferFileViaFTP(fileName, config.ftpTargetFolder)

    # transfer to KJL Bot SFTP Server
    #transferFileViaSFTP(fileName, sftpHostName = sftpHostName, sftpPort = sftpPort, sftpUsername = sftpUsername, sftpPassword = sftpPassword, sftpTargetDir = sftpTargetDir)
    fileName = Path('recentBooks.json')
    transferFileViaFTP_SSL(fileName, config.kjlFtpSSLTargetDir)
