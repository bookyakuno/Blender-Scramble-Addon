# 「ユーザー設定」エリア > ヘッダー
# "User Prefences" Area > Header

import bpy
from bpy.props import *
import zipfile, urllib.request, os, sys, re
import csv, codecs
import subprocess
import webbrowser
from xml.dom import minidom
import xml.etree.ElementTree as ElementTree

_KEYMAP_DIC = {
	'Window': ['Window',],
	'Screen': ['Screen', 'Screen Editing', 'Region Context Menu',],
	'View2D': ['View2D',],
	'View2D Buttons List': ['View2D Buttons List',],
	'User Interface': ['User Interface',],
	'3D View': ['3D View', 'Object Mode', 'Mesh', 'Curve', 'Armature', 'Metaball', 'Lattice', 'Font', 'Pose', 'Vertex Paint', 'Weight Paint', 'Paint Vertex Selection (Weight, Vertex)', 'Paint Face Mask (Weight, Vertex, Texture)', 'Sculpt', 'Particle', 'Knife Tool Modal Map', 'Custom Normals Modal Map', 'Bevel Modal Map', 'Paint Stroke Modal', 'Paint Curve', 'Object Non-modal', 'View3D Walk Modal', 'View3D Fly Modal', 'View3D Rotate Modal', 'View3D Move Modal', 'View3D Zoom Modal', 'View3D Dolly Modal', '3D View Generic',],
	'Graph Editor': ['Graph Editor', 'Graph Editor Generic',],
	'Dopesheet': ['Dopesheet', 'Dopesheet Generic',],
	'NLA Channels': ['NLA Channels', 'NLA Editor', 'NLA Generic',],
	'Image': ['Image', 'UV Editor', 'Image Paint', 'Image Generic',],
	'Outliner': ['Outliner',],
	'Node Editor': ['Node Editor', 'Node Generic',],
	'Sequencer': ['Sequencer', 'SequencerCommon', 'SequencerPreview',],
	'File Browser': ['File Browser', 'File Browser Buttons', 'File Browser Main',],
	'Info': ['Info',],
	'Property Editor': ['Property Editor',],
	'Text': ['Text', 'Text Generic',],
	'Console': ['Console',],
	'Clip': ['Clip', 'Clip Editor', 'Clip Graph Editor', 'Clip Dopesheet Editor',],
	'Grease Pencil': ['Grease Pencil', 'Grease Pencil Stroke Edit Mode', 'Grease Pencil Stroke Paint (Draw brush)', 'Grease Pencil Stroke Paint (Fill)', 'Grease Pencil Stroke Paint (Erase)', 'Grease Pencil Stroke Paint (Tint)', 'Grease Pencil Stroke Paint Mode', 'Grease Pencil Stroke Sculpt Mode', 'Grease Pencil Stroke Sculpt (Smooth)', 'Grease Pencil Stroke Sculpt (Thickness)', 'Grease Pencil Stroke Sculpt (Strength)', 'Grease Pencil Stroke Sculpt (Grab)', 'Grease Pencil Stroke Sculpt (Push)', 'Grease Pencil Stroke Sculpt (Twist)', 'Grease Pencil Stroke Sculpt (Pinch)', 'Grease Pencil Stroke Sculpt (Randomize)', 'Grease Pencil Stroke Sculpt (Clone)', 'Grease Pencil Stroke Weight Mode', 'Grease Pencil Stroke Weight (Draw)', 'Grease Pencil Stroke Vertex Mode', 'Grease Pencil Stroke Vertex (Draw)', 'Grease Pencil Stroke Vertex (Blur)', 'Grease Pencil Stroke Vertex (Average)', 'Grease Pencil Stroke Vertex (Smear)', 'Grease Pencil Stroke Vertex (Replace)',],
	'Mask Editing': ['Mask Editing',],
	'Frames': ['Frames',],
	'Markers': ['Markers',],
	'Animation': ['Animation',],
	'Animation Channels': ['Animation Channels',],
	'View3D Gesture Circle': ['View3D Gesture Circle',],
	'Gesture Straight Line': ['Gesture Straight Line',],
	'Gesture Zoom Border': ['Gesture Zoom Border',],
	'Gesture Box': ['Gesture Box',],
	'Standard Modal Map': ['Standard Modal Map',],
	'Transform Modal Map': ['Transform Modal Map',],
	'Eyedropper Modal Map': ['Eyedropper Modal Map',],
	'Eyedropper ColorRamp PointSampling Map': ['Eyedropper ColorRamp PointSampling Map',],
}
# 以下は存在するがパネルでの表示がない項目 (at 2.83)
	#'Clip Time Scrub', 'Gizmos', 'Generic Gizmo',
	#'Generic Gizmo Click Drag', 'Generic Gizmo Drag',
	#'Generic Gizmo Maybe Drag', 'Generic Gizmo Select',
	#'Generic Gizmo Tweak Modal Map', 'Header', 'Time Scrub',
	#'Toolbar Popup', 'View3D Placement Modal Map',


