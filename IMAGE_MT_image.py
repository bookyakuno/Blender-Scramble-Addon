# 「UV/画像エディター」エリア > 「画像」メニュー
# "UV/Image Editor" Area > "Image" Menu

import bpy
import os, numpy, urllib, math
from bpy.props import *

################
# オペレーター #
################

class RenameImageFileName(bpy.types.Operator):
	bl_idname = "image.rename_image_file_name"
	bl_label = "Image name from file name"
	bl_description = "External images are using name of active image file name"
	bl_options = {'REGISTER', 'UNDO'}

	isExt : BoolProperty(name="Include Extension", default=True)

	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (context.edit_image.filepath == ""):
			return False
		return True
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		name = bpy.path.basename(img.filepath_raw)
		if (not self.isExt):
			name, ext = os.path.splitext(name)
		try:
			img.name = name
		except: pass
		return {'FINISHED'}

class AllRenameImageFileName(bpy.types.Operator):
	bl_idname = "image.all_rename_image_file_name"
	bl_label = "Change all image names to used file name"
	bl_description = "names of all images using external image file name"
	bl_options = {'REGISTER', 'UNDO'}

	isExt : BoolProperty(name="Include Extension", default=True)

	@classmethod
	def poll(cls, context):
		if (len(bpy.data.images) <= 0):
			return False
		for img in bpy.data.images:
			if (img.filepath != ""):
				return True
		return False
	def execute(self, context):
		for img in  bpy.data.images:
			name = bpy.path.basename(img.filepath_raw)
			if (not self.isExt):
				name, ext = os.path.splitext(name)
			try:
				img.name = name
			except: pass
		return {'FINISHED'}

