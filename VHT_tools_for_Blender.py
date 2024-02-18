#   VHT tools for Blender
#   Copyright (c) 2023 Aurel Constantinescu
#   https://www.virtualhometheater.com
#   support@virtualhometheater.com


bl_info = {
    "name": "VHT tools for Blender",
    "author": "Aurel Constantinescu",
    "version": (1, 0, 0),##version
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar > VHT tools",
    "description": ("These tools will create a new window with stereoscopic SbS 180 projection for live scene view in VR and will help artist to render stereoscopic VR images or videos files."),
    "warning": "To view in VR the live stereoscopic viewport will require to use the Virtual Home Theater (VHT) VR app from Steam store and two displays!",
    "doc_url": "https://virtualhometheater.com",
    "category": "VR"
}


import bpy
from bpy.types import (Panel, Operator)
import mathutils
from math import (degrees, radians)
import os
import subprocess
import time
from datetime import datetime
import ctypes
from ctypes.wintypes import MAX_PATH


us32dll = ctypes.windll.user32
sh32dll = ctypes.windll.shell32
unibuf = ctypes.create_unicode_buffer(MAX_PATH + 1)
if sh32dll.SHGetSpecialFolderPathW(None, unibuf, 0x0005, False):
    documents_path = unibuf.value
else:
    documents_path = r'C:\Users\admin\Documents'


VHT_app = 0
scene_cam_name = 'none'

cycles_samples = 16
cycles_use_denoising = True


def getshadintype(): 
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            return space.shading.type                     
    return 'MATERIAL'

                  
def getlight():    
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            return space.shading.light                           
    return 'STUDIO'


def getcolortype():    
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            return space.shading.color_type                           
    return 'MATERIAL'


def getshowshadows():    
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            return space.shading.show_shadows                           
    return False


def getcavitytype():    
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            return space.shading.cavity_type                           
    return 'WORLD'    


def getshowcavity():    
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            return space.shading.show_cavity                         
    return False    


def getcavitytype():    
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            return space.shading.cavity_type                           
    return 'WORLD'    


def getshowobjectoutline():    
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            return space.shading.show_object_outline                           
    return False


def getshowspecularhighlight():    
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            return space.shading.show_specular_highlight                           
    return False


def Signal_string(): 
    scene = bpy.context.scene
    render = scene.render
    _signal = 'REL9mm' 
    cam_name = scene.camera.name
    wh = -1
    for window in bpy.context.window_manager.windows:
        if(window.screen.name == "VHT_screen"):
            wh = window.height                                                      
    if(cam_name.find('EQD180') != -1 
    or cam_name.find('VR180') != -1 
    or cam_name.find('VR360') != -1):             
        if(getshadintype() == 'RENDERED'
        and scene.render.engine == 'CYCLES'):
            _signal = cam_name.split('.')[0]           
    return _signal + '_wh' + str(wh) + '_rx' + str(render.resolution_x) + '_ry' + str(render.resolution_y) + '_'  


def check_AR():
    scene = bpy.context.scene
    render = scene.render
    render.use_border = True
    cam_name = scene.camera.name
    if(cam_name.find('VR360') != -1
    and getshadintype() == 'RENDERED'
    and render.engine == 'CYCLES'):
        render.resolution_x = 2 * render.resolution_y
    else:
        render.resolution_x = render.resolution_y


def Signal_to_VHT(_signal2):
    global VHT_app
    if(VHT_app):
        __path = documents_path + r'\Virtual Home Theater\pfm_vht.txt'
        f = open(__path, 'w')
        f.write(_signal2)
        f.close()


def update_vr_context():
    #check_AR()
    Signal_to_VHT(Signal_string()) 
    ReFrame_Camera_Bounds_function()   


def Shading_function(_type): 
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.type = _type # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
    update_vr_context()


def SOLID_shading_light_function(_light):
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.light = _light # 'STUDIO' 'MATCAP' 'FLAT'
    update_vr_context()


def SOLID_shading_color_type_function(_color_type):
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.color_type = _color_type # 'MATERIAL' 'TEXTURE'
    update_vr_context()
    

def SOLID_shading_show_shadows_function():
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.show_shadows = not space.shading.show_shadows
    update_vr_context()
    
    
def SOLID_shading_show_cavity_function():
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.show_cavity = not space.shading.show_cavity
    update_vr_context()   
    
    
def SOLID_shading_cavity_type_function(_cavity_type):
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.cavity_type = _cavity_type # 'WORLD' 'SCREEN' 'BOTH'
                            space.shading.show_cavity = True
    update_vr_context()
    
    
def SOLID_shading_show_object_outline_function():
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.show_object_outline = not space.shading.show_object_outline
    update_vr_context()   
    
 
def SOLID_shading_show_specular_highlight_function():
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.show_specular_highlight = not space.shading.show_specular_highlight
    update_vr_context() 
 
  
def Render_engine_function(_engine):
    bpy.context.scene.render.engine = _engine # 'BLENDER_EEVEE' 'BLENDER_WORKBENCH' 'CYCLES'
    update_vr_context() 
       

def GUI_desktop_on_off_function():
    update_vr_context()
    Signal_to_VHT(Signal_string() + '_dmam_')
    
   
def GUI_repose_function():
    Signal_to_VHT('GUI_repose')
    
           
def GUI_on_off_function():
    Signal_to_VHT('GUI_switch')
    
        
def HMD_repose_function():
    Signal_to_VHT('HMD_repose')
    
    
def Level_update_function():
    update_vr_context()
    scene = bpy.context.scene   
    tilt = degrees(scene.camera.rotation_euler.x) % 180 - 90
    Signal_to_VHT(Signal_string() + "_tilt{:0.0f}_".format(tilt) )
    
    
def Level_zero_function():
    update_vr_context()
    Signal_to_VHT(Signal_string() + '_tilt0_')


def Hide_sidebar_function():
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.show_region_ui = False

       
def ReFrame_Camera_Bounds_function():   
    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            for area in screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            bpy.ops.view3d.view_center_camera({'area':area,'region':area.regions[0],})


def Use_Scene_Camera_function(context):  
    bpy.context.space_data.lock_camera = True
    context.space_data.stereo_3d_camera = 'RIGHT'
    update_vr_context()


def Check_for_vht(_appID):
    libraryfolders = r'C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf'
    file = open(libraryfolders, "r")
    if(file):
        for sLine in file:	 
            if(sLine.find(_appID) != -1):
                file.close()
                return 1
    else:
        return -1
    file.close()
    return 0
   

def End_VHT_app_function(context):
    global VHT_app     
    ##if(VHT_app):
    Signal_to_VHT("END_VHT")      
    VHT_app = 0 


