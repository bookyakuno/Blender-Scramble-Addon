# 「3Dビュー」エリア > 「視点を揃える」メニュー
# "3D View" Area > "View" Menu > "Align View" Menu

import bpy

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
		pre_cursor_location = bpy.context.space_data.cursor_location[:]
		bpy.context.space_data.cursor_location = new_view_location[:]
		bpy.ops.view3d.view_center_cursor()
		bpy.context.space_data.cursor_location = pre_cursor_location[:]
		return {'FINISHED'}

class ResetView(bpy.types.Operator):
	bl_idname = "view3d.reset_view"
	bl_label = "Viewpoint at Origin"
	bl_description = "3D view perspective moves in center of coordinates"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		pre_cursor_location = context.space_data.cursor_location[:]
		context.space_data.cursor_location = (0.0, 0.0, 0.0)
		bpy.ops.view3d.view_center_cursor()
		context.space_data.cursor_location = pre_cursor_location[:]
		return {'FINISHED'}

class SelectAndView(bpy.types.Operator):
	bl_idname = "view3d.select_and_view"
	bl_label = "Select and Set view center"
	bl_description = "Select object under mouse, in heart of point of view (SHIFT while additional choices)"
	bl_options = {'REGISTER'}
	
	items = [
		("view_selected_ex", "No Zoom", "", 1),
		("view_selected", "Zoom", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="How to change view")
	mouse_loc = bpy.props.IntVectorProperty(name="Mouse Position", size=2)
	isExtend = bpy.props.BoolProperty(name="Select Additional", default=False)
	
	def execute(self, context):
		bpy.ops.view3d.select(location=self.mouse_loc, extend=self.isExtend)
		if (self.mode == "view_selected_ex"):
			bpy.ops.view3d.view_selected_ex()
		else:
			bpy.ops.view3d.view_selected()
		return {'FINISHED'}
	def invoke(self, context, event):
		self.mouse_loc[0] = event.mouse_region_x
		self.mouse_loc[1] = event.mouse_region_y
		self.isExtend = event.shift
		return self.execute(context)

class SnapMeshView(bpy.types.Operator):
	bl_idname = "view3d.snap_mesh_view"
	bl_label = "Snap view to mesh"
	bl_description = "(Please use shortcuts) move center point of view mesh surface under mouse"
	bl_options = {'MACRO'}
	
	mouse_co = bpy.props.IntVectorProperty(name="Mouse Position", size=2)
	
	def execute(self, context):
		preGp = context.scene.grease_pencil
		preGpSource = context.scene.tool_settings.grease_pencil_source
		preCursorCo = bpy.context.space_data.cursor_location[:]
		context.space_data.cursor_location = context.region_data.view_location[:]
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
		bpy.context.space_data.cursor_location = tempLayer.frames[-1].strokes[-1].points[0].co
		bpy.ops.view3d.view_center_cursor()
		bpy.context.space_data.cursor_location = preCursorCo
		tempGp.layers.remove(tempLayer)
		tempGp.user_clear()
		bpy.data.grease_pencil.remove(tempGp)
		context.scene.grease_pencil = preGp
		context.scene.tool_settings.grease_pencil_source = preGpSource
		return {'FINISHED'}
	def invoke(self, context, event):
		self.mouse_co[0] = event.mouse_region_x
		self.mouse_co[1] = event.mouse_region_y
		return self.execute(context)

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
		bpy.context.space_data.cursor_location = (0, 0, 0)
		bpy.ops.view3d.view_center_cursor()
		return {'FINISHED'}

class SnapMeshViewAndCursor(bpy.types.Operator):
	bl_idname = "view3d.snap_mesh_view_and_cursor"
	bl_label = "Snap mesh view and 3D cursor"
	bl_description = "(Please use shortcuts) move viewpoint and 3D cursor mesh surface under mouse"
	bl_options = {'REGISTER'}
	
	mouse_co = bpy.props.IntVectorProperty(name="Mouse Position", size=2)
	
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
		bpy.context.space_data.cursor_location = tempLayer.frames[-1].strokes[-1].points[0].co
		bpy.ops.view3d.view_center_cursor()
		tempGp.layers.remove(tempLayer)
		context.scene.grease_pencil = preGp
		context.scene.tool_settings.grease_pencil_source = preGpSource
		return {'FINISHED'}
	def invoke(self, context, event):
		self.mouse_co[0] = event.mouse_region_x
		self.mouse_co[1] = event.mouse_region_y
		return self.execute(context)

################
# クラスの登録 #
################

classes = [
	ViewSelectedEX,
	ResetView,
	SelectAndView,
	SnapMeshView,
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
		self.layout.operator(ResetView.bl_idname, icon="PLUGIN")
		self.layout.operator(ResetViewAndCursor.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ViewSelectedEX.bl_idname, icon="PLUGIN")
		self.layout.operator(SelectAndView.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SnapMeshView.bl_idname, icon="PLUGIN")
		self.layout.operator(SnapMeshViewAndCursor.bl_idname, icon="PLUGIN")
		self.layout.operator(ReverseView.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
