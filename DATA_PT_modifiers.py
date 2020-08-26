# 「プロパティ」エリア > 「モディファイア」タブ
# "Propaties" Area > "Modifiers" Tab

import bpy
from bpy.props import *

################
# オペレーター #
################

class ApplyAllModifiers(bpy.types.Operator):
	bl_idname = "object.apply_all_modifiers"
	bl_label = "Apply All Modifiers"
	bl_description = "Applies to all modifiers of selected object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers[:]:
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
		return {'FINISHED'}

class DeleteAllModifiers(bpy.types.Operator):
	bl_idname = "object.delete_all_modifiers"
	bl_label = "Remove All Modifiers"
	bl_description = "Remove all modifiers of selected object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			modifiers = obj.modifiers[:]
			for modi in modifiers:
				obj.modifiers.remove(modi)
		return {'FINISHED'}

class ToggleApplyModifiersView(bpy.types.Operator):
	bl_idname = "object.toggle_apply_modifiers_view"
	bl_label = "Switch Modifiers Apply/Unapply to View"
	bl_description = "Shows or hides application to view all modifiers of selected object"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		if context.active_object:
			for mod in context.active_object.modifiers:
				return True
		return False

	def execute(self, context):
		is_apply = True
		for mod in context.active_object.modifiers:
			if mod.show_viewport:
				is_apply = False
				break
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				mod.show_viewport = is_apply
		if is_apply:
			self.report(type={"INFO"}, message="Applied modifiers to view")
		else:
			self.report(type={"INFO"}, message="Unregistered modifiers apply to view")
		return {'FINISHED'}

class SyncShowModifiers(bpy.types.Operator):
	bl_idname = "object.sync_show_modifiers"
	bl_label = "Sync Modifiers Use"
	bl_description = "synchronized modifier used when rendering selection / view"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		("1", "Rendering => View", "", 1),
		("0", "View => Rendering", "", 2),
		]
	mode : EnumProperty(items=items, name="Calculate", default="0")

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if int(self.mode):
					mod.show_viewport = mod.show_render
				else:
					mod.show_render = mod.show_viewport
		return {'FINISHED'}

class ToggleAllShowExpanded(bpy.types.Operator):
	bl_idname = "wm.toggle_all_show_expanded"
	bl_label = "Toggle all modifiers expand/close"
	bl_description = "Expand / collapse all modifiers of active objects to switch (toggle)"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		if context.active_object:
			for mod in context.active_object.modifiers:
				return True
		return False

	def execute(self, context):
		obj = context.active_object
		if len(obj.modifiers):
			vs = 0
			for mod in obj.modifiers:
				if mod.show_expanded:
					vs += 1
				else:
					vs -= 1
			is_close = False
			if 0 < vs:
				is_close = True
			for mod in obj.modifiers:
				mod.show_expanded = not is_close
		else:
			self.report(type={'WARNING'}, message="None Modifiers")
			return {'CANCELLED'}
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ApplyModifiersAndJoin(bpy.types.Operator):
	bl_idname = "object.apply_modifiers_and_join"
	bl_label = "Apply modifiers + join"
	bl_description = "integration from object\'s modifiers to apply all"
	bl_options = {'REGISTER', 'UNDO'}

	unapply_subsurf : BoolProperty(name="Except Subsurf", default=True)
	unapply_armature : BoolProperty(name="Except Armature", default=True)
	unapply_mirror : BoolProperty(name="Except Mirror", default=False)

	@classmethod
	def poll(cls, context):
		if 2 <= len(context.selected_objects):
			return True
		return False

	def execute(self, context):
		pre_active_object = context.active_object
		for obj in context.selected_objects:
			context.scene.objects.active = obj
			for mod in obj.modifiers[:]:
				if self.unapply_subsurf and mod.type == 'SUBSURF':
					continue
				if self.unapply_armature and mod.type == 'ARMATURE':
					continue
				if self.unapply_mirror and mod.type == 'MIRROR':
					continue
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
		context.scene.objects.active = pre_active_object
		bpy.ops.object.join()
		return {'FINISHED'}

