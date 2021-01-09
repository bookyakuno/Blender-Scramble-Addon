# 「プロパティ」エリア > 「モディファイア」タブ
# "Propaties" Area > "Modifiers" Tab

import bpy
from bpy.props import *
from bpy.ops import *

################
# オペレーター #
################

class ApplyAllModifiers(bpy.types.Operator):
	bl_idname = "object.apply_all_modifiers"
	bl_label = "Apply all modifiers"
	bl_description = "Apply all the selected objects' modifiers"
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
				bpy.ops.object.modifier_apply(modifier=mod.name)
		return {'FINISHED'}

class DeleteAllModifiers(bpy.types.Operator):
	bl_idname = "object.delete_all_modifiers"
	bl_label = "Remove all modifiers"
	bl_description = "Remove all the selected objects' modifiers"
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
	bl_label = "Toggle show/hide of all modifiers in viewport"
	bl_description = "Toggle display states in viewport of all the selected objects' modifiers"
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
			self.report(type={"INFO"}, message="Show all modifiers in viewport")
		else:
			self.report(type={"INFO"}, message="Hide all modifiers in viewport")
		return {'FINISHED'}

class SyncShowModifiers(bpy.types.Operator):
	bl_idname = "object.sync_show_modifiers"
	bl_label = "Change Modifiers' Display in Viewport and Rendering"
	bl_description = "Change display settingsof all the selected objects' modifiers in viewport and during rendering"
	bl_options = {'REGISTER', 'UNDO'}

	change_view : BoolProperty(name="Viewport", default=True)
	mode_view : EnumProperty(name="Viewport", items=[
		("SHOW","Show All","",0),("HIDE","Hide All","",1),
		("FROM_REND", "Show Only 'Used-during-Rendering'", "", 2)])
	change_rend : BoolProperty(name="Rendering", default=True)
	mode_rend : EnumProperty(name="Rendering", items=[
		("SHOW","Show All","",0),("HIDE","Hide All","",1),
		("FROM_VIEW", "Show Only 'Displayed-in-Viewport'", "", 2)])

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop(self, 'change_view')
		box = self.layout.box()
		box.prop(self, 'mode_view', expand=True)
		box.enabled = self.change_view and not (self.change_rend and self.mode_rend=='FROM_VIEW')
		self.layout.prop(self, 'change_rend')
		box = self.layout.box()
		box.prop(self, 'mode_rend', expand=True)
		box.enabled = self.change_rend and not (self.change_view and self.mode_view=='FROM_REND')

	def execute(self, context):
		mode_dic = {'SHOW':"True", 'HIDE':"False", 'FROM_VIEW': "mod.show_viewport", 'FROM_REND': "mod.show_render"}
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if self.change_view and not (self.change_rend and self.mode_rend=='FROM_VIEW'):
					mod.show_viewport = eval(mode_dic[self.mode_view])
				if self.change_rend and not (self.change_view and self.mode_view=='FROM_REND'):
					mod.show_render = eval(mode_dic[self.mode_rend])
		return {'FINISHED'}

class ToggleAllShowExpanded(bpy.types.Operator):
	bl_idname = "wm.toggle_all_show_expanded"
	bl_label = "Toggle expand/close of all modifiers"
	bl_description = "Toggle all modifier panels' expansion-states of the active object"
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
	bl_label = "Apply Modifiers and Join Objects"
	bl_description = "Apply all the selected objects' modifiers, and join them into the active object"
	bl_options = {'REGISTER', 'UNDO'}

	unapply_subsurf : BoolProperty(name="Not Apply Subdivision Surface", default=True)
	unapply_armature : BoolProperty(name="Not Apply Armature", default=True)
	unapply_mirror : BoolProperty(name="Not Apply Mirror", default=False)

	@classmethod
	def poll(cls, context):
		if 2 <= len(context.selected_objects):
			return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop(self, 'unapply_subsurf')
		self.layout.prop(self, 'unapply_armature')
		self.layout.prop(self, 'unapply_mirror')

	def execute(self, context):
		pre_active_object = context.active_object
		for obj in context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			for mod in obj.modifiers[:]:
				if self.unapply_subsurf and mod.type == 'SUBSURF':
					continue
				if self.unapply_armature and mod.type == 'ARMATURE':
					continue
				if self.unapply_mirror and mod.type == 'MIRROR':
					continue
				bpy.ops.object.modifier_apply(modifier=mod.name)
		bpy.context.view_layer.objects.active = pre_active_object
		bpy.ops.object.join()
		return {'FINISHED'}

