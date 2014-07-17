#!/usr/bin/env python
import string
import random
import cgi
import collections

print("Content-type:text/html\r\n\r\n")

form = cgi.FieldStorage()

#if "upload" in form:
#	uploaded_file = form.getfirst("upload")
#	list_version = uploaded_file.split("\n")

#if "serverfile" in form:
list_version = open("example_sampling_plan.cor")

colour_dict = dict()
name_dict = dict()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))


colour_options = ["aqua","blue","chartreuse","goldenrod","green","lightblue","lightgreen","lightgrey","orange","pink","purple","red","salmon","turquoise","violet","white","yellow"]

header_title_list = ["Hole Name","Core Length","Unsampled Length","Hole Depth","Sections per Core","Starting Depth","Starting Core Number"]
header_variable_list = ['hole_name','core_length','unsampled_length','hole_depth','sections_per_core','starting_depth','starting_core']
header_variable_dict = dict()
header_variable_lengths = [10,2,2,8,1,8,4]
header_variable_units = ['','m','m','m','','m','']

request_list = list()
name_list = list()
colour_list = list()
oneoff_sample_dict = dict()
request_counter = -1

for line in list_version:
	if line.startswith("hole_name"):
		header_variable_dict["hole_name"] = line.split("=")[1].split("\"")[1].strip(" \n\"")
	if line.startswith("core_length"):
		header_variable_dict["core_length"] = line.split("=")[1].strip(" \n")
	if line.startswith("unsampled_length"):
		header_variable_dict["unsampled_length"] = line.split("=")[1].strip(" \n")	
	if line.startswith("hole_depth"):
		header_variable_dict["hole_depth"] = line.split("=")[1].strip(" \n")
	if line.startswith("sections_per_core"):
		header_variable_dict["sections_per_core"] = line.split("=")[1].strip(" \n")
	if line.startswith("starting_depth"):
		header_variable_dict["starting_depth"] = line.split("=")[1].strip(" \n")
	if line.startswith("starting_core"):
		header_variable_dict["starting_core"] = line.split("=")[1].strip(" \n")
	if line.startswith("request"):
		request_list.append(line.split(" ")[1].split(":")[0])
		name_list.append(line.split(":")[1].strip("\" \n"))
		colour_list.append(line.split(":")[2].strip("\" \n"))
		request_counter = request_counter +1
		oneoff_sample_dict[request_counter] = list()
	if line.startswith('\"'):
		request_label = line.split('\"')[1]
		oneoff_sample_dict[request_counter].append(list())
		if "WRC" in request_label:
			WRC_width = request_label.split(" ")[0].strip("cm")
			oneoff_sample_dict[request_counter][-1].append(WRC_width)
			if "at" in line:
				WRC_depth = line.split("at")[1].strip(" ")
				oneoff_sample_dict[request_counter][-1].append(WRC_depth)
				
				notes = request_label.split(">")[1].strip(" \n")
				oneoff_sample_dict[request_counter][-1].append(notes)
			if "every" in line:
				interval = line.split("every")[1].split("from")[0].strip(" ")
				oneoff_sample_dict[request_counter][-1].append(interval)
				start_depth = line.split("from")[1].split("to")[0].strip(" ")
				oneoff_sample_dict[request_counter][-1].append(start_depth)
				stop_depth = line.split("to")[1].strip(" \n")
				oneoff_sample_dict[request_counter][-1].append(stop_depth)
				notes = request_label.split(">")[1].strip(" \n")
				oneoff_sample_dict[request_counter][-1].append(notes)

request_list.append("")
name_list.append("")
colour_list.append("")

				


print("<HTML><HEAD><TITLE>Corganiser: New Sampling Plan</TITLE></HEAD><BODY><H1>Corganiser: New Sampling Plan</H1><FORM action = \"./new_cor_file.py\" method=\"POST\"><TABLE width=600>")