class AutoRenameModifiers(bpy.types.Operator):
	bl_idname = "object.auto_rename_modifiers"
	bl_label = "Auto rename modifier names"
	bl_description = "Rename selected object modifier name refers to, for example,"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				try:
					if mod.subtarget:
						mod.name = mod.subtarget
					continue
				except AttributeError: pass
				try:
					if mod.target:
						mod.name = mod.target.name
					continue
				except AttributeError: pass
				try:
					if mod.object:
						mod.name = mod.object.name
					continue
				except AttributeError: pass
				try:
					if mod.vertex_group:
						mod.name = mod.vertex_group
					continue
				except AttributeError: pass
		return {'FINISHED'}

############################
# オペレーター(ブーリアン) #
############################

class AddBoolean(bpy.types.Operator):
	bl_idname = "object.add_boolean"
	bl_label = "Add Boolean"
	bl_description = "Additional Boolean selected objects to an active object"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('INTERSECT', "Intersect", "", 1),
		('UNION', "Union", "", 2),
		('DIFFERENCE', "Difference", "", 3),
		]
	mode : EnumProperty(items=items, name="Calculate")

	@classmethod
	def poll(cls, context):
		if 2 <= len(context.selected_objects):
			return True
		return False

	def execute(self, context):
		activeObj = context.active_object
		for obj in context.selected_objects:
			if obj.type == 'MESH' and activeObj.name != obj.name:
				modi = activeObj.modifiers.new("Boolean", 'BOOLEAN')
				modi.object = obj
				modi.operation = self.mode
				obj.draw_type = 'BOUNDS'
		return {'FINISHED'}

class ApplyBoolean(bpy.types.Operator):
	bl_idname = "object.apply_boolean"
	bl_label = "Apply Boolean"
	bl_description = "Apply to Boolean objects and other active objects"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('INTERSECT', "Intersect", "", 1),
		('UNION', "Union", "", 2),
		('DIFFERENCE', "Difference", "", 3),
		]
	mode : EnumProperty(items=items, name="Calculate")

	@classmethod
	def poll(cls, context):
		if 2 <= len(context.selected_objects):
			return True
		return False

	def execute(self, context):
		activeObj = context.active_object
		for obj in context.selected_objects:
			if obj.type == 'MESH' and activeObj.name != obj.name:
				modi = activeObj.modifiers.new("Boolean", 'BOOLEAN')
				modi.object = obj
				modi.operation = self.mode
				bpy.ops.object.modifier_apply (modifier=modi.name)
				bpy.ops.object.select_all(action='DESELECT')
				obj.select = True
				bpy.ops.object.delete()
				activeObj.select = True
		return {'FINISHED'}

############################
# オペレーター(サブサーフ) #
############################

class SetRenderSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.set_render_subsurf_level"
	bl_label = "Set number of subdivision when rendering"
	bl_description = "Sets number of subdivisions during rendering of selected object subsurfmodifaia"
	bl_options = {'REGISTER', 'UNDO'}

	level : IntProperty(name="Number of Divisions", default=2, min=0, max=6)

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'SUBSURF':
					return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			if obj.type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE']:
				for modi in obj.modifiers:
					if modi.type == 'SUBSURF':
						modi.render_levels = self.level
		return {'FINISHED'}

class EqualizeSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.equalize_subsurf_level"
	bl_label = "Sync subsurf level preview or rendering"
	bl_description = "Set in same subdivision of subsurfmodifaia of selected object when you preview and rendering time"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('ToRender', "Preview => Rendering", "", 1),
		('ToPreview', "Rendering => Preview", "", 2),
		]
	mode : EnumProperty(items=items, name="How to set up")

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'SUBSURF':
					return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			if obj.type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE']:
				for modi in obj.modifiers:
					if modi.type == 'SUBSURF':
						if self.mode == 'ToRender':
							modi.render_levels = modi.levels
						else:
							modi.levels = modi.render_levels
		return {'FINISHED'}

