# 「プロパティ」エリア > 「アクティブツールとワークスペースの設定」タブ > 「テクスチャスロット」パネル
# "Propaties" Area > "Active Tool and Workspace Settings" Tab > "Texture Slots" Panel

import bpy
import os
from bpy.props import *
from bpy.ops import *
from bpy_extras.io_utils import ImportHelper

################
# オペレーター #
################

class ShowTextureImage(bpy.types.Operator):
	bl_idname = "texture.show_texture_image"
	bl_label = "Show Texture in Image Editor"
	bl_description = "Show the active slot's image in image editor"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if context.scene.tool_settings.image_paint.mode == 'MATERIAL':
			if len(context.object.active_material.texture_paint_images) == 0:
				return False
		return True

	def execute(self, context):
		mat = context.object.active_material
		if context.scene.tool_settings.image_paint.mode == 'MATERIAL':
			active_slot_number = mat.paint_active_slot
			act_image = mat.texture_paint_images[active_slot_number]
		elif context.scene.tool_settings.image_paint.mode == 'IMAGE':
			act_image = context.scene.tool_settings.image_paint.canvas
		for area in context.screen.areas:
			if (area.type == 'IMAGE_EDITOR'):
				area.spaces[0].image = act_image
				break
		else:
			bpy.ops.screen.userpref_show()
			new_window = context.window_manager.windows[-1]
			image_area = new_window.screen.areas[-1]
			image_area.type = 'IMAGE_EDITOR'
			image_area.spaces[0].image = act_image
			bpy.ops.image.view_zoom_ratio(ratio=0.5)
		return {'FINISHED'}

class AddExternalImage(bpy.types.Operator, ImportHelper):
	bl_idname = "texture.add_external_image"
	bl_label = "Use External Image File"
	bl_description = "Add an external image file as base color in texture paint slots"
	bl_options = {'REGISTER'}

	filter_glob : StringProperty( default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp', options={'HIDDEN'} )

	def execute(self, context):
		bpy.ops.image.open(filepath=self.filepath)
		filename = os.path.basename(self.filepath)
		mat = context.object.active_material
		mat.use_nodes = True
		texture_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
		for n in mat.node_tree.nodes:
			if n.type == 'BSDF_PRINCIPLED':
				bsdf_node = n
				break
		else:
			self.report(type={"ERROR"}, message="There exists no Principled BSDF shader")
			return {"CANCELLED"}
		if bsdf_node.inputs["Base Color"].is_linked:
			old_texture_node = bsdf_node.inputs["Base Color"].links[0].from_node
			texture_node.location = [old_texture_node.location[0]-20, old_texture_node.location[1]-20]
		else:
			texture_node.location = [texture_node.location[0]-300, texture_node.location[1]+300]
		texture_node.image = bpy.data.images[filename]
		mat.node_tree.links.new(texture_node.outputs[0], bsdf_node.inputs[0])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		mat.paint_active_slot = len(mat.texture_paint_images)-1
		return {'FINISHED'}

class StartTexturePaint(bpy.types.Operator):
	bl_idname = "texture.start_texture_paint"
	bl_label = "Add Image as Base Color"
	bl_description = "Add an image as base color in texture paint slots"
	bl_options = {'REGISTER'}

	image_counts : IntProperty(name="Number of images", default=0)
	image_name : StringProperty(name="Image to be used", default="")

	def __init__(self):
		self.image_counts = len(bpy.data.images)
		self.image_name = bpy.data.images[-1].name
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		return True
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		if len(bpy.data.images) > self.image_counts:
			self.image_name = bpy.data.images[-1].name
			self.image_counts = len(bpy.data.images)
		self.layout.prop_search(self, "image_name", bpy.data, "images",text="Select Image", text_ctxt="", translate=True, icon='IMAGE')
		self.layout.operator(AddExternalImage.bl_idname, icon='FILEBROWSER')

	def execute(self, context):
		mat = context.object.active_material
		mat.use_nodes = True
		texture_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
		for n in mat.node_tree.nodes:
			if n.type == 'BSDF_PRINCIPLED':
				bsdf_node = n
				break
		else:
			self.report(type={"ERROR"}, message="There exists no Principled BSDF shader")
			return {"CANCELLED"}
		if bsdf_node.inputs["Base Color"].is_linked:
			old_texture_node = bsdf_node.inputs["Base Color"].links[0].from_node
			texture_node.location = [old_texture_node.location[0]-20, old_texture_node.location[1]-20]
		else:
			texture_node.location = [texture_node.location[0]-300, texture_node.location[1]+300]
		texture_node.image = bpy.data.images[self.image_name]
		mat.node_tree.links.new(texture_node.outputs[0], bsdf_node.inputs[0])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		mat.paint_active_slot = len(mat.texture_paint_images)-1
		return {'FINISHED'}

################
# オペレーター (旧 TEXTURE_MT_special) #
_STORE_ITEMS = [] #保存用グローバル変数：EnumPropertyの動的なitems作成におけるバグへの対処用
################

class RenameTextureFileName(bpy.types.Operator):
	bl_idname = "texture.rename_texture_file_name"
	bl_label = "Match Texture Name to Image File Name"
	bl_description = "Change the name of active slot's texture to its linked image file's name"
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
	bl_label = "Remove All Texture Slots"
	bl_description = "Remove all texture slots"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
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
				if linked_node.type in ["NORMAL_MAP", "BUMP"]:
					mat.node_tree.nodes.remove(linked_node)
			except IndexError:
				pass
			mat.node_tree.nodes.remove(nod)
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}

