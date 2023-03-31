# 「テキストエディター」エリア > 「テキスト」メニュー
# "Text Editor" Area > "Text" Menu

import bpy
from bpy.props import *
import os, subprocess

################
# オペレーター #
################

class ExternalEdit(bpy.types.Operator):
	bl_idname = "text.external_edit"
	bl_label = "Edit with External Editors"
	bl_description = "Open current text in text editors referenced at User Preference"
	bl_options = {'REGISTER', 'UNDO'}

	index : IntProperty(name="Index", default=1, min=1, max=3, soft_min=1, soft_max=3)

	@classmethod
	def poll(cls, context):
		if (not context.edit_text):
			return False
		if (context.edit_text.filepath == ""):
			return False
		return True
	def execute(self, context):
		path = bpy.path.abspath(context.edit_text.filepath)
		if (self.index == 1):
			editor_path = context.preferences.addons[__name__.partition('.')[0]].preferences.text_editor_path_1
		elif (self.index == 2):
			editor_path = context.preferences.addons[__name__.partition('.')[0]].preferences.text_editor_path_2
		elif (self.index == 3):
			editor_path = context.preferences.addons[__name__.partition('.')[0]].preferences.text_editor_path_3
		subprocess.Popen([editor_path, path])
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	ExternalEdit
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
		pref = context.preferences.addons[__name__.partition('.')[0]].preferences
		paths = [pref.text_editor_path_1, pref.text_editor_path_2, pref.text_editor_path_3]
		if sum([len(x) for x in paths]):
			self.layout.separator()
			self.layout.label(text="== Edit Text with Editors ==")
			for idx, p in enumerate(paths):
				if p:
					path = os.path.basename(p)
					name, ext = os.path.splitext(path)
					self.layout.operator(ExternalEdit.bl_idname, icon="PLUGIN", text=f"= {name} =").index = idx
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