class SetSubsurfOptimalDisplay(bpy.types.Operator):
	bl_idname = "object.set_subsurf_optimal_display"
	bl_label = "Set Optimization"
	bl_description = "Sets optimization of subsurfmodifaia of selected object"
	bl_options = {'REGISTER', 'UNDO'}

	mode : BoolProperty(name="Optimized View")

	# @classmethod
	# def poll(cls, context):
	# 	for obj in context.selected_objects:
	# 		for mod in obj.modifiers:
	# 			if mod.type == 'SUBSURF':
	# 				return True
	# 	return False
	#
	def execute(self, context):
		# for obj in context.selected_objects:
		# 	if obj.type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE']:
		# 		for modi in obj.modifiers:
		# 			if modi.type == 'SUBSURF':
		# 				modi.show_only_control_edges = self.mode
		sel = bpy.context.selected_objects
		act_obj = bpy.context.active_object
		if act_obj.type == 'MESH' or act_obj.type == 'CURVE' or act_obj.type == 'FONT' or act_obj.type == 'META' or act_obj.type == 'SURFACE':
			for mod in act_obj.modifiers:
				if mod.type == 'SUBSURF':
					optimal = not(mod.show_only_control_edges)
					break
			else: optimal = False
			for obj in sel:
				if obj.type == 'MESH' or obj.type == 'CURVE' or obj.type == 'FONT' or obj.type == 'META' or obj.type == 'SURFACE':
					for mod in obj.modifiers:
						if mod.type == 'SUBSURF':
							mod.show_only_control_edges = optimal


		return {'FINISHED'}

class DeleteSubsurf(bpy.types.Operator):
	bl_idname = "object.delete_subsurf"
	bl_label = "Delete Subsurfs selected objects"
	bl_description = "Removes selected object subsurfmodifaia"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'SUBSURF':
					return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			if obj.type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE']:
				for modi in obj.modifiers:
					if modi.type == 'SUBSURF':
						obj.modifiers.remove(modi)
		return {'FINISHED'}

class AddSubsurf(bpy.types.Operator):
	bl_idname = "object.add_subsurf"
	bl_label = "Add Subsurfs selected objects"
	bl_description = "Add subsurfmodifaia to selected object"
	bl_options = {'REGISTER', 'UNDO'}

	subdivision_type : EnumProperty(items=[("CATMULL_CLARK", "Catmulclark", "", 1), ("SIMPLE", "Simple", "", 2)], name="Subdivision Method")
	levels : IntProperty(name="Number of View", default=2, min=0, max=6)
	render_levels : IntProperty(name="Number of Render", default=2, min=0, max=6)
	use_subsurf_uv : BoolProperty(name="Subdivide UV", default=True)
	show_only_control_edges : BoolProperty(name="Optimized View")

	@classmethod
	def poll(cls, context):
		if len(context.selected_objects):
			return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			if obj.type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE']:
				modi = obj.modifiers.new("Subsurf", 'SUBSURF')
				modi.subdivision_type = self.subdivision_type
				modi.levels = self.levels
				modi.render_levels = self.render_levels
				modi.use_subsurf_uv = self.use_subsurf_uv
				modi.show_only_control_edges = self.show_only_control_edges
		return {'FINISHED'}

##############################
# オペレーター(アーマチュア) #
##############################

class SetArmatureDeformPreserveVolume(bpy.types.Operator):
	bl_idname = "object.set_armature_deform_preserve_volume"
	bl_label = "Set armature \"Preserve Volume\""
	bl_description = "Armtuamodifaia selected objects keep volume together off and on the"
	bl_options = {'REGISTER', 'UNDO'}

	use_deform_preserve_volume : BoolProperty(name="Use Preserve Volume", default=True)

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'ARMATURE':
					return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'ARMATURE':
					mod.use_deform_preserve_volume = self.use_deform_preserve_volume
		return {'FINISHED'}

########################
# オペレーター(カーブ) #
########################

class QuickCurveDeform(bpy.types.Operator):
	bl_idname = "object.quick_curve_deform"
	bl_label = "Quick Curve Transform"
	bl_description = "Quickly apply curve modifier"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('POS_X', "+X", "", 1),
		('POS_Y', "+Y", "", 2),
		('POS_Z', "+Z", "", 3),
		('NEG_X', "-X", "", 4),
		('NEG_Y', "-Y", "", 5),
		('NEG_Z', "-Z", "", 6),
		]
	deform_axis : EnumProperty(items=items, name="Axis Deformation")
	is_apply : BoolProperty(name="Apply Modifiers", default=False)

	@classmethod
	def poll(cls, context):
		if not context.object:
			return False
		if context.object.type != 'MESH':
			return False
		if len(context.selected_objects) != 2:
			return False
		for obj in context.selected_objects:
			if obj.type == 'CURVE':
				return True
		return False

	def execute(self, context):
		mesh_obj = context.active_object
		if mesh_obj.type != 'MESH':
			self.report(type={'ERROR'}, message="Please run mesh object is active")
			return {'CANCELLED'}
		if len(context.selected_objects) != 2:
			self.report(type={'ERROR'}, message="By selecting only two meshes, curves, please run")
			return {'CANCELLED'}
		for obj in context.selected_objects:
			if mesh_obj.name != obj.name:
				if obj.type == 'CURVE':
					curve_obj = obj
					break
		else:
			self.report(type={'ERROR'}, message="Curve objects run in selected state")
			return {'CANCELLED'}
		curve = curve_obj.data
		pre_use_stretch = curve.use_stretch
		pre_use_deform_bounds = curve.use_deform_bounds
		curve.use_stretch = True
		curve.use_deform_bounds = True
		bpy.ops.object.transform_apply_all()
		mod = mesh_obj.modifiers.new("temp", 'CURVE')
		mod.object = curve_obj
		mod.deform_axis = self.deform_axis
		for i in range(len(mesh_obj.modifiers)):
			bpy.ops.object.modifier_move_up(modifier=mod.name)
		if (self.is_apply):
			bpy.ops.object.modifier_apply(modifier=mod.name)
			curve.use_stretch = pre_use_stretch
			curve.use_deform_bounds = pre_use_deform_bounds
		return {'FINISHED'}

