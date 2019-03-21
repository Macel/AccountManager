#!/usr/bin/env python
#
# Copyright 2001-2002 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Vinay Sajip
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# This file is part of the Python logging distribution. See
# http://www.red-dove.com/python_logging.html
#
"""
Test harness for the logging module. Tests BufferingSMTPHandler, an alternative
implementation of SMTPHandler.
Copyright (C) 2001-2002 Vinay Sajip. All Rights Reserved.
"""
import string
import logging
import logging.handlers
from smtplib import *


class BufferingSMTPHandler(logging.handlers.BufferingHandler):
	def __init__(self, fromaddr, toaddrs, subject, capacity, mailhost,
              mailport=None, mailusername=None, mailpassword=None):
		logging.handlers.BufferingHandler.__init__(self, capacity)
		self.mailhost = mailhost
		self.mailport = mailport
		self.fromaddr = fromaddr
		self.toaddrs = toaddrs
		self.subject = subject
		self.username = mailusername
		self.password = mailpassword

		self.setFormatter(logging.Formatter(
			"%(asctime)s %(levelname)-5s %(message)s"))

	def flush(self):
		if len(self.buffer) > 0:
			try:
				port = self.mailport
				if not port:
					port = SMTP_PORT
				smtp = SMTP(host=self.mailhost, port=port)
				if not (self.username is None) and not (self.password is None):
					smtp.login(user=self.username, password=self.password)
				msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (self.fromaddr, string.join(self.toaddrs, ","),
                                                         self.subject)
				for record in self.buffer:
					s = self.format(record)
					msg = msg + s + "\r\n"
				smtp.sendmail(self.fromaddr, self.toaddrs, msg)
				smtp.quit()
			except SMTPConnectError as e:
				raise e
			except SMTPHeloError as e:
				smtp.close()
				raise e
			except SMTPAuthenticationError as e:
				smtp.close()
				raise e
			except SMTPException as e:
				smtp.close()
				raise e
			except:
				self.handleError(None)  # no particular record
			self.buffer = []