class AutoRenameModifiers(bpy.types.Operator):
	bl_idname = "object.auto_rename_modifiers"
	bl_label = "Auto-rename all modifiers' names"
	bl_description = "Set the names of all the selected objects' modifiers to the names of their target objects"
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
					if mod.mirror_object:
						mod.name = mod.mirror_object.name
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
	bl_description = "Add to the active object Boolean modifiers that refer to each of the other selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('INTERSECT', "Intersect", "", 1),
		('UNION', "Union", "", 2),
		('DIFFERENCE', "Difference", "", 3),
		]
	mode : EnumProperty(items=items, name="Mode")

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
				obj.display_type = 'BOUNDS'
		return {'FINISHED'}

class ApplyBoolean(bpy.types.Operator):
	bl_idname = "object.apply_boolean"
	bl_label = "Add and Apply Boolean"
	bl_description = "Add and apply to the active object Boolean modifiers that refer to each of the other selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('INTERSECT', "Intersect", "", 1),
		('UNION', "Union", "", 2),
		('DIFFERENCE', "Difference", "", 3),
		]
	mode : EnumProperty(items=items, name="Mode")

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
				obj.select_set(True)
				bpy.ops.object.delete()
				activeObj.select_set(True)
		return {'FINISHED'}

############################
# オペレーター(サブサーフ) #
############################

class SetRenderSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.set_render_subsurf_level"
	bl_label = "Set Number of Subdivisions When Rendering"
	bl_description = "Set 'number of subdivisions when rendering' property of the selected objects' Subdivision Surface modifiers"
	bl_property = "level_enum"
	bl_options = {'REGISTER', 'UNDO'}

	level : IntProperty(name="Number of Subdivisions", default=6, min=0, max=10)
	is_more: BoolProperty(name="5 <", default=False)

	items = [(str(i+1),str(i+1),"",i) for i in range(5)]
	level_enum : EnumProperty(items=items, name="preset_level", default="2")

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'SUBSURF':
					return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_popup(self, event)
	def draw(self, context):
		sp = self.layout.split(factor=0.75)
		row = sp.split(factor=0.8)
		row.row().prop(self, 'level_enum', expand=True)
		row.prop(self, 'is_more')
		row = sp.row()
		row.prop(self, 'level', text="")
		row.enabled = self.is_more

	def execute(self, context):
		if self.is_more:
			level = self.level
		else:
			level = int(self.level_enum)
		for obj in context.selected_objects:
			if obj.type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE']:
				for modi in obj.modifiers:
					if modi.type == 'SUBSURF':
						modi.render_levels = level
						modi.show_expanded = False
						modi.show_expanded = True
		return {'FINISHED'}

class SetViewportSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.set_viewport_subsurf_level"
	bl_label = "Set Number of Subdivisions in Viewport"
	bl_description = "Set 'number of subdivisions' property of the selected objects' Subdivision Surface modifiers"
	bl_options = {'REGISTER', 'UNDO'}

	level : IntProperty(name="Number of Subdivisions", default=6, min=0, max=10)
	is_more: BoolProperty(name="5 <", default=False)

	items = [(str(i+1),str(i+1),"",i) for i in range(5)]
	level_enum : EnumProperty(items=items, name="preset_level", default="2")

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'SUBSURF':
					return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_popup(self, event)

	def draw(self, context):
		sp = self.layout.split(factor=0.75)
		row = sp.split(factor=0.8)
		row.row().prop(self, 'level_enum', expand=True)
		row.prop(self, 'is_more')
		row = sp.row()
		row.prop(self, 'level', text="")
		row.enabled = self.is_more

	def execute(self, context):
		if self.is_more:
			level = self.level
		else:
			level = int(self.level_enum)
		for obj in context.selected_objects:
			if obj.type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE']:
				for modi in obj.modifiers:
					if modi.type == 'SUBSURF':
						modi.levels = level
						modi.show_expanded = False
						modi.show_expanded = True
		return {'FINISHED'}

class EqualizeSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.equalize_subsurf_level"
	bl_label = "Match number of subdivisions in viewport and rendering"
	bl_description = "Match number of subdivisions in viewport to that during rendering, or vice verse, in each selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('ToRender', "during Rendering", "", 1),
		('ToPreview', "in Viewport", "", 2),
		]
	mode : EnumProperty(items=items, name="Method")

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'SUBSURF':
					return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_popup(self, event)
	def draw(self, context):
		self.layout.label(text="Use Number")
		row = self.layout.row()
		row.separator_spacer()
		row.prop(self, 'mode', expand=True)

	def execute(self, context):
		for obj in context.selected_objects:
			if obj.type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE']:
				for modi in obj.modifiers:
					if modi.type == 'SUBSURF':
						if self.mode == 'ToRender':
							modi.render_levels = modi.levels
						else:
							modi.levels = modi.render_levels
						modi.show_expanded = False
						modi.show_expanded = True
		return {'FINISHED'}

class SetSubsurfOptimalDisplay(bpy.types.Operator):
	bl_idname = "object.set_subsurf_optimal_display"
	bl_label = "Set Optimal Display"
	bl_description = "Set 'Optimal Display' property of the selected objects' Subdivision Surface modifiers"
	bl_options = {'REGISTER', 'UNDO'}

	items = [('1', "Enabled", "", 1),('0', "Disabled", "", 2)]
	is_use : EnumProperty(items=items, name="Optimal Display")

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'SUBSURF':
					return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_popup(self, event)
	def draw(self, context):
		row = self.layout.row()
		row.label(text="Optimal Display")
		row.prop(self, 'is_use', expand=True)

	def execute(self, context):
		for obj in context.selected_objects:
			if obj.type in ['MESH', 'CURVE', 'FONT', 'META', 'SURFACE']:
				for modi in obj.modifiers:
					if modi.type == 'SUBSURF':
						modi.show_only_control_edges = int(self.is_use)
		"""
		sel = bpy.context.selected_objects
		act_obj = bpy.context.active_object
		if act_obj.type in ['MESH', 'CURVE', 'FONT', 'META', 'SURFACE']:
			for mod in act_obj.modifiers:
				if mod.type == 'SUBSURF':
					optimal = not(mod.show_only_control_edges)
					break
			else: optimal = False
			for obj in sel:
				if obj.type in ['MESH', 'CURVE', 'FONT', 'META', 'SURFACE']:
					for mod in obj.modifiers:
						if mod.type == 'SUBSURF':
							mod.show_only_control_edges = optimal
		"""
		return {'FINISHED'}

class DeleteSubsurf(bpy.types.Operator):
	bl_idname = "object.delete_subsurf"
	bl_label = "Delete Subdivision Surface"
	bl_description = "Remove Subdivision Surface modifiers from the selected objects"
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
	bl_label = "Add Subdivision Surface"
	bl_description = "Add Subdivision Surface modifiers to the selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	ps = bpy.types.SubsurfModifier.bl_rna.properties
	subdivision_type : EnumProperty(name="Method", items=[
		(it.identifier, it.name, it.description, idx) for idx, it
		in enumerate(ps["subdivision_type"].enum_items)])
	levels : IntProperty(name="Viewport", default=2, min=0, max=6)
	render_levels : IntProperty(name="Render", default=2, min=0, max=6)
	uv_smooth : EnumProperty(name="UV Smooth", items=[
		(it.identifier, it.name, it.description, idx) for idx, it
		in enumerate(ps["uv_smooth"].enum_items)])
	show_only_control_edges : BoolProperty(name="Optimal Display", default=False)

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
				modi.uv_smooth = self.uv_smooth
				modi.show_only_control_edges = self.show_only_control_edges
		return {'FINISHED'}