def update_func(self, context):
    # print("my test function", self)
	bpy.ops.ui.search_key_bind()

################
# オペレーター #
################

class ChangeUserPreferencesTab(bpy.types.Operator):
	bl_idname = "ui.change_preferences_tab"
	bl_label = "Switch User Preference Tab"
	bl_description = "Switch user settings tab in turn"
	bl_options = {'REGISTER'}

	is_left : BoolProperty(name="To Left", default=False)

	def execute(self, context):
		tabs = ['INTERFACE', 'THEMES', 'VIEWPORT', 'LIGHTS', 'EDITING', 'ANIMATION', 'ADDONS', 'INPUT', 'NAVIGATION', 'KEYMAP', 'SYSTEM', 'SAVE_LOAD', 'FILE_PATHS', 'EXPERIMENTAL']
		now_tab = context.preferences.active_section
		if (now_tab not in tabs):
			self.report(type={'ERROR'}, message="Active tab is undefined value")
			return {'CANCELLED'}
		if (self.is_left):
			tabs.reverse()
		index = tabs.index(now_tab) + 1
		try:
			context.preferences.active_section = tabs[index]
		except IndexError:
			context.preferences.active_section = tabs[0]
		return {'FINISHED'}

################################
# オペレーター(ショートカット) #
################################

class SearchKeyBind(bpy.types.Operator):
	bl_idname = "ui.search_key_bind"
	bl_label = "Search by Key-Binding"
	bl_description = "Show keymaps which key bindings contain the designated key"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		keymap = context.window_manager.keyconfigs.addon.keymaps['temp'].keymap_items[0]
		if (keymap.type == 'NONE'):
			self.report(type={'ERROR'}, message="Target key is empty")
			return {'CANCELLED'}
		filter_str = keymap.type
		if (not keymap.any):
			if (keymap.shift):
				filter_str = filter_str + " Shift"
			if (keymap.ctrl):
				filter_str = filter_str + " Ctrl"
			if (keymap.alt):
				filter_str = filter_str + " Alt"
			if (keymap.oskey):
				filter_str = filter_str + " oskey"
		else:
			filter_str = filter_str + " Any"
		context.space_data.filter_type = 'KEY'
		context.space_data.filter_text = filter_str
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ClearFilterText(bpy.types.Operator):
	bl_idname = "ui.clear_filter_text"
	bl_label = "Clear Search Shortcuts"
	bl_description = "Set empty value as target key-binding for filtering"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		if (context.space_data.filter_text):
			return True
		return False
	def execute(self, context):
		context.space_data.filter_text = ""
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class CloseKeyMapItems(bpy.types.Operator):
	bl_idname = "ui.close_key_map_items"
	bl_label = "Close All Children"
	bl_description = "Close all kyemap Children"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		for keyconfig in context.window_manager.keyconfigs:
			for keymap in keyconfig.keymaps:
				if (keymap.show_expanded_children):
					return True
				if (keymap.show_expanded_items):
					return True
				for keymap_item in keymap.keymap_items:
					if (keymap_item.show_expanded):
						return True
		return False
	def execute(self, context):
		for keyconfig in context.window_manager.keyconfigs:
			for keymap in keyconfig.keymaps:
				keymap.show_expanded_children = False
				keymap.show_expanded_items = False
				for keymap_item in keymap.keymap_items:
					keymap_item.show_expanded = False
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ShowShortcutHtml(bpy.types.Operator):
	bl_idname = "system.show_shortcut_html"
	bl_label = "Show Shortcut List in Browser"
	bl_description = "Show the page to check assigned shortcuts in browser"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		addonDir = os.path.dirname(__file__)
		keyDatas = dict()
		with codecs.open(os.path.join(addonDir, "ShortcutHtmlKeysData.csv"), 'r', encoding='utf-8') as f:
			reader = csv.reader(f)
			for row in reader:
				name = row[1]
				keyDatas[name] = {}
				keyDatas[name]["key_name"] = row[0]
				keyDatas[name]["key_code"] = row[1]
				keyDatas[name]["shape"] = row[2]
				keyDatas[name]["coords"] = row[3]
				keyDatas[name]["configs"] = dict()
		keyconfigs = context.window_manager.keyconfigs
		for kc in (keyconfigs.user, keyconfigs.addon):
			for km in kc.keymaps:
				for kmi in km.keymap_items:
					if (kmi.type in keyDatas):
						if (not kmi.name):
							continue
						if (km.name in keyDatas[kmi.type]["configs"]):
							keyDatas[kmi.type]["configs"][km.name].append(kmi)
						else:
							keyDatas[kmi.type]["configs"][km.name] = [kmi]
		areaStrings = ""
		for name, data in keyDatas.items():
			title = "<b>【" +data["key_name"]+ " 】</b><br><br>"
			for mapName, cfgs in data["configs"].items():
				title = title + "<b>[" + mapName + "]</b><br>"
				cfgsData = []
				for cfg in cfgs:
					cfgStr = ""
					color = ["0", "0", "0"]
					if (cfg.shift):
						cfgStr = cfgStr + " Shift"
						color[2] = "6"
					if (cfg.ctrl):
						cfgStr = cfgStr + " Ctrl"
						color[1] = "6"
					if (cfg.alt):
						cfgStr = cfgStr + " Alt"
						color[0] = "6"
					if (cfg.oskey):
						cfgStr = cfgStr + " OS"
					if (cfg.key_modifier != 'NONE'):
						cfgStr = cfgStr + " " + cfg.key_modifier
					if (cfgStr):
						cfgStr = "(+" + cfgStr[1:] + ")"
					if (cfg.any):
						cfgStr = "(Always)"
					modifierKeyStr = cfgStr
					if (cfg.name):
						if (cfg.idname == "wm.call_menu"):
							cfgStr = cfgStr + "「" + cfg.properties.name + "」Call Menu"
						elif (cfg.idname == "wm.context_set_enum"):
							cfgStr = cfgStr + "「" + cfg.properties.data_path + "」to「" + cfg.properties.value + "」To Change"
						elif (cfg.idname == "wm.context_toggle"):
							cfgStr = cfgStr + "「" + cfg.properties.data_path + "」switch"
						elif (cfg.idname == "wm.context_toggle_enum"):
							cfgStr = cfgStr + "「" + cfg.properties.data_path + "」to「" + cfg.properties.value_1 + "」And「" + cfg.properties.value_2 + "」To Switch"
						elif (cfg.idname == "wm.context_menu_enum"):
							cfgStr = cfgStr + "「" + cfg.properties.data_path + "」Call Menu"
						else:
							cfgStr = cfgStr + cfg.name
					else:
						cfgStr = cfgStr + cfg.propvalue
					if (not cfg.active):
						cfgStr = "<s>" + cfgStr + "</s>"
					cfgStr = "  <font size='2' color='#" +color[0]+color[1]+color[2]+ "'>" + cfgStr + "</font><br>"
					cfgsData.append([cfgStr, modifierKeyStr])
				cfgsData = sorted(cfgsData, key=lambda i: len(i[1]))
				alreadys = []
				for i in cfgsData:
					if (i[0] not in alreadys):
						title = title + i[0]
						alreadys.append(i[0])
			areaStrings = areaStrings+ '<area href="#" title="' +title+ '" shape="' +data["shape"]+ '" coords="' +data["coords"]+ '">\n'
		file = codecs.open(os.path.join(addonDir, "ShortcutHtmlTemplate.html"), 'r', encoding='utf-8')
		template = file.read()
		file.close()
		template = template.replace("<!-- [AREAS] -->", areaStrings)
		file = codecs.open(os.path.join(addonDir, "ShortcutHtmlTemp.html"), "w", 'utf-8')
		file.write(template)
		file.close()
		webbrowser.open(os.path.join(addonDir, "ShortcutHtmlTemp.html"))
		return {'FINISHED'}

