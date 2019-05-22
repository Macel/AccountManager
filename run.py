import sys
import argparse
import logging
import logging.handlers
from BufferingSMTPHandler import BufferingSMTPHandler
from AccountManager_Module_AD.ADSyncer import ADSyncer
from Settings import LOGGING_LEVEL, LOGGING_PATH, SMTP_SERVER_IP, \
                     SMTP_SERVER_PORT, SMTP_SERVER_USERNAME, SMTP_FROM_ADDRESS, \
                     SMTP_SERVER_PASSWORD, LOGGING_ALERTS_CONTACT, SYNC_TO_AD

###
# Init script
###
if __name__ == '__main__':
    ###
    # log configuration
    ###
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--DatasourcePath',
        help='Path to the data source file for user accounts.',
        required=True
        )
    parser.add_argument(
        '--DatasourceFileType',
        help='\'CSV\', or \'TSV\'',
        required=True,
        choices=['CSV', 'TSV']
    )

    args = parser.parse_args()

    logger = logging.getLogger("accounts")
    fileformatter = logging.Formatter(
        '%(levelname)s '
        '; %(asctime)s '
        '; %(message)s'
    )

    filehandler = logging.handlers.RotatingFileHandler(
        filename=LOGGING_PATH,
        mode='a',
        maxBytes=10485760,
        backupCount=5
    )

    emailhandler = BufferingSMTPHandler(
        mailhost=SMTP_SERVER_IP,
        fromaddr=SMTP_FROM_ADDRESS,
        toaddrs=LOGGING_ALERTS_CONTACT,
        subject="SyncAccounts: Warnings or "
        "Errors Generated",
        mailport=SMTP_SERVER_PORT,
        mailusername=SMTP_SERVER_USERNAME,
        mailpassword=SMTP_SERVER_PASSWORD,
        capacity=1000
    )

    filehandler.setFormatter(fileformatter)
    filehandler.setLevel(LOGGING_LEVEL)
    emailhandler.setLevel(logging.WARN)
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(filehandler)
    logger.addHandler(emailhandler)

    logger.info("Logging initialized")

    if (SYNC_TO_AD):
        adsyncer = ADSyncer(logger, args)
        adsyncer.runSyncProcess()

    logger.info("Finished running sync scripts.")
    emailhandler.flush() # Ensure logging email gets sent...
