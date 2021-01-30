# 「ユーザー設定」エリア > 「ファイルパス」タブ
# "User Preferences" Area > "File Paths" Tab

import bpy
from bpy.props import *
import sys, platform
try:
	import winreg
except:
	pass

################
# オペレーター #
################

class RegisterBlendFile(bpy.types.Operator):
	bl_idname = "system.register_blend_file"
	bl_label = "Associate blend File to Current Version of Blender"
	bl_description = "Associate blend files to the current version of Blender"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		if (platform.system() != 'Windows'):
			return False
		return True
	def execute(self, context):
		winreg.SetValue(winreg.HKEY_CURRENT_USER, r"Software\Classes\.blend", winreg.REG_SZ, 'blend_auto_file')
		winreg.SetValue(winreg.HKEY_CURRENT_USER, r"Software\Classes\blend_auto_file\shell\open\command", winreg.REG_SZ, '"'+sys.argv[0]+'" "%1"')
		self.report(type={"INFO"}, message="Target files have been associated to the current version")
		return {'FINISHED'}

class RegisterBlendBackupFiles(bpy.types.Operator):
	bl_idname = "system.register_blend_backup_files"
	bl_label = "Associate Backup File to Current Version"
	bl_description = "Associate backup files such as blend1 to the current version of Blender"
	bl_options = {'REGISTER'}

	max : IntProperty(name="Limit of files to associate", default=10, min=1, max=1000, soft_min=1, soft_max=1000)

	@classmethod
	def poll(cls, context):
		if (platform.system() != 'Windows'):
			return False
		return True
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		row = self.layout.split(factor=0.33)
		row.label(text="Files to associate")
		row = row.box().row(align=True)
		for tx in ["blend1", " ", "~", "blend"]:
			row.label(text=tx)
		row.prop(self, 'max', text="")

	def execute(self, context):
		winreg.SetValue(winreg.HKEY_CURRENT_USER, r"Software\Classes\blend1_auto_file\shell\open\command", winreg.REG_SZ, '"'+sys.argv[0]+'" "%1"')
		for i in range(self.max):
			i += 1
			winreg.SetValue(winreg.HKEY_CURRENT_USER, r"Software\Classes\.blend"+str(i), winreg.REG_SZ, 'blend1_auto_file')
		self.report(type={"INFO"}, message="Target files have been associated to the current version")
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	RegisterBlendFile,
	RegisterBlendBackupFiles
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
		self.layout.label(text="Scramble Addon:", icon='PLUGIN')
		split = self.layout.split(factor=0.7)
		split_sub = split.split(factor=0.95)
		col = split_sub.column()
		col.label(text="External Image Editor")
		col.prop(context.preferences.addons[__name__.partition('.')[0]].preferences, 'image_editor_path_1', text="")
		col.prop(context.preferences.addons[__name__.partition('.')[0]].preferences, 'image_editor_path_2', text="")
		col.prop(context.preferences.addons[__name__.partition('.')[0]].preferences, 'image_editor_path_3', text="")
		col.label(text="External Text Editor")
		col.prop(context.preferences.addons[__name__.partition('.')[0]].preferences, 'text_editor_path_1', text="")
		col.prop(context.preferences.addons[__name__.partition('.')[0]].preferences, 'text_editor_path_2', text="")
		col.prop(context.preferences.addons[__name__.partition('.')[0]].preferences, 'text_editor_path_3', text="")

		col = split.column()
		col.label(text="File Associations (Windows Only)")
		col.operator(RegisterBlendFile.bl_idname, icon='PLUGIN', text="Blend File")
		col.operator(RegisterBlendBackupFiles.bl_idname, icon='PLUGIN', text="Backup File")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
