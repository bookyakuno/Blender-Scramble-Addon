# アドオンを読み込む時に最初にこのファイルが読み込まれます
'''
Original Author ： Saidenka
Update Blender2.8x, Current Support ： Bookyakuno, nikogoli
'''

import os, csv, codecs
from bpy.props import *

# アドオン情報
bl_info = {
	"name" : "Scramble Addon",
	"author" : "Saidenka, Bookyakuno, nikogoli",
	"version" : (1, 0, 8),
	"blender" : (2, 90, 0),
	"location" : "End of a varied menu",
	"description" : "Assortment of extended functions of saidenka\'s production",
	"warning" : "",
	"wiki_url" : "https://github.com/bookyakuno/Blender-Scramble-Addon",
	"tracker_url" : "https://github.com/bookyakuno/Blender-Scramble-Addon/issues",
	"category" : "Custom"
}

# サブスクリプト群をインポート
if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"BONE_PT_context_bone",
	"BONE_PT_display",
	"BONE_PT_inverse_kinematics",
	"BONE_PT_transform",
	"DATA_PT_bone_groups",
	"DATA_PT_geometry_curve",
	"DATA_PT_modifiers",
	"DATA_PT_pose_library",
	"DATA_PT_shape_keys",
	"DATA_PT_skeleton",
	"DATA_PT_uv_texture",
	"DATA_PT_vertex_colors",
	"DOPESHEET_MT_key",
	"IMAGE_MT_image",
	"IMAGE_MT_select",
	"IMAGE_MT_uvs",
	"IMAGE_MT_view",
	"INFO_HT_header",
	"INFO_MT_file",
	"INFO_MT_file_external_data",
	"INFO_MT_help",
	"INFO_MT_mesh_add",
	"INFO_MT_render",
	"INFO_MT_window",
	"MATERIAL_MT_specials",
	"MATERIAL_PT_context_material",
	"MESH_MT_shape_key_specials",
	"MESH_MT_vertex_group_specials",
	"DATA_PT_vertex_groups",
	"NODE_MT_node",
	"NODE_MT_view",
	"OBJECT_PT_context_object",
	"OBJECT_PT_display",
	"OBJECT_PT_transform",
	"PHYSICS_PT_rigid_body",
	"PHYSICS_PT_rigid_body_constraint",
	"PROPERTIES_HT_header",
	"RENDER_PT_bake",
	"RENDER_PT_render",
	"SCENE_PT_rigid_body_world",
	"TEXTURE_MT_specials",
	"TEXTURE_PT_context_texture",
	"TEXTURE_PT_image",
	"TEXTURE_PT_mapping",
	"TEXT_MT_text",
	"USERPREF_HT_header",
	"USERPREF_PT_file",
	"VIEW3D_MT_armature_specials",
	"VIEW3D_MT_bone_options_toggle",
	"VIEW3D_MT_edit_armature",
	"VIEW3D_MT_edit_mesh",
	"VIEW3D_MT_edit_mesh_delete",
	"VIEW3D_MT_edit_mesh_showhide",
	"VIEW3D_MT_edit_mesh_specials",
	"VIEW3D_MT_edit_mesh_vertices",
	"VIEW3D_MT_make_links",
	"VIEW3D_MT_object",
	"VIEW3D_MT_object_apply",
	"VIEW3D_MT_object_showhide",
	"VIEW3D_MT_object_specials",
	"VIEW3D_MT_paint_weight",
	"VIEW3D_MT_pose_constraints",
	"VIEW3D_MT_pose_showhide",
	"VIEW3D_MT_pose_specials",
	"VIEW3D_MT_select_edit_armature",
	"VIEW3D_MT_select_edit_mesh",
	"VIEW3D_MT_select_object",
	"VIEW3D_MT_select_pose",
	"VIEW3D_MT_snap",
	"VIEW3D_MT_uv_map",
	"VIEW3D_MT_view",
	"VIEW3D_MT_view_align",
	"VIEW3D_MT_view_align_selected",
	"VIEW3D_PT_addon_sidebar",
	"VIEW3D_PT_imapaint_tools_missing",
	"VIEW3D_PT_layers",
	"VIEW3D_PT_slots_projectpaint",
	"VIEW3D_PT_tools_imagepaint_external",
	"VIEW3D_PT_transform_orientations",
	"VIEW3D_PT_view3d_cursor",
	"VIEW3D_PT_view3d_name",
	"VIEW3D_PT_view3d_properties",
	"undisplay_commands",
	"DATA_PT_shape_curve",
	"BONE_PT_constraints",
	"PHYSICS_PT_dynamic_paint",
	"PHYSICS_PT_field",
	"PHYSICS_PT_softbody",
	"PHYSICS_PT_cloth",
	"BONE_PT_transform_locks",
	"BONE_PT_relations",
	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])
