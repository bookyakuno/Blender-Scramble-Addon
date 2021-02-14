# 「3Dビュー」エリア > サイドバー > 「ビュー」タブ > 「3Dカーソル」パネル
# "3D View" Area > Sidebar > "View" Tab > "3D Cursor" Panel

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
		row = self.layout.split(factor=0.2, align=True)
		row.label(text="Move")
		row.operator('view3d.snap_cursor_to_selected', icon='SNAP_VOLUME', text="Selected")
		row.operator('view3d.snap_cursor_to_center', icon='OBJECT_ORIGIN', text="Origin")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
