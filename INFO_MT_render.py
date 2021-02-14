# 「トップバー」エリア > 「レンダー」メニュー
# "TOPBAR" Area > "Render" Menu

import bpy
import sys, subprocess
from bpy.props import *

################
# オペレーター #
################

class SetRenderResolutionPercentage(bpy.types.Operator):
	bl_idname = "render.set_render_resolution_percentage"
	bl_label = "Set Rendering Image's Size (%)"
	bl_description = "Set rendering's size as a percentage of the resolution settings"
	bl_options = {'REGISTER', 'UNDO'}

	size : IntProperty(name="Render Size (%)", default=100, min=1, max=1000, soft_min=1, soft_max=1000, step=1)

	def execute(self, context):
		context.scene.render.resolution_percentage = self.size
		return {'FINISHED'}

class SetRenderSlot(bpy.types.Operator):
	bl_idname = "render.set_render_slot"
	bl_label = "Set Render Slot"
	bl_description = "Sets slot to save rendering results"
	bl_options = {'REGISTER', 'UNDO'}

	slot : IntProperty(name="Slot", default=1, min=0, max=100, soft_min=0, soft_max=100, step=1)

	def execute(self, context):
		for img in bpy.data.images:
			if (img.type == 'RENDER_RESULT'):
				img.render_slots.active_index = self.slot
		return {'FINISHED'}

class ToggleThreadsMode(bpy.types.Operator):
	bl_idname = "render.toggle_threads_mode"
	bl_label = "Change Number of Threads"
	bl_description = "Toggles thread number of CPUS used to render"
	bl_options = {'REGISTER', 'UNDO'}

	threads : IntProperty(name="Number of Threads", default=1, min=1, max=16, soft_min=1, soft_max=16, step=1)

	def execute(self, context):
		if (context.scene.render.threads_mode == 'FIXED'):
			context.scene.render.threads = self.threads
		return {'FINISHED'}
	def invoke(self, context, event):
		self.threads = context.scene.render.threads
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop(context.scene.render, 'threads_mode', expand=True)
		if context.scene.render.threads_mode == 'FIXED':
			sp = self.layout.split(factor=0.55)
			row = sp.row()
			row.label(text="")
			row.label(text="Number of Threads")
			sp.prop(self, 'threads', text="")

class SetAllSubsurfRenderLevels(bpy.types.Operator):
	bl_idname = "render.set_all_subsurf_render_levels"
	bl_label = "Set Subsurfs' Subdivisions when Rendering"
	bl_description = "Set all subsurfs' numbers of subdivisions when rendering together"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('ABSOLUTE', "Absolute Value", "", 1),
		('RELATIVE', "Relative Value", "", 2),
		]
	mode : EnumProperty(items=items, name="Setting Mode")
	levels : IntProperty(name="Number of Subdivisions", default=2, min=-20, max=20, soft_min=-20, soft_max=20, step=1)

	def execute(self, context):
		for obj in bpy.data.objects:
			if (obj.type != 'MESH' and obj.type != 'CURVE'):
				continue
			for mod in obj.modifiers:
				if (mod.type == 'SUBSURF'):
					if (self.mode == 'ABSOLUTE'):
						mod.render_levels = self.levels
					elif (self.mode == 'RELATIVE'):
						mod.render_levels += self.levels
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class SyncAllSubsurfRenderLevels(bpy.types.Operator):
	bl_idname = "render.sync_all_subsurf_render_levels"
	bl_label = "Set Subdivisions Based on Number in Viewport"
	bl_description = "Set the number of subdivisions when rendering based on the number in viewport"
	bl_options = {'REGISTER', 'UNDO'}

	level_offset : IntProperty(name="Offset", default=0, min=-20, max=20, soft_min=-20, soft_max=20, step=1)

	def execute(self, context):
		for obj in bpy.data.objects:
			if (obj.type != 'MESH'):
				continue
			for mod in obj.modifiers:
				if (mod.type == 'SUBSURF'):
					mod.render_levels = mod.levels + self.level_offset
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		box = self.layout.box()
		row = box.split(factor=0.65)
		row.label(text="'When Rendering' = 'In Viewport' + ")
		row.prop(self, 'level_offset', text="")

