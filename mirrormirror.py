#Mirror Mirror Integration V1
import bpy
from bgl import *
from bpy.props import *
from math import radians, degrees
from ... utils.context import ExecutionContext
from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time
from ... utils.blender_ui import get_location_in_current_3d_view
from .. utils import clear_ssharps, mark_ssharps, set_smoothing
from ... overlay_drawer import show_custom_overlay, disable_active_overlays, show_text_overlay
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text, draw_box, draw_logo_csharp

import bpy
from bpy.app.handlers import persistent

#------------------- FUNCTIONS------------------------------
# Do the Basic Union, Difference and Intersection Operations
def Operation(context,_operation):
        ''' select the object, then select what you want it's mirror object to be '''
        #select 2 context object
    
        try:
            # select objects
     
            if(len(bpy.context.selected_objects)) == 1 : # one is selected , add mirror mod immediately to that object#
                modifier_ob = bpy.context.active_object         
                mirror_mod = modifier_ob.modifiers.new("mirror_mirror","MIRROR")
          

            else:
                mirror_ob = bpy.context.active_object         # last ob selected
                mirror_ob.select_set(False) # pop modifier_ob from sel_stack
                modifier_ob = bpy.context.selected_objects[0]

                mirror_mod = modifier_ob.modifiers.new("mirror_mirror","MIRROR")
                mirror_mod.mirror_object = mirror_ob
                
            if _operation == "MIRROR_X":
                mirror_mod.use_x = True
                mirror_mod.use_y = False
                mirror_mod.use_z = False
            elif _operation == "MIRROR_Y":
                mirror_mod.use_x = False
                mirror_mod.use_y = True
                mirror_mod.use_z = False
            elif _operation == "MIRROR_Z":
                mirror_mod.use_x = False
                mirror_mod.use_y = False
                mirror_mod.use_z = True
            
            mirror_ob.select= 1
            modifier_ob.select=1
            bpy.bpy.context.view_layer.objects.active = modifier_ob
        except: 
            pass
           
#------------------- OPERATOR CLASSES ------------------------------                
# Mirror Tool                 

class MirrorX(bpy.types.Operator):
    """This adds an X mirror to the selected object"""
    bl_idname = "hops.mirror_mirror_x"
    bl_label = "Mirror X"
    bl_options = {"REGISTER", "UNDO"}
    
    axis = "X"
    

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return context.active_object is not None
    
    def invoke(self, context, event):
        self.execute(context)
        
 
        if tool_overlays_enabled():
            disable_active_overlays()
            self.wake_up_overlay = show_custom_overlay(draw,
                parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())
     
        return {"FINISHED"}
    
    def parameter_getter(self):
        return self.axis
    
    def execute(self, context):
        Operation(context,"MIRROR_X")
        
        try: self.wake_up_overlay()
        except: pass
        return {'FINISHED'}
    
    
class MirrorY(bpy.types.Operator):
    """This  adds a Y mirror modifier"""
    bl_idname = "hops.mirror_mirror_y"
    bl_label = "Mirror Y"
    bl_options = {"REGISTER", "UNDO"}
    
    axis = "Y"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return context.active_object is not None
    
    def invoke(self, context, event):
        self.execute(context)
        
        object = bpy.context.active_object
        if object.hops.status != "CSTEP":
            if tool_overlays_enabled():
                disable_active_overlays()
                self.wake_up_overlay = show_custom_overlay(draw,
                    parameter_getter = self.parameter_getter,
                    location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                    location_type = "CUSTOM",
                    stay_time = Hops_display_time(),
                    fadeout_time = Hops_fadeout_time())
        

        return {"FINISHED"}
    
    def parameter_getter(self):
        return self.axis
    
    def execute(self, context):
        Operation(context,"MIRROR_Y")
        
        try: self.wake_up_overlay()
        except: pass
        return {'FINISHED'}

class MirrorZ(bpy.types.Operator):
    """This  add a Z mirror modifier"""
    bl_idname = "hops.mirror_mirror_z"
    bl_label = "Mirror Z"
    bl_options = {"REGISTER", "UNDO"}

    axis = "Z"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return context.active_object is not None
    
    def invoke(self, context, event):
        self.execute(context)
        
        object = bpy.context.active_object
        if object.hops.status != "CSTEP":
            if tool_overlays_enabled():
                disable_active_overlays()
                self.wake_up_overlay = show_custom_overlay(draw,
                    parameter_getter = self.parameter_getter,
                    location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                    location_type = "CUSTOM",
                    stay_time = Hops_display_time(),
                    fadeout_time = Hops_fadeout_time())

        return {"FINISHED"}
    
    def parameter_getter(self):
        return self.axis
    
    def execute(self, context):
        Operation(context,"MIRROR_Z")
        
        try: self.wake_up_overlay()
        except: pass
        return {'FINISHED'}
    
# Overlay
###################################################################

def draw(display, parameter_getter):
    axis = parameter_getter()
    scale_factor = 0.9

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    set_drawing_dpi(display.get_dpi() * scale_factor)
    dpi_factor = display.get_dpi_factor() * scale_factor
    line_height = 18 * dpi_factor

    transparency = display.transparency

    color_text1, color_text2, color_border, color_border2 = get_hops_preferences_colors_with_transparency(transparency)
    region_width = bpy.context.region.width


    # Box
    ########################################################

    location = display.location
    x, y = location.x - 60* dpi_factor, location.y - 118* dpi_factor

    draw_box(0, 43 *dpi_factor, region_width, -4 * dpi_factor, color = color_border2)
    draw_box(0, 0, region_width, -82 * dpi_factor, color = color_border)

    draw_logo_csharp(color_border2) #Logo so illa. I love this bitch.


    # Name
    ########################################################
    draw_text("MIRROR_mirror", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)

    
    # First Coloumn
    ########################################################
    x = x - 160 * dpi_factor
    r = 34 * dpi_factor

    draw_text("AXIS", x , y,
              align = "LEFT",size = 11, color = color_text2)

    draw_text(axis, x + r, y,
              align = "LEFT",size = 11, color = color_text2)
              
    #draw_text("Mirrored Across: ", x, y - line_height,
    #          align = "LEFT", size = 12, color = color_text2)

    #draw_text(axis, x + r, y - line_height,
    #          align = "LEFT", size = 12, color = color_text2)

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)