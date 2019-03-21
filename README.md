# AccountManager

The purpose of this project is to create an easy-to-configure solution for automating the synchronization of user account information between systems that do not already have methods for doing so.  In this respect, it is very similar to an identity management solution.

I am actively developing this to provide a solution for my employer to synchronize from a student information system database to Active Directory.  In order to generalize as much as possible, the data source I am writing in support for now will be a CSV export as provided by the student information system, so theoretically any system that can export a CSV with user information could be made the data source.

The long-term goal is to modularize this project to make it easy to write additional modules to support other systems (as data sources and destinations) as needed.  For example, the ability to use a SQL database as a data source, or the ability to sync to a specific product such as a financial system or timeclock management system could be added in.

Since this is still very early in development, and I am in a time crunch to get the AD implementation done, I will stop here for now.. But feel free to contact me if you have any interest in this project including implementation questions, suggestions or a desire to contribute.

Credit should also go to Vinay Sajip whose code I have integrated into this project as BufferingSMTPHandler.py for logging purposes.

Requirements 
============ 

The current plan for ADAccountManager is use pyad, available at https://github.com/zakird/pyad

Installable via pip,
::
pip install pyad

pyad requires pywin32, available at http://sourceforge.net/projects/pywin32 

Also installable via pip,
:: 
pip install pywin32 



