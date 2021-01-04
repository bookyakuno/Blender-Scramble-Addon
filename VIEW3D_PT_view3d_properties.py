# 「3Dビュー」エリア > プロパティ > 「ビュー」パネル
# "3D View" Area > Propaties > "View" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class SaveView(bpy.types.Operator):
	bl_idname = "view3d.save_view"
	bl_label = "Save Current View"
	bl_description = "Save current view's location, rotation and distance"
	bl_options = {'REGISTER', 'UNDO'}

	save_name : StringProperty(name="Name", default="View", options={'SKIP_SAVE'})
	is_overwrite : BoolProperty(name="Overwrite", default=False)
	method : EnumProperty(name="Method", items=[
		("1","Prefix","",1),("-1","Suffix","",2)])
	right : BoolProperty(name="Right", default=False)
	left : BoolProperty(name="Left", default=False)	
	front : BoolProperty(name="Front", default=False)
	back : BoolProperty(name="Back", default=False)
	top : BoolProperty(name="Top", default=False)
	bottom : BoolProperty(name="Bottom", default=False)
	act_obj : BoolProperty(name="Active Object", default=False)
	act_camera : BoolProperty(name="Active Camera", default=False)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=330)
	def draw(self, context):
		row = self.layout.split(factor=0.7)
		row.prop(self, 'save_name')
		row.prop(self, 'is_overwrite')
		box = self.layout.box()
		row = box.row()
		row.label(text="Add")
		row.box().row().prop(self, 'method', expand=True)
		row = box.row()		
		for d in ['right','left','front','back','top','bottom']:
			row.prop(self, d, toggle=1)
			lis = [d.capitalize(), self.save_name]
			if eval(f"self.{d}"):
				self.save_name = "_".join(lis[::int(self.method)])
			exec(f"self.{d} = False")
		row = box.split(factor=0.15)
		row.label(text="Name")
		row.prop(self, 'act_obj', toggle=1)
		lis = [context.active_object.name, self.save_name]
		if self.act_obj:
			self.save_name = "_".join(lis[::int(self.method)])
			self.act_obj = False
		row.prop(self, 'act_camera', toggle=1)
		lis = [context.scene.camera.name, self.save_name]
		if self.act_camera:
			self.save_name = "_".join(lis[::int(self.method)])
			self.act_camera = False

	def execute(self, context):
		view_datas = context.scene.scramble_vd_prop
		if len(view_datas) > 0:
			names = [vd.data_name for vd in view_datas]
		else:
			names = None
		if names and self.save_name in names:
			if self.is_overwrite:
				new_vd = view_datas[names.index(self.save_name)]
			else:
				new_vd = view_datas.add()
				i = 1
				new_name = f"{self.save_name}.{i:03}"
				while new_name in names:
					i += 1
					new_name = f"{self.save_name}.{i:03}"
				new_vd.data_name = new_name
		else:
			new_vd = view_datas.add()
			new_vd.data_name = self.save_name
		rdata = context.region_data
		new_vd.location = ",".join([str(x) for x in rdata.view_location])
		new_vd.rotation = ",".join([str(x) for x in rdata.view_rotation])
		new_vd.distance = rdata.view_distance
		new_vd.perspective = rdata.view_perspective
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class LoadView(bpy.types.Operator):
	bl_idname = "view3d.load_view"
	bl_label = "Load Other View"
	bl_description = "Change view's location, rotation and distance to saved values"
	bl_options = {'REGISTER',}

	target : StringProperty(name="Target", default="")

	def execute(self, context):
		view_datas = context.scene.scramble_vd_prop
		names = [vd.data_name for vd in view_datas]
		target_vd = view_datas[names.index(self.target)]
		for i, v in enumerate(target_vd.location.split(',')):
			context.region_data.view_location[i] = float(v)
		for i, v in enumerate(target_vd.rotation.split(',')):
			context.region_data.view_rotation[i] = float(v)
		context.region_data.view_distance = target_vd.distance
		context.region_data.view_perspective = target_vd.perspective
		self.report(type={'INFO'}, message=self.target)
		return {'FINISHED'}

class DeleteViewSavedata(bpy.types.Operator):
	bl_idname = "view3d.delete_view_savedata"
	bl_label = "Delete View Data"
	bl_description = "Remove saved view's information"
	bl_options = {'REGISTER',}

	target : StringProperty(name="Target", default="", options={'HIDDEN'})

	def execute(self, context):
		view_datas = context.scene.scramble_vd_prop
		names = [vd.data_name for vd in view_datas]
		view_datas.remove(names.index(self.target))
		return {'FINISHED'}

class ScrambleViewDataPropGroup(bpy.types.PropertyGroup):
	data_name : bpy.props.StringProperty(name="Name", default="")
	location : bpy.props.StringProperty(name="Location", default="")
	rotation : bpy.props.StringProperty(name="Rotation", default="")
	distance : bpy.props.FloatProperty(name="Distance", default=0.0)
	perspective : bpy.props.StringProperty(name="Perspective", default="")

################
# クラスの登録 #
################

classes = [
	SaveView,
	LoadView,
	DeleteViewSavedata,
	ScrambleViewDataPropGroup
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.scramble_vd_prop = bpy.props.CollectionProperty(type=ScrambleViewDataPropGroup)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.scramble_vd_prop


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
		col = self.layout.column()
		col.use_property_split = False
		col.prop(context.preferences.inputs, 'use_zoom_to_mouse')
		col.prop(context.preferences.inputs, 'use_rotate_around_active')
		self.layout.prop(context.scene, 'sync_mode')
		box = self.layout.box()
		box.operator(SaveView.bl_idname, icon="PLUGIN")
		view_datas = context.scene.scramble_vd_prop
		if view_datas and len(view_datas) > 0:
			box.label(text="Load Other View", icon='PLUGIN')
			for name in [vd.data_name for vd in view_datas]:
				row = box.row()
				row.operator(LoadView.bl_idname, text=name).target = name
				row.operator(DeleteViewSavedata.bl_idname, icon="CANCEL", text="").target = name
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
