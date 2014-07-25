#!/usr/bin/env python
print("Content-type: text/html")
import cgi
import string
import random
import os

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

#Set up all the variables to go into a a sampling plan 
colour_options = ["aqua","blue","chartreuse","goldenrod","green","lightblue","lightgreen","orange","pink","purple","red","salmon","turquoise","violet","yellow","white","whitesmoke","lightgrey","darkslategray","gainsboro","gray"]

header_title_list = ["Hole Name","Core Length","Unsampled Length","Hole Depth","Sections per Core","Starting Depth","Starting Core Number"]
header_variable_list = ['hole_name','core_length','unsampled_length','hole_depth','sections_per_core','starting_depth','starting_core']
header_variable_dict = dict()
header_variable_lengths = [10,2,2,8,1,8,4]
header_variable_units = ['','m','m','m','','m','']

skipped_sections_list = list()
skipped_cores_list = list()
request_list = list()
name_list = list()
colour_list = list()
oneoff_sample_dict = dict()
order_change_list = list()

#File input parsing

def process_input_file(function_input_file):
	request_counter = -1
	for line in function_input_file:
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
		if line.startswith("skip"):
			if len(line.split("=")[1]) > 2:
				skip_list = line.split("=")[1].strip(" \n").split(",")
				for skipped_section in skip_list:
					skipped_cores_list.append(skipped_section.split(":")[0].strip(" "))
					skipped_sections_list.append(skipped_section.split(":")[1].strip(" "))
			if len(skipped_sections_list) == 0:
				skipped_sections_list.append("")
				skipped_cores_list.append("")
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
	
	skipped_sections_list.append("")
	skipped_cores_list.append("")
	
	request_list.append("")
	name_list.append("")
	colour_list.append("")
	
form = cgi.FieldStorage()

if "upload" in form:
	uploaded_file = form.getfirst("upload")
	input_file = uploaded_file.split("\n")
	process_input_file(input_file)

if "serverfile" in form:
	input_file = open("output_files/" + form.getfirst("serverfile"))
	process_input_file(input_file)

#Process data input from form (CGI)

if "upload" not in form:
	if "serverfile" not in form:
		for variable in header_variable_list:
			header_variable_dict[variable] = form.getfirst(variable)
			if header_variable_dict[variable] == None or "clear" in form:
				header_variable_dict[variable] = ""
			header_variable_dict[variable] = cgi.escape(header_variable_dict[variable])

		for i in range(0,100):
			if form.getfirst("skipped_section"+str(i)) != None and "clear" not in form:
				skipped_sections_list.append(form.getfirst("skipped_section"+str(i)))
				skipped_cores_list.append(form.getfirst("skipped_core"+str(i)))
			else:
				skipped_sections_list.append("")
				skipped_cores_list.append("")
				break
		
		for i in range(0,100):
			if form.getfirst(str(i)) != None and "clear" not in form:
				request_list.append(form.getfirst(str(i)))
				name_list.append(form.getfirst(str(i)+"name"))
				colour_list.append(form.getfirst(str(i)+"colour"))
				oneoff_sample_dict[i] = list()
				for j in range(0,100):
					if form.getfirst("request" + str(i) + "sample" + str(j) + "WRCwidth") != None:
						if form.getfirst("request" + str(i) + "sample" + str(j) + "interval") == None:
							WRC_width = form.getfirst("request" + str(i) + "sample" + str(j) + "WRCwidth")
							WRC_depth = form.getfirst("request" + str(i) + "sample" + str(j) + "depth")
							notes = " ".join(form.getlist("request" + str(i) + "sample" + str(j) + "notes"))
							oneoff_sample_dict[i].append([WRC_width,WRC_depth,notes])
						if form.getfirst("request" + str(i) + "sample" + str(j) + "interval") != None:
							WRC_width = form.getfirst("request" + str(i) + "sample" + str(j) + "WRCwidth")
							interval = form.getfirst("request" + str(i) + "sample" + str(j) + "interval")
							start_depth = form.getfirst("request" + str(i) + "sample" + str(j) + "startdepth")
							stop_depth = form.getfirst("request" + str(i) + "sample" + str(j) + "stopdepth")
							notes = " ".join(form.getlist("request" + str(i) + "sample" + str(j) + "notes"))
							oneoff_sample_dict[i].append([WRC_width,interval,start_depth,stop_depth,notes])
				if form.getfirst(str(i)+"newsamples") == "newsample":
					oneoff_sample_dict[i].append(["","",""])
				if form.getfirst(str(i)+"newsamples") == "newseries":
					oneoff_sample_dict[i].append(["","","","",""])
				if form.getfirst(str(i) + "moverequest") == "up":
					if i != 0:
						order_change_list.append([i,i-1])
				lowest_position = len(request_list) - 1
				if form.getfirst(str(i) + "moverequest") == "down":
					order_change_list.append([i,i+1])
				if form.getfirst(str(i) + "moverequest") == "delete":
					order_change_list.append(i)
			else:
				request_list.append("")
				name_list.append("")
				colour_list.append("aqua")
				break

		for change in order_change_list:
			if isinstance(change, int):
				request_list.pop(change)
				name_list.pop(change)
				colour_list.pop(change)
				del oneoff_sample_dict[change]
				for i in oneoff_sample_dict:
					if i > change:
						oneoff_sample_dict[i-1] = oneoff_sample_dict[i]
						del oneoff_sample_dict[i]
			if isinstance(change, list):
				if change[1] != len(request_list)-1:
					request_list[change[0]],request_list[change[1]] = request_list[change[1]],request_list[change[0]]
					name_list[change[0]],name_list[change[1]] = name_list[change[1]],name_list[change[0]]
					colour_list[change[0]],colour_list[change[1]] = colour_list[change[1]],colour_list[change[0]]
					oneoff_sample_dict[change[0]],oneoff_sample_dict[change[1]] = oneoff_sample_dict[change[1]],oneoff_sample_dict[change[0]]

