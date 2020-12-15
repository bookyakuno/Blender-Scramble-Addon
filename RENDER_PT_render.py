# 「プロパティ」エリア > 「レンダー」タブ > 「レンダー」パネル
# "Propaties" Area > "Render" Tab > "Render" Panel

import bpy
from bpy.props import *
import sys, subprocess

################
# オペレーター #
################

class RenderBackground(bpy.types.Operator):
	bl_idname = "render.render_background"
	bl_label = "Render from Command Line"
	bl_description = "Render the current blend file from command line"
	bl_options = {'REGISTER'}

	is_quit : BoolProperty(name="Quit Blender", default=False)
	file_items = [
		('IMAGE', "Image", "", 1),
		('ANIME', "Animation", "", 2),
		]
	file_mode : EnumProperty(items=file_items, name="Type", default='IMAGE')
	engine_items = [('BLENDER_EEVEE', "Eevee", "", 1),('CYCLES', "Cycles", "", 2)]
	engine_mode : EnumProperty(items=engine_items, name="Engine", default='BLENDER_EEVEE')
	thread : IntProperty(name="Number of Threads", default=0, min=1, max=16, soft_min=1, soft_max=16)

	@classmethod
	def poll(cls, context):
		if (bpy.data.filepath == ""):
			return False
		return True
	def invoke(self, context, event):
		self.thread = context.scene.render.threads
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop(self, 'engine_mode', expand=True)
		self.layout.prop(self, 'file_mode', expand=True)
		for p in ['thread', 'is_quit']:
			row = self.layout.row()
			row.use_property_split = True
			row.prop(self, p) 

	def execute(self, context):
		blend_path = bpy.data.filepath
		if (self.file_mode == 'IMAGE'):
			subprocess.Popen([sys.argv[0], '-b', blend_path, '-E', self.engine_mode, '-f', str(context.scene.frame_current), '-t', str(self.thread)])
		elif (self.file_mode == 'ANIME'):
			subprocess.Popen([sys.argv[0], '-b', blend_path, '-a', '-E', self.engine_mode, '-t', str(self.thread)])
		if (self.is_quit):
			bpy.ops.wm.quit_blender()
		return {'FINISHED'}



################
# クラスの登録 #
################


classes = [
	RenderBackground
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
		row = self.layout.row(align=True)
		row.operator("render.render", text="Render", icon='RENDER_STILL')
		row.operator("render.render", text="Animation", icon='RENDER_ANIMATION').animation = True
		row = self.layout.split()
		row.label(text="Display:")
		row = row.row(align=True)
		row.prop(context.preferences.view, "render_display_type", text="")
		row.prop(bpy.context.scene.render, "use_lock_interface", icon_only=True)
		self.layout.operator(RenderBackground.bl_idname, icon='CONSOLE')


	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