class SimplifyRenderPanel(bpy.types.Operator):
	bl_idname = "render.siplify_render_panel"
	bl_label = "Change 'Simpify' Settings"
	bl_description = "Change render's 'simpify' settings"

	item = [('0',"Disabled", "", 1), ('1',"Enabled", "", 2)]
	is_use : EnumProperty(name="Method", items=item)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=375)
	def draw(self, context):
		self.layout.prop(self, 'is_use', expand=True)
		box1 = self.layout.box()
		if int(self.is_use):
			row = box1.split(factor=0.2)			
			row.label(text="Vierport")
			row.label(text="Upper Limit of Subdivisions")
			row.prop(context.scene.render, "simplify_subdivision", text="")
			row = box1.split(factor=0.61)
			row_row = row.split(factor=0.15)
			row_row.label(text="")
			row_row.label(text="Ratio of Displayed Child Particles")
			row.prop(context.scene.render, "simplify_child_particles", text="")
			if context.scene.render.engine == 'CYCLES':
				row = box1.split(factor=0.61)
				row_row = row.split(factor=0.15)
				row_row.label(text="")
				row_row.label(text="Upper Limit of texture size")
				row.prop(context.scene.cycles, "texture_limit", text="")
				row = box1.split(factor=0.61)
				row_row = row.split(factor=0.15)
				row_row.label(text="")
				row_row.label(text="Bounces of AO")
				row.prop(context.scene.cycles, "ao_bounces", text="")
			box2 = self.layout.box()
			row = box2.split(factor=0.2)
			row.label(text="Rendering")
			row.label(text="Upper Limit of Subdivisions")
			row.prop(context.scene.render, "simplify_subdivision_render", text="")
			row = box2.split(factor=0.61)
			row_row = row.split(factor=0.15)
			row_row.label(text="")
			row_row.label(text="Ratio of Displayed Child Particles")
			row.prop(context.scene.render, "simplify_child_particles_render", text="")
			if context.scene.render.engine == 'CYCLES':
				row = box2.split(factor=0.61)
				row_row = row.split(factor=0.15)
				row_row.label(text="")
				row_row.label(text="Upper Limit of texture size")
				row.prop(context.scene.cycles, "texture_limit_render", text="")
				row = box2.split(factor=0.61)
				row_row = row.split(factor=0.15)
				row_row.label(text="")
				row_row.label(text="Bounces of AO")
				row.prop(context.scene.cycles, "ao_bounces_render", text="")
		#self.layout.prop(context.scene.render, "simplify_shadow_samples", icon="PLUGIN")
		#self.layout.prop(context.scene.render, "simplify_ao_sss", icon="PLUGIN")
		#self.layout.prop(context.scene.render, "use_simplify_triangulate", icon="PLUGIN")

	def execute(self, context):
		context.scene.render.use_simplify = int(self.is_use)
		return {'FINISHED'}

################
# サブメニュー #
################

class RenderResolutionPercentageMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_render_resolution_percentage"
	bl_label = "Set Rendering Image's Size (%)"
	bl_description = "Set rendering's size as a percentage of the resolution settings"

	def draw(self, context):
		x = bpy.context.scene.render.resolution_x
		y = bpy.context.scene.render.resolution_y
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="10% ("+str(int(x*0.1))+"x"+str(int(y*0.1))+")", icon="PLUGIN").size = 10
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="20% ("+str(int(x*0.2))+"x"+str(int(y*0.2))+")", icon="PLUGIN").size = 20
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="30% ("+str(int(x*0.3))+"x"+str(int(y*0.3))+")", icon="PLUGIN").size = 30
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="40% ("+str(int(x*0.4))+"x"+str(int(y*0.4))+")", icon="PLUGIN").size = 40
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="50% ("+str(int(x*0.5))+"x"+str(int(y*0.5))+")", icon="PLUGIN").size = 50
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="60% ("+str(int(x*0.6))+"x"+str(int(y*0.6))+")", icon="PLUGIN").size = 60
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="70% ("+str(int(x*0.7))+"x"+str(int(y*0.7))+")", icon="PLUGIN").size = 70
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="80% ("+str(int(x*0.8))+"x"+str(int(y*0.8))+")", icon="PLUGIN").size = 80
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="90% ("+str(int(x*0.9))+"x"+str(int(y*0.9))+")", icon="PLUGIN").size = 90
		self.layout.separator()
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="100% ("+str(int(x))+"x"+str(int(y))+")", icon="PLUGIN").size = 100
		self.layout.separator()
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="150% ("+str(int(x*1.5))+"x"+str(int(y*1.5))+")", icon="PLUGIN").size = 150
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="200% ("+str(int(x*2.0))+"x"+str(int(y*2.0))+")", icon="PLUGIN").size = 200
		self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="300% ("+str(int(x*3.0))+"x"+str(int(y*3.0))+")", icon="PLUGIN").size = 300

class SlotsRenderMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_render_slots"
	bl_label = "Set Render Slot"
	bl_description = "Change the render slot"

	def draw(self, context):
		for i in range(max([len(im.render_slots) for im in bpy.data.images])):
			self.layout.operator(SetRenderSlot.bl_idname, text="Slot"+str(i+1)).slot = i

class SubsurfMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_render_subsurf"
	bl_label = "Set Subsurfs' Subdivisions when Rendering"
	bl_description = "Set all subsurfs' numbers of subdivisions when rendering together"

	def draw(self, context):
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="+1 Subdivisions", icon="PLUGIN")
		operator.mode = 'RELATIVE'
		operator.levels = 1
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="-1 Subdivisions", icon="PLUGIN")
		operator.mode = 'RELATIVE'
		operator.levels = -1
		self.layout.separator()
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivisions: 0", icon="PLUGIN")
		operator.mode = 'ABSOLUTE'
		operator.levels = 0
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivisions: 1", icon="PLUGIN")
		operator.mode = 'ABSOLUTE'
		operator.levels = 1
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivisions: 2", icon="PLUGIN")
		operator.mode = 'ABSOLUTE'
		operator.levels = 2
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivisions: 3", icon="PLUGIN")
		operator.mode = 'ABSOLUTE'
		operator.levels = 3
		self.layout.separator()
		self.layout.operator(SyncAllSubsurfRenderLevels.bl_idname, icon="PLUGIN")

################
# クラスの登録 #
################

classes = [
	SetRenderResolutionPercentage,
	SetRenderSlot,
	ToggleThreadsMode,
	SetAllSubsurfRenderLevels,
	SyncAllSubsurfRenderLevels,
	RenderResolutionPercentageMenu,
	SimplifyRenderPanel,
	SlotsRenderMenu,
	SubsurfMenu
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
		self.layout.prop(context.scene.render, 'resolution_x', text="Resolution X", icon="PLUGIN")
		self.layout.prop(context.scene.render, 'resolution_y', text="Resolution Y", icon="PLUGIN")
		self.layout.prop(context.scene.render, 'resolution_percentage', text="Rendering Image's Size", icon="PLUGIN")
		self.layout.menu(RenderResolutionPercentageMenu.bl_idname, icon="PLUGIN")
		for img in bpy.data.images:
			if (img.type == 'RENDER_RESULT'):
				self.layout.menu(SlotsRenderMenu.bl_idname, text=f"Set RenderSlot (Now: slot {str(img.render_slots.active_index+1)})", icon="PLUGIN")
				break
		self.layout.prop_menu_enum(context.scene.render.image_settings, 'file_format', text="Set File Format", icon="PLUGIN")
		self.layout.separator()
		self.layout.prop(context.scene, 'frame_start', text="Start Frame", icon="PLUGIN")
		self.layout.prop(context.scene, 'frame_end', text="End Frame", icon="PLUGIN")
		self.layout.prop(context.scene, 'frame_step', text="Frame Step", icon="PLUGIN")
		self.layout.prop(context.scene.render, 'fps', text="FPS", icon="PLUGIN")
		self.layout.separator()
		if context.scene.render.engine == "CYCLES":
			self.layout.prop(context.scene.world.light_settings, 'use_ambient_occlusion', text="Use AO", icon="PLUGIN")
		elif context.scene.render.engine == "BLENDER_EEVEE":
			self.layout.prop(context.scene.eevee, 'use_gtao', text="Use AO", icon="PLUGIN")
			self.layout.prop(context.scene.eevee, 'use_bloom', text="Use Bloom", icon="PLUGIN")
			self.layout.prop(context.scene.eevee, 'use_shadow_high_bitdepth', text="Use High Bitdepth Shadows", icon="PLUGIN")
			self.layout.prop(context.scene.eevee, 'use_soft_shadows', text="Use Soft Shadows", icon="PLUGIN")
		self.layout.prop(context.scene.render, 'use_freestyle', text="Use FreeStyle", icon="PLUGIN")
		self.layout.separator()
		if context.scene.render.engine == "CYCLES":
			if (context.scene.render.threads_mode == 'AUTO'):
				text = f"{ToggleThreadsMode.bl_label} (Now: Auto-detect)"
			else:
				text = f"{ToggleThreadsMode.bl_label} (Now: Fixed)"
			self.layout.operator(ToggleThreadsMode.bl_idname, text=text, icon="PLUGIN")
		self.layout.menu(SubsurfMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SimplifyRenderPanel.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
