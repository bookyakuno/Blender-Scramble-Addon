# 「3Dビュー」エリア > プロパティ > 「トランスフォーム座標系」パネル
# "3D View" Area > Propaties > "Transform Orientations" Panel

import bpy
from bpy.ops import *

################
# オペレーター #
################

##########
# パネル #
##########

class VIEW3D_PT_scramble_view3d_orientation(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "View"
	bl_label = "Transform Orientations"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		if (IsMenuEnable(__name__.split('.')[-1])):
			box = self.layout.box()
			box.props_enum(context.scene.transform_orientation_slots[0], "type")
			row = self.layout.row()
			operator = row.operator("transform.create_orientation", text="", icon='ADD')
			operator.use = True
			operator.overwrite = True
			if context.scene.transform_orientation_slots[0].custom_orientation != None:
				row.prop(context.scene.transform_orientation_slots[0].custom_orientation, "name", text="")
				row.operator("transform.delete_orientation", text="", icon='PANEL_CLOSE')
		if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
			self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]

################
# クラスの登録 #
################

classes = [
	VIEW3D_PT_scramble_view3d_orientation,
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
