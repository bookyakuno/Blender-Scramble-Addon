# 「プロパティ」エリア > 「ボーン」タブ > 「表示」パネル
# "Propaties" Area > "Bone" Tab > "Display" Panel

import bpy

################
# オペレーター #
################

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
		split = self.layout.split()
		split.label(text="")
		split.operator('pose.create_custom_shape', icon='PARTICLE_PATH')# VIEW3D_MT_pose_context_menu.py で定義
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