def Start_VHT_app_function(context):
    global VHT_app 
    monitors = us32dll.GetSystemMetrics(80)
    if(monitors > 1): 
        steam_path = r'C:\Program Files (x86)\Steam\steam.exe'
      
        if(VHT_app):
            Signal_to_VHT("END_VHT")  
            VHT_app = 0     
        else:
            Signal_to_VHT("")  
            if(Check_for_vht("989060") == 1):
                VHT_app = subprocess.Popen([steam_path, '-applaunch', '989060', '-mode', 'blender_' + Signal_string()])
            else:
                if(Check_for_vht("1107280") == 1):
                    VHT_app = subprocess.Popen([steam_path, '-applaunch', '1107280', '-mode', 'blender_' + Signal_string()])
           
            if(VHT_app == 0):
                print("\a")
                us32dll.MessageBoxW(0,"Steam or VHT VR app not found!", "VHT tools", 48)
                return
                
            ReFrame_Camera_Bounds_function()
            Use_Scene_Camera_function(context)
    else:
        print("\a")
        us32dll.MessageBoxW(0,"To use this tool with the VHT VR app you need to have two active monitors!", "VHT tools", 48)
        

def POST_function(a, b):
    print("\a")
    bpy.app.handlers.render_complete.remove(POST_function)
    
    scene = bpy.context.scene
    render = scene.render
    cycles = scene.cycles
    
    global cycles_samples
    global cycles_use_denoising
    cycles.samples = cycles_samples
    cycles.use_denoising = cycles_use_denoising
    

def FFmpeg_function(a, b):
    print("\a")
    bpy.app.handlers.render_complete.remove(FFmpeg_function)
    
    scene = bpy.context.scene
    render = scene.render
    cycles = scene.cycles

    global cycles_samples
    global cycles_use_denoising
    cycles.samples = cycles_samples
    cycles.use_denoising = cycles_use_denoising

    codec = " -c:v hevc_nvenc -b:v 0 -crf 23 "
    if(render.image_settings.color_mode == 'RGBA' and render.image_settings.file_format == 'PNG'):
        codec = " -c:v vp9 -b:v 0 -crf 23 -pix_fmt yuva420p "

    ffmpeg_path = "ffmpeg" #"C:\\folder\\ffmpeg"
    files_input = '"' + render.filepath + "%4d." + render.image_settings.file_format.lower() + '"'
    file_output = '"' + render.filepath + ".mp4" + '"'
    
    os.system(ffmpeg_path
    + " -framerate " + str(render.fps)
    + " -start_number " + str(scene.frame_start)
    + " -i " + files_input
    + codec
    + file_output)
 

def Render_function(context, _samples, _denoise, _procent, _animation, _useFFmpeg):
    print("\a")
    print("Render started")
       
    scene = bpy.context.scene
    render = scene.render
    cycles = scene.cycles
    
    #   Prepare computer for rendering:
    #   Free some GPU resources (VRAM & compute) if used!
    os.system("taskkill /f /im vrmonitor.exe") # SteamVR
    time.sleep(1)
    os.system("taskkill /f /im MixedRealityPortal.exe") # Microsoft WMR
    os.system("taskkill /f /im OculusClient.exe") # Meta Oculus VR
    End_VHT_app_function(context)
    #   close Blender VHT_screen
    #   The closing window feature in Blender is missing!!!
    #for screen in bpy.data.screens: 
    #    if(screen.name == "VHT_screen"):
    #        #screen.close()   
    Shading_function('WIREFRAME') # using this instead
    #Shading_function('SOLID')
    
    global cycles_samples
    global cycles_use_denoising
    cycles_samples = cycles.samples
    cycles_use_denoising = cycles.use_denoising
        
    if(_samples > 0):  
        cycles.samples = _samples
        cycles.use_denoising = _denoise
        #if(_denoise):
        #    cycles.denoiser = 'OPTIX' # 'OPTIX' OPENIMAGEDENOISE'
                        
    render.resolution_percentage = _procent

    #scenename = bpy.path.basename(bpy.data.filepath)
    scenename = bpy.data.filepath
    scenename = os.path.splitext(scenename)[0]   
    
    if(bpy.context.scene.render.engine == 'CYCLES' ):
        cam_name = scene.camera.name
    else:
        cam_name = scene.camera.name.replace('EQD180', 'REL9mm')
        cam_name = cam_name.replace('VR180', 'REL9mm')
        cam_name = cam_name.replace('VR360', 'REL9mm')
       
    dimo = "_SbS_crosseye_"   
    dtn = datetime.now()   
    if(render.image_settings.stereo_3d_format.display_mode == 'TOPBOTTOM'):
        dimo = "_TaB_"    
    tilt = degrees(scene.camera.rotation_euler.x) % 180 - 90
    scenename = scenename + dtn.strftime(" R_%Y-%m-%d-%H-%M-%S_") + cam_name + "_FF3D" + dimo + "tilt{:0.0f}_".format(tilt) ##format  
    render.filepath = scenename

    if(_useFFmpeg == True and _animation == True):       
        try:
            bpy.app.handlers.render_complete.remove(POST_function)
        except:
            print("except")
        bpy.app.handlers.render_complete.append(FFmpeg_function)    
    else:
        try:
            bpy.app.handlers.render_complete.remove(FFmpeg_function)
        except:
            print("except")
        bpy.app.handlers.render_complete.append(POST_function)
               
    bpy.ops.render.render('INVOKE_DEFAULT', animation=_animation, write_still=True)
    print("Render ended")


def Add_EQD180_camera_function(context):
    scene = bpy.context.scene
    #render = scene.render
    #cycles = scene.cycles
    
    camera_data = bpy.data.cameras.new(name='EQD180')
    camera_data.lens_unit = 'MILLIMETERS'
    camera_data.lens = 9 # 9 11
    camera_data.type = 'PANO' #‘PERSP’, ‘ORTHO’, ‘PANO’
    camera_data.show_name = True
    #
    cd_cycles = camera_data.cycles
    cd_cycles.panorama_type = 'FISHEYE_EQUIDISTANT'
    cd_cycles.fisheye_fov = radians(180)
    #
    cd_stereo = camera_data.stereo
    cd_stereo.interocular_distance = 0.065
    cd_stereo.convergence_mode = 'PARALLEL' #‘OFFAXIS’, ‘PARALLEL’, ‘TOE’
    cd_stereo.pivot = 'CENTER' #‘LEFT’, ‘RIGHT’, ‘CENTER’
    cd_stereo.convergence_distance = 1.95
    cd_stereo.use_spherical_stereo = False
    cd_stereo.use_pole_merge = False
    # Angle at which interocular distance starts to fade to 0
    cd_stereo.pole_merge_angle_from = 1.0472 #[0, 1.5708], default 1.0472
    # Angle at which interocular distance is 0
    cd_stereo.pole_merge_angle_to = 1.309 #[0, 1.5708], default 1.309
    #
    camera_object = bpy.data.objects.new('EQD180', camera_data)
    camera_object.location = (0, -1.53, 1)
    camera_object.rotation_euler = (radians(90), radians(0), radians(0))
    camera_object.lock_rotation[1] = True
    #
    scene.collection.objects.link(camera_object)
    Use_Scene_Camera_function(context)


