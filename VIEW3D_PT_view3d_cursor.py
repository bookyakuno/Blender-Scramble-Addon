# 「3Dビュー」エリア > プロパティ > 「3Dカーソル」パネル
# "3D View" Area > Propaties > "3D Cursor" Panel

import bpy

################
# オペレーター #
################

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		row = self.layout.row(align=True)
		row.operator('view3d.snap_cursor_to_selected', icon='LAYER_ACTIVE', text="To Select")
		row.operator('view3d.snap_cursor_to_center', icon='X', text="Reset")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
