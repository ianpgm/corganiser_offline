import collections
import sys
import math
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from decimal import Decimal

completed_requests = set()
previous_sample = ['empty','empty']
print("Content-type:text/html\r\n\r\n")
print("<HTML><HEAD><TITLE>Corganiser New .cor File</TITLE></HEAD><BODY><H1>Generating corganiser (.cor) file and resulting PDF...</H1>\n")



def error_check(sample):
	if sample[0] < -0.01 or sample[1] < -0.01:
		print("Error 1")
		print(sample)
		exit()

	if sample[0] > section_length + 0.01 or sample[1] > section_length + 0.01:
		print("Error 2")
		print(sample)
		exit()

def determine_request_number(current_core,current_section,depths_in_section):
	if len(core_dict[current_core][current_section]) == 0:
		return("null null")
	else:
		for WRC in core_dict[current_core][current_section]:
			if abs(core_dict[current_core][current_section][WRC][0] - depths_in_section[0]) < 0.01 and abs(core_dict[current_core][current_section][WRC][1] - depths_in_section[1]) < 0.01:
				return(WRC)
				break
		return("null null")

def determine_upper(core_to_det,section_to_det,width):
	upper_section_list = list()
	for WRC in core_dict[core_to_det][section_to_det]:
		upper_section_list.append((core_dict[core_to_det][section_to_det][WRC][0],core_dict[core_to_det][section_to_det][WRC][1]))
	
	sorted_upper_section_list = sorted(upper_section_list, key=lambda upper_depth: upper_depth[0])[::-1]
	
	if len(sorted_upper_section_list) == 0 or sorted_upper_section_list[0][1] < section_length - width:
		return([[section_length,section_length],"null null"])
	
	for i in range(0,len(sorted_upper_section_list)):
		if i == len(sorted_upper_section_list)-1:
			if sorted_upper_section_list[i][0] >= width:
				sampleID = determine_request_number(core_to_det,section_to_det,sorted_upper_section_list[i])
				return([sorted_upper_section_list[i],sampleID])
			else:
				print("Error - section full! Too many samples. Spread samples out more and try again.")
				exit()
			break
		if sorted_upper_section_list[i][0] - sorted_upper_section_list[i+1][1] >= width:
			sampleID = determine_request_number(core_to_det,section_to_det,sorted_upper_section_list[i])
			return([sorted_upper_section_list[i],sampleID])

def determine_lower(core_to_det,section_to_det,width):
	lower_section_list = list()
	if section_to_det == len(core_dict[core_to_det]) - 1:
		print("Error, attempting to retrieve lower samples from the bottom section")
	
	for WRC in core_dict[core_to_det][section_to_det+1]:
		lower_section_list.append((core_dict[core_to_det][section_to_det+1][WRC][0],core_dict[core_to_det][section_to_det+1][WRC][1]))

	sorted_lower_section_list = sorted(lower_section_list, key=lambda lower_depth: lower_depth[0])

	if len(sorted_lower_section_list) == 0 or sorted_lower_section_list[0][0] > width:
		return([[0,0],"null null"])

	for i in range(0,len(sorted_lower_section_list)):
		if i == len(sorted_lower_section_list)-1:
			if section_length - sorted_lower_section_list[i][1] >= width:
				sampleID = determine_request_number(core_to_det,section_to_det+1,sorted_lower_section_list[i])
				return([sorted_lower_section_list[i],sampleID])
			else:
				print("Error - section full! Too many samples. Spread samples out more and try again.")
				exit()
			break
		if sorted_lower_section_list[i+1][0] - sorted_lower_section_list[i][1] >= width:
			sampleID = determine_request_number(core_to_det,section_to_det+1,sorted_lower_section_list[i])
			return([sorted_lower_section_list[i],sampleID])
			

def placeWRC(width, depth,sampleID):
	print("Placing " + sampleID + " at a target depth of " + str(depth) + "m (true depth " + str(starting_depth + depth/correction_factor) + "m)<br>")
	hit_skipped_section = False
	for core in core_depth_dict:
		if depth > hole_depth or depth < 0:
			print("Error! Sample outside of hole's depth range: " + sampleID + "<br>")
			exit()
		if sampleID in completed_requests:
			continue
		#determine target core
		if (depth >= core_depth_dict[core][0] - 0.01 and depth <= core_depth_dict[core][1] + 0.01) or hit_skipped_section == True:
			#determine target section

