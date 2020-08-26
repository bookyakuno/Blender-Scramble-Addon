# 「プロパティ」エリア > 「カーブデータ」タブ > 「ジオメトリ」パネル
# "Propaties" Area > "Curve" Tab > "Geometry" Panel

import bpy

################
# オペレーター #
################

class copy_geometry_settings(bpy.types.Operator):
	bl_idname = "curve.copy_geometry_settings"
	bl_label = "Copy Geometry Settings"
	bl_description = "Copy selection curve of other settings panel geometry of curve object is active"
	bl_options = {'REGISTER', 'UNDO'}
	
	offset = bpy.props.BoolProperty(name="Offset", default=True)
	extrude = bpy.props.BoolProperty(name="Extrude", default=True)
	bevel_depth = bpy.props.BoolProperty(name="Depth", default=True)
	bevel_resolution = bpy.props.BoolProperty(name="Resolution", default=True)
	taper_object = bpy.props.BoolProperty(name="Taper", default=True)
	bevel_object = bpy.props.BoolProperty(name="Bevel", default=True)
	bevel_factor_mapping_start = bpy.props.BoolProperty(name="Start Method", default=True)
	bevel_factor_start = bpy.props.BoolProperty(name="Start", default=True)
	bevel_factor_mapping_end = bpy.props.BoolProperty(name="End Method", default=True)
	bevel_factor_end = bpy.props.BoolProperty(name="End", default=True)
	use_map_taper = bpy.props.BoolProperty(name="Map Taper", default=True)
	use_fill_caps = bpy.props.BoolProperty(name="Fill Caps", default=True)
	
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
		row.label("Modification:")
		row.label("Bevel:")
		row = self.layout.row()
		row.prop(self, 'offset')
		row.prop(self, 'bevel_depth')
		row = self.layout.row()
		row.prop(self, 'extrude')
		row.prop(self, 'bevel_resolution')
		row = self.layout.row()
		row.label("Objects:")
		row = self.layout.row()
		row.prop(self, 'taper_object')
		row.prop(self, 'bevel_object')
		row = self.layout.row()
		row.label("Bevel Factor:")
		row = self.layout.row()
		row.prop(self, 'bevel_factor_mapping_start')
		row.prop(self, 'bevel_factor_start')
		row = self.layout.row()
		row.prop(self, 'bevel_factor_mapping_end')
		row.prop(self, 'bevel_factor_end')
		row = self.layout.row()
		row.prop(self, 'use_map_taper')
		row.prop(self, 'use_fill_caps')
	
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
	bl_label = "Activate taper object"
	bl_description = "curve is specified as tapered object"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob.type == 'CURVE':
			if ob.data.taper_object:
				return True
		return False
	
	def execute(self, context):
		ob = context.active_object.data.taper_object
		ob.select = True
		ob.hide = False
		context.scene.objects.active = ob
		for i, b in enumerate(ob.layers):
			if b:
				context.scene.layers[i] = True
		return {'FINISHED'}

class ActivateBevelObject(bpy.types.Operator):
	bl_idname = "curve.activate_bevel_object"
	bl_label = "Activate Bevel Object"
	bl_description = "curve is specified as beveled objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob.type == 'CURVE':
			if ob.data.bevel_object:
				return True
		return False
	
	def execute(self, context):
		ob = context.active_object.data.bevel_object
		ob.select = True
		ob.hide = False
		context.scene.objects.active = ob
		for i, b in enumerate(ob.layers):
			if b:
				context.scene.layers[i] = True
		return {'FINISHED'}

class activate_taper_parent_object(bpy.types.Operator):
	bl_idname = "curve.activate_taper_parent_object"
	bl_label = "Used as taper curve to activate"
	bl_description = "Activates curve as tapered object using this curve"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		for curve in bpy.data.curves:
			target_name = curve.taper_object.name if curve.taper_object else ""
			if target_name == ob.name:
				return True
		return False
	
	def execute(self, context):
		count = 0
		active_ob = context.active_object
		for ob in bpy.data.objects:
			if ob.type == 'CURVE':
				curve = ob.data
				target_name = curve.taper_object.name if curve.taper_object else ""
				if active_ob.name == target_name:
					ob.select = True
					ob.hide = False
					context.scene.objects.active = ob
					for i, b in enumerate(ob.layers):
						if b:
							context.scene.layers[i] = True
					count += 1
		if 2 <= count:
			self.report(type={'WARNING'}, message="Found more than one")
		return {'FINISHED'}

class activate_bevel_parent_object(bpy.types.Operator):
	bl_idname = "curve.activate_bevel_parent_object"
	bl_label = "Activate bevel curve object"
	bl_description = "Activates curve as beveled objects using this curve"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		for curve in bpy.data.curves:
			target_name = curve.bevel_object.name if curve.bevel_object else ""
			if target_name == ob.name:
				return True
		return False
	
	def execute(self, context):
		count = 0
		active_ob = context.active_object
		for ob in bpy.data.objects:
			if ob.type == 'CURVE':
				curve = ob.data
				target_name = curve.bevel_object.name if curve.bevel_object else ""
				if active_ob.name == target_name:
					ob.select = True
					ob.hide = False
					context.scene.objects.active = ob
					for i, b in enumerate(ob.layers):
						if b:
							context.scene.layers[i] = True
					count += 1
		if 2 <= count:
			self.report(type={'WARNING'}, message="Found more than one")
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	copy_geometry_settings,
	ActivateTaperObject,
	ActivateBevelObject,
	activate_taper_parent_object,
	activate_bevel_parent_object
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
	for id in bpy.context.preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		if context.active_object:
			data = context.active_object.data
			if data.bevel_object or data.taper_object:
				row = self.layout.split(percentage=0.5)
				if data.taper_object:
					sub = row.row(align=True)
					sub.operator(ActivateTaperObject.bl_idname, icon='PARTICLE_PATH', text="")
					sub.prop(data.taper_object.data, 'resolution_u')
				else:
					row.label("")
				if data.bevel_object:
					sub = row.row(align=True)
					sub.operator(ActivateBevelObject.bl_idname, icon='OUTLINER_OB_SURFACE', text="")
					sub.prop(data.bevel_object.data, 'resolution_u')
				else:
					row.label("")
		
		flag = [False, False]
		ob = context.active_object
		for curve in bpy.data.curves:
			target_name = curve.taper_object.name if curve.taper_object else ""
			if target_name == ob.name:
				flag[0] = True
			target_name = curve.bevel_object.name if curve.bevel_object else ""
			if target_name == ob.name:
				flag[1] = True
			if any(flag):
				break
		if any(flag):
			row = self.layout.split(percentage=0.5)
			if flag[0]:
				row.operator(activate_taper_parent_object.bl_idname, icon='PARTICLE_PATH', text="Active Parent Taper")
			else:
				row.label("")
			if flag[1]:
				row.operator(activate_bevel_parent_object.bl_idname, icon='OUTLINER_OB_SURFACE', text="Active Parent Bevel")
			else:
				row.label("")
		
		if 2 <= len(context.selected_objects):
			i = 0
			for obj in context.selected_objects:
				if obj.type == 'CURVE':
					i += 1
			if 2 <= i:
				self.layout.operator(copy_geometry_settings.bl_idname, icon='COPY_ID')
	if (context.preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
