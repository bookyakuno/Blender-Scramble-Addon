# 「3Dビュー」エリア > 「オブジェクト」モード > 「Ctrl + L」キー
# "3D View" Area > "Object" Mode > "Ctrl + L" Key

import bpy, bmesh

################
# オペレーター #
################

class MakeLinkObjectName(bpy.types.Operator):
	bl_idname = "object.make_link_object_name"
	bl_label = "Sync Object Name"
	bl_description = "Link name of active object to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) < 2):
			return False
		return True
	def execute(self, context):
		name = context.active_object.name
		for obj in context.selected_objects:
			if (obj.name != name):
				obj.name = "temp"
				obj.name = name
		bpy.context.active_object.name = name
		return {'FINISHED'}

class MakeLinkLayer(bpy.types.Operator):
	bl_idname = "object.make_link_layer"
	bl_label = "Set Same Layer"
	bl_description = "link active object layers to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) < 2):
			return False
		return True
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.name != context.active_object.name):
				obj.layers = context.active_object.layers
		return {'FINISHED'}

class MakeLinkDisplaySetting(bpy.types.Operator):
	bl_idname = "object.make_link_display_setting"
	bl_label = "Make same objects display setting"
	bl_description = "Copy settings panel of active object to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	isSameType = bpy.props.BoolProperty(name="Only objects of same type", default=True)
	show_name = bpy.props.BoolProperty(name="Name", default=True)
	show_axis = bpy.props.BoolProperty(name="Axis", default=True)
	show_wire = bpy.props.BoolProperty(name="Wire Frame", default=True)
	show_all_edges = bpy.props.BoolProperty(name="Show All Edges", default=True)
	show_bounds = bpy.props.BoolProperty(name="Bound", default=True)
	show_texture_space = bpy.props.BoolProperty(name="Texture Space", default=True)
	show_x_ray = bpy.props.BoolProperty(name="X-ray", default=True)
	show_transparent = bpy.props.BoolProperty(name="Alpha", default=True)
	draw_bounds_type = bpy.props.BoolProperty(name="Bound Type", default=True)
	draw_type = bpy.props.BoolProperty(name="Maximum Draw Type", default=True)
	color = bpy.props.BoolProperty(name="Object Color", default=True)
	
	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) < 2):
			return False
		return True
	def execute(self, context):
		activeObj = context.active_object
		for obj in context.selected_objects:
			if (not self.isSameType or activeObj.type == obj.type):
				if (obj.name != activeObj.name):
					if (self.show_name):
						obj.show_name = activeObj.show_name
					if (self.show_axis):
						obj.show_axis = activeObj.show_axis
					if (self.show_wire):
						obj.show_wire = activeObj.show_wire
					if (self.show_all_edges):
						obj.show_all_edges = activeObj.show_all_edges
					if (self.show_bounds):
						obj.show_bounds = activeObj.show_bounds
					if (self.show_texture_space):
						obj.show_texture_space = activeObj.show_texture_space
					if (self.show_x_ray):
						obj.show_x_ray = activeObj.show_x_ray
					if (self.show_transparent):
						obj.show_transparent = activeObj.show_transparent
					if (self.draw_bounds_type):
						obj.draw_bounds_type = activeObj.draw_bounds_type
					if (self.draw_type):
						obj.draw_type = activeObj.draw_type
					if (self.color):
						obj.color = activeObj.color
		return {'FINISHED'}

class MakeLinkUVNames(bpy.types.Operator):
	bl_idname = "object.make_link_uv_names"
	bl_label = "Link empty UV map"
	bl_description = "Empty, add UV active objects to other selected objects"
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
				obj.data.uv_textures.new(uv.name)
		return {'FINISHED'}

class MakeLinkArmaturePose(bpy.types.Operator):
	bl_idname = "object.make_link_armature_pose"
	bl_label = "Link motion of armature"
	bl_description = "By constraints on other selected armature mimic active armature movement"
	bl_options = {'REGISTER', 'UNDO'}
	
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
		return {'FINISHED'}

######################
# オペレーター(変形) #
######################

class MakeLinkTransform(bpy.types.Operator):
	bl_idname = "object.make_link_transform"
	bl_label = "Link Transform"
	bl_description = "Information of active object copies to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	copy_location = bpy.props.BoolProperty(name="Location", default=True)
	copy_rotation = bpy.props.BoolProperty(name="Rotation", default=True)
	copy_scale = bpy.props.BoolProperty(name="Scale", default=True)
	
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
	bl_label = "Transform"
	bl_description = "Link object transforms"
	
	def draw(self, context):
		op = self.layout.operator(MakeLinkTransform.bl_idname, text="Transform", icon='PLUGIN')
		op.copy_location, op.copy_rotation, op.copy_scale = True, True, True
		self.layout.separator()
		op = self.layout.operator(MakeLinkTransform.bl_idname, text="Location", icon='PLUGIN')
		op.copy_location, op.copy_rotation, op.copy_scale = True, False, False
		op = self.layout.operator(MakeLinkTransform.bl_idname, text="Rotation", icon='PLUGIN')
		op.copy_location, op.copy_rotation, op.copy_scale = False, True, False
		op = self.layout.operator(MakeLinkTransform.bl_idname, text="Scale", icon='PLUGIN')
		op.copy_location, op.copy_rotation, op.copy_scale = False, False, True

################
# クラスの登録 #
################

classes = [
	MakeLinkObjectName,
	MakeLinkLayer,
	MakeLinkDisplaySetting,
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
	for id in bpy.context.preferences.addons["Blender-Scramble-Addon-master"].preferences.disabled_menu.split(','):
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
		self.layout.operator(MakeLinkObjectName.bl_idname, text="Object Name", icon="PLUGIN")
		self.layout.operator(MakeLinkLayer.bl_idname, text="Layer", icon="PLUGIN")
		self.layout.operator(MakeLinkDisplaySetting.bl_idname, text="Display Setting", icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(MakeLinkUVNames.bl_idname, text="Empty UV", icon="PLUGIN")
		self.layout.operator(MakeLinkArmaturePose.bl_idname, text="Movement of Armature", icon="PLUGIN")
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
