# 「プロパティ」エリア > 「テクスチャ」タブ > 「画像」パネル
# "Propaties" Area > "Texture" Tab > "Image" Panel

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
	bl_label = "Texture images show in image editor"
	bl_description = "Image is used in active texture shows image editor"
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
		for area in context.screen.areas:
			if (area.type == 'IMAGE_EDITOR'):
				return True
		return False
	def execute(self, context):
		mat = context.object.active_material
		if context.scene.tool_settings.image_paint.mode == 'MATERIAL':
			active_slot_number = mat.paint_active_slot
			act_image = mat.texture_paint_images[active_slot_number]
		elif context.scene.tool_settings.image_paint.mode == 'IMAGE':
			act_image = context.scene.tool_settings.image_paint.canvas
		for area in context.screen.areas:
			if (area.type == 'IMAGE_EDITOR'):
				for space in area.spaces:
					if (space.type == 'IMAGE_EDITOR'):
						space.image = act_image
		return {'FINISHED'}

class AddExternalImage(bpy.types.Operator, ImportHelper):
	bl_idname = "texture.add_external_image"
	bl_label = "Add External Image"
	bl_description = "Add an external image file for texture paint"
	bl_options = {'REGISTER'}

	filter_glob : StringProperty( default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp', options={'HIDDEN'} )

	def execute(self, context):
		bpy.ops.image.open(filepath=self.filepath)
		filename = os.path.basename(self.filepath)
		mat = context.object.active_material
		mat.use_nodes = True
		node_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
		try:
			node_mat = mat.node_tree.nodes['プリンシプル BSDF']
		except KeyError:
			node_mat = mat.node_tree.nodes['Principled BSDF']
		if node_mat.inputs["Base Color"].is_linked:
			old_node_tex = node_mat.inputs["Base Color"].links[0].from_node
			node_tex.location = [old_node_tex.location[0]-20, old_node_tex.location[1]-20]
		else:
			node_tex.location = [node_tex.location[0]-300, node_tex.location[1]+300]
		node_tex.image = bpy.data.images[filename]		
		mat.node_tree.links.new(node_tex.outputs[0], node_mat.inputs[0])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}


class StartTexturePaint(bpy.types.Operator):
	bl_idname = "texture.start_texture_paint"
	bl_label = "Add an image as base-color for texture paint"
	bl_description = "Add an image as base-color in texture paint slots"
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
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False
		return True
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		if len(bpy.data.images) > self.image_counts:
			self.image_name = bpy.data.images[-1].name
			self.image_counts = len(bpy.data.images)
		self.layout.prop_search(self, "image_name", bpy.data, "images",text="Select image", text_ctxt="", translate=True, icon='IMAGE')
		row = self.layout.row(align=True)
		row.operator('image.new', icon='ADD')
		row.operator(AddExternalImage.bl_idname, icon='FILEBROWSER')

	def execute(self, context):	
		mat = context.object.active_material
		mat.use_nodes = True
		node_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
		try:
			node_mat = mat.node_tree.nodes['プリンシプルBSDF']
		except KeyError:
			node_mat = mat.node_tree.nodes['Principled BSDF']
		if node_mat.inputs["Base Color"].is_linked:
			old_node_tex = node_mat.inputs["Base Color"].links[0].from_node
			node_tex.location = [old_node_tex.location[0]-20, old_node_tex.location[1]-20]
		else:
			node_tex.location = [node_tex.location[0]-300, node_tex.location[1]+300]
		node_tex.image = bpy.data.images[self.image_name]
		mat.node_tree.links.new(node_tex.outputs[0], node_mat.inputs[0])
		context.scene.tool_settings.image_paint.mode = 'MATERIAL'
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	ShowTextureImage,
	AddExternalImage,
	StartTexturePaint
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
		row = self.layout.row(align=True)
		row.operator(ShowTextureImage.bl_idname, icon='IMAGE', text="Show image UV/Image editor")
		row.operator(StartTexturePaint.bl_idname, icon='OUTLINER_OB_IMAGE')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
