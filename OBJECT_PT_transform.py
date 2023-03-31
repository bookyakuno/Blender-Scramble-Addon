# 「プロパティ」エリア > 「オブジェクト」タブ > 「トランスフォーム」パネル
# "Propaties" Area > "Object" Tab > "Transform" Panel

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
		row = self.layout.row(align=True)
		op = row.operator('object.make_link_transform', icon='CON_LOCLIKE', text="Copy Location")
		#VIEW3D_MT_make_links.py で定義
		op.copy_location, op.copy_rotation, op.copy_scale = True, False, False
		op = row.operator('object.make_link_transform', icon='CON_ROTLIKE', text="Copy Rotation")
		op.copy_location, op.copy_rotation, op.copy_scale = False, True, False
		op = row.operator('object.make_link_transform', icon='CON_SIZELIKE', text="Copy Scale")
		op.copy_location, op.copy_rotation, op.copy_scale = False, False, True
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