def Add_REL9mm_camera_function(context):
    scene = bpy.context.scene
    #render = scene.render
    #cycles = scene.cycles

    camera_data  = bpy.data.cameras.new(name='REL9mm')
    camera_data.lens_unit = 'MILLIMETERS'
    camera_data.lens = 9 # 9 11
    camera_data.type = 'PERSP' #‘PERSP’, ‘ORTHO’, ‘PANO’
    camera_data.show_name = True
    #
    cd_stereo = camera_data.stereo
    cd_stereo.interocular_distance = 0.065
    cd_stereo.convergence_mode = 'PARALLEL' #‘OFFAXIS’, ‘PARALLEL’, ‘TOE’
    cd_stereo.pivot = 'CENTER' #‘LEFT’, ‘RIGHT’, ‘CENTER’
    cd_stereo.convergence_distance = 1.95
    cd_stereo.use_spherical_stereo = False
    cd_stereo.use_pole_merge = False
    # Angle at which interocular distance starts to fade to 0
    cd_stereo.pole_merge_angle_from = 1.0472 #[0, 1.5708], default 1.0472
    # Angle at which interocular distance is 0
    cd_stereo.pole_merge_angle_to = 1.309 #[0, 1.5708], default 1.309
    #
    camera_object = bpy.data.objects.new('REL9mm', camera_data)
    camera_object.location = (0, -1.53, 1)
    camera_object.rotation_euler = (radians(90), radians(0), radians(0))
    camera_object.lock_rotation[1] = True
    #
    scene.collection.objects.link(camera_object)
    Use_Scene_Camera_function(context)


def Add_VR180_camera_function(context):
    scene = bpy.context.scene
    #render = scene.render
    #cycles = scene.cycles

    camera_data = bpy.data.cameras.new(name='VR180')
    camera_data.lens_unit = 'MILLIMETERS'
    camera_data.lens = 9 # 9 11
    camera_data.type = 'PANO' #‘PERSP’, ‘ORTHO’, ‘PANO’
    camera_data.show_name = True
    #
    cd_cycles = camera_data.cycles
    cd_cycles.panorama_type = 'EQUIRECTANGULAR'
    cd_cycles.latitude_max = radians(90)
    cd_cycles.latitude_min = radians(-90)
    cd_cycles.longitude_max = radians(90)
    cd_cycles.longitude_min = radians(-90)
    #cd_cycles.fisheye_fov = radians(180)
    #
    cd_stereo = camera_data.stereo
    cd_stereo.interocular_distance = 0.065
    cd_stereo.convergence_mode = 'PARALLEL' #‘OFFAXIS’, ‘PARALLEL’, ‘TOE’
    cd_stereo.pivot = 'CENTER' #‘LEFT’, ‘RIGHT’, ‘CENTER’
    cd_stereo.convergence_distance = 1.95
    cd_stereo.use_spherical_stereo = True
    #
    cd_stereo.use_pole_merge = True
    # Angle at which interocular distance starts to fade to 0
    cd_stereo.pole_merge_angle_from = 1.0472 #[0, 1.5708], default 1.0472
    # Angle at which interocular distance is 0
    cd_stereo.pole_merge_angle_to = 1.309 #[0, 1.5708], default 1.309
    #
    camera_object = bpy.data.objects.new('VR180', camera_data)
    camera_object.location = (0, -1.53, 1)
    camera_object.rotation_euler = (radians(90), radians(0), radians(0))
    camera_object.lock_rotation[1] = True
    #
    scene.collection.objects.link(camera_object)
    Use_Scene_Camera_function(context)
    
    
def Add_VR360_camera_function(context):
    scene = bpy.context.scene
    #render = scene.render
    #cycles = scene.cycles

    camera_data = bpy.data.cameras.new(name='VR360')
    camera_data.lens_unit = 'MILLIMETERS'
    camera_data.lens = 9 # 9 11
    camera_data.type = 'PANO' #‘PERSP’, ‘ORTHO’, ‘PANO’
    camera_data.show_name = True
    #
    cd_cycles = camera_data.cycles
    cd_cycles.panorama_type = 'EQUIRECTANGULAR'
    cd_cycles.latitude_max = radians(90)
    cd_cycles.latitude_min = radians(-90)
    cd_cycles.longitude_max = radians(180)
    cd_cycles.longitude_min = radians(-180)
    #cd_cycles.fisheye_fov = radians(180)
    #
    cd_stereo = camera_data.stereo
    cd_stereo.interocular_distance = 0.065
    cd_stereo.convergence_mode = 'PARALLEL' #‘OFFAXIS’, ‘PARALLEL’, ‘TOE’
    cd_stereo.pivot = 'CENTER' #‘LEFT’, ‘RIGHT’, ‘CENTER’
    cd_stereo.convergence_distance = 1.95
    cd_stereo.use_spherical_stereo = True
    #
    cd_stereo.use_pole_merge = True
    # Angle at which interocular distance starts to fade to 0
    cd_stereo.pole_merge_angle_from = 1.0472 #[0, 1.5708], default 1.0472
    # Angle at which interocular distance is 0
    cd_stereo.pole_merge_angle_to = 1.309 #[0, 1.5708], default 1.309
    #
    camera_object = bpy.data.objects.new('VR360', camera_data)
    camera_object.location = (0, -1.53, 1)
    camera_object.rotation_euler = (radians(90), radians(0), radians(0))
    camera_object.lock_rotation[1] = True
    #
    scene.collection.objects.link(camera_object)
    Use_Scene_Camera_function(context)
    
    
def Preview_settings(context): 
    cycles = context.scene.cycles
    cycles.preview_samples = 16                   
    cycles.use_preview_denoising = True
    cycles.preview_denoiser = 'OPENIMAGEDENOISE' #'OPTIX' 'OPENIMAGEDENOISE'