class RemoveTextureSlot(bpy.types.Operator):
	bl_idname = "texture.remove_texture_slot"
	bl_label = "Remove Active Texture Slot"
	bl_description = "Remove active texture slot"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
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
			if linked_node.type in ["NORMAL_MAP", "BUMP"]:
				mat.node_tree.nodes.remove(linked_node)
		except IndexError:
			pass
		mat.node_tree.nodes.remove(tex_node)
		mat.paint_active_slot = active_slot_number
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}

class MoveActiveSlotMost(bpy.types.Operator):
	bl_idname = "texture.move_active_slot_most"
	bl_label = "Move Texture to Top / Bottom"
	bl_description = "Move active texture slot to top or bottom"
	bl_options = {'REGISTER', 'UNDO'}

	is_top : BoolProperty(name="Top", default=True)

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if len(context.object.active_material.texture_paint_images) <= 1:
			return False
		return True

	def execute(self, context):
		node_list = []
		top_info = None
		mat = context.object.active_material
		slot_num = mat.paint_active_slot
		if self.is_top:
			if (slot_num == 0):
				return {'CANCELLED'}
		else:
			if (len(mat.texture_paint_images) == slot_num+1):
				return {'CANCELLED'}
		image_names = [im.name for im in mat.texture_paint_images]
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		for idx, name in enumerate(image_names):
			nod = tex_nodes_dic[name]
			try:
				linked_socket = nod.outputs[0].links[0].to_socket
			except IndexError:
				linked_socket = None
			if idx == slot_num:
				target_info = {"name":name, "location":nod.location, "socket":linked_socket}
			else:
				node_list.append({"name":name, "location":nod.location, "socket":linked_socket})
			mat.node_tree.nodes.remove(nod)
		if self.is_top:
			new_order = list([target_info] + node_list)
		else:
			new_order = list(node_list + [target_info])
		for info in new_order:
			texture_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
			texture_node.location = [info["location"][0], info["location"][1]]
			texture_node.image = bpy.data.images[info["name"]]
			if info["socket"]:
				mat.node_tree.links.new(texture_node.outputs[0],info["socket"])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		if self.is_top:
			mat.paint_active_slot = 0
		else:
			mat.paint_active_slot = len(image_names)-1
		return {'FINISHED'}

