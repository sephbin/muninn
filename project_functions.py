class project_functions():
	def doorNoAppendToRoomNo(object):
		letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z", "RL","JF","IH","PD","IK","AB","CC","LG","RL","AC","AY","JK","DN","JF","SS","HC","CL","AR","HM","PN","MF","MK","EF","DP","MS","MW"]
		variables = object.project.functions()["doorNumbering"]["variables"]
		mark = ""
		try:
			mark = str(object.parent_room.data()['Number'])
		except:
			mark = "??"
		parentRoomDoors = object.parent_room.doors.all()
		doors = list(map(lambda x: x, parentRoomDoors))
		
		try:	mark += variables["prefix"]
		except:	pass

		if variables["numberType"] == "letters":
			try:
				mark += letters[doors.index(object)]
			except:
				mark += letters[0]
		if variables["numberType"] == "numbers":
			try:
				mark += str(doors.index(object)+variables["numberOffset"]).zfill(variables["numberDigits"])
			except:
				mark += str(0+variables["numberOffset"]).zfill(variables["numberDigits"])

		try:	mark += variables["suffix"]
		except:	pass

		return mark
	def doorNoSingle(object):
		letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z", "RL","JF","IH","PD","IK","AB","CC","LG","RL","AC","AY","JK","DN","JF","SS","HC","CL","AR","HM","PN","MF","MK","EF","DP","MS","MW"]
		variables = object.project.functions()["doorNumbering"]["variables"]
		mark = ""
		try:
			parentRoomDoors = object.parent_room.doors.all()
			doors = list(map(lambda x: x, parentRoomDoors))
		except Exception as e:
			# mark += str(e)
			doors = []
		
		try:	mark += variables["prefix"]
		except:	pass

		if variables["numberType"] == "letters":
			try:
				mark += letters[doors.index(object)]
			except:
				mark += letters[0]
		if variables["numberType"] == "numbers":
			try:
				mark += str(doors.index(object)+variables["numberOffset"]).zfill(variables["numberDigits"])
			except Exception as e:
				mark += str(0+variables["numberOffset"]).zfill(variables["numberDigits"])
				# mark += "("
				# mark += str(e)
				# mark += ")"
				# mark += str(e)

		try:	mark += variables["suffix"]
		except:	pass

		return mark