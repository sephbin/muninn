from django.contrib.postgres.fields import JSONField
from django.db import models
import django.utils.html as dhtml
import json
import uuid
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.models import User
from labsauth.models import *
from .project_functions import project_functions

location_choices = (
	('Sydney','Sydney'),
	('Melborune','Melborune'),
	('Perth','Perth'),
	('Brisbane','Brisbane'),
	('Canberra','Canberra'),
	('Adelaide','Adelaide'),
	('International','International'),
)


# Create your models here.
def exists(variable):
	if variable:
		return variable
	else:
		return ""

class project(models.Model):
	name =				models.CharField(max_length=200)
	number =			models.CharField(max_length=200, unique=True)
	location=			models.CharField(max_length=200,choices=location_choices)
	department_text =	models.TextField(max_length=9999, default="{}")
	users =				models.ManyToManyField(User, related_name='muninnProjects')
	functions =			models.TextField(max_length=9999, default="")
	function_store =	models.TextField(max_length=9999, default="{}")
	class Meta:
		ordering = ['number']
	def __str__(self):
		return (self.number+" - "+self.name)
	def departments(self):
		return json.loads(self.department_text)
	def functions(self):
		try:
			flist = json.loads(self.function_store)
			for k,v in flist.items():
				try:
					flist[k]["function"] = getattr(project_functions,v["functionName"])
				except: pass
			return flist
		except Exception as e:	return {"error": str(e)}
	def save( self, *args, **kw ):
		# roomTypes = room_type.objects.filter(project = self)
		# rooms = room.objects.filter(project = self)
		# if len(roomTypes) == 0:
		# 	nrt = room_type()
		# 	nrt.project = self
		# 	nrt.type_name = "-"
		# 	nrt.save()
		# if len(rooms) == 0:
		# 	nr = room()
		# 	nr.project = self
		# 	nr.room_name = "-"
		# 	nr.room_type = room_type.objects.all()[0]
		# 	nr.save()
		super( project, self ).save( *args, **kw )

class finish_schedule(models.Model):
	project = models.ForeignKey(project, on_delete=models.CASCADE)
	finishes = models.ManyToManyField('finish', through='rel_finish',through_fields=('rfinish_schedule', 'rfinish'), blank=True,)
	def revision(self):
		children = finish_schedule.objects.filter(project=self.project)
		children = list(map(lambda x: x.id, children))
		i = children.index(self.id)+1
		return i
	def __str__(self):
		children = finish_schedule.objects.filter(project=self.project)
		children = list(map(lambda x: x.id, children))
		retstr = "%s - Rev %s" %(self.project, self.revision())
		if children[-1] == self.id:
			retstr += " (CURRENT)"
		return retstr

class supplier(models.Model):
	company =models.CharField(max_length=200)
	representative=models.CharField(max_length=200)
	phone=models.CharField(max_length=20, blank=True, null=True)
	email=models.EmailField(blank=True, null=True)
	location=models.CharField(max_length=200,choices=location_choices)
	def __str__(self):
		return (self.company +": "+self.representative)
	def full(self):
		return '''Company: %s\nRep: %s\nPh: %s\nEmail: %s''' % (self.company, self.representative, self.phone, self.email)

class finish(models.Model):
	schedules = models.ManyToManyField('finish_schedule', through='rel_finish',through_fields=('rfinish','rfinish_schedule'), blank=True,)
	image = models.ImageField(blank=True, null=True)
	fin_product = models.CharField(max_length=200, blank=True, null=True)
	fin_finish =models.CharField(max_length=200, blank=True, null=True)
	fin_colour =models.CharField(max_length=200, blank=True, null=True)
	fin_code =models.CharField(max_length=200, blank=True, null=True)
	fin_size = models.CharField(max_length=200, blank=True, null=True)
	fin_notes = models.CharField(max_length=200, blank=True, null=True)
	supplier = models.ForeignKey(supplier, on_delete=models.CASCADE, null=True)

	def image_tag(self):
		return dhtml.mark_safe('<img src="/media/%s" width="150" height="auto" />' % (self.image))
	image_tag.short_description = 'Image'
	image_tag.allow_tags = True

	def finish(self):
		return dhtml.mark_safe('<div><b>Product: </b>%s<br><b>Finish: </b>%s<br><b>Colour: </b>%s<br><b>Code: </b>%s<br><b>Size: </b>%s<br><b>Notes: </b>%s<br></div>' % (self.fin_product, self.fin_finish, self.fin_colour, self.fin_code, self.fin_size, self.fin_notes))
	def supplytext(self):
		return dhtml.mark_safe('<div><b>Company: </b>%s<br><b>Rep: </b>%s<br><b>Ph: </b><a href="tel:%s">%s</a><br><b>Email: </b><a href="mailto:%s">%s</a><br></div>' % (self.supplier.company, self.supplier.representative, self.supplier.phone, self.supplier.phone, self.supplier.email,self.supplier.email))
	supplytext.short_description = 'Supplier'
	def __str__(self):
		try:
			findetails = [exists(self.fin_product),exists(self.fin_finish),exists(self.fin_colour)]
			findettext = " - ".join(findetails)
			return (str(findettext))
		except Exception as e:
			return str(e)

