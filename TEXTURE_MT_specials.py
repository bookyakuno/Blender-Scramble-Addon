# 「プロパティ」エリア > 「テクスチャ」タブ > リスト右の▼
# "Propaties" Area > "Texture" Tab > List Right ▼

import bpy
from bpy.props import *

################
# オペレーター #
################

class RenameTextureFileName(bpy.types.Operator):
	bl_idname = "texture.rename_texture_file_name"
	bl_label = "Image File name to Texture Name"
	bl_description = "rename this image file's name to the name of source file"
	bl_options = {'REGISTER', 'UNDO'}

	isExt : BoolProperty(name="Include Extension", default=True)

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False
		return True
	def execute(self, context):
		mat = context.object.active_material
		active_slot_number = mat.paint_active_slot
		try:
			act_image = mat.texture_paint_images[active_slot_number]
		except IndexError:
			self.report(type={"ERROR"}, message="Image is not specified")
			return {"CANCELLED"}
		if (act_image.filepath_raw != ""):
			name = bpy.path.basename(act_image.filepath_raw)
			if (not self.isExt):
				name, ext = os.path.splitext(name)
			try:
				act_image.name = name
			except: pass
		return {'FINISHED'}

class RemoveAllTextureSlots(bpy.types.Operator):
	bl_idname = "texture.remove_all_texture_slots"
	bl_label = "Clear all texture slots"
	bl_description = "Empties all active material texture slots"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) == 0:
			return False
		return True
	def execute(self, context):
		mat = context.object.active_material
		image_names = [im.name for im in context.object.active_material.texture_paint_images]
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		for name in image_names:
			nod = tex_nodes_dic[name]
			try:
				linked_node = nod.outputs[0].links[0].to_node
				if linked_node.type in ["NORMAL_MAP", "BUMP", "ノーマルマップ", "バンプ"]:
					mat.node_tree.nodes.remove(linked_node)
			except IndexError:
				pass
			mat.node_tree.nodes.remove(nod)
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}

class RemoveTextureSlot(bpy.types.Operator):
	bl_idname = "texture.remove_texture_slot"
	bl_label = "Remove this texture slot"
	bl_description = "Remove this image from active material texture slots"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) == 0:
			return False
		return True
	def execute(self, context):
		mat = context.object.active_material
		active_slot_number = mat.paint_active_slot
		act_image_name = mat.texture_paint_images[active_slot_number].name
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		tex_node = tex_nodes_dic[act_image_name]
		try:
			linked_node = tex_node.outputs[0].links[0].to_node
			if linked_node.type in ["NORMAL_MAP", "BUMP", "ノーマルマップ", "バンプ"]:
				mat.node_tree.nodes.remove(linked_node)
		except IndexError:
			pass
		mat.node_tree.nodes.remove(tex_node)
		mat.paint_active_slot = active_slot_number
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}


class SlotMoveTop(bpy.types.Operator):
	bl_idname = "texture.slot_move_top"
	bl_label = "To Top"
	bl_description = "Move active texture slot at top"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) <= 1:
			return False
		if (context.object.active_material.paint_active_slot == 0):
			return False
		return True
	def execute(self, context):
		node_list = []
		top_info = None
		mat = context.object.active_material
		slot_num = mat.paint_active_slot
		image_names = [im.name for im in context.object.active_material.texture_paint_images]
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		for idx, name in enumerate(image_names):
			nod = tex_nodes_dic[name]
			try:
				linked_socket = nod.outputs[0].links[0].to_socket
			except IndexError:
				linked_socket = None
			if idx == slot_num:
				top_info = {"name":name, "location":nod.location, "socket":linked_socket}
			else:
				node_list.append({"name":name, "location":nod.location, "socket":linked_socket})
			mat.node_tree.nodes.remove(nod)
		for info in list([top_info] + node_list):
			node_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
			node_tex.location = [info["location"][0], info["location"][1]]
			node_tex.image = bpy.data.images[info["name"]]
			if info["socket"]:
				mat.node_tree.links.new(node_tex.outputs[0],info["socket"])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		mat.paint_active_slot = 0
		return {'FINISHED'}