#			for section_number in range(1,sections_per_core+1):
			depth_section_base_diff = section_length
			target_section = 0
			adjusted_due_to_skip = False
			for i in range(0,sections_per_core):
				section_base = core_depth_dict[core][0] + (i + 1) * section_length
				if abs(depth - section_base) < depth_section_base_diff or hit_skipped_section:
					depth_section_base_diff = abs(depth - section_base)
					target_section = i
					hit_skipped_section = False			
				if skip_dict[core][target_section] and interval > section_length:
					print(sampleID + " target section is on the skip list (core "+core+"section "+str(target_section)+"), skipping to next section.")
					hit_skipped_section = True
					adjusted_due_to_skip = True
					continue
			if target_section+1 == sections_per_core and skip_dict[core][target_section] and interval > section_length:
				print(sampleID + " target section is on the skip list (core "+core+"section "+str(target_section)+"), skipping to next core.")
				hit_skipped_section = True
				continue
			#if it's the last section in the core, it has to be upper, unless it was moved down there from a higher section.
			if target_section == sections_per_core-1 and adjusted_due_to_skip == False:
				print("A")
				target_segment = "upper"
				highest_upper_sample = determine_upper(core,target_section,width)[0][0]
				lowest_lower_sample = 0
			else:
				#if this is a sample that comes around every section, then it needs to be "upper" to match the lowest section in the core
				if interval <= section_length:
					print("B")
					target_segment = "upper"
					highest_upper_sample = determine_upper(core,target_section,width)[0][0]
				else:
					#Was this sample moved because of a skipped section? If so then it needs to be lower (relative to the higher section) to get it as close as possible to the desired section.
					if adjusted_due_to_skip:
						print("C")
						target_section = target_section - 1
						target_segment = "lower"
						lowest_lower_sample = determine_lower(core,target_section,width)[0][1]
					else:
						#determine whether the previous sample was at this section interface
						highest_upper_request_number = determine_upper(core,target_section,width)[1].split(" ")[0]
						lowest_lower_request_number = determine_lower(core,target_section,width)[1].split(" ")[0]
						if highest_upper_request_number == sampleID.split(" ")[0]:
							print("D")
							target_segment = "upper"
							highest_upper_sample = determine_upper(core,target_section,width)[0][0]
						else:
							if lowest_lower_request_number == sampleID.split(" ")[0]:
								print("E")
								target_segment = "lower"
								lowest_lower_sample = determine_lower(core,target_section,width)[0][1]
							else:
								#go through samples already placed at this interval and determine what the highest upper sample and lowest lower sample are along with their sample request numbers and depths
								print("F")
								highest_upper_sample = determine_upper(core,target_section,width)[0][0]
								lowest_lower_sample = determine_lower(core,target_section,width)[0][1]
								print(highest_upper_sample)
								print(lowest_lower_sample)
								if section_length - highest_upper_sample <= lowest_lower_sample:
									print("G")
									target_segment = "upper"
								else:
									print("H")
									target_segment = "lower"
 			
			if target_segment == "lower":
				core_dict[core][target_section+1][sampleID] = [lowest_lower_sample, lowest_lower_sample + width]
				print(sampleID + " placed in " + core + ", section " + str(target_section+2) + "<br>")
				error_check(core_dict[core][target_section+1][sampleID])
				return([request_number,'lower'])
			else:
				core_dict[core][target_section][sampleID] = [highest_upper_sample - width, highest_upper_sample]
				print(sampleID + " placed in " + core + ", section " + str(target_section+1) + "<br>")
				error_check(core_dict[core][target_section][sampleID])
				return([request_number,'upper'])
			completed_requests.add(sampleID)
	
colour_dict = dict()
name_dict = dict()
skip_list = list()