class rel_finish(models.Model):
	rfinish_schedule = models.ForeignKey(finish_schedule, on_delete=models.CASCADE, related_name='rschedule')
	rfinish = models.ForeignKey(finish, on_delete=models.CASCADE, related_name='rfinish')


class room_type(models.Model):
	class Meta:
		ordering = ['code','type_name']

	project = models.ForeignKey('project',on_delete=models.CASCADE)
	type_name = models.CharField(max_length=200, blank=True, null=True)
	data_text = models.TextField(max_length=99999, default="{}")
	code = models.CharField(max_length=200, blank=True, null=True)
	def __str__(self):
		return(str(self.project)+":"+self.type_name)
	def data(self):
		try:
			return json.loads(self.data_text)
		except:
			print(self.type_name)
			return {}
	def save( self, *args, **kw ):
		try:
			d = self.data()
			department_letter = self.project.departments()[self.data()["Department"]]
			if d["Room Type ID"] == "-" or d["Room Type ID"] == "":
				## GET OTHER ROOM TYPES WITH SAME DEPARTMENT
				rts = room_type.objects.filter(project = self.project)
				rtsf = list(filter(lambda x: x.data()["Department"] == self.data()["Department"], rts))
				rtsm = list(map(lambda x: x.data()["Room Type ID"], rtsf))
				rtsm = list(filter(lambda x: x != "" and x != "-", rtsm))
				rtsm = list(map(lambda x: x.replace("F",""),rtsm))
				rtsm = list(map(lambda x: int(x.replace(department_letter,"")),rtsm))
				rtsm.sort()
				last = rtsm[-1]+1
				last = "%02d" % (last,)
				d["Room Type ID"] = department_letter+str(last)
			self.data_text = json.dumps(d)
		except Exception as e:
			print(str(e))
		try:
			self.code = self.data()["RDS ID"]
		except:
			pass
		super( room_type, self ).save( *args, **kw )

