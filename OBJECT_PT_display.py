# 「プロパティ」エリア > 「オブジェクト」タブ > 「ビューポート表示」パネル
# "Propaties" Area > "Object" Tab > "Viewport Display" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class CopyDisplaySetting(bpy.types.Operator):
	bl_idname = "object.copy_display_setting"
	bl_label = "Copy Display Setting"
	bl_description = "Copy active object's display settings to other selected objects"
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
	copy_display_type : BoolProperty(name="Display As", default=True)
	copy_color : BoolProperty(name="Object Color", default=True)
	only_same : BoolProperty(name="Copy to only same type", default=False)

	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) <= 1):
			return False
		return True

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		obj = context.active_object
		row = self.layout.split(factor=0.45)
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
		box.prop(self, 'copy_color')
		column.separator()
		box = column.box()
		box.prop(self, 'copy_display_type')
		column.separator()
		box = column.box()
		box.prop(self, 'copy_show_bounds')		
		box.prop(self, 'copy_display_bounds_type')
		column.separator()
		column.prop(self, 'only_same')
		row = column.row(align=True)
		row.label(text="Type")
		row.label(text=obj.type)

	def execute(self, context):
		ps = [
			'show_name','show_axis','show_wire',
			'show_all_edges','show_texture_space',
			'show_shadows','show_in_front','color',
			'display_type','show_bounds','display_bounds_type']
		active_obj = context.active_object
		other_objs = list(set(context.selected_objects) - {active_obj})
		for obj in other_objs:
			if not self.only_same or obj.type==active_obj.type:
				print(obj.type==active_obj.type)
				for p in ps:
					if eval(f"self.copy_{p}"):
						if p == 'show_shadows':
							exec(f"obj.display.{p} = active_obj.display.{p}")
						else:
							exec(f"obj.{p} = active_obj.{p}")
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
