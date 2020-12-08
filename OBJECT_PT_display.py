# 「プロパティ」エリア > 「オブジェクト」タブ > 「表示」パネル
# "Propaties" Area > "Object" Tab > "Display" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class CopyDisplaySetting(bpy.types.Operator):
	bl_idname = "object.copy_display_setting"
	bl_label = "Copy Display Setting"
	bl_description = "Copy selected objects of other display settings"
	bl_options = {'REGISTER', 'UNDO'}

	copy_show_name : BoolProperty(name="Name", default=True)
	copy_show_axis : BoolProperty(name="Axis", default=True)
	copy_show_wire : BoolProperty(name="Wireframe", default=True)
	copy_show_all_edges : BoolProperty(name="Show All Edges", default=True)
	copy_show_bounds : BoolProperty(name="Bounds", default=True)
	copy_display_bounds_type : BoolProperty(name="Boundary Display Type", default=True)
	copy_show_texture_space : BoolProperty(name="Texture Space", default=True)
	copy_show_shadows : BoolProperty(name="Shadow", default=True)
	copy_show_in_front : BoolProperty(name="In Front", default=True)
	#copy_show_transparent : BoolProperty(name="Display Color with Alpha", default=True)
	copy_display_type : BoolProperty(name="Display As", default=True)
	copy_color : BoolProperty(name="Object Color", default=True)

	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) <= 1):
			return False
		return True

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		row = self.layout.row()
		column = row.column().box()
		column.prop(self, 'copy_show_name')
		column.prop(self, 'copy_show_axis')
		column.prop(self, 'copy_show_wire')
		column.prop(self, 'copy_show_all_edges')
		column.prop(self, 'copy_show_texture_space')
		column.prop(self, 'copy_show_shadows')
		column.prop(self, 'copy_show_in_front')
		column = row.column()
		box = column.box()
		box .prop(self, 'copy_color')
		#box .prop(self, 'copy_show_transparent')
		column.separator()
		box = column.box()
		box.prop(self, 'copy_display_type')
		column.separator()
		box = column.box()
		box.prop(self, 'copy_show_bounds')		
		box.prop(self, 'copy_display_bounds_type')

	def execute(self, context):
		active_obj = context.active_object
		for obj in context.selected_objects:
			if (obj.name != active_obj.name):
				if (self.copy_show_name):
					obj.show_name = active_obj.show_name
				if (self.copy_show_axis):
					obj.show_axis = active_obj.show_axis
				if (self.copy_show_wire):
					obj.show_wire = active_obj.show_wire
				if (self.copy_show_all_edges):
					obj.show_all_edges = active_obj.show_all_edges
				if (self.copy_show_bounds):
					obj.show_bounds = active_obj.show_bounds
				if (self.copy_display_bounds_type):
					obj.display_bounds_type = active_obj.display_bounds_type
				if (self.copy_show_texture_space):
					obj.show_texture_space = active_obj.show_texture_space
				if (self.copy_show_in_front):
					obj.show_in_front = active_obj.show_in_front
				if (self.copy_show_shadows):
					obj.copy_show_shadows = active_obj.copy_show_shadows
				#if (self.copy_show_transparent):
				#	obj.show_transparent = active_obj.show_transparent
				if (self.copy_display_type):
					obj.display_type = active_obj.display_type
				if (self.copy_color):
					obj.color = active_obj.color[:]
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	CopyDisplaySetting
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
		row = self.layout.row()
		sub = row.row(align=True)
		op = sub.operator('wm.context_set_string', icon='SHADING_BBOX', text="")
		op.data_path, op.value = 'active_object.display_type', 'BOUNDS'
		op = sub.operator('wm.context_set_string', icon='SHADING_WIRE', text="")
		op.data_path, op.value = 'active_object.display_type', 'WIRE'
		op = sub.operator('wm.context_set_string', icon='SHADING_SOLID', text="")
		op.data_path, op.value = 'active_object.display_type', 'SOLID'
		op = sub.operator('wm.context_set_string', icon='SHADING_TEXTURE', text="")
		op.data_path, op.value = 'active_object.display_type', 'TEXTURED'
		row.operator(CopyDisplaySetting.bl_idname, icon='MESH_UVSPHERE')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