class RegisterLastCommandKeyconfig(bpy.types.Operator):
	bl_idname = "wm.register_last_command_keyconfig"
	bl_label = "Assign Key-Binding to Last Command"
	bl_description = "Assign a designated key binding to the lastly executed command"
	bl_options = {'REGISTER'}

	is_clipboard : BoolProperty(name="Use copied text", options={'HIDDEN'})
	command : StringProperty(name="Command text", options={'HIDDEN'})
	sub_command : StringProperty(name="Additional command text", options={'HIDDEN'})

	def item_callback(self, context):
		names = [k for k in _KEYMAP_DIC.keys()]
		return [(name, name, "", idx) for idx, name in enumerate(names)]
	def item_callback_sub(self, context):
		names = _KEYMAP_DIC[self.key_area]
		return [(name, name, "", idx) for idx, name in enumerate(names)]

	key_area : EnumProperty(items=item_callback, name="Effective Area")
	key_sub_area : EnumProperty(items=item_callback_sub, name="Sub Area")

	# bpy.types.Scene.shift : BoolProperty(update=update_func)
	# bpy.types.Scene.ctrl : BoolProperty(update=update_func, default=True)
	# bpy.types.Scene.alt : BoolProperty(update=update_func)
	# bpy.types.Scene.oskey : BoolProperty(update=update_func)

	def invoke(self, context, event):
		pre_clipboard = context.window_manager.clipboard
		pre_area_type = context.area.type
		context.area.type = 'INFO'
		if (not self.is_clipboard):
			for area in context.screen.areas:
				area.tag_redraw()
			#bpy.ops.info.reports_display_update()
			for i in range(50):
				bpy.ops.info.select_all()
				bpy.ops.info.report_copy()
				if (context.window_manager.clipboard != ""):
					break
			bpy.ops.info.select_all()
		context.area.type = pre_area_type
		commands = context.window_manager.clipboard.split("\n")
		context.window_manager.clipboard = pre_clipboard
		if (commands[-1] == ''):
			commands = commands[:-1]
		if (len(commands) <= 0):
			self.report(type={'ERROR'}, message="Lastly executed command cannot be found")
			return {'CANCELLED'}
		commands.reverse()
		for command in commands:
			if (re.search(r"^bpy\.ops\.wm\.call_menu", command)):
				self.command = 'wm.call_menu'
				self.sub_command = 'name:'+re.search(r'^bpy\.ops\.wm\.call_menu\(name\="([^"]+)"\)$', command).groups()[0]
				break
			elif (re.search(r"^bpy\.ops\.", command)):
				self.command = re.search(r"^bpy\.ops\.([^\(]+)", command).groups()[0]
				#options = re.search(r"\((.*)\)$", command).groups()[0]
				#properties = options.split(",")
				break
			elif (re.search(r"^bpy\.context\.", command)):
				if (re.search(r"True$", command) or re.search(r"False$", command)):
					self.command = 'wm.context_toggle'
					self.sub_command = 'data_path:'+re.search(r"^bpy\.context\.([^ ]+)", command).groups()[0]
				elif (re.search(r" = '[^']+'$", command)):
					self.command = 'wm.context_set_enum'
					self.sub_command = 'data_path:'+re.search(r"^bpy\.context\.([^ ]+)", command).groups()[0]
					self.sub_command = self.sub_command+","+'value:'+re.search(r" = '([^']+)'$", command).groups()[0]
				elif (re.search(r" = \d+$", command)):
					self.command = 'wm.context_set_int'
					self.sub_command = 'data_path:'+re.search(r"^bpy\.context\.([^ ]+)", command).groups()[0]
					self.sub_command = self.sub_command+","+'value:'+re.search(r" = (\d+)$", command).groups()[0]
				elif (re.search(r' = [+-]?(\d*\.\d+|\d+\.?\d*)([eE][+-]?\d+|)\Z$', command)):
					self.command = 'wm.context_set_float'
					self.sub_command = 'data_path:'+re.search(r"^bpy\.context\.([^ ]+)", command).groups()[0]
					self.sub_command = self.sub_command+","+'value:'+re.search(r' = [+-]?(\d*\.\d+|\d+\.?\d*)([eE][+-]?\d+|)\Z$', command).groups()[0]
				else:
					self.report(type={'ERROR'}, message="Failed to extract command strings")
					return {'CANCELLED'}
				break
		else:
			self.report(type={'ERROR'}, message="Failed to extract command strings")
			return {'CANCELLED'}
		return context.window_manager.invoke_props_dialog(self, width=310)
	def draw(self, context):
		row = self.layout.split(factor=0.2)
		row.label(text="Command")
		box = row.box()
		if self.sub_command:
			box.label(text=f'{self.command} + {self.sub_command}')
		else:
			box.label(text=f'{self.command}')
		self.layout.separator()
		row = self.layout.box().row(align=True)
		row.prop(self, 'key_area', text="")
		row.label(text="", icon='TRIA_RIGHT')
		row.prop(self, 'key_sub_area', text="")
		try:
			keymap = context.window_manager.keyconfigs.addon.keymaps['temp']
		except KeyError:
			keymap = context.window_manager.keyconfigs.addon.keymaps.new('temp')
		if (1 <= len(keymap.keymap_items)):
			keymap_item = keymap.keymap_items[0]
		else:
			keymap_item = keymap.keymap_items.new('', 'W', 'PRESS')
		row = self.layout.row(align=True)
		row.prop(keymap_item, 'type', event=True, text="")
		row.prop(keymap_item, 'value', text="")
		row.prop(keymap_item, 'repeat')
		row = self.layout.row(align=True)
		row.prop(keymap_item, 'any', toggle=True)
		row.prop(keymap_item, 'shift', toggle=True)
		row.prop(keymap_item, 'ctrl', toggle=True)
		row.prop(keymap_item, 'alt', toggle=True)
		row.prop(keymap_item, 'oskey', toggle=True)
		row.prop(keymap_item, 'key_modifier', event=True, text="")

	def execute(self, context):
		temp_map = context.window_manager.keyconfigs.addon.keymaps['temp'].keymap_items[0]
		keymap_item = context.window_manager.keyconfigs.user.keymaps[self.key_sub_area].keymap_items.new(self.command, temp_map.type, temp_map.value, any=temp_map.any, shift=temp_map.shift, ctrl=temp_map.ctrl, alt=temp_map.alt, oskey=temp_map.oskey, key_modifier=temp_map.key_modifier, repeat=temp_map.repeat)
		for command in self.sub_command.split(","):
			if (not command):
				continue
			name, value = command.split(":")
			if (re.search(r"^\d+$", value)):
				keymap_item.properties[name] = int(value)
			elif (re.search(r"^[+-]?(\d*\.\d+|\d+\.?\d*)([eE][+-]?\d+|)\Z$", value)):
				keymap_item.properties[name] = float(value)
			else:
				keymap_item.properties[name] = value
		for keyconfig in context.window_manager.keyconfigs:
			for keymap in keyconfig.keymaps:
				keymap.show_expanded_children = False
				keymap.show_expanded_items = False
				for keymap_item in keymap.keymap_items:
					keymap_item.show_expanded = False
		context.window_manager.keyconfigs.user.keymaps[self.key_area].show_expanded_children = True
		context.window_manager.keyconfigs.user.keymaps[self.key_sub_area].show_expanded_children = True
		context.window_manager.keyconfigs.user.keymaps[self.key_sub_area].show_expanded_items = True
		context.window_manager.keyconfigs.user.keymaps[self.key_sub_area].keymap_items[-1].show_expanded = True
		for area in context.screen.areas:
			area.tag_redraw()
		self.report(type={"INFO"}, message="Register the shortcut")
		return {'FINISHED'}

