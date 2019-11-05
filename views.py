from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
import json
from django.db import transaction
import sys, os
from labsauth.models import *

def dblog(message):
	el = errorlog()
	
	try:
		el.error = json.dumps(message)
	except:
		el.error = str(message)
	el.save()
# Create your views here.
class RoomViewSet(viewsets.ModelViewSet):
	queryset = room.objects.all()
	serializer_class = RoomSerializer
	filter_backends = [filters.SearchFilter ,DjangoFilterBackend]
	filterset_fields = ['project__number',]
	search_fields = ('data_text',)

class RoomTypeViewSet(viewsets.ModelViewSet):
	queryset = room_type.objects.all()
	serializer_class = RoomTypeSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('project__number',)

class DoorViewSet(viewsets.ModelViewSet):
	queryset = door.objects.all()
	serializer_class = DoorSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('project__number',)

@csrf_exempt
def room_bulkcou(request):
	log = []
	if request.method == "POST":
		try:
			# dblog(request.POST)
			data = request.POST["data"]
			bulktype = ""
			try:
				# bulktype = request.POST["bulktype"]
				pass
			except: pass
			log.append(bulktype)
			jd = json.loads(data)
			out = {"out": "working", "log":log}
			createdcount = 0
			for modeldict in jd:
				try:
					modeldict['project_number']
				except:
					# dblog(modeldict)
					elidspl = modeldict['element_id'].split("|")
					modeldict['project_number'] = elidspl[0]
					modeldict['element_id'] = elidspl[1]
				try:
					try:
						modeldict['project_number']
						exist = get_object_or_404(room, element_id=str(modeldict['project_number'])+"|"+str(modeldict['element_id']))
					except:
						exist = get_object_or_404(room, element_id=modeldict['element_id'])
					existdata = exist.unique_data()
					existdata.update(modeldict['data'])
					modeldict['data_text'] = json.dumps(existdata)
				except:
					modeldict['data_text'] = json.dumps(modeldict['data'])
					pass
				# modeldict['A'] = str(type(modeldict['project_number']))
				pro = get_object_or_404(project, number=str(modeldict['project_number']))
				modeldict['project'] = pro
				modeldict['element_id'] = str(modeldict['project_number'])+"|"+str(modeldict['element_id'])
				try:
					modeldict['room_type_name']
					try:
						modeldict['room_type'] = get_object_or_404(room_type, project=modeldict['project'] ,type_name=str(modeldict['room_type_name']))
						log.append(str(modeldict['room_type']))
					except:
						log.append("NO ROOM TYPE")
						modeldict['room_type'] = get_object_or_404(room_type, project=modeldict['project'], type_name="-")
				except:
					pass
				try:
					del modeldict['data']
					del modeldict['project_number']
					del modeldict['room_type_name']
				except:
					pass
				elid = modeldict['element_id']
				del modeldict['element_id']
				log.append(elid)
				mod, created = room.objects.update_or_create(element_id=elid, defaults=modeldict)
				if created:
					createdcount += 0
			log.append("created: "+str(createdcount))

			if bulktype == "deleteunused":
				log.append("gonna delete!")
				roomids = []
				jd = json.loads(data)
				for postRoom in jd:
					roomids.append(str(postRoom['project_number'])+"|"+str(postRoom['element_id']))
				log.append("don't delete:")
				log.append(roomids)
				pro = get_object_or_404(project, number=str(jd[0]['project_number']))
				try: allrooms = room.objects.filter(project=pro, source_file= jd[0].source_file)
				except: allrooms = []
				deleted = 0
				log.append("checked:")
				for delroom in allrooms:
					log.append(delroom.element_id)
					#log.append(delroom.element_id not in roomids)
					if delroom.element_id not in roomids:
						log.append(delroom.element_id)
						deleted += 1
						delroom.delete()
				log.append("deleted: "+str(deleted))


		
			return JsonResponse(out)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			other = sys.exc_info()[0].__name__
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			errorType = str(exc_type)
			return JsonResponse({"isError": True, "error":str(e), "errorType":errorType, "function":fname, "line":exc_tb.tb_lineno, "log":log})

	else:
		return HttpResponse("ONLY POST REQUESTS")

