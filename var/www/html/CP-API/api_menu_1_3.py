#!/usr/bin/env python
# Author: CB Currier
# Date: 11/19/2018
# Description: Dynamic loading and form generation of Exported CP Management API 

import os, sys, argparse, json, cgi, cgitb, urllib, string, requests, urllib 
os.sys.path.append(os.path.dirname(os.path.abspath('.')))
import auth

cgitb.enable()
# Required header that tells the browser how to render the HTML.
print "Content-Type: text/html\n\n"

# Define function to generate login HTML form.
def login_form():
    print "<HTML>\n"
    print "<HEAD>\n"
    print "\t<TITLE>Info Form</TITLE>\n"
    print "</HEAD>\n"
    print "<BODY BGCOLOR = white>\n"
    print "\t<H3>Please, enter your username and password.</H3>\n"
    print "\t<TABLE BORDER = 0>\n"
    print "\t\t<FORM METHOD = post ACTION = \"api_menu_1_3.py\">\n"
    print "\t\t<TR><TH>Server:</TH><TD><input type = text name = \"server\" value = \""+auth.server+"\"></TD><TR>\n"
    print "\t\t<TR><TH>Domain:</TH><TD><input type=text name = \"domain\" value=\"Default\"></TD><TR>\n"
    print "\t\t<tr><th>Username:</TH><TD><input type = text name = \"username\" value = \""+auth.muser+"\"></TD><TR>\n"
    print "\t\t<TR><TH>Password:</TH><TD><input type = password name = \"password\" value=\""+auth.mpass+"\"></TD></TR>\n"
    print "\t</TABLE>\n"
    print "\t<INPUT TYPE = hidden NAME = \"doaction\" VALUE = \"login\">\n"
    print "\t<INPUT TYPE = submit VALUE = \"Enter\">\n"
    print "\t</FORM>\n"
    print "</BODY>\n"
    print "</HTML>\n"

def api_call(ip_addr, port, command, json_payload, sid):
    url = 'https://' + ip_addr + ':' + port + '/web_api/' + command
    if sid == '':
        request_headers = {'Content-Type' : 'application/json'}
    else:
        request_headers = {'Content-Type' : 'application/json', 'X-chkp-sid' : sid}
    r = requests.post(url, data=json.dumps(json_payload), headers=request_headers, verify=False)
    return r.json()


def login(server, user, password, dmain):
    if (dmain != 'Default' ):
    	payload = {'user' : user, 'password' : password, 'domain' : dmain }
    else:
    	payload = {'user' : user, 'password' : password }

    response = api_call(server, '443', 'login', payload, '')
    return response["sid"]

def logout(server, sid, publish):
#def logout(server, sid):
    payload = {}
    if (publish=="publish"):
	api_call(server, '443', 'publish', payload, sid)
    else:
	api_call(server, '443', 'discard', payload, sid)

    response = api_call(server, '443', 'logout', payload, sid )
    return response["message"]

form = cgi.FieldStorage()
if (form.has_key("server")):
   server = form["server"].value

if (form.has_key("session_key")):
   session_key = form["session_key"].value
else:
   if (form.has_key("doaction") and form.has_key("username") and form.has_key("password")):
	if (form["doaction"].value == "login"):
     	  session_key = login(form["server"].value, form["username"].value, form["password"].value, form["domain"].value)		
   else:
        if (form.has_key("logout")):
	  if (form.has_key("old_session_key")):
	    if (form.has_key("pub")):
	      logout(form["server"].value, form["old_session_key"].value, form["pub"].value )
	    else:
  	      logout(form["server"].value, form["old_session_key"].value, '' )

filename = "Web_API_R80.20.postman_collection.json"
ohead = open("/var/www/html/include/cpheaderinc.html","r")
contents = ohead.read();
ohead.close()
print contents

try:
  session_key
except NameError:
  pass
