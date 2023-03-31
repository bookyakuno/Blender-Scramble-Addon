# 「3Dビュー」エリア > サイドバー > 「アイテム」タブ > 「アイテム」パネル
# "3D View" Area > Sidebar > "Item" Tab > "Item" Panel

import bpy

################
# オペレーター #
################

##########
# パネル #
##########

class VIEW3D_PT_scramble_view3d_name(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Item"
	bl_label = "Item"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(cls, context):
		if context.object:
			return True
		else:
			return False

	def draw(self, context):
		if (IsMenuEnable(__name__.split('.')[-1])):
			if context.object:
				self.layout.prop(context.object,"name")
			else:
				self.layout.label(text="",icon="NONE")
			# 特に記載がない関数は OBJECT_PT_context_object で定義
			row = self.layout.split(factor=0.7,align=True)
			row.label(text="To Clipboard", icon='COPYDOWN')
			row.operator('object.copy_object_name', icon='OBJECT_DATAMODE', text="")
			if (context.active_bone or context.active_pose_bone):
				row.operator('object.copy_bone_name', icon='BONE_DATA', text="")# BONE_PT_context_bone.py で定義
			row.operator('object.copy_data_name', icon='EDITMODE_HLT', text="")
			row = self.layout.split(factor=0.7,align=True)
			row.label(text="Use Same Name", icon='LINKED')
			row.operator('object.object_name_to_data_name', icon='TRIA_DOWN_BAR', text="")
			row.operator('object.data_name_to_object_name', icon='TRIA_UP_BAR', text="")
			if context.object:
				self.layout.template_ID(context.object, 'data')
		if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
			self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]

################
# クラスの登録 #
################

classes = [
	VIEW3D_PT_scramble_view3d_name
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
