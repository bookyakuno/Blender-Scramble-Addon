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
		#Left - Right - Bottom - Top - TopLeft - TopRight - BottomLeft - BottomRight
		pie_menu = self.layout.menu_pie()
		pie_menu.operator('object.copy_object_name', icon="COPYDOWN")#OBJECT_PT_context_object で定義
		pie_menu.operator('object.make_link_object_name', icon="SYNTAX_OFF")#VIEW3D_MT_make_links.py で定義
		op = pie_menu.operator('object.make_link_transform', icon='CON_LOCLIKE', text="Copy Location")#VIEW3D_MT_make_links.py で定義
		op.copy_location, op.copy_rotation, op.copy_scale = True, False, False
		pie_menu.operator('object.make_links_data', icon='MATERIAL', text="Copy Material").type = 'MATERIAL'
		pie_menu.operator('object.make_links_data', icon='MODIFIER', text="Copy Modifier").type = 'MODIFIERS'
		pie_menu.operator('object.make_links_data', icon='GROUP', text="Move to Same Collection").type = 'GROUPS'
		op = pie_menu.operator('object.make_link_transform', icon='CON_ROTLIKE', text="Copy Rotation")
		op.copy_location, op.copy_rotation, op.copy_scale = False, True, False
		op = pie_menu.operator('object.make_link_transform', icon='CON_SIZELIKE', text="Copy Scale")
		op.copy_location, op.copy_rotation, op.copy_scale = False, False, True

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
		#Left - Right - Bottom - Top - TopLeft - TopRight - BottomLeft - BottomRight
		pie_menu = self.layout.menu_pie()
		pie_menu.enabled = (not context.active_object == None)
		pie_menu.operator(SetObjectMode.bl_idname, text="Pose", icon="POSE_HLT").mode = "POSE"
		pie_menu.operator(SetObjectMode.bl_idname, text="Sculpt", icon="SCULPTMODE_HLT").mode = "SCULPT"
		pie_menu.operator(SetObjectMode.bl_idname, text="Weight Paint", icon="WPAINT_HLT").mode = "WEIGHT_PAINT"
		pie_menu.operator(SetObjectMode.bl_idname, text="Object Mode", icon="OBJECT_DATAMODE").mode = "OBJECT"
		pie_menu.operator(SetObjectMode.bl_idname, text="Particle Edit", icon="PARTICLEMODE").mode = "PARTICLE_EDIT"
		pie_menu.operator(SetObjectMode.bl_idname, text="Edit Mode", icon="EDITMODE_HLT").mode = "EDIT"
		pie_menu.operator(SetObjectMode.bl_idname, text="Texture Paint", icon="TPAINT_HLT").mode = "TEXTURE_PAINT"
		pie_menu.operator(SetObjectMode.bl_idname, text="Vertex Paint", icon="VPAINT_HLT").mode = "VERTEX_PAINT"
class SetObjectMode(bpy.types.Operator): #
	bl_idname = "object.set_object_mode"
	bl_label = "Set Object Modes"
	bl_description = "Set interactive mode of object"
	bl_options = {'REGISTER'}

	mode : StringProperty(name="Interactive Mode", default="OBJECT")

	def execute(self, context):
		try:
			bpy.ops.object.mode_set(mode=self.mode)
		except TypeError:
			self.report(type={"ERROR"}, message="The selected mode cannot use for active object")
			return {'CANCELLED'}
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
		#Left - Right - Bottom - Top - TopLeft - TopRight - BottomLeft - BottomRight
		pie_menu = self.layout.menu_pie()
		#以下の関数は全て DATA_PT_modifiers で定義
		pie_menu.menu_pie().operator('object.add_subsurf', icon="MODIFIER")
		box = pie_menu.menu_pie().box().box().box()
		box.enabled = bpy.ops.object.set_viewport_subsurf_level.poll()
		box.operator_context = 'EXEC_DEFAULT'
		box.label(text="Set Number of Subdivisions in Viewport", icon="VIEW3D")
		row = box.row(align=True)
		for i in range(5):
			row.operator('object.set_viewport_subsurf_level', text=str(i+1)).level_enum = str(i+1)
		pie_menu.menu_pie().operator('object.set_subsurf_optimal_display', icon="MOD_WIREFRAME")
		pie_menu.menu_pie().operator('object.equalize_subsurf_level', icon="LIBRARY_DATA_DIRECT")
		pie_menu.menu_pie().operator('object.delete_subsurf', icon="CANCEL")
		box = pie_menu.menu_pie().box().box().box()
		box.enabled = bpy.ops.object.set_render_subsurf_level.poll()
		box.operator_context = 'EXEC_DEFAULT'
		box.label(text="Set Number of Subdivisions When Rendering", icon="RESTRICT_RENDER_OFF")
		row = box.row(align=True)
		for i in range(5):
			row.operator('object.set_render_subsurf_level', text=str(i+1)).level_enum= str(i+1)

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
		layout = self.layout.menu_pie()
		layout.enabled = (not context.active_object == None)
		ps = ['BOUNDS', 'WIRE', 'SOLID', 'TEXTURED']
		icons = ["SHADING_BBOX", "SHADING_WIRE", "SHADING_SOLID", "SHADING_TEXTURE"]
		act_obj = context.active_object
		for p, icon in zip(ps, icons):
			name = bpy.types.UILayout.enum_item_name(act_obj, 'display_type', p)
			layout.operator(SetDrawType.bl_idname, text=name, icon=icon).type = p
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
		bpy.ops.object.delete(use_global=self.use_global)
		return {'FINISHED'}

################
# サブメニュー #
################

class ShortcutMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_shortcut"
	bl_label = "Change Properties (For Shortcut)"
	bl_description = "Functions to change objects' properties that can be used easily by assigning shortcut"

	def draw(self, context):
		self.layout.operator(DeleteUnmassage.bl_idname, icon="PLUGIN")
		self.layout.operator('object.apply_modifiers_and_join', icon="PLUGIN")#DATA_PT_modifiers で定義
		self.layout.separator()
		self.layout.operator(CopyPieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(ObjectModePieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(SubdivisionSetPieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(DrawTypePieOperator.bl_idname, icon="PLUGIN")

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
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