class SlotMoveUp(bpy.types.Operator):
	bl_idname = "texture.slot_move_up"
	bl_label = "Move Up"
	bl_description = "Move up active texture slot"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) <= 1:
			return False
		if (context.object.active_material.paint_active_slot == 0):
			return False
		return True
	def execute(self, context):
		node_list = []
		mat = context.object.active_material
		slot_num = mat.paint_active_slot
		image_names = [im.name for im in context.object.active_material.texture_paint_images[slot_num-1:]]
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		for name in image_names:
			nod = tex_nodes_dic[name]
			try:
				linked_socket = nod.outputs[0].links[0].to_socket
			except IndexError:
				linked_socket = None
			node_list.append({"name":name, "location":nod.location, "socket":linked_socket})
			mat.node_tree.nodes.remove(nod)
		for info in list([node_list[1],node_list[0]] + node_list[2:]):
			node_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
			node_tex.location = [info["location"][0], info["location"][1]]
			node_tex.image = bpy.data.images[info["name"]]
			if info["socket"]:
				mat.node_tree.links.new(node_tex.outputs[0],info["socket"])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		mat.paint_active_slot = slot_num -1
		return {'FINISHED'}

class SlotMoveBottom(bpy.types.Operator):
	bl_idname = "texture.slot_move_bottom"
	bl_label = "To Bottom"
	bl_description = "Move active texture slot to bottom"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) <= 1:
			return False
		active_index = context.object.active_material.paint_active_slot
		if (len(context.object.active_material.texture_paint_images) == active_index+1):
			return False
		return True
	def execute(self, context):
		node_list = []
		bottom_info = None
		mat = context.object.active_material
		slot_num = mat.paint_active_slot
		image_names = [im.name for im in context.object.active_material.texture_paint_images]
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		for idx, name in enumerate(image_names):
			nod = tex_nodes_dic[name]
			try:
				linked_socket = nod.outputs[0].links[0].to_socket
			except IndexError:
				linked_socket = None
			if idx == slot_num:
				bottom_info = {"name":name, "location":nod.location, "socket":linked_socket}
			else:
				node_list.append({"name":name, "location":nod.location, "socket":linked_socket})
			mat.node_tree.nodes.remove(nod)
		for info in list(node_list + [bottom_info]):
			node_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
			node_tex.location = [info["location"][0], info["location"][1]]
			node_tex.image = bpy.data.images[info["name"]]
			if info["socket"]:
				mat.node_tree.links.new(node_tex.outputs[0],info["socket"])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		mat.paint_active_slot = len(image_names)-1
		return {'FINISHED'}		

class SlotMoveDown(bpy.types.Operator):
	bl_idname = "texture.slot_move_down"
	bl_label = "Move Down"
	bl_description = "Move down active texture slot"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) <= 1:
			return False
		active_index = context.object.active_material.paint_active_slot
		if (len(context.object.active_material.texture_paint_images) == active_index+1):
			return False
		return True
	def execute(self, context):
		node_list = []
		mat = context.object.active_material
		slot_num = mat.paint_active_slot
		image_names = [im.name for im in context.object.active_material.texture_paint_images[slot_num:]]
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		for name in image_names:
			nod = tex_nodes_dic[name]
			try:
				linked_socket = nod.outputs[0].links[0].to_socket
			except IndexError:
				linked_socket = None
			node_list.append({"name":name, "location":nod.location, "socket":linked_socket})
			mat.node_tree.nodes.remove(nod)
		for info in list([node_list[1],node_list[0]] + node_list[2:]):
			node_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
			node_tex.location = [info["location"][0], info["location"][1]]
			node_tex.image = bpy.data.images[info["name"]]
			if info["socket"]:
				mat.node_tree.links.new(node_tex.outputs[0],info["socket"])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		mat.paint_active_slot = slot_num +1
		return {'FINISHED'}


