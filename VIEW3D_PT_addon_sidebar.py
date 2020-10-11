# 「3Dビュー」エリア > サイドバー > 「Scramble」パネル
# "3D View" Area > Side bar> "Scramble" Panel

import bpy
from . import VIEW3D_PT_layers, VIEW3D_PT_transform_orientations, VIEW3D_PT_view3d_cursor, VIEW3D_PT_view3d_name, VIEW3D_PT_view3d_properties

if 'bpy' in locals():
	import importlib
	importlib.reload(VIEW3D_PT_transform_orientations)
	importlib.reload(VIEW3D_PT_view3d_name)

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
		return bpy.context.object

	def draw(self, context):
		VIEW3D_PT_view3d_name.menu(self, context)


class VIEW3D_PT_scramble_view3d_orientation(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "View"
	bl_label = "Transform Orientations"
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		VIEW3D_PT_transform_orientations.menu(self, context)


################
# クラスの登録 #
################

classes = [
	VIEW3D_PT_scramble_view3d_name,
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

# メニューを登録する関数
def menu(self, context):
	pass
