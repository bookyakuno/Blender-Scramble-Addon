# 「プロパティ」エリア > 「オブジェクト」タブ
# "Propaties" Area > "Object" Tab

import bpy
from bpy.props import *

################
# オペレーター #
################

class DataNameToObjectName(bpy.types.Operator):
	bl_idname = "object.data_name_to_object_name"
	bl_label = "Change Object's Name to Data's Name"
	bl_description = "Change the object's name to the same as its data's name"
	bl_options = {'REGISTER', 'UNDO'}

	apply_selected : BoolProperty(name="Apply to selected objects", default=False, options={'HIDDEN'})
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.data):
			return False
		return True

	def execute(self, context):
		if self.apply_selected:
			for obj in context.selected_objects:
				obj.name = obj.data.name
		else:
			context.object.name = context.object.data.name
		return {'FINISHED'}

class ObjectNameToDataName(bpy.types.Operator):
	bl_idname = "object.object_name_to_data_name"
	bl_label = "Change Data's Name to Object's Name"
	bl_description = "Change the data's name to the same as its object's name"
	bl_options = {'REGISTER', 'UNDO'}

	apply_selected : BoolProperty(name="Apply to selected objects", default=False, options={'HIDDEN'})

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.data):
			return False
		return True

	def execute(self, context):
		if self.apply_selected:
			for obj in context.selected_objects:
				obj.data.name = obj.name
		else:
			context.object.data.name = context.object.name
		return {'FINISHED'}

class CopyObjectName(bpy.types.Operator):
	bl_idname = "object.copy_object_name"
	bl_label = "Copy Object Name to Clipboard"
	bl_description = "Copy the active object's name to Clipboard"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (context.window_manager.clipboard == context.object.name):
			return False
		return True
	def execute(self, context):
		context.window_manager.clipboard = context.object.name
		self.report(type={'INFO'}, message=context.object.name)
		return {'FINISHED'}

class CopyDataName(bpy.types.Operator):
	bl_idname = "object.copy_data_name"
	bl_label = "Copy Data Name to Clipboard"
	bl_description = "Copy the data's name of active object's to Clipboard"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.data):
			return False
		if (context.window_manager.clipboard == context.object.data.name):
			return False
		return True
	def execute(self, context):
		context.window_manager.clipboard = context.object.data.name
		self.report(type={'INFO'}, message=context.object.data.name)
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	DataNameToObjectName,
	ObjectNameToDataName,
	CopyObjectName,
	CopyDataName
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
		row = self.layout.split(factor=0.55)
		#row.alignment = 'RIGHT'
		box = row.box().row(align=True)
		box.label(text="To Clipboard", icon='COPYDOWN')
		box.operator('object.copy_object_name', icon='OBJECT_DATAMODE', text="")
		if (context.active_bone or context.active_pose_bone):
			box.operator('object.copy_bone_name', icon='BONE_DATA', text="")# BONE_PT_context_bone.py で定義
		box.operator('object.copy_data_name', icon='EDITMODE_HLT', text="")
		box = row.box().row(align=True)
		box.label(text="Match Names", icon='LINKED')
		box.operator('object.object_name_to_data_name', icon='TRIA_DOWN_BAR', text="")
		box.operator('object.data_name_to_object_name', icon='TRIA_UP_BAR', text="")
		self.layout.template_ID(context.object, 'data')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