class RemoveUnlinkedSlots(bpy.types.Operator):
	bl_idname = "texture.remove_unlinkeed_slots"
	bl_label = "Remove Unlinked Texture slots"
	bl_description = "Removes all images that has no links with other shader."
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) <= 1:
			return False
		return True
	def execute(self, context):
		nolink_nodes = []
		mat = context.object.active_material
		image_names = [im.name for im in context.object.active_material.texture_paint_images]
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		for name in image_names:
			nod = tex_nodes_dic[name]
			try:
				linked_node = nod.outputs[0].links[0].to_node
				if linked_node.type in ["NORMAL_MAP", "BUMP", "ノーマルマップ", "バンプ"]:
					if len(linked_node.outputs[0].links) == 0:
						mat.node_tree.nodes.remove(linked_node)
						mat.node_tree.nodes.remove(nod)
			except IndexError:
				mat.node_tree.nodes.remove(nod)
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}

"""
class TruncateEmptySlots(bpy.types.Operator):
	bl_idname = "texture.truncate_empty_slots"
	bl_label = "Cut empty texture slots"
	bl_description = "No texture is assigned an empty texture slots will be filled, truncated"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.material):
			return False
		flag = 0
		for slot in context.material.texture_slots:
			if (slot and flag == 0):
				flag = 1
			elif (not slot and flag == 1):
				flag = 2
			elif (slot and flag == 2):
				return True
		return False
	def execute(self, context):
		empty_slot_count = 0
		for i, slot in enumerate(context.material.texture_slots[:]):
			if (slot):
				context.material.active_texture_index = i
				for j in range(empty_slot_count):
					bpy.ops.texture.slot_move(type='UP')
			else:
				empty_slot_count += 1
		return {'FINISHED'}
"""
class RemoveFollowingSlots(bpy.types.Operator):
	bl_idname = "texture.remove_following_slots"
	bl_label = "Delete Below Here"
	bl_description = "Remove all active texture slot below"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) <= 1:
			return False
		active_index = context.object.active_material.paint_active_slot
		if (len(context.object.active_material.texture_paint_images) == active_index+1):
			return False
		return True
	def execute(self, context):
		mat = context.object.active_material
		slot_num = mat.paint_active_slot
		image_names = [im.name for im in context.object.active_material.texture_paint_images[slot_num+1:]]
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		for name in image_names:
			nod = tex_nodes_dic[name]
			try:
				linked_node = nod.outputs[0].links[0].to_node
				if linked_node.type in ["NORMAL_MAP", "BUMP", "ノーマルマップ", "バンプ"]:
					mat.node_tree.nodes.remove(linked_node)
			except IndexError:
				pass
			mat.node_tree.nodes.remove(nod)
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}