class room(models.Model):
	project = models.ForeignKey('project',on_delete=models.CASCADE)
	element_id = models.CharField(max_length=200, default=uuid.uuid4, unique=True)
	source_file = models.CharField(max_length=256, blank=True, null = True)
	room_name = models.CharField(max_length=200, blank=True, null=True)
	room_type = models.ForeignKey('room_type',on_delete=models.SET_NULL, null=True, blank=True)
	data_text = models.TextField(max_length=99999, default="{}")
	number_store = models.CharField(max_length=200, default="----")
	class Meta:
		ordering = ['room_name']
	def __str__(self):
		try:
			return(self.element_id+": "+self.room_name)
		except:
			return(self.room_name)

	def elid(self):
		try:
			return(self.element_id+": "+self.room_name)
		except:
			return(self.room_name)

	def unique_data(self):
		try:
			jdata = json.loads(self.data_text)
			jdata["Name"] = self.room_name
			keystodelete = []
			for k,v in jdata.items():
				if v == '':
					keystodelete.append(k)
			for k in keystodelete:
				del jdata[k]
			return jdata
		except Exception as e:
			return {}
	def room_type_name(self):
		try:
			return self.room_type.type_name
		except:
			return ""
	def data(self):
		try:
			basedata = self.room_type.data()
			uniqdata = self.unique_data()
			uniqdata["Contents"] = self.contentlist()
			uniqdata["Doors"] = self.doorslist()
			# uniqdata["Doors"] = self.alldoorslist()
			uniqdata["All Doors"] = self.alldoorslist(key="Mark")
			uniqdata["All Doors - Type"] = self.alldoorslist(key="Type")
			uniqdata["Name"] = self.room_name
			uniqdata["Revit Element Id"] = self.element_id.split("|")[1]

			try: uniqdata["Type Name"] = self.room_type.type_name
			except: pass
			basedata.update(uniqdata)
			return basedata
		except:
			uniqdata = json.loads(self.data_text)
			uniqdata["Contents"] = self.contentlist()
			uniqdata["Doors"] = self.doorslist()
			# uniqdata["Doors"] = self.alldoorslist()
			uniqdata["All Doors"] = self.alldoorslist(key="Mark")
			uniqdata["All Doors - Type"] = self.alldoorslist(key="Type")
			uniqdata["Name"] = self.room_name
			try: uniqdata["Type Name"] = self.room_type.type_name
			except: pass

			return uniqdata
	def contentlist(self):
		try:
			els = self.elements.all()
			obs = []
			for el in els:
				obs.append(el.data()['Keynote'])
			outob = list(set(obs))
			outob.sort()
			outstring = []
			for s in outob:
				c = obs.count(s)
				st = "%sno %s" %(str(c),s)
				outstring.append(st)
			outstring = "; ".join(outstring)
			return outstring
		except:
			return ""
	def doorslist(self):
		els = self.doors.all()
		els = list(map(lambda x: x.mark,els))
		try:
			outstring = "; ".join(els)
			return outstring
		except:
			outstring = ""
			return outstring
	def alldoors(self):
		from_els = self.from_door.all()
		to_els = self.to_door.all()

		els = from_els | to_els
		return els
	def alldoorslist(self, key = "Mark"):
		els = []
		for x in self.alldoors():
			try:
				val = str(x.data()[key])
				els.append(val)
			except Exception as e:
				els.append(str(e))
		# els = list(map(lambda x: x.mark, self.alldoors()))

		try:
			outstring = "  ".join(els)
			return outstring
		except:
			outstring = ""
			return outstring

	def save( self, *args, **kw ):
		try:
			self.number_store = self.data()["Number"]
		except:
			self.number_store = "----"
		super( room, self ).save( *args, **kw )
		