class ShowEmptyShortcuts(bpy.types.Operator):
	bl_idname = "view3d.show_empty_shortcuts"
	bl_label = "Show List of Not-Binded Keys"
	bl_description = "Show a list of keys which are not assigned to any commands in the designated group"
	bl_options = {'REGISTER'}

	def item_callback(self, context):
		names = [k for k in _KEYMAP_DIC.keys()]
		return [(name, name, "", idx) for idx, name in enumerate(names)]

	key_area : EnumProperty(items=item_callback, name="Effective Area")

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		addonDir = os.path.dirname(__file__)
		with open(os.path.join(addonDir, "KeysList.csv"), 'r', encoding='utf-8') as f:
			reader = csv.reader(f)
			if context.preferences.view.language == 'ja_JP':
				key_names = {row[2]:row[0] for row in reader if row[2]!='PLUS'}
			else:
				key_names = {row[2]:row[1] for row in reader}
		keyconfigs = context.window_manager.keyconfigs
		outcome_list = []
		for sub_area in _KEYMAP_DIC[self.key_area]:
			key_binds = {key:None for key in key_names.keys()}
			for keyconfig in (keyconfigs.user, keyconfigs.addon):
				if sub_area in keyconfig.keymaps:
					for item in keyconfig.keymaps[sub_area].keymap_items:
						if (item.type in key_binds) and (item.active):
							if (not item.shift and not item.ctrl and not item.alt and not item.oskey and item.key_modifier == 'NONE'):
								key_binds[item.type] = item.idname
							elif (item.any):
								key_binds[item.type] = item.idname
			non_assigned_keys = [key_names[key] for key, value in key_binds.items() if not value]
			outcome_list.append(f"=== {sub_area} ===\n" + "\n".join(non_assigned_keys))
		bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
		text_area = context.window_manager.windows[-1].screen.areas[-1]
		text_area.type = 'TEXT_EDITOR'
		text_area.spaces[0].text = bpy.data.texts.new(name=f"Non-Assigned Keys at {self.key_area}")
		pre_clipboard = context.window_manager.clipboard
		context.window_manager.clipboard = "\n\n".join(outcome_list)
		override = context.copy()
		override['area'] = text_area
		bpy.ops.text.paste(override)
		bpy.ops.text.jump(override, line=1)
		context.window_manager.clipboard = pre_clipboard
		return {'FINISHED'}