def Create_Window_SbS(context, _camera):      
    global scene_cam_name
    
    scene = context.scene
    render = scene.render
    cycles = scene.cycles

    for screen in bpy.data.screens: 
        if(screen.name == "VHT_screen"):
            return

    cameraname = "none"
    for camera in bpy.data.cameras:
        if(camera.name.find(_camera) != -1):
            cameraname = camera.name
            break
    if(cameraname == "none"):
        if(_camera == "EQD180"):
            Add_EQD180_camera_function(context)
        elif(_camera == "VR180"):
            Add_VR180_camera_function(context)
        elif(_camera == "VR360"):
            Add_VR360_camera_function(context)   
        else:
            Add_EQD180_camera_function(context)
            _camera = "EQD180"
        cameraname = _camera 
                       
    if(cameraname.find('VR360') != -1):    
        Render_settings_function(8192,4096)#8k4k
    else:        
        Render_settings_function(4096,4096)#4k4k

    # Create new Wimdow
    context.preferences.view.render_display_type = "WINDOW"
    bpy.ops.render.view_show("INVOKE_DEFAULT")
    VHT_window = context.window_manager.windows[-1]
    VHT_window.screen.name = "VHT_screen"
    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
    VHT_window.screen.areas[0].type = 'VIEW_3D'
    VHT_window.screen.areas[1].type = 'VIEW_3D'
                 
    context.scene.camera = context.scene.objects[cameraname]
    scene_cam_name = cameraname
        
    num_view = 0
    for area in VHT_window.screen.areas: #bpy.context.screen.areas
        if area.type == 'VIEW_3D':
            for space in area.spaces: 
                if space.type == 'VIEW_3D':
                    num_view = num_view + 1
                    space.shading.type = 'SOLID' # SOLID MATERIAL RENDERED
                    if(cameraname.find('VR360') != -1):    
                         space.shading.type = 'RENDERED'
                    else:        
                         space.shading.type = 'SOLID' # SOLID MATERIAL RENDERED
                    space.lock_object = bpy.data.objects[cameraname]
                    space.show_gizmo = False
                    space.overlay.show_overlays = False
                    space.lock_camera = True
                    space.show_region_ui = False    
                    space.region_3d.view_perspective = 'CAMERA'
                    bpy.ops.view3d.view_center_camera({'area':area,'region':area.regions[0],})   
                    if num_view%2 == 0:
                        space.stereo_3d_camera = 'RIGHT'
                    if num_view%2 == 1:
                        space.stereo_3d_camera = 'LEFT'                   
 
    Preview_settings(context)
 

def Render_settings_function(_sx, _sy):
    scene = bpy.context.scene
    render = scene.render
    cycles = scene.cycles

    AR = _sx / _sy

    cam_name = scene.camera.name  
    if(cam_name.find('VR360') == -1 and AR == 2):
        return
        
    # Render settings
    render.engine = 'CYCLES' #'BLENDER_EEVEE', 'BLENDER_WORKBENCH'. 'CYCLES'
    render.resolution_x = _sx
    render.resolution_y = _sy
    render.resolution_percentage = 100
    render.use_multiview = True
    render.use_border = True
    #render.image_settings.file_format = 'PNG'

    #scenename = bpy.path.basename(bpy.data.filepath)
    scenename = bpy.data.filepath
    scenename = os.path.splitext(scenename)[0]   
    dtn = datetime.now()  

    render.image_settings.views_format = 'STEREO_3D' # 'STEREO_3D', 'INDIVIDUAL'
    render.image_settings.stereo_3d_format.display_mode = 'SIDEBYSIDE' # SIDEBYSIDE TOPBOTTOM
    
    imfrm = "_FF3D_SbS_crosseye_" ##format2  
    if(cam_name.find('VR360') != -1 and AR == 2):
        imfrm = "_FF3D_TaB_" ##format2   
        render.image_settings.stereo_3d_format.display_mode = 'TOPBOTTOM' # SIDEBYSIDE TOPBOTTOM
              
    render.image_settings.stereo_3d_format.use_sidebyside_crosseyed = True
    render.filepath = scenename + dtn.strftime(" R_%Y-%m-%d_") + cam_name + imfrm ##format2 
      
    #cycles.feature_set = 'EXPERIMENTAL' # 'SUPPORTED' 'EXPERIMENTAL'
    #cycles.device = 'GPU' # 'CPU', 'GPU'
    #cycles.samples = 2048
    
    # Preview for VHT
    Preview_settings(bpy.context)
    
    # Render to files
    #cycles.use_denoising = False
    #cycles.denoiser = 'OPENIMAGEDENOISE' # 'OPTIX' OPENIMAGEDENOISE'

    update_vr_context()


#Operators--------------------------------------------------------------------


class Render_settings_4k4k_operator(Operator):
    bl_idname = "vht.render_settings_4k4k_operator"
    bl_label = "Render_settings_4k4k_operator"
    def execute(self, context):
        Render_settings_function(4096, 4096)
        return {'FINISHED'}   
        
               
class Render_settings_8k4k_operator(Operator):
    bl_idname = "vht.render_settings_8k4k_operator"
    bl_label = "Render_settings_8k4k_operator"
    def execute(self, context):
        Render_settings_function(8192,4096)
        return {'FINISHED'}   
        
        
class GUI_desktop_on_off_operator(Operator):
    bl_idname = "vht.gui_desktop_on_off_operator"
    bl_label = "GUI_desktop_on_off_operator"
    def execute(self, context):
        GUI_desktop_on_off_function()
        return {'FINISHED'}   
        
        
class GUI_repose_operator(Operator):
    bl_idname = "vht.gui_repose_operator"
    bl_label = "GUI_repose_operator"
    def execute(self, context):
        GUI_repose_function()
        return {'FINISHED'}   
        
        
class GUI_on_off_operator(Operator):
    bl_idname = "vht.gui_on_off_operator"
    bl_label = "GUI_on_off_operator"
    def execute(self, context):
        GUI_on_off_function()
        return {'FINISHED'}   
        
        
class HMD_repose_operator(Operator):
    bl_idname = "vht.hmd_repose_operator"
    bl_label = "HMD_repose_operator"
    def execute(self, context):
        HMD_repose_function()
        return {'FINISHED'}   


class Level_update_operator(Operator):
    bl_idname = "vht.level_update_operator"
    bl_label = "Level_update_operator"
    def execute(self, context):
        Level_update_function()
        return {'FINISHED'}   


class Level_zero_operator(Operator):
    bl_idname = "vht.level_zero_operator"
    bl_label = "Level_zero_operator"
    def execute(self, context):
        Level_zero_function()
        return {'FINISHED'}          
       

class Create_Window_SbS_EQD180_Operator(Operator):
    bl_idname = "vht.create_window_sbs_eqd180"
    bl_label = "Create Window SbS EQD180 Operator"
    def execute(self, context):
        Create_Window_SbS(context, 'EQD180')
        return {'FINISHED'}    
        

class Create_Window_SbS_VR180_Operator(Operator):
    bl_idname = "vht.create_window_sbs_vr180"
    bl_label = "Create Window SbS VR180 Operator"
    def execute(self, context):
        Create_Window_SbS(context, 'VR180')
        return {'FINISHED'}  
        
        
