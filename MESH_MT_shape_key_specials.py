# 「プロパティ」エリア > 「オブジェクトデータ」タブ > シェイプキーリスト右の▼
# "Propaties" Area > "Object" Tab > ShapeKeys List Right ▼

import bpy
from bpy.props import *

################
# オペレーター #
################

class CopyShape(bpy.types.Operator):
	bl_idname = "mesh.copy_shape"
	bl_label = "Duplicate Shape Key"
	bl_description = "Duplicate active shape key"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob) and ob.mode == 'OBJECT':
			if ob.type in {'MESH','CURVE'}:
				if (ob.active_shape_key):
					return True
		return False

	def execute(self, context):
		obj = context.active_object
		if obj.type in {'MESH','CURVE'}:
			me = obj.data
			keys = {}
			for key in me.shape_keys.key_blocks:
				keys[key.name] = key.value
				key.value = 0
			obj.active_shape_key.value = 1
			relativeKey = obj.active_shape_key.relative_key
			while relativeKey != relativeKey.relative_key:
				relativeKey.value = 1
				relativeKey = relativeKey.relative_key
			obj.shape_key_add(name=obj.active_shape_key.name, from_mix=True)
			obj.active_shape_key_index = len(me.shape_keys.key_blocks) - 1
			for k, v in keys.items():
				me.shape_keys.key_blocks[k].value = v
		return {'FINISHED'}

class InsertKeyframeAllShapes(bpy.types.Operator):
	bl_idname = "mesh.insert_keyframe_all_shapes"
	bl_label = "Insert Keyframes for All Shapes"
	bl_description = "Insert keyframe for all shapes' values on the current frame"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if ob.type in {'MESH','CURVE'}:
				if (ob.active_shape_key):
					return True
		return False

	def execute(self, context):
		for shape in context.active_object.data.shape_keys.key_blocks:
			shape.keyframe_insert(data_path="value")
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class InsertKeyframeWithInverval(bpy.types.Operator):
	bl_idname = "mesh.insert_keyframe_with_interval"
	bl_label = "Insert Keyframes with Fixed Interval"
	bl_description = "Insert zero-and- positive-value keyframes for each shape keys with designated interval"
	bl_options = {'REGISTER', 'UNDO'}

	interval : IntProperty(name="Interval", default=20, min=0)
	set_max : BoolProperty(name="Use Current Value instead of '1'", default=False)
	item = [("CURRENT", "Current Frame", "", 1), ("STEP", "End of Previous Transformation", "", 2)]
	method : EnumProperty(name="Zero-Value Keyframes", items=item)

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if ob.type in {'MESH','CURVE'}:
				if (ob.active_shape_key):
					return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=350)
	def draw(self, context):
		row = self.layout.split(factor=0.45)
		rowrow = row.split(factor=0.9).split(factor=0.4)
		rowrow.label(text="Interval")
		rowrow.prop(self, 'interval', text="")
		row.prop(self, 'set_max')
		sp = self.layout.split(factor=0.45)
		sp.label(text="Zero-Value Keyframes")
		sp.prop(self, 'method', text="")

	def execute(self, context):
		keybrocks = context.active_object.data.shape_keys.key_blocks
		start = context.scene.frame_current
		end_frames = [start + t*self.interval for t in range(1, len(keybrocks)+1)]
		if self.set_max:
			valuse = [s.value for s in keybrocks]
		else:
			valuse = [1] * len(keybrocks)
		if self.method == 'CURRENT':
			start_frames = [start] * len(keybrocks)
		elif self.method == 'STEP':
			start_frames = [start] + end_frames[:-1]
		print(start_frames)
		for idx, shape in enumerate(keybrocks):
			context.scene.frame_current = start_frames[idx]
			shape.value = 0
			shape.keyframe_insert(data_path="value")
			context.scene.frame_current = end_frames[idx]
			shape.value = valuse[idx]
			shape.keyframe_insert(data_path="value")
		context.scene.frame_current = start
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class SelectShapeTop(bpy.types.Operator):
	bl_idname = "object.select_shape_top"
	bl_label = "Select Top"
	bl_description = "Select the top shape key"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if ob.type in {'MESH','CURVE'}:
				if (ob.data.shape_keys):
					if (2 <= len(ob.data.shape_keys.key_blocks)):
						return True
		return False

	def execute(self, context):
		context.active_object.active_shape_key_index = 0
		return {'FINISHED'}

class SelectShapeBottom(bpy.types.Operator):
	bl_idname = "object.select_shape_bottom"
	bl_label = "Select Bottom"
	bl_description = "Select the bottom shape key"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if ob.type in {'MESH','CURVE'}:
				if (ob.data.shape_keys):
					if (2 <= len(ob.data.shape_keys.key_blocks)):
						return True
		return False

	def execute(self, context):
		context.active_object.active_shape_key_index = len(context.active_object.data.shape_keys.key_blocks) - 1
		return {'FINISHED'}

