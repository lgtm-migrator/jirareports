# Requires pypiwin32 and jira

# To Do:
# * Increase spacing between bullet points
# * Add Error handling in case the password is wrong

import datetime
from getpass import getpass
import win32com.client
from jira import JIRA


def getpassword():
    """ Get JIRA password, so we aren't hardcoding it """
    password = getpass("JIRA Password: ")
    if not password:
        exit()
    else:
        return password

USERNAME = 'rhart'
PASSWORD = getpassword()
JQL = JIRA(server=('https://jira.starrez.com'), basic_auth=(USERNAME, PASSWORD))


# Get data from JIRA
class PortalX:
    """ Query JIRA for information on PortalX """
    def __init__(self):
        print("Querying JIRA for PortalX issues...")
        self.techdebt = JQL.search_issues('"Epic Link" = PORTALX-1499 and ' \
        + 'resolution = Unresolved', maxResults=200)
        self.bugs = JQL.search_issues('project = PortalX AND resolution = ' \
        + 'Unresolved AND type in (Bug, "Testing Bug", "Sub-Task Bug") and component != "UITest"', maxResults=200)
        self.closedbugs1w = JQL.search_issues('project = PortalX AND resolved ' \
        + '>= -1w AND type in (Bug, "Testing Bug", "Sub-Task Bug") AND ' \
        + 'resolution not in (duplicate, "No Action Required") and component != "UITest"', maxResults=200)
        self.enhancements = JQL.search_issues('project = PortalX AND resolved ' \
        '>= -1w AND type not in (Bug, "Testing Bug", "Sub-Task Bug") AND ' \
        'resolution = Fixed ORDER BY priority DESC', maxResults=200)

class StarRezWeb:
    """ Query JIRA for information on StarRez Web """
    def __init__(self):
        print("Querying JIRA for StarRez Web issues...")
        self.techdebt = JQL.search_issues('"Epic Link" = WEB-7359 and resolution = ' \
        + 'Unresolved', maxResults=200)
        self.bugs = JQL.search_issues('project = WEB AND resolution = Unresolved ' \
        + ' AND type in (Bug, "Testing Bug", "Sub-Task Bug") and component != "UITest"', maxResults=200)
        self.closedbugs1w = JQL.search_issues('project = "StarRez Web" AND ' \
        + 'resolved >= -1w AND type in (Bug, "Testing Bug", "Sub-Task Bug") ' \
        + 'AND resolution not in (duplicate, "No Action Required") and component != "UITest"', maxResults=200)
        self.enhancements = JQL.search_issues('project = "StarRez Web" AND resolved' \
        + ' >= -1w AND type not in (Bug, "Testing Bug", "Sub-Task Bug") AND ' \
        + 'resolution = Fixed ORDER BY priority DESC', maxResults=200)

class Cloud:
    """ Query JIRA for information on Cloud """
    def __init__(self):
        print("Querying JIRA for Cloud issues...")
        self.bugs = JQL.search_issues('project = Cloud AND resolution = Unresolved ' \
        + 'AND type in (Bug, "Testing Bug", "Sub-Task Bug")', maxResults=200)
        self.enhancements = JQL.search_issues('project = Cloud AND resolved >= -1w ' \
        + 'AND type not in (Bug, "Testing Bug", "Sub-Task Bug") AND ' \
        + 'resolution in (Done, Fixed) ORDER BY priority DESC', maxResults=200)

class Techhelp:
    """ Query JIRA for information on Techhelps """
    def __init__(self):
        print("Querying JIRA for Techhelp issues...")
        self.in2weeks = JQL.search_issues('project = tech and createdDate >= -2w', maxResults=200)
        self.in3weeks = JQL.search_issues('project = TECH AND created >= -3w AND ' \
        + 'created <= -1w', maxResults=200)
        if len(self.in2weeks) > len(self.in3weeks):
            self.trend = "up"
        else:
            self.trend = "down"

class FeatureParity:
    """ Query JIRA for information on Feature Parity """
    def __init__(self):
        self.todo = JQL.search_issues('labels = Feature_Parity AND resolution = unresolved ',
                                      maxResults=200)
        self.done = JQL.search_issues('labels = Feature_Parity AND resolution = fixed ',
                                      maxResults=500)

portalx = PortalX()
srweb = StarRezWeb()
cloud = Cloud()
techhelp = Techhelp()
featureparity = FeatureParity()


# Create Email Contents
print("Generating Email...")
with open('devupdate.html', 'r') as emailFormat:
    BODY = emailFormat.read().replace('\n', '')

BODY += "<p>Feature Parity: <a href=\"https://jira.starrez.com/issues/?filter=20417\">%s</a> pending, %s done</p>" % (len(featureparity.todo), len(featureparity.done))
BODY += "<p><br><b>Product Health</b><br>"
BODY += "SRWeb - <a href=\"https://jira.starrez.com/issues/?filter=19937\">%s</a> open bugs, <a href=\"https://jira.starrez.com/issues/?filter=24217\">%s</a> open Tech Debt issues<br>" % (len(srweb.bugs), len(srweb.techdebt))
BODY += "PortalX - <a href=\"https://jira.starrez.com/issues/?filter=20511\">%s</a> open bugs, <a href=\"https://jira.starrez.com/issues/?filter=24218\">%s</a> open Tech Debt issues<br>" % (len(portalx.bugs), len(portalx.techdebt))
BODY += "Cloud - <a href=\"https://jira.starrez.com/issues/?filter=23239\">%s</a> open bugs</p>" % len(cloud.bugs)

BODY += "<br><p>**Insert Bug Graph**</p><br>"

BODY += "<p><b>Techhelps</b> - %s jobs in the last two weeks, %s from %s at the last check<br>" \
        % (len(techhelp.in2weeks), techhelp.trend, len(techhelp.in3weeks))

BODY += "<br>**Insert Techhelp Chart**</p><br>"

BODY += "<p>Done in the last week:<br><ul>"
BODY += "<li>%s Bugs (<a href=\"https://jira.starrez.com/issues/?filter=22711\">%s " \
        % (len(portalx.closedbugs1w + srweb.closedbugs1w), len(portalx.closedbugs1w))
BODY += "PortalX</a> / <a href=\"https://jira.starrez.com/issues/?filter=22518)\">" \
        + "%s SRWeb</a>)</li>" % len(srweb.closedbugs1w)

for issue in portalx.enhancements:
    BODY += "<li><a href=\"https://jira.starrez.com/browse/%s\">%s</a> - %s</li>" \
    % (issue, issue, issue.fields.summary)
for issue in srweb.enhancements:
    BODY += "<li><a href=\"https://jira.starrez.com/browse/%s\">%s</a> - %s</li>" \
    % (issue, issue, issue.fields.summary)
for issue in cloud.enhancements:
    BODY += "<li><a href=\"https://jira.starrez.com/browse/%s\">%s</a> - %s</li>" \
    % (issue, issue, issue.fields.summary)
BODY += "</ul></p><p>Thanks,<br><br>Rafe<br></p></body></html>"


def createemail(emailbody):
    """ Sent Email Contents to Outlook """
    olmailitem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newmail = obj.CreateItem(olmailitem)
    today = datetime.date.today()
    newmail.Subject = today.strftime("Development Update - %d %b %Y")
    newmail.HTMLBody = emailbody
    newmail.display()

createemail(BODY)