class Create_Window_SbS_VR360_Operator(Operator):
    bl_idname = "vht.create_window_sbs_vr360"
    bl_label = "Create Window SbS VR360 Operator"
    def execute(self, context):
        Create_Window_SbS(context, 'VR360')
        return {'FINISHED'}  
        

class Shading_WIREFRAME_operator(Operator):
    bl_idname = "vht.shading_wirefream"
    bl_label = "Shading_WIREFRAME_operator"
    def execute(self, context):
        Shading_function('WIREFRAME')
        return {'FINISHED'}  
        
        
class Shading_SOLID_operator(Operator):
    bl_idname = "vht.shading_solid"
    bl_label = "Shading_SOLID_operator"
    def execute(self, context):
        Shading_function('SOLID')
        return {'FINISHED'}  
    

class Shading_MATERIAL_operator(Operator):
    bl_idname = "vht.shading_material"
    bl_label = "Shading_MATERIAL_operator"
    def execute(self, context):
        Shading_function('MATERIAL')
        return {'FINISHED'}  


class Shading_RENDERED_operator(Operator):
    bl_idname = "vht.shading_rendered"
    bl_label = "Shading_RENDERED_operator"
    def execute(self, context):
        Shading_function('RENDERED')
        return {'FINISHED'}    


class Render_engine_EEVEE_operator(Operator):
    bl_idname = "vht.render_engine_eevee"
    bl_label = "Render_engine_EEVEE_operator"
    def execute(self, context):
        Render_engine_function('BLENDER_EEVEE')
        return {'FINISHED'}         


class Render_engine_WORKBENCH_operator(Operator):
    bl_idname = "vht.render_engine_workbench"
    bl_label = "Render_engine_WORKBENCH_operator"
    def execute(self, context):
        Render_engine_function('BLENDER_WORKBENCH')
        return {'FINISHED'}   
    
    
class Render_engine_CYCLES_operator(Operator):
    bl_idname = "vht.render_engine_cycles"
    bl_label = "Render_engine_CYCLES Operator"
    def execute(self, context):
        Render_engine_function('CYCLES')
        return {'FINISHED'}   


class SOLID_shading_light_STUDIO_operator(Operator):
    bl_idname = "vht.solid_shading_light_studio"
    bl_label = "SOLID shading light STUDIO operator"
    def execute(self, context):
        SOLID_shading_light_function('STUDIO')
        return {'FINISHED'}   


class SOLID_shading_light_MATCAP_operator(Operator):
    bl_idname = "vht.solid_shading_light_matcap"
    bl_label = "SOLID shading light MATCAP operator"
    def execute(self, context):
        SOLID_shading_light_function('MATCAP')
        return {'FINISHED'} 


class SOLID_shading_light_FLAT_operator(Operator):
    bl_idname = "vht.solid_shading_light_flat"
    bl_label = "SOLID shading light FLAT operator"
    def execute(self, context):
        SOLID_shading_light_function('FLAT')
        return {'FINISHED'} 


class SOLID_shading_color_type_MATERIAL_operator(Operator):
    bl_idname = "vht.solid_shading_color_type_material"
    bl_label = "SOLID shading color type MATERIAL operator"
    def execute(self, context):
        SOLID_shading_color_type_function('MATERIAL')
        return {'FINISHED'}   


class SOLID_shading_color_type_TEXTURE_operator(Operator):
    bl_idname = "vht.solid_shading_color_type_texture"
    bl_label = "SOLID shading color type TEXTURE operator"
    def execute(self, context):
        SOLID_shading_color_type_function('TEXTURE')
        return {'FINISHED'}  

 
class SOLID_shading_show_shadows_operator(Operator):
    bl_idname = "vht.solid_shading_show_shadows"
    bl_label = "SOLID shading show_shadows operator"
    def execute(self, context):
        SOLID_shading_show_shadows_function()
        return {'FINISHED'}  


class SOLID_shading_show_cavity_operator(Operator):
    bl_idname = "vht.solid_shading_show_cavity"
    bl_label = "SOLID shading show cavity operator"
    def execute(self, context):
        SOLID_shading_show_cavity_function()
        return {'FINISHED'} 


class SOLID_shading_cavity_type_WORLD_operator(Operator):
    bl_idname = "vht.solid_cavity_type_world"
    bl_label = "SOLID shading cavity typ WORLD operator"
    def execute(self, context):
        SOLID_shading_cavity_type_function('WORLD')
        return {'FINISHED'} 
        
        
class SOLID_shading_cavity_type_SCREEN_operator(Operator):
    bl_idname = "vht.solid_cavity_type_screen"
    bl_label = "SOLID shading cavity typ SCREEN operator"
    def execute(self, context):
        SOLID_shading_cavity_type_function('SCREEN')
        return {'FINISHED'}        
        
        
class SOLID_shading_cavity_type_BOTH_operator(Operator):
    bl_idname = "vht.solid_cavity_type_both"
    bl_label = "SOLID shading cavity typ BOTH operator"
    def execute(self, context):
        SOLID_shading_cavity_type_function('BOTH')
        return {'FINISHED'}         
        
        
class SOLID_shading_show_object_outline_operator(Operator):
    bl_idname = "vht.solid_shading_show_object_outline"
    bl_label = "SOLID shading show object outline operator"
    def execute(self, context):
        SOLID_shading_show_object_outline_function()
        return {'FINISHED'}          


class SOLID_shading_show_specular_highlight_operator(Operator):
    bl_idname = "vht.solid_shading_show_specular_highlight"
    bl_label = "SOLID shading show specular highlight operator"
    def execute(self, context):
        SOLID_shading_show_specular_highlight_function()
        return {'FINISHED'} 


class Hide_sidebar_operator(Operator):
    bl_idname = "vht.hide_sidebar"
    bl_label = "Hide_sidebar_operator"
    def execute(self, context):
        Hide_sidebar_function()
        return {'FINISHED'} 


class ReFrame_Camera_Bounds_operator(Operator):
    bl_idname = "vht.reframe_camera_bounds"
    bl_label = "ReFrame_Camera_Bounds_operator"
    def execute(self, context):
        ReFrame_Camera_Bounds_function()
        return {'FINISHED'} 
        
        
class Use_Scene_Camera_operator(Operator):
    bl_idname = "vht.use_scene_camera_operator"
    bl_label = "Use_Scene_Camera_operator"
    def execute(self, context):
        Use_Scene_Camera_function(context)
        return {'FINISHED'}        
        
    
class Add_EQD180_camera_operator(Operator):
    bl_idname = "vht.add_eqd180_camera_operator"
    bl_label = "Add_EQD180_camera_operator"
    def execute(self, context):
        Add_EQD180_camera_function(context)
        return {'FINISHED'} 
        
        