for line in open(sys.argv[1]):
	if line.startswith("hole_name"):
		hole_name = line.split("=")[1].split("\"")[1].strip(" \n\"")
	if line.startswith("core_length"):
		core_length = float(line.split("=")[1].strip(" \n"))	
	if line.startswith("unsampled_length"):
		unsampled_length = float(line.split("=")[1].strip(" \n"))	
	if line.startswith("hole_depth"):
		full_depth = float(line.split("=")[1].strip(" \n"))
	if line.startswith("sections_per_core"):
		sections_per_core = int(line.split("=")[1].strip(" \n"))
	if line.startswith("starting_depth"):
		starting_depth = float(line.split("=")[1].strip(" \n"))
	if line.startswith("starting_core"):
		starting_core = int(line.split("=")[1].strip(" \n"))
	
	if line.startswith("skip"):
		if len(line.split("=")[1]) > 2:
			skip_list = line.split("=")[1].strip(" \n").split(",")
			for item in enumerate(skip_list):
				skip_list[item[0]].strip(" ")
			
	
	if line.startswith("Begin Requests:"):
		correction_factor = core_length/(core_length + unsampled_length)
		hole_depth = (full_depth-starting_depth)*correction_factor
		core_dict = collections.OrderedDict()
		core_depth_dict = collections.OrderedDict()
		skip_dict = collections.OrderedDict()
		number_of_cores = int(hole_depth / core_length)
		number_of_sections = int(hole_depth / core_length) * sections_per_core
		section_length = float(core_length) / float(sections_per_core)
		if Decimal(str(hole_depth)) % Decimal(str(core_length)) > 0.1:
			print("Error! Hole depth must be a multiple of core length plus unsampled length.<br>")
			exit()
		else:
			for i in range(0, number_of_cores):
				top_of_core =  i * core_length
				base_of_core = i * core_length + core_length
				core_dict["core_" + str(i)] = list()
				core_depth_dict["core_" + str(i)] = [top_of_core,base_of_core]
				skip_dict["core_" + str(i)] = list()
				for j in range(0, sections_per_core):
					core_dict["core_" + str(i)].append(dict())
					skip_dict["core_" + str(i)].append(False)
		for skipped_section in skip_list:
			skip_core = skipped_section.split(":")[0].strip(" ")
			skip_section = skipped_section.split(":")[1].strip(" ")
			if skip_core == 'all':
				for core in skip_dict:
					skip_dict[core][int(skip_section)-1] = True
			else:
				skip_dict["core_" + str(int(skip_core)-1)][int(skip_section)-1] = True
		print("Creating hole " + hole_name + " with depth range " + str(starting_depth) + "m to " + str(full_depth) + "m, core length " + str(core_length) + "m, " + str(sections_per_core) + " sections per core, and " + str(unsampled_length) + "m unsampled depth in between cores. Starting core numbering at " + str(starting_core) + ".<br>" )
	if line.startswith("request"):
		interval = section_length + 1
		request_number = line.split(" ")[1].split(":")[0]
		request_name = line.split(":")[1].strip("\" \n")
		name_dict[request_number] = request_name
		request_colour = line.split(":")[2].strip("\" \n")
		colour_dict[request_number] = request_colour
	if line.startswith('\"'):
		request_label = line.split('\"')[1]
		if "WRC" in request_label:
			WRC_width = float(request_label.split(" ")[0].strip("cm")) / 100
			if "at" in line.split("\"")[2]:
				WRC_depth = float(line.split("\"")[2].split("at")[1].strip(" "))
				adjusted_depth = WRC_depth - starting_depth - WRC_depth*unsampled_length/core_length
				placeWRC(WRC_width,adjusted_depth,sampleID = request_number + " " + request_label + " " + str(WRC_depth))
			if "every" in line.split("\"")[2]:
				interval = float(line.split("\"")[2].split("every")[1].split("from")[0].strip(" "))
				if line.split("from")[1].split("to")[0].strip(" ") == "beginning":
					start_depth = 0
				else:
					start_depth = (float(line.split("from")[1].split("to")[0].strip(" ")) - starting_depth)*correction_factor
				if line.split("to")[1].strip(" \n") == "end":
					stop_depth = hole_depth
				else:
					stop_depth = (float(line.split("to")[1].strip(" \n")) - starting_depth)*correction_factor
				no_of_depths = int((stop_depth-start_depth)/interval)
				depth_list = list()
				for depth_number in range(1,no_of_depths+1):
					depth_list.append(start_depth+depth_number*interval)
				for depth in depth_list:
					placeWRC(WRC_width,depth,sampleID = request_number + " " + request_label + " " + str(depth))

def draw_short_cores():
	section_height_on_page = float(25 - sections_per_core) / float(sections_per_core)
	c = canvas.Canvas(sys.argv[1] + ".pdf")

	for core in core_dict:
		label_dict = dict()
		section_counter = 0
		print("creating sheet for " + core + "<br>")
		core_number = int(core.split("_")[1])
		c.setFont("Helvetica-Bold", 30)
		c.drawString(7*cm, 27.5*cm, "Core " + str(starting_core + core_number))
		c.drawString(7*cm, 26.5*cm, hole_name + ": " + str(float(starting_depth + core_depth_dict[core][0] + float(core_number)*unsampled_length)) + "m - " + str(float(starting_depth + core_depth_dict[core][1] + float(core_number+1)*unsampled_length)) + "m")
