# 「トップバー」エリア > 「ファイル」メニュー
# "TOPBAR" Area > "File" Menu

import bpy
import mathutils
import os.path
import os, sys, codecs
import subprocess
import fnmatch
from bpy.props import *

################
# オペレーター #
################

class RestartBlender(bpy.types.Operator):
	bl_idname = "wm.restart_blender"
	bl_label = "Restart"
	bl_description = "Restart Blender"
	bl_options = {'REGISTER'}

	def execute(self, context):
		py = os.path.join(os.path.dirname(__file__), "console_toggle.py")
		filepath = bpy.data.filepath
		if (filepath != ""):
			subprocess.Popen([sys.argv[0], filepath, '-P', py])
		else:
			subprocess.Popen([sys.argv[0],'-P', py])
		bpy.ops.wm.quit_blender()
		return {'FINISHED'}

class RecoverLatestAutoSave(bpy.types.Operator):
	bl_idname = "wm.recover_latest_auto_save"
	bl_label = "Load Last AutoSave"
	bl_description = "Open the LAST 'automatically saved file' to restore it"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		tempPath = context.preferences.filepaths.temporary_directory
		if (not tempPath):
			return False
		for fileName in fnmatch.filter(os.listdir(tempPath), "*.blend"):
			if (fileName != "quit.blend"):
				return True
		return False

	def execute(self, context):
		tempPath = context.preferences.filepaths.temporary_directory
		lastFile = None
		for fileName in fnmatch.filter(os.listdir(tempPath), "*.blend"):
			path = os.path.join(tempPath, fileName)
			if (lastFile):
				mtime = os.stat(path).st_mtime
				if (lastTime < mtime and fileName != "quit.blend"):
					lastFile = path
					lastTime = mtime
			else:
				lastFile = path
				lastTime = os.stat(path).st_mtime
		bpy.ops.wm.recover_auto_save(filepath=lastFile)
		self.report(type={'INFO'}, message="Loaded last auto-save file")
		return {'FINISHED'}

class SaveMainfileUnmassage(bpy.types.Operator):
	bl_idname = "wm.save_mainfile_unmassage"
	bl_label = "Save Without Confirmation"
	bl_description = "Save file without displaying the confirmation message"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		if (bpy.data.filepath):
			return True
		return False

	def execute(self, context):
		if (bpy.data.filepath != ""):
			bpy.ops.wm.save_mainfile()
			self.report(type={"INFO"}, message=bpy.path.basename(bpy.data.filepath)+" Saved")
		else:
			self.report(type={"ERROR"}, message="Do \"Save As\" beforehand")
		return {'FINISHED'}

class LoadLastFile(bpy.types.Operator):
	bl_idname = "wm.load_last_file"
	bl_label = "Open Last Used File"
	bl_description = "Open the file at the top of 'Open Recent'"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		recent_files = os.path.join(bpy.utils.user_resource('CONFIG'), "recent-files.txt")
		file = codecs.open(recent_files, 'r', 'utf-8-sig')
		path = file.readline().rstrip("\r\n")
		file.close()
		if (path != ""):
			return True
		return False

	def execute(self, context):
		recent_files = os.path.join(bpy.utils.user_resource('CONFIG'), "recent-files.txt")
		file = codecs.open(recent_files, 'r', 'utf-8-sig')
		path = file.readline().rstrip("\r\n")
		file.close()
		bpy.ops.wm.open_mainfile(filepath=path)
		return {'FINISHED'}

##########################
# オペレーター(全体処理) #
##########################