class ImportKeyConfigXml(bpy.types.Operator):
	bl_idname = "file.import_key_config_xml"
	bl_label = "Import Keymap from XML File"
	bl_description = "game reads in XML format"
	bl_options = {'REGISTER'}

	filepath : StringProperty(subtype='FILE_PATH')
	items = [
		('RESET', "Reset", "", 1),
		('ADD', "Add", "", 2),
		]
	mode : EnumProperty(items=items, name="Mode", default='ADD')

	def execute(self, context):
		context.preferences.addons[__name__.partition('.')[0]].preferences.key_config_xml_path = self.filepath
		try:
			tree = ElementTree.parse(self.filepath)
		except:
			self.report(type={'ERROR'}, message="Failed to load XML file")
			return {'CANCELLED'}
		root = tree.getroot()
		if (root.tag != 'BlenderKeyConfig'):
			self.report(type={'ERROR'}, message="This XML file is not for Key Config")
			return {'CANCELLED'}
		try:
			if (root.attrib['Version'] != '1.2'):
				self.report(type={'ERROR'}, message="Only XML files of Version 1.2 can be accepted")
				return {'CANCELLED'}
		except KeyError:
			self.report(type={'ERROR'}, message="Failed to check version of XML file")
			return {'CANCELLED'}
		for key_config_elem in root.findall('KeyConfig'):
			key_config_name = key_config_elem.attrib['name']
			key_config = context.window_manager.keyconfigs[key_config_name]
			for key_map_elem in key_config_elem.findall('KeyMap'):
				key_map_name = key_map_elem.attrib['name']
				key_map = key_config.keymaps[key_map_name]
				if (key_map.is_modal):
					continue
				if (self.mode == 'RESET'):
					for key_map_item in key_map.keymap_items:
						key_map.keymap_items.remove(key_map_item)
				for key_map_item_elem in key_map_elem.findall('KeyMapItem'):
					active = True
					if ('Active' in key_map_item_elem.attrib):
						active = bool(int(key_map_item_elem.attrib['Active']))
					id_name = key_map_item_elem.find('Command').text
					if (not id_name):
						continue
					key_elem = key_map_item_elem.find('Key')
					type = key_elem.text
					if (not type):
						continue
					map_type = 'KEYBOARD'
					if ('Type' in key_elem.attrib):
						map_type = key_elem.attrib['Type']
					value = 'PRESS'
					if ('Value' in key_elem.attrib):
						value = key_elem.attrib['Value']
					if (not type):
						continue
					any = False
					if ('Any' in key_elem.attrib):
						shift, ctrl, alt, any = True, True, True, True
					else:
						shift = False
						if ('Shift' in key_elem.attrib):
							shift = bool(int(key_elem.attrib['Shift']))
						ctrl = False
						if ('Ctrl' in key_elem.attrib):
							ctrl = bool(int(key_elem.attrib['Ctrl']))
						alt = False
						if ('Alt' in key_elem.attrib):
							alt = bool(int(key_elem.attrib['Alt']))
					os = False
					if ('OS' in key_elem.attrib):
						os = bool(int(key_elem.attrib['OS']))
					key_modifier = 'NONE'
					if ('KeyModifier' in key_elem.attrib):
						key_modifier = key_elem.attrib['KeyModifier']
					key_map_item = key_map.keymap_items.new(id_name, type, value, any=any, shift=shift, ctrl=ctrl, alt=alt, oskey=os, key_modifier=key_modifier)
					key_map_item.active = active
					for property_elem in key_map_item_elem.findall('Property'):
						try:
							property_name = property_elem.attrib['Name']
							property_type = property_elem.attrib['Type']
							property_value = property_elem.text
							if (property_type == 'int'):
								key_map_item.properties[property_name] = int(property_value)
							elif (property_type == 'float'):
								key_map_item.properties[property_name] = float(property_value)
							elif (property_type == 'str'):
								key_map_item.properties[property_name] = str(property_value)
							else:
								print("Unknown Type: " + property_type)
						except AttributeError:
							continue
		return {'FINISHED'}
	def invoke(self, context, event):
		self.filepath = context.preferences.addons[__name__.partition('.')[0]].preferences.key_config_xml_path
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

