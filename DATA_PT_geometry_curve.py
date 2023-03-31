# 「プロパティ」エリア > 「カーブデータ」タブ > 「ジオメトリ」パネル
# "Propaties" Area > "Curve" Tab > "Geometry" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class CopyGeometrySettings(bpy.types.Operator):
	bl_idname = "curve.copy_geometry_settings"
	bl_label = "Copy Geometry Settings"
	bl_description = "Copy active curve's geometry settings to other selected curves"
	bl_options = {'REGISTER', 'UNDO'}

	offset : BoolProperty(name="Offset", default=True)
	extrude : BoolProperty(name="Extrude", default=True)
	bevel_depth : BoolProperty(name="Depth", default=True)
	bevel_resolution : BoolProperty(name="Resolution", default=True)
	taper_object : BoolProperty(name="Taper Object", default=True)
	bevel_object : BoolProperty(name="Bevel Object", default=True)
	bevel_factor_mapping_start : BoolProperty(name="Mapping Method (Start)", default=True)
	bevel_factor_mapping_end : BoolProperty(name="Mapping Method (End)", default=True)
	bevel_factor_start : BoolProperty(name="Bevel Start", default=True)
	bevel_factor_end : BoolProperty(name="Bevel End", default=True)
	use_map_taper : BoolProperty(name="Map Taper", default=True)
	use_fill_caps : BoolProperty(name="Fill Caps", default=True)

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.type == 'CURVE':
				if 2 <= len(context.selected_objects):
					for ob in context.selected_objects:
						if context.active_object.name != ob.name:
							if ob.type == 'CURVE':
								return True
		return False

	def invoke(self, context, event):
		self.offset = False
		self.extrude = False
		self.bevel_depth = False
		self.bevel_resolution = False
		self.taper_object = False
		self.bevel_object = False
		self.bevel_factor_mapping_start = False
		self.bevel_factor_start = False
		self.bevel_factor_mapping_end = False
		self.bevel_factor_end = False
		self.use_map_taper = False
		self.use_fill_caps = False

		curve = context.active_object.data
		if 0.0 < curve.offset:
			self.offset = True
		if 0.0 < curve.extrude:
			self.extrude = True
		if curve.taper_object:
			self.taper_object = True
			self.use_map_taper = True

		if curve.bevel_object:
			self.bevel_object = True
			self.bevel_factor_mapping_start = True
			self.bevel_factor_start = True
			self.bevel_factor_mapping_end = True
			self.bevel_factor_end = True
			self.use_fill_caps = True
		elif 0.0 < curve.bevel_depth:
			self.bevel_depth = True
			self.bevel_resolution = True
			self.bevel_factor_mapping_start = True
			self.bevel_factor_start = True
			self.bevel_factor_mapping_end = True
			self.bevel_factor_end = True

		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		row = self.layout.row()
		column = row.column().box()
		column.prop(self, 'offset')
		column.prop(self, 'extrude')
		column = row.column().box()
		column.label(text="Taper")
		column.prop(self, 'taper_object')
		column.prop(self, 'use_map_taper')
		box = self.layout.box()
		box.label(text="Bevel")
		row = box.row()
		row.prop(self, 'bevel_depth')
		row.prop(self, 'bevel_resolution')
		row = box.row()
		row.prop(self, 'bevel_object')
		row.prop(self, 'use_fill_caps')
		row = box.row()
		row.prop(self, 'bevel_factor_start')
		row.prop(self, 'bevel_factor_end')
		row = box.row()
		row.prop(self, 'bevel_factor_mapping_start')
		row.prop(self, 'bevel_factor_mapping_end')

	def execute(self, context):
		active_ob = context.active_object
		active_data = active_ob.data
		for ob in context.selected_objects:
			if ob.name != active_ob.name:
				if ob.type == 'CURVE':
					data = ob.data
					if self.offset:
						data.offset = active_data.offset
					if self.extrude:
						data.extrude = active_data.extrude
					if self.bevel_depth:
						data.bevel_depth = active_data.bevel_depth
					if self.bevel_resolution:
						data.bevel_resolution = active_data.bevel_resolution
					if self.taper_object:
						data.taper_object = active_data.taper_object
					if self.bevel_object:
						data.bevel_object = active_data.bevel_object
					if self.bevel_factor_mapping_start:
						data.bevel_factor_mapping_start = active_data.bevel_factor_mapping_start
					if self.bevel_factor_start:
						data.bevel_factor_start = active_data.bevel_factor_start
					if self.bevel_factor_mapping_end:
						data.bevel_factor_mapping_end = active_data.bevel_factor_mapping_end
					if self.bevel_factor_end:
						data.bevel_factor_end = active_data.bevel_factor_end
					if self.use_map_taper:
						data.use_map_taper = active_data.use_map_taper
					if self.use_fill_caps:
						data.use_fill_caps = active_data.use_fill_caps
		return {'FINISHED'}

