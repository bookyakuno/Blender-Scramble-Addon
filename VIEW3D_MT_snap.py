# 「3Dビュー」エリア > 「Shift + S」キー
# "3D View" Area > "Shift + S" Key

import bpy
from bpy.props import *

################
# オペレーター #
################

class SnapMesh3DCursor(bpy.types.Operator):
	bl_idname = "view3d.snap_mesh_3d_cursor"
	bl_label = "3D Cursor Snap to Mesh"
	bl_description = "(Please use shortcuts) mesh surface under mouse move 3D cursor"
	bl_options = {'REGISTER'}

	mouse_co : IntVectorProperty(name="Mouse Position", size=2)

	def execute(self, context):
		preGp = context.scene.grease_pencil
		preGpSource = context.scene.tool_settings.grease_pencil_source
		context.scene.tool_settings.grease_pencil_source = 'SCENE'
		if (preGp):
			tempGp = preGp
		else:
			try:
				tempGp = bpy.data.grease_pencil["temp"]
			except KeyError:
				tempGp = bpy.data.grease_pencil.new("temp")
		context.scene.grease_pencil = tempGp
		tempLayer = tempGp.layers.new("temp", set_active=True)
		tempGp.draw_mode = 'SURFACE'
		bpy.ops.gpencil.draw(mode='DRAW_POLY', stroke=[{"name":"", "pen_flip":False, "is_start":True, "location":(0, 0, 0),"mouse":self.mouse_co, "pressure":1, "time":0, "size":0}, {"name":"", "pen_flip":False, "is_start":True, "location":(0, 0, 0),"mouse":(0, 0), "pressure":1, "time":0, "size":0}])
		bpy.context.scene.cursor.location = tempLayer.frames[-1].strokes[-1].points[0].co
		tempGp.layers.remove(tempLayer)
		context.scene.grease_pencil = preGp
		context.scene.tool_settings.grease_pencil_source = preGpSource
		return {'FINISHED'}
	def invoke(self, context, event):
		self.mouse_co[0] = event.mouse_region_x
		self.mouse_co[1] = event.mouse_region_y
		return self.execute(context)

class Move3DCursorToViewLocation(bpy.types.Operator):
	bl_idname = "view3d.move_3d_cursor_to_view_location"
	bl_label = "3D cursor to view"
	bl_description = "Move 3D cursor to location of center point of"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.context.scene.cursor.location = context.region_data.view_location[:]
		return {'FINISHED'}

class Move3DCursorFar(bpy.types.Operator):
	bl_idname = "view3d.move_3d_cursor_far"
	bl_label = "Hide 3D Cursor (move far)"
	bl_description = "Pretend to hide 3D cursor to move far far away"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.context.scene.cursor.location = (24210, 102260, 38750)
		return {'FINISHED'}


class PieSnapGrid(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_snap_pie_grid"
	bl_label = "Snap Menu (Grid)"

	def draw(self, context):
		layout = self.layout
		pie = layout.menu_pie()
		box = pie.split().column()
		box.operator("view3d.snap_mesh_3d_cursor", text="Cursor to Grid", icon='CURSOR')
		box.operator("view3d.snap_cursor_to_grid", text="Cursor to Grid", icon='CURSOR')


class PieSnapMore(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_snap_pie_more"
	bl_label = "Snap Menu (Scramble Addon)"

	def draw(self, context):
		layout = self.layout
		pie = layout.menu_pie()
		box = pie.split().column()
		box.operator("view3d.move_3d_cursor_to_view_location", text="Cursor => View Positon", icon='CURSOR')
		box.operator("view3d.move_3d_cursor_far", text="Hide 3D Cursor (move far)", icon='CURSOR')
		box.operator("view3d.snap_mesh_3d_cursor", text="Cursor => Mesh surface", icon='CURSOR')


class PieSnap(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_snap_pie_scramble"
	bl_label = "Snap Pie Menu (new menu added)"

	def draw(self, context):
		layout = self.layout
		pie = layout.menu_pie()
		# 4 - LEFT
		pie.menu("VIEW3D_MT_snap_pie_grid", text="Snap Menu (Grid)", icon='SNAP_GRID')
		# 6 - RIGHT
		pie.menu("VIEW3D_MT_snap_pie_more", text="Snap Menu (Scramble Addon)", icon='PLUGIN')
		# 2 - BOTTOM
		pie.operator("view3d.snap_cursor_to_selected", text="Cursor to Selected",
					icon='CURSOR')
		# 8 - TOP
		pie.operator("view3d.snap_selected_to_cursor", text="Selection to Cursor",
					icon='RESTRICT_SELECT_OFF').use_offset = False
		# 7 - TOP - LEFT
		pie.operator("view3d.snap_selected_to_cursor", text="Selection to Cursor (Keep Offset)", icon='RESTRICT_SELECT_OFF').use_offset = True
		# 9 - TOP - RIGHT
		pie.operator("view3d.snap_selected_to_active", text="Selection to Active", icon='RESTRICT_SELECT_OFF')
		# 1 - BOTTOM - LEFT
		pie.operator("view3d.snap_cursor_to_center", text="Cursor to World Origin", icon='CURSOR')
		# 3 - BOTTOM - RIGHT
		pie.operator("view3d.snap_cursor_to_active", text="Cursor to Active", icon='CURSOR')


################
# クラスの登録 #
################

classes = [
	SnapMesh3DCursor,
	Move3DCursorToViewLocation,
	Move3DCursorFar,
	PieSnapGrid,
	PieSnapMore,
	PieSnap
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
		self.layout.operator(Move3DCursorToViewLocation.bl_idname, text="Cursor => View Positon", icon="PLUGIN")
		self.layout.operator(Move3DCursorFar.bl_idname, text="Hide Cursor (Move Far)", icon="PLUGIN")
		self.layout.operator(SnapMesh3DCursor.bl_idname, text="Cursor => Mesh surface", icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