class ExportKeyConfigXml(bpy.types.Operator):
	bl_idname = "file.export_key_config_xml"
	bl_label = "Export Keymap as XML File"
	bl_description = "Export kye bindings as XML file"
	bl_options = {'REGISTER'}

	filepath : StringProperty(subtype='FILE_PATH')

	def execute(self, context):
		context.preferences.addons[__name__.partition('.')[0]].preferences.key_config_xml_path = self.filepath
		data = ElementTree.Element('BlenderKeyConfig', {'Version':'1.2'})
		for keyconfig in [context.window_manager.keyconfigs.user]:
			keyconfig_elem = ElementTree.SubElement(data, 'KeyConfig', {'name':keyconfig.name})
			for keymap in keyconfig.keymaps:
				if (keymap.is_modal):
					continue
				keymap_elem = ElementTree.SubElement(keyconfig_elem, 'KeyMap', {'name':keymap.name})
				for keymap_item in keymap.keymap_items:
					if (keymap_item.idname == ''):
						continue
					attrib = {'name':keymap_item.name}
					if (not keymap_item.active):
						attrib['Active'] = '0'
					keymap_item_elem = ElementTree.SubElement(keymap_elem, 'KeyMapItem', attrib)
					attrib = {}
					if (keymap_item.map_type != 'KEYBOARD'):
						attrib['Type'] = keymap_item.map_type
					if (keymap_item.value != 'PRESS'):
						attrib['Value'] = keymap_item.value
					if (keymap_item.any):
						attrib['Any'] = '1'
					else:
						if (keymap_item.shift):
							attrib['Shift'] = '1'
						if (keymap_item.ctrl):
							attrib['Ctrl'] = '1'
						if (keymap_item.alt):
							attrib['Alt'] = '1'
						if (keymap_item.oskey):
							attrib['OS'] = '1'
						if (keymap_item.key_modifier != 'NONE'):
							attrib['KeyModifier'] = keymap_item.key_modifier
					ElementTree.SubElement(keymap_item_elem, 'Key', attrib).text = keymap_item.type
					ElementTree.SubElement(keymap_item_elem, 'Command').text = keymap_item.idname
					if (keymap_item.properties):
						if (0 < len(keymap_item.properties.keys())):
							for property_name in keymap_item.properties.keys():
								property = keymap_item.properties[property_name]
								property_type = type(property).__name__
								if (property_type == 'IDPropertyGroup'):
									pass
								else:
									if (property != ''):
										property_elem = ElementTree.SubElement(keymap_item_elem, 'Property',
											{'Type':property_type,
											'Name':property_name})
										property_elem.text = str(property)
		string = minidom.parseString(ElementTree.tostring(data, encoding="utf-8")).toprettyxml()
		string = string.replace("</KeyMapItem>", "</KeyMapItem>\n\t\t\t")
		f = codecs.open(self.filepath, 'w', 'utf-8')
		f.write(string)
		f.close()
		return {'FINISHED'}
	def invoke(self, context, event):
		self.filepath = context.preferences.addons[__name__.partition('.')[0]].preferences.key_config_xml_path
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