class Add_VR180_camera_operator(Operator):
    bl_idname = "vht.add_vr180_camera_operator"
    bl_label = "Add_VR180_camera_operator"
    def execute(self, context):
        Add_VR180_camera_function(context)
        return {'FINISHED'} 
        
        
class Add_REL9mm_camera_operator(Operator):
    bl_idname = "vht.add_rel9mm_camera_operator"
    bl_label = "Add_REL9mm_camera_operator"
    def execute(self, context):
        Add_REL9mm_camera_function(context)
        return {'FINISHED'} 
        
        
class Add_VR360_camera_operator(Operator):
    bl_idname = "vht.add_vr360_camera_operator"
    bl_label = "Add_VR360_camera_operator"
    def execute(self, context):
        Add_VR360_camera_function(context)
        return {'FINISHED'} 
        
        
class Start_VHT_app_operator(Operator):
    bl_idname = "vht.start_vht_app_operator"
    bl_label = "Start_VHT_app_operator"
    def execute(self, context):
        Start_VHT_app_function(context)
        return {'FINISHED'}        
        
        
class End_VHT_app_operator(Operator):
    bl_idname = "vht.end_vht_app_operator"
    bl_label = "End_VHT_app_operator"
    def execute(self, context):
        End_VHT_app_function(context)
        return {'FINISHED'}        


class Render_quick_operator(Operator):
    bl_idname = "vht.render_quick_operator"
    bl_label = "Render_quick_operator"
    def execute(self, context):
        Render_function(context, 16, True, 100, False, False)#_samples, _denoise, _procent, _animation, _useFFmpeg
        return {'FINISHED'}    


class Render_1024_operator(Operator):
    bl_idname = "vht.render_1024_operator"
    bl_label = "Render_1024_operator"
    def execute(self, context):
        Render_function(context, 1024, True, 100, False, False)
        return {'FINISHED'} 


class Render_set_operator(Operator):
    bl_idname = "vht.render_4096_operator"
    bl_label = "Render_set_operator"
    def execute(self, context):
        Render_function(context, 0, False, 100, False, False)
        return {'FINISHED'}         
        

class Render_quick_video_operator(Operator):
    bl_idname = "vht.render_quick_video_operator"
    bl_label = "Render_quick_video_operator"
    def execute(self, context):
        Render_function(context, 16, True, 25, True, True)#_samples, _denoise, _procent, _animation, _useFFmpeg
        return {'FINISHED'}    


class Render_1024_video_operator(Operator):
    bl_idname = "vht.render_1024_video_operator"
    bl_label = "Render_1024_video_operator"
    def execute(self, context):
        Render_function(context, 1024, True, 100, True, True)
        return {'FINISHED'} 


class Render_set_video_operator(Operator):
    bl_idname = "vht.render_set_video_operator"
    bl_label = "Render_set_video_operator"
    def execute(self, context):
        Render_function(context, 0, False, 100, True, True)
        return {'FINISHED'} 
        
        
#Panel-------------------------------------------------------------


