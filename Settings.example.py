"""
Configurable settings used by sync scripts.
"""

import logging
from AccountManager_Module_AD.ADOrgUnitAssignments import ADOrgUnitAssignment
from AttributeMapping import AttributeMapping
from AccountManager_Module_AD.ADGroupAssignments import ADGroupAssignment
from AssignmentRules import AssignmentRule
from CSVPager import CSVPager
from UserNameAssignments import UserNameAssignment
from PasswordAssignments import PasswordAssignment, PASS_TYPE_ALPHA, \
                                PASS_TYPE_ALPHA_NUMERIC, PASS_TYPE_ALPHA_SYMBOLS, \
                                PASS_TYPE_WORDS, PASS_TYPE_STATIC
from NewUserNotifications import NewUserNotification

# Some Constants...
SYNCHRONIZED = AttributeMapping.SYNCHRONIZED
NOT_SYNCHRONIZED = AttributeMapping.NOT_SYNCHRONIZED
MATCH_ANY_RULE = ADOrgUnitAssignment.MATCH_ANY_RULE
MATCH_ALL_RULES = ADOrgUnitAssignment.MATCH_ALL_RULES

# Logging Config
LOGGING_LEVEL = logging.DEBUG
LOGGING_PATH = ".\\sync.log"
LOGGING_ALERTS_CONTACT = "blah@blah.org"

# SMTP connection information
SMTP_SERVER_IP = "1.2.3.4"
SMTP_SERVER_PORT = 25
SMTP_SERVER_USERNAME = None
SMTP_SERVER_PASSWORD = None
SMTP_FROM_ADDRESS = "blah@blah.org"

# How many records should be processed at a time from the datasource file?
IMPORT_CHUNK_SIZE = 500

# DS (Data Source) Column Definition: Defines names for each column in the
# import CSV by column number (starting with zero).
DS_COLUMN_DEFINITION = {
    "ID": 0,
    "STATUS": 1,
    "FIRST_NAME": 2,
    "MIDDLE_NAME": 3,
    "LAST_NAME": 4,
    "DEPARTMENT": 5,
    "TITLE": 6,
    "PSCHOOLID": 7,
    "EMAIL": 8,
    "COPIERPIN": 9,
    "RESETPASS": 10,
}

# The column defined below should contain a "1" to indicate that any target
# databases which generate their own passwords should re-generate a new pass
# for the user.
RESET_PASS_COLUMN_NAME = "RESETPASS"

# The name of the column in the datasource that identifies the active/Inactive
# state of the user account.
DS_STATUS_COLUMN_NAME = "STATUS"

# When synchronizing the active status of accounts to target databases,
# which values signify an active or inactive (disabled) account?
# Multiple potential values may be provided
# Example: DS_ACTIVE_STATUS_VALUE = ("Active", "Pre-Registered")
DS_STATUS_ACTIVE_VALUES = ("ACTIVE",)
DS_STATUS_INACTIVE_VALUES = ("INACTIVE",)

# DS_ACCOUNT_IDENTIFIER is the unique source identifier to link to destination on.
DS_ACCOUNT_IDENTIFIER = "ID"

# The secondary match column is the alternate method of locating a user in the
# target database if the account is not already linked.  This should be a Value
# that is guaranteed to be unique to the user.
DS_SECONDARY_MATCH_COLUMN = "EMAIL"

# If the data source will be providing the username and/or password, define
# the column names from the column definition that contain this information here.
DS_USERNAME_COLUMN_NAME = "USERNAME"
DS_PASSWORD_COLUMN_NAME = "PASSWORD"

# By default the new/reset password account notifications emails will include
# the generated usernames and passwords for each user record stored there,
# as well as the name of the target database for which the accounts were
# created/modified. The following specifies any additional information from
# the datasource that should be included.  The names of the columns as
# defined in DS_COLUMN_DEFINITION should be specified here.
ACCOUNT_NOTIFICATION_FIELDS = (
    "FIRST_NAME",
    "MIDDLE_NAME",
    "LAST_NAME",
    "DEPARTMENT",
    "TITLE"
)