else:
	from . import (
	BONE_PT_context_bone,
	BONE_PT_display,
	BONE_PT_inverse_kinematics,
	BONE_PT_transform,
	DATA_PT_bone_groups,
	DATA_PT_geometry_curve,
	DATA_PT_modifiers,
	DATA_PT_pose_library,
	DATA_PT_shape_keys,
	DATA_PT_skeleton,
	DATA_PT_uv_texture,
	DATA_PT_vertex_colors,
	DOPESHEET_MT_key,
	IMAGE_MT_image,
	IMAGE_MT_select,
	IMAGE_MT_uvs,
	IMAGE_MT_view,
	INFO_HT_header,
	INFO_MT_file,
	INFO_MT_file_external_data,
	INFO_MT_help,
	INFO_MT_mesh_add,
	INFO_MT_render,
	INFO_MT_window,
	MATERIAL_MT_specials,
	MATERIAL_PT_context_material,
	MESH_MT_shape_key_specials,
	MESH_MT_vertex_group_specials,
	DATA_PT_vertex_groups,
	NODE_MT_node,
	NODE_MT_view,
	OBJECT_PT_context_object,
	OBJECT_PT_display,
	OBJECT_PT_transform,
	PHYSICS_PT_rigid_body,
	PHYSICS_PT_rigid_body_constraint,
	PROPERTIES_HT_header,
	RENDER_PT_bake,
	RENDER_PT_render,
	SCENE_PT_rigid_body_world,
	TEXTURE_MT_specials,
	TEXTURE_PT_context_texture,
	TEXTURE_PT_image,
	TEXTURE_PT_mapping,
	TEXT_MT_text,
	USERPREF_HT_header,
	USERPREF_PT_file,
	VIEW3D_MT_armature_specials,
	VIEW3D_MT_bone_options_toggle,
	VIEW3D_MT_edit_armature,
	VIEW3D_MT_edit_mesh,
	VIEW3D_MT_edit_mesh_delete,
	VIEW3D_MT_edit_mesh_showhide,
	VIEW3D_MT_edit_mesh_specials,
	VIEW3D_MT_edit_mesh_vertices,
	VIEW3D_MT_make_links,
	VIEW3D_MT_object,
	VIEW3D_MT_object_apply,
	VIEW3D_MT_object_showhide,
	VIEW3D_MT_object_specials,
	VIEW3D_MT_paint_weight,
	VIEW3D_MT_pose_constraints,
	VIEW3D_MT_pose_showhide,
	VIEW3D_MT_pose_specials,
	VIEW3D_MT_select_edit_armature,
	VIEW3D_MT_select_edit_mesh,
	VIEW3D_MT_select_object,
	VIEW3D_MT_select_pose,
	VIEW3D_MT_snap,
	VIEW3D_MT_uv_map,
	VIEW3D_MT_view,
	VIEW3D_MT_view_align,
	VIEW3D_MT_view_align_selected,
	VIEW3D_PT_addon_sidebar,
	VIEW3D_PT_imapaint_tools_missing,
	VIEW3D_PT_layers,
	VIEW3D_PT_slots_projectpaint,
	VIEW3D_PT_tools_imagepaint_external,
	VIEW3D_PT_transform_orientations,
	VIEW3D_PT_view3d_cursor,
	VIEW3D_PT_view3d_name,
	VIEW3D_PT_view3d_properties,
	undisplay_commands,
	DATA_PT_shape_curve,
	BONE_PT_constraints,
	PHYSICS_PT_dynamic_paint,
	PHYSICS_PT_field,
	PHYSICS_PT_softbody,
	PHYSICS_PT_cloth,
	BONE_PT_transform_locks,
	BONE_PT_relations,
	)
	#from . import ***

import bpy

# アドオン設定
class AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	tab_addon_menu            : EnumProperty(name="Tab", description="", items=[
	('DISPLAY', "Display", ""),
	 # ('KEYMAP', "Keymap", ""),
	('EXTERNAL_APP', "External app", ""),
	('LINK', "Link", "")
	], default='DISPLAY')

	disabled_menu : StringProperty(name="Invalid Menu", default="")
	use_disabled_menu : BoolProperty(name="Enable 'On/Off additional items' Button", default=False)
	view_savedata : StringProperty(name="View Save Data", default="")
	key_config_xml_path : StringProperty(name="XML Config Path", default="BlenderKeyConfig.xml")

	image_editor_path_1 : StringProperty(name="Path of Image Edit Software 1", default="", subtype='FILE_PATH')
	image_editor_path_2 : StringProperty(name="Path of Image Edit Software 2", default="", subtype='FILE_PATH')
	image_editor_path_3 : StringProperty(name="Path of Image Edit Software 3", default="", subtype='FILE_PATH')

	text_editor_path_1 : StringProperty(name="Path Text Edit Software 1", default="", subtype='FILE_PATH')
	text_editor_path_2 : StringProperty(name="Path Text Edit Software 2", default="", subtype='FILE_PATH')
	text_editor_path_3 : StringProperty(name="Path Text Edit Software 3", default="", subtype='FILE_PATH')

	def draw(self, context):
		layout = self.layout

		row = layout.row(align=True)
		row.prop(self,"tab_addon_menu",expand=True)

		if self.tab_addon_menu == "DISPLAY":
			box = layout.box()
			box.prop(self, 'use_disabled_menu')
			box.prop(self, 'disabled_menu')
			box = layout.box()
			box.prop(self, 'view_savedata')
			box = layout.box()
			box.prop(self, 'key_config_xml_path')


		elif self.tab_addon_menu == "EXTERNAL_APP":
			box = layout.box()
			box.label(text="Image Editor",icon="IMAGE")
			box.prop(self, 'image_editor_path_1')
			box.prop(self, 'image_editor_path_2')
			box.prop(self, 'image_editor_path_3')
			box = layout.box()
			box.label(text="Eext Editoer",icon="TEXT")
			box.prop(self, 'text_editor_path_1')
			box.prop(self, 'text_editor_path_2')
			box.prop(self, 'text_editor_path_3')


		elif self.tab_addon_menu == "LINK":
			box = layout.box()
			box.operator(
				"wm.url_open", text="Github", icon="URL"
			).url = "https://github.com/bookyakuno/Blender-Scramble-Addon"