class VHT_PT_Panel(Panel):
    bl_idname = "VHT_PT_Panel"
    bl_label = "VHT tools v1.0.0"##version
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "VHT tools"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):    
        layout = self.layout
        obj = context.object
               
        global VHT_app
        global scene_cam_name
        
        cam_name = context.scene.camera.name
        if(scene_cam_name != cam_name):
            scene_cam_name = cam_name
            #check_AR()
            Signal_to_VHT(Signal_string()) 
            #ReFrame_Camera_Bounds_function() 

        vhtscreeenexist = False
        for screen in bpy.data.screens: 
            if(screen.name == "VHT_screen"):
                vhtscreeenexist = True
                break

        layout.label(text="VHT app:")
        col = layout.column(align=True)
        if(VHT_app == 0):
            if(vhtscreeenexist):
                col.operator(Start_VHT_app_operator.bl_idname, text="Launch VR session")
            else:
                layout.label(text="Need VR stereoscopic window!")              
        else:
            col.operator(End_VHT_app_operator.bl_idname, text="End VR session")

        layout.separator()             
        layout.label(text="VHT control:")
        col = layout.column(align=True)
        if(VHT_app):
            col.operator(GUI_repose_operator.bl_idname, text="GUI repose")
            col.operator(GUI_on_off_operator.bl_idname, text="GUI ON-OFF")
            col.operator(HMD_repose_operator.bl_idname, text="HMD repose")
            col.operator(GUI_desktop_on_off_operator.bl_idname, text="Desktops <-> VR View")
            col.operator(Level_update_operator.bl_idname, text="Level Update (tilted view)")
            col.operator(Level_zero_operator.bl_idname, text="Level Zero (front view)")
        else:
            layout.label(text="Need VHT app to run!")

        layout.separator() 
        layout.label(text="Create VR stereoscopic window:")
        col = layout.column(align=True)
        if(vhtscreeenexist == False):
            col.operator(Create_Window_SbS_EQD180_Operator.bl_idname, text="EQD180 SbS crosseye")
            col.operator(Create_Window_SbS_VR180_Operator.bl_idname, text="VR180 SbS crosseye")
            col.operator(Create_Window_SbS_VR360_Operator.bl_idname, text="VR360 SbS")
        else:
            layout.label(text="On 2nd display and full screen!")
            layout.label(text="Press Numpad 0 for camera view!")
            layout.label(text="Change camera at Scene Properies!")
            
        layout.separator()  
        layout.label(text="Add VR stereoscopic camera:")
        col = layout.column(align=True)
        col.operator(Add_EQD180_camera_operator.bl_idname, text="EQD180")
        col.operator(Add_REL9mm_camera_operator.bl_idname, text="REL9mm")
        col.operator(Add_VR180_camera_operator.bl_idname, text="VR180")
        col.operator(Add_VR360_camera_operator.bl_idname, text="VR360")




        layout.separator()         
        layout.label(text="Render engine:")
        col = layout.column(align=True)  
        
        if(bpy.context.scene.render.engine == 'BLENDER_EEVEE' ):
            col.operator(Render_engine_EEVEE_operator.bl_idname, text="-----EEVEE-----")
        else:
            col.operator(Render_engine_EEVEE_operator.bl_idname, text="EEVEE")
        
        if(bpy.context.scene.render.engine == 'BLENDER_WORKBENCH' ):
            col.operator(Render_engine_WORKBENCH_operator.bl_idname, text="-----WORKBENCH-----")
        else:
            col.operator(Render_engine_WORKBENCH_operator.bl_idname, text="WORKBENCH")

        if(bpy.context.scene.render.engine == 'CYCLES' ):
            col.operator(Render_engine_CYCLES_operator.bl_idname, text="-----CYCLES-----")
        else:
            col.operator(Render_engine_CYCLES_operator.bl_idname, text="CYCLES")


        layout.separator()         
        layout.label(text="Render settings:")
        col = layout.column(align=True)
        col.operator(Render_settings_4k4k_operator.bl_idname, text="4Kx4K for EQD, REL or VR180")
        col.operator(Render_settings_8k4k_operator.bl_idname, text="8Kx4K for VR360")
        
        
        

        layout.separator()             
        layout.label(text="Shading:")
        col = layout.column(align=True)    
        shadingtype = getshadintype()        
        if(vhtscreeenexist):       
            #shadingtype = getshadintype()
            if(shadingtype == 'WIREFRAME' ):
                col.operator(Shading_WIREFRAME_operator.bl_idname, text="-----Wireframe-----")
            else:
                col.operator(Shading_WIREFRAME_operator.bl_idname, text="Wireframe")
            
            if(shadingtype == 'SOLID' ):
                col.operator(Shading_SOLID_operator.bl_idname, text="-----Solid-----")
            else:
                col.operator(Shading_SOLID_operator.bl_idname, text="Solid")
           
            if(bpy.context.scene.render.engine != 'BLENDER_WORKBENCH'):
                if(shadingtype == 'MATERIAL' ):
                    col.operator(Shading_MATERIAL_operator.bl_idname, text="-----Material-----")
                else:
                    col.operator(Shading_MATERIAL_operator.bl_idname, text="Material")
           
            if(shadingtype == 'RENDERED' ):
                col.operator(Shading_RENDERED_operator.bl_idname, text="-----Rendered-----")
            else:
                col.operator(Shading_RENDERED_operator.bl_idname, text="Rendered")


        if(shadingtype == 'SOLID' ):
            layout.separator()             
            layout.label(text="Light:")  
            col = layout.column(align=True)             
            light = getlight()
            if(light == 'STUDIO'):
                col.operator(SOLID_shading_light_STUDIO_operator.bl_idname, text="-----STUDIO-----")
            else:
                col.operator(SOLID_shading_light_STUDIO_operator.bl_idname, text="STUDIO")
            if(light == 'MATCAP'):
                col.operator(SOLID_shading_light_MATCAP_operator.bl_idname, text="-----MATCAP-----")
            else:
                col.operator(SOLID_shading_light_MATCAP_operator.bl_idname, text="MATCAP")                
            if(light == 'FLAT'):
                col.operator(SOLID_shading_light_FLAT_operator.bl_idname, text="-----FLAT-----")
            else:
                col.operator(SOLID_shading_light_FLAT_operator.bl_idname, text="FLAT")


            layout.label(text="Color type:")   
            col = layout.column(align=True) 
            color_type = getcolortype()
            if(color_type == 'MATERIAL'):
                col.operator(SOLID_shading_color_type_MATERIAL_operator.bl_idname, text="-----MATERIAL-----")
            else:
                col.operator(SOLID_shading_color_type_MATERIAL_operator.bl_idname, text="MATERIAL")
            if(color_type == 'TEXTURE'):
                col.operator(SOLID_shading_color_type_TEXTURE_operator.bl_idname, text="-----TEXTURE-----")
            else:
                col.operator(SOLID_shading_color_type_TEXTURE_operator.bl_idname, text="TEXTURE")


            layout.label(text="Show shadows:")     
            col = layout.column(align=True) 
            show_shadows = getshowshadows()
            if(show_shadows):
                col.operator(SOLID_shading_show_shadows_operator.bl_idname, text="True")
            else:
                col.operator(SOLID_shading_show_shadows_operator.bl_idname, text="False")
                

            layout.label(text="Cavity type:")   
            col = layout.column(align=True)
            show_cavity = getshowcavity()
            cavity_type = getcavitytype()
            if(show_cavity == False):
                col.operator(SOLID_shading_show_cavity_operator.bl_idname, text="-----Off-----")
            else:
                col.operator(SOLID_shading_show_cavity_operator.bl_idname, text="Off")
            if(cavity_type == 'WORLD' and show_cavity):
                col.operator(SOLID_shading_cavity_type_WORLD_operator.bl_idname, text="-----WORLD-----")
            else:
                col.operator(SOLID_shading_cavity_type_WORLD_operator.bl_idname, text="WORLD")
            if(cavity_type == 'SCREEN' and show_cavity):
                col.operator(SOLID_shading_cavity_type_SCREEN_operator.bl_idname, text="-----SCREEN-----")
            else:
                col.operator(SOLID_shading_cavity_type_SCREEN_operator.bl_idname, text="SCREEN")                
            if(cavity_type == 'BOTH' and show_cavity):
                col.operator(SOLID_shading_cavity_type_BOTH_operator.bl_idname, text="-----BOTH-----")
            else:
                col.operator(SOLID_shading_cavity_type_BOTH_operator.bl_idname, text="BOTH")


            layout.label(text="Show object outline:")    
            col = layout.column(align=True)             
            show_object_outline = getshowobjectoutline()
            if(show_object_outline):
                col.operator(SOLID_shading_show_object_outline_operator.bl_idname, text="True")
            else:
                col.operator(SOLID_shading_show_object_outline_operator.bl_idname, text="False")
                
                
            layout.label(text="Show specular highlight:")      
            col = layout.column(align=True) 
            show_specular_highlight = getshowspecularhighlight()            
            if(show_specular_highlight):
                col.operator(SOLID_shading_show_specular_highlight_operator.bl_idname, text="True")
            else:
                col.operator(SOLID_shading_show_specular_highlight_operator.bl_idname, text="False")




         
        layout.separator()             
        layout.label(text="Miscellaneous:")
        col = layout.column(align=True)
        col.operator(Hide_sidebar_operator.bl_idname, text="Hide sidebars")
        col.operator(ReFrame_Camera_Bounds_operator.bl_idname, text="ReFrame Camera Bounds")
        col.operator(Use_Scene_Camera_operator.bl_idname, text="Use Scene Camera")


        layout.separator()         
        layout.label(text="Start to render IMAGE:")
        col = layout.column(align=True)
        col.operator(Render_quick_operator.bl_idname, text="Quick at 16 samples + den")
        col.operator(Render_1024_operator.bl_idname, text="at 1024 samples + den")
        col.operator(Render_set_operator.bl_idname, text="as SET")
               
               
        layout.separator()         
        layout.label(text="Start to render VIDEO:")
        col = layout.column(align=True)
        col.operator(Render_quick_video_operator.bl_idname, text="Quick at 25% + 16 sam + den")
        col.operator(Render_1024_video_operator.bl_idname, text="at 1024 samples + den")
        col.operator(Render_set_video_operator.bl_idname, text="as SET")
        

#Registration-----------------------------------------------------------