class ActivateTaperObject(bpy.types.Operator):
	bl_idname = "curve.activate_taper_object"
	bl_label = "Activate Taper Object"
	bl_description = "Activate the taper object of this curve"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'CURVE':
				if ob.data.taper_object:
					return True
		return False

	def make_collec_dic(self, layer_collection, dictionary):
		for coll in layer_collection.children:
			dictionary[coll.name] = {"self":coll, "parent":layer_collection}
			if len(coll.children) > 0:
				dictionary = self.make_collec_dic(coll, dictionary)
		return dictionary

	def execute(self, context):
		ob = context.active_object.data.taper_object
		ob.hide_set(False)
		ob.select_set(True)
		context.active_object.select_set(False)
		dic = {}
		collec_dic = self.make_collec_dic(context.view_layer.layer_collection, dic)
		bpy.context.view_layer.objects.active = ob
		if ob.users_collection[0] != context.view_layer.layer_collection.collection:
			coll_name = ob.users_collection[0].name
			while coll_name != context.view_layer.layer_collection.name:
				collec_dic[coll_name]['self'].hide_viewport = False
				coll_name = collec_dic[coll_name]['parent'].name
		return {'FINISHED'}

class ActivateBevelObject(bpy.types.Operator):
	bl_idname = "curve.activate_bevel_object"
	bl_label = "Activate Bevel Object"
	bl_description = "Activate the bevel object of this curve"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'CURVE':
				if ob.data.bevel_object:
					return True
		return False

	def make_collec_dic(self, layer_collection, dictionary):
		for coll in layer_collection.children:
			dictionary[coll.name] = {"self":coll, "parent":layer_collection}
			if len(coll.children) > 0:
				dictionary = self.make_collec_dic(coll, dictionary)
		return dictionary

	def execute(self, context):
		ob = context.active_object.data.bevel_object
		ob.hide_set(False)
		ob.select_set(True)
		context.active_object.select_set(False)
		dic = {}
		collec_dic = self.make_collec_dic(context.view_layer.layer_collection, dic)
		bpy.context.view_layer.objects.active = ob
		if ob.users_collection[0] != context.view_layer.layer_collection.collection:
			coll_name = ob.users_collection[0].name
			while coll_name != context.view_layer.layer_collection.name:
				collec_dic[coll_name]['self'].hide_viewport = False
				coll_name = collec_dic[coll_name]['parent'].name
		return {'FINISHED'}

class ActivateTaperParentObject(bpy.types.Operator):
	bl_idname = "curve.activate_taper_parent_object"
	bl_label = "Activate Curve which Uses This for Taper"
	bl_description = "Activate curve object that uses this curve as Taper Object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		for curve in bpy.data.curves:
			target_name = curve.taper_object.name if curve.taper_object else ""
			if target_name == ob.name:
				return True
		return False

	def make_collec_dic(self, layer_collection, dictionary):
		for coll in layer_collection.children:
			dictionary[coll.name] = {"self":coll, "parent":layer_collection}
			if len(coll.children) > 0:
				dictionary = self.make_collec_dic(coll, dictionary)
		return dictionary

	def execute(self, context):
		dic = {}
		collec_dic = self.make_collec_dic(context.view_layer.layer_collection, dic)
		active_ob = context.active_object
		for ob in bpy.data.objects:
			if ob.type == 'CURVE':
				curve = ob.data
				target_name = curve.taper_object.name if curve.taper_object else ""
				if active_ob.name == target_name:
					ob.hide_set(False)
					ob.select_set(True)
					active_ob.select_set(False)
					bpy.context.view_layer.objects.active = ob
					if ob.users_collection[0] != context.view_layer.layer_collection.collection:
						coll_name = ob.users_collection[0].name
						while coll_name != context.view_layer.layer_collection.name:
							collec_dic[coll_name]['self'].hide_viewport = False
							coll_name = collec_dic[coll_name]['parent'].name
		return {'FINISHED'}