@csrf_exempt
def room_types_bulkcou(request):
	log = []
	if request.method == "POST":
		try:
			data = request.POST["data"]
			jd = json.loads(data)
			log.append(jd)
			out = {"out": "working"}
			for modeldict in jd:
				try:
					exist = get_object_or_404(room_type, id=modeldict['id'])
					existdata = exist.data()
					existdata.update(modeldict['data'])
					modeldict['data_text'] = json.dumps(existdata)
				except:
					modeldict['data_text'] = json.dumps(modeldict['data'])
					pass
				try:
					projectid = get_object_or_404(project, id=modeldict['project'])
					modeldict['project'] = projectid
				except: pass
				deletekeys = ['data','project_number']
				for key in deletekeys:
					try: del modeldict[key]
					except: pass
				log.append(modeldict)
				if modeldict['id']=='': del modeldict['id']
				try: mod, created = room_type.objects.update_or_create(id=modeldict['id'], defaults=modeldict)
				except:
					m = room_type(**modeldict)
					m.save()


		
			return JsonResponse(out)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			other = sys.exc_info()[0].__name__
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			errorType = str(exc_type)
			return JsonResponse({"isError": True, "error":str(e), "errorType":errorType, "function":fname, "line":exc_tb.tb_lineno, "log":log})

	else:
		return HttpResponse("ONLY POST REQUESTS")


@csrf_exempt
def door_bulkcou(request):
	log = []
	if request.method == "POST":
		try:
			# log.append(request.POST)
			data = request.POST["data"]
			jd = json.loads(data)
			
			with transaction.atomic():
				for modeldict in jd:

					###########################################################################################################################################################

					try:
						modeldict['project_number']
					except:
						elidspl = modeldict['element_id'].split("|")
						modeldict['project_number'] = elidspl[0]

					try:
						try:
							modeldict['project_number']
							exist = get_object_or_404(door, element_id=str(modeldict['element_id']))
						except:
							exist = get_object_or_404(door, element_id=modeldict['element_id'])
						existdata = exist.unique_data()
						existdata.update(modeldict['data'])
						modeldict['data_text'] = json.dumps(existdata)
					except:
						modeldict['data_text'] = json.dumps(modeldict['data'])
						pass

					###########################################################################################################################################################

					pro = get_object_or_404(project, number=str(modeldict['project_number']))
					modeldict['project'] = pro
					# modeldict['data_text'] = json.dumps(modeldict['data'])
					
					try:
						# log.append(modeldict['from_room_id'])
						fromroomob = get_object_or_404(room, element_id=modeldict['from_room_id'])
						log.append("FROM_ROOM-------------")
						log.append(str(fromroomob))
						modeldict['from_room'] = fromroomob
					except:
						# log.append("No to_room")
						pass
					try:
						# log.append(modeldict['to_room_id'])
						toroomob = get_object_or_404(room, element_id=modeldict['to_room_id'])
						# log.append(str(toroomob))
						modeldict['to_room'] = toroomob
					except:
						# log.append("No to_room")
						pass

					#####
					deletekeys = ['data','project_number','from_room_id','to_room_id']
					for key in deletekeys:
						try:
							del modeldict[key]
						except: pass

					try:
						mod, created = door.objects.update_or_create(element_id=modeldict['element_id'], defaults=modeldict)
						log.append(created)
					except Exception as e:
						log.append(str(e))
						pass
			out = {"out": "working" , "log": log}
			return JsonResponse(out)
		except Exception as e:
			out = {"out": str(e) , "log": log}
			return JsonResponse(out)

	else:
		return HttpResponse("DOORS - ONLY POST REQUESTS")

@csrf_exempt
def element_bulkcou(request):
	if request.method == "POST":
		try:
			data = request.POST["data"]
			jd = json.loads(data)
			out = {"out": "working"}
			for modeldict in jd:

				pro = get_object_or_404(project, number=str(modeldict['project_number']))
				modeldict['project'] = pro
				modeldict['data_text'] = json.dumps(modeldict['data'])
				#####
				deletekeys = ['data','project_number']
				for key in deletekeys:
					try: del modeldict[key]
					except: pass

				mod, created = element.objects.update_or_create(element_id=modeldict['element_id'], defaults=modeldict)

		
			return JsonResponse(out)
		except Exception as e:
			return HttpResponse(str(e))

	else:
		return HttpResponse("ONLY POST REQUESTS")


