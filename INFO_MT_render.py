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
	bl_label = "Set multi of resolution"
	bl_description = "Set to be rendered settings resolution percentage?"
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
	bl_label = "Switch Use Threads"
	bl_description = "Toggles thread number of CPUS used to render"
	bl_options = {'REGISTER', 'UNDO'}

	threads : IntProperty(name="Number of Threads", default=1, min=1, max=16, soft_min=1, soft_max=16, step=1)

	def execute(self, context):
		if (context.scene.render.threads_mode == 'AUTO'):
			context.scene.render.threads_mode = 'FIXED'
			context.scene.render.threads = self.threads
		else:
			context.scene.render.threads_mode = 'AUTO'
		return {'FINISHED'}
	def invoke(self, context, event):
		if (context.scene.render.threads_mode == 'AUTO'):
			self.threads = context.scene.render.threads
			return context.window_manager.invoke_props_dialog(self)
		else:
			return self.execute(context)

class SetAllSubsurfRenderLevels(bpy.types.Operator):
	bl_idname = "render.set_all_subsurf_render_levels"
	bl_label = "Set Subsurf levels during rendering"
	bl_description = "Together sets granularity of Subsurf applied during rendering"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('ABSOLUTE', "Absolute Value", "", 1),
		('RELATIVE', "Relative Value", "", 2),
		]
	mode : EnumProperty(items=items, name="Setting Mode")
	levels : IntProperty(name="Level of Subsurf", default=2, min=-20, max=20, soft_min=-20, soft_max=20, step=1)

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
					else:
						self.report(type={'ERROR'}, message="Invalid Setting Value")
						return {'CANCELLED'}
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class SyncAllSubsurfRenderLevels(bpy.types.Operator):
	bl_idname = "render.sync_all_subsurf_render_levels"
	bl_label = "Sync preview value when rendering Subsurf levels"
	bl_description = "Granularity of Subsurf apply when rendering entire object sets level in preview"
	bl_options = {'REGISTER', 'UNDO'}

	level_offset : IntProperty(name="Subdivision-level Offset", default=0, min=-20, max=20, soft_min=-20, soft_max=20, step=1)

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

################
# サブメニュー #
################

class RenderResolutionPercentageMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_render_resolution_percentage"
	bl_label = "Render Size (%)"
	bl_description = "Set to be rendered settings resolution percentage?"

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

class SimplifyRenderMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_render_simplify"
	bl_label = "Simplification of Render"
	bl_description = "Simplify Rendering Settings"

	def draw(self, context):
		self.layout.prop(context.scene.render, "use_simplify", icon="PLUGIN")
		self.layout.separator()
		self.layout.prop(context.scene.render, "simplify_subdivision", icon="PLUGIN")
		#self.layout.prop(context.scene.render, "simplify_shadow_samples", icon="PLUGIN")
		self.layout.prop(context.scene.render, "simplify_child_particles", icon="PLUGIN")
		#self.layout.prop(context.scene.render, "simplify_ao_sss", icon="PLUGIN")
		#self.layout.prop(context.scene.render, "use_simplify_triangulate", icon="PLUGIN")

class SlotsRenderMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_render_slots"
	bl_label = "Render Slots"
	bl_description = "Change slot to save rendering results"

	def draw(self, context):
		for i in range(max([len(im.render_slots) for im in bpy.data.images])):
			self.layout.operator(SetRenderSlot.bl_idname, text="Slot"+str(i+1)).slot = i
"""
class ShadeingMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_render_shadeing"
	bl_label = "Used Shading"
	bl_description = "Oon/Off shading"

	def draw(self, context):
		self.layout.prop(context.scene.render, 'use_textures', icon="PLUGIN")
		self.layout.prop(context.scene.render, 'use_shadows', icon="PLUGIN")
		self.layout.prop(context.scene.render, 'use_sss', icon="PLUGIN")
		self.layout.prop(context.scene.render, 'use_envmaps', icon="PLUGIN")
		self.layout.prop(context.scene.render, 'use_raytrace', icon="PLUGIN")
"""
class SubsurfMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_render_subsurf"
	bl_label = "All Subsurf Levels"
	bl_description = "Setting Subsurf subdivision level of all objects at once"

	def draw(self, context):
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision + 1", icon="PLUGIN")
		operator.mode = 'RELATIVE'
		operator.levels = 1
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision - 1", icon="PLUGIN")
		operator.mode = 'RELATIVE'
		operator.levels = -1
		self.layout.separator()
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision = 0", icon="PLUGIN")
		operator.mode = 'ABSOLUTE'
		operator.levels = 0
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision = 1", icon="PLUGIN")
		operator.mode = 'ABSOLUTE'
		operator.levels = 1
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision = 2", icon="PLUGIN")
		operator.mode = 'ABSOLUTE'
		operator.levels = 2
		operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision = 3", icon="PLUGIN")
		operator.mode = 'ABSOLUTE'
		operator.levels = 3
		self.layout.separator()
		self.layout.operator(SyncAllSubsurfRenderLevels.bl_idname, text="Sync Viewport Value", icon="PLUGIN")

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
	SimplifyRenderMenu,
	SlotsRenderMenu,
	#ShadeingMenu,
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
		self.layout.menu(RenderResolutionPercentageMenu.bl_idname, text="RenderSize (Now:"+str(context.scene.render.resolution_percentage)+"%)", icon="PLUGIN")
		for img in bpy.data.images:
			if (img.type == 'RENDER_RESULT'):
				self.layout.menu(SlotsRenderMenu.bl_idname, text="RenderSlot (Now: slot"+str(img.render_slots.active_index+1)+")", icon="PLUGIN")
				break
		self.layout.prop_menu_enum(context.scene.render.image_settings, 'file_format', text="File Format", icon="PLUGIN")
		self.layout.separator()
		self.layout.prop(context.scene, 'frame_start', text="Start Frame", icon="PLUGIN")
		self.layout.prop(context.scene, 'frame_end', text="End Frame", icon="PLUGIN")
		self.layout.prop(context.scene, 'frame_step', text="Frame Step", icon="PLUGIN")
		self.layout.prop(context.scene.render, 'fps', text="FPS", icon="PLUGIN")
		self.layout.separator()
		#self.layout.prop(context.scene.render, 'use_antialiasing', text="Use Anti-aliasing", icon="PLUGIN")
		self.layout.prop(context.scene.world.light_settings, 'use_ambient_occlusion', text="Use AO", icon="PLUGIN")
		self.layout.prop(context.scene.render, 'use_freestyle', text="Use FreeStyle", icon="PLUGIN")
		#self.layout.menu(ShadeingMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		text = ToggleThreadsMode.bl_label
		if (context.scene.render.threads_mode == 'AUTO'):
			text = text + " (Now Auto-sensing)"
		else:
			text = text + " (Current constant value:" + str(context.scene.render.threads) + ")"
		self.layout.operator(ToggleThreadsMode.bl_idname, text=text, icon="PLUGIN")
		self.layout.menu(SubsurfMenu.bl_idname, icon="PLUGIN")
		#self.layout.prop_menu_enum(context.scene.render, 'antialiasing_samples', text="Anti-aliasing Samples", icon="PLUGIN")
		#self.layout.prop(context.scene.world.light_settings, 'samples', text="AO Samples", icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(SimplifyRenderMenu.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