#HTML Output Section

if "generate" not in form:
	print("\n<HTML><HEAD><TITLE>Corganiser: New Sampling Plan</TITLE></HEAD><BODY><H1>Corganiser: New Sampling Plan</H1><FORM action = \"new_cor_file.py\" method=\"POST\"><TABLE width=600>")
	for i in range(len(header_title_list)):
		print("<TR><TD width=150>" + header_title_list[i] + ":</TD>")
		print("<TD width=100><input size = " + str(header_variable_lengths[i]) +" type=\"text\" name=\"" + header_variable_list[i] + "\", value = \"" + header_variable_dict[header_variable_list[i]] + "\">" + header_variable_units[i] + "</TD>")
		if header_variable_list[i] == "hole_name":
			print("<TD rowspan=7><b>Tips:</b><ul><li>Specify depths of \"beginning\" or \"end\" to indicate the top and bottom of the hole.<li>Make sure both request number and name fields are filled before adding a new request or sample<li>To delete a sample or sample series, just empty all of its fields then hit \"Update\"<li>Trying to delete more than one request at once will result in an error.<li>The hole name cannot contain spaces.</ul>")
	
	print("</TABLE><br><TABLE width=450 style=\"border: 1px solid black;\">")
	
	for skipped_section in enumerate(skipped_sections_list):
		print("<TR width=450><TD>Skip section <input type=\"text\" size=3 name=\"skipped_section" + str(skipped_section[0]) + "\" value=\"" + skipped_section[1] + "\"> core <input type=\"text\" size=3 name=\"skipped_core" + str(skipped_section[0]) + "\" value=\"" + skipped_cores_list[skipped_section[0]] + "\">")
	
	
	print("<br>To skip a given section in all cores enter \"all\" as the core number.</TABLE><br>")
		
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

if "generate" in form:
	filename = "output_files/" + header_variable_dict['hole_name'] + "_" + header_variable_dict['starting_core'] + "_" + id_generator() + ".cor"
	
	output_file = open(filename, "w")
	for header_variable in header_variable_list:
		if header_variable == "hole_name":
			output_file.write(header_variable + " = \"" + header_variable_dict[header_variable] + "\"\n")
		else:
			output_file.write(header_variable + " = " + header_variable_dict[header_variable] + "\n")
	
	output_file.write("skip = ")
	skip_string = str()
	
	for skipped_section in enumerate(skipped_sections_list):
		if skipped_section[1] != "":
			skip_string = skip_string + skipped_cores_list[skipped_section[0]] + ":" + skipped_section[1] + ", "
	
	output_file.write(skip_string.strip(", "))
	
	output_file.write("\n\nBegin Requests:\n\n")
	
	
	for i in range(0,len(request_list)-1):
		output_file.write("request " + request_list[i] + ": \"" + name_list[i] + "\" : \"" + colour_list[i] + "\"\n")
		for sample in oneoff_sample_dict[i]:
			if len(sample) == 3:
				sample_description = "\"" + sample[0] + "cm WRC -> " + sample[2] + "\" at " + sample[1] + "\n"
				output_file.write(sample_description)
			if len(sample) == 5:
				sample_description = "\"" + sample[0] + "cm WRC -> " + sample[4] + "\" every " + sample[1] + " from " + sample[2] + " to " + sample[3] + "\n"
				output_file.write(sample_description)
		output_file.write("\n")
	
	output_file.close()
	os.system("python corganiser_universal_6.py " + filename)
	
	short_filename = filename.split("/")[-1]
	
	
	print("<br>Sampling plan in PDF format: <A HREF=\"" + "/output_files/" + short_filename + ".pdf\">"+short_filename+".pdf</A>")
	print("<br>Sampling plan in tab-delimited text (tdt) format: <A HREF=\"" + "/output_files/" + short_filename + ".tdt\">"+short_filename+".tdt</A>")
	print("<br>Sampling plan in COR format (for future use by uploading back to this site or use in command line mode): <A HREF=\"" + "/output_files/" + short_filename + "\">"+short_filename+"</A>")
	print("<br><a href=\"new_cor_file.py?serverfile=" + short_filename + "\">Reload this sampling plan for editing.</a>")
	