@transaction.atomic
def doortable(request, projectno):
	
	pro = get_object_or_404(project, number=str(projectno))
	rooms = room.objects.filter(project = pro).order_by("number_store")
	rooms = list(filter(lambda x: len(x.doors.all())>0, rooms))
	print(len(rooms))
	tree = []
	for r in rooms:
		print(r)
		apob = {}
		apob['room_name'] = r.room_name
		apob['data'] = r.data()
		apob['doors'] = []
		for d in r.doors.all():
			doorob = {}
			doorob['from_room'] = d.from_room
			doorob['to_room'] = d.to_room
			doorob['data'] = d.data()
			
			###
			j = doorob["data"]
			edata = ["DoorPanelHeight_ANZRS","DoorPanelWidth_ANZRS","DoorPanelDepth_ANZRS","DoorPanelBWidth_ANZRS","DoorFrameHeight","DoorFrameWidth"]
			for ed in edata:
				try:
					j[ed]
					if j[ed] == '': j[ed] = 0
				except: j[ed] = 0
			if j['DoorPanelBWidth_ANZRS'] != 0:
				if int(float(j['DoorPanelWidth_ANZRS'])) == int(float(j['DoorPanelBWidth_ANZRS'])):
					j['leaf'] = "%sx%s(2)" %(
						int(float(j["DoorPanelHeight_ANZRS"])),
						int(float(j["DoorPanelWidth_ANZRS"])))
				else:
					j['leaf'] = "%sx%s/%s" %(
						int(float(j["DoorPanelHeight_ANZRS"])),
						int(float(j["DoorPanelWidth_ANZRS"])),
						int(float(j["DoorPanelBWidth_ANZRS"])))
			else:
				j['leaf'] = "%sx%s" %(
					int(float(j["DoorPanelHeight_ANZRS"])),
					int(float(j["DoorPanelWidth_ANZRS"])))				
			j['frame'] = "%sx%s" %(
				int(float(j["DoorFrameHeight"])),
				int(float(j["DoorFrameWidth"])))

			###
			for k in j:
				if j[k] == "CHECK":
					j[k] = "TBC"
				if j[k] == "" and j["DoorHardware_Signage"] == "":
					j[k] = "TBC"
			if j['frame'] == "0x0":
				j['frame'] = "Frameless"
				j['Door_Frame_Type'] = ""
			if j['leaf'] == "0x0":
				j['leaf'] = "Leafless"
				l = ['DoorHardware_Seal','DoorHardware_Keying','DoorHardware_DoorStop','DoorHardware_Closer','DoorHardware_Hinge','DoorHardware_Handle', 'Door_Leaf_Type', 'DoorHardware_Signage']
				for o in l:
					j[o]=""
			apob['doors'].append(doorob)

		tree.append(apob)
	# tree = [tree[0],tree[100],tree[500]]
	# for r in rooms:
	# 	for d in r.doors.all():
	# 		d.save()
	context = { "context": tree }
	return render(request, "doors/door_ind.html", context)

@transaction.atomic
def doortemp(request, projectno):
	pro = get_object_or_404(project, number=projectno )
	doors = door.objects.filter(project = pro,
		# element_id="217102.00|6182177"
		)

	log = []

	for item in doors:
		item.save()
		try:
			print(item.data()["Mark"])
			# log.append(str(item.data()))
			log.append(str(item.elid()))
		except: pass
	return JsonResponse({"log":log})


@transaction.atomic
def roomtemp(request, projectno):
	pro = get_object_or_404(project, number=projectno )
	rooms = room.objects.filter(project = pro,
		# element_id="217102.00|6182177"
		)

	log = []

	for item in rooms:
		item.save()
		try:
			print(item.data()["Number"])
			log.append(str(item.elid()))
		except: pass
	return JsonResponse({"log":log})