class door(models.Model):

	project = models.ForeignKey('project',on_delete=models.CASCADE)
	element_id = models.CharField(max_length=200, default=uuid.uuid4, unique=True)
	data_text = models.TextField(max_length=9999, default="{}")
	from_room = models.ForeignKey('room', on_delete=models.SET_NULL, null=True, blank=True, related_name="from_door")
	to_room = models.ForeignKey('room', on_delete=models.SET_NULL, null=True, blank=True, related_name="to_door")
	parent_room = models.ForeignKey('room', on_delete=models.SET_NULL, null=True, blank=True, related_name="doors")
	mark = models.CharField(max_length=200, null=True, blank=True)
	data_store = models.TextField(max_length=9999, default="{}")

	class Meta:
		ordering = ['element_id']

	def __str__(self):
		return(self.element_id)

	def elid(self):
		try:
			return(self.element_id+": "+self.mark)
		except:
			return(self.element_id)
	
	def family(self):
		try:
			return self.data()['Family']
		except:
			return ""

	def room_data(self):
		roomdat = self.parent_room.data()
		rdd = {}
		keys = [
		"DoorHardware_Set",
		"DoorHardware_Closer",
		"DoorHardware_Handle",
		"DoorHardware_Hinge",
		"DoorHardware_Keying",
		"DoorHardware_Protection",
		"DoorHardware_Seal",
		"DoorHardware_Signage",
		"DoorHardware_DoorStop",
		"DoorHardware_VisionPanel",
		"Door_Leaf_Type",
		"Door_Leaf_Finish",
		"Door_Frame_Type",
		"Door_Frame_Finish"]
		for k in keys:
			try: rdd[k] = roomdat[k]
			except: pass
		return rdd
	
	def unique_data(self):
		log = []
		letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z", "RL","JF","IH","PD","IK","AB","CC","LG","AC","AY","JK","DN","SS","HC","CL","AR","HM","PN","MF","MK","EF","DP","MS","MW"]
		try:
			job = json.loads(self.data_text)
			try:
				job["Mark"] = self.getmark()
			except:
				pass
			try:
				job["DoorPanelWidth_ANZRS"] = int(job["DoorPanelWidth_ANZRS"])
				job["DoorPanelHeight_ANZRS"] = int(job["DoorPanelHeight_ANZRS"])
			except: pass
			return job
		except Exception as e:
			return {"error":str(e), "log":log}
	def dyn_alldata(self):
		try:
			try:
				basedata = self.room_data()
			except:
				basedata = {}
			uniqdata = self.unique_data()
			basedata.update(uniqdata)
			fam = basedata["Family"]
			fam = fam.split(", Family:")
			fam = fam[0].replace("Family Type: ", "")
			basedata["Type"] = fam 
			return basedata
		except Exception as e:
			return {"error":str(e)}
	def data(self):
		try:
			return json.loads(self.data_store)
		except Exception as e:
			return {"error":str(e)}

	def get_room_no(self):
		try:
			frno = self.from_room.data()["Number"]
			try:
				frpr = self.from_room.data()["Door Priority"]
			except: frpr = 0
			tono = self.to_room.data()["Number"]
			try:
				topr = self.to_room.data()["Door Priority"]
			except: topr = 0

			if float(frpr) >= float(topr):
				rono = self.from_room
				return rono
			else:
				rono = self.to_room
				return rono
		except Exception as e:
			print("ERROR")
			print(e)
			job = json.loads(self.data_text)
			job["Error"] = str(e)
			self.data_text = json.dumps(job)

			frono = self.from_room
			trono = self.to_room
			if frono == None:
				return trono
			elif trono == None:
				return frono
			else:
				return None
	def getmark(self):
		mark = self.project.functions()["doorNumbering"]["function"](object = self)
		return mark
	def save( self, *args, **kw ):
		self.parent_room = self.get_room_no()
		self.mark = self.getmark()
		alldata = self.dyn_alldata()
		try:	alldata["Room Number"] = self.parent_room.data()["Number"]
		except: alldata["Room Number"] = "??"
		self.data_store = json.dumps(alldata)
		super( door, self ).save( *args, **kw )


class element(models.Model):
	project = models.ForeignKey('project',on_delete=models.CASCADE)
	element_id = models.CharField(max_length=200, default=uuid.uuid4, unique=True)
	data_text = models.TextField(max_length=9999, default="{}")
	parent_room = models.ForeignKey('room', on_delete=models.SET_NULL, null=True, blank=True, related_name="elements")
	
	class Meta:
		ordering = ['element_id']

	def __str__(self):
		return(self.element_id)

	def family(self):
		try:
			return self.data()['Family']
		except:
			return ""
	def unique_data(self):
		try:
			job = json.loads(self.data_text)
			return job
		except:
			return {}
	def data(self):
		return self.unique_data()
	def get_room(self):
		try:
			roomid = self.unique_data()["Room"]
			roomob = get_object_or_404(room, element_id=roomid)
			return roomob
		except:
			return None
	def save( self, *args, **kw ):
		self.parent_room = self.get_room()
		super( element, self ).save( *args, **kw )






# Create your models here.
def exists(variable):
	if variable:
		return variable
	else:
		return ""