class QuickArrayAndCurveDeform(bpy.types.Operator):
	bl_idname = "object.quick_array_and_curve_deform"
	bl_label = "Quick Array + Curve Transform"
	bl_description = "Quickly apply curve modifier with modifiers array replication"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('POS_X', "+X", "", 1),
		('POS_Y', "+Y", "", 2),
		('POS_Z', "+Z", "", 3),
		('NEG_X', "-X", "", 4),
		('NEG_Y', "-Y", "", 5),
		('NEG_Z', "-Z", "", 6),
		]
	deform_axis : EnumProperty(items=items, name="Axis Deformation")
	use_merge_vertices : BoolProperty(name="Combine Vertices", default=True)
	is_apply : BoolProperty(name="Apply Modifiers", default=False)

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (context.object.type != 'MESH'):
			return False
		if (len(context.selected_objects) != 2):
			return False
		for obj in context.selected_objects:
			if (obj.type == 'CURVE'):
				return True
		return False

	def execute(self, context):
		mesh_obj = context.active_object
		if (mesh_obj.type != 'MESH'):
			self.report(type={'ERROR'}, message="Please run mesh object is active")
			return {'CANCELLED'}
		if (len(context.selected_objects) != 2):
			self.report(type={'ERROR'}, message="By selecting only two meshes, curves, please run")
			return {'CANCELLED'}
		for obj in context.selected_objects:
			if (mesh_obj.name != obj.name):
				if (obj.type == 'CURVE'):
					curve_obj = obj
					break
		else:
			self.report(type={'ERROR'}, message="Curve objects run in selected state")
			return {'CANCELLED'}
		curve = curve_obj.data
		pre_use_stretch = curve.use_stretch
		pre_use_deform_bounds = curve.use_deform_bounds
		curve.use_stretch = True
		curve.use_deform_bounds = True
		bpy.ops.object.transform_apply_all()

		mod_array = mesh_obj.modifiers.new("Array", 'ARRAY')
		mod_array.fit_type = 'FIT_CURVE'
		mod_array.curve = curve_obj
		mod_array.use_merge_vertices = self.use_merge_vertices
		mod_array.use_merge_vertices_cap = self.use_merge_vertices
		if (self.deform_axis == 'POS_Y'):
			mod_array.relative_offset_displace = (0, 1, 0)
		elif (self.deform_axis == 'POS_Z'):
			mod_array.relative_offset_displace = (0, 0, 1)
		elif (self.deform_axis == 'NEG_X'):
			mod_array.relative_offset_displace = (-1, 0, 0)
		elif (self.deform_axis == 'NEG_Y'):
			mod_array.relative_offset_displace = (0, -1, 0)
		elif (self.deform_axis == 'NEG_Z'):
			mod_array.relative_offset_displace = (0, 0, -1)

		mod_curve = mesh_obj.modifiers.new("Curve", 'CURVE')
		mod_curve.object = curve_obj
		mod_curve.deform_axis = self.deform_axis

		for i in range(len(mesh_obj.modifiers)):
			bpy.ops.object.modifier_move_up(modifier=mod_curve.name)
		for i in range(len(mesh_obj.modifiers)):
			bpy.ops.object.modifier_move_up(modifier=mod_array.name)

		if (self.is_apply):
			bpy.ops.object.modifier_apply(modifier=mod_array.name)
			bpy.ops.object.modifier_apply(modifier=mod_curve.name)
			curve.use_stretch = pre_use_stretch
			curve.use_deform_bounds = pre_use_deform_bounds
		return {'FINISHED'}

