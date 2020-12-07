# 「ノードエディター」エリア > 「ノード」メニュー
# "Node Editor" Area > "Node" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class CopyAllMaterialNode(bpy.types.Operator):
	bl_idname = "node.copy_all_material_node"
	bl_label = "Copy to other material shader node"
	bl_description = "Copies of other material shader nodes are displayed"
	bl_options = {'REGISTER', 'UNDO'}

	isOnlySelected : BoolProperty(name="Selected Object Only", default=True)
	isOnlyUseNode : BoolProperty(name="Material Using Nodes Only", default=True)
	isReplace : BoolProperty(name="Replace Node Tree", default=False)

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (not context.object.active_material.use_nodes):
			return False
		if (context.space_data.tree_type != 'ShaderNodeTree'):
			return False
		return True
	def execute(self, context):
		activeObj = context.active_object
		activeMat = activeObj.active_material
		mats = []
		if (self.isOnlySelected):
			for obj in context.selected_objects:
				for mslot in obj.material_slots:
					if (mslot.material):
						if (activeMat.name != mslot.material.name):
							for mat in mats:
								if (mat.name == mslot.material.name):
									break
							else:
								mats.append(mslot.material)
		else:
			mats = bpy.data.materials
		if (self.isOnlyUseNode):
			matDummy = mats[:]
			mats = []
			for mat in matDummy:
				if (mat.use_nodes):
					mats.append(mat)
		bpy.ops.node.select_all(action='SELECT')
		bpy.ops.node.clipboard_copy()
		bpy.ops.mesh.primitive_cube_add()
		bpy.ops.object.material_slot_add()
		dummyObj = context.active_object
		for mat in mats:
			dummyObj.material_slots[0].material = mat
			dummyObj.active_material_index = 0
			mat.use_nodes = True
			if self.isReplace:
				mat.node_tree.nodes.clear()
			context.space_data.node_tree = mat.node_tree
			if not self.isReplace:
				frame = context.space_data.node_tree.nodes.new(type='NodeFrame')
				frame.label = mat.name
				bpy.ops.node.select_all(action='DESELECT')
				bpy.ops.node.clipboard_paste()
				for n in context.selected_nodes:
					n.parent = frame
			else:
				bpy.ops.node.clipboard_paste()
		bpy.ops.object.delete()
		activeObj.select_set(True)
		bpy.context.view_layer.objects.active = activeObj
		return {'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		for p in ['isOnlySelected', 'isOnlyUseNode', "isReplace"]:
			sp = self.layout.split(factor=0.2)
			sp.label(text="")
			sp.prop(self, p)

################
# クラスの登録 #
################

classes = [
	CopyAllMaterialNode
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
		self.layout.operator(CopyAllMaterialNode.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