class element_type(models.Model):
	element_types = (
		('CH','Chair'),
		('FA','Fan'),
		('TB','Table'),
		('UM', 'Umbrella'),
	)
	element_type = models.CharField(max_length=255,choices=element_types)
	item = models.CharField(max_length=255, blank=True, null=True)
	description = models.TextField(max_length=9999, blank=True, null=True)
	dimensions = models.TextField(max_length=9999, blank=True, null=True)
	image = models.ImageField(blank=True, null=True)
	comments = models.TextField(max_length=9999, blank=True, null=True)
	supplier = models.ForeignKey(supplier, on_delete=models.CASCADE, null=True)
	projects = models.ManyToManyField(project, blank=True, null=True)
	def image_tag(self):
		return dhtml.mark_safe('<img src="/media/%s" width="150" height="auto" />' % (self.image))
	image_tag.short_description = 'Image'
	image_tag.allow_tags = True
	def description_tag(self):
		text = self.description
		text = text.replace("\n","<br>")
		return dhtml.mark_safe(text)
	description_tag.short_description = 'Description'
	description_tag.allow_tags = True
	def supplytext_tag(self):
		return dhtml.mark_safe('<div><b>Company: </b>%s<br><b>Rep: </b>%s<br><b>Ph: </b><a href="tel:%s">%s</a><br><b>Email: </b><a href="mailto:%s">%s</a><br></div>' % (self.supplier.company, self.supplier.representative, self.supplier.phone, self.supplier.phone, self.supplier.email,self.supplier.email))
	supplytext_tag.short_description = 'Supplier'
	supplytext_tag.allow_tags = True
	def dimension_tag(self):
		text = self.dimensions
		text = text.replace("\n","<br>")
		return dhtml.mark_safe(text)
	dimension_tag.short_description = 'Dimension'
	dimension_tag.allow_tags = True
	def comment_tag(self):
		text = self.comments
		text = text.replace("\n","<br>")
		return dhtml.mark_safe(text)
	comment_tag.short_description = 'Comments'
	comment_tag.allow_tags = True
	def code(self):
		return self.element_type
	def save( self, *args, **kw ):
		print("-------------------------------------")
		super( element_type, self ).save( *args, **kw )
		print("saved element")

def create_project_element_types(sender, **kwargs):
	print("creating a project element type")
	print(kwargs['instance'].projects.all())
	for i in kwargs['instance'].projects.all():
		print("running for")
		try:
			p = get_object_or_404(project_element_types, project=i, element=kwargs['instance'])
		except:
			p = project_element_types()
			p.element = kwargs['instance']
			p.project = i
			print("saving a element_type into project")
			p.save()

m2m_changed.connect(create_project_element_types, sender=element_type.projects.through)
class project_element_types(models.Model):
	element = models.ForeignKey(element_type, on_delete=models.CASCADE, null=True)
	quantity = models.IntegerField(default = 1)
	project = models.ForeignKey(project, on_delete=models.CASCADE, null=True)
	code = models.CharField(max_length=10, null=True, blank=True)
	class Meta:
		ordering = ['code']
	def image_tag(self):
		return self.element.image_tag()
	image_tag.short_description = 'Image'
	image_tag.allow_tags = True
	def description_tag(self):
		return self.element.description_tag()
	description_tag.short_description = 'Description'
	description_tag.allow_tags = True
	def supplytext_tag(self):
		return self.element.supplytext_tag()
	supplytext_tag.short_description = 'Supplier'
	supplytext_tag.allow_tags = True
	def dimension_tag(self):
		return self.element.dimension_tag()
	dimension_tag.short_description = 'Dimension'
	dimension_tag.allow_tags = True
	def comment_tag(self):
		return self.element.comment_tag()
	comment_tag.short_description = 'Comments'
	comment_tag.allow_tags = True
	def space_tag(self):
		try:
			text = []
			for space in self.spaces.all():
				text.append (space.space.space_name+": "+str(space.quantity))
			text = "<br>".join(text)
			return text
		except Exception as e:
			return str(e)
	space_tag.short_description = 'Spaces'
	space_tag.allow_tags = True
	def save( self, *args, **kw ):
		if not self.code:
			basecode = self.element.code()
			otherobs = project_element_types.objects.filter(project=self.project)
			no = 1
			for i in otherobs:
				if i.element.code() == basecode:
					no += 1
			newno = "%02d" % (no,)
			self.code = basecode+newno
		print("saving a project_element_type")
		super( project_element_types, self ).save( *args, **kw )

class space_element_quantity(models.Model):
	element = models.ForeignKey('project_element_types', on_delete=models.CASCADE, null=True, related_name="spaces")
	space = models.ForeignKey('space', on_delete=models.CASCADE, null=True, related_name="elements")
	quantity = models.IntegerField(default = 1)

class space(models.Model):
	project = models.ForeignKey(project, on_delete=models.CASCADE, null=True)
	space_name = models.CharField(max_length=256, null=True, blank=True, unique=True)

	def __str__(self):
		return self.space_name
	def furnitureScheduleTag(self):
		url = "/bd/schedules/furniture/%s/%s" %(self.project.number, self.space_name)
		return dhtml.mark_safe('<a href="%s">FURN LINK</a>' %(url))
	furnitureScheduleTag.short_description = 'Furniture Schedule'
	furnitureScheduleTag.allow_tags = True