def register():
    bpy.utils.register_class(VHT_PT_Panel)    

    bpy.utils.register_class(Start_VHT_app_operator)
    bpy.utils.register_class(End_VHT_app_operator)

    bpy.utils.register_class(Add_EQD180_camera_operator)  
    bpy.utils.register_class(Add_VR180_camera_operator)  
    bpy.utils.register_class(Add_REL9mm_camera_operator)  
    bpy.utils.register_class(Add_VR360_camera_operator)  
    
    bpy.utils.register_class(Create_Window_SbS_EQD180_Operator)
    bpy.utils.register_class(Create_Window_SbS_VR180_Operator)
    bpy.utils.register_class(Create_Window_SbS_VR360_Operator)
    
    bpy.utils.register_class(Shading_WIREFRAME_operator)
    bpy.utils.register_class(Shading_SOLID_operator)
    bpy.utils.register_class(Shading_MATERIAL_operator)
    bpy.utils.register_class(Shading_RENDERED_operator)
    
    bpy.utils.register_class(Render_engine_EEVEE_operator)        
    bpy.utils.register_class(Render_engine_WORKBENCH_operator)  
    bpy.utils.register_class(Render_engine_CYCLES_operator)  
        
    bpy.utils.register_class(Hide_sidebar_operator)         
    bpy.utils.register_class(ReFrame_Camera_Bounds_operator)      
    bpy.utils.register_class(Use_Scene_Camera_operator)    
    
    bpy.utils.register_class(GUI_desktop_on_off_operator)    
    bpy.utils.register_class(GUI_repose_operator)    
    bpy.utils.register_class(GUI_on_off_operator)    
    bpy.utils.register_class(HMD_repose_operator)    
    bpy.utils.register_class(Level_update_operator)  
    bpy.utils.register_class(Level_zero_operator)  
    
    bpy.utils.register_class(Render_settings_4k4k_operator)    
    bpy.utils.register_class(Render_settings_8k4k_operator)   
    
    bpy.utils.register_class(Render_quick_operator)  
    bpy.utils.register_class(Render_1024_operator)  
    bpy.utils.register_class(Render_set_operator)  
    
    bpy.utils.register_class(Render_quick_video_operator)  
    bpy.utils.register_class(Render_1024_video_operator)  
    bpy.utils.register_class(Render_set_video_operator)  
    
    bpy.utils.register_class(SOLID_shading_light_STUDIO_operator)
    bpy.utils.register_class(SOLID_shading_light_MATCAP_operator)  
    bpy.utils.register_class(SOLID_shading_light_FLAT_operator)
    bpy.utils.register_class(SOLID_shading_color_type_MATERIAL_operator)     
    bpy.utils.register_class(SOLID_shading_color_type_TEXTURE_operator)    
    bpy.utils.register_class(SOLID_shading_show_shadows_operator)
    bpy.utils.register_class(SOLID_shading_show_cavity_operator)
    bpy.utils.register_class(SOLID_shading_cavity_type_WORLD_operator)      
    bpy.utils.register_class(SOLID_shading_cavity_type_SCREEN_operator)
    bpy.utils.register_class(SOLID_shading_cavity_type_BOTH_operator)     
    bpy.utils.register_class(SOLID_shading_show_object_outline_operator)
    bpy.utils.register_class(SOLID_shading_show_specular_highlight_operator)   
    
    
    
def unregister():
    bpy.utils.unregister_class(VHT_PT_Panel)

    bpy.utils.unregister_class(Start_VHT_app_operator)
    bpy.utils.unregister_class(End_VHT_app_operator)
    
    bpy.utils.unregister_class(Add_EQD180_camera_operator)  
    bpy.utils.unregister_class(Add_VR180_camera_operator)  
    bpy.utils.unregister_class(Add_REL9mm_camera_operator)  
    bpy.utils.unregister_class(Add_VR360_camera_operator) 
    
    bpy.utils.unregister_class(Create_Window_SbS_EQD180_Operator)
    bpy.utils.unregister_class(Create_Window_SbS_VR180_Operator)
    bpy.utils.unregister_class(Create_Window_SbS_VR360_Operator)
    
    bpy.utils.unregister_class(Shading_WIREFRAME_operator)
    bpy.utils.unregister_class(Shading_SOLID_operator)
    bpy.utils.unregister_class(Shading_MATERIAL_operator)
    bpy.utils.unregister_class(Shading_RENDERED_operator)

    bpy.utils.unregister_class(Render_engine_EEVEE_operator)        
    bpy.utils.unregister_class(Render_engine_WORKBENCH_operator)  
    bpy.utils.unregister_class(Render_engine_CYCLES_operator)   
    
    bpy.utils.unregister_class(Hide_sidebar_operator) 
    bpy.utils.unregister_class(ReFrame_Camera_Bounds_operator)         
    bpy.utils.unregister_class(Use_Scene_Camera_operator)   

    bpy.utils.unregister_class(GUI_desktop_on_off_operator)    
    bpy.utils.unregister_class(GUI_repose_operator)    
    bpy.utils.unregister_class(GUI_on_off_operator)    
    bpy.utils.unregister_class(HMD_repose_operator)   
    bpy.utils.unregister_class(Level_update_operator) 
    bpy.utils.unregister_class(Level_zero_operator)  

    bpy.utils.unregister_class(Render_settings_4k4k_operator)    
    bpy.utils.unregister_class(Render_settings_8k4k_operator) 
    
    bpy.utils.unregister_class(Render_quick_operator) 
    bpy.utils.unregister_class(Render_1024_operator)
    bpy.utils.unregister_class(Render_set_operator)
    
    bpy.utils.unregister_class(Render_quick_video_operator) 
    bpy.utils.unregister_class(Render_1024_video_operator)
    bpy.utils.unregister_class(Render_set_video_operator)
    
    bpy.utils.unregister_class(SOLID_shading_light_STUDIO_operator)
    bpy.utils.unregister_class(SOLID_shading_light_MATCAP_operator)
    bpy.utils.unregister_class(SOLID_shading_light_FLAT_operator)
    bpy.utils.unregister_class(SOLID_shading_color_type_MATERIAL_operator)
    bpy.utils.unregister_class(SOLID_shading_color_type_TEXTURE_operator)
    bpy.utils.unregister_class(SOLID_shading_show_shadows_operator)
    bpy.utils.unregister_class(SOLID_shading_show_cavity_operator)
    bpy.utils.unregister_class(SOLID_shading_cavity_type_WORLD_operator)
    bpy.utils.unregister_class(SOLID_shading_cavity_type_SCREEN_operator)
    bpy.utils.unregister_class(SOLID_shading_cavity_type_BOTH_operator)
    bpy.utils.unregister_class(SOLID_shading_show_object_outline_operator)
    bpy.utils.unregister_class(SOLID_shading_show_specular_highlight_operator)

    
#-----------------------------------------------------------


if __name__ == "__main__":
    register()