################
# サブメニュー #
################

class ModifierMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_modifiers_specials"
	bl_label = "Modifier Actions"
	bl_description = "Modifiers"

	def draw(self, context):
		self.layout.menu(SubsurfMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(ArmatureMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(BooleanMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(CurveMenu.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(ApplyModifiersAndJoin.bl_idname, icon='PLUGIN')

class SubsurfMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_modifiers_subsurf"
	bl_label = "Subsurf"
	bl_description = "Subsurface Operations"

	def draw(self, context):
		self.layout.operator(AddSubsurf.bl_idname, icon='PLUGIN')
		self.layout.operator(DeleteSubsurf.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(SetRenderSubsurfLevel.bl_idname, icon='PLUGIN')
		self.layout.operator(EqualizeSubsurfLevel.bl_idname, icon='PLUGIN')
		self.layout.operator(SetSubsurfOptimalDisplay.bl_idname, icon='PLUGIN')

class BooleanMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_modifiers_boolean"
	bl_label = "Boolean"
	bl_description = "Boolean Operations"

	def draw(self, context):
		self.layout.operator(AddBoolean.bl_idname, icon='PLUGIN', text="Boolean Add (Intersect)").mode = "INTERSECT"
		self.layout.operator(AddBoolean.bl_idname, icon='PLUGIN', text="Boolean Add (Union)").mode = "UNION"
		self.layout.operator(AddBoolean.bl_idname, icon='PLUGIN', text="Boolean Add (Difference)").mode = "DIFFERENCE"
		self.layout.separator()
		self.layout.operator(ApplyBoolean.bl_idname, icon='PLUGIN', text="Boolean Apply (Intersect)").mode = "INTERSECT"
		self.layout.operator(ApplyBoolean.bl_idname, icon='PLUGIN', text="Boolean Apply (Union)").mode = "UNION"
		self.layout.operator(ApplyBoolean.bl_idname, icon='PLUGIN', text="Boolean Apply (Difference)").mode = "DIFFERENCE"

class ArmatureMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_modifiers_armature"
	bl_label = "Armature"
	bl_description = "Armatures"

	def draw(self, context):
		self.layout.operator(SetArmatureDeformPreserveVolume.bl_idname, icon='PLUGIN')

class CurveMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_modifiers_curve"
	bl_label = "Curve"
	bl_description = "Curve Operators"

	def draw(self, context):
		self.layout.operator(QuickCurveDeform.bl_idname, icon='PLUGIN')
		self.layout.operator(QuickArrayAndCurveDeform.bl_idname, icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	ApplyAllModifiers,
	DeleteAllModifiers,
	ToggleApplyModifiersView,
	SyncShowModifiers,
	ToggleAllShowExpanded,
	ApplyModifiersAndJoin,
	AutoRenameModifiers,
	AddBoolean,
	ApplyBoolean,
	SetRenderSubsurfLevel,
	EqualizeSubsurfLevel,
	SetSubsurfOptimalDisplay,
	DeleteSubsurf,
	AddSubsurf,
	SetArmatureDeformPreserveVolume,
	QuickCurveDeform,
	QuickArrayAndCurveDeform,
	ModifierMenu,
	SubsurfMenu,
	BooleanMenu,
	ArmatureMenu,
	CurveMenu
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
		if (context.active_object):
			if (len(context.active_object.modifiers)):
				col = self.layout.column(align=True)
				row = col.row(align=True)
				row.operator(AutoRenameModifiers.bl_idname, icon='SCRIPT', text="Rename All")
				row.operator(ApplyAllModifiers.bl_idname, icon='IMPORT', text="Apply All")
				row.operator(DeleteAllModifiers.bl_idname, icon='X', text="Delete All")
				row = col.row(align=True)
				row.operator(ToggleApplyModifiersView.bl_idname, icon='RESTRICT_VIEW_OFF', text="View")
				row.operator(ToggleAllShowExpanded.bl_idname, icon='FULLSCREEN_ENTER', text="Expand/Close")
				row.operator(SyncShowModifiers.bl_idname, icon='LINKED', text="Use Sync")
		self.layout.menu(ModifierMenu.bl_idname, icon='PLUGIN')
	if (bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
