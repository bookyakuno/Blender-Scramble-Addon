# 「3Dビュー」エリア > メッシュの「編集」モード > 「選択」メニュー
# "3D View" Area > "Edit" Mode with Mesh > "Select" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class SelectAxisLimit(bpy.types.Operator):
	bl_idname = "mesh.select_axis_limit"
	bl_label = "Select Vertex (X=0)"
	bl_description = "Select vertices which X-axis location is zero"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		("0", "X Axis", "", 1),
		("1", "Y Axis", "", 2),
		("2", "Z Axis", "", 3),
		]
	axis : EnumProperty(items=items, name="Axis")
	offset : FloatProperty(name="Offset", default=0.0, step=10, precision=3)
	threshold : FloatProperty(name="Threshold", default=0.0000001, min=0.0, soft_min=0.0, step=0.1, precision=10)

	def execute(self, context):
		bpy.ops.object.mode_set(mode="OBJECT")
		sel_mode = context.tool_settings.mesh_select_mode[:]
		context.tool_settings.mesh_select_mode = [True, False, False]
		obj = context.active_object
		me = obj.data
		if (obj.type == "MESH"):
			for vert in me.vertices:
				co = [vert.co.x, vert.co.y, vert.co.z][int(self.axis)]
				if (-self.threshold <= co - self.offset <= self.threshold):
					vert.select = True
		bpy.ops.object.mode_set(mode="EDIT")
		context.tool_settings.mesh_select_mode = sel_mode
		return {'FINISHED'}

class SelectAxisOver(bpy.types.Operator):
	bl_idname = "mesh.select_axis_over"
	bl_label = "Select Vertex (One Side)"
	bl_description = "Select vertices on one side"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		("0", "X Axis", "", 1),
		("1", "Y Axis", "", 2),
		("2", "Z Axis", "", 3),
		]
	axis : EnumProperty(items=items, name="Axis")
	direction : EnumProperty(name="Direction", items=[
		("1", "Right / Top", "", 2),("-1", "Left / Bottom", "", 1)])
	offset : FloatProperty(name="Offset", default=0, step=10, precision=3)
	threshold : FloatProperty(name="Threshold", default=0.0000001, step=0.1, precision=10)

	def execute(self, context):
		bpy.ops.object.mode_set(mode="OBJECT")
		sel_mode = context.tool_settings.mesh_select_mode[:]
		context.tool_settings.mesh_select_mode = [True, False, False]
		obj = context.active_object
		me = obj.data
		if (obj.type == "MESH"):
			for vert in me.vertices:
				co = [vert.co.x, vert.co.y, vert.co.z][int(self.axis)]
				direct = int(self.direction)
				if (self.offset * direct <= co * direct + self.threshold):
					vert.select = True
		bpy.ops.object.mode_set(mode="EDIT")
		context.tool_settings.mesh_select_mode = sel_mode
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	SelectAxisLimit,
	SelectAxisOver
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
		self.layout.operator(SelectAxisLimit.bl_idname, icon="PLUGIN")
		self.layout.operator(SelectAxisOver.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
