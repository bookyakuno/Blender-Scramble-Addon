# 「3Dビュー」エリア > 「オブジェクト」モード > 「Ctrl + L」キー
# "3D View" Area > "Object" Mode > "Ctrl + L" Key

import bpy, bmesh
from bpy.props import *

################
# オペレーター #
################

class MakeLinkObjectName(bpy.types.Operator):
	bl_idname = "object.make_link_object_name"
	bl_label = "Change to Same Object Name"
	bl_description = "Rename selected objects based on active object's name"
	bl_options = {'REGISTER', 'UNDO'}

	name_sep : EnumProperty(name="Numbering Expression",items=[
		(".",".00X","",1),("_","_00X","",2),("-","-00X","",3)])
	method : EnumProperty(name="Active Object",items=[
		("NO","No number","",1),("ZERO","000","",2),("ONE","001","",3)])

	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) < 2):
			return False
		return True
	def draw(self, context):
		row = self.layout.row(align=True)
		row.label(text="New Name")
		box = row.box().row()
		box.label(text=context.active_object.name)
		box.prop(self, 'name_sep', text="")
		row = self.layout.row(align=True)
		row.label(text="Active Object")
		row.prop(self, 'method', text="")

	def execute(self, context):
		new_name = context.active_object.name
		selected_others = list(set(context.selected_objects) - {context.active_object})
		name_head = f"{new_name}{self.name_sep}"
		if self.method == 'NO':
			new_names = [f"{name_head}{num+1:03}" for num in range(len(selected_others))]
		if self.method == 'ZERO':
			new_names = [f"{name_head}{num+1:03}" for num in range(len(selected_others))]
		elif self.method == 'ONE':
			new_names = [f"{name_head}{num+2:03}" for num in range(len(selected_others))]
		suffix_dic = {'NO':None,'ZERO':"000",'ONE':"001"}
		if suffix_dic[self.method]:
			nam = f"{name_head}{suffix_dic[self.method]}"
			try:
				existed_obs = bpy.data.objects[nam]
				existed_obs.name = "temp"
				context.active_object.name = nam
				existed_obs.name = nam
			except KeyError:
				context.active_object.name = nam
		for ob, nam in zip(selected_others, new_names):
			try:
				existed_obs = bpy.data.objects[nam]
				existed_obs.name = "temp"
				ob.name = nam
				existed_obs.name = nam
			except KeyError:
				ob.name = nam
		return {'FINISHED'}

class MakeLinkUVNames(bpy.types.Operator):
	bl_idname = "object.make_link_uv_names"
	bl_label = "Change to Same-name UV Map"
	bl_description = "Add to selected objects empty UV maps which names are same as active object's maps"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) < 2):
			return False
		if (context.object.type != 'MESH'):
			return False
		if (len(context.object.data.uv_layers) <= 0):
			return False
		for obj in context.selected_objects:
			if (obj.name != context.object.name):
				if (obj.type == 'MESH'):
					return True
		return False

	def execute(self, context):
		active_obj = context.active_object
		target_objs = []
		for obj in context.selected_objects:
			if (obj.type == 'MESH' and active_obj.name != obj.name):
				target_objs.append(obj)
		for obj in target_objs:
			for uv in active_obj.data.uv_layers:
				obj.data.uv_layers.new(name=uv.name)
		return {'FINISHED'}

class MakeLinkArmaturePose(bpy.types.Operator):
	bl_idname = "object.make_link_armature_pose"
	bl_label = "Follow to Active Armature"
	bl_description = "Add constraint to selected armatures so that they follow to active armature"
	bl_options = {'REGISTER', 'UNDO'}

	influence : FloatProperty(name="Influence", default=1.0, max=1.0, min=0.0)

	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) < 2):
			return False
		if (context.object.type != 'ARMATURE'):
			return False
		for obj in context.selected_objects:
			if (obj.name != context.object.name):
				if (obj.type == 'ARMATURE'):
					return True
		return False

	def execute(self, context):
		active_obj = context.active_object
		target_objs = []
		for obj in context.selected_objects:
			if (obj.type == 'ARMATURE' and active_obj.name != obj.name):
				target_objs.append(obj)
		for obj in target_objs:
			for bone in active_obj.pose.bones:
				try:
					target_bone = obj.pose.bones[bone.name]
				except KeyError:
					continue
				consts = target_bone.constraints
				for const in consts[:]:
					consts.remove(const)
				const = consts.new('COPY_TRANSFORMS')
				const.target = active_obj
				const.subtarget = bone.name
				const.influence = self.influence
		return {'FINISHED'}

######################
# オペレーター(変形) #
######################

class MakeLinkTransform(bpy.types.Operator):
	bl_idname = "object.make_link_transform"
	bl_label = "Change to Same Transform"
	bl_description = "Change selected objects' locations / rotations / scales to same as active object's"
	bl_options = {'REGISTER', 'UNDO'}

	copy_location : BoolProperty(name="Location", default=True)
	copy_rotation : BoolProperty(name="Rotation", default=True)
	copy_scale : BoolProperty(name="Scale", default=True)

	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) < 2):
			return False
		return True

	def execute(self, context):
		active_obj = context.active_object
		for obj in context.selected_objects:
			if (obj.name != active_obj.name):
				if (self.copy_location):
					obj.location = active_obj.location[:]
				if (self.copy_rotation):
					obj.rotation_mode = active_obj.rotation_mode
					if (obj.rotation_mode == 'QUATERNION'):
						obj.rotation_quaternion = active_obj.rotation_quaternion[:]
					elif (obj.rotation_mode == 'AXIS_ANGLE'):
						obj.rotation_axis_angle = active_obj.rotation_axis_angle[:]
					else:
						obj.rotation_euler = active_obj.rotation_euler[:]
				if (self.copy_scale):
					obj.scale = active_obj.scale[:]
		return {'FINISHED'}

################
# サブメニュー #
################

class TransformMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_make_links_transform"
	bl_label = "Change to Same Transform"
	bl_description = "Change selected objects' locations / rotations / scales to same as active object's"

	def draw(self, context):
		op = self.layout.operator(MakeLinkTransform.bl_idname)
		op.copy_location, op.copy_rotation, op.copy_scale = True, True, True
		self.layout.separator()
		op = self.layout.operator(MakeLinkTransform.bl_idname, text="Copy Location")
		op.copy_location, op.copy_rotation, op.copy_scale = True, False, False
		op = self.layout.operator(MakeLinkTransform.bl_idname, text="Copy Rotation")
		op.copy_location, op.copy_rotation, op.copy_scale = False, True, False
		op = self.layout.operator(MakeLinkTransform.bl_idname, text="Copy Scale")
		op.copy_location, op.copy_rotation, op.copy_scale = False, False, True

################
# クラスの登録 #
################

classes = [
	MakeLinkObjectName,
	MakeLinkUVNames,
	MakeLinkArmaturePose,
	MakeLinkTransform,
	TransformMenu
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.menu(TransformMenu.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(MakeLinkObjectName.bl_idname, icon="PLUGIN")
		self.layout.operator('object.copy_display_setting', text="Change to Same Display Setting", icon="PLUGIN")# object.copy_display_setting で定義
		self.layout.operator(MakeLinkUVNames.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(MakeLinkArmaturePose.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