class ShapeKeyApplyRemoveAll(bpy.types.Operator):
	bl_idname = "object.shape_key_apply_remove_all"
	bl_label = "Transform to Current Shape (Remove all keys)"
	bl_description = "Transform mesh to the current shape and remove all shape keys"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob) and ob.mode == 'OBJECT':
			if ob.type in {'MESH','CURVE'}:
				if (ob.data.shape_keys):
					if (2 <= len(ob.data.shape_keys.key_blocks)):
						return True
		return False

	def execute(self, context):
		bpy.ops.object.shape_key_add(from_mix=True)
		bpy.ops.object.shape_key_move(type='DOWN')
		bpy.ops.object.mode_set(mode='EDIT', toggle=False)
		bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
		bpy.ops.object.shape_key_remove(all=True)
		return {'FINISHED'}

class ShapeKeyApplyInverseBase(bpy.types.Operator):
	bl_idname = "object.shape_key_apply_inverse_base"
	bl_label = "Transform to Current Shape (Switch to Base)"
	bl_description = "Transform mesh to the current shape and remove all shape keys"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob and ob.mode == 'OBJECT':
			if ob.type in {'MESH','CURVE'}:
				if (ob.data.shape_keys):
					if (2 <= len(ob.data.shape_keys.key_blocks)):
						return True
		return False

	def execute(self, context):
		obj = context.active_object
		me = obj.data
		name = f"{me.shape_keys.key_blocks[0].name}_original"
		obj.active_shape_key_index = 0
		bpy.ops.mesh.copy_shape()
		me.shape_keys.key_blocks[-1].name = name
		bpy.ops.object.shape_key_add(from_mix=True)
		bpy.ops.object.shape_key_move(type='UP')
		obj.active_shape_key_index = 0
		while len(me.shape_keys.key_blocks) > 2:
			bpy.ops.object.shape_key_remove()
		return {'FINISHED'}

class AddLinkDriverShapeKeys(bpy.types.Operator):
	bl_idname = "object.add_link_driver_shape_keys"
	bl_label = "Link Shape Keys with Same Name by Driver"
	bl_description = "Add drivers to selected objects' shape keys, and make them follow the active object's shape keys with same name"
	bl_options = {'REGISTER', 'UNDO'}

	add_shape_key : BoolProperty(name="Add Missing Shapes to Active Object", default=True)

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type in {'MESH','CURVE'}:
				if ob.data.shape_keys:
					for obj in context.selected_objects:
						if ob.name == obj.name:
							continue
						if ob.type in {'MESH','CURVE'}:
							if obj.data.shape_keys:
								return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		self.layout.prop(self, 'add_shape_key')

	def execute(self, context):
		active_ob = context.active_object
		active_key = active_ob.data.shape_keys
		for ob in context.selected_objects:
			if active_ob.name == ob.name:
				continue
			key = ob.data.shape_keys
			for shape in key.key_blocks:
				if shape.name not in active_key.key_blocks.keys():
					if self.add_shape_key:
						bpy.ops.object.shape_key_add(from_mix=False)
						active_key.key_blocks[-1].name = shape.name
				if shape.name in active_key.key_blocks.keys():
					driver = key.driver_add('key_blocks["' + shape.name + '"].value').driver
					driver.type = 'AVERAGE'
					variable = driver.variables.new()
					target = variable.targets[0]
					target.id_type = 'KEY'
					target.id = active_key
					target.data_path = 'key_blocks["' + shape.name + '"].value'
		return {'FINISHED'}

class mute_all_shape_keys(bpy.types.Operator):
	bl_idname = "object.mute_all_shape_keys"
	bl_label = "Disable / Enable All Shapes"
	bl_description = "Enable or disable all shape keys"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('ENABLE', "Enabled", "", 1),
		('DISABLE', "Disabled", "", 2),
		]
	mode : EnumProperty(items=items, name="Mode")

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type in {'MESH','CURVE'}:
				if ob.data.shape_keys:
					if len(ob.data.shape_keys.key_blocks):
						return True
		return False

	def execute(self, context):
		ob = context.active_object
		for key in ob.data.shape_keys.key_blocks:
			if self.mode == 'ENABLE':
				key.mute = False
			elif self.mode == 'DISABLE':
				key.mute = True
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	CopyShape,
	InsertKeyframeAllShapes,
	InsertKeyframeWithInverval,
	SelectShapeTop,
	SelectShapeBottom,
	ShapeKeyApplyRemoveAll,
	ShapeKeyApplyInverseBase,
	AddLinkDriverShapeKeys,
	mute_all_shape_keys
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
		self.layout.operator(SelectShapeTop.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectShapeBottom.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(mute_all_shape_keys.bl_idname, icon='PLUGIN', text="Disable All").mode = 'DISABLE'
		self.layout.operator(mute_all_shape_keys.bl_idname, icon='PLUGIN', text="Enable All").mode = 'ENABLE'
		self.layout.separator()
		self.layout.operator(CopyShape.bl_idname, icon='PLUGIN')
		self.layout.operator(ShapeKeyApplyRemoveAll.bl_idname, icon='PLUGIN')
		self.layout.operator(ShapeKeyApplyInverseBase.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(InsertKeyframeAllShapes.bl_idname, icon='PLUGIN')
		self.layout.operator(InsertKeyframeWithInverval.bl_idname, icon='PLUGIN')
		self.layout.operator(AddLinkDriverShapeKeys.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
