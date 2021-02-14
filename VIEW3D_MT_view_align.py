# 「3Dビュー」エリア > 「ビュー」メニュー > 「視点を揃える」メニュー
# "3D View" Area > "View" Menu > "Align View" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class ViewSelectedEX(bpy.types.Operator):
	bl_idname = "view3d.view_selected_ex"
	bl_label = "Center View to Selected (Non-Zoom)"
	bl_description = "Center the view keeping current distance so that selected in the middle of the view"
	bl_options = {'REGISTER'}

	def execute(self, context):
		pre_view_location = context.region_data.view_location[:]
		smooth_view = context.preferences.view.smooth_view
		context.preferences.view.smooth_view = 0
		view_distance = context.region_data.view_distance
		bpy.ops.view3d.view_selected()
		context.region_data.view_distance = view_distance
		context.preferences.view.smooth_view = smooth_view
		context.region_data.update()
		new_view_location = context.region_data.view_location[:]
		context.region_data.view_location = pre_view_location[:]
		pre_cursor_location = bpy.context.scene.cursor.location[:]
		bpy.context.scene.cursor.location = new_view_location[:]
		bpy.ops.view3d.view_center_cursor()
		bpy.context.scene.cursor.location = pre_cursor_location[:]
		return {'FINISHED'}

class ResetView(bpy.types.Operator):
	bl_idname = "view3d.reset_view"
	bl_label = "Center View to Origin"
	bl_description = "Center the view so that origin in the middle of the view"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		pre_cursor_location = context.scene.cursor.location[:]
		context.scene.cursor.location = (0.0, 0.0, 0.0)
		bpy.ops.view3d.view_center_cursor()
		context.scene.cursor.location = pre_cursor_location[:]
		return {'FINISHED'}

class SelectAndView(bpy.types.Operator):
	bl_idname = "view3d.select_and_view"
	bl_label = "Center View to Mouse & Select Object"
	bl_description = "Select object under the mouse cursor, and center the view so that it in the middle of the view"
	bl_options = {'REGISTER'}

	zoom : BoolProperty(name="Zoom", default=False)
	mouse_loc : IntVectorProperty(name="Mouse Position", size=2, options={'HIDDEN'})
	isExtend : BoolProperty(name="Select Additional", default=False, options={'HIDDEN'})

	def invoke(self, context, event):
		self.mouse_loc[0] = event.mouse_region_x
		self.mouse_loc[1] = event.mouse_region_y
		self.isExtend = event.shift
		return self.execute(context)

	def execute(self, context):
		bpy.ops.view3d.select(location=self.mouse_loc, extend=self.isExtend)
		if not self.zoom:
			bpy.ops.view3d.view_selected_ex()
		else:
			bpy.ops.view3d.view_selected()
		return {'FINISHED'}

class ReverseView(bpy.types.Operator):
	bl_idname = "view3d.reverse_view"
	bl_label = "View from Opposite Side"
	bl_description = "Orbit the view around 180 degree and move to opposite side of current view"
	bl_options = {'REGISTER'}

	def execute(self, context):
		view_rotation = context.region_data.view_rotation.copy().to_euler()
		view_rotation.rotate_axis('Y', 3.1415926535)
		context.region_data.view_rotation = view_rotation.copy().to_quaternion()
		return {'FINISHED'}

class ResetViewAndCursor(bpy.types.Operator):
	bl_idname = "view3d.reset_view_and_cursor"
	bl_label = "Center View to Origin & Move 3D Cursor"
	bl_description = "Center the view so that origin in the middle of the view, and move 3D cursor to origin"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.context.scene.cursor.location = (0, 0, 0)
		bpy.ops.view3d.view_center_cursor()
		return {'FINISHED'}

class SnapMeshViewAndCursor(bpy.types.Operator):
	bl_idname = "view3d.snap_mesh_view_and_cursor"
	bl_label ="Center View to Mouse & Move 3D Cursor"
	bl_description = "Center the view to the mouse cursor and move 3D cursor there"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.ops.view3d.view_center_pick('INVOKE_DEFAULT')
		context.scene.cursor.location = context.region_data.view_location
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	ViewSelectedEX,
	ResetView,
	SelectAndView,
	ReverseView,
	ResetViewAndCursor,
	SnapMeshViewAndCursor
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
		self.layout.operator(ViewSelectedEX.bl_idname, icon="PLUGIN")
		self.layout.operator(ReverseView.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ResetView.bl_idname, icon="PLUGIN")
		self.layout.operator(ResetViewAndCursor.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator('view3d.view_center_pick')
		self.layout.operator(SnapMeshViewAndCursor.bl_idname, icon="PLUGIN")
		self.layout.operator(SelectAndView.bl_idname, icon="PLUGIN")

	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