#		c.drawString(8*cm, 26.5*cm, hole_name + ": " + str(core_depth_dict[core][0]) + "m - " + str(core_depth_dict[core][1]) + "m")
		
		c.setFont("Helvetica", 10)
		c.drawString(4.1*cm, 28.1*cm, "TOP")
		c.drawString(3.7*cm, 3.5*cm, "BOTTOM")	
		section_counter = 0
		c.setFillColor('white')
		for section in core_dict[core]:
			start_point = 28-(section_counter+1)*section_height_on_page - section_counter
			c.rect(3*cm,start_point*cm,3*cm,section_height_on_page*cm, fill=0)
			c.line(2.8*cm,start_point*cm,2.8*cm,(start_point+section_height_on_page)*cm)
			c.rotate(90)
			c.setFillColor('black')
			c.setFont("Helvetica", 10)
			c.drawString((start_point+(1.3*section_height_on_page/3))*cm, -1.5*cm, "SECTION " + str(section_counter +1))
			c.rotate(-90)
			fivecm_notch_interval = int((section_length / 0.05)) + 1
			fivecm_notch_level = start_point
			for i in range(fivecm_notch_interval):
				fivecm_notch_level = start_point+i*section_height_on_page *(0.05 / section_length)
				c.line(2.8*cm,fivecm_notch_level*cm,2.6*cm,fivecm_notch_level*cm)
			twentyfivecm_notch_interval = int((section_length / 0.25)) + 1
			twentyfivecm_notch_level = start_point
			for i in range(twentyfivecm_notch_interval):
				twentyfivecm_notch_level = start_point+i*section_height_on_page *(0.25 / section_length)
				c.line(2.8*cm,twentyfivecm_notch_level*cm,2.4*cm,twentyfivecm_notch_level*cm)
				interval_name = section_length - 0.25*i
				c.setFont("Helvetica", 8)
				c.setFillColor('black')
				c.drawString(1.8*cm, (twentyfivecm_notch_level-0.1)*cm, str(int(100*interval_name)))
		
			for WRC in section:
				request_number = WRC.split(" ")[0]
				if request_number not in label_dict.keys():
					label_dict[request_number] = list()
				upper_limit = start_point + section_height_on_page *(1- section[WRC][0] / section_length)
				lower_limit = start_point + section_height_on_page *(1- section[WRC][1] / section_length)
				c.setFillColor(colour_dict[request_number])
				c.rect(3*cm,lower_limit*cm,3*cm,(upper_limit - lower_limit)*cm, fill=1)
				c.setFillColor('black')
				c.setFont("Helvetica", 8)
				c.drawString(4.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, request_number)
				descriptor = (WRC.split(" ")[1] + WRC.split(">")[1])
				descriptor_stripped = str()
				for word in descriptor.split(" ")[:len(descriptor.split(" "))-1]:
					descriptor_stripped = descriptor_stripped + " " + word
				c.drawString(6.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, descriptor_stripped)
#				c.drawString(6.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, descriptor)
				c.setFont("Helvetica-Oblique", 7)
				c.drawString(3.05*cm, (upper_limit-0.25)*cm, str(100*section[WRC][0]))
				c.setFont("Helvetica", 8)
			section_counter = section_counter + 1
			label_counter = 0
			for request_number in label_dict:
				box_height = 0.5
				start_point = (26 - 0.5*label_counter - box_height)
				c.setFillColor(colour_dict[request_number])
				c.rect(12*cm,(start_point-0.1)*cm,8*cm,(box_height)*cm, fill=1)
				c.setFont("Helvetica", 12)
				c.setFillColor('black')
				c.drawString(12.1*cm, (start_point+box_height-0.5)*cm, request_number + " " + name_dict[request_number])
				label_start_point = start_point+box_height-1
				label_counter = label_counter + 1.5
	
		c.showPage()

	c.save()

