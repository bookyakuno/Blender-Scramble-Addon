# 「3Dビュー」エリア > 「オブジェクト」モード > 「オブジェクト」メニュー
# "3D View" Area > "Object" Mode > "Object" Menu

import bpy, bmesh
from bpy.props import *

################
# パイメニュー #
################

class CopyPieOperator(bpy.types.Operator):
	bl_idname = "object.copy_pie_operator"
	bl_label = "Copy"
	bl_description = "Pie object copy is"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=CopyPie.bl_idname)
		return {'FINISHED'}
class CopyPie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_copy"
	bl_label = "Copy"
	bl_description = "Pie object copy is"

	def draw(self, context):
		self.layout.menu_pie().operator("view3d.copybuffer", icon="COPY_ID")
		self.layout.menu_pie().operator(CopyObjectName.bl_idname, icon="MONKEY")

class ObjectModePieOperator(bpy.types.Operator):
	bl_idname = "object.object_mode_pie_operator"
	bl_label = "Object Modes"
	bl_description = "Is pie menu objects in interactive mode"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=ObjectModePie.bl_idname)
		return {'FINISHED'}
class ObjectModePie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_object_mode"
	bl_label = "Object Modes"
	bl_description = "Is pie menu objects in interactive mode"

	def draw(self, context):
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="Pose", icon="POSE_HLT").mode = "POSE"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="Sculpt", icon="SCULPTMODE_HLT").mode = "SCULPT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="Weight Paint", icon="WPAINT_HLT").mode = "WEIGHT_PAINT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="Object", icon="OBJECT_DATAMODE").mode = "OBJECT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="Particle Edit", icon="PARTICLEMODE").mode = "PARTICLE_EDIT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="Edit", icon="EDITMODE_HLT").mode = "EDIT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="Texture Paint", icon="TPAINT_HLT").mode = "TEXTURE_PAINT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="Vertex Paint", icon="VPAINT_HLT").mode = "VERTEX_PAINT"
class SetObjectMode(bpy.types.Operator): #
	bl_idname = "object.set_object_mode"
	bl_label = "Set Object Modes"
	bl_description = "Set interactive mode of object"
	bl_options = {'REGISTER'}

	mode : StringProperty(name="Interactive Mode", default="OBJECT")

	def execute(self, context):
		if (context.active_object):
			try:
				bpy.ops.object.mode_set(mode=self.mode)
			except TypeError:
				self.report(type={"WARNING"}, message=context.active_object.name+" Is able to enter interactive mode")
		else:
			self.report(type={"WARNING"}, message="There is no active object")
		return {'FINISHED'}

class SubdivisionSetPieOperator(bpy.types.Operator):
	bl_idname = "object.subdivision_set_pie_operator"
	bl_label = "Subsurf Setting"
	bl_description = "Is pie menu to set Subsurf levels"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=SubdivisionSetPie.bl_idname)
		return {'FINISHED'}
class SubdivisionSetPie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_subdivision_set"
	bl_label = "Subsurf Setting"
	bl_description = "Is pie menu to set Subsurf levels"

	def draw(self, context):
		self.layout.menu_pie().operator("object.subdivision_set", text="Level: 2", icon="MOD_SUBSURF").level = 2
		self.layout.menu_pie().operator("object.subdivision_set", text="Level: 6", icon="MOD_SUBSURF").level = 6
		self.layout.menu_pie().operator("object.subdivision_set", text="Level: 0", icon="MOD_SUBSURF").level = 0
		self.layout.menu_pie().operator("object.subdivision_set", text="Level: 4", icon="MOD_SUBSURF").level = 4
		self.layout.menu_pie().operator("object.subdivision_set", text="Level: 3", icon="MOD_SUBSURF").level = 3
		self.layout.menu_pie().operator("object.subdivision_set", text="Level: 5", icon="MOD_SUBSURF").level = 5
		self.layout.menu_pie().operator("object.subdivision_set", text="Level: 1", icon="MOD_SUBSURF").level = 1

class DrawTypePieOperator(bpy.types.Operator):
	bl_idname = "object.display_type_pie_operator"
	bl_label = "Maximum Draw Type"
	bl_description = "Is pie menu to set up drawing type"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=DrawTypePie.bl_idname)
		return {'FINISHED'}
class DrawTypePie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_display_type"
	bl_label = "Maximum Draw Type"
	bl_description = "Is pie menu to set up drawing type"

	def draw(self, context):
		self.layout.menu_pie().operator(SetDrawType.bl_idname, text="Bound", icon="BBOX").type = "BOUNDS"
		self.layout.menu_pie().operator(SetDrawType.bl_idname, text="Wire Frame", icon="WIRE").type = "WIRE"
		self.layout.menu_pie().operator(SetDrawType.bl_idname, text="Solid", icon="SOLID").type = "SOLID"
		self.layout.menu_pie().operator(SetDrawType.bl_idname, text="Texture", icon="POTATO").type = "TEXTURED"
class SetDrawType(bpy.types.Operator): #
	bl_idname = "object.set_display_type"
	bl_label = "Setting maximum Drawing Type"
	bl_description = "Set maximum drawing type"
	bl_options = {'REGISTER'}

	type : StringProperty(name="Drawing Type", default="OBJECT")

	def execute(self, context):
		for obj in context.selected_objects:
			obj.display_type = self.type
		return {'FINISHED'}

################
# オペレーター #
################

class DeleteUnmassage(bpy.types.Operator):
	bl_idname = "object.delete_unmassage"
	bl_label = "Delete Without Confirmation"
	bl_description = "Deletes object without displaying confirmation message when deleting"
	bl_options = {'REGISTER', 'UNDO'}

	use_global : BoolProperty(name="Delete All", default=False)

	def execute(self, context):
		if (context.active_object):
			self.report(type={"INFO"}, message=context.active_object.name+" such as deleted")
		bpy.ops.object.delete(use_global=self.use_global)
		return {'FINISHED'}

################
# サブメニュー #
################

class PieMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_menu"
	bl_label = "Pie Menu"
	bl_description = "Is pie on object action menu"

	def draw(self, context):
		self.layout.operator(CopyPieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(ObjectModePieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(SubdivisionSetPieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(DrawTypePieOperator.bl_idname, icon="PLUGIN")

class ShortcutMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_shortcut"
	bl_label = "By Shortcuts"
	bl_description = "Looks useful functions is to register shortcut"

	def draw(self, context):
		self.layout.operator(DeleteUnmassage.bl_idname, icon="PLUGIN")
		self.layout.operator(ApplyModifiersAndJoin.bl_idname, icon="PLUGIN")

################
# クラスの登録 #
################

classes = [
	CopyPieOperator,
	CopyPie,
	ObjectModePieOperator,
	ObjectModePie,
	SetObjectMode,
	SubdivisionSetPieOperator,
	SubdivisionSetPie,
	DrawTypePieOperator,
	DrawTypePie,
	SetDrawType,
	DeleteUnmassage,
	PieMenu,
	ShortcutMenu
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

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.menu(ShortcutMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(PieMenu.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
