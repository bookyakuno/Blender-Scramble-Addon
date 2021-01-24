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

################
# クラスの登録 #
################

classes = [
	CopyShape,
	SelectShapeTop,
	SelectShapeBottom,
	AddLinkDriverShapeKeys,
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
		self.layout.operator(CopyShape.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(AddLinkDriverShapeKeys.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(SelectShapeTop.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectShapeBottom.bl_idname, icon='PLUGIN')

	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
