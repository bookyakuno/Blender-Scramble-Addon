# 「3Dビュー」エリア > 「アーマチュア編集」モード > 「選択」メニュー
# "3D View" Area > "Armature Edit" Mode > "Select" Menu

import bpy

################
# オペレーター #
################

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.operator('pose.select_path', icon='PLUGIN')
		self.layout.operator('pose.select_parent_end', icon='PLUGIN')
		self.layout.operator('pose.select_children_end', icon='PLUGIN')
		self.layout.separator()
		self.layout.operator('pose.select_axis_over', icon='PLUGIN')
		self.layout.operator('pose.select_serial_number_name_bone', icon='PLUGIN')
		self.layout.operator('pose.select_move_symmetry_name_bones', icon='PLUGIN')
		self.layout.separator()
		self.layout.menu('VIEW3D_MT_select_pose_grouped', icon='PLUGIN')
		self.layout.separator()
		self.layout.menu('VIEW3D_MT_select_pose_shortcuts', icon='PLUGIN')
	if (context.preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
