# 「3Dビュー」エリア > プロパティ > 「ビュー」パネル
# "3D View" Area > Propaties > "View" Panel

import bpy

################
# オペレーター #
################

class SaveView(bpy.types.Operator):
	bl_idname = "view3d.save_view"
	bl_label = "Save View"
	bl_description = "Save current 3D view perspective"
	bl_options = {'REGISTER', 'UNDO'}
	
	save_name = bpy.props.StringProperty(name="Name", default="View Save Data")
	
	def execute(self, context):
		data = ""
		for line in context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata.split('|'):
			if (line == ""):
				continue
			try:
				save_name = line.split(':')[0]
			except ValueError:
				context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata = ""
				self.report(type={'ERROR'}, message="Failed load view, reseted save data")
				return {'CANCELLED'}
			if (str(self.save_name) == save_name):
				continue
			data = data + line + '|'
		text = data + str(self.save_name) + ':'
		co = context.region_data.view_location
		text = text + str(co[0]) + ',' + str(co[1]) + ',' + str(co[2]) + ':'
		ro = context.region_data.view_rotation
		text = text + str(ro[0]) + ',' + str(ro[1]) + ',' + str(ro[2]) + ',' + str(ro[3]) + ':'
		text = text + str(context.region_data.view_distance) + ':'
		text = text + context.region_data.view_perspective
		context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata = text
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class LoadView(bpy.types.Operator):
	bl_idname = "view3d.load_view"
	bl_label = "Load View"
	bl_description = "Load to current 3D view perspective"
	bl_options = {'REGISTER', 'UNDO'}
	
	index = bpy.props.StringProperty(name="View save data name", default="View Save Data")
	
	def execute(self, context):
		for line in context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata.split('|'):
			if (line == ""):
				continue
			try:
				index, loc, rot, distance, view_perspective = line.split(':')
			except ValueError:
				context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata = ""
				self.report(type={'ERROR'}, message="Failed load view, reseted save data")
				return {'CANCELLED'}
			if (str(self.index) == index):
				for i, v in enumerate(loc.split(',')):
					context.region_data.view_location[i] = float(v)
				for i, v in enumerate(rot.split(',')):
					context.region_data.view_rotation[i] = float(v)
				context.region_data.view_distance = float(distance)
				context.region_data.view_perspective = view_perspective
				self.report(type={'INFO'}, message=str(self.index))
				break
		else:
			self.report(type={'WARNING'}, message="Save data does not exist")
		return {'FINISHED'}

class DeleteViewSavedata(bpy.types.Operator):
	bl_idname = "view3d.delete_view_savedata"
	bl_label = "Delete View Save"
	bl_description = "Removes all view save data"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata == ""):
			return False
		return True
	def execute(self, context):
		context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata = ""
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	SaveView,
	LoadView,
	DeleteViewSavedata
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
	for id in bpy.context.preferences.addons["Blender-Scramble-Addon-master"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.prop(context.preferences.view, 'use_zoom_to_mouse')
		self.layout.prop(context.preferences.view, 'use_rotate_around_active')
		self.layout.prop(context.scene, 'sync_mode')
		box = self.layout.box()
		col = box.column(align=True)
		col.operator(SaveView.bl_idname, icon="PLUGIN")
		if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata != ""):
			col.operator(DeleteViewSavedata.bl_idname, icon="PLUGIN")
		if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata):
			col = box.column(align=True)
			col.label(text="Load view save data", icon='PLUGIN')
			for line in context.preferences.addons["Blender-Scramble-Addon-master"].preferences.view_savedata.split('|'):
				if (line == ""):
					continue
				try:
					index = line.split(':')[0]
				except ValueError:
					pass
				col.operator(LoadView.bl_idname, text=index, icon="PLUGIN").index = index
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