else:
  treeml = """
	<div id='jstree'> 
	<ul>
"""
  print treeml
  j = 0;
  # Open JSON document
  with open(filename) as json_data:
    api_file = json.load(json_data)
    api_items = {}
    for prefix in api_file["item"]:
      item_name = prefix["name"]
      desc = prefix["description"]
    #     api_items[item] = {"api_item": item_name, "desc": desc}
      if j != 0:
	print "</ul>\n"
      print "<li>&nbsp;" + item_name[3:] + "\n"
      j=0
      for nextitem in prefix["item"]:
	j = j+1;
	aname = nextitem["name"]	
	if form.has_key("kitem"):
		if (form['kitem'].value == aname ):
			abody = json.loads(nextitem["request"]["body"]["raw"])
			adesc = nextitem["request"]["description"]
	if j == 1:
		print "<ul>"
	linq = urllib.urlencode({"kitem":aname,"session_key":session_key,"server":server})
	print "	<li>&nbsp;<span onClick=\"javascript:window.location.href='api_menu_1_3.py?%s'\">"% linq ,aname,"</span></li>"

    print """
	</ul>
  </div>
"""
print """
<script src='/web/vendor/jquery.1.12.1.min.js'></script>
  <!-- include the minified jstree source -->
<script src='/web/vendor/jstree.min.js'></script>
<script>
 $(function () {
    // create an instance when the DOM is ready
    $('#jstree').jstree();
    // bind to events triggered on the tree
    $('#jstree').on("changed.jstree", function (e, data) {
     console.log(data.selected);
   });
    // interact with the tree - either way is OK
     $('button').on('click', function () {
     $('#jstree').jstree(true).select_node('add_host');
     $('#jstree').jstree('select_node', 'add_host');
     $.jstree.reference('#jstree').select_node('add_host');
   });
 });
</script>
"""
pbod = open("/var/www/html/include/cpbodypanelincl.html","r")
panl = pbod.read();
pbod.close()
print panl
if (form.has_key("session_key")):
  if (form.has_key("logout")):
    logout(form["server"].value, form["session_key"].value)
    login_form()

try:
    session_key
except NameError:
    pass
    login_form()