# 追加メニューの有効/無効
class ToggleMenuEnable(bpy.types.Operator):
	bl_idname = "wm.toggle_menu_enable"
	bl_label = "On/Off Additional Items"
	bl_description = "Extra menu of ScrambleAddon toggle Enable/Disable"
	bl_options = {'REGISTER', 'UNDO'}

	id : StringProperty()

	def execute(self, context):
		recovery = ""
		is_on = False
		for id in context.preferences.addons[__name__.partition('.')[0]].preferences.disabled_menu.split(','):
			if (id == ""):
				continue
			if (id == self.id):
				is_on = True
			else:
				recovery = recovery + id + ","
		if (not is_on):
			recovery = recovery + self.id + ","
		if (recovery != ""):
			if (recovery[-1] == ","):
				recovery = recovery[:-1]
		context.preferences.addons[__name__.partition('.')[0]].preferences.disabled_menu = recovery
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}


# 翻訳辞書の取得
def GetTranslationDict():
	dict = {}
	path = os.path.join(os.path.dirname(__file__), "TranslationDictionary.csv")
	with codecs.open(path, 'r', 'utf-8') as f:
		reader = csv.reader(f)
		dict['ja_JP'] = {}
		for row in reader:
			if row:
				for context in bpy.app.translations.contexts:
					dict['ja_JP'][(context, row[1].replace('\\n', '\n'))] = row[0].replace('\\n', '\n')

	return dict


classes = [
	ToggleMenuEnable,
	AddonPreferences,
]

