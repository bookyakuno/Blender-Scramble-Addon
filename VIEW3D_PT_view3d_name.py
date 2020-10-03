# 「3Dビュー」エリア > プロパティパネル > 「アイテム」パネル
# "3D View" Area > Propaties > "Item" Panel

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
		row.alignment = 'RIGHT'
		row.label(text="To Clipboard", icon='COPYDOWN')
		row.operator('object.copy_object_name', icon='OBJECT_DATAMODE', text="")
		if (context.active_bone or context.active_pose_bone):
			row.operator('object.copy_bone_name', icon='BONE_DATA', text="")
		row.operator('object.copy_data_name', icon='EDITMODE_HLT', text="")
		row = self.layout.row(align=True)
		row.alignment = 'RIGHT'
		row.label(text="Name Sync", icon='LINKED')
		row.operator('object.object_name_to_data_name', icon='TRIA_DOWN_BAR', text="")
		row.operator('object.data_name_to_object_name', icon='TRIA_UP_BAR', text="")
		if context.object:
			self.layout.template_ID(context.object, 'data')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