class MoveKeyBindCategory(bpy.types.Operator):
	bl_idname = "ui.move_key_bind_category"
	bl_label = "Move Expanded Key Binding to Other Categories"
	bl_description = "Move the expanded key binding to other categories"
	bl_options = {'REGISTER', 'UNDO'}

	def item_callback(self, context):
		names = [k for k in _KEYMAP_DIC.keys()]
		return [(name, name, "", idx) for idx, name in enumerate(names)]
	def item_callback_sub(self, context):
		names = _KEYMAP_DIC[self.key_area]
		return [(name, name, "", idx) for idx, name in enumerate(names)]

	key_area : EnumProperty(items=item_callback, name="Move Category")
	key_sub_area : EnumProperty(items=item_callback_sub, name="Sub Area")
	source_delete : BoolProperty(name="Remove Original", default=True)

	@classmethod
	def poll(cls, context):
		for keymap in context.window_manager.keyconfigs.user.keymaps:
			if (not keymap.is_modal):
				for keymap_item in keymap.keymap_items:
					if (keymap_item.show_expanded):
						return True
		return False
	def invoke(self, context, event):
		i = 0
		for keymap in context.window_manager.keyconfigs.user.keymaps:
			if (not keymap.is_modal):
				for keymap_item in keymap.keymap_items:
					if (keymap_item.show_expanded):
						i += 1
		if (2 <= i):
			self.report(type={'ERROR'}, message="Please execute when just one element is expanded")
			return {'CANCELLED'}
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		box = self.layout.box()
		box.label(text="Move to")
		row = box.row(align=True)
		row.prop(self, 'key_area', text="")
		row.label(text="", icon='TRIA_RIGHT')
		row.prop(self, 'key_sub_area', text="")
		row = self.layout.row()
		row.use_property_split =True
		row.prop(self, 'source_delete')

	def execute(self, context):
		for keymap in context.window_manager.keyconfigs.user.keymaps:
			if (not keymap.is_modal):
				for keymap_item in keymap.keymap_items:
					if (keymap_item.show_expanded):
						target_keymap = context.window_manager.keyconfigs.user.keymaps[self.key_sub_area]
						target_keymap_item = target_keymap.keymap_items.new(
							idname=keymap_item.idname,
							type=keymap_item.type,
							value=keymap_item.value,
							any=keymap_item.any,
							shift=keymap_item.shift,
							ctrl=keymap_item.ctrl,
							alt=keymap_item.alt,
							oskey=keymap_item.oskey,
							key_modifier=keymap_item.key_modifier)
						for property_name in keymap_item.properties.keys():
							target_keymap_item.properties[property_name] = keymap_item.properties[property_name]
						if self.source_delete:
							keymap.keymap_items.remove(keymap_item)
						context.window_manager.keyconfigs.user.keymaps[self.key_area].show_expanded_children = True
						target_keymap.show_expanded_children = True
						target_keymap.show_expanded_items = True
						target_keymap_item.show_expanded = True
						break
				else:
					continue
				break
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

##########################
# オペレーター(アドオン) #
##########################

