# 「情報」エリア > ヘッダー
# "Info" Area > Header

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
def menu_prepend(self, context):
#	if (IsMenuEnable(__name__.split('.')[-1])):
#		self.layout.operator('wm.load_last_file', icon='RECOVER_LAST', text="")
	if (context.preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