class ReloadAllImage(bpy.types.Operator):
	bl_idname = "image.reload_all_image"
	bl_label = "Reload All Images"
	bl_description = "Reloads all image data referring to external file"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (len(bpy.data.images) <= 0):
			return False
		for img in bpy.data.images:
			if (img.filepath != ""):
				return True
		return False
	def execute(self, context):
		for img in bpy.data.images:
			if (img.filepath != ""):
				img.reload()
				try:
					img.update()
				except RuntimeError:
					pass
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class FillOverrideColor(bpy.types.Operator):
	bl_idname = "image.fill_override_color"
	bl_label = "Override Color"
	bl_description = "All over colors you specify active image"
	bl_options = {'REGISTER', 'UNDO'}

	color : FloatVectorProperty(name="Color", description="Fill Color", default=(1, 1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR_GAMMA', size=4)

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	def execute(self, context):
		img = context.edit_image
		pixel = list(self.color[:3])
		if (4 <= img.channels):
			pixel.append(self.color[-1])
		img.pixels = pixel * (img.size[0] * img.size[1])
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class FillColor(bpy.types.Operator):
	bl_idname = "image.fill_color"
	bl_label = "Fill With Color"
	bl_description = "Fill with color image active all"
	bl_options = {'REGISTER', 'UNDO'}

	color : FloatVectorProperty(name="Color", description="Fill Color", default=(1, 1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR_GAMMA', size=4)

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		img = context.edit_image
		color = self.color[:3]
		alpha = self.color[-1]
		unalpha = 1.0 - alpha
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height * img_width, img_channel)
		pixels[:,0] = (pixels[:,0] * unalpha) + (color[0] * alpha)
		pixels[:,1] = (pixels[:,1] * unalpha) + (color[1] * alpha)
		pixels[:,2] = (pixels[:,2] * unalpha) + (color[2] * alpha)
		img.pixels = pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class FillTransparency(bpy.types.Operator):
	bl_idname = "image.fill_transparency"
	bl_label = "Fill Transparent"
	bl_description = "transparent parts of image are active in specified color fills"
	bl_options = {'REGISTER', 'UNDO'}

	color : FloatVectorProperty(name="Fill Color", default=(1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR_GAMMA')

	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (len(context.edit_image.pixels) <= 0):
			return False
		if (context.edit_image.channels < 4):
			return False
		return True
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		color = self.color[:]
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		if (4 <= img_channel):
			alphas = pixels[:,:,3]
			unalphas = 1.0 - alphas
		else:
			alphas = numpy.ones(img_height * img_width)
			unalphas = numpy.zeros(img_height * img_width)
		pixels[:,:,0]= (pixels[:,:,0] * alphas) + (color[0] * unalphas)
		pixels[:,:,1]= (pixels[:,:,1] * alphas) + (color[1] * unalphas)
		pixels[:,:,2]= (pixels[:,:,2] * alphas) + (color[2] * unalphas)
		pixels[:,:,3] = 1.0
		img.pixels = pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Normalize(bpy.types.Operator):
	bl_idname = "image.normalize"
	bl_label = "Normalize Image"
	bl_description = "Normalize Active Image"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		rs = pixels[:,:,0]
		gs = pixels[:,:,1]
		bs = pixels[:,:,2]
		values = (rs + gs + bs) / 3
		min = numpy.amin(values)
		max = numpy.amax(values)
		multi = 1 / (max - min)
		for c in range(3):
			pixels[:,:,c] = (pixels[:,:,c] - min) * multi
		img.pixels = pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class RenameImageFile(bpy.types.Operator):
	bl_idname = "image.rename_image_file"
	bl_label = "Change name of image file"
	bl_description = "Change file name of active image"
	bl_options = {'REGISTER'}

	new_name : StringProperty(name="New File Name")

	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (context.edit_image.filepath == ""):
			return False
		return True
	def invoke(self, context, event):
		self.new_name = bpy.path.basename(context.edit_image.filepath_raw)
		if (self.new_name == ""):
			self.report(type={"ERROR"}, message="External file does not exist in this image")
			return {"CANCELLED"}
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		pre_filepath = context.edit_image.filepath_raw
		dir = os.path.dirname(bpy.path.abspath(context.edit_image.filepath_raw))
		name = bpy.path.basename(context.edit_image.filepath_raw)
		if (self.new_name == name):
			self.report(type={"ERROR"}, message="image file name is same as original")
			return {"CANCELLED"}
		bpy.ops.image.save_as(filepath=os.path.join(dir, self.new_name))
		context.edit_image.name = self.new_name
		os.remove(bpy.path.abspath(pre_filepath))
		return {'FINISHED'}

# ながとさんに協力して頂きました、感謝！
class BlurImage(bpy.types.Operator):
	bl_idname = "image.blur_image"
	bl_label = "Blur image (Note heavy)"
	bl_description = "Blur Active Image"
	bl_options = {'REGISTER', 'UNDO'}

	strength : IntProperty(name="Blur Strength", default=10, min=1, max=100, soft_min=1, soft_max=100)

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		img = context.edit_image
		w, h, c = img.size[0], img.size[1], img.channels
		ps = numpy.array(img.pixels)
		lengthes = []
		for i in range(999):
			length = 2 ** i
			lengthes.append(length)
			if (self.strength < sum(lengthes)):
				lengthes[-1] -= sum(lengthes) - self.strength
				if (2 <= len(lengthes)):
					if (lengthes[-1] == 0):
						lengthes = lengthes[:-1]
					elif (lengthes[-1] <= lengthes[-2] / 2):
						lengthes[-2] += lengthes[-1]
						lengthes = lengthes[:-1]
				break
		divisor = 16 ** len(lengthes)
		for length in lengthes:
			for (dx, dy, endX, endY) in [(w*c, c, h, w), (c, w*c, w, h)]:
				for (start, end, sign) in [(0, endX, 1), (endX-1, -1, -1)]:
					dir  = sign * dx
					diff = dir * length
					for y in range(0, dy*endY, dy):
						for x in range(start*dx, end*dx - diff, dir):
							for i in range(y + x, y + x + c):
								ps[i] = ps[i] + ps[i + diff]
						for x in range(end*dx - diff, end*dx, dir):
							for i in range(y + x, y + x + c):
								ps[i] = ps[i] * 2
		for y in range(0, h*w*c, w*c):
			for x in range(0, w*c, c):
				for i in range(y + x, y + x + c):
					ps[i] = ps[i] / divisor
		img.pixels = ps.tolist()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ReverseWidthImage(bpy.types.Operator):
	bl_idname = "image.reverse_width_image"
	bl_label = "Flip Horizontally"
	bl_description = "Reverse this image horizontally"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		#for i in range(img_height):
		#	pixels[i] = pixels[i][::-1]
		pixels[:,:] = pixels[:,::-1]
		img.pixels = pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ReverseHeightImage(bpy.types.Operator):
	bl_idname = "image.reverse_height_image"
	bl_label = "Flip Vertically"
	bl_description = "Reverse this image verticaliy"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		pixels = pixels[::-1]
		img.pixels = pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Rotate90Image(bpy.types.Operator):
	bl_idname = "image.rotate_90_image"
	bl_label = "Rotate 90 Degrees"
	bl_description = "Rotate active image 90 degrees"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		new_pixels = numpy.zeros((img_width, img_height, img_channel))
		for y in range(img_height):
			new_pixels[:,y,:] = pixels[y,::-1,:]
		img.scale(img_height, img_width)
		img.pixels = new_pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Rotate180Image(bpy.types.Operator):
	bl_idname = "image.rotate_180_image"
	bl_label = "Rotate 180 Degrees"
	bl_description = "Rotate active image 180 degrees"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		pixels[:,:] = pixels[:,::-1]
		pixels = pixels[::-1]
		img.pixels = pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Rotate270Image(bpy.types.Operator):
	bl_idname = "image.rotate_270_image"
	bl_label = "Rotate 270 Degrees"
	bl_description = "Rotate active image 270 degrees"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		new_pixels = numpy.zeros((img_width, img_height, img_channel))
		for y in range(img_height):
			new_pixels[:,y,:] = pixels[-y-1,:,:]
		img.scale(img_height, img_width)
		img.pixels = new_pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ExternalEditEX(bpy.types.Operator):
	bl_idname = "image.external_edit_ex"
	bl_label = "Edit by external editor (Advance)"
	bl_description = "Open image in an external editor of additional files page of custom"
	bl_options = {'REGISTER', 'UNDO'}

	index : IntProperty(name="Number of Use", default=1, min=1, max=3, soft_min=1, soft_max=3)

	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (context.edit_image.filepath == ""):
			return False
		return True

	def execute(self, context):
		img = context.edit_image
		path = bpy.path.abspath(img.filepath)
		pre_path = context.preferences.filepaths.image_editor
		if (self.index == 1):
			context.preferences.filepaths.image_editor = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.image_editor_path_1
		elif (self.index == 2):
			context.preferences.filepaths.image_editor = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.image_editor_path_2
		elif (self.index == 3):
			context.preferences.filepaths.image_editor = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.image_editor_path_3
		bpy.ops.image.external_edit(filepath=path)
		context.preferences.filepaths.image_editor = pre_path
		return {'FINISHED'}

class Resize(bpy.types.Operator):
	bl_idname = "image.resize"
	bl_label = "Resize Image"
	bl_description = "Resize Active Image"
	bl_options = {'REGISTER', 'UNDO'}

	def width_update(self, context):
		if (self.keep_ratio):
			img = bpy.context.edit_image
			w, h = img.size[0], img.size[1]
			ratio = w / h
			new_height = round(self.width / ratio)
			if self.height != new_height:
				self.height = new_height
		return None
	def height_update(self, context):
		if (self.keep_ratio):
			img = bpy.context.edit_image
			w, h = img.size[0], img.size[1]
			ratio = w / h
			new_width = round(self.height * ratio)
			if self.width != new_width:
				self.width = new_width
		return None

	width : IntProperty(name="Width", default=0, min=1, max=8192, soft_min=1, soft_max=8192, step=1, subtype='PIXEL', update=width_update)
	height : IntProperty(name="Height", default=0, min=1, max=8192, soft_min=1, soft_max=8192, step=1, subtype='PIXEL', update=height_update)
	keep_ratio : BoolProperty(name="Keep Ratio", default=True)

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def invoke(self, context, event):
		img = context.edit_image
		self.width, self.height = img.size[0], img.size[1]
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		img.scale(self.width, self.height)
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Duplicate(bpy.types.Operator):
	bl_idname = "image.duplicate"
	bl_label = "Copy Image"
	bl_description = "Duplicate Active Image"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def execute(self, context):
		src = context.edit_image
		new = bpy.data.images.new(
			name = src.name,
			width = src.size[0],
			height = src.size[1],
			float_buffer = src.is_float,
			stereo3d = src.is_stereo_3d)
		for name in dir(src):
			if (name == 'pixels'):
				new.pixels = src.pixels[:]
				continue
			elif (name == 'name'):
				#new.name = src.name + "_copy"
				continue
			elif (name not in ['packed_files', 'packed_file', 'pack', 'mapping']):
				continue
			elif (name[0] != '_' and 'rna' not in name):
				value = src.__getattribute__(name)
				try:
					new.__setattr__(name, value[:])
				except AttributeError:
					pass
				except TypeError:
					try:
						new.__setattr__(name, value)
					except:
						pass
		context.space_data.image = new
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class NewUVChecker(bpy.types.Operator):
	bl_idname = "image.new_uv_checker"
	bl_label = "New UV Grid"
	bl_description = "UV grid to download from WEB, and create new images"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('UVCheckerMap01-1024.png', "01 (1024x1024)", "", 1),
		('UVCheckerMap02-1024.png', "02 (1024x1024)", "", 2),
		('UVCheckerMap03-1024.png', "03 (1024x1024)", "", 3),
		('UVCheckerMap04-1024.png', "04 (1024x1024)", "", 4),
		('UVCheckerMap05-1024.png', "05 (1024x1024)", "", 5),
		('UVCheckerMap06-1024.png', "06 (1024x1024)", "", 6),
		('UVCheckerMap07-1024.png', "07 (1024x1024)", "", 7),
		('UVCheckerMap08-1024.png', "08 (1024x1024)", "", 8),
		('UVCheckerMap09-1024.png', "09 (1024x1024)", "", 9),
		('UVCheckerMap10-1024.png', "10 (1024x1024)", "", 10),
		('UVCheckerMap11-1024.png', "11 (1024x1024)", "", 11),
		('UVCheckerMap12-1024.png', "12 (1024x1024)", "", 12),
		('UVCheckerMap13-1024.png', "13 (1024x1024)", "", 13),
		('UVCheckerMap14-1024.png', "14 (1024x1024)", "", 14),
		('UVCheckerMap15-1024.png', "15 (1024x1024)", "", 15),
		('UVCheckerMap16-1024.png', "16 (1024x1024)", "", 16),
		('UVCheckerMap17-1024.png', "17 (1024x1024)", "", 17),
		('UVCheckerMap01-512.png', "01 (512x512)", "", 18),
		('UVCheckerMap02-512.png', "02 (512x512)", "", 19),
		('UVCheckerMap03-512.png', "03 (512x512)", "", 20),
		('UVCheckerMap04-512.png', "04 (512x512)", "", 21),
		('UVCheckerMap05-512.png', "05 (512x512)", "", 22),
		('UVCheckerMap06-512.png', "06 (512x512)", "", 23),
		('UVCheckerMap07-512.png', "07 (512x512)", "", 24),
		('UVCheckerMap08-512.png', "08 (512x512)", "", 25),
		('UVCheckerMap09-512.png', "09 (512x512)", "", 26),
		('UVCheckerMap10-512.png', "10 (512x512)", "", 27),
		('UVCheckerMap11-512.png', "11 (512x512)", "", 28),
		('UVCheckerMap12-512.png', "12 (512x512)", "", 29),
		('UVCheckerMap13-512.png', "13 (512x512)", "", 30),
		('UVCheckerMap14-512.png', "14 (512x512)", "", 31),
		('UVCheckerMap15-512.png', "15 (512x512)", "", 32),
		('UVCheckerMap16-512.png', "16 (512x512)", "", 33),
		('UVCheckerMap17-512.png', "17 (512x512)", "", 34),
		]
	image_name : EnumProperty(items=items, name="Image File")
	name : StringProperty(name="Name", default="UVCheckerMap")

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		base_url = "https://raw.githubusercontent.com/Arahnoid/UVChecker-map/master/UVCheckerMaps/"
		temp_path = os.path.join(bpy.app.tempdir, self.name)
		url = base_url + self.image_name
		opener = urllib.request.build_opener()
		try:
			httpres = opener.open(url)
		except urllib.error.HTTPError:
			self.report(type={'ERROR'}, message="Failed to download file")
			return {'CANCELLED'}
		with open(temp_path, 'wb') as file:
			file.write(httpres.read())
		bpy.ops.image.open(filepath=temp_path)
		bpy.ops.image.pack()
		context.space_data.image.filepath = ""
		os.remove(temp_path)
		return {'FINISHED'}

class Tiles(bpy.types.Operator):
	bl_idname = "image.tiles"
	bl_label = "Tile Image"
	bl_description = "Array and scale-down active image"
	bl_options = {'REGISTER', 'UNDO'}

	count : IntProperty(name="Number of Tile", default=2, min=2, max=8, soft_min=2, soft_max=8)

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, count):
		row = self.layout.split(factor=0.3)
		sp = row.split(factor=0.2)
		sp.label(text="")
		sp.label(text="Number of Tiles")
		row.prop(self, "count", text="")
		row.label(text=f" * {self.count} = {self.count * self.count}")

	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		small_w_f = img_width / self.count
		small_h_f = img_height / self.count
		small_w = math.ceil(small_w_f)
		small_h = math.ceil(small_h_f)
		img.scale(small_w, small_h)
		small_pixels = numpy.array(img.pixels).reshape(small_h, small_w, img_channel)
		img.scale(img_width, img_height)
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		for y in range(self.count):
			for x in range(self.count):
				min_x = round(x * small_w_f)
				max_x = round((x + 1) * small_w_f)
				min_y = round(y * small_h_f)
				max_y = round((y + 1) * small_h_f)
				w, h = max_x - min_x, max_y - min_y
				pixels[min_y:max_y,min_x:max_x,:] = small_pixels[:h,:w,:]
		img.pixels = pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ResizeBlur(bpy.types.Operator):
	bl_idname = "image.resize_blur"
	bl_label = "Blur Image Fast"
	bl_description = "active image blur fast do"
	bl_options = {'REGISTER', 'UNDO'}

	size : FloatProperty(name="Strength", default=50, min=1, max=99, soft_min=1, soft_max=99, step=0, precision=0, subtype='PERCENTAGE')
	count : IntProperty(name="Count", default=10, min=1, max=100, soft_min=1, soft_max=100)

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		img = context.edit_image
		img_w, img_h = img.size[0], img.size[1]
		small_w = round(img_w * (100 - self.size) * 0.01)
		small_h = round(img_h * (100 - self.size) * 0.01)
		for i in range(self.count):
			img.scale(small_w, small_h)
			img.scale(img_w, img_h)
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class NewNoise(bpy.types.Operator):
	bl_idname = "image.new_noise"
	bl_label = "Create new noise image"
	bl_description = "Add new noise image"
	bl_options = {'REGISTER', 'UNDO'}

	monochrome : BoolProperty(name="Decolor Noise", default=False)
	alpha_noise : BoolProperty(name="Alpha Noise", default=False)
	name : StringProperty(name="Name", default="Noise")
	width : IntProperty(name="Width", default=1024, min=1, max=8192, soft_min=1, soft_max=8192)
	height : IntProperty(name="Height", default=1024, min=1, max=8192, soft_min=1, soft_max=8192)
	alpha : BoolProperty(name="Alpha", default=True)
	float_buffer : BoolProperty(name="32-bit Float", default=False)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		img = bpy.data.images.new(self.name, self.width, self.height, alpha=self.alpha, float_buffer=self.float_buffer)
		width, height, channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(width, height, channel)
		if (self.monochrome):
			values = numpy.random.rand(width, height)
			pixels[:,:,0] = values.copy()
			pixels[:,:,1] = values.copy()
			pixels[:,:,2] = values.copy()
		else:
			pixels[:,:,0] = numpy.random.rand(width, height)
			pixels[:,:,1] = numpy.random.rand(width, height)
			pixels[:,:,2] = numpy.random.rand(width, height)
		if (self.alpha_noise):
			if (4 <= channel):
				pixels[:,:,3] = numpy.random.rand(width, height)
		img.pixels = pixels.flatten()
		img.gl_free()
		context.space_data.image = img
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Decolorization(bpy.types.Operator):
	bl_idname = "image.decolorization"
	bl_label = "Decolorize"
	bl_description = "This decolor active image"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height * img_width, img_channel)
		values = (pixels[:,0] + pixels[:,1] + pixels[:,2]) / 3
		pixels[:,0] = values.copy()
		pixels[:,1] = values.copy()
		pixels[:,2] = values.copy()
		img.pixels = pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Clipping(bpy.types.Operator):
	bl_idname = "image.clipping"
	bl_label = "Change size of image"
	bl_description = "Change size active image"
	bl_options = {'REGISTER', 'UNDO'}

	width : IntProperty(name="Width", default=1024, min=1, max=8192, soft_min=1, soft_max=8192)
	height : IntProperty(name="Height", default=1024, min=1, max=8192, soft_min=1, soft_max=8192)
	items = [
		('LEFT', "Left", "", 1),
		('CENTER', "Center", "", 2),
		('RIGHT', "Right", "", 3),
		]
	width_align : EnumProperty(items=items, name="Horizontal Position")
	items = [
		('UP', "Up", "", 1),
		('CENTER', "Center", "", 2),
		('DOWN', "Down", "", 3),
		]
	height_align : EnumProperty(items=items, name="Vertical Position")
	fill_color : FloatVectorProperty(name="Fill Color", default=(1, 1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=3, precision=2, subtype='COLOR_GAMMA', size=4)

	@classmethod
	def poll(cls, context):
		if 'edit_image' in dir(context):
			if context.edit_image:
				if len(context.edit_image.pixels):
					return True
		return False

	def invoke(self, context, event):
		img = context.edit_image
		self.width, self.height = img.size[0], img.size[1]
		return context.window_manager.invoke_props_dialog(self, width=400)

	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		new = numpy.empty([self.height, self.width, img_channel])
		new[:,:] = self.fill_color[:img_channel]
		new_w_min, new_w_max, w_min, w_max = None, None, None, None
		if (self.width < img_width):
			if (self.width_align == 'LEFT'):
				w_max = self.width
			elif (self.width_align == 'CENTER'):
				i = int((img_width - self.width) / 2)
				w_min = i
				w_max = i + self.width
			elif (self.width_align == 'RIGHT'):
				w_min = img_width - self.width
		elif (img_width < self.width):
			if (self.width_align == 'LEFT'):
				new_w_max = img_width
			elif (self.width_align == 'CENTER'):
				i = int((self.width - img_width) / 2)
				new_w_min = i
				new_w_max = i + img_width
			elif (self.width_align == 'RIGHT'):
				new_w_min = self.width - img_width
		new_h_min, new_h_max, h_min, h_max = None, None, None, None
		if (self.height < img_height):
			if (self.height_align == 'UP'):
				h_min = img_height - self.height
			elif (self.height_align == 'CENTER'):
				i = int((img_height - self.height) / 2)
				h_min = i
				h_max = i + self.height
			elif (self.height_align == 'DOWN'):
				h_max = self.height
		elif (img_height < self.height):
			if (self.height_align == 'UP'):
				new_h_max = img_height
			elif (self.height_align == 'CENTER'):
				i = int((self.height - img_height) / 2)
				new_h_min = i
				new_h_max = i + img_height
			elif (self.height_align == 'DOWN'):
				new_h_min = self.height - img_height
		new[new_h_min:new_h_max,new_w_min:new_w_max] = pixels[h_min:h_max,w_min:w_max]
		pixels = new
		img.scale(self.width, self.height)
		img.pixels = pixels.flatten()
		img.gl_free()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# サブメニュー #
################

class TransformMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_image_transform"
	bl_label = "Transform"
	bl_description = "Image Transform Menu"

	def draw(self, context):
		self.layout.operator(ReverseWidthImage.bl_idname, icon='PLUGIN')
		self.layout.operator(ReverseHeightImage.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(Rotate90Image.bl_idname, icon='PLUGIN')
		self.layout.operator(Rotate180Image.bl_idname, icon='PLUGIN')
		self.layout.operator(Rotate270Image.bl_idname, icon='PLUGIN')

class ExternalEditEXMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_image_external_edit_ex"
	bl_label = "External Editor (Extra)"

	def draw(self, context):
		prefs = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
		if (prefs.image_editor_path_1):
			path = os.path.basename(prefs.image_editor_path_1)
			name, ext = os.path.splitext(path)
			self.layout.operator(ExternalEditEX.bl_idname, icon='PLUGIN', text=name).index = 1
		if (prefs.image_editor_path_2):
			path = os.path.basename(prefs.image_editor_path_2)
			name, ext = os.path.splitext(path)
			self.layout.operator(ExternalEditEX.bl_idname, icon='PLUGIN', text=name).index = 2
		if (prefs.image_editor_path_3):
			path = os.path.basename(prefs.image_editor_path_3)
			name, ext = os.path.splitext(path)
			self.layout.operator(ExternalEditEX.bl_idname, icon='PLUGIN', text=name).index = 3

class FillMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_image_fill"
	bl_label = "Paint"

	def draw(self, context):
		self.layout.operator(FillOverrideColor.bl_idname, icon='PLUGIN', text="Override")
		self.layout.operator(FillColor.bl_idname, icon='PLUGIN', text="Paint Out")
		self.layout.operator(FillTransparency.bl_idname, icon='PLUGIN', text="Fill Transparent")

class NewMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_image_new"
	bl_label = "New Images (Extra)"

	def draw(self, context):
		self.layout.operator(NewUVChecker.bl_idname, icon='PLUGIN', text="UV Grid")
		self.layout.operator(NewNoise.bl_idname, icon='PLUGIN', text="Noise")

class ColorMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_image_color"
	bl_label = "Color"

	def draw(self, context):
		self.layout.operator(Normalize.bl_idname, icon='PLUGIN', text="Normalize")
		self.layout.operator(Decolorization.bl_idname, icon='PLUGIN', text="Decolorization")

class EditMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_image_edit"
	bl_label = "Edit"

	def draw(self, context):
		self.layout.operator(Duplicate.bl_idname, icon='PLUGIN', text="Copy")
		self.layout.operator(Clipping.bl_idname, icon='PLUGIN', text="Change Size")
		self.layout.operator(Resize.bl_idname, icon='PLUGIN', text="Scale")
		self.layout.operator(Tiles.bl_idname, icon='PLUGIN', text="Tile")

class FilterMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_image_filter"
	bl_label = "Filter"

	def draw(self, context):
		self.layout.operator(ResizeBlur.bl_idname, icon='PLUGIN', text="Blur (high Speed)")
		self.layout.operator(BlurImage.bl_idname, icon='PLUGIN', text="Blur (slow)")

################
# クラスの登録 #
################

classes = [
	RenameImageFileName,
	AllRenameImageFileName,
	ReloadAllImage,
	FillOverrideColor,
	FillColor,
	FillTransparency,
	Normalize,
	RenameImageFile,
	BlurImage,
	ReverseWidthImage,
	ReverseHeightImage,
	Rotate90Image,
	Rotate180Image,
	Rotate270Image,
	ExternalEditEX,
	Resize,
	Duplicate,
	NewUVChecker,
	Tiles,
	ResizeBlur,
	NewNoise,
	Decolorization,
	Clipping,
	TransformMenu,
	ExternalEditEXMenu,
	FillMenu,
	NewMenu,
	ColorMenu,
	EditMenu,
	FilterMenu
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
		self.layout.menu(NewMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(ExternalEditEXMenu.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.menu(EditMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(ColorMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(FillMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(TransformMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(FilterMenu.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(RenameImageFile.bl_idname, icon='PLUGIN')
		self.layout.operator(RenameImageFileName.bl_idname, icon='PLUGIN')
		self.layout.operator(AllRenameImageFileName.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(ReloadAllImage.bl_idname, icon='PLUGIN')
	if (bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