# New User Notifications:
# The following sets of rules determines who gets notified when a user account
# is created *OR*  their password is reset via the forcepwdreset flag..
CES_STUDENT_USER_NOTIFICATION_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade PK[3-4]$"),
    AssignmentRule("DEPARTMENT", "^Grade K$"),
    AssignmentRule("DEPARTMENT", "^Grade 1$"),
    AssignmentRule("DEPARTMENT", "^Grade 2$"),
)
JJIS_STUDENT_USER_NOTIFICATION_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 3$"),
    AssignmentRule("DEPARTMENT", "^Grade 4$"),
    AssignmentRule("DEPARTMENT", "^Grade 5$"),
)
WJMS_STUDENT_USER_NOTIFICATION_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 6$"),
    AssignmentRule("DEPARTMENT", "^Grade 7$"),
    AssignmentRule("DEPARTMENT", "^Grade 8$"),
)
BA_STUDENT_USER_NOTIFICATION_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 9$"),
    AssignmentRule("DEPARTMENT", "^Grade 10$"),
    AssignmentRule("DEPARTMENT", "^Grade 11$"),
    AssignmentRule("DEPARTMENT", "^Grade 12$"),
)
CES_STAFF_USER_NOTIFICATION_RULES = (
    AssignmentRule("DEPARTMENT", "^CES$"),
)
JJIS_STAFF_USER_NOTIFICATION_RULES = (
    AssignmentRule("DEPARTMENT", "^JJIS$"),
)
WJMS_STAFF_USER_NOTIFICATION_RULES = (
    AssignmentRule("DEPARTMENT", "^WJJMS$"),
)
BA_STAFF_USER_NOTIFICATION_RULES = (
    AssignmentRule("DEPARTMENT", "^BA$"),
    AssignmentRule("DEPARTMENT", "^BAAE$"),
)
DISTRICT_STAFF_USER_NOTIFICATION_RULES = (
    AssignmentRule("DEPARTMENT", "^District$"),
    AssignmentRule("DEPARTMENT", "^Grad$"),
    AssignmentRule("DEPARTMENT", "^ODD$"),
    AssignmentRule("DEPARTMENT", "^ENR$"),
    AssignmentRule("DEPARTMENT", "^SRP$"),
)

# If you do not want new user notifications to be sent,
# just leave this tuple empty...
NEW_USER_NOTIFICATIONS = (
    NewUserNotification(CES_STUDENT_USER_NOTIFICATION_RULES,
                        MATCH_ANY_RULE,
                        "blah@blah.org"),
    NewUserNotification(JJIS_STUDENT_USER_NOTIFICATION_RULES,
                        MATCH_ANY_RULE,
                        "blah@blah.org"),
    NewUserNotification(WJMS_STUDENT_USER_NOTIFICATION_RULES,
                        MATCH_ANY_RULE,
                        "blah@blah.org"),
    NewUserNotification(BA_STUDENT_USER_NOTIFICATION_RULES,
                        MATCH_ANY_RULE,
                        "blah@blah.org"),
    NewUserNotification(CES_STAFF_USER_NOTIFICATION_RULES,
                        MATCH_ANY_RULE,
                        "blah@blah.org"),
    NewUserNotification(JJIS_STAFF_USER_NOTIFICATION_RULES,
                        MATCH_ANY_RULE,
                        "blah@blah.org"),
    NewUserNotification(WJMS_STAFF_USER_NOTIFICATION_RULES,
                        MATCH_ANY_RULE,
                        "blah@blah.org"),
    NewUserNotification(BA_STAFF_USER_NOTIFICATION_RULES,
                        MATCH_ANY_RULE,
                        "blah@blah.org"),
    NewUserNotification(DISTRICT_STAFF_USER_NOTIFICATION_RULES,
                        MATCH_ANY_RULE,
                        "blah@blah.org"),
)

###
# Specify which sync modules to use here.
# Since AD is currently the only one...
###
SYNC_TO_AD = True