# プラグインをインストールしたときの処理
def register():

	for cls in classes:
	    bpy.utils.register_class(cls)

	bpy.app.translations.unregister(__name__)
	translation_dict = GetTranslationDict()
	bpy.app.translations.register(__name__, translation_dict)

	#　register_module(__name__)の廃止に伴い、サブモジュールのクラスも
	#　bpy.utils.register_class(cls)を使って登録することが必要
	BONE_PT_context_bone.register()
	bpy.types.BONE_PT_context_bone.append(BONE_PT_context_bone.menu)
	#BONE_PT_display.register()#クラスなしのためregister()は未定義
	bpy.types.BONE_PT_display.append(BONE_PT_display.menu)
	BONE_PT_inverse_kinematics.register()
	bpy.types.BONE_PT_inverse_kinematics.append(BONE_PT_inverse_kinematics.menu)
	BONE_PT_transform.register()
	bpy.types.BONE_PT_transform.append(BONE_PT_transform.menu)
	DATA_PT_bone_groups.register()
	bpy.types.DATA_PT_bone_groups.append(DATA_PT_bone_groups.menu)
	DATA_PT_geometry_curve.register()
	bpy.types.DATA_PT_geometry_curve.append(DATA_PT_geometry_curve.menu)
	DATA_PT_modifiers.register()
	bpy.types.DATA_PT_modifiers.append(DATA_PT_modifiers.menu)
	DATA_PT_pose_library.register()
	bpy.types.DATA_PT_pose_library.append(DATA_PT_pose_library.menu)
	DATA_PT_shape_keys.register()
	bpy.types.DATA_PT_shape_keys.prepend(DATA_PT_shape_keys.menu_prepend)
	DATA_PT_skeleton.register()
	bpy.types.DATA_PT_skeleton.append(DATA_PT_skeleton.menu)
	DATA_PT_uv_texture.register()
	bpy.types.DATA_PT_uv_texture.append(DATA_PT_uv_texture.menu)
	DATA_PT_vertex_colors.register()
	bpy.types.DATA_PT_vertex_colors.append(DATA_PT_vertex_colors.menu)
	DATA_PT_vertex_groups.register()
	bpy.types.DATA_PT_vertex_groups.append(DATA_PT_vertex_groups.menu)
	DOPESHEET_MT_key.register()
	bpy.types.DOPESHEET_MT_key.append(DOPESHEET_MT_key.menu)
	IMAGE_MT_image.register()
	bpy.types.IMAGE_MT_image.append(IMAGE_MT_image.menu)
	IMAGE_MT_select.register()
	bpy.types.IMAGE_MT_select.append(IMAGE_MT_select.menu)
	IMAGE_MT_uvs.register()
	bpy.types.IMAGE_MT_uvs.append(IMAGE_MT_uvs.menu)
	IMAGE_MT_view.register()
	bpy.types.IMAGE_MT_view.append(IMAGE_MT_view.menu)
	#INFO_HT_header.register()#クラスなしのためregister()は未定義
	bpy.types.INFO_HT_header.prepend(INFO_HT_header.menu_prepend)
	INFO_MT_file.register()
	bpy.types.TOPBAR_MT_file.append(INFO_MT_file.menu)
	INFO_MT_file_external_data.register()
	bpy.types.TOPBAR_MT_file_external_data.append(INFO_MT_file_external_data.menu)
	#INFO_MT_help.register()#クラスなしのためregister()は未定義
	bpy.types.TOPBAR_MT_help.append(INFO_MT_help.menu)
	INFO_MT_mesh_add.register()
	bpy.types.VIEW3D_MT_mesh_add.append(INFO_MT_mesh_add.menu)
	INFO_MT_render.register()
	bpy.types.TOPBAR_MT_render.append(INFO_MT_render.menu)
	INFO_MT_window.register()
	bpy.types.TOPBAR_MT_window.append(INFO_MT_window.menu)
	MATERIAL_MT_specials.register()
	bpy.types.MATERIAL_MT_context_menu.append(MATERIAL_MT_specials.menu)
	#MATERIAL_PT_context_material.register()#クラスなしのためregister()は未定義
	#bpy.types.MATERIAL_PT_context_material.append(MATERIAL_PT_context_material.menu)
	MESH_MT_shape_key_specials.register()
	bpy.types.MESH_MT_shape_key_context_menu.append(MESH_MT_shape_key_specials.menu)
	MESH_MT_vertex_group_specials.register()
	bpy.types.MESH_MT_vertex_group_context_menu.append(MESH_MT_vertex_group_specials.menu)
	NODE_MT_node.register()
	bpy.types.NODE_MT_node.append(NODE_MT_node.menu)
	NODE_MT_view.register()
	bpy.types.NODE_MT_view.append(NODE_MT_view.menu)
	OBJECT_PT_context_object.register()
	bpy.types.OBJECT_PT_context_object.append(OBJECT_PT_context_object.menu)
	OBJECT_PT_display.register()
	bpy.types.OBJECT_PT_display.append(OBJECT_PT_display.menu)
	#OBJECT_PT_transform.register()#クラスなしのためregister()は未定義
	bpy.types.OBJECT_PT_transform.append(OBJECT_PT_transform.menu)
	PHYSICS_PT_rigid_body.register()
	bpy.types.PHYSICS_PT_rigid_body.append(PHYSICS_PT_rigid_body.menu)
	PHYSICS_PT_rigid_body_constraint.register()
	bpy.types.PHYSICS_PT_rigid_body_constraint.append(PHYSICS_PT_rigid_body_constraint.menu)
	PROPERTIES_HT_header.register()
	bpy.types.PROPERTIES_HT_header.append(PROPERTIES_HT_header.menu)
	RENDER_PT_bake.register()
	bpy.types.CYCLES_RENDER_PT_bake.append(RENDER_PT_bake.menu)
	RENDER_PT_render.register()
	bpy.types.RENDER_PT_context.append(RENDER_PT_render.menu)
	SCENE_PT_rigid_body_world.register()
	bpy.types.SCENE_PT_rigid_body_world.append(SCENE_PT_rigid_body_world.menu)
	#TEXTURE_MT_specials.register()#TEXTURE_PT_image に統合
	#bpy.types.VIEW3D_PT_slots_projectpaint.append(TEXTURE_MT_specials.menu)
	#TEXTURE_PT_context_texture.register()#クラスなしのためregister()は未定義
	#bpy.types.TEXTURE_PT_context_texture.append(TEXTURE_PT_context_texture.menu)
	TEXTURE_PT_image.register()
	bpy.types.VIEW3D_PT_slots_projectpaint.append(TEXTURE_PT_image.menu)
	#TEXTURE_PT_mapping.register()#TEXTURE_PT_image に統合
	#bpy.types.VIEW3D_PT_slots_projectpaint.append(TEXTURE_PT_mapping.menu)
	TEXT_MT_text.register()
	bpy.types.TEXT_MT_text.append(TEXT_MT_text.menu)
	USERPREF_HT_header.register()
	bpy.types.USERPREF_PT_navigation_bar.append(USERPREF_HT_header.menu)
	USERPREF_PT_file.register()
	bpy.types.USERPREF_PT_file_paths_applications.append(USERPREF_PT_file.menu)
	VIEW3D_MT_armature_specials.register()
	bpy.types.VIEW3D_MT_armature_context_menu.append(VIEW3D_MT_armature_specials.menu)
	VIEW3D_MT_bone_options_toggle.register()
	bpy.types.VIEW3D_MT_bone_options_toggle.append(VIEW3D_MT_bone_options_toggle.menu)
	VIEW3D_MT_edit_armature.register()
	bpy.types.VIEW3D_MT_edit_armature.append(VIEW3D_MT_edit_armature.menu)
	VIEW3D_MT_edit_mesh.register()
	bpy.types.VIEW3D_MT_edit_mesh.append(VIEW3D_MT_edit_mesh.menu)
	VIEW3D_MT_edit_mesh_delete.register()
	bpy.types.VIEW3D_MT_edit_mesh_delete.append(VIEW3D_MT_edit_mesh_delete.menu)
	VIEW3D_MT_edit_mesh_showhide.register()
	bpy.types.VIEW3D_MT_edit_mesh_showhide.append(VIEW3D_MT_edit_mesh_showhide.menu)
	VIEW3D_MT_edit_mesh_specials.register()
	bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(VIEW3D_MT_edit_mesh_specials.menu)
	VIEW3D_MT_edit_mesh_vertices.register()
	bpy.types.VIEW3D_MT_edit_mesh_vertices.append(VIEW3D_MT_edit_mesh_vertices.menu)
	VIEW3D_MT_make_links.register()
	bpy.types.VIEW3D_MT_make_links.append(VIEW3D_MT_make_links.menu)
	VIEW3D_MT_object.register()
	bpy.types.VIEW3D_MT_object.append(VIEW3D_MT_object.menu)
	#VIEW3D_MT_object_apply.register() #廃止
	#bpy.types.VIEW3D_MT_object_apply.append(VIEW3D_MT_object_apply.menu)
	VIEW3D_MT_object_showhide.register()
	bpy.types.VIEW3D_MT_object_showhide.append(VIEW3D_MT_object_showhide.menu)
	VIEW3D_MT_object_specials.register()
	bpy.types.VIEW3D_MT_object_context_menu.append(VIEW3D_MT_object_specials.menu)
	VIEW3D_MT_paint_weight.register()
	bpy.types.VIEW3D_MT_paint_weight.append(VIEW3D_MT_paint_weight.menu)
	VIEW3D_MT_pose_constraints.register()
	bpy.types.VIEW3D_MT_pose_constraints.append(VIEW3D_MT_pose_constraints.menu)
	VIEW3D_MT_pose_showhide.register()
	bpy.types.VIEW3D_MT_pose_showhide.append(VIEW3D_MT_pose_showhide.menu)
	VIEW3D_MT_pose_specials.register()
	bpy.types.VIEW3D_MT_pose_context_menu.append(VIEW3D_MT_pose_specials.menu)
	#VIEW3D_MT_select_edit_armature.register()#クラスなしのためregister()は未定義
	bpy.types.VIEW3D_MT_select_edit_armature.append(VIEW3D_MT_select_edit_armature.menu)
	VIEW3D_MT_select_edit_mesh.register()
	bpy.types.VIEW3D_MT_select_edit_mesh.append(VIEW3D_MT_select_edit_mesh.menu)
	VIEW3D_MT_select_object.register()
	bpy.types.VIEW3D_MT_select_object.append(VIEW3D_MT_select_object.menu)
	VIEW3D_MT_select_pose.register()
	bpy.types.VIEW3D_MT_select_pose.append(VIEW3D_MT_select_pose.menu)
	VIEW3D_MT_snap.register()
	bpy.types.VIEW3D_MT_snap.append(VIEW3D_MT_snap.menu)
	VIEW3D_MT_uv_map.register()
	bpy.types.VIEW3D_MT_uv_map.append(VIEW3D_MT_uv_map.menu)
	VIEW3D_MT_view.register()
	bpy.types.VIEW3D_MT_view.append(VIEW3D_MT_view.menu)
	VIEW3D_MT_view_align.register()
	bpy.types.VIEW3D_MT_view_align.append(VIEW3D_MT_view_align.menu)
	VIEW3D_MT_view_align_selected.register()
	bpy.types.VIEW3D_MT_view_align_selected.append(VIEW3D_MT_view_align_selected.menu)
	VIEW3D_PT_addon_sidebar.register()#menuなし
	#===　廃止したもの　===
	#VIEW3D_PT_imapaint_tools_missing.register()
	#bpy.types.VIEW3D_PT_imapaint_tools_missing.append(VIEW3D_PT_imapaint_tools_missing.menu)
	#VIEW3D_PT_slots_projectpaint.register()
	#bpy.types.VIEW3D_PT_slots_projectpaint.append(VIEW3D_PT_slots_projectpaint.menu)
	#VIEW3D_PT_tools_imagepaint_external.register()#VIEW3D_MT_viewに移動
	#bpy.types.IMAGE_MT_image.append(VIEW3D_PT_tools_imagepaint_external.menu)
	#=========
	#VIEW3D_PT_layers.register()#クラスなし
	bpy.types.VIEW3D_PT_collections.append(VIEW3D_PT_layers.menu)
	#=== VIEW3D_PT_addon_sidebarの中で使用するので以下の2つはメニューを登録しない ===
	#VIEW3D_PT_transform_orientations.register()#クラスなし
	#bpy.types.VIEW3D_PT_transform_orientations.append(VIEW3D_PT_transform_orientations.menu)
	#VIEW3D_PT_view3d_name.register()#クラスなし
	#bpy.types.VIEW3D_PT_tools_object_options.append(VIEW3D_PT_view3d_name.menu)
	#========
	#VIEW3D_PT_view3d_cursor.register()#クラスなし
	bpy.types.VIEW3D_PT_view3d_cursor.append(VIEW3D_PT_view3d_cursor.menu)
	VIEW3D_PT_view3d_properties.register()
	bpy.types.VIEW3D_PT_view3d_properties.append(VIEW3D_PT_view3d_properties.menu)
	DATA_PT_shape_curve.register()
	bpy.types.DATA_PT_shape_curve.append(DATA_PT_shape_curve.menu)
	BONE_PT_constraints.register()
	bpy.types.BONE_PT_constraints.append(BONE_PT_constraints.menu)
	PHYSICS_PT_dynamic_paint.register()
	bpy.types.PHYSICS_PT_dynamic_paint.append(PHYSICS_PT_dynamic_paint.menu)
	PHYSICS_PT_field.register()
	bpy.types.PHYSICS_PT_field.append(PHYSICS_PT_field.menu)
	PHYSICS_PT_softbody.register()
	bpy.types.PHYSICS_PT_softbody.append(PHYSICS_PT_softbody.menu)
	PHYSICS_PT_cloth.register()
	bpy.types.PHYSICS_PT_cloth.append(PHYSICS_PT_cloth.menu)
	BONE_PT_transform_locks.register()
	bpy.types.BONE_PT_transform.append(BONE_PT_transform_locks.menu)
	BONE_PT_relations.register()
	bpy.types.BONE_PT_relations.append(BONE_PT_relations.menu)
	#bpy.types.***.append(***.menu)

