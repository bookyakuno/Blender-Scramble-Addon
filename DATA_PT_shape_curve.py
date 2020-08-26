# 「プロパティ」エリア > 「カーブデータ」タブ > 「シェイプ」パネル
# "Propaties" Area > "Armature" Tab > "Shape" Panel

import bpy

################
# オペレーター #
################

class copy_curve_shape_setting(bpy.types.Operator):
	bl_idname = "curve.copy_curve_shape_setting"
	bl_label = "Copy Shape Settings"
	bl_description = "Copy selected curve other active curve shape settings"
	bl_options = {'REGISTER', 'UNDO'}
	
	dimensions = bpy.props.BoolProperty(name="2D/3D", default=True)
	resolution_u = bpy.props.BoolProperty(name="Preview U", default=True)
	render_resolution_u = bpy.props.BoolProperty(name="Render U", default=True)
	fill_mode = bpy.props.BoolProperty(name="Fill Method", default=True)
	use_fill_deform = bpy.props.BoolProperty(name="Fill Deformed", default=True)
	twist_mode = bpy.props.BoolProperty(name="Twist Method", default=True)
	use_radius = bpy.props.BoolProperty(name="Radius", default=True)
	use_stretch = bpy.props.BoolProperty(name="Stretch", default=True)
	twist_smooth = bpy.props.BoolProperty(name="Smooth", default=True)
	use_deform_bounds = bpy.props.BoolProperty(name="Fix Border", default=True)
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'CURVE':
				for obj in context.selected_objects:
					if ob.name != obj.name:
						if obj.type == 'CURVE':
							return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.label("Shape")
		self.layout.prop(self, 'dimensions')
		row = self.layout.row()
		row.label("Resolution:")
		row.label("Fill:")
		row = self.layout.row()
		row.prop(self, 'resolution_u')
		row.prop(self, 'fill_mode')
		row = self.layout.row()
		row.prop(self, 'render_resolution_u')
		row.prop(self, 'use_fill_deform')
		row = self.layout.row()
		row.label("Twisting:")
		row.label("Path / Curve-Deform:")
		row = self.layout.row()
		row.prop(self, 'twist_mode')
		row.prop(self, 'use_radius')
		row.prop(self, 'use_stretch')
		row = self.layout.row()
		row.prop(self, 'twist_smooth')
		row.prop(self, 'use_deform_bounds')
	
	def execute(self, context):
		active_ob = context.active_object
		active_curve = active_ob.data
		for ob in context.selected_objects:
			if active_ob.name != ob.name:
				if ob.type == 'CURVE':
					curve = ob.data
					
					if self.dimensions:
						curve.dimensions = active_curve.dimensions
					if self.resolution_u:
						curve.resolution_u = active_curve.resolution_u
					if self.render_resolution_u:
						curve.render_resolution_u = active_curve.render_resolution_u
					if self.fill_mode:
						curve.fill_mode = active_curve.fill_mode
					if self.use_fill_deform:
						curve.use_fill_deform = active_curve.use_fill_deform
					if self.twist_mode:
						curve.twist_mode = active_curve.twist_mode
					if self.use_radius:
						curve.use_radius = active_curve.use_radius
					if self.use_stretch:
						curve.use_stretch = active_curve.use_stretch
					if self.twist_smooth:
						curve.twist_smooth = active_curve.twist_smooth
					if self.use_deform_bounds:
						curve.use_deform_bounds = active_curve.use_deform_bounds
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	copy_curve_shape_setting
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
		if 2 <= len(context.selected_objects):
			self.layout.operator(copy_curve_shape_setting.bl_idname, icon='COPY_ID')
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