else:
     print "You are logged in!\n"
     print "\t\t<form method = post action = \"api_menu_1_3.py\">\n"
     print "\t\t<INPUT TYPE = \"hidden\" NAME = \"server\" VALUE =", server, ">\n"
     print "\t\t<INPUT TYPE = \"hidden\" NAME = \"old_session_key\" VALUE =", session_key, ">\n"
     print "\t\t<INPUT TYPE = \"hidden\" NAME =\"logout\" VALUE = \"logout\" >\n"
     print "\t\t<INPUT TYPE = \"submit\" VALUE = \"Logout.\">\n"
     print "\t\t<INPUT TYPE=\"checkbox\" NAME=\"pub\" VALUE=\"publish\"><label for=\"pub\"><small>Session:Publish(<i>checked</i>)/Discard(<i>unchecked</i>)</small></label></form>\n"
     print "<div id=\"results\" class=\"nano\" style=\"height:500;width:700;overflow-y:scroll\">\n"
     print "<br><br>"

     if form.has_key("kitem"):
	if (form.has_key("exec")):
	  if (form["exec"].value == "Submit"):
	    #mload = []
	    xpayload = {}
	    #print xpayload
	    for key in form:
		if( key == "server" or key == "session_key" or key == "exec" or key == "kitem" ):
		  pass
		else:
		  if key in xpayload:
        	    xpayload[key].append(form[key].value)
    		  else:
        	    xpayload[key] = form[key].value
	    #print xpayload
	    xres = api_call(server, '443', form["kitem"].value , xpayload, session_key)
	    try:
		xres["message"]
	    except KeyError:
    	        if ( "show-packages" in form["kitem"].value ):
		  for obj in xres["packages"]:
		     print obj["name"],'-',obj["type"],'<br>\n'
    	        elif ( "show-threat-layers" in form["kitem"].value ):
		  for obj in xres["threat-layers"]:
		     print obj["name"],'-',obj["type"],'<br>\n'
	        elif ( "show-threat-protections" in form["kitem"].value ):
		  for obj in xres["protections"]:
		     print obj["name"],'-',obj["type"],'<br>\n'
	        elif ( "show-sessions" in form["kitem"].value ):
		   print 'Total Sessions:',xres["total"]
	  	   for obj in xres["objects"]:
 	             print '<table border=1><tr><td><b>Session:</b></td><td><b>',obj["user-name"],'</b></td></tr>\n<tr><td>Description:</td><td>',obj["description"]
		     print '</td></tr>\n<tr><td>Status:</td><td>',obj["state"],'</td></tr>\n<tr><td>ip-address:</td><td>',obj["ip-address"]
		     print '</td></tr>\n<tr><td>Login Time:</td><td>',obj["last-login-time"]["iso-8601"],'</td></tr>\n<tr><td>Session Expired:</td><td>',obj["expired-session"]
		     print '</td></tr>\n<tr><td>Application</td><td>',obj["application"],'</tr>\n<tr><td>Comments:</td><td>',obj["comments"],'</td></tr></table>\n'
	        elif ( "show-threat-indicators" in form["kitem"].value ):
		  for obj in xres["indicators"]:
		     print obj["name"],'-',obj["type"],'<br>\n'
    	        elif ( "show-host" in form["kitem"].value and not "show-hosts" in form["kitem"].value ):
		     print 'Host: ',xres["name"],'-',xres["ipv4-address"],'<br>\nColor:',xres["color"],'<br>\nComments:',xres["comments"]	
    	        elif ( "show-network" in form["kitem"].value and not "show-networks" in form["kitem"].value ):
		     print 'Network: ',xres["name"],'<br>\nColor:',xres["color"],'<br>\nComments:',xres["comments"]		
   	        elif ( "show-security-zone" in form["kitem"].value and not "show-security-zones" in form["kitem"].value ):
		     print 'Zone: ',xres["name"],'<br>\nColor:',xres["color"],'<br>\nComments:',xres["comments"]		
	        elif ( "show-ips-status" in form["kitem"].value ):
		     print 'Installed Version: ',xres["installed-version"],'<br>\nCreated:',xres["installed-version-creation-time"]["iso-8601"],'<br>\nUpdate Available:',xres["update-available"],'<br>\nLatest Version:',xres["latest-version"],'<br>\nLatest Creation Time: ',xres["latest-version-creation-time"]["iso-8601"]
	    	elif ( "show-application-site" in form["kitem"].value and not "show-application-sites" in form["kitem"].value):
		     print '<table><tr><td> Application Site: &nbsp;</td><td>',xres["name"],'</td></tr>\n<tr><td>Description:</td><td>',xres["description"],'</td></tr>\n<tr><td>Color:</td><td>',xres["color"],'</td></tr>\n<tr><td>Comments:</td><td>',xres["comments"],'</td></tr>\n<tr><td align=left colspan=2>Additional Categories:</td></tr>\n'
                     for addlcat in xres["additional-categories"]:
                       print '<tr><td>&nbsp</td><td>',addlcat,"</td></tr>\n"
		     print '</table>'
 	        elif ( "show" in form["kitem"].value ):
		  for obj in xres["objects"]:
		     print obj["name"],'-',obj["type"],'<br>\n'
		else:
		     print '<p><code>',json.dumps(xres,indent=4, sort_keys=True),'</code></p>'
	    else:
	        print '<p><code>',xres["message"],'</code></p>\n'
	else:
	  print """
	<form action=\"api_menu_1_3.py\" name=\"apicall\" method=\"post\">
	<table border=2 class=\"x-box-inner\" role=\"presentation\">
"""
	  print '<input type=hidden name=\"kitem\" value=\"%s\">\n' % form['kitem'].value
	  print '<br><h2>%s</h2><br><table>' % adesc
	  fieldsa = []
	  for a in abody:
	    t = str(abody[a.encode('ascii','ignore')])
##########################################
# code to add dropdown for details level #
##########################################
	    if ( "details-level" in a ):
	      print '<tr><td><div class=\"sources\">'
	      print '<b>',a,'</td><td><input name=\"%s\"' % a + ' placeholder=\"%s\" type=' % t
	      print '\"text\" list=\"details-level-list\" size=\"30\"><datalist id=\"details-level-list\" name=\"details-level-list\"><option value=\"standard\">standard</option><option value=\"full\">full</option><option value=\"uid\">uid</option></datalist></div></td></tr>'
	    else:
	      print '<tr><td><b>',a,'</td><td><input name=\"%s\"' % a + ' value=\"%s\"></td></tr>' % t
	    fieldsa.append(str(a))
	  
	  print "<tr><td colspan=2><input type=\"submit\" name=\"exec\" value=\"Submit\"></td></tr>\n</table>"
	  print "<input type=\"hidden\" name=\"server\" value=\"%s\">\n" % server
	  infields = ",".join(fieldsa)
     	  print "\t\t<INPUT TYPE = \"hidden\" NAME = \"session_key\" VALUE =\"%s\">\n</form>" % session_key
	

print '</div></div></body>'
print '</html>'