##############################
# オペレーター(アーマチュア) #
##############################

class SetArmatureDeformPreserveVolume(bpy.types.Operator):
	bl_idname = "object.set_armature_deform_preserve_volume"
	bl_label = "Set 'Preserve Volume' property"
	bl_description = "Set 'Preserve Volume' property of the selected objects' Armature modifiers"
	bl_options = {'REGISTER', 'UNDO'}

	items = [('1', "Enable", "", 1),('0', "Disable", "", 2)]
	is_use : EnumProperty(items=items, name="Preserve Volume")

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'ARMATURE':
					return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_popup(self, event)
	def draw(self, context):
		row = self.layout.row()
		row.label(text="Preserve Volume")
		row.prop(self, 'is_use', expand=True)

	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if mod.type == 'ARMATURE':
					mod.use_deform_preserve_volume = int(self.is_use)
		return {'FINISHED'}

########################
# オペレーター(カーブ) #
########################

class QuickCurveDeform(bpy.types.Operator):
	bl_idname = "object.quick_curve_deform"
	bl_label = "Add Curve"
	bl_description = "Add to the active object Curve modifier that refers to the selected curve object"
	bl_options = {'REGISTER', 'UNDO'}

	ps = bpy.types.CurveModifier.bl_rna.properties
	deform_axis : EnumProperty(name="Deform Axis", items=[
		(it.identifier, it.name, it.description, idx) for idx, it
		in enumerate(ps["deform_axis"].enum_items) ])
	is_apply : BoolProperty(name="Apply Modifiers", default=False)

	@classmethod
	def poll(cls, context):
		if len(context.selected_objects) == 2:
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		mesh_obj = context.active_object
		if mesh_obj.type != 'MESH':
			self.report(type={'ERROR'}, message="Please run when mesh object is active")
			return {'CANCELLED'}
		for obj in context.selected_objects:
			if mesh_obj.name != obj.name:
				if obj.type == 'CURVE':
					curve_obj = obj
					break
		else:
			self.report(type={'ERROR'}, message="Please run selecting curve object")
			return {'CANCELLED'}
		curve = curve_obj.data
		pre_use_stretch = curve.use_stretch
		pre_use_deform_bounds = curve.use_deform_bounds
		curve.use_stretch = True
		curve.use_deform_bounds = True
		bpy.ops.object.transform_apply()
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
	bl_label = "Add Array and Curve"
	bl_description = "Add to the active object Array modifier and Curve modifier that refers to the selected curve object"
	bl_options = {'REGISTER', 'UNDO'}

	ps = bpy.types.CurveModifier.bl_rna.properties
	deform_axis : EnumProperty(name="Deform Axis", items=[
		(it.identifier, it.name, it.description, idx) for idx, it
		in enumerate(ps["deform_axis"].enum_items) ])

	ps2 = bpy.types.ArrayModifier.bl_rna.properties
	use_merge_vertices : BoolProperty(name=ps2["use_merge_vertices"].name, description=ps2["use_merge_vertices"].description, default=True)
	is_apply : BoolProperty(name="Apply Modifiers", default=False)

	@classmethod
	def poll(cls, context):
		if len(context.selected_objects) == 2:
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		mesh_obj = context.active_object
		if (mesh_obj.type != 'MESH'):
			self.report(type={'ERROR'}, message="Please run when mesh object is active")
			return {'CANCELLED'}
		for obj in context.selected_objects:
			if (mesh_obj.name != obj.name):
				if (obj.type == 'CURVE'):
					curve_obj = obj
					break
		else:
			self.report(type={'ERROR'}, message="Please run selecting curve object")
			return {'CANCELLED'}
		curve = curve_obj.data
		pre_use_stretch = curve.use_stretch
		pre_use_deform_bounds = curve.use_deform_bounds
		curve.use_stretch = True
		curve.use_deform_bounds = True
		bpy.ops.object.transform_apply()

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

class SubsurfMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_modifiers_subsurf"
	bl_label = "Subsurf"
	bl_description = "Manipulate Subdivision Surface modifier"

	def draw(self, context):
		self.layout.operator(AddSubsurf.bl_idname, icon='MODIFIER')
		self.layout.operator(DeleteSubsurf.bl_idname, icon='CANCEL')
		self.layout.separator()
		self.layout.operator(SetViewportSubsurfLevel.bl_idname, icon='PLUGIN')
		self.layout.operator(SetRenderSubsurfLevel.bl_idname, icon='PLUGIN')
		self.layout.operator(EqualizeSubsurfLevel.bl_idname, icon='PLUGIN')
		self.layout.operator(SetSubsurfOptimalDisplay.bl_idname, icon='PLUGIN')

class BooleanMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_modifiers_boolean"
	bl_label = "Boolean"
	bl_description = "Manipulate Boolean modifier"

	def draw(self, context):
		self.layout.operator(AddBoolean.bl_idname, icon='PLUGIN', text="Add Boolean (Intersect)").mode = "INTERSECT"
		self.layout.operator(AddBoolean.bl_idname, icon='PLUGIN', text="Add Boolean (Union)").mode = "UNION"
		self.layout.operator(AddBoolean.bl_idname, icon='PLUGIN', text="Add Boolean (Difference)").mode = "DIFFERENCE"
		self.layout.separator()
		self.layout.operator(ApplyBoolean.bl_idname, icon='PLUGIN', text="Add and Apply Boolean (Intersect)").mode = "INTERSECT"
		self.layout.operator(ApplyBoolean.bl_idname, icon='PLUGIN', text="Add and Apply Boolean (Union)").mode = "UNION"
		self.layout.operator(ApplyBoolean.bl_idname, icon='PLUGIN', text="Add and Apply Boolean (Difference)").mode = "DIFFERENCE"

class ArmatureMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_modifiers_armature"
	bl_label = "Armature"
	bl_description = "Manipulate Armature modifier"

	def draw(self, context):
		self.layout.operator(SetArmatureDeformPreserveVolume.bl_idname, icon='PLUGIN')

class CurveMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_modifiers_curve"
	bl_label = "Curve"
	bl_description = "Manipulate Curve modifier"

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
	SetViewportSubsurfLevel,
	EqualizeSubsurfLevel,
	SetSubsurfOptimalDisplay,
	DeleteSubsurf,
	AddSubsurf,
	SetArmatureDeformPreserveVolume,
	QuickCurveDeform,
	QuickArrayAndCurveDeform,
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
				row.operator(ToggleApplyModifiersView.bl_idname, icon='RESTRICT_VIEW_OFF', text="Show / Hide")
				row.operator(ToggleAllShowExpanded.bl_idname, icon='FULLSCREEN_ENTER', text="Expand / Close")
				row.operator(SyncShowModifiers.bl_idname, icon='LINKED', text="Display Setting")

		sp = self.layout.split(factor=0.9)
		row = sp.row(align=True)
		row_sub = row.row(align=True)
		row_sub.menu(SubsurfMenu.bl_idname, text="Subsurf",icon="MOD_SUBSURF")
		row_sub = row.row(align=True)
		row_sub.active = len([m for m in bpy.context.object.modifiers if m.type == "ARMATURE"])
		row_sub.menu(ArmatureMenu.bl_idname, text="Armature",icon="OUTLINER_DATA_ARMATURE")
		row_sub = row.row(align=True)
		row_sub.active = (len(bpy.context.selected_objects) >= 2)
		row_sub.menu(BooleanMenu.bl_idname, text="Boolean",icon="MOD_BOOLEAN")
		row_sub = row.row(align=True)
		row_sub.active = bool(bool(len(bpy.context.selected_objects) >= 2) and bool([o for o in bpy.context.selected_objects if o.type == "CURVE"]))
		row_sub.menu(CurveMenu.bl_idname, text="Curve",icon="CURVE_DATA")
		sp.operator(ApplyModifiersAndJoin.bl_idname, text="Join")
	if (bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
