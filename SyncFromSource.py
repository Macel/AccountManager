if __name__ == '__main__':
    import logging
    import logging.handlers
    from BufferingSMTPHandler import BufferingSMTPHandler
    from Settings import LOGGING_LEVEL, LOGGING_PATH, SMTP_SERVER_IP, \
        SMTP_SERVER_PORT, SMTP_SERVER_USERNAME, SMTP_FROM_ADDRESS, \
        SMTP_SERVER_PASSWORD, LOGGING_ALERTS_CONTACT, DATA_SOURCE_FILE, \
        IMPORT_CHUNK_SIZE, AD_DC, AD_USERNAME, AD_PASSWORD, AD_OU_ASSIGNMENTS, \
        AD_ATTRIBUTE_MAP, AD_GROUP_ASSIGNMENTS
    from AccountManager import AccountManager # for atom code completion
    from ADAccountManager import ADAccountManager
    from CSVPager import CSVPager

    ###
    # log configuration
    ###
    logger = logging.getLogger("accounts")
    fileformatter = logging.Formatter('%(levelname)s '
                                      '; %(asctime)s '
                                      '; %(message)s')
    filehandler = logging.handlers.RotatingFileHandler(
        filename=LOGGING_PATH + "ADToGoogleSync.log",
        mode='a',
        maxBytes=10485760,
        backupCount=5)

    emailhandler = BufferingSMTPHandler(mailhost=SMTP_SERVER_IP,
                                        fromaddr=SMTP_FROM_ADDRESS,
                                        toaddrs=LOGGING_ALERTS_CONTACT,
                                        subject="SyncAccounts: Warnings or "
                                        "Errors Generated",
                                        mailport=SMTP_SERVER_PORT,
                                        mailusername=SMTP_SERVER_USERNAME,
                                        mailpassword=SMTP_SERVER_PASSWORD,
                                        capacity=1000)

    filehandler.setFormatter(fileformatter)
    filehandler.setLevel(LOGGING_LEVEL)
    emailhandler.setLevel(logging.WARN)
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(filehandler)
    logger.addHandler(emailhandler)

    # Begin Script
    logger.info("Logging initialized")

    # Sync accounts on paged data.
    pager = CSVPager(DATA_SOURCE_FILE, CSVPager.FILE_TYPE_TSV,
                     IMPORT_CHUNK_SIZE)
    logger.info("pager total record count: " + str(pager.csvRecordCount))
    i = 0

    while True:
        # With each page of records from the CSV file, run the sync process
        previ = i
        i = pager.getPage(i)
        currentPage = pager.page
        logger.debug("Page starting at index " + str(previ)
                     + " ending at index: " + str(i-1))
        for row in currentPage:
            logger.debug(str(row))

        # With the current page, use ADAccountManager to sync data to AD
        adam = ADAccountManager(AD_DC, AD_USERNAME, AD_PASSWORD,
                                AD_OU_ASSIGNMENTS,
                                AD_ATTRIBUTE_MAP,
                                AD_GROUP_ASSIGNMENTS,
                                IMPORT_CHUNK_SIZE)
        adam.data = currentPage
        logger.info(adam.performSync())
        if i == -1:  # End of CSV file reached
            break

    logger.info("Sync Process has completed.")
    # End Script
