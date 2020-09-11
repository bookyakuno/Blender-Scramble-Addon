# 「プロパティ」エリア > 「レンダー」タブ > 「レンダー」パネル
# "Propaties" Area > "Render" Tab > "Render" Panel

import bpy
from bpy.props import *
import sys, subprocess
from bpy.app.handlers import persistent

################
# オペレーター #
################

class RenderBackground(bpy.types.Operator):
	bl_idname = "render.render_background"
	bl_label = "Background Rendering"
	bl_description = "Renders current blend file from command line"
	bl_options = {'REGISTER'}

	is_quit : BoolProperty(name="Quit Blender", default=False)
	items = [
		('IMAGE', "Image", "", 1),
		('ANIME', "Animation", "", 2),
		]
	mode : EnumProperty(items=items, name="Setting Mode", default='IMAGE')
	thread : IntProperty(name="Number of Threads", default=0, min=1, max=16, soft_min=1, soft_max=16)

	@classmethod
	def poll(cls, context):
		if (bpy.data.filepath == ""):
			return False
		return True
	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.scale_y = 1.2
		row.prop(self,"mode",expand=True)
		layout.prop(self,"thread")
		layout.separator()
		layout.prop(self,"is_quit")
		return {'FINISHED'}
	def execute(self, context):
		blend_path = bpy.data.filepath
		if (self.mode == 'IMAGE'):
			subprocess.Popen([sys.argv[0], '-b', blend_path, '-f', str(context.scene.frame_current), '-t', str(self.thread)])
		elif (self.mode == 'ANIME'):
			subprocess.Popen([sys.argv[0], '-b', blend_path, '-a', '-t', str(self.thread)])
		if (self.is_quit):
			bpy.ops.wm.quit_blender()
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)



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
