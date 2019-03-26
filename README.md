# AccountManager

This project is currently under development and there is not yet a working build.

The purpose of this project is to create an easy-to-configure solution for automating the synchronization of user account information between systems that do not already have methods for doing so.  In this respect, it is very similar to an identity management solution.

I am actively developing this to provide a solution for my employer to synchronize from a student information system database to Active Directory.  In order to generalize as much as possible, the data source I am writing in support for now will be a CSV export as provided by the student information system, so theoretically any system that can export a CSV with user information could be made the data source.

The long-term goal is to modularize this project to make it easy to write additional modules to support other systems (as data sources and destinations) as needed.  For example, the ability to use a SQL database as a data source, or the ability to sync to a specific product such as a financial system or timeclock management system could be added in.

Since this is still very early in development, and I am in a time crunch to get the AD implementation done, I will stop here for now.. But feel free to contact me if you have any interest in this project including implementation questions, suggestions or a desire to contribute.

Credit should also go to Vinay Sajip whose code I have integrated into this project as BufferingSMTPHandler.py for logging purposes.

Requirements
============

The current plan for ADAccountManager is to use python-ldap as the connection provider.
http://python-ldap.org/

Certain Windows AD-specific functionality, such as setting the 'user cannot change password' flag, or any other ACL-based operations, cannot be implemented with
a generic ldapv3 module.  Other workarounds may be available in such instances.  For example, instead of setting the 'user cannot change password' flag, a group policy can be applied on the users who should not be able to change password that prevents them from accessing the password reset functionality in windows.

Installable via pip,
::
python -m pip install python-ldap

If you are running this from a windows machine, I recommend downloading a precompiled 'wheel' of python-ldap as extra steps would need to be taken in a windows environment to get python-ldap to install via pip.  Unofficial win32 x86/64 wheels for python-ldap can be obtained via https://www.lfd.uci.edu/~gohlke/pythonlibs/

in order to install the wheel file, you will need to install the wheels module for pip
::
python -m pip install wheel

... And then to install the wheel file it would be something like:
::
python -m pip install /path/to/wheelfile.whl