# プラグインをアンインストールしたときの処理
def unregister():
	for cls in classes:
	    bpy.utils.unregister_class(cls)

	bpy.app.translations.unregister(__name__)

	BONE_PT_context_bone.unregister()
	bpy.types.BONE_PT_context_bone.remove(BONE_PT_context_bone.menu)
	#BONE_PT_display.unregister()#クラスなしのためunregister()は未定義
	bpy.types.BONE_PT_display.remove(BONE_PT_display.menu)
	BONE_PT_inverse_kinematics.unregister()
	bpy.types.BONE_PT_inverse_kinematics.remove(BONE_PT_inverse_kinematics.menu)
	BONE_PT_transform.unregister()
	bpy.types.BONE_PT_transform.remove(BONE_PT_transform.menu)
	DATA_PT_bone_groups.unregister()
	bpy.types.DATA_PT_bone_groups.remove(DATA_PT_bone_groups.menu)
	DATA_PT_geometry_curve.unregister()
	bpy.types.DATA_PT_geometry_curve.remove(DATA_PT_geometry_curve.menu)
	DATA_PT_modifiers.unregister()
	bpy.types.DATA_PT_modifiers.remove(DATA_PT_modifiers.menu)
	DATA_PT_pose_library.unregister()
	bpy.types.DATA_PT_pose_library.remove(DATA_PT_pose_library.menu)
	DATA_PT_shape_keys.unregister()
	bpy.types.DATA_PT_shape_keys.remove(DATA_PT_shape_keys.menu_prepend)
	DATA_PT_skeleton.unregister()
	bpy.types.DATA_PT_skeleton.remove(DATA_PT_skeleton.menu)
	DATA_PT_uv_texture.unregister()
	bpy.types.DATA_PT_uv_texture.remove(DATA_PT_uv_texture.menu)
	DATA_PT_vertex_colors.unregister()
	bpy.types.DATA_PT_vertex_colors.remove(DATA_PT_vertex_colors.menu)
	DATA_PT_vertex_groups.unregister()
	bpy.types.DATA_PT_vertex_groups.remove(DATA_PT_vertex_groups.menu)
	DOPESHEET_MT_key.unregister()
	bpy.types.DOPESHEET_MT_key.remove(DOPESHEET_MT_key.menu)
	IMAGE_MT_image.unregister()
	bpy.types.IMAGE_MT_image.remove(IMAGE_MT_image.menu)
	IMAGE_MT_select.unregister()
	bpy.types.IMAGE_MT_select.remove(IMAGE_MT_select.menu)
	IMAGE_MT_uvs.unregister()
	bpy.types.IMAGE_MT_uvs.remove(IMAGE_MT_uvs.menu)
	IMAGE_MT_view.unregister()
	bpy.types.IMAGE_MT_view.remove(IMAGE_MT_view.menu)
	#INFO_HT_header.unregister()#クラスなしのためunregister()は未定義
	bpy.types.INFO_HT_header.remove(INFO_HT_header.menu_prepend)
	INFO_MT_file.unregister()
	bpy.types.TOPBAR_MT_file.remove(INFO_MT_file.menu)
	INFO_MT_file_external_data.unregister()
	bpy.types.TOPBAR_MT_file_external_data.remove(INFO_MT_file_external_data.menu)
	#INFO_MT_help.unregister()#クラスなしのためunregister()は未定義
	bpy.types.TOPBAR_MT_help.remove(INFO_MT_help.menu)
	INFO_MT_mesh_add.unregister()
	bpy.types.VIEW3D_MT_mesh_add.remove(INFO_MT_mesh_add.menu)
	INFO_MT_render.unregister()
	bpy.types.TOPBAR_MT_render.remove(INFO_MT_render.menu)
	INFO_MT_window.unregister()
	bpy.types.TOPBAR_MT_window.remove(INFO_MT_window.menu)
	MATERIAL_MT_specials.unregister()
	bpy.types.MATERIAL_MT_context_menu.remove(MATERIAL_MT_specials.menu)
	#MATERIAL_PT_context_material.unregister()#クラスなしのためunregister()は未定義
	#bpy.types.MATERIAL_PT_context_material.remove(MATERIAL_PT_context_material.menu)
	MESH_MT_shape_key_specials.unregister()
	bpy.types.MESH_MT_shape_key_context_menu.remove(MESH_MT_shape_key_specials.menu)
	MESH_MT_vertex_group_specials.unregister()
	bpy.types.MESH_MT_vertex_group_context_menu.remove(MESH_MT_vertex_group_specials.menu)
	NODE_MT_node.unregister()
	bpy.types.NODE_MT_node.remove(NODE_MT_node.menu)
	NODE_MT_view.unregister()
	bpy.types.NODE_MT_view.remove(NODE_MT_view.menu)
	OBJECT_PT_context_object.unregister()
	bpy.types.OBJECT_PT_context_object.remove(OBJECT_PT_context_object.menu)
	OBJECT_PT_display.unregister()
	bpy.types.OBJECT_PT_display.remove(OBJECT_PT_display.menu)
	#OBJECT_PT_transform.unregister()#クラスなしのためunregister()は未定義
	bpy.types.OBJECT_PT_transform.remove(OBJECT_PT_transform.menu)
	PHYSICS_PT_rigid_body.unregister()
	bpy.types.PHYSICS_PT_rigid_body.remove(PHYSICS_PT_rigid_body.menu)
	PHYSICS_PT_rigid_body_constraint.unregister()
	bpy.types.PHYSICS_PT_rigid_body_constraint.remove(PHYSICS_PT_rigid_body_constraint.menu)
	PROPERTIES_HT_header.unregister()
	bpy.types.PROPERTIES_HT_header.remove(PROPERTIES_HT_header.menu)
	RENDER_PT_bake.unregister()
	if hasattr(bpy.types, "CYCLES_RENDER_PT_bake"): # script.reroad で再読込すると、CYCLES_RENDER_PT_bakeが見つからないというエラーが出るので、とりあえずエラー文をスルー
		bpy.types.CYCLES_RENDER_PT_bake.remove(RENDER_PT_bake.menu)
	RENDER_PT_render.unregister()
	bpy.types.RENDER_PT_context.remove(RENDER_PT_render.menu)
	SCENE_PT_rigid_body_world.unregister()
	bpy.types.SCENE_PT_rigid_body_world.remove(SCENE_PT_rigid_body_world.menu)
	#TEXTURE_MT_specials.unregister()#TEXTURE_PT_image に統合
	#bpy.types.VIEW3D_PT_slots_projectpaint.remove(TEXTURE_MT_specials.menu)
	#TEXTURE_PT_context_texture.unregister()#クラスなしのためunregister()は未定義
	#bpy.types.TEXTURE_PT_context_texture.remove(TEXTURE_PT_context_texture.menu)
	TEXTURE_PT_image.unregister()
	bpy.types.VIEW3D_PT_slots_projectpaint.remove(TEXTURE_PT_image.menu)
	#TEXTURE_PT_mapping.unregister()#TEXTURE_PT_image に統合
	#bpy.types.VIEW3D_PT_slots_projectpaint.remove(TEXTURE_PT_mapping.menu)
	TEXT_MT_text.unregister()
	bpy.types.TEXT_MT_text.remove(TEXT_MT_text.menu)
	USERPREF_HT_header.unregister()
	bpy.types.USERPREF_PT_navigation_bar.remove(USERPREF_HT_header.menu)
	USERPREF_PT_file.unregister()
	bpy.types.USERPREF_PT_file_paths_applications.remove(USERPREF_PT_file.menu)
	VIEW3D_MT_armature_specials.unregister()
	bpy.types.VIEW3D_MT_armature_context_menu.remove(VIEW3D_MT_armature_specials.menu)
	VIEW3D_MT_bone_options_toggle.unregister()
	bpy.types.VIEW3D_MT_bone_options_toggle.remove(VIEW3D_MT_bone_options_toggle.menu)
	VIEW3D_MT_edit_armature.unregister()
	bpy.types.VIEW3D_MT_edit_armature.remove(VIEW3D_MT_edit_armature.menu)
	VIEW3D_MT_edit_mesh.unregister()
	bpy.types.VIEW3D_MT_edit_mesh.remove(VIEW3D_MT_edit_mesh.menu)
	VIEW3D_MT_edit_mesh_delete.unregister()
	bpy.types.VIEW3D_MT_edit_mesh_delete.remove(VIEW3D_MT_edit_mesh_delete.menu)
	VIEW3D_MT_edit_mesh_showhide.unregister()
	bpy.types.VIEW3D_MT_edit_mesh_showhide.remove(VIEW3D_MT_edit_mesh_showhide.menu)
	VIEW3D_MT_edit_mesh_specials.unregister()
	bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(VIEW3D_MT_edit_mesh_specials.menu)
	VIEW3D_MT_edit_mesh_vertices.unregister()
	bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(VIEW3D_MT_edit_mesh_vertices.menu)
	VIEW3D_MT_make_links.unregister()
	bpy.types.VIEW3D_MT_make_links.remove(VIEW3D_MT_make_links.menu)
	VIEW3D_MT_object.unregister()
	bpy.types.VIEW3D_MT_object.remove(VIEW3D_MT_object.menu)
	#VIEW3D_MT_object_apply.unregister() #廃止
	#bpy.types.VIEW3D_MT_object_apply.remove(VIEW3D_MT_object_apply.menu)
	VIEW3D_MT_object_showhide.unregister()
	bpy.types.VIEW3D_MT_object_showhide.remove(VIEW3D_MT_object_showhide.menu)
	VIEW3D_MT_object_specials.unregister()
	bpy.types.VIEW3D_MT_object_context_menu.remove(VIEW3D_MT_object_specials.menu)
	VIEW3D_MT_paint_weight.unregister()
	bpy.types.VIEW3D_MT_paint_weight.remove(VIEW3D_MT_paint_weight.menu)
	VIEW3D_MT_pose_constraints.unregister()
	bpy.types.VIEW3D_MT_pose_constraints.remove(VIEW3D_MT_pose_constraints.menu)
	VIEW3D_MT_pose_showhide.unregister()
	bpy.types.VIEW3D_MT_pose_showhide.remove(VIEW3D_MT_pose_showhide.menu)
	VIEW3D_MT_pose_specials.unregister()
	bpy.types.VIEW3D_MT_pose_context_menu.remove(VIEW3D_MT_pose_specials.menu)
	#VIEW3D_MT_select_edit_armature.unregister()#クラスなしのためunregister()は未定義
	bpy.types.VIEW3D_MT_select_edit_armature.remove(VIEW3D_MT_select_edit_armature.menu)
	VIEW3D_MT_select_edit_mesh.unregister()
	bpy.types.VIEW3D_MT_select_edit_mesh.remove(VIEW3D_MT_select_edit_mesh.menu)
	VIEW3D_MT_select_object.unregister()
	bpy.types.VIEW3D_MT_select_object.remove(VIEW3D_MT_select_object.menu)
	VIEW3D_MT_select_pose.unregister()
	bpy.types.VIEW3D_MT_select_pose.remove(VIEW3D_MT_select_pose.menu)
	VIEW3D_MT_snap.unregister()
	bpy.types.VIEW3D_MT_snap.remove(VIEW3D_MT_snap.menu)
	VIEW3D_MT_uv_map.unregister()
	bpy.types.VIEW3D_MT_uv_map.remove(VIEW3D_MT_uv_map.menu)
	VIEW3D_MT_view.unregister()
	bpy.types.VIEW3D_MT_view.remove(VIEW3D_MT_view.menu)
	VIEW3D_MT_view_align.unregister()
	bpy.types.VIEW3D_MT_view_align.remove(VIEW3D_MT_view_align.menu)
	VIEW3D_MT_view_align_selected.unregister()
	bpy.types.VIEW3D_MT_view_align_selected.remove(VIEW3D_MT_view_align_selected.menu)
	VIEW3D_PT_addon_sidebar.unregister()#menuなし
	#===　廃止したもの　===
	#VIEW3D_PT_imapaint_tools_missing.unregister()
	#bpy.types.VIEW3D_PT_imapaint_tools_missing.remove(VIEW3D_PT_imapaint_tools_missing.menu)
	#VIEW3D_PT_slots_projectpaint.unregister()
	#bpy.types.VIEW3D_PT_slots_projectpaint.remove(VIEW3D_PT_slots_projectpaint.menu)
	#VIEW3D_PT_tools_imagepaint_external.unregister()#VIEW3D_MT_viewに移動
	#bpy.types.IMAGE_MT_image.remove(VIEW3D_PT_tools_imagepaint_external.menu)	
	#========
	#VIEW3D_PT_layers.unregister()#クラスなし
	bpy.types.VIEW3D_PT_collections.remove(VIEW3D_PT_layers.menu)
	#=== VIEW3D_PT_addon_sidebarの中で使用するので以下の2つはメニューを登録解除しない ===
	#VIEW3D_PT_transform_orientations.unregister()#クラスなし
	#bpy.types.VIEW3D_PT_transform_orientations.remove(VIEW3D_PT_transform_orientations.menu)
	#VIEW3D_PT_view3d_name.unregister()#クラスなし
	#bpy.types.VIEW3D_PT_tools_object_options.remove(VIEW3D_PT_view3d_name.menu)
	#========
	#VIEW3D_PT_view3d_cursor.unregister()#クラスなし
	bpy.types.VIEW3D_PT_view3d_cursor.remove(VIEW3D_PT_view3d_cursor.menu)
	VIEW3D_PT_view3d_properties.unregister()
	bpy.types.VIEW3D_PT_view3d_properties.remove(VIEW3D_PT_view3d_properties.menu)
	DATA_PT_shape_curve.unregister()
	bpy.types.DATA_PT_shape_curve.remove(DATA_PT_shape_curve.menu)
	BONE_PT_constraints.unregister()
	bpy.types.BONE_PT_constraints.remove(BONE_PT_constraints.menu)
	PHYSICS_PT_dynamic_paint.unregister()
	bpy.types.PHYSICS_PT_dynamic_paint.remove(PHYSICS_PT_dynamic_paint.menu)
	PHYSICS_PT_field.unregister()
	bpy.types.PHYSICS_PT_field.remove(PHYSICS_PT_field.menu)
	PHYSICS_PT_softbody.unregister()
	bpy.types.PHYSICS_PT_softbody.remove(PHYSICS_PT_softbody.menu)
	PHYSICS_PT_cloth.unregister()
	bpy.types.PHYSICS_PT_cloth.remove(PHYSICS_PT_cloth.menu)
	BONE_PT_transform_locks.unregister()
	bpy.types.BONE_PT_transform.remove(BONE_PT_transform_locks.menu)
	BONE_PT_relations.unregister()
	bpy.types.BONE_PT_relations.remove(BONE_PT_relations.menu)
	#bpy.types.***.remove(***.menu)

# メイン関数
if __name__ == "__main__":
	register()