class CopyPasteTextureSlot(bpy.types.Operator):
	bl_idname = "texture.texture_slot_copy_paste"
	bl_label = "Copy & Paste this texture slot"
	bl_description = "Copy & paste this texture slot to other material of this object"
	bl_property = "material_list"
	bl_options = {'REGISTER', 'UNDO'}

	def get_object_list_callback(self, context):
		items = ((slot.material.name, slot.material.name, "") for slot in context.object.material_slots)
		return items
	
	material_list : EnumProperty(name="Images", items=get_object_list_callback)
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (len(context.object.material_slots) <= 1):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) == 0:
			return False
		return True
	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		mat = context.object.active_material
		act_image_name = mat.texture_paint_images[mat.paint_active_slot].name
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		nod = tex_nodes_dic[act_image_name]
		try:
			linked_socket = nod.outputs[0].links[0].to_socket
			if linked_socket.node.type in ["NORMAL_MAP", "BUMP", "ノーマルマップ", "バンプ"]:
				try:
					more_socket = linked_socket.node.outputs[0].links[0].to_socket
				except IndexError:
					more_socket = None
			else:
				more_socket = None
		except IndexError:
			linked_socket = None
		node_info = {"name":act_image_name, "location":nod.location, "socket":linked_socket, "more":more_socket}
		if self.material_list == mat.name:
			self.report(type={"ERROR"}, message="Cannot copy&paste to the same material")
			return {"CANCELLED"}
		target_mat = context.object.material_slots[self.material_list].material
		node_tex = target_mat.node_tree.nodes.new('ShaderNodeTexImage')
		node_tex.location = node_info["location"]
		node_tex.image = bpy.data.images[node_info["name"]]
		if node_info["socket"]:
			if node_info["more"]:
				if node_info["socket"].node.type == "NORMAL_MAP":
					new_node = target_mat.node_tree.nodes.new('ShaderNodeNormalMap')
				elif node_info["socket"].node.type == "BUMP":
					new_node = target_mat.node_tree.nodes.new('ShaderNodeBump')
				new_node.location = node_info["socket"].node.location
				try:
					node_mat = target_mat.node_tree.nodes["プリンシプル BSDF"]
				except KeyError:
					node_mat = target_mat.node_tree.nodes["Principled BSDF"]
				target_mat.node_tree.links.new(node_tex.outputs[0], new_node.inputs[node_info["socket"].identifier])
				target_mat.node_tree.links.new(new_node.outputs[0], node_mat.inputs[node_info["more"].identifier])
			else:
				try:
					node_mat = target_mat.node_tree.nodes["プリンシプル BSDF"]
				except KeyError:
					node_mat = target_mat.node_tree.nodes["Principled BSDF"]
				target_mat.node_tree.links.new(node_tex.outputs[0], node_mat.inputs[node_info["socket"].identifier])
		context.object.active_material_index = context.object.material_slots.find(target_mat.name)
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}


################
# サブメニュー #
################

class SpecialMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_slots_projectpaint_specials"
	bl_label = "Special menu for texture slots"
	bl_description = "Special menu for texture slots"

	def draw(self, context):
			self.layout.operator(SlotMoveUp.bl_idname, icon="TRIA_UP")
			self.layout.operator(SlotMoveDown.bl_idname, icon="TRIA_DOWN")
			self.layout.separator()
			self.layout.operator(SlotMoveTop.bl_idname, icon="PLUGIN")
			self.layout.operator(SlotMoveBottom.bl_idname, icon="PLUGIN")
			#self.layout.operator(TruncateEmptySlots.bl_idname, icon="PLUGIN")
			self.layout.separator()
			self.layout.operator(CopyPasteTextureSlot.bl_idname, icon='COPYDOWN')			
			self.layout.separator()
			self.layout.operator(RemoveTextureSlot.bl_idname, icon='PANEL_CLOSE')
			self.layout.operator(RemoveFollowingSlots.bl_idname, icon='PLUGIN')
			self.layout.operator(RemoveAllTextureSlots.bl_idname, icon="CANCEL")
			self.layout.operator(RemoveUnlinkedSlots.bl_idname, icon='PLUGIN')
			self.layout.separator()
			self.layout.operator(RenameTextureFileName.bl_idname, icon="PLUGIN")
			self.layout.operator('texture.all_rename_texture_file_name', icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	RenameTextureFileName,
	RemoveAllTextureSlots,
	RemoveTextureSlot,
	SlotMoveTop,
	SlotMoveUp,
	SlotMoveBottom,
	SlotMoveDown,
	RemoveUnlinkedSlots,
	#TruncateEmptySlots,
	RemoveFollowingSlots,
	CopyPasteTextureSlot,
	SpecialMenu
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
		if (context.scene.tool_settings.image_paint.mode == 'MATERIAL'):
			self.layout.menu(SpecialMenu.bl_idname, text="  Texuture Slots Menu", icon='PLUGIN')#
			
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
