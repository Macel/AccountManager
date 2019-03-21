"""
Configurable settings used by sync scripts.
"""

import logging
from ADOrgUnitAssignments import ADOrgUnitAssignment, ADOrgUnitAssignmentRule
from AttributeMapping import AttributeMapping

# Some Constants...
SYNCHRONIZED = AttributeMapping.SYNCHRONIZED
NOT_SYNCHRONIZED = AttributeMapping.NOT_SYNCHRONIZED
MATCH_ANY_RULE = ADOrgUnitAssignment.MATCH_ANY_RULE
MATCH_ALL_RULES = ADOrgUnitAssignment.MATCH_ALL_RULES


# Logging Config
LOGGING_LEVEL = logging.DEBUG
LOGGING_PATH = ".\\"
LOGGING_ALERTS_CONTACT = "service-notifications@mydomain.org"


# Data Source information
DATA_SOURCE_FILE = ".\\studenttest.tsv"
IMPORT_CHUNK_SIZE = 500


# SMTP connection information
SMTP_SERVER_IP = "10.100.20.7"
SMTP_SERVER_PORT = 25
SMTP_SERVER_USERNAME = None
SMTP_SERVER_PASSWORD = None
SMTP_FROM_ADDRESS = "AccountSync@mydomain.org"


# DS (Data Source) Column Definition: Defines names for each column in the
# import CSV by column number (starting with zero).AD_PASSWORD
DS_COLUMN_DEFINITION = (
    "ID",
    "STATUS",
    "FIRST_NAME",
    "MIDDLE_NAME",
    "LAST_NAME",
    "DEPARTMENT",
    "TITLE"
)

# Default Grace period before accounts marked as inactive in the authoritative
# source are deactivated in external sources.
DEFAULT_ACCOUNT_GRACE_PERIOD_DAYS = 30


# AD Connection settings
AD_DC = "dc.example.org"
AD_USERNAME = "someusername"
AD_PASSWORD = "somepassword"


# The DN of the default OU for users who do not match any OU assignment rules
AD_DEFAULT_USER_OU = "OU=Unassigned,OU=Users,DC=example,DC=org"


# AD Attribute map:  Each entry is the column name from the import CSV file,
# an AD attribute that should have the column value synced to, and true/False
# for whether or not the value should remain synchronized for existing accounts.
AD_ATTRIBUTE_MAP = (
    AttributeMapping("FIRST_NAME", "fn", SYNCHRONIZED),
    AttributeMapping("MIDDLE_NAME", "mn", SYNCHRONIZED),
    AttributeMapping("LAST_NAME", "sn", SYNCHRONIZED),
    AttributeMapping("DEPARTMENT", "department", SYNCHRONIZED),
    AttributeMapping("TITLE", "title", SYNCHRONIZED),
)


# AD OU Assignments: A list of rules and matching OUs (by distinguished name)
# If a user matches multiple rules, they will be assigned to the first matching
# OU.  If a user does not match any of the assignment rules, they will be
# placed in the default OU specified in this settings file.
# For readability, the actual assignment rules lists are seperated out
# from the AD_OU_ASSIGNMENTS list
# Note that assignment rules are regular expressions.
GRADE_PK_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade PK[3-4]$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_K_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade K$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_1_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 1$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_2_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 2$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_3_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 3$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_4_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 4$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_5_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 5$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_6_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 6$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_7_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 7$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_8_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 8$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_9_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 9$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_10_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 10$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_11_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 11$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)
GRADE_12_OU_ASSIGNMENT_RULES = (
    ADOrgUnitAssignmentRule("DEPARTMENT", "^Grade 12$"),
    ADOrgUnitAssignmentRule("ACTIVESTATUS", "ACTIVE")
)

AD_OU_ASSIGNMENTS = (
    ADOrgUnitAssignment("OU=PK,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_PK_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=K,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_K_OU_ASSIGNMENT_RULES),
    ADOrgUnitAssignment("OU=1,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_1_OU_ASSIGNMENT_RULES),
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
    ADOrgUnitAssignment("OU=12,OU=Students,OU=Users,OU=CPS,DC=colchesterct,DC=org", MATCH_ALL_RULES, GRADE_12_OU_ASSIGNMENT_RULES)
)


# AD Group Assignments:  Rules that determine group membership in AD.
# Each assignment is a list of rules that must be met in order to be assigned
# the group, followed by the DN of the group to be assigned, and true/false
# stating whether membership of this group should remain synchronized
# (The user should be removed from group if they no longer meet the
# membership requirements).
# For readability, the actual assignment rules lists are seperated out.
GRADE_PK_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade PK[3-4]$")
)
GRADE_K_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade K$")
)
GRADE_1_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 1$")
)
GRADE_2_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 2$")
)
GRADE_3_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 3$")
)
GRADE_4_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 4$")
)
GRADE_5_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 5$")
)
GRADE_6_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 6$")
)
GRADE_7_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 7$")
)
GRADE_8_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 8$")
)
GRADE_9_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 9$")
)
GRADE_10_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 10$")
)
GRADE_11_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 11$")
)
GRADE_12_STUDENTS_GROUP_RULES = (
    ("DEPARTMENT", "^Grade 12$")
)

AD_GROUP_ASSIGNMENTS = (
    (GRADE_PK_STUDENTS_GROUP_RULES, "CN=Grade PK Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_K_STUDENTS_GROUP_RULES, "CN=Grade K Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_1_STUDENTS_GROUP_RULES, "CN=Grade 1 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_2_STUDENTS_GROUP_RULES, "CN=Grade 2 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_3_STUDENTS_GROUP_RULES, "CN=Grade 3 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_4_STUDENTS_GROUP_RULES, "CN=Grade 4 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_5_STUDENTS_GROUP_RULES, "CN=Grade 5 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_6_STUDENTS_GROUP_RULES, "CN=Grade 6 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_7_STUDENTS_GROUP_RULES, "CN=Grade 7 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_8_STUDENTS_GROUP_RULES, "CN=Grade 8 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_9_STUDENTS_GROUP_RULES, "CN=Grade 9 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_10_STUDENTS_GROUP_RULES, "CN=Grade 10 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_11_STUDENTS_GROUP_RULES, "CN=Grade 11 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED),
    (GRADE_12_STUDENTS_GROUP_RULES, "CN=Grade 12 Students - User Group,OU=User Groups,OU=Groups,OU=CPS,DC=colchesterct,DC=org", SYNCHRONIZED)

)
