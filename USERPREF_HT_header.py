# 「ユーザー設定」エリア > ヘッダー
# "User Prefences" Area > Header

import bpy
import zipfile, urllib.request, os, sys, re
import csv, codecs
import collections
import subprocess
import webbrowser
from xml.dom import minidom
import xml.etree.ElementTree as ElementTree



def update_func(self, context):
    # print("my test function", self)
	bpy.ops.ui.search_key_bind()

################
# オペレーター #
################

class ChangeUserPreferencesTab(bpy.types.Operator):
	bl_idname = "ui.change_preferences_tab"
	bl_label = "Switch user prefences tab"
	bl_description = "Cycles user settings tab"
	bl_options = {'REGISTER'}

	is_left = bpy.props.BoolProperty(name="To Left", default=False)

	def execute(self, context):
		tabs = ['INTERFACE', 'EDITING', 'INPUT', 'ADDONS', 'THEMES', 'FILES', 'SYSTEM']
		now_tab = context.preferences.active_section
		if (now_tab not in tabs):
			self.report(type={'ERROR'}, message="Unexpected Tab Now")
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
	bl_label = "Search Key Bind"
	bl_description = "Find matching key bindings you set assignment"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		keymap = context.window_manager.keyconfigs.addon.keymaps['temp'].keymap_items[0]
		if (keymap.type == 'NONE'):
			self.report(type={'ERROR'}, message="Set search key is empty")
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
	bl_description = "Remove string used to search for shortcuts"
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
	bl_label = "Close all key configs"
	bl_description = "Collapses all game menu"
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
	bl_label = "Show shortcut list by browser"
	bl_description = "Can confirm Blender all shortcuts in browser"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		addonDir = os.path.dirname(__file__)
		keyDatas = collections.OrderedDict()
		with codecs.open(os.path.join(addonDir, "ShortcutHtmlKeysData.csv"), 'r', 'utf-8') as f:
			reader = csv.reader(f)
			for row in reader:
				name = row[1]
				keyDatas[name] = {}
				keyDatas[name]["key_name"] = row[0]
				keyDatas[name]["key_code"] = row[1]
				keyDatas[name]["shape"] = row[2]
				keyDatas[name]["coords"] = row[3]
				keyDatas[name]["configs"] = collections.OrderedDict()
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
		file = codecs.open(os.path.join(addonDir, "ShortcutHtmlTemplate.html"), 'r', 'utf-8')
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
	bl_label = "Create Shortcut by Last Command"
	bl_description = "Last command create shortcut"
	bl_options = {'REGISTER'}




	is_clipboard = bpy.props.BoolProperty(name="(Do Not Change)")
	command = bpy.props.StringProperty(name="(Do Not Change)")
	sub_command = bpy.props.StringProperty(name="(Do Not Change)")
	items = [
		('Window', "Window", "", 1),
		('Screen', "Screen", "", 2),
		('Screen Editing', "Screen Edit", "", 3),
		('View2D', "2D View", "", 4),
		('Frames', "Frame", "", 5),
		('Header', "Header", "", 6),
		('View2D Buttons List', "2D view buttons list", "", 7),
		('Property Editor', "Property Editor", "", 8),
		('3D View Generic', "3D View General", "", 9),
		('Grease Pencil', "Grease Pencil", "", 10),
		('Grease Pencil Stroke Edit Mode', "Grease Pencil Stroke Edit Mode", "", 11),
		('Face Mask', "Face Mask", "", 12),
		('Weight Paint Vertex Selection', "Select weight painting vertex", "", 13),
		('Pose', "Pose", "", 14),
		('Object Mode', "Object Mode", "", 15),
		('Paint Curve', "Paint Curve", "", 16),
		('Curve', "Curve", "", 17),
		('Image Paint', "Image Paint", "", 18),
		('Vertex Paint', "Vertex Paint", "", 19),
		('Weight Paint', "Weight Paint", "", 20),
		('Sculpt', "Sculpt", "", 21),
		('Mesh', "Mesh", "", 22),
		('Armature', "Armature", "", 23),
		('Metaball', "Metaballs", "", 24),
		('Lattice', "Lattice", "", 25),
		('Particle', "Particle", "", 26),
		('Font', "Font", "", 27),
		('Object Non-modal', "Object Non-modal", "", 28),
		('3D View', "3D View", "", 29),
		('Outliner', "Outliner", "", 30),
		('Info', "Info", "", 31),
		('View3D Gesture Circle', "3D Burgess Cha circle", "", 32),
		('Gesture Border', "Gesture Boundary", "", 33),
		('Gesture Zoom Border', "Zoom Gesture Border", "", 34),
		('Gesture Straight Line', "Gesture Lines", "", 35),
		('Standard Modal Map', "Common Modal Map", "", 36),
		('Animation', "Animation", "", 37),
		('Animation Channels', "Animation Channel", "", 38),
		('Knife Tool Modal Map', "Knife Modal Map", "", 39),
		('UV Editor', "UV Editor", "", 40),
		('Transform Modal Map', "Transform Modal Map", "", 41),
		('UV Sculpt', "UV Sculpt", "", 42),
		('Paint Stroke Modal', "Paint Stroke Modal", "", 43),
		('Mask Editing', "Mask Edit", "", 44),
		('Markers', "Marker", "", 45),
		('Timeline', "Timeline", "", 46),
		('View3D Fly Modal', "3D view fly modal", "", 47),
		('View3D Walk Modal', "3D view walk modal", "", 48),
		('View3D Rotate Modal', "3D view rotation modal", "", 49),
		('View3D Move Modal', "3D view mobile modal", "", 50),
		('View3D Zoom Modal', "3D views zoom modal", "", 51),
		('View3D Dolly Modal', "3D Bewdley Modal", "", 52),
		('Graph Editor Generic', "Graph General", "", 53),
		('Graph Editor', "Graph Editor", "", 54),
		('Image Generic', "Images General", "", 55),
		('Image', "Image", "", 56),
		('Node Generic', "Node General", "", 57),
		('Node Editor', "Node Editor", "", 58),
		('File Browser', "File Browser", "", 59),
		('File Browser Main', "File Browser Main", "", 60),
		('File Browser Buttons', "File Browser Button", "", 61),
		('Dopesheet', "DopeSheet", "", 62),
		('NLA Generic', "NLA General", "", 63),
		('NLA Channels', "NLA Channel", "", 64),
		('NLA Editor', "NLA Editor", "", 65),
		('Text Generic', "Text General", "", 66),
		('Text', "Text", "", 67),
		('SequencerCommon', "Sequencer-common", "", 68),
		('Sequencer', "Sequencer", "", 69),
		('SequencerPreview', "Sequencer Preview", "", 70),
		('Logic Editor', "Logic Editor", "", 71),
		('Console', "Console", "", 72),
		('Clip', "Clip", "", 73),
		('Clip Editor', "Clip Editor", "", 74),
		('Clip Graph Editor', "Clip Graph Editor", "", 75),
		('Clip Dopesheet Editor', "Clip Deepseat Editor", "", 76),
		]
	key_map = bpy.props.EnumProperty(items=items, name="Effective Area")
	items = [
		('LEFTMOUSE', "Left Click", "", 1),
		('MIDDLEMOUSE', "Click Wheel", "", 2),
		('RIGHTMOUSE', "Right Click", "", 3),
		('BUTTON4MOUSE', "Mouse Button 4", "", 4),
		('BUTTON5MOUSE', "Mouse Button 5", "", 5),
		('BUTTON6MOUSE', "Mouse Button 6", "", 6),
		('BUTTON7MOUSE', "Mouse Button 7", "", 7),
		('MOUSEMOVE', "Mouse Movement", "", 8),
		('INBETWEEN_MOUSEMOVE', "Mouse Moving Border", "", 9),
		('WHEELUPMOUSE', "Wheel Up", "", 10),
		('WHEELDOWNMOUSE', "Wheel Down", "", 11),
		('A', "A Key", "", 12),
		('B', "B Key", "", 13),
		('C', "C Key", "", 14),
		('D', "D Key", "", 15),
		('E', "E Key", "", 16),
		('F', "F Key", "", 17),
		('G', "G Key", "", 18),
		('H', "H Key", "", 19),
		('I', "I Key", "", 20),
		('J', "J Key", "", 21),
		('K', "K Key", "", 22),
		('L', "L Key", "", 23),
		('M', "M Key", "", 24),
		('N', "N Key", "", 25),
		('O', "O Key", "", 26),
		('P', "P Key", "", 27),
		('Q', "Q Key", "", 28),
		('R', "R Key", "", 29),
		('S', "S Key", "", 30),
		('T', "T Key", "", 31),
		('U', "U Key", "", 32),
		('V', "V Key", "", 33),
		('W', "W Key", "", 34),
		('X', "X Key", "", 35),
		('Y', "Y Key", "", 36),
		('Z', "Z Key", "", 37),
		('ZERO', "0", "", 38),
		('ONE', "1", "", 39),
		('TWO', "2", "", 40),
		('THREE', "3", "", 41),
		('FOUR', "4", "", 42),
		('FIVE', "5", "", 43),
		('SIX', "6", "", 44),
		('SEVEN', "7", "", 45),
		('EIGHT', "8", "", 46),
		('NINE', "9", "", 47),
		('LEFT_CTRL', "Left Ctrl", "", 48),
		('LEFT_ALT', "Left ALT", "", 49),
		('LEFT_SHIFT', "Left Shift", "", 50),
		('RIGHT_ALT', "Right ALT", "", 51),
		('RIGHT_CTRL', "Right Ctrl", "", 52),
		('RIGHT_SHIFT', "Right Shift", "", 53),
		('OSKEY', "OS Key", "", 54),
		('GRLESS', "\\", "", 55),
		('ESC', "Esc Key", "", 56),
		('TAB', "Tab Key", "", 57),
		('RET', "Enter Key", "", 58),
		('SPACE', "Space Key", "", 59),
		('BACK_SPACE', "BackSpace Key", "", 60),
		('DEL', "Delete Key", "", 61),
		('SEMI_COLON', ":", "", 62),
		('PERIOD', ". (Period)", "", 63),
		('COMMA', ", (Comma)", "", 64),
		('QUOTE', "^", "", 65),
		('ACCENT_GRAVE', "@", "", 66),
		('MINUS', "-", "", 67),
		('SLASH', "/", "", 68),
		('BACK_SLASH', "\\(BackSlash)", "", 69),
		('EQUAL', ";", "", 70),
		('LEFT_BRACKET', "[", "", 71),
		('RIGHT_BRACKET', "]", "", 72),
		('LEFT_ARROW', "Left", "", 73),
		('DOWN_ARROW', "Down", "", 74),
		('RIGHT_ARROW', "Right", "", 75),
		('UP_ARROW', "Up", "", 76),
		('NUMPAD_2', "Numpad 2", "", 77),
		('NUMPAD_4', "Numpad 4", "", 78),
		('NUMPAD_6', "Numpad 6", "", 79),
		('NUMPAD_8', "Numpad 8", "", 80),
		('NUMPAD_1', "Numpad 1", "", 81),
		('NUMPAD_3', "Numpad 3", "", 82),
		('NUMPAD_5', "Numpad 5", "", 83),
		('NUMPAD_7', "Numpad 7", "", 84),
		('NUMPAD_9', "Numpad 9", "", 85),
		('NUMPAD_PERIOD', "Numpad Period", "", 86),
		('NUMPAD_SLASH', "Numpad Slash", "", 87),
		('NUMPAD_ASTERIX', "Numpad *", "", 88),
		('NUMPAD_0', "Numpad 0", "", 89),
		('NUMPAD_MINUS', "Numpad Minus", "", 90),
		('NUMPAD_ENTER', "Numpad Enter", "", 91),
		('NUMPAD_PLUS', "Numpad +", "", 92),
		('F1', "F1", "", 93),
		('F2', "F2", "", 94),
		('F3', "F3", "", 95),
		('F4', "F4", "", 96),
		('F5', "F5", "", 97),
		('F6', "F6", "", 98),
		('F7', "F7", "", 99),
		('F8', "F8", "", 100),
		('F9', "F9", "", 101),
		('F10', "F10", "", 102),
		('F11', "F11", "", 103),
		('F12', "F12", "", 104),
		('F13', "F13", "", 105),
		('F14', "F14", "", 106),
		('F15', "F15", "", 107),
		('F16', "F16", "", 108),
		('F17', "F17", "", 109),
		('F18', "F18", "", 110),
		('F19', "F19", "", 111),
		('PAUSE', "Pause Key", "", 112),
		('INSERT', "Insert Key", "", 113),
		('HOME', "Home Key", "", 114),
		('PAGE_UP', "PageUp Key", "", 115),
		('PAGE_DOWN', "PageDown Key", "", 116),
		('END', "End Key", "", 117),
		]
	type = bpy.props.EnumProperty(items=items, name="Input Keys",update=update_func)
	shift = bpy.props.BoolProperty(name="Shift key is modifier", default=False,update=update_func)
	ctrl = bpy.props.BoolProperty(name="Set Ctrl modifier keys", default=False,update=update_func)
	alt = bpy.props.BoolProperty(name="Alt key is modifier", default=False,update=update_func)
	oskey = bpy.props.BoolProperty(name="oskey key is modifier", default=False,update=update_func)


	# bpy.types.Scene.shift = bpy.props.BoolProperty(update=update_func)
	# bpy.types.Scene.ctrl = bpy.props.BoolProperty(update=update_func, default=True)
	# bpy.types.Scene.alt = bpy.props.BoolProperty(update=update_func)
	# bpy.types.Scene.oskey = bpy.props.BoolProperty(update=update_func)

	def execute(self, context):
		keymap_item = context.window_manager.keyconfigs.user.keymaps[self.key_map].keymap_items.new(self.command, self.type, 'PRESS', False, self.shift, self.ctrl, self.alt, self.oskey)
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
		context.window_manager.keyconfigs.user.keymaps[self.key_map].show_expanded_children = True
		context.window_manager.keyconfigs.user.keymaps[self.key_map].show_expanded_items = True
		context.window_manager.keyconfigs.user.keymaps[self.key_map].keymap_items[-1].show_expanded = True
		for area in context.screen.areas:
			area.tag_redraw()
		self.report(type={"INFO"}, message="Please save user settings, shortcuts, register if you")
		return {'FINISHED'}
	def invoke(self, context, event):
		pre_clipboard = context.window_manager.clipboard
		pre_area_type = context.area.type
		context.area.type = 'INFO'
		if (not self.is_clipboard):
			for area in context.screen.areas:
				area.tag_redraw()
			bpy.ops.info.reports_display_update()
			for i in range(50):
				bpy.ops.info.select_all_toggle()
				bpy.ops.info.report_copy()
				if (context.window_manager.clipboard != ""):
					break
			bpy.ops.info.select_all_toggle()
		context.area.type = pre_area_type
		commands = context.window_manager.clipboard.split("\n")
		context.window_manager.clipboard = pre_clipboard
		if (commands[-1] == ''):
			commands = commands[:-1]
		if (len(commands) <= 0):
			self.report(type={'ERROR'}, message="Last command not found")
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
					self.report(type={'ERROR'}, message="Command type not supported")
					return {'CANCELLED'}
				break
		else:
			self.report(type={'ERROR'}, message="Could not find command can register")
			return {'CANCELLED'}
		return context.window_manager.invoke_props_dialog(self)