def draw_long_cores():
	section_height_on_page = 8
	c = canvas.Canvas(sys.argv[1] + ".pdf")	
	pages_per_core = int(math.ceil(float(sections_per_core) / 3.0))
	print(str(pages_per_core) + "<br>")
	
	for core in core_dict:
	
		for page in range(1,pages_per_core+1):
			label_dict = dict()	
			print("Creating sheet for " + core + "<br>")
			core_number = int(core.split("_")[1])
			c.setFont("Helvetica-Bold", 20)
			c.drawString(12*cm, 27.5*cm, "Core " + str(starting_core + core_number) + ", sections " + str(3*page-2) + "-" + str(3*page))
			c.drawString(12*cm, 26.5*cm, hole_name + ": " + str(float(starting_depth + core_depth_dict[core][0] + float(core_number)*unsampled_length)) + "m - " + str(float(starting_depth + core_depth_dict[core][1] + float(core_number+1)*unsampled_length)) + "m")
			c.setFont("Helvetica", 10)
			c.drawString(4.1*cm, 28.1*cm, "TOP")
			c.drawString(3.7*cm, 1.5*cm, "BOTTOM")	
			section_counter = 0
			c.setFillColor('white')
			for section in core_dict[core][3*page-3:3*page]:
				print("section counter " + str(section_counter) + "<br>")
				start_point = 28-(section_counter+1)*section_height_on_page - section_counter
				c.rect(3*cm,start_point*cm,3*cm,section_height_on_page*cm, fill=0)
				c.line(2.8*cm,start_point*cm,2.8*cm,(start_point+section_height_on_page)*cm)
				c.rotate(90)
				c.setFillColor('black')
				c.setFont("Helvetica", 10)
				c.drawString((start_point+(1.3*section_height_on_page/3))*cm, -1.5*cm, "SECTION " + str(section_counter +1 + (page-1)*3))
				c.rotate(-90)
				fivecm_notch_interval = int((section_length / 0.05)) + 1
				fivecm_notch_level = start_point
				for i in range(fivecm_notch_interval):
					fivecm_notch_level = start_point+i*section_height_on_page *(0.05 / section_length)
					c.line(2.8*cm,fivecm_notch_level*cm,2.6*cm,fivecm_notch_level*cm)
				twentyfivecm_notch_interval = int((section_length / 0.25)) + 1
				twentyfivecm_notch_level = start_point
				for i in range(twentyfivecm_notch_interval):
					twentyfivecm_notch_level = start_point+i*section_height_on_page *(0.25 / section_length)
					c.line(2.8*cm,twentyfivecm_notch_level*cm,2.4*cm,twentyfivecm_notch_level*cm)
					interval_name = section_length - 0.25*i
					c.setFont("Helvetica", 8)
					c.setFillColor('black')
					c.drawString(1.8*cm, (twentyfivecm_notch_level-0.1)*cm, str(int(100*interval_name)))
		
				for WRC in section:
					request_number = WRC.split(" ")[0]
					if request_number not in label_dict.keys():
						label_dict[request_number] = list()
					upper_limit = start_point + section_height_on_page *(1- section[WRC][0] / section_length)
					lower_limit = start_point + section_height_on_page *(1- section[WRC][1] / section_length)
					c.setFillColor(colour_dict[request_number])
					c.rect(3*cm,lower_limit*cm,3*cm,(upper_limit - lower_limit)*cm, fill=1)
					c.setFillColor('black')
					c.setFont("Helvetica", 8)
					c.drawString(4.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, request_number)
					descriptor = (WRC.split(" ")[1] + WRC.split(">")[1])
					descriptor_stripped = str()
					for word in descriptor.split(" ")[:len(descriptor.split(" "))-1]:
						descriptor_stripped = descriptor_stripped + " " + word
					c.drawString(6.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, descriptor_stripped)
#					c.drawString(6.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, descriptor)
					label_counter = 0
				for request_number in label_dict:
					box_height = 0.5
					start_point = (26 - 0.5*label_counter - box_height)
					c.setFillColor(colour_dict[request_number])
					c.rect(12*cm,(start_point-0.1)*cm,8*cm,(box_height)*cm, fill=1)
					c.setFont("Helvetica", 12)
					c.setFillColor('black')
					c.drawString(12.1*cm, (start_point+box_height-0.5)*cm, request_number + " " + name_dict[request_number])
					label_start_point = start_point+box_height-1
					label_counter = label_counter + 1.5
				section_counter = section_counter + 1
			c.showPage()

	c.save()


def tdt_output():
	tdt_output_file = open(sys.argv[1] + ".tdt", "w")
	tdt_output_file.write("Core\tCore_upper_depth\tCore_lower_depth\tSection\tSample_ID\tWRC_upper_depth_in_section\tWRC_lower_depth_in_section\n")
	for core in core_dict:
		core_number = int(core.split("_")[1])
		str_core_number = str(starting_core + core_number)
		for section in enumerate(core_dict[core]):
			for WRC in section[1]:
				tdt_output_file.write(str_core_number + "\t" + str(float(starting_depth + core_depth_dict[core][0] + float(core_number)*unsampled_length)) + "\t" + str(float(starting_depth + core_depth_dict[core][1] + float(core_number+1)*unsampled_length)) + "\t" + str(section[0]+1) + "\t\'" + WRC + '\'\t' + str(section[1][WRC][0]) + '\t' + str(section[1][WRC][1]) + "\n")

if(sections_per_core <= 3):
	draw_short_cores()
else:
	draw_long_cores()

tdt_output()
								