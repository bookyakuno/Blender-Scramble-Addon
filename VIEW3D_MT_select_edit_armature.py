# 「3Dビュー」エリア > 「アーマチュア編集」モード > 「選択」メニュー
# "3D View" Area > "Armature Edit" Mode > "Select" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class SelectOneAndPathForEdit(bpy.types.Operator):
	bl_idname = "armature.select_one_and_path"
	bl_label = "Select Bones to Mouse"
	bl_description = "Select bones which exist between selected bones and mouse position"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.selected_bones or context.selected_pose_bones:
			return True
		return False

	def execute(self, context):
		bpy.ops.object.mode_set(mode='POSE')
		bpy.ops.pose.select_one_and_path('INVOKE_DEFAULT')
		bpy.ops.object.mode_set(mode='EDIT')
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	SelectOneAndPathForEdit
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
		#以下は全て VIEW3D_MT_select_pose で定義
		self.layout.separator()
		self.layout.operator('pose.select_path', icon='PLUGIN')
		self.layout.operator('pose.select_parent_end', icon='PLUGIN')
		self.layout.operator('pose.select_children_end', icon='PLUGIN')
		self.layout.operator('pose.select_both_end', icon='PLUGIN')
		self.layout.separator()
		self.layout.operator('pose.select_axis_over', icon='PLUGIN')
		self.layout.operator('pose.select_serial_number_name_bone', icon='PLUGIN')
		self.layout.operator('pose.select_move_symmetry_name_bones', icon='PLUGIN').keep_current = True
		self.layout.separator()
		self.layout.operator('pose.select_move_symmetry_name_bones', text="Change Selection (Flipped-Name)", icon='PLUGIN').keep_current = False
		self.layout.operator(SelectOneAndPathForEdit.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
