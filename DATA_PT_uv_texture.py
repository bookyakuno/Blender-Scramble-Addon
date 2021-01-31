# 「プロパティ」エリア > 「オブジェクトデータ」タブ > 「UVマップ」パネル
# "Propaties" Area > "Object Data" Tab > "UV Maps" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class RenameSpecificNameUV(bpy.types.Operator):
	bl_idname = "object.rename_specific_name_uv"
	bl_label = "Rename specific UVs Together"
	bl_description = "Rename the selected objects' UV Maps with specific name to the designated one"
	bl_options = {'REGISTER', 'UNDO'}

	source_name : StringProperty(name="Target", default="")
	replace_name : StringProperty(name="New Name", default="New UV")

	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) == 0):
			return False
		return True

	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				continue
			me = obj.data
			for uv in me.uv_layers[:]:
				if (uv.name == self.source_name):
					uv.name = self.replace_name
		return {'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class DeleteSpecificNameUV(bpy.types.Operator):
	bl_idname = "object.delete_specific_name_uv"
	bl_label = "Delete specific UVs together"
	bl_description = "Remove the selected objects' UV Maps with specific name"
	bl_options = {'REGISTER', 'UNDO'}

	name : StringProperty(name="Name", default="UV")

	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) == 0):
			return False
		return True
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				continue
			me = obj.data
			for uv in me.uv_layers:
				if (uv.name == self.name):
					me.uv_layers.remove(uv)
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class RemoveUnselectedUV(bpy.types.Operator):
	bl_idname = "object.remove_unselected_uv"
	bl_label = "Remove Unselected UV"
	bl_description = "Remove Unselected UV Maps of the active object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (not obj):
			return False
		if (obj.type != 'MESH'):
			return False
		me = obj.data
		if (len(me.uv_layers) == 0):
			return False
		return True

	def execute(self, context):
		me = context.active_object.data
		#uv_layersにおいて、要素が削除されるとactiveが更新され頂点グループなどがuv_layersに追加されるバグ？があるので、name要素を指定してuv_layersへの参照を切る		
		pre_uv_name = me.uv_layers.active.name
		uv_names = [a.name for a in me.uv_layers]
		for uv in uv_names:
			if uv != pre_uv_name:
				me.uv_layers.remove(me.uv_layers[uv])
		me.uv_layers.active = me.uv_layers[pre_uv_name]
		return {'FINISHED'}

class MoveActiveUV(bpy.types.Operator):
	bl_idname = "object.move_active_uv"
	bl_label = "Move UV"
	bl_description = "Move the active UV up or down"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('UP', "To Up", "", 1),
		('DOWN', "To Down", "", 2),
		]
	mode : EnumProperty(items=items, name="Direction", default="UP")

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (not obj):
			return False
		if (obj.type != 'MESH'):
			return False
		me = obj.data
		if (len(me.uv_layers) <= 1):
			return False
		return True
	def execute(self, context):
		obj = context.active_object
		me = obj.data
		if (self.mode == 'UP'):
			if (me.uv_layers.active_index <= 0):
				return {'CANCELLED'}
			target_index = me.uv_layers.active_index - 1
		elif (self.mode == 'DOWN'):
			target_index = me.uv_layers.active_index + 1
			if (len(me.uv_layers) <= target_index):
				return {'CANCELLED'}
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		uv_layer = me.uv_layers.active
		target_uv_layer = me.uv_layers[target_index]
		uv_tex = me.uv_layers.active
		target_uv_tex = me.uv_layers[target_index]
		for data_name in dir(uv_tex):
			if (data_name[0] != '_' and data_name != 'bl_rna' and data_name != 'rna_type' and data_name != 'data'):
				temp = uv_tex.__getattribute__(data_name)
				target_temp = target_uv_tex.__getattribute__(data_name)
				target_uv_tex.__setattr__(data_name, temp)
				uv_tex.__setattr__(data_name, target_temp)
				target_uv_tex.__setattr__(data_name, temp)
				uv_tex.__setattr__(data_name, target_temp)
		for i in range(len(uv_layer.data)):
			for data_name in dir(uv_layer.data[i]):
				if (data_name[0] != '_' and data_name != 'bl_rna' and data_name != 'rna_type'):
					try:
						temp = target_uv_layer.data[i].__getattribute__(data_name)[:]
					except TypeError:
						temp = target_uv_layer.data[i].__getattribute__(data_name)
					target_uv_layer.data[i].__setattr__(data_name, uv_layer.data[i].__getattribute__(data_name))
					uv_layer.data[i].__setattr__(data_name, temp)
		for i in range(len(uv_tex.data)):
			temp = uv_tex.data[i].uv
			uv_tex.data[i].uv = target_uv_tex.data[i].uv
			target_uv_tex.data[i].uv = temp
		me.uv_layers.active_index = target_index
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

################
# サブメニュー #
################

class UVMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_uv"
	bl_label = "Bulk Manipulation"
	bl_description = "Manipulate selected objects' UV Maps together"

	def draw(self, context):
		self.layout.operator(RenameSpecificNameUV.bl_idname, icon="PLUGIN")
		self.layout.operator(DeleteSpecificNameUV.bl_idname, icon="PLUGIN")

################
# クラスの登録 #
################

classes = [
	RenameSpecificNameUV,
	DeleteSpecificNameUV,
	RemoveUnselectedUV,
	MoveActiveUV,
	UVMenu
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
		if (context.active_object.type == 'MESH'):
			if (context.active_object.data.uv_layers.active):
				row = self.layout.row()
				sub = row.row(align=True)
				sub.operator(MoveActiveUV.bl_idname, icon='TRIA_UP', text="").mode = 'UP'
				sub.operator(MoveActiveUV.bl_idname, icon='TRIA_DOWN', text="").mode = 'DOWN'
				row.operator(RemoveUnselectedUV.bl_idname, icon="PLUGIN")
				row.menu(UVMenu.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