class ActivateBevelParentObject(bpy.types.Operator):
	bl_idname = "curve.activate_bevel_parent_object"
	bl_label = "Activate Curve which Uses This for Bevel"
	bl_description = "Activate curve object that uses this curve as Bevel Object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		for curve in bpy.data.curves:
			target_name = curve.bevel_object.name if curve.bevel_object else ""
			if target_name == ob.name:
				return True
		return False

	def make_collec_dic(self, layer_collection, dictionary):
		for coll in layer_collection.children:
			dictionary[coll.name] = {"self":coll, "parent":layer_collection}
			if len(coll.children) > 0:
				dictionary = self.make_collec_dic(coll, dictionary)
		return dictionary

	def execute(self, context):
		dic = {}
		collec_dic = self.make_collec_dic(context.view_layer.layer_collection, dic)
		active_ob = context.active_object
		for ob in bpy.data.objects:
			if ob.type == 'CURVE':
				curve = ob.data
				target_name = curve.bevel_object.name if curve.bevel_object else ""
				if active_ob.name == target_name:
					ob.hide_set(False)
					ob.select_set(True)
					active_ob.select_set(False)
					bpy.context.view_layer.objects.active = ob
					if ob.users_collection[0] != context.view_layer.layer_collection.collection:
						coll_name = ob.users_collection[0].name
						while coll_name != context.view_layer.layer_collection.name:
							collec_dic[coll_name]['self'].hide_viewport = False
							coll_name = collec_dic[coll_name]['parent'].name
		return {'FINISHED'}

class ChangeObjectResolution(bpy.types.Operator):
	bl_idname = "curve.change_object_resolution"
	bl_label = "Change Curve Object's Resolution"
	bl_description = "Change curve's resolution witch used as taper or bevel object"
	bl_options = {'REGISTER', 'UNDO'}

	ps = bpy.types.Curve.bl_rna.properties
	reso : IntProperty(name=ps["resolution_u"].name,
			description=ps["resolution_u"].description,
			min=0, max=1024, default=0)
	rend_reso : IntProperty(name=ps["render_resolution_u"].name,
			description=ps["render_resolution_u"].description,
			min=0, max=1024, default=0)
	is_taper : BoolProperty(name="Taper", default=False, options={'HIDDEN'})

	def invoke(self, context, event):
		return context.window_manager.invoke_props_popup(self, event)
	def execute(self, context):
		if self.is_taper:
			curve = context.active_object.data.taper_object.data
		else:
			curve = context.active_object.data.bevel_object.data
		curve.resolution_u = self.reso
		curve.render_resolution_u = self.rend_reso
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	CopyGeometrySettings,
	ActivateTaperObject,
	ActivateBevelObject,
	ActivateTaperParentObject,
	ActivateBevelParentObject,
	ChangeObjectResolution
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
		if context.active_object:
			data = context.active_object.data
			if data.taper_object:
				box = self.layout.box()
				sp = box.split(factor=0.4)
				sp.label(text="Taper Object", icon='PARTICLE_PATH')
				sp.operator(ActivateTaperObject.bl_idname, text="Activate", icon='RESTRICT_SELECT_OFF')
				sp.operator(ChangeObjectResolution.bl_idname, text="Resolution", icon='CURVE_DATA')
			if data.bevel_object:
				if not data.taper_object:
					box = self.layout.box()
				sp = box.split(factor=0.4)
				sp.label(text="Bevel Object", icon='OUTLINER_OB_SURFACE')
				sp.operator(ActivateBevelObject.bl_idname, text="Activate", icon='RESTRICT_SELECT_OFF')
				sp.operator(ChangeObjectResolution.bl_idname, text="Resolution", icon='CURVE_DATA')
		taper_objs = [c.taper_object for c in bpy.data.curves if c.taper_object]
		bevel_objs = [c.bevel_object for c in bpy.data.curves if c.bevel_object]
		if context.active_object in taper_objs + bevel_objs:
			row = self.layout.box().split(factor=0.5)
			row.label(text="Activate Object Using This For")
			row.operator(ActivateTaperParentObject.bl_idname, icon='PARTICLE_PATH', text="Taper")
			row.operator(ActivateBevelParentObject.bl_idname, icon='OUTLINER_OB_SURFACE', text="Bevel")
		if 2 <= len([ob.type for ob in context.selected_objects if ob.type=='CURVE']):
			self.layout.operator(CopyGeometrySettings.bl_idname, icon='COPY_ID')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