###
# **** AD-Specific Sync Settings ****
###
# AD Connection settings
AD_DC = "server.colchesterct.org"
AD_USERNAME = "syncsvc"
AD_PASSWORD = "somepassword"

# The base DN to search in AD for users
AD_BASE_USER_DN = "OU=Users,OU=CPS,DC=colchesterct,DC=org"

# The DN of the default OU for users who do not match any OU assignment rules
AD_DEFAULT_USER_OU = "OU=Unassigned,OU=Users,OU=CPS,DC=colchesterct,DC=org"

# TARGET_ACCOUNT_IDENTIFIER is the name of the attribute in the target database
# that will be linked to.
AD_TARGET_ACCOUNT_IDENTIFIER = "powerschoolID"

# The AD Secondary Match Attribute is the attribute that should be checked
# against the DS_SECONDARY_MATCH_COLUMN if a user account is not found in AD
# with the link ID of the data source user.  If a secondary match is found,
# the user will be linked and updated accordingly.  The secondary field should
# uniquely identify a user.
AD_SECONDARY_MATCH_ATTRIBUTE = "mail"

# Should a username and password be generated for any new user accounts created
# in AD?  The following two variables define this.
# If AD_SHOULD_GENERATE_USERNAME is false, DS_USERNAME_COLUMN will be referenced
# for both the sAMAccountName and the userPrincipalName.
# Usernames need to be 20 characters or less and cannot contain any of the
# following characters: " / \ [ ] : | < > + = ; ? * ,
# They cannot be terminated with a period (.)
#
# If AD_SHOULD_GENERATE_PASSWORD is false, DS_PASSWORD_COLUMN will be referenced
# and the password complexity provided in the datasource should match the
# minimum complexity requirements of your domain.
# For security reasons, it is recommended NOT to have the datasource provide
# passwords as they would be stored in plain text in the export file.
AD_SHOULD_GENERATE_USERNAME = True
AD_SHOULD_GENERATE_PASSWORD = True

# AD Attribute map:  Each entry is the column name from the import CSV file,
# an AD attribute that should have the column value synced to, and true/False
# for whether or not the value should remain synchronized for existing accounts.
# *Note: If you want to force a password change on the next sync,
# you would include a field in your datasource file for REQ_PASS_CHG with a
# value of 0 and add the following to the attribute map:
#   AttributeMapping("REQ_PASS_CHG", "pwdLastSet", SYNCHRONIZED)
#   REQ_PASS_CHG = -1 , no
#   REQ_PASS_CHG = 0 , force pass change on next login
AD_ATTRIBUTE_MAP = (
    AttributeMapping("FIRST_NAME", "givenName", SYNCHRONIZED),
    AttributeMapping("MIDDLE_NAME", "middleName", SYNCHRONIZED),
    AttributeMapping("LAST_NAME", "sn", SYNCHRONIZED),
    AttributeMapping("DEPARTMENT", "department", SYNCHRONIZED),
    AttributeMapping("TITLE", "title", SYNCHRONIZED),
    AttributeMapping("EMAIL", "mail", NOT_SYNCHRONIZED),
    AttributeMapping("COPIERPIN", "pager", SYNCHRONIZED)
)