class MoveActiveSlot(bpy.types.Operator):
	bl_idname = "texture.move_active_slot"
	bl_label = "Move Texture Slot"
	bl_description = "Move up or down active texture slot"
	bl_options = {'REGISTER', 'UNDO'}

	is_up : BoolProperty(name="Up", default=True)

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		return True

	def execute(self, context):
		node_list = []
		mat = context.object.active_material
		slot_num = mat.paint_active_slot
		if self.is_up:
			if (slot_num == 0):
				return {'CANCELLED'}
			image_names = [im.name for im in mat.texture_paint_images[slot_num-1:]]
		else:
			if (len(mat.texture_paint_images) == slot_num+1):
				return {'CANCELLED'}
			image_names = [im.name for im in mat.texture_paint_images[slot_num:]]
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
			texture_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
			texture_node.location = [info["location"][0], info["location"][1]]
			texture_node.image = bpy.data.images[info["name"]]
			if info["socket"]:
				mat.node_tree.links.new(texture_node.outputs[0],info["socket"])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		if self.is_up:
			mat.paint_active_slot = slot_num -1
		else:
			mat.paint_active_slot = slot_num +1
		return {'FINISHED'}

class RemoveUnlinkedSlots(bpy.types.Operator):
	bl_idname = "texture.remove_unlinkeed_slots"
	bl_label = "Remove Unused Texture Slots"
	bl_description = "Removes slots which  images have no links with other shader"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
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
				if linked_node.type in ["NORMAL_MAP", "BUMP"]:
					if len(linked_node.outputs[0].links) == 0:
						mat.node_tree.nodes.remove(linked_node)
						mat.node_tree.nodes.remove(nod)
			except IndexError:
				mat.node_tree.nodes.remove(nod)
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}

class RemoveFollowingSlots(bpy.types.Operator):
	bl_idname = "texture.remove_following_slots"
	bl_label = "Remove Slots Below Active"
	bl_description = "Remove all texture slots below active one"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if len(context.object.active_material.texture_paint_images) <= 1:
			return False
		return True

	def execute(self, context):
		mat = context.object.active_material
		slot_num = mat.paint_active_slot
		if len(mat.texture_paint_images) == slot_num+1:
			return {'CANCELLED'}
		image_names = [im.name for im in context.object.active_material.texture_paint_images[slot_num+1:]]
		tex_nodes_dic = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
		for name in image_names:
			nod = tex_nodes_dic[name]
			try:
				linked_node = nod.outputs[0].links[0].to_node
				if linked_node.type in ["NORMAL_MAP", "BUMP"]:
					mat.node_tree.nodes.remove(linked_node)
			except IndexError:
				pass
			mat.node_tree.nodes.remove(nod)
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}

class CopyPasteTextureSlot(bpy.types.Operator):
	bl_idname = "texture.texture_slot_copy_paste"
	bl_label = "Copy Active Slot to Other Material"
	bl_description = "Copy active slot's image to active object's other material"
	bl_property = "selected_mat"
	bl_options = {'REGISTER', 'UNDO'}

	def item_callback(self, context):
		_STORE_ITEMS.clear()
		names = [slot.material.name for slot in context.object.material_slots]
		for idx, name in enumerate(names):
			_STORE_ITEMS.append((str(idx), name, "", idx))
		#print(_STORE_ITEMS[0])#作成したリストの要素がうまく認識されないバグ?への一応の対処
		return _STORE_ITEMS

	selected_mat : EnumProperty(name="Material", items=item_callback)

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (len(context.object.material_slots) <= 1):
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
			if linked_socket.node.type in ["NORMAL_MAP", "BUMP"]:
				try:
					more_socket = linked_socket.node.outputs[0].links[0].to_socket
				except IndexError:
					more_socket = None
			else:
				more_socket = None
		except IndexError:
			linked_socket = None
			more_socket = None
		node_info = {"name":act_image_name, "location":nod.location, "socket":linked_socket, "more":more_socket}
		target_mat = context.object.material_slots[int(self.selected_mat)].material
		if target_mat == mat:
			self.report(type={"ERROR"}, message="Cannot copy to the same material")
			return {"CANCELLED"}
		texture_node = target_mat.node_tree.nodes.new('ShaderNodeTexImage')
		texture_node.location = node_info["location"]
		texture_node.image = bpy.data.images[node_info["name"]]
		if node_info["socket"]:
			if node_info["more"]:
				if node_info["socket"].node.type == "NORMAL_MAP":
					new_node = target_mat.node_tree.nodes.new('ShaderNodeNormalMap')
				elif node_info["socket"].node.type == "BUMP":
					new_node = target_mat.node_tree.nodes.new('ShaderNodeBump')
				new_node.location = node_info["socket"].node.location
				for n in target_mat.node_tree.nodes:
					if n.type == 'BSDF_PRINCIPLED':
						bsdf_node = n
						break
				else:
					self.report(type={"ERROR"}, message="There exists no Principled BSDF shader")
					return {"CANCELLED"}
				target_mat.node_tree.links.new(texture_node.outputs[0], new_node.inputs[node_info["socket"].identifier])
				target_mat.node_tree.links.new(new_node.outputs[0], bsdf_node.inputs[node_info["more"].identifier])
			else:
				for n in target_mat.node_tree.nodes:
					if n.type == 'BSDF_PRINCIPLED':
						bsdf_node = n
						break
				else:
					self.report(type={"ERROR"}, message="There exists no Principled BSDF shader")
					return {"CANCELLED"}
				target_mat.node_tree.links.new(texture_node.outputs[0], bsdf_node.inputs[node_info["socket"].identifier])
		context.object.active_material_index = context.object.material_slots.find(target_mat.name)
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}