class UpdateScrambleAddon(bpy.types.Operator):
	bl_idname = "script.update_scramble_addon"
	bl_label = "Update Scramble Addon"
	bl_description = "Download 'Scramble Addon' and update to it"
	bl_options = {'REGISTER'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		pass

	def execute(self, context):
		response = urllib.request.urlopen("https://github.com/bookyakuno/Blender-Scramble-Addon/archive/master.zip")
		tempDir = bpy.app.tempdir
		zipPath = os.path.join(tempDir, "scramble_addon.zip")
		addonDir = os.path.dirname(__file__)
		f = open(zipPath, "wb")
		f.write(response.read())
		f.close()
		zf = zipfile.ZipFile(zipPath, "r")
		for f in zf.namelist():
			if not os.path.basename(f):
				pass
			else:
				if ("scramble_addon" in f):
					uzf = open(os.path.join(addonDir, os.path.basename(f)), 'wb')
					uzf.write(zf.read(f))
					uzf.close()
		zf.close()
		self.report(type={"INFO"}, message="Update completed. Please restart Blender")
		return {'FINISHED'}

class ToggleDisabledMenu(bpy.types.Operator):
	bl_idname = "wm.toggle_disabled_menu"
	bl_label = "Toggle Display of 'On/Off Additional Items'"
	bl_description = "Show or hide 'turn on/off additional items' buttons displayed at end of menus added by the add-on"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu = not context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# サブメニュー #
################

class InputMenu(bpy.types.Menu):
	bl_idname = "USERPREF_MT_header_input"
	bl_label = "Keymap"
	bl_description = "Functions to manipulate key bindings"

	def draw(self, context):
		self.layout.operator(ShowShortcutHtml.bl_idname, icon="PLUGIN")
		self.layout.operator(ShowEmptyShortcuts.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RegisterLastCommandKeyconfig.bl_idname, icon="PLUGIN").is_clipboard = False
		self.layout.operator(RegisterLastCommandKeyconfig.bl_idname, text="Assign Key-Binding to Command in Clipboard", icon="PLUGIN").is_clipboard = True
		self.layout.separator()
		self.layout.operator(ImportKeyConfigXml.bl_idname, icon="PLUGIN")
		self.layout.operator(ExportKeyConfigXml.bl_idname, icon="PLUGIN")

class AddonsMenu(bpy.types.Menu):
	bl_idname = "USERPREF_MT_header_scramble_addon"
	bl_label = "Scramble Addon"
	bl_description = "Functions to manipulate scramble Addon"

	def draw(self, context):
		self.layout.operator(ToggleDisabledMenu.bl_idname, icon="PLUGIN")
		self.layout.operator(UpdateScrambleAddon.bl_idname, icon="PLUGIN")

################
# クラスの登録 #
################

classes = [
	ChangeUserPreferencesTab,
	SearchKeyBind,
	ClearFilterText,
	CloseKeyMapItems,
	ShowShortcutHtml,
	RegisterLastCommandKeyconfig,
	ShowEmptyShortcuts,
	ImportKeyConfigXml,
	ExportKeyConfigXml,
	MoveKeyBindCategory,
	UpdateScrambleAddon,
	ToggleDisabledMenu,
	InputMenu,
	AddonsMenu
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
		row.alignment = "CENTER"
		row.operator(ChangeUserPreferencesTab.bl_idname, icon='TRIA_UP', text="").is_left = True
		row.operator(ChangeUserPreferencesTab.bl_idname, icon='TRIA_DOWN', text="").is_left = False
		active_section = context.preferences.active_section
		if (active_section == 'KEYMAP'):
			row = self.layout.row(align=True)
			row.menu(InputMenu.bl_idname, icon="PLUGIN")
			row.operator(CloseKeyMapItems.bl_idname, icon='FULLSCREEN_EXIT', text="")
			row.operator(MoveKeyBindCategory.bl_idname, icon='NODETREE', text="")
			self.layout.separator()
			try:
				keymap = context.window_manager.keyconfigs.addon.keymaps['temp']
			except KeyError:
				keymap = context.window_manager.keyconfigs.addon.keymaps.new('temp')
			if (1 <= len(keymap.keymap_items)):
				keymap_item = keymap.keymap_items[0]
			else:
				keymap_item = keymap.keymap_items.new('', 'W', 'PRESS')
			self.layout.label(text="Search by Key-Binding")
			row = self.layout.row(align=True)
			row.prop(keymap_item, 'type', event=True, text="")
			row.operator(SearchKeyBind.bl_idname, icon="VIEWZOOM", text="")
			row.operator(ClearFilterText.bl_idname, icon='X', text="")
			row = self.layout.row(align=True)
			row.prop(keymap_item, 'any', toggle=True)
			row.prop(keymap_item, 'shift', toggle=True)
			row.prop(keymap_item, 'ctrl', toggle=True)
			row.prop(keymap_item, 'alt', toggle=True)
			row.prop(keymap_item, 'oskey', toggle=True)

		elif (active_section == 'ADDONS'):
			self.layout.menu(AddonsMenu.bl_idname, icon="PLUGIN")

	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