class ShowEmptyShortcuts(bpy.types.Operator):
	bl_idname = "view3d.show_empty_shortcuts"
	bl_label = "Non-Assigning Shortcuts List"
	bl_description = "Information area shows key assignments in current editing mode without"
	bl_options = {'REGISTER'}

	def execute(self, context):
		addonDir = os.path.dirname(__file__)
		key_names = collections.OrderedDict()
		key_strings = []
		key_binds = collections.OrderedDict()
		with open(os.path.join(addonDir, "KeysList.csv"), 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				key_names[row[1]] = row[0]
				key_strings.append(row[1])
				key_binds[row[1]] = None
		keyconfigs = context.window_manager.keyconfigs
		permits = ['Window', 'Screen', '3D View Generic', '3D View', 'Frames', 'Object Non-modal']
		if (context.mode == 'EDIT_MESH'):
			permits.append('Mesh')
		elif (context.mode == 'EDIT_CURVE'):
			permits.append('Curve')
		elif (context.mode == 'EDIT_SURFACE'):
			permits.append('Curve')
		elif (context.mode == 'EDIT_TEXT'):
			permits.append('Font')
		elif (context.mode == 'EDIT_ARMATURE'):
			permits.append('Armature')
		elif (context.mode == 'EDIT_METABALL'):
			permits.append('Metaball')
		elif (context.mode == 'EDIT_LATTICE'):
			permits.append('Lattice')
		elif (context.mode == 'POSE'):
			permits.append('Pose')
		elif (context.mode == 'SCULPT'):
			permits.append('Sculpt')
		elif (context.mode == 'PAINT_WEIGHT'):
			permits.append('Weight Paint')
		elif (context.mode == 'PAINT_VERTEX'):
			permits.append('Vertex Paint')
		elif (context.mode == 'PAINT_TEXTURE'):
			permits.append('Image Paint')
		elif (context.mode == 'PARTICLE'):
			permits.append('Particle')
		elif (context.mode == 'OBJECT'):
			permits.append('Object Mode')
		for keyconfig in (keyconfigs.user, keyconfigs.addon):
			for keymap in keyconfig.keymaps:
				if (not keymap.name in permits):
					continue
				for item in keymap.keymap_items:
					if (item.type in key_strings):
						if (item.active):
							if (not item.shift and not item.ctrl and not item.alt and not item.oskey and item.key_modifier == 'NONE'):
								key_binds[item.type] = item.idname
							elif (item.any):
								key_binds[item.type] = item.idname
		self.report(type={'INFO'}, message = permits[-1]+"Free mode, assign following")
		for key, value in key_binds.items():
			if (not value):
				self.report(type={'INFO'}, message = key_names[key]+" ")
		return {'FINISHED'}

class ImportKeyConfigXml(bpy.types.Operator):
	bl_idname = "file.import_key_config_xml"
	bl_label = "Import Key Config XML"
	bl_description = "game reads in XML format"
	bl_options = {'REGISTER'}

	filepath = bpy.props.StringProperty(subtype='FILE_PATH')
	items = [
		('RESET', "Reset", "", 1),
		('ADD', "Add", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Mode", default='ADD')

	def execute(self, context):
		context.preferences.addons[__name__.partition('.')[0]].preferences.key_config_xml_path = self.filepath
		try:
			tree = ElementTree.parse(self.filepath)
		except:
			self.report(type={'ERROR'}, message="Failed to load XML file")
			return {'CANCELLED'}
		root = tree.getroot()
		if (root.tag != 'BlenderKeyConfig'):
			self.report(type={'ERROR'}, message="This file is not Blender game XML file")
			return {'CANCELLED'}
		try:
			if (root.attrib['Version'] != '1.2'):
				self.report(type={'ERROR'}, message="Does not correspond to version of Blender game XML file")
				return {'CANCELLED'}
		except KeyError:
			self.report(type={'ERROR'}, message="Could not determine version of Blender game XML file")
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
					key_map_item = key_map.keymap_items.new(id_name, type, value, any, shift, ctrl, alt, os, key_modifier)
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
	bl_label = "Export Key Config XML"
	bl_description = "Game save in XML format"
	bl_options = {'REGISTER'}

	filepath = bpy.props.StringProperty(subtype='FILE_PATH')

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
	bl_label = "Move shortcut expanded to other categories"
	bl_description = "Move key assignments that expand into other categories"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('Window', "Window", "", 1),
		('Screen', "Screen", "", 2),
		('Screen Editing', "Screen Edit", "", 3),
		('View2D', "2D View", "", 4),
		('Frames', "Frame", "", 5),
		('Header', "Header", "", 6),
		('View2D Buttons List', "2D view buttons list", "", 7),
		('Property Editor', "Property Editor", "", 8),
		('3D View Generic', "3D View General", "", 9),
		('Grease Pencil', "Grease Pencil", "", 10),
		('Grease Pencil Stroke Edit Mode', "Grease Pencil Stroke Edit Mode", "", 11),
		('Face Mask', "Face Mask", "", 12),
		('Weight Paint Vertex Selection', "Select weight painting vertex", "", 13),
		('Pose', "Pose", "", 14),
		('Object Mode', "Object Mode", "", 15),
		('Paint Curve', "Paint Curve", "", 16),
		('Curve', "Curve", "", 17),
		('Image Paint', "Image Paint", "", 18),
		('Vertex Paint', "Vertex Paint", "", 19),
		('Weight Paint', "Weight Paint", "", 20),
		('Sculpt', "Sculpt", "", 21),
		('Mesh', "Mesh", "", 22),
		('Armature', "Armature", "", 23),
		('Metaball', "Metaballs", "", 24),
		('Lattice', "Lattice", "", 25),
		('Particle', "Particle", "", 26),
		('Font', "Font", "", 27),
		('Object Non-modal', "Object Non-modal", "", 28),
		('3D View', "3D View", "", 29),
		('Outliner', "Outliner", "", 30),
		('Info', "Info", "", 31),
		('View3D Gesture Circle', "3D Burgess Cha circle", "", 32),
		('Gesture Border', "Gesture Boundary", "", 33),
		('Gesture Zoom Border', "Zoom Gesture Border", "", 34),
		('Gesture Straight Line', "Gesture Lines", "", 35),
		('Standard Modal Map', "Common Modal Map", "", 36),
		('Animation', "Animation", "", 37),
		('Animation Channels', "Animation Channel", "", 38),
		('Knife Tool Modal Map', "Knife Modal Map", "", 39),
		('UV Editor', "UV Editor", "", 40),
		('Transform Modal Map', "Transform Modal Map", "", 41),
		('UV Sculpt', "UV Sculpt", "", 42),
		('Paint Stroke Modal', "Paint Stroke Modal", "", 43),
		('Mask Editing', "Mask Edit", "", 44),
		('Markers', "Marker", "", 45),
		('Timeline', "Timeline", "", 46),
		('View3D Fly Modal', "3D view fly modal", "", 47),
		('View3D Walk Modal', "3D view walk modal", "", 48),
		('View3D Rotate Modal', "3D view rotation modal", "", 49),
		('View3D Move Modal', "3D view mobile modal", "", 50),
		('View3D Zoom Modal', "3D views zoom modal", "", 51),
		('View3D Dolly Modal', "3D Bewdley Modal", "", 52),
		('Graph Editor Generic', "Graph General", "", 53),
		('Graph Editor', "Graph Editor", "", 54),
		('Image Generic', "Images General", "", 55),
		('Image', "Image", "", 56),
		('Node Generic', "Node General", "", 57),
		('Node Editor', "Node Editor", "", 58),
		('File Browser', "File Browser", "", 59),
		('File Browser Main', "File Browser Main", "", 60),
		('File Browser Buttons', "File Browser Button", "", 61),
		('Dopesheet', "DopeSheet", "", 62),
		('NLA Generic', "NLA General", "", 63),
		('NLA Channels', "NLA Channel", "", 64),
		('NLA Editor', "NLA Editor", "", 65),
		('Text Generic', "Text General", "", 66),
		('Text', "Text", "", 67),
		('SequencerCommon', "Sequencer-common", "", 68),
		('Sequencer', "Sequencer", "", 69),
		('SequencerPreview', "Sequencer Preview", "", 70),
		('Logic Editor', "Logic Editor", "", 71),
		('Console', "Console", "", 72),
		('Clip', "Clip", "", 73),
		('Clip Editor', "Clip Editor", "", 74),
		('Clip Graph Editor', "Clip Graph Editor", "", 75),
		('Clip Dopesheet Editor', "Clip Deepseat Editor", "", 76),
		]
	category = bpy.props.EnumProperty(items=items, name="Move Category")
	source_delete = bpy.props.BoolProperty(name="Remove Original", default=True)

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
		if (i <= 0):
			self.report(type={'ERROR'}, message="Unfolding assignment does not exist")
			return {'CANCELLED'}
		if (2 <= i):
			self.report(type={'ERROR'}, message="Try only one expansion assignments in the")
			return {'CANCELLED'}
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		for keymap in context.window_manager.keyconfigs.user.keymaps:
			if (not keymap.is_modal):
				for keymap_item in keymap.keymap_items:
					if (keymap_item.show_expanded):
						target_keymap = context.window_manager.keyconfigs.user.keymaps[self.category]
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
	bl_label = "Update Blender-Scramble-Addon"
	bl_description = "Downloads, updates and check out Blender-Scramble-Addon"
	bl_options = {'REGISTER'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		pass

	def execute(self, context):
		response = urllib.request.urlopen("https://github.com/saidenka/Blender-Scramble-Addon/archive/master.zip")
		tempDir = bpy.app.tempdir
		zipPath = os.path.join(tempDir, "Scramble Addon.zip")
		addonDir = os.path.dirname(__file__)
		f = open(zipPath, "wb")
		f.write(response.read())
		f.close()
		zf = zipfile.ZipFile(zipPath, "r")
		for f in zf.namelist():
			if not os.path.basename(f):
				pass
			else:
				if ("Scramble Addon" in f):
					uzf = open(os.path.join(addonDir, os.path.basename(f)), 'wb')
					uzf.write(zf.read(f))
					uzf.close()
		zf.close()
		self.report(type={"INFO"}, message="Please restart Blender updated add-ons")
		return {'FINISHED'}

class ToggleDisabledMenu(bpy.types.Operator):
	bl_idname = "wm.toggle_disabled_menu"
	bl_label = "Toggle \"On/Off Additional Items\""
	bl_description = "Show or hide turn on/off additional items button at end of menu by ScrambleAddon"
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
	bl_idname = "USERPREF_HT_header_input"
	bl_label = "  ShortcutKeys"
	bl_description = "Operations related to shortcut menu"

	def draw(self, context):
		self.layout.operator(ShowShortcutHtml.bl_idname, icon="PLUGIN")
		self.layout.operator(ShowEmptyShortcuts.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RegisterLastCommandKeyconfig.bl_idname, text="Create Shortcut by Last Command", icon="PLUGIN").is_clipboard = False
		self.layout.operator(RegisterLastCommandKeyconfig.bl_idname, text="Clipboard command create shortcut", icon="PLUGIN").is_clipboard = True
		self.layout.separator()
		self.layout.operator(ImportKeyConfigXml.bl_idname, icon="PLUGIN")
		self.layout.operator(ExportKeyConfigXml.bl_idname, icon="PLUGIN")

class AddonsMenu(bpy.types.Menu):
	bl_idname = "USERPREF_HT_header_scramble_addon"
	bl_label = "  Scramble Addon"
	bl_description = "Operations involving scramble Addon menu"

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
		active_section = context.preferences.active_section
		if (active_section == 'INPUT'):
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
			row = self.layout.row(align=True)
			sub = row.row()
			sub.prop(keymap_item, 'type', event=True, text="")
			sub.scale_x = 0.5
			row.prop(keymap_item, 'shift', text="Shift", toggle=True)
			row.prop(keymap_item, 'ctrl', text="Ctrl", toggle=True)
			row.prop(keymap_item, 'alt', text="Alt", toggle=True)
			row.prop(keymap_item, 'oskey', text="Oskey", toggle=True)
			row.prop(keymap_item, 'any', text="Any", toggle=True)
			row.operator(SearchKeyBind.bl_idname, icon="PLUGIN")
			row.operator(ClearFilterText.bl_idname, icon='X', text="")
		elif (active_section == 'ADDONS'):
			self.layout.menu(AddonsMenu.bl_idname, icon="PLUGIN")
		row = self.layout.row(align=True)
		row.operator(ChangeUserPreferencesTab.bl_idname, icon='TRIA_LEFT', text="").is_left = True
		row.operator(ChangeUserPreferencesTab.bl_idname, icon='TRIA_RIGHT', text="").is_left = False
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