################
# サブメニュー #
################

class SpecialMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_slots_projectpaint_specials"
	bl_label = "Manipulate Texture Slots"
	bl_description = "Functions to manipulate texture slots"

	def draw(self, context):
			self.layout.operator(CopyPasteTextureSlot.bl_idname, icon='COPYDOWN')
			self.layout.separator()
			self.layout.operator(RemoveFollowingSlots.bl_idname, icon='PLUGIN')
			self.layout.operator(RemoveAllTextureSlots.bl_idname, icon="CANCEL")
			self.layout.operator(RemoveUnlinkedSlots.bl_idname, icon='PLUGIN')
			self.layout.separator()
			self.layout.operator(RenameTextureFileName.bl_idname, icon="PLUGIN")
			self.layout.operator('texture.all_rename_texture_file_name', icon='PLUGIN')# INFO_MT_file.py で定義

################
# クラスの登録 #
################

classes = [
	ShowTextureImage,
	AddExternalImage,
	StartTexturePaint,
	RenameTextureFileName,
	RemoveAllTextureSlots,
	RemoveTextureSlot,
	MoveActiveSlotMost,
	MoveActiveSlot,
	RemoveUnlinkedSlots,
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
			sp = self.layout.split(factor=0.55)
			sp.use_property_split = False
			row = sp.row()
			row_item = row.row(align=True)
			row_item.operator(MoveActiveSlot.bl_idname, icon="TRIA_UP", text="").is_up = True
			row_item.operator(MoveActiveSlot.bl_idname, icon="TRIA_DOWN", text="").is_up = False
			row_item = row.row(align=True)
			row_item.operator(MoveActiveSlotMost.bl_idname, icon="TRIA_UP_BAR", text="").is_top = True
			row_item.operator(MoveActiveSlotMost.bl_idname, icon="TRIA_DOWN_BAR", text="").is_top = False
			row_item = row.row(align=True)
			row_item.operator(RemoveTextureSlot.bl_idname, icon='REMOVE', text="")
			row_item.operator(StartTexturePaint.bl_idname, icon='OUTLINER_OB_IMAGE', text="Add")
			sp.operator(ShowTextureImage.bl_idname, icon='IMAGE', text="Show in Image Editor")
			sp = self.layout.split(factor=0.6)
			sp.use_property_split = False
			sp.menu(SpecialMenu.bl_idname, icon='PLUGIN')
			# 以下は旧 TEXTURE_PT_mappting の機能(に相当するもの)
			sp.prop_search(context.object.data.uv_layers, "active", context.object.data, "uv_layers",text="UV", icon='PLUGIN')
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			sp = self.layout.split(factor=0.55)
			sp.operator(StartTexturePaint.bl_idname, icon='OUTLINER_OB_IMAGE')
			sp.operator(ShowTextureImage.bl_idname, icon='IMAGE', text="Show in Image Editor")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