for i in range(len(header_title_list)):
	print("<TR><TD width=150>" + header_title_list[i] + ":</TD>")
	print("<TD width=100><input size = " + str(header_variable_lengths[i]) +" type=\"text\" name=\"" + header_variable_list[i] + "\", value = \"" + header_variable_dict[header_variable_list[i]] + "\">" + header_variable_units[i] + "</TD>")
	if header_variable_list[i] == "hole_name":
			print("<TD rowspan=7><b>Tips:</b><ul><li>Specify depths of \"beginning\" or \"end\" to indicate the top and bottom of the hole.<li>Make sure both request number and name fields are filled before adding a new request or sample<li>To delete a sample or sample series, just empty all of its fields then hit \"Update\"<li>Trying to delete more than one request at once will result in an error.<li>The hole name cannot contain spaces.</ul>")
print("</TABLE><br>")

for i in range(0,len(request_list)):
	print("<TABLE style=\"border: 1px solid black;\"><TR><TD>Request Number: <input size=4 type=\"text\" name=\"" + str(i) + "\", value = \"" + request_list[i] + "\">&nbspRequest Name: <input type=\"text\" name=\"" + str(i)+"name" + "\", value = \"" + name_list[i] + "\">&nbspColour:<select name=\"" + str(i) + "colour\">")

	for colour in colour_options:
		print("<option = \"" + colour + "\"")
		if colour == colour_list[i]:
			print("selected = \"" + colour_list[i] +"\"")
		print(">" + colour + "</option>")

	print("</select></td>")
	if i in oneoff_sample_dict.keys():
		sample_counter = 0
		for oneoff_sample in oneoff_sample_dict[i]:
			if len(oneoff_sample) == 3:
				sample_counter = sample_counter + 1
				print("<TR><TD><input size=2 type=\"text\" name = \"request" + str(i) + "sample" + str(sample_counter) + "WRCwidth\", value = \"" + oneoff_sample_dict[i][sample_counter-1][0] + "\">cm WRC at <input size=4 type=\"text\" name = \"" + "request" + str(i) + "sample" + str(sample_counter) + "depth\", value = \"" + oneoff_sample_dict[i][sample_counter-1][1] + "\">m depth. Notes:<input type=\"text\" name = \"request" + str(i) + "sample" + str(sample_counter) + "notes\", value = \"" + oneoff_sample_dict[i][sample_counter-1][2] + "\"></TD>")
			if len(oneoff_sample) ==5:
				sample_counter = sample_counter + 1
				print("<TR><TD><input size=2 type=\"text\" name = \"request" + str(i) + "sample" + str(sample_counter) + "WRCwidth\", value = \"" + oneoff_sample_dict[i][sample_counter-1][0] + "\">cm WRC every <input size=2 type=\"text\" name = \"" + "request" + str(i) + "sample" + str(sample_counter) + "interval\", value = \"" + oneoff_sample_dict[i][sample_counter-1][1] + "\">m from <input size=4 type=\"text\" name = \"" + "request" + str(i) + "sample" + str(sample_counter) + "startdepth\", value = \"" + oneoff_sample_dict[i][sample_counter-1][2] + "\">m depth to <input size=4 type=\"text\" name = \"" + "request" + str(i) + "sample" + str(sample_counter) + "stopdepth\", value = \"" + oneoff_sample_dict[i][sample_counter-1][3] + "\">m depth. Notes:<input type=\"text\" name = \"request" + str(i) + "sample" + str(sample_counter) + "notes\", value = \"" + oneoff_sample_dict[i][sample_counter-1][4] + "\"></TD>")


	print("<TR><TD>Add samples to request:<select name = \"" + str(i) + "newsamples\" onchange=\"this.form.submit()\">\n<option value=\"\"></option>\n<option value=\"newsample\">new one-off sample</option><option value=\"newseries\">new sample series</option></select>")
	print("Move/Delete request:<select name = \"" + str(i) + "moverequest\" onchange=\"this.form.submit()\">\n<option value=\"\"></option>\n<option value=\"up\">move request up</option><option value=\"down\">move request down</option>\n<option value=\"delete\">delete request</option></select></TD>")
	print("</TABLE><br>")

print("<input type=\"submit\" value=\"Update\" name = \"update\">")
print("<input type=\"submit\" value=\"Generate Sampling Plan\" name = \"generate\">")
print("<input type=\"submit\" value=\"Clear Form\" name = \"clear\">")



print("</FORM></BODY></HTML>")