class RenameDataBlocks(bpy.types.Operator):
	bl_idname = "file.rename_data_blocks"
	bl_label = "Rename all of specific Data  (use cautiously)"
	bl_description = "Rename all of the designated type's data"
	bl_options = {'REGISTER', 'UNDO'}

	actions : BoolProperty(name="Action", default=False)
	armatures : BoolProperty(name="Armature", default=False)
	brushes : BoolProperty(name="Brush", default=False)
	cameras : BoolProperty(name="Camera", default=False)
	curves : BoolProperty(name="Curve", default=False)
	fonts : BoolProperty(name="Font", default=False)
	grease_pencil : BoolProperty(name="Grease Pencil", default=False)
	groups : BoolProperty(name="Group", default=False)
	images : BoolProperty(name="Image", default=False)
	lamps : BoolProperty(name="Lamp", default=False)
	lattices : BoolProperty(name="Lattice", default=False)
	libraries : BoolProperty(name="Library", default=False)
	linestyles : BoolProperty(name="Line Style", default=False)
	masks : BoolProperty(name="Mask", default=False)
	materials : BoolProperty(name="Material", default=False)
	meshes : BoolProperty(name="Mesh", default=False)
	metaballs : BoolProperty(name="Metaballs", default=False)
	movieclips : BoolProperty(name="Movie Clip", default=False)
	node_groups : BoolProperty(name="Node Groups", default=False)
	objects : BoolProperty(name="Object", default=False)
	palettes : BoolProperty(name="Palette", default=False)
	particles : BoolProperty(name="Particle", default=False)
	scenes : BoolProperty(name="Scene", default=False)
	screens : BoolProperty(name="Screen", default=False)
	scripts : BoolProperty(name="Script", default=False)
	shape_keys : BoolProperty(name="Shape Key", default=False)
	sounds : BoolProperty(name="Sound", default=False)
	speakers : BoolProperty(name="Speaker", default=False)
	texts : BoolProperty(name="Text", default=False)
	textures : BoolProperty(name="Texture", default=False)
	window_managers : BoolProperty(name="Window Manager", default=False)
	worlds : BoolProperty(name="World", default=False)

	modifiers : BoolProperty(name="Modifier", default=False)
	constraints : BoolProperty(name="Constraints", default=False)

	vertex_groups : BoolProperty(name="Vertex Group", default=False)
	uvs : BoolProperty(name="UV", default=False)
	vertex_colors : BoolProperty(name="Vertex Color", default=False)

	bones : BoolProperty(name="Bone", default=False)
	bone_constraints : BoolProperty(name="Bone Constraints", default=False)

	prefix : StringProperty(name="Add Prefix", default="")
	suffix : StringProperty(name="Add Suffix", default="")

	source : StringProperty(name="Target text", default="")
	replace : StringProperty(name="New Text", default="")

	selected_only : BoolProperty(name="Selected Objects Only", default=False)
	show_log : BoolProperty(name="Show Log", default=True)

	def draw(self, context):
		data_names = ['objects', 'meshes', 'curves', 'metaballs', 'fonts', 'armatures', 'lattices', 'cameras', 'lamps', 'speakers', 'materials', 'textures', 'images', 'actions', 'brushes', 'grease_pencil', 'groups', 'libraries', 'linestyles', 'masks', 'movieclips', 'node_groups', 'palettes', 'particles', 'scenes', 'screens', 'scripts', 'shape_keys', 'sounds', 'texts', 'window_managers', 'worlds']
		self.layout.label(text="Check Rename Data")
		box = self.layout.box()
		for i, data_name in enumerate(data_names):
			if (i % 3 == 0):
				row = box.row()
			row.prop(self, data_name)
		box2 = self.layout.box()
		row = box2.row()
		row.label(text="Object")
		row.prop(self, 'modifiers')
		row.prop(self, 'constraints')
		box3 = self.layout.box()
		box3.label(text="Mesh")
		row = box3.row()
		row.prop(self, 'vertex_groups')
		row.prop(self, 'uvs')
		row.prop(self, 'vertex_colors')
		box4 = self.layout.box()
		row = box4.row()		
		row.label(text="Armature")
		row.prop(self, 'bones')
		row.prop(self, 'bone_constraints')
		self.layout.label(text="Rename Settings")
		box5 = self.layout.box()
		row = box5.row()
		row.prop(self, 'prefix')
		row.prop(self, 'suffix')
		row = box5.row()
		row.prop(self, 'source')
		row.prop(self, 'replace')
		row = box5.row()
		row.prop(self, 'selected_only')
		row.prop(self, 'show_log')
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=600)
	def rename(self, name):
		new_name = self.prefix + name.replace(self.source, self.replace) + self.suffix
		if (self.show_log):
			if (name != new_name):
				self.report(type={'INFO'}, message=name+" => "+new_name)
		return new_name
	def execute(self, context):
		data_names = ['objects', 'meshes', 'curves', 'metaballs', 'fonts', 'armatures', 'lattices', 'cameras', 'lamps', 'speakers', 'materials', 'textures', 'images', 'actions', 'brushes', 'grease_pencil', 'groups', 'libraries', 'linestyles', 'masks', 'movieclips', 'node_groups', 'palettes', 'particles', 'scenes', 'screens', 'scripts', 'shape_keys', 'sounds', 'texts', 'window_managers', 'worlds']
		for data_name in data_names:
			if (self.__getattribute__(data_name)):
				if (self.selected_only):
					if (data_name == 'objects'):
						for obj in context.selected_objects[:]:
							obj.name = self.rename(obj.name)
					elif (data_name == 'armatures'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'ARMATURE'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'cameras'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'CAMERA'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'curves'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'CURVE' or obj.type == 'SURFACE'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'fonts'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'FONT'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'lamps'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'LAMP'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'lattices'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'LATTICE'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'meshes'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'MESH'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'metaballs'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'META'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'speakers'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'SPEAKER'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name in 'materials'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for slot in obj.material_slots:
								if (slot):
									if (slot.material.name not in alreadys):
										slot.material.name = self.rename(slot.material.name)
										alreadys.append(slot.material.name)
					elif (data_name in 'textures'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for slot in obj.material_slots:
								if (slot):
									for tex_slot in slot.material.texture_slots:
										if (tex_slot):
											if (tex_slot.texture.name not in alreadys):
												tex_slot.texture.name = self.rename(tex_slot.texture.name)
												alreadys.append(tex_slot.texture.name)
					elif (data_name in 'images'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for slot in obj.material_slots:
								if (slot):
									for tex_slot in slot.material.texture_slots:
										if (tex_slot):
											if (tex_slot.texture.type == 'IMAGE'):
												if (tex_slot.texture.image):
													if (tex_slot.texture.image.name not in alreadys):
														tex_slot.texture.image.name = self.rename(tex_slot.texture.image.name)
														alreadys.append(tex_slot.texture.image.name)
					elif (data_name in 'grease_pencil'):
						alreadys = []
						for obj in context.selected_objects[:]:
							if (obj.grease_pencil):
								if (obj.grease_pencil.name not in alreadys):
									obj.grease_pencil.name = self.rename(obj.grease_pencil.name)
									alreadys.append(obj.grease_pencil.name)
					elif (data_name in 'particles'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for mod in obj.modifiers[:]:
								if (mod.type == 'PARTICLE_SYSTEM'):
									if (mod.particle_system.name not in alreadys):
										mod.particle_system.name = self.rename(mod.particle_system.name)
										alreadys.append(mod.particle_system.name)
					elif (data_name in 'groups'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for group in obj.users_group[:]:
								if (group.name not in alreadys):
									group.name = self.rename(group.name)
									alreadys.append(group.name)
					elif (data_name in 'shape_keys'):
						alreadys = []
						for obj in context.selected_objects[:]:
							if (obj.type == 'MESH'):
								if (obj.data.shape_keys):
									if (obj.data.shape_keys.name not in alreadys):
										obj.data.shape_keys.name = self.rename(obj.data.shape_keys.name)
										alreadys.append(obj.data.shape_keys.name)
					else:
						self.report(type={'INFO'}, message="Ignored "+data_name+" data")
				else:
					for data in bpy.data.__getattribute__(data_name)[:]:
						data.name = self.rename(data.name)
		if (self.vertex_groups):
			if (self.selected_only):
				objs = context.selected_objects[:]
			else:
				objs = bpy.data.objects[:]
			for obj in objs:
				for vg in obj.vertex_groups[:]:
					vg.name = self.rename(vg.name)
		if (self.bones):
			if (self.selected_only):
				arms = []
				for obj in context.selected_objects:
					if (obj.type == 'ARMATURE'):
						arms.append(obj.data)
			else:
				arms = bpy.data.armatures[:]
			for arm in arms:
				for bone in arm.bones:
					bone.name = self.rename(bone.name)
		if (self.uvs):
			if (self.selected_only):
				mes = []
				for obj in context.selected_objects:
					if (obj.type == 'MESH'):
						mes.append(obj.data)
			else:
				mes = bpy.data.meshes[:]
			for me in mes:
				for uvl in me.uv_layers[:]:
					uvl.name = self.rename(uvl.name)
		if (self.vertex_colors):
			if (self.selected_only):
				mes = []
				for obj in context.selected_objects:
					if (obj.type == 'MESH'):
						mes.append(obj.data)
			else:
				mes = bpy.data.meshes[:]
			for me in mes:
				for vc in me.vertex_colors[:]:
					vc.name = self.rename(vc.name)
		if (self.modifiers):
			if (self.selected_only):
				objs = context.selected_objects[:]
			else:
				objs = bpy.data.objects[:]
			for obj in objs:
				for mod in obj.modifiers[:]:
					mod.name = self.rename(mod.name)
		if (self.constraints):
			if (self.selected_only):
				objs = context.selected_objects[:]
			else:
				objs = bpy.data.objects[:]
			for obj in objs:
				for const in obj.constraints[:]:
					const.name = self.rename(const.name)
		if (self.bone_constraints):
			if (self.selected_only):
				objs = context.selected_objects[:]
			else:
				objs = bpy.data.objects[:]
			for obj in objs:
				if (obj.type == 'ARMATURE'):
					for bone in obj.pose.bones[:]:
						for const in bone.constraints:
							const.name = self.rename(const.name)
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

##############################
# オペレーター(オブジェクト) #
##############################

class AllOnShowAllEdges(bpy.types.Operator):
	bl_idname = "object.all_on_show_all_edges"
	bl_label = "Set 'All Edges' Property Together"
	bl_description = "Set 'All Edges' property of all objects"
	bl_options = {'REGISTER', 'UNDO'}

	item = [('1',"Enabled", "", 1), ('0',"Disabled", "", 2)]
	isOn : EnumProperty(name="Method", items=item)

	@classmethod
	def poll(cls, context):
		if (len(bpy.data.objects)):
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop(self, 'isOn', expand=True)

	def execute(self, context):
		print(bool(int(self.isOn)))
		for obj in bpy.data.objects:
			obj.show_all_edges = bool(int(self.isOn))
		return {'FINISHED'}

class AllSetDrawType(bpy.types.Operator):
	bl_idname = "object.all_set_display_type"
	bl_label = "Set display method in viewport together"
	bl_description = "Set display method in viewport together for all of the designated type's objects"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		("MESH", "Mesh", "", 1),
		("CURVE", "Curve", "", 2),
		("SURFACE", "Surface", "", 3),
		("META", "Metaballs", "", 4),
		("FONT", "Text", "", 5),
		("ARMATURE", "Armature", "", 6),
		("LATTICE", "Lattice", "", 7),
		("EMPTY", "Empty", "", 8),
		("CAMERA", "Camera", "", 9),
		("LAMP", "Lamp", "", 10),
		("SPEAKER", "Speaker", "", 11),
		("ALL", "All Objects", "", 12),
		]
	objType : EnumProperty(items=items, name="Object Type")
	items = [
		("TEXTURED", "Texture", "", 1),
		("SOLID", "Solid", "", 2),
		("WIRE", "Wire", "", 3),
		("BOUNDS", "Bound", "", 4),
		]
	type : EnumProperty(items=items, name="Display As")

	@classmethod
	def poll(cls, context):
		if (len(bpy.data.objects)):
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		for obj in bpy.data.objects:
			if (self.objType == obj.type or self.objType == "ALL"):
				obj.display_type = self.type
		return {'FINISHED'}

class AllRenameObjectData(bpy.types.Operator):
	bl_idname = "object.all_rename_object_data"
	bl_label = "Match All Data Names to Objects' Names"
	bl_description = "Change all objects' linked data names to their objects' names"
	bl_options = {'REGISTER', 'UNDO'}

	isSelected : BoolProperty(name="Only Selected Object", default=False)

	@classmethod
	def poll(cls, context):
		if (len(bpy.data.objects)):
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		if (self.isSelected):
			objs = context.selected_objects
		else:
			objs = bpy.data.objects
		for obj in objs:
			if (obj and obj.data):
				obj.data.name = obj.name
		return {'FINISHED'}

############################
# オペレーター(マテリアル) #
############################
"""
class AllSetMaterialReceiveTransparent(bpy.types.Operator):
	bl_idname = "material.all_set_material_receive_transparent"
	bl_label = "On all material \"Receive Transparent\""
	bl_description = "You to receive semi-transparent shadow? \"about whether all material (off) on the"
	bl_options = {'REGISTER', 'UNDO'}

	isOff : BoolProperty(name="Off", default=False)

	@classmethod
	def poll(cls, context):
		if (len(bpy.data.materials)):
			return True
		return False

	def execute(self, context):
		for mat in bpy.data.materials:
			mat.use_transparent_shadows = not self.isOff
		return {'FINISHED'}

class AllSetMaterialColorRamp(bpy.types.Operator):
	bl_idname = "material.all_set_material_color_ramp"
	bl_label = "Copy material color ramp settings"
	bl_description = "Color ramp settings of active material is all material other (only selected objects are allowed) to copy"
	bl_options = {'REGISTER', 'UNDO'}

	isOnlySelected : BoolProperty(name="Selected Object Only", default=False)

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (len(bpy.data.materials)):
			return True
		return False

	def execute(self, context):
		activeMat = context.active_object.active_material
		if (not activeMat):
			self.report(type={"ERROR"}, message="None Active Material")
			return {"CANCELLED"}
		mats = []
		if (self.isOnlySelected):
			for obj in context.selected_objects:
				for mslot in obj.material_slots:
					if (mslot.material):
						for mat in mats:
							if (mat.name == mslot.material.name):
								break
						else:
							mats.append(mslot.material)
		else:
			mats = bpy.data.materials
		for mat in mats:
			if (mat.name != activeMat.name):
				mat.use_diffuse_ramp = activeMat.use_diffuse_ramp
				mat.diffuse_ramp.color_mode = activeMat.diffuse_ramp.color_mode
				mat.diffuse_ramp.hue_interpolation = activeMat.diffuse_ramp.hue_interpolation
				mat.diffuse_ramp.interpolation = activeMat.diffuse_ramp.interpolation
				for i in range(len(activeMat.diffuse_ramp.elements)):
					if (len(mat.diffuse_ramp.elements) < i+1):
						color = mat.diffuse_ramp.elements.new(color.position)
					else:
						color = mat.diffuse_ramp.elements[i]
					color.position = activeMat.diffuse_ramp.elements[i].position
					color.alpha = activeMat.diffuse_ramp.elements[i].alpha
					color.color = activeMat.diffuse_ramp.elements[i].color
				mat.diffuse_ramp_input = activeMat.diffuse_ramp_input
				mat.diffuse_ramp_blend = activeMat.diffuse_ramp_blend
				mat.diffuse_ramp_factor = activeMat.diffuse_ramp_factor
		return {'FINISHED'}
"""
class AllSetMaterialFreestyleColor(bpy.types.Operator):
	bl_idname = "material.all_set_material_freestyle_color"
	bl_label = "Copy FreeStyle Line Color to All Other Materials"
	bl_description = "Copy the active material's FreeStyle line color to all other materials"
	bl_options = {'REGISTER', 'UNDO'}

	isOnlySelected : BoolProperty(name="Copy to Only Selected Objects' Materials", default=False)
	isColor : BoolProperty(name="Color", default=True)
	isAlpha : BoolProperty(name="Alpha", default=True)

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (len(bpy.data.materials)):
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=300)
	def draw(self, context):
		sp = self.layout.split(factor=0.2)
		row = sp.row()
		row.label(text="")
		row.prop(self, 'isOnlySelected', text="")
		sp.label(text="Copy to Only Selected Objects' Materials")
		row = self.layout.box().split(factor=0.4)
		row.label(text="Settings to copy")
		row.prop(self, 'isColor')
		row.prop(self, 'isAlpha')

	def execute(self, context):
		activeMat = context.active_object.active_material
		mats = []
		if (self.isOnlySelected):
			for obj in context.selected_objects:
				for mslot in obj.material_slots:
					if (mslot.material):
						for mat in mats:
							if (mat.name == mslot.material.name):
								break
						else:
							mats.append(mslot.material)
		else:
			mats = bpy.data.materials
		for mat in mats:
			if (mat.name != activeMat.name):
				col = list(mat.line_color[:])
				if (self.isColor):
					col[0] = activeMat.line_color[0]
					col[1] = activeMat.line_color[1]
					col[2] = activeMat.line_color[2]
				if (self.isAlpha):
					col[3] = activeMat.line_color[3]
				mat.line_color = tuple(col)
		return {'FINISHED'}

class AllSetMaterialFreestyleColorByDiffuse(bpy.types.Operator):
	bl_idname = "material.all_set_material_freestyle_color_by_diffuse"
	bl_label = "Match All FreeStyle Line Colors to Diffuse Colors"
	bl_description = "Change all materials' FreeStyle line colors to their diffuse colors in viewport"
	bl_options = {'REGISTER', 'UNDO'}

	isOnlySelected : BoolProperty(name="Apply to Only Selected Objects' Materials", default=False)
	methods = [
		("DIFFUSE", "Diffuse Color in viewport", "", 1),
		("BLEND", "Diffuse Color Mixed with Other Color", "", 2)
		]
	color_method : EnumProperty(items=methods, name="FreeStyle Line Color")
	blendColor : FloatVectorProperty(name="Blend Color", default=(0.0, 0.0, 0.0), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype="COLOR")
	items = [
		("MIX", "Mix", "", 1),
		("MULTI", "Multiplication", "", 2),
		("SCREEN", "Screen", "", 3),
		]
	blendMode : EnumProperty(items=items, name="Blend Mode")
	blendValue : FloatProperty(name="Blend Strength", default=0.5, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)

	@classmethod
	def poll(cls, context):
		if (len(bpy.data.materials)):
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=330)
	def draw(self, context):
		sp = self.layout.split(factor=0.2)
		row = sp.row()
		row.label(text="")
		row.prop(self, 'isOnlySelected', text="")
		sp.label(text="Apply to Only Selected Objects' Materials")
		self.layout.props_enum(self, 'color_method')
		if self.color_method == 'BLEND':
			box = self.layout.box()
			row = box.row()
			row.label(text="Blend Color")
			row.prop(self, 'blendColor', text="")
			row = box.row()
			row.label(text="Blend Mode")
			row.prop(self, 'blendMode', text="")
			row = box.row()
			row.label(text="Blend Strength")
			row.prop(self, 'blendValue', text="")
		else:
			box = self.layout.box()

	def execute(self, context):
		mats = []
		if (self.isOnlySelected):
			for obj in context.selected_objects:
				for mslot in obj.material_slots:
					if (mslot.material):
						for mat in mats:
							if (mat.name == mslot.material.name):
								break
						else:
							mats.append(mslot.material)
		else:
			mats = bpy.data.materials
		for mat in mats:
			c = (mat.diffuse_color[0], mat.diffuse_color[1], mat.diffuse_color[2], mat.line_color[3])
			b = self.blendColor
			v = self.blendValue
			if (self.blendMode == "MIX"):
				c = ( (c[0]*(1-v))+(b[0]*v), (c[1]*(1-v))+(b[1]*v), (c[2]*(1-v))+(b[2]*v), c[3] )
			if (self.blendMode == "MULTI"):
				c = ( (c[0]*(1-v))+((c[0]*b[0])*v), (c[1]*(1-v))+((c[1]*b[1])*v), (c[2]*(1-v))+((c[2]*b[2])*v), c[3] )
			if (self.blendMode == "SCREEN"):
				c = ( (c[0]*(1-v))+(1-((1-c[0])*(1-b[0]))*v), (c[1]*(1-v))+(1-((1-c[1])*(1-b[1]))*v), (c[2]*(1-v))+(1-((1-c[2])*(1-b[2]))*v), c[3] )
			mat.line_color = c
		return {'FINISHED'}

class AllSetMaterialObjectColor(bpy.types.Operator):
	bl_idname = "material.all_set_material_object_color"
	bl_label = "Set All Materials' Diffuse Colors"
	bl_description = "Set all materials' diffuse colors in viewport"
	bl_options = {'REGISTER', 'UNDO'}

	item = [
		("1", "Enabled", "", 1),
		("0", "Disabled", "", 2)
		]
	use_object_color : EnumProperty(name="On/Off", items=item)
	set_color : BoolProperty(name="Set Color", default=True)	
	only_selected : BoolProperty(name="Apply to Only Selected Objects' Materials", default=False)
	color : FloatVectorProperty(name="Color",default=(1, 1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR_GAMMA', size=4)

	@classmethod
	def poll(cls, context):
		if (len(bpy.data.materials)):
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop(self, 'use_object_color', expand=True)
		if int(self.use_object_color):
			sp = self.layout.split(factor=0.2)
			sp.label(text="")
			sp.prop(self, 'set_color')
		if self.set_color:
			box = self.layout.box()
			sp = box.split(factor=0.1)
			row = sp.row()
			row.label(text="")
			row.prop(self, 'only_selected', text="")
			sp.label(text="Apply to Only Selected Objects' Materials")
			row = box.row()
			row.label(text="Diffuse Color")
			row.prop(self, 'color', text="")
		else:
			box = self.layout.box()	

	def execute(self, context):
		for ar in context.screen.areas:
			if ar.type == "VIEW_3D":
				area = ar
		space = area.spaces[0]
		if int(self.use_object_color):
			space.shading.color_type = 'MATERIAL'
		else:
			space.shading.color_type = 'OBJECT'
		if self.set_color:
			mats = []
			if (self.only_selected):
				for obj in context.selected_objects:
					for slot in obj.material_slots:
						if (slot.material):
							mats.append(slot.material)
				mats = set(mats)
			else:
				mats = bpy.data.materials[:]
			for mat in mats:
				mat.diffuse_color = self.color
		return {'FINISHED'}

############################
# オペレーター(テクスチャ) #
############################
"""
class AllSetBumpMethod(bpy.types.Operator):
	bl_idname = "texture.all_set_bump_method"
	bl_label = "Set all bump of quality"
	bl_description = "Bump-map texture of all quality sets in bulk"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		("BUMP_ORIGINAL", "Original", "", 1),
		("BUMP_COMPATIBLE", "Compatibility", "", 2),
		("BUMP_LOW_QUALITY", "Low Quality", "", 3),
		("BUMP_MEDIUM_QUALITY", "Normal Quality", "", 4),
		("BUMP_BEST_QUALITY", "High Quality", "", 5),
		]
	method : EnumProperty(items=items, name="Bump Quality", default="BUMP_BEST_QUALITY")

	@classmethod
	def poll(cls, context):
		if (not len(bpy.data.materials)):
			return False
		for mat in  bpy.data.materials:
			for slot in mat.texture_slots:
				if (slot):
					return True
		return False

	def execute(self, context):
		for mat in bpy.data.materials:
			for slot in mat.texture_slots:
				try:
					slot.bump_method = self.method
				except AttributeError: pass
		return {'FINISHED'}
"""
class AllRenameTextureFileName(bpy.types.Operator):
	bl_idname = "texture.all_rename_texture_file_name"
	bl_label = "Match All Texture Names to Image File Names"
	bl_description = "Change all textures' names to their linked image files' names"
	bl_options = {'REGISTER', 'UNDO'}

	isExt : BoolProperty(name="Include Extension", default=True)

	@classmethod
	def poll(cls, context):
		for tex in bpy.data.textures:
			if (tex.type == "IMAGE"):
				if (tex.image):
					if (tex.image.filepath != ""):
						return True
		return False

	def execute(self, context):
		for tex in  bpy.data.textures:
			if (tex.type == "IMAGE"):
				if (tex.image.filepath_raw != ""):
					name = bpy.path.basename(tex.image.filepath_raw)
					if (not self.isExt):
						name, ext = os.path.splitext(name)
					try:
						tex.name = name
					except: pass
		return {'FINISHED'}
"""
class FixEmptyTextureUVLayer(bpy.types.Operator):
	bl_idname = "texture.fix_empty_texture_uv_layer"
	bl_label = "Fill active UV if blanks"
	bl_description = "Under active UV texture UV specified fields is linked to an empty mesh object fills"
	bl_options = {'REGISTER', 'UNDO'}

	isSelectedOnly : BoolProperty(name="Selected Object Only", default=False)

	@classmethod
	def poll(cls, context):
		for obj in bpy.data.objects:
			if (obj.type == 'MESH'):
				if (len(obj.data.uv_layers)):
					for mslot in obj.material_slots:
						if (mslot.material):
							for tslot in mslot.material:
								if (tslot):
									if (tslot.texture_coords == 'UV'):
										if(tslot.uv_layer == ""):
											return True
		return False

	def execute(self, context):
		objs = bpy.data.objects
		if (self.isSelectedOnly):
			objs = context.selected_objects
		for obj in objs:
			if (obj.type == "MESH"):
				me = obj.data
				if (len(me.uv_layers) > 0):
					uv = me.uv_layers.active
					for mslot in obj.material_slots:
						mat = mslot.material
						if (mat):
							for tslot in mat.texture_slots:
								if (tslot != None):
									if (tslot.texture_coords == "UV"):
										if(tslot.uv_layer == ""):
											tslot.uv_layer = uv.name
		return {'FINISHED'}
"""
##########################
# オペレーター(物理演算) #
##########################

class AllSetPhysicsFrames(bpy.types.Operator):
	bl_idname = "scene.all_set_physics_frames"
	bl_label = "Match All Physics' Start/End to Rendering's ones"
	bl_description = "Change all physics' start / end frames to the rendering's start / end frames"
	bl_options = {'REGISTER', 'UNDO'}

	startOffset : IntProperty(name="Start Offset", default=0, step=1)
	endOffset : IntProperty(name="End Offset", default=0, step=1)

	isRigidBody : BoolProperty(name="RigidBody", default=True)
	isCloth : BoolProperty(name="Cloth", default=True)
	isSoftBody : BoolProperty(name="Soft Body", default=True)
	isFluid : BoolProperty(name="Fluid", default=True)
	isDynamicPaint : BoolProperty(name="Dynamic Paint", default=True)

	isParticle : BoolProperty(name="Particle", default=False)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		box = self.layout.box()
		sp = box.split(factor=0.55)
		row = sp.row()
		row.label(text="Start Frame")
		row.label(text=f":  {context.scene.frame_start} + {self.startOffset}")
		sp.prop(self, 'startOffset')
		sp = box.split(factor=0.55)
		row = sp.row()
		row.label(text="End Frame")
		row.label(text=f":  {context.scene.frame_end} + {self.endOffset}")
		sp.prop(self, 'endOffset')
		box = self.layout.box()
		row = box.row()
		row.prop(self, 'isRigidBody')
		row.prop(self, 'isCloth')
		row.prop(self, 'isSoftBody')
		row = box.row()
		row.prop(self, 'isFluid')
		row.prop(self, 'isDynamicPaint')
		row.prop(self, 'isParticle')

	def execute(self, context):
		start = context.scene.frame_start + self.startOffset
		end = context.scene.frame_end + self.endOffset
		if (self.isRigidBody and context.scene.rigidbody_world):
			context.scene.rigidbody_world.point_cache.frame_start = start
			context.scene.rigidbody_world.point_cache.frame_end = end
		if (self.isFluid):
			for obj in bpy.data.objects:
				for modi in obj.modifiers:
					if (modi.type == 'FLUID_SIMULATION'):
						modi.settings.start_time = (1.0 / context.scene.render.fps) * start
						modi.settings.end_time = (1.0 / context.scene.render.fps) * end
		if (self.isSoftBody):
			for obj in bpy.data.objects:
				for modi in obj.modifiers:
					if (modi.type == 'SOFT_BODY'):
						modi.point_cache.frame_start = start
						modi.point_cache.frame_end = end
		if (self.isDynamicPaint):
			for obj in bpy.data.objects:
				for modi in obj.modifiers:
					if (modi.type == 'DYNAMIC_PAINT'):
						if (modi.canvas_settings):
							for surface in modi.canvas_settings.canvas_surfaces:
								surface.frame_start = start
								surface.frame_end = end
		if (self.isCloth):
			for obj in bpy.data.objects:
				for modi in obj.modifiers:
					if (modi.type == 'CLOTH'):
						modi.point_cache.frame_start = start
						modi.point_cache.frame_end = end

		if (self.isParticle):
			for particle in bpy.data.particles:
				particle.frame_start = start
				particle.frame_end = end
		return {'FINISHED'}

##########################
# サブメニュー(Modifier) #
##########################

class EntireProcessMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process"
	bl_label = "Manipulate Data Together"
	bl_description = "Functions to manipulate specific data together"

	def draw(self, context):
		self.layout.operator(RenameDataBlocks.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.menu(EntireProcessObjectMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(EntireProcessMaterialMenu.bl_idname, icon='PLUGIN')
		#self.layout.menu(EntireProcessTextureMenu.bl_idname, icon='PLUGIN')
		self.layout.operator(AllRenameTextureFileName.bl_idname, icon='PLUGIN')
		#self.layout.menu(EntireProcessImageMenu.bl_idname, icon='PLUGIN')
		self.layout.operator('image.all_rename_image_file_name', icon='PLUGIN')
		#self.layout.menu(EntireProcessPhysicsMenu.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetPhysicsFrames.bl_idname, icon='PLUGIN')

class EntireProcessObjectMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_object"
	bl_label = "Manipulate Objects Together"
	bl_description = "Manipulate all objects together"

	def draw(self, context):
		self.layout.operator(AllOnShowAllEdges.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetDrawType.bl_idname, icon='PLUGIN')
		self.layout.operator(AllRenameObjectData.bl_idname, icon='PLUGIN')

class EntireProcessMaterialMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_material"
	bl_label = "Manipulate Materials Together"
	bl_description = "Manipulate all materials together"

	def draw(self, context):
		#self.layout.operator(AllSetMaterialReceiveTransparent.bl_idname, icon='PLUGIN')
		#self.layout.operator(AllSetMaterialColorRamp.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetMaterialFreestyleColor.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetMaterialFreestyleColorByDiffuse.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetMaterialObjectColor.bl_idname, icon='PLUGIN')

class EntireProcessTextureMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_texture"
	bl_label = "Manipulate Textures Together"
	bl_description = "Manipulate all textures together"

	def draw(self, context):
		self.layout.operator(AllRenameTextureFileName.bl_idname, icon='PLUGIN')
		#self.layout.operator(AllSetBumpMethod.bl_idname, icon='PLUGIN')
		#self.layout.operator(FixEmptyTextureUVLayer.bl_idname, icon='PLUGIN')

class EntireProcessImageMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_image"
	bl_label = "Manipulate Images Together"
	bl_description = "Manipulate all images together"

	def draw(self, context):
		self.layout.operator('image.all_rename_image_file_name', icon='PLUGIN')

class EntireProcessPhysicsMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_physics"
	bl_label = "Manipulate Physics Together"
	bl_description = "Manipulate all physics together"

	def draw(self, context):
		self.layout.operator(AllSetPhysicsFrames.bl_idname, icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	RestartBlender,
	RecoverLatestAutoSave,
	SaveMainfileUnmassage,
	LoadLastFile,
	RenameDataBlocks,
	AllOnShowAllEdges,
	AllSetDrawType,
	AllRenameObjectData,
	#AllSetMaterialReceiveTransparent,
	#AllSetMaterialColorRamp,
	AllSetMaterialFreestyleColor,
	AllSetMaterialFreestyleColorByDiffuse,
	AllSetMaterialObjectColor,
	#AllSetBumpMethod,
	AllRenameTextureFileName,
	#FixEmptyTextureUVLayer,
	AllSetPhysicsFrames,
	EntireProcessMenu,
	EntireProcessObjectMenu,
	EntireProcessMaterialMenu,
	EntireProcessTextureMenu,
	EntireProcessImageMenu,
	EntireProcessPhysicsMenu
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
		self.layout.operator(LoadLastFile.bl_idname, icon='PLUGIN')
		self.layout.operator(RecoverLatestAutoSave.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(SaveMainfileUnmassage.bl_idname, icon='PLUGIN')
		self.layout.operator('wm.save_userpref', icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(RestartBlender.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.menu(EntireProcessMenu.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
