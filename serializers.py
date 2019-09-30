from .models import *
from rest_framework import serializers

# class RoomSerializer(serializers.ModelSerializer):
# 	race = raceSerializer(read_only=True)
# 	campaign = campaignSerializer(read_only=True)
# 	status = statusSerializer(read_only=True)
# 	characterType = characterTypeSerializer(read_only=True)
# 	reladvantage = RelAdvantageSerializer(read_only=True, many=True)
# 	reldisadvantage = RelDisadvantageSerializer(read_only=True, many=True)
# 	relskill = RelSkillSerializer(read_only=True, many=True)
# 	relpossession = RelPossessionSerializer(read_only=True, many=True)
# 	possessionTotals = serializers.DictField()
# 	damage = serializers.DictField()
# 	cost = serializers.IntegerField()
# 	class Meta:
# 		model = character
# 		fields = ('__all__')

class RoomSerializer(serializers.ModelSerializer):
	data = serializers.JSONField()
	# room_type_name = serializers.CharField(source='room_type.type_name', )
	room_type_name = serializers.CharField()
	class Meta:
		model = room
		fields = ('__all__')

class RoomTypeSerializer(serializers.ModelSerializer):
	data = serializers.JSONField()
	class Meta:
		model = room_type
		fields = ('__all__')

class DoorRoomSerializer(serializers.ModelSerializer):
	class Meta:
		model = room
		fields = ('element_id','id','room_name','number_store')

class DoorSerializer(serializers.ModelSerializer):
	parent_room = DoorRoomSerializer()
	to_room = DoorRoomSerializer()
	from_room = DoorRoomSerializer()
	data = serializers.JSONField()
	class Meta:
		model = door
		fields = ('__all__')