# AD OU Assignments: A list of rules and matching OUs (by distinguished name)
# If a user matches multiple rules, they will be assigned to the first matching
# OU.  If a user does not match any of the assignment rules, they will be
# placed in the default OU specified in this settings file.
# For readability, the actual assignment rules lists are seperated out
# from the AD_OU_ASSIGNMENTS list
# Note that assignment rules are regular expressions.
GRADE_2_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 2$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_3_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 3$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_4_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 4$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_5_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 5$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_6_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 6$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_7_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 7$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_8_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 8$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_9_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 9$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_10_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 10$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_11_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 11$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
GRADE_12_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 12$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
CES_STAFF_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^CES$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
JJIS_STAFF_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^JJIS$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
WJMS_STAFF_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^WJJMS$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
BA_STAFF_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^BA$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
BAED_STAFF_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "^BAAE$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
DISTRICT_STAFF_OU_ASSIGNMENT_RULES = (
    AssignmentRule("DEPARTMENT", "(^District$)|(^SRP$)|(^ENR$)|(^ODD$)|(^Grad$)"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)

AD_OU_ASSIGNMENTS = (
    ADOrgUnitAssignment("OU=2,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_2_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=3,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_3_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=4,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_4_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=5,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_5_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=6,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_6_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=7,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_7_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=8,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_8_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=9,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_9_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=10,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_10_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=11,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_11_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=12,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_12_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=CES,OU=Staff,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, CES_STAFF_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=JJIS,OU=Staff,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, JJIS_STAFF_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=WJMS,OU=Staff,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, WJMS_STAFF_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=BA,OU=Staff,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, BA_STAFF_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=BAED,OU=Staff,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, BAED_STAFF_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=District,OU=Staff,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, DISTRICT_STAFF_OU_ASSIGNMENT_RULES),
)


# AD Group Assignments:  Rules that determine group membership in AD.
# Each assignment is a list of rules that must be met in order to be assigned
# the group, followed by the DN of the group to be assigned, and true/false
# stating whether membership of this group should remain synchronized
# (The user should be removed from group if they no longer meet the
# membership requirements).
# For readability, the actual assignment rules lists are seperated out.
GRADE_2_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 2$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_3_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 3$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_4_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 4$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_5_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 5$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_6_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 6$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_7_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 7$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_8_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 8$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_9_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 9$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_10_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 10$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_11_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 11$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADE_12_STUDENTS_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade 12$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
STUDENT_WEB_FILTERING_GROUP_RULES = (
    AssignmentRule("TITLE", "^STUDENT$"),
)
CES_STAFF_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^CES$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
JJIS_STAFF_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^JJIS$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
WJMS_STAFF_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^WJJMS$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
BA_STAFF_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^BA$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
BAED_STAFF_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "^BAAE$"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
DISTRICT_STAFF_GROUP_RULES = (
    AssignmentRule("DEPARTMENT", "(^District$)|(^SRP$)|(^ENR$)|(^ODD$)|(^Grad$)"),
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$")
)
STAFF_WEB_FILTERING_GROUP_RULES = (
    AssignmentRule("TITLE", "^((?!STUDENT).)*$"),
)
FOLDER_REDIRECTED_USERS_RULES = (
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
ACTIVE_SYNCHRONIZED_USERS_RULES = (
    AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
)
OFFICE_365_FACULTY_LICENSE_RULES = (
	AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
	AssignmentRule("TITLE", "^((?!STUDENT).)*$")
)
OFFICE_365_STUDENT_LICENSE_RULES = (
	AssignmentRule(DS_STATUS_COLUMN_NAME, "^ACTIVE$"),
	AssignmentRule("TITLE", "^STUDENT$")
)

AD_GROUP_ASSIGNMENTS = (
    ADGroupAssignment("CN=Grade 2 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_2_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 3 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_3_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 4 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_4_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 5 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_5_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 6 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_6_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 7 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_7_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 8 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_8_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 9 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_9_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 10 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_10_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 11 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_11_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Grade 12 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, GRADE_12_STUDENTS_GROUP_RULES),
    ADGroupAssignment("CN=Student Web Filtering - Resource Group,OU=Web Filtering Groups,OU=Resource Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", NOT_SYNCHRONIZED, MATCH_ALL_RULES, STUDENT_WEB_FILTERING_GROUP_RULES),
    ADGroupAssignment("CN=CES Staff - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, CES_STAFF_GROUP_RULES),
    ADGroupAssignment("CN=JJIS Staff - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, JJIS_STAFF_GROUP_RULES),
    ADGroupAssignment("CN=WJMS Staff - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, WJMS_STAFF_GROUP_RULES),
    ADGroupAssignment("CN=BA Staff - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, BA_STAFF_GROUP_RULES),
    ADGroupAssignment("CN=BAED Staff - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, BAED_STAFF_GROUP_RULES),
    ADGroupAssignment("CN=District Staff - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, DISTRICT_STAFF_GROUP_RULES),
    ADGroupAssignment("CN=Staff Web Filtering - Resource Group,OU=Web Filtering Groups,OU=Resource Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", NOT_SYNCHRONIZED, MATCH_ALL_RULES, STAFF_WEB_FILTERING_GROUP_RULES),
    ADGroupAssignment("CN=Folder Redirected Users - Resource Group,OU=Folder Redirection,OU=Resource Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", NOT_SYNCHRONIZED, MATCH_ALL_RULES, FOLDER_REDIRECTED_USERS_RULES),
	ADGroupAssignment("CN=Active Synchronized Users - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, ACTIVE_SYNCHRONIZED_USERS_RULES),
	ADGroupAssignment("CN=Office 365 Faculty License - Resource Group,OU=Resource Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, OFFICE_365_FACULTY_LICENSE_RULES),
	ADGroupAssignment("CN=Office 365 Student License - Resource Group,OU=Resource Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED, MATCH_ALL_RULES, OFFICE_365_STUDENT_LICENSE_RULES),
)

# Should inactive users be removed from all security/distribution groups?
AD_REMOVE_INACTIVE_USERS_FROM_GROUPS = True

# The following is the subject header for new user notifications emails in AD
AD_USER_NOTIFICATION_SUBJECT = "New AD User Accounts Notification"

# The following message gets prepended to the new user notifications emails for
# AD.  New user notification emails include a list of user account names and
# initial passwords at the bottom of the email body.
AD_USER_NOTIFICATION_MSG = (
    "AD Accounts have been created for the following users.  "
    "This will also be their new email address.  "
    "Please make sure to update their email address in Powerschool if you are "
    "the responsible party.  They will need to be provided their username and "
    "passwords:\n"
)

# The following is the subject header for password reset notifications emails
# in AD.
AD_PASS_RESET_NOTIFICATION_SUBJECT = "AD User Password(s) Reset Notification "

# The following message gets prepended to the password reset notifications
# emails for AD.  Password reset emails include a list of user account names
# and initial passwords at the bottom of the email body.
AD_PASS_RESET_NOTIFICATION_MSG = (
    "The following AD accounts have have had their passwords reset by the "
    "AccountManager.  Please make note of the following new passwords for "
    "these users:\n"
)

###
# **** Username and Password Settings ****
###

# Definition for which fields and formatting should be used to generate
# usernames.  Format codes represent how many characters and which direction
# they should be read from.
# Example: "LTR:12" means *up to* the first 12 characters of the corresponding
# field in the username fields tuple should be used.  If the corresponding
# username field is less than or equal to 12 characters in length, the entire
# field will be used in the username.
# "RTL:2" would mean that the last two characters of the corresponding field in
# the username fields tuple should be used.
# If the username tuple looks like:
# ("Robert","Meany","2015")
# And the formatting tuple looks like:
# ("LTR:3","LTR:99","RTL:2")
# The resulting username would be:
#  RobMeany15
# The below example username format tuples include multiple formats
# in the case a conflicting name already exists in AD when a new username is
# generated, usernames will be attempted in the order below until a unique
# name is found.
# It is recommended to have several options for formatting codes so as to
# reduce the likelyhood that a user account creation will fail due to being
# unable to find a unique username.

STUDENT_USERNAME_FIELDS = ("FIRST_NAME", "LAST_NAME", "PSCHOOLID",)
STUDENT_USERNAME_FORMATS = (
    ("LTR:1", "LTR:4", "RTL:5"),
)

STAFF_USERNAME_FIELDS = ("FIRST_NAME", "LAST_NAME",)
STAFF_USERNAME_FORMATS = (
    ("LTR:1", "LTR:14"),
    ("LTR:2", "LTR:13"),
    ("LTR:3", "LTR:12"),
    ("LTR:4", "LTR:11"),
    ("LTR:5", "LTR:10"),
    ("LTR:6", "LTR:9"),
)

# Word lists for word-based password generator:
PASS_FIRST_WORD_LIST = (
    "",
)

PASS_SECOND_WORD_LIST = (
    "Abolish",
    "Abridge",
    "Absence",
    "Account",
    "Address",
    "Advance",
    "Adviser",
    "Analyst",
    "Applaud",
    "Approve",
    "Archive",
    "Arrange",
    "Article",
    "Auction",
    "Awesome",
    "Bananas",
    "Bargain",
    "Barrier",
    "Battery",
    "Bedroom",
    "Benefit",
    "Biscuit",
    "Bracket",
    "Breathe",
    "Calorie",
    "Capital",
    "Captain",
    "Capture",
    "Catbird",
    "Central",
    "Century",
    "Certain",
    "Chapter",
    "Charter",
    "Chicken",
    "Chimney",
    "Citizen",
    "Clarify",
    "Climate",
    "Cluster",
    "Collect",
    "College",
    "Combine",
    "Comfort",
    "Command",
    "Compact",
    "Company",
    "Compete",
    "Compose",
    "Concept",
    "Confine",
    "Confuse",
    "Contain",
    "Content",
    "Control",
    "Convert",
    "Cookies",
    "Council",
    "Country",
    "Crevice",
    "Current",
    "Cyclone",
    "Decline",
    "Default",
    "Deficit",
    "Deliver",
    "Density",
    "Dentist",
    "Deposit",
    "Dessert",
    "Develop",
    "Diagram",
    "Dialect",
    "Diamond",
    "Dictate",
    "Digital",
    "Dignity",
    "Digress",
    "Dilemma",
    "Discuss",
    "Distant",
    "Dolphin",
    "Economy",
    "Edition",
    "Embrace",
    "Emotion",
    "Endorse",
    "Enhance",
    "Enlarge",
    "Episode",
    "Equinox",
    "Evening",
    "Extinct",
    "Extract",
    "Extreme",
    "Eyebrow",
    "Falsify",
    "Fantasy",
    "Fashion",
    "Feather",
    "Feature",
    "Feeling",
    "Finance",
    "Fixture",
    "Formula",
    "Fortune",
    "Freckle",
    "Freedom",
    "Freight",
    "Garbage",
    "Genuine",
    "Glimpse",
    "Graphic",
    "Habitat",
    "Haircut",
    "Hallway",
    "Harmony",
    "Harvest",
    "Healthy",
    "Helpful",
    "History",
    "Horizon",
    "Hostage",
    "Housing",
    "Hunting",
    "Imagine",
    "Impress",
    "Imprint",
    "Improve",
    "Indulge",
    "Inflate",
    "Initial",
    "Insight",
    "Inspire",
    "Install",
    "Kitchen",
    "Laundry",
    "Lecture",
    "Leopard",
    "Liberal",
    "Liberty",
    "License",
    "Limited",
    "Loyalty",
    "Maximum",
    "Meaning",
    "Measure",
    "Meeting",
    "Mention",
    "Minimum",
    "Miracle",
    "Mistake",
    "Monarch",
    "Monster",
    "Morning",
    "Musical",
    "Mystery",
    "Nervous",
    "Neutral",
    "Nuclear",
    "Nucleus",
    "Obscure",
    "Octopus",
    "Officer",
    "Opinion",
    "Opposed",
    "Outlook",
    "Overall",
    "Paradox",
    "Parking",
    "Passive",
    "Pasture",
    "Patient",
    "Pattern",
    "Payment",
    "Pencils",
    "Penguin",
    "Pension",
    "Percent",
    "Perform",
    "Perfume",
    "Persist",
    "Physics",
    "Picture",
    "Plastic",
    "Playful",
    "Popular",
    "Precede",
    "Predict",
    "Prevent",
    "Printer",
    "Private",
    "Process",
    "Product",
    "Profile",
    "Promise",
    "Promote",
    "Prosper",
    "Protect",
    "Protest",
    "Provoke",
    "Publish",
    "Pudding",
    "Pumpkin",
    "Pursuit",
    "Qualify",
    "Quarrel",
    "Quarter",
    "Radical",
    "Rainbow",
    "Reactor",
    "Reality",
    "Realize",
    "Receipt",
    "Recover",
    "Recruit",
    "Recycle",
    "Reflect",
    "Related",
    "Reptile",
    "Request",
    "Reserve",
    "Respect",
    "Retreat",
    "Reverse",
    "Routine",
    "Royalty",
    "Rubbish",
    "Sailing",
    "Sausage",
    "Scandal",
    "Scatter",
    "Scholar",
    "Scratch",
    "Screech",
    "Seasons",
    "Section",
    "Secular",
    "Seminar",
    "Serious",
    "Session",
    "Shatter",
    "Shelter",
    "Silence",
    "Similar",
    "Society",
    "Soldier",
    "Soprano",
    "Speaker",
    "Species",
    "Splurge",
    "Stadium",
    "Station",
    "Steward",
    "Stomach",
    "Storage",
    "Strange",
    "Student",
    "Stumble",
    "Subject",
    "Sulphur",
    "Swallow",
    "Sweater",
    "Teacher",
    "Testify",
    "Texture",
    "Theater",
    "Thinker",
    "Thirsty",
    "Thunder",
    "Trainer",
    "Trivial",
    "Trouble",
    "Unaware",
    "Unicorn",
    "Uniform",
    "Urgency",
    "Vanilla",
    "Variety",
    "Vehicle",
    "Venture",
    "Village",
    "Visible",
    "Volcano",
    "Warning",
    "Wedding",
    "Welcome",
    "Welfare",
    "Wrestle",
)

# Password Assignment rules determine which type of password should be generate
# for a new user.

GRADES_2_TO_5_PASSWORD_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade [2-5]$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
GRADES_5_TO_12_PASSWORD_RULES = (
    AssignmentRule("DEPARTMENT", "^Grade ([6-9]|1[0-2])$"),
    AssignmentRule("TITLE", "^STUDENT$"),
)
STAFF_PASSWORD_RULES = (
    AssignmentRule("TITLE", "^((?!STUDENT).)*$"),
)
PASSWORD_ASSIGNMENTS = (
    PasswordAssignment(rules=GRADES_2_TO_5_PASSWORD_RULES,
                       matchMethod=MATCH_ALL_RULES,
                       length=7,
                       passtype=PASS_TYPE_WORDS,
                       firstwords=PASS_FIRST_WORD_LIST,
                       secondwords=PASS_SECOND_WORD_LIST,
                       usermustreset=False),
    PasswordAssignment(rules=GRADES_5_TO_12_PASSWORD_RULES,
                       matchMethod=MATCH_ALL_RULES,
                       length=8,
                       passtype=PASS_TYPE_ALPHA_NUMERIC,
                       usermustreset=False),
    PasswordAssignment(rules=STAFF_PASSWORD_RULES,
                       matchMethod=MATCH_ANY_RULE,
                       length=8,
                       passtype=PASS_TYPE_STATIC,
                       staticpass="SomeInitialPassword",
                       usermustreset=True),
)

# Username formatting rules look at what attributes determine how a username
# for a new user should be formatted.
STUDENT_USERNAME_FORMATTING_RULES = (AssignmentRule("TITLE", "^STUDENT$"),)
STAFF_USERNAME_FORMATTING_RULES = (AssignmentRule("TITLE", "^((?!STUDENT).)*$"),)

USERNAME_ASSIGNMENTS = (
    UserNameAssignment(rules=STUDENT_USERNAME_FORMATTING_RULES,
                       matchMethod=MATCH_ALL_RULES,
                       formats=STUDENT_USERNAME_FORMATS,
                       userNameFields=STUDENT_USERNAME_FIELDS),
    UserNameAssignment(rules=STAFF_USERNAME_FORMATTING_RULES,
                       matchMethod=MATCH_ALL_RULES,
                       formats=STAFF_USERNAME_FORMATS,
                       userNameFields=STAFF_USERNAME_FIELDS),
)
