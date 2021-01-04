# 「3Dビュー」エリア > 「視点を揃える」メニュー
# "3D View" Area > "View" Menu > "Align View" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class ViewSelectedEX(bpy.types.Operator):
	bl_idname = "view3d.view_selected_ex"
	bl_label = "Show Selected (non-zoom)"
	bl_description = "Selected ones over center of 3D perspective not (zoom)"
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
	bl_label = "Viewpoint at Origin"
	bl_description = "3D view perspective moves in center of coordinates"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		pre_cursor_location = context.scene.cursor.location[:]
		context.scene.cursor.location = (0.0, 0.0, 0.0)
		bpy.ops.view3d.view_center_cursor()
		context.scene.cursor.location = pre_cursor_location[:]
		return {'FINISHED'}

class SelectAndView(bpy.types.Operator):
	bl_idname = "view3d.select_and_view"
	bl_label = "Select and Set view center"
	bl_description = "Select object under mouse, in heart of point of view (SHIFT while additional choices)"
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
	bl_label = "Invert View"
	bl_description = "This reverses present view"
	bl_options = {'REGISTER'}

	def execute(self, context):
		view_rotation = context.region_data.view_rotation.copy().to_euler()
		view_rotation.rotate_axis('Y', 3.1415926535)
		context.region_data.view_rotation = view_rotation.copy().to_quaternion()
		return {'FINISHED'}

class ResetViewAndCursor(bpy.types.Operator):
	bl_idname = "view3d.reset_view_and_cursor"
	bl_label = "3D cursor with viewpoint at origin"
	bl_description = "Perspective and 3D cursor position move to starting point (XYZ=0.0)"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.context.scene.cursor.location = (0, 0, 0)
		bpy.ops.view3d.view_center_cursor()
		return {'FINISHED'}

class SnapMeshViewAndCursor(bpy.types.Operator):
	bl_idname = "view3d.snap_mesh_view_and_cursor"
	bl_label = "Snap mesh view and 3D cursor"
	bl_description = "(Please use shortcuts) move viewpoint and 3D cursor mesh surface under mouse"
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