def createIndesignSchedule(request, projectno, spacename):
	from jinja2 import Template
	from jinja2 import Environment
	from jinja2 import FileSystemLoader
	import shutil
	import os
	from PIL import Image
	import time
	log = []
	try:
		# dbfile = self.csv
		# print(self.csv)
		dir_path = os.path.dirname(os.path.realpath(__file__))
		apath = dir_path
		dir_path = dir_path.split("\\")
		dir_path = dir_path[:-2]
		fpath = dir_path
		fpath.append("media")
		mpath = fpath
		mpath = "\\".join(mpath)
		# log.append(apath)
		env = Environment(loader=FileSystemLoader(apath+'\jinjatemplates'),trim_blocks=True)
		pro = get_object_or_404(project, number = projectno )
		instance = get_object_or_404(space, project = pro,space_name = spacename )
		# log.append(str(instance))
		reader = []
		try:
			shutil.rmtree(apath+'\\temp\\schedules\\Furniture Schedule\\Images\\')
			os.mkdir(apath+'\\temp\\schedules\\Furniture Schedule\\Images')
		except: pass
		columnwidths = 2.8345880264212084291989123614307
		for i in instance.elements.all():
			apob = {
			"INCLUDE" : True,
			"CODE" : i.element.code,
			"DESCRIPTION" : i.element.element.description,
			"QUANTITY" : i.quantity,
			"DIMENSIONS" : i.element.element.dimensions,
			# "IMAGEDIR" : dir(i.element.element.image),
			"ADDRESS" : i.element.element.image.path,
			"COMMENTS" : i.element.element.comments,
			"SUPPLIER" : i.element.element.supplier.full(),
			}
			reader.append(apob)
		rows = []
		for row in reader:
			o = {}
			for item in row:
				if row[item] != "":
					try: o[item] = row[item].replace("\r\n","\n")
					except: o[item] = row[item]

			try:
				img = Image.open(o['ADDRESS'])
				img.save(apath+'\\temp\\schedules\\Furniture Schedule\\Images\\'+o['CODE']+'.png')
				o['ADDRESS'] = "\\Images\\"+o['CODE']+'.png'
				size = img.size
				log.append(size)
				# print(size)
				o['ratio'] = 0.5*size[1]/size[0]
			except:
				# if 'ADDRESS' in o: del o['ADDRESS']
				o['ratio'] = 1
			try:
				o['CODE']
			except:
				o['CODE']= "ZZ99"
			# print(o)
			try:
				if o["INCLUDE"]:
					rows.append(o)
			except:
				pass
		# log.append(rows)
		####STORY#####
		template = env.get_template('story_template.xml',)
		m = (template.render(d=rows))
		# log.append(m)
		file = open(apath+r'\temp\schedules\Furniture Schedule\Schedule\Stories\Story_ue2.xml','w', encoding="utf-8")
		file.write(m)
		file.close()
		
		####SPREADS#####
		spreads = range(1,int(len(rows)/4)+1)
		spreadIDS = []
		for spread in spreads:
			currentindex = spreads.index(spread)
			spreadOb = {
			"id": "%02d" % (spread,),
			"spreadID": "us%02d" % (spread,),
			"textFrameID":"ut%02d" % (spread,),
			"prevTextFrameID":"ut%02d" % (currentindex,),
			"nextTextFrameID":"ut%02d" % (currentindex+2,),
			}

			if currentindex == 0:
				spreadOb["prevTextFrameID"] = "n"
			if currentindex == len(spreads)-1:
				spreadOb["nextTextFrameID"] = "n"
			spreadIDS.append(spreadOb)
			template = env.get_template('spread_template.xml',)
			m = (template.render(d=spreadOb))
			filepath = r'\temp\schedules\Furniture Schedule\Schedule\Spreads\Spread_%s.xml' %(spreadOb["spreadID"])
			file = open(apath+filepath,'w', encoding="utf-8")
			file.write(m)
			file.close()

		####DES MAP####
		template = env.get_template('designmap_template.xml',)
		m = (template.render(d=spreadIDS))
		filepath = r'\temp\schedules\Furniture Schedule\Schedule\designmap.xml'
		file = open(apath+filepath,'w', encoding="utf-8")
		file.write(m)
		file.close()







		idmlname = spacename
		try: os.remove(apath+'\\temp\\schedules\\Furniture Schedule\\'+"Schedule"+".idml")
		except: pass
		shutil.make_archive(apath+'\\temp\\schedules\\Furniture Schedule\\'+"Schedule", 'zip', apath+'\\temp\\schedules\\Furniture Schedule\\Schedule')
		os.rename(apath+'\\temp\\schedules\\Furniture Schedule\\'+"Schedule"+".zip", apath+'\\temp\\schedules\\Furniture Schedule\\'+"Schedule"+".idml")
		try:
			os.remove(mpath+"\\schedules\\"+idmlname+".zip")
		except:
			pass
		shutil.make_archive(mpath+"\\schedules\\"+idmlname, 'zip', apath+'\\temp\\schedules\\Furniture Schedule')
		# return JsonResponse({"log":log})
		context = {"idml": idmlname+".zip", "log":json.dumps(log)}
		time.sleep( 2 )
		return render(request, "muninn/schedule_download.html", context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		other = sys.exc_info()[0].__name__
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		errorType = str(exc_type)
		return JsonResponse({"isError": True, "error":str(e), "errorType":errorType, "function":fname, "line":exc_tb.tb_lineno, "log":log})

def emilytemp(request):
	log = []
	try:
		r = room.objects.all()[0]
		log.append(str(r))
		els = []
		from_els = r.from_door.all()
		to_els = r.to_door.all()
		for e in from_els:
			els.append(e)
		for e in to_els:
			els.append(e)
		
		for e in els:
			log.append(e.element_id)
		return JsonResponse({"log":log})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		other = sys.exc_info()[0].__name__
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		errorType = str(exc_type)
		return JsonResponse({"isError": True, "error":str(e), "errorType":errorType, "function":fname, "line":exc_tb.tb_lineno, "log":log})
	
def temp(request):
	log = []
	# import csv
	# file = 'C:\\Temp\\USYD.tsv'
	# data = []
	# with open(file) as fh:
	# 	rd = csv.DictReader(fh, delimiter='\t') 
	# 	for row in rd:
	# 		data.append(row)
	# selectproj = project.objects.get(number="215132.00")
	# for rt in data:
	# 	newrt = room_type()
	# 	newrt.project = selectproj
	# 	newrt.type_name = rt["TYP-ROOM TYPE TAG"]
	# 	newrt.data_text = json.dumps(rt)
	# 	newrt.save()
	pro = get_object_or_404(project, number="217102.00" )
	rooms = room.objects.filter(project = pro)
	for item in rooms:
		item.save()

	return JsonResponse({"log":log, "finished":"excellent"})


def emergencyFix(request):
	log = []
	try:
		projectno = "217102.00"
		elid_lu = {"2852188":	"5240161", "2852197":	"5240162", "2852311":	"5240165", "2852312":	"5240166", "2852321":	"5240167", "2852340":	"5240168", "2852342":	"5240169", "2852343":	"5240170", "2852346":	"5240171", "2852348":	"5240172", "2852360":	"5240173", "2852372":	"5240174", "2852402":	"5240175", "2852405":	"5240176", "2852408":	"5240177", "2852422":	"5240178", "2852441":	"5240179", "2852451":	"5240180", "2852462":	"5240181", "2852473":	"5240182", "2852487":	"5240183", "2852504":	"5240184", "2852505":	"5240185", "2852527":	"5240186", "2852528":	"5240187", "2852581":	"5240188", "2852582":	"5240189", "2852583":	"5240190", "2852584":	"5240191", "2852608":	"5240192", "2852613":	"5240193", "2852614":	"5240194", "2852627":	"5240195", "2852633":	"5240196", "2852654":	"5240197", "2852688":	"5240198", "2852708":	"5240199", "2852710":	"5240200", "2852721":	"5240201", "3175049":	"5240323", "3939647":	"5241411", "3939652":	"5241412", "3939673":	"5241413", "3942393":	"5241425", "3942562":	"5241428", "4569690":	"5243316", "4569759":	"5243317", "4570142":	"5243319", "4570602":	"5243325", "4635390":	"5243342", "5015636":	"5244915", "5015646":	"5244916", "5028883":	"5244918", "5031142":	"5244925", "5058730":	"5244939", "5060490":	"5244942", "5078010":	"5244944", "5078015":	"5244945", "5078949":	"5244959", "5093720":	"5245075", "5104768":	"5245090", "5109379":	"5245116", "5109389":	"5245117", "5109399":	"5245118", "5109590":	"5245119", "5184729":	"5245531", "5276599":	"5245621", "5297452":	"5245677", "5302434":	"5245683", "5328983":	"5245719", "5329451":	"5245720", "5329463":	"5245721", "5576884":	"5246526", "5576895":	"5246527", "5576906":	"5246528", "5576920":	"5246529", "5576932":	"5246530", "5576961":	"5246531", "5576979":	"5246532", "5583692":	"5246536", "5584064":	"5246537", "5584074":	"5246538", "5590552":	"5246540", "5590562":	"5246541", "5590714":	"5246542", "5590725":	"5246543", "5604260":	"5246579", "5604487":	"5246580", "5605611":	"5246581", "5605612":	"5246582", "5606007":	"5246585", "5606008":	"5246586", "5606571":	"5246590", "5607063":	"5246591", "5607067":	"5246592", "5640694":	"5246870", "5656396":	"5246911", "5702364":	"5248374", "5715100":	"5248419", "5730600":	"5248466", "5730601":	"5248467", "5730602":	"5248468", "5730603":	"5248469", "5798761":	"5248886", "5798762":	"5248887", "5798763":	"5248888", "5799312":	"5248889", "6071475":	"5249093", "6071480":	"5249094", "6121037":	"5250477", "6622532":	"5252211", "6714916":	"5252359", "6715307":	"5252365", "6779117":	"5252388", "6802793":	"5252467", "6802841":	"5252515", "6805627":	"5252615", "6811982":	"5252731", "6825309":	"5252907", "6825328":	"5252908", "6825344":	"5252909", "6840969":	"5252958", "6840980":	"5252959", "6850722":	"5252962", "6850726":	"5252963", "6850998":	"5252973", "6851008":	"5252974", }
		
		# elid_lu = {"2852079":	"5184821"}
		for k,v in elid_lu.items():
			try:
				constructedelid = projectno+"|"+k
				newelid = projectno+"|"+v
				roomtofix = get_object_or_404(room, element_id=constructedelid)
				roomtofix.element_id = newelid
				print(roomtofix)
				print(newelid)
				roomtofix.save()
			except Exception as e:
				log.append(str(e))
		return JsonResponse({"done":True, "log":log})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		other = sys.exc_info()[0].__name__
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		errorType = str(exc_type)
		return JsonResponse({"isError": True, "error":str(e), "errorType":errorType, "function":fname, "line":exc_tb.tb_lineno, "log":log})


@csrf_exempt
def googletemp(request):
	log = []
	if request.method == "POST":
		log.append("POST")
		try:
			log.append(request.POST)
			data = request.POST["data"]
			jd = json.loads(data)
			out = {"out": "working", "log":log}
			createdcount = 0
			for modeldict in jd:
				elidspl = modeldict['element_id'].split("|")
				modeldict['project_number'] = elidspl[0]
				modeldict['element_id'] = elidspl[1]
				try:
					try:
						modeldict['project_number']
						exist = get_object_or_404(room, element_id=str(modeldict['project_number'])+"|"+str(modeldict['element_id']))
					except:
						exist = get_object_or_404(room, element_id=modeldict['element_id'])
					existdata = exist.unique_data()
					existdata.update(modeldict['data'])
					modeldict['data_text'] = json.dumps(existdata)
				except:
					modeldict['data_text'] = json.dumps(modeldict['data'])
					pass

				pro = get_object_or_404(project, number=str(modeldict['project_number']))
				modeldict['project'] = pro
				modeldict['element_id'] = str(modeldict['project_number'])+"|"+str(modeldict['element_id'])

				try:
					modeldict['room_type_name']
					try:
						modeldict['room_type'] = get_object_or_404(room_type, project=modeldict['project'] ,type_name=str(modeldict['room_type_name']))
						log.append(str(modeldict['room_type']))
					except:
						log.append("NO ROOM TYPE")
						modeldict['room_type'] = get_object_or_404(room_type, project=modeldict['project'], type_name="-")
				except:
					pass
					
				try:
					del modeldict['data']
					del modeldict['project_number']
				except:
					pass
				elid = modeldict['element_id']
				del modeldict['element_id']
				log.append(elid)
				mod, created = room.objects.update_or_create(element_id=elid, defaults=modeldict)
				if created:
					createdcount += 0
				log.append("created: "+str(createdcount))
				print("FINISHED")
				print(out)
			return JsonResponse(out)

		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			other = sys.exc_info()[0].__name__
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			errorType = str(exc_type)
			return JsonResponse({"isError": True, "error":str(e), "errorType":errorType, "function":fname, "line":exc_tb.tb_lineno, "log":log})
		
		return JsonResponse(out)
	else:
		return HttpResponse("ONLY POST REQUESTS")