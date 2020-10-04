# 「3Dビュー」エリア > サイドバー > 「Scramble」パネル
# "3D View" Area > Side bar> "Scramble" Panel

import bpy
from . import VIEW3D_PT_layers, VIEW3D_PT_transform_orientations, VIEW3D_PT_view3d_cursor, VIEW3D_PT_view3d_name, VIEW3D_PT_view3d_properties

if 'bpy' in locals():
	import importlib
	importlib.reload(VIEW3D_PT_layers)
	importlib.reload(VIEW3D_PT_transform_orientations)
	importlib.reload(VIEW3D_PT_view3d_cursor)
	importlib.reload(VIEW3D_PT_view3d_name)
	importlib.reload(VIEW3D_PT_view3d_properties)

################
# オペレーター #
################

##########
# パネル #
##########

class VIEW3D_PT_scramble_view3d_properties(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Scramble"
	bl_label = "Properties"
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		VIEW3D_PT_view3d_properties.menu(self, context)


class VIEW3D_PT_scramble_view3d_name(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Scramble"
	bl_label = "Item name"
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		VIEW3D_PT_view3d_name.menu(self, context)


class VIEW3D_PT_scramble_view3d_cursor(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Scramble"
	bl_label = "Cursor"
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		VIEW3D_PT_view3d_cursor.menu(self, context)


class VIEW3D_PT_scramble_view3d_orientation(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Scramble"
	bl_label = "Transform Orientation"
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		VIEW3D_PT_transform_orientations.menu(self, context)


class VIEW3D_PT_scramble_view3d_collrections(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Scramble"
	bl_label = "Collection Display Panel"
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		VIEW3D_PT_layers.menu(self, context)


################
# クラスの登録 #
################

classes = [
	VIEW3D_PT_scramble_view3d_properties,
	VIEW3D_PT_scramble_view3d_name,
	VIEW3D_PT_scramble_view3d_cursor,
	VIEW3D_PT_scramble_view3d_orientation,
	VIEW3D_PT_scramble_view3d_collrections
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
