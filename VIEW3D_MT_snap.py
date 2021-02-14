# 「3Dビュー」エリア > 「ビュー」メニュー > 「表示切り替えメニュー」 > 「スナップメニュー (Blender 2.7)」
# "3D View" Area > "View" Menu > "Toggle Display" Menu > "Snap Menu (Blender 2.7)"

import bpy
from bpy.props import *

################
# オペレーター #
################

class SnapMesh3DCursor(bpy.types.Operator):
	bl_idname = "view3d.snap_mesh_3d_cursor"
	bl_label = "Cursor to Mouse"
	bl_description = "Move 3D cursor to the mouse cursor"
	bl_options = {'REGISTER'}

	def execute(self, context):
		pre_view = context.region_data.view_location[:]
		bpy.ops.view3d.view_center_pick('INVOKE_DEFAULT')
		context.scene.cursor.location = context.region_data.view_location
		context.region_data.view_location = pre_view
		return {'FINISHED'}

class Move3DCursorToViewLocation(bpy.types.Operator):
	bl_idname = "view3d.move_3d_cursor_to_view_location"
	bl_label = "Cursor to Center of View"
	bl_description = "Move 3D cursor to the center of viewport"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.context.scene.cursor.location = context.region_data.view_location[:]
		return {'FINISHED'}

class Move3DCursorFar(bpy.types.Operator):
	bl_idname = "view3d.move_3d_cursor_far"
	bl_label = "Cursor to Out of View"
	bl_description = "Move 3D cursor far away not to appear in viewport"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.context.scene.cursor.location = (24210, 102260, 38750)
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	SnapMesh3DCursor,
	Move3DCursorToViewLocation,
	Move3DCursorFar
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
		self.layout.operator(SnapMesh3DCursor.bl_idname, icon="PLUGIN")
		self.layout.operator(Move3DCursorToViewLocation.bl_idname, icon="PLUGIN")
		self.layout.operator(Move3DCursorFar.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
