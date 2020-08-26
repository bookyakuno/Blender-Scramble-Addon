# 「プロパティ」エリア > 「オブジェクト」タブ > 「表示」パネル
# "Propaties" Area > "Object" Tab > "Display" Panel

import bpy

################
# オペレーター #
################

class CopyDisplaySetting(bpy.types.Operator):
	bl_idname = "object.copy_display_setting"
	bl_label = "Copy Display Setting"
	bl_description = "Copy selected objects of other display settings"
	bl_options = {'REGISTER', 'UNDO'}
	
	copy_show_name = bpy.props.BoolProperty(name="Name", default=True)
	copy_show_axis = bpy.props.BoolProperty(name="Axis", default=True)
	copy_show_wire = bpy.props.BoolProperty(name="Wire Frame", default=True)
	copy_show_all_edges = bpy.props.BoolProperty(name="Show All Edges", default=True)
	copy_show_bounds = bpy.props.BoolProperty(name="Bound", default=True)
	copy_draw_bounds_type = bpy.props.BoolProperty(name="Bound Type", default=True)
	copy_show_texture_space = bpy.props.BoolProperty(name="Texture Space", default=True)
	copy_show_x_ray = bpy.props.BoolProperty(name="X-ray", default=True)
	copy_show_transparent = bpy.props.BoolProperty(name="Alpha", default=True)
	copy_draw_type = bpy.props.BoolProperty(name="Maximum Draw Type", default=True)
	copy_color = bpy.props.BoolProperty(name="Object Color", default=True)
	
	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) <= 1):
			return False
		return True
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		row = self.layout.row()
		row.prop(self, 'copy_show_name')
		row.prop(self, 'copy_show_bounds')
		row = self.layout.row()
		row.label(text="")
		row.prop(self, 'copy_draw_bounds_type')
		row = self.layout.row()
		row.prop(self, 'copy_show_axis')
		row.prop(self, 'copy_show_texture_space')
		row = self.layout.row()
		row.prop(self, 'copy_show_wire')
		row.prop(self, 'copy_show_x_ray')
		row = self.layout.row()
		row.prop(self, 'copy_show_all_edges')
		row.prop(self, 'copy_show_transparent')
		row = self.layout.row()
		row.prop(self, 'copy_draw_type')
		row.prop(self, 'copy_color')
	
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
				if (self.copy_draw_bounds_type):
					obj.draw_bounds_type = active_obj.draw_bounds_type
				if (self.copy_show_texture_space):
					obj.show_texture_space = active_obj.show_texture_space
				if (self.copy_show_x_ray):
					obj.show_x_ray = active_obj.show_x_ray
				if (self.copy_show_transparent):
					obj.show_transparent = active_obj.show_transparent
				if (self.copy_draw_type):
					obj.draw_type = active_obj.draw_type
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
		op = sub.operator('wm.context_set_string', icon='MESH_CUBE', text="")
		op.data_path, op.value = 'active_object.draw_type', 'BOUNDS'
		op = sub.operator('wm.context_set_string', icon='WIRE', text="")
		op.data_path, op.value = 'active_object.draw_type', 'WIRE'
		op = sub.operator('wm.context_set_string', icon='SOLID', text="")
		op.data_path, op.value = 'active_object.draw_type', 'SOLID'
		op = sub.operator('wm.context_set_string', icon='TEXTURE_SHADED', text="")
		op.data_path, op.value = 'active_object.draw_type', 'TEXTURED'
		row.operator(CopyDisplaySetting.bl_idname, icon='MESH_UVSPHERE')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
