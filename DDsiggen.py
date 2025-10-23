# This script takes multiple individual image files and generates composite images that can be used as a user signature on web forums.
# (c) by Tierparkzone
# This script is provided under the MIT license (see attached 'LICENSE' file).

from nicegui import ui, events, app, native
from PIL import ImageOps, Image, ImageDraw, ImageTransform, ImageFilter, ImageFont
from pathlib import Path
from io import BytesIO
import os
import math
import asyncio
#import requests
#import imageio as iio

#Version Number
version_no = "0.17"



## Functions

#Import Images

def import_quick(wait_dialog):
	global quick_updated_flag
	global quick_undoable_flag
	global I_scaled
	global I_scaled_bak
	global images
	global images_bak
	
	quick_updated_flag = False
	quick_undoable_flag = False

	print("Importing...")
	images = []
	f_images = os.listdir(".")
	for file in f_images:
		if file.endswith((".jpg", ".png", ".jpeg", ".JPG", ".PNG", ".JPEG")):
			images.append(file)

	I_fullscale = []
	for image in images:
		I_fullscale.append(Image.open(image))

	I_scaled = []
	for image in I_fullscale:
		ImageOps.exif_transpose(image=image, in_place=True)
		I_scaled.append(ImageOps.fit(image=image, size=[200,200], method=Image.Resampling.LANCZOS, centering=[0.5,0.0]))

	I_scaled_bak = I_scaled.copy()
	images_bak = images.copy()
	quick_ui_imgSettings.refresh()
	quick_update_buttons()
	wait_dialog.close()
	ui.notify(f"{len(I_scaled)} photos found")
	print("Quick Import Completed!")

async def import_quick_alert():
	with ui.dialog().props("persistent") as import_quick_dialog, ui.card():
		ui.label("Any changes to the list of photos (Step 01.) will be lost. \n This cannot be undone!").style("white-space:pre-wrap;")
		with ui.row():
			ui.button("Re-Scan",on_click=lambda: import_quick_dialog.submit(True)).style("width:200px;")
			ui.button("Abort",on_click=lambda: import_quick_dialog.submit(False)).props("color=positive").style("width:200px;")
	is_continue = await import_quick_dialog
	if is_continue:
		import_quick_launch()

def import_quick_launch():
	with ui.dialog().props("persistent") as wait_dialog, ui.card():
		with ui.row():
			ui.spinner()
			ui.label("Importing...")
	wait_dialog.on("show",lambda:import_quick(wait_dialog))
	wait_dialog.open()

'''
def import_from_url(image_url):
	if image_url:
		url_response = requests.get(image_url)
		new_image = Image.open(BytesIO(url_response.content))
		return(new_image)
'''

#Import other data

def import_namesE():
	if os.path.isfile("names.txt"):
		f_namesE = open("names.txt","r",encoding="utf-8")
		namesE = f_namesE.readlines()
		namesE = [i.rstrip() for i in namesE]
	else:
		namesE = []
	return(namesE)


def import_namesJ():
	if os.path.isfile("namesJ.txt"):
		f_namesJ = open("namesJ.txt","r",encoding="utf-8")
		namesJ = f_namesJ.readlines()
		namesJ = [i.rstrip() for i in namesJ]
	else:
		namesJ = []
	return(namesJ)


#Rename
		
def rename_char(e: events.GenericEventArguments) -> None:
    for row in new_rows:
        if row['id'] == e.args['id']:
            row.update(e.args)
    table.update()


#Reorder Images

def I_scaled_moveup(current_idx) -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_scaled
	global I_scaled_undo
	global images
	global images_undo
	if current_idx>0:
		quick_updated_flag = False
		#ui.notify(f"Moved down {current_idx}.")
		I_scaled_undo = I_scaled.copy()
		images_undo = images.copy()
		I_scaled.insert(current_idx-1, I_scaled.pop(current_idx))
		images.insert(current_idx-1, images.pop(current_idx))
		quick_undoable_flag = True
	quick_list_imgDisplay.refresh()
	quick_update_buttons()
		
def I_scaled_movedn(current_idx) -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_scaled
	global I_scaled_undo
	global images
	global images_undo
	if current_idx<len(I_scaled)-1:
		quick_updated_flag = False
		#ui.notify(f"Moved up {current_idx}.")
		I_scaled_undo = I_scaled.copy()
		images_undo = images.copy()
		I_scaled.insert(current_idx+1, I_scaled.pop(current_idx))
		images.insert(current_idx+1, images.pop(current_idx))
		quick_undoable_flag = True
	quick_list_imgDisplay.refresh()
	quick_update_buttons()
	
def I_scaled_delete(current_idx) -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_scaled
	global I_scaled_undo
	global images
	global images_undo
	quick_updated_flag = False
	#ui.notify(f"Deleted {current_idx}.")
	I_scaled_undo = I_scaled.copy()
	images_undo = images.copy()
	I_scaled.pop(current_idx)
	images.pop(current_idx)
	ui.notify("Photo removed from list")
	quick_undoable_flag = True
	quick_list_imgDisplay.refresh()
	quick_update_buttons()
	
def I_scaled_reset() -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_scaled
	global I_scaled_undo
	global I_scaled_bak
	global images
	global images_undo
	global images_bak
	quick_updated_flag = False
	I_scaled_undo = I_scaled.copy()
	images_undo = images.copy()
	I_scaled = I_scaled_bak.copy()
	images = images_bak.copy()
	ui.notify("List of photos was reset")
	quick_undoable_flag = True
	quick_list_imgDisplay.refresh()
	quick_update_buttons()

def I_scaled_undofunc() -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_scaled
	global I_scaled_undo
	global images
	global images_undo
	quick_updated_flag = False
	quick_undoable_flag = False
	I_scaled = I_scaled_undo.copy()
	images = images_undo.copy()
	ui.notify("Last operation undone")
	quick_list_imgDisplay.refresh()
	quick_update_buttons()
	

#Generate Layout

def generate_quicklayout():
	global layout_images_target
	global quick_updated_flag
	global quick_generated_flag
	global layout_images
	global layout_columns
	global layout_rows
	global layout_pad
	nchar = len(I_scaled)
	
	if nchar==0:
		layout_images=0
		layout_rows=0
		layout_columns=0
		layout_pad=0
		return()
	elif layout_images_target.value == "One Image":
		layout_images=1
	elif layout_images_target.value == "Two Images" and nchar>1:
		layout_images=2
	elif nchar<6:
		layout_images=1
	else:
		layout_images=2	
	
	if layout_images == 2:
		nchar_img=math.ceil(nchar/layout_images)
	else:
		nchar_img=nchar
	
	if nchar_img<6:
		layout_rows=1
		layout_columns=nchar_img
	elif nchar_img<17:
		layout_rows=2
		layout_columns=math.ceil(nchar_img/layout_rows)
	elif nchar_img<34:
		layout_rows=3
		layout_columns=math.ceil(nchar_img/layout_rows)
	else:	
		layout_rows=4
		layout_columns=math.ceil(nchar_img/layout_rows)
	layout_total=layout_rows*layout_columns*layout_images
	layout_pad=layout_total-nchar
	if layout_images==1:
		ui.notify(f"{layout_images} image with {layout_columns} by {layout_rows} photos. {layout_pad} padding.")
	else:
		ui.notify(f"{layout_images} images with {layout_columns} by {layout_rows} photos, {layout_pad} padding")
	quick_updated_flag = True
	quick_generated_flag = False
	quick_ui_layoutDisplay.refresh()
	quick_update_buttons()
	#return(layout_images,layout_rows,layout_columns,layout_pad)

def force_quicklayout():
	global quick_updated_flag
	quick_updated_flag = False
	quick_update_buttons()


#Generate Signature

def generate_quicksig():
	global quick_generated_flag
	I_masked=mask_images()
	combine_images(I_masked)
	scale_signature()
	quick_generated_flag=True
	quick_ui_sigDisplay.refresh()

def mask_images():
	I_masked=[]
	for image in I_scaled:
		image_masked = image.copy()
		I_masked.append(image_masked)
	for image in I_masked:
		image.putalpha(aMask_select)
	return(I_masked)
		
def combine_images(I_masked):
	global sig01
	global sig02
	n_char = len(I_masked)
	i_char=0
	
	sig01=Image.new("RGBA",(200*layout_columns,200*layout_rows),(0,0,0,0))
	i_rows=0
	while i_rows<layout_rows:
		i_columns=0
		while i_columns<layout_columns:
			if i_char<n_char:
				sig01.paste(I_masked[i_char],(200*i_columns,200*i_rows))
				#print(f"{i_char}:image01,row{i_rows},column{i_columns}...")
				i_char=i_char+1
			i_columns=i_columns+1
		i_rows=i_rows+1
	
	if layout_images>1:
		sig02=Image.new("RGBA",(200*layout_columns,200*layout_rows),(0,0,0,0))
		i_rows=0
		while i_rows<layout_rows:
			i_columns=0
			while i_columns<layout_columns:
				if i_char<n_char:
					sig02.paste(I_masked[i_char],(200*i_columns,200*i_rows))
					#print(f"{i_char}:image02,row{i_rows},column{i_columns}...")
					i_char=i_char+1
				i_columns=i_columns+1
			i_rows=i_rows+1
	else:
		sig02=0

def scale_signature():
	global sig01
	global sig02
	sig01 = ImageOps.contain(image=sig01, size=[550,200], method=Image.Resampling.LANCZOS)
	if sig02!=0:
		sig02 = ImageOps.contain(image=sig02, size=[550,200], method=Image.Resampling.LANCZOS)


def save_quicksig():
	global sig01
	global sig02
	global quick_export_flag
	os.makedirs("./signatures", exist_ok=True)
	if sig01!=0:
		sig01.save("./signatures/qicksig_001.png")
		ui.notify("First image saved as 'qicksig_001.png' in 'signatures'")
	if sig02!=0:
		sig02.save("./signatures/qicksig_002.png")
		ui.notify("Second image saved as 'qicksig_002.png' in 'signatures'")
	quick_export_flag=True
	quick_ui_sigExport.refresh()


#Extra Functionality

def quick_update_buttons():
	quick_button_undoDisplay.refresh()
	quick_button_updateLayout.refresh()
	quick_button_genSig.refresh()
	quick_button_exportSig.refresh()

def exit_application():
	with ui.dialog().props("persistent maximized") as exit_dialog, ui.card():
		ui.label("Application terminated! You can now close this browser tab.")
	exit_dialog.open()
	app.shutdown()


## Script starts here ############################################################	

print("Please wait a moment while the application is starting...")


## Initialize Globals and Flags

quick_undoable_flag=False
quick_updated_flag=False
quick_generated_flag=False
quick_export_flag=False

select_alphamask = "circle"

images=[]
images_undo=[]
images_bak=[]
I_scaled=[]
I_scaled_undo=[]
I_scaled_bak=[]
layout_images=0
layout_rows=0
layout_columns=0
layout_pad=0
sig01=0
sig02=0

## Import local files


	
# Create Alpha-Masks

aMask_circle = Image.new(mode="L", size=[600,600], color=0)
ImageDraw.Draw(aMask_circle).ellipse(xy=[(4,4),(595,595)], fill=255)
aMask_circle = ImageOps.contain(image=aMask_circle, size=[200,200], method=Image.Resampling.LANCZOS)

aMask_blrcir = Image.new(mode="L", size=[600,600], color=0)
ImageDraw.Draw(aMask_blrcir).ellipse(xy=[(23,23),(576,576)], fill=255)
aMask_blrcir = aMask_blrcir.filter(ImageFilter.GaussianBlur(radius=12.0))
aMask_blrcir = ImageOps.contain(image=aMask_blrcir, size=[200,200], method=Image.Resampling.LANCZOS)

aMask_square = Image.new(mode="L", size=[200,200], color=255)

aMask_sqedge = Image.new(mode="L", size=[200,200], color=0)
ImageDraw.Draw(aMask_sqedge).rectangle(xy=[(4,4),(195,195)], fill=255)

aMask_blrsqr = Image.new(mode="L", size=[600,600], color=0)
ImageDraw.Draw(aMask_blrsqr).rectangle(xy=[(23,23),(576,576)], fill=255)
aMask_blrsqr = aMask_blrsqr.filter(ImageFilter.GaussianBlur(radius=12.0))
aMask_blrsqr = ImageOps.contain(image=aMask_blrsqr, size=[200,200], method=Image.Resampling.LANCZOS)

aMask_rndrec = Image.new(mode="L", size=[600,600], color=0)
ImageDraw.Draw(aMask_rndrec).rounded_rectangle(xy=[(9,9),(590,590)], radius=60, fill=255)
aMask_rndrec = ImageOps.contain(image=aMask_rndrec, size=[200,200], method=Image.Resampling.LANCZOS)

aMask_blrdrc = Image.new(mode="L", size=[600,600], color=0)
ImageDraw.Draw(aMask_blrdrc).rounded_rectangle(xy=[(23,23),(576,576)], radius=60, fill=255)
aMask_blrdrc = aMask_blrdrc.filter(ImageFilter.GaussianBlur(radius=12.0))
aMask_blrdrc = ImageOps.contain(image=aMask_blrdrc, size=[200,200], method=Image.Resampling.LANCZOS)

aMask_skdrec = Image.new(mode="L", size=[600,600], color=0)
ImageDraw.Draw(aMask_skdrec).rounded_rectangle(xy=[(0,9),(539,590)], radius=60, fill=255)
aMask_skdrec = aMask_skdrec.transform(aMask_skdrec.size,Image.AFFINE,(1,0.1,-60,0,1,0),resample=Image.Resampling.BICUBIC)
aMask_skdrec = ImageOps.contain(image=aMask_skdrec, size=[200,200], method=Image.Resampling.LANCZOS)

aMask_blskrc = Image.new(mode="L", size=[600,600], color=0)
ImageDraw.Draw(aMask_blskrc).rounded_rectangle(xy=[(13,23),(526,576)], radius=60, fill=255)
aMask_blskrc = aMask_blskrc.transform(aMask_blskrc.size,Image.AFFINE,(1,0.1,-60,0,1,0),resample=Image.Resampling.BICUBIC)
aMask_blskrc = aMask_blskrc.filter(ImageFilter.GaussianBlur(radius=12.0))
aMask_blskrc = ImageOps.contain(image=aMask_blskrc, size=[200,200], method=Image.Resampling.LANCZOS)

aMask_select = aMask_circle

# Image to indicate padding 
padding_image = Image.new(mode="RGB", size=[200,200], color="#6b6868")
#dd = ImageDraw.Draw(padding_image)
#dd.text((15,85),"PADDING",fill="#ffffff",font=ImageFont.truetype("fonts/GenEiPOPle-Bk.ttf",30))



## UI starts here ################################################################

ui.colors(primary="#ff6065", secondary="#896566", accent="#e4e2e2", positive="#6b6868")
dark_mode=ui.dark_mode()
dark_mode.enable()
ui.add_head_html("<style>body{background-color:#f2f0f0;}</style>")
ui.add_css(".default_tooltip{font-size:14px;}")


with ui.header().classes(replace='row items-center') as header:
	with ui.tabs() as modeSelect:
		ui.tab("Quick Sig")
		ui.tab("Create New")
		ui.tab("Load Config")
	ui.space()
	ui.label(f"Tierparkzone's Forum Signature Generator - ver.{version_no}")
	ui.element("spacer").style("width:25px;")
	with ui.button(icon="o_nights_stay",color="secondary",on_click=dark_mode.toggle).style("width:40px; height:40px"):
		ui.tooltip("Toggle Dark Mode").classes("default_tooltip")
	ui.element("spacer").style("width:15px;")
	with ui.button(icon="o_close",color="secondary",on_click=lambda:exit_application()).style("width:40px; height:40px"):
		ui.tooltip("Exit Application").classes("default_tooltip")
	ui.element("spacer").style("width:15px;")


## Quick Sig Panel

with ui.tab_panels(modeSelect, value="Quick Sig").classes("w-full"):
	with ui.tab_panel("Quick Sig"):
		ui.label("QUICKLY GENERATE A SIMPLE SIGNATURE.")
		with ui.row(wrap=True):
			ui.label("How to use:")
			ui.label("Place the photos you want to use in your signature into the same folder as this executable, then hit 'SCAN FOLDER'. If your photos show up below, you're good to go.").style("max-width:450px;")
		
		@ui.refreshable
		def quick_button_undoDisplay () -> None:
			if quick_undoable_flag:
				ui.button("Undo", on_click=lambda:I_scaled_undofunc()).style("width:200px;")
			else:
				with ui.button("Undo", color="accent").style("width:200px;").props("disable"):
					ui.tooltip("Cannot undo any further.").classes("default_tooltip")
		
		@ui.refreshable
		def quick_button_updateLayout() -> None:
			if quick_updated_flag:
				with ui.button("Update Layout",color="accent").style("width:200px;").props("disable"):
					ui.tooltip("Already up to date").classes("default_tooltip")
			else:
				ui.button("Update Layout",on_click=lambda:generate_quicklayout()).style("width:200px;")
		
		@ui.refreshable
		def quick_button_genSig() -> None:
			if quick_updated_flag:
				ui.button("Generate Signature", on_click=lambda:generate_quicksig()).style("width:200px;")
			else:
				with ui.button("Generate Signature", color="accent").style("width:200px;"):
					ui.tooltip("Please update the layout!").classes("default_tooltip")
					
		@ui.refreshable
		def quick_button_exportSig() -> None:
			if quick_updated_flag and quick_generated_flag:
				ui.button("Export Files", icon="o_save", on_click=lambda:save_quicksig()).style("width:200px;")
			else:
				with ui.button("Export Files", icon="o_save", color="accent").style("width:200px;").props("disable"):
					ui.tooltip("Please re-generate the signature!").props("max-width='200px'").classes("default_tooltip")

		@ui.refreshable
		def quick_list_imgDisplay() -> None:
			with ui.row(wrap=True):
				for idx, image in enumerate(I_scaled):
					with ui.grid(columns="80px 40px 80px").classes("gap-0"):
						ui.image(image).props(f"width=200px height=200px").classes("col-span-full")
						with ui.button_group().style("width: 200px;"):
							if idx==0:
								ui.button(icon="o_chevron_left", color="accent").style("width:80px;").props("disable")
							else:
								ui.button(icon="o_chevron_left", on_click=lambda iid=idx:I_scaled_moveup(iid)).style("width:80px;")
							if len(I_scaled)<=1:
								ui.button(icon="o_delete", color="accent").style("width:40px;").props("disable")
							else:
								with ui.button(icon="o_delete", color="secondary", on_click=lambda iid=idx:I_scaled_delete(iid)).style("width:40px;"):
									ui.tooltip("Remove photo from list").classes("default_tooltip")
							if idx==len(I_scaled)-1:
								ui.button(icon="o_chevron_right", color="accent").style("width:80px;").props("disable")
							else:
								ui.button(icon="o_chevron_right", on_click=lambda iid=idx:I_scaled_movedn(iid)).style("width:80px;")

		@ui.refreshable
		def quick_ui_imgSettings() -> None:
			global layout_images_target
			if I_scaled:
				with ui.button("Re-Scan",on_click=lambda:import_quick_alert()).style("width:200px;"):
					ui.tooltip("If you have changed any photo files in the folder, use this to update the list of photos.").props("max-width='200px'").classes("default_tooltip")
			else:
				ui.button("Scan Folder",on_click=lambda:import_quick_launch()).style("width:200px;")
			
			ui.separator()

			if I_scaled:
				ui.label("01. Reorder or remove photos:")
				ui.label("Use the arrow buttons to reorder photos in the list as desired. Unwanted photos can be removed with the 'Trash' button. If you would like to start over, use the 'RESET LIST' button. The most recent action can be undone.").style("max-width:550px;")
				quick_list_imgDisplay()
				with ui.row(wrap=True):
					quick_button_undoDisplay()
					with ui.button("Reset List", on_click=lambda:I_scaled_reset()).style("width:200px;"):
						ui.tooltip("Reset the list of photos without scanning for new files.").props("max-width='200px'").classes("default_tooltip")

				ui.separator()

				ui.label("02. Confirm layout:")
				ui.label("Once the list of photos is sorted to your liking, click 'UPDATE LAYOUT'. This will generate a preview of how the photos will be arranged in your signature. Slots marked with 'Padding' will be left empty in the final signature. You can force all photos into a single signature image or spread them out over two. The photos above can still be reordered. - Then hit 'UPDATE LAYOUT' again.").style("max-width:550px;")
				with ui.row(wrap=True):
					quick_button_updateLayout()
					layout_images_target = ui.radio(["Auto", "One Image", "Two Images"], value="Auto", on_change=lambda:force_quicklayout()).props("inline")

		quick_ui_imgSettings()

		@ui.refreshable
		def quick_ui_layoutDisplay() -> None:
			if layout_images>0 and I_scaled:
				#ui.label("OK!")
				imgsizeX=math.floor(550/layout_columns)
				imgsizeY=math.floor(200/layout_rows)
				imgsize=min([imgsizeX,imgsizeY])
				imgsizeXX=imgsize*layout_columns
				imgsizeYY=imgsize*layout_rows
				
				ui.label("First Signature Image:")
				with ui.row(wrap=True):
					imgY=1
					imgN=0
					with ui.column():
						while imgY<=layout_rows:
							imgX=1
							with ui.row():
								while imgX<=layout_columns:
									if imgN<len(I_scaled):
										ui.image(I_scaled[imgN]).props(f"width={imgsize}px height={imgsize}px")
									else:
										with ui.image(padding_image).props(f"width={imgsize}px height={imgsize}px"):
											ui.label("Padding").style(f"width:{imgsize}px; height:{imgsize}px;").classes(f"text-white bg-positive overflow-hidden text-ellipsis")
									imgN=imgN+1
									imgX=imgX+1
							imgY=imgY+1
					ui.element("spacer").style("width:15px;")
					with ui.column():
						if layout_images==1:
							ui.label(f"{layout_columns} by {layout_rows} photos, {layout_pad} padding")
						else:
							ui.label(f"{layout_columns} by {layout_rows} photos")
						ui.label(f"Signature image size: {layout_columns*imgsize}px by {layout_rows*imgsize}px")
						ui.label(f"Individual photo size:{imgsize}px by {imgsize}px")
					
				if layout_images>1:
					ui.label("Second Signature Image:")
					with ui.row(wrap=True):
						imgY=1
						with ui.column():
							while imgY<=layout_rows:
								imgX=1
								with ui.row():
									while imgX<=layout_columns:
										if imgN<len(I_scaled):
											ui.image(I_scaled[imgN]).props(f"width={imgsize}px height={imgsize}px")
										else:
											with ui.image(padding_image).props(f"width={imgsize}px height={imgsize}px"):
												ui.label("Padding").style(f"width:{imgsize}px; height:{imgsize}px;").classes(f"text-white bg-positive overflow-hidden text-ellipsis")
										imgN=imgN+1
										imgX=imgX+1
								imgY=imgY+1
						ui.element("spacer").style("width:15px;")
						with ui.column():
							ui.label(f"{layout_columns} by {layout_rows} photos, {layout_pad} padding")
							ui.label(f"Signature image size: {layout_columns*imgsize}px by {layout_rows*imgsize}px")
							ui.label(f"Individual photo size:{imgsize}px by {imgsize}px")
								
				ui.separator()

				ui.label("03. Select photo style:")
				ui.label("Chose what appearance the individual photos should have in your signature. (Black areas will become transparent.)").style("max-width:550px;")

				def AMset(AMvalue):
					global select_alphamask

					select_alphamask=AMvalue
					update_AMbuttons()

				def update_AMbuttons():
					global aMask_select
					global select_alphamask

					if select_alphamask=="circle":
						button_AMcircle.props("color=primary")
						aMask_select=aMask_circle
						#ui.notify("Selected circle")
					else:
						button_AMcircle.props("color=positive")
					if select_alphamask=="blrcir":
						button_AMblrcir.props("color=primary")
						aMask_select=aMask_blrcir
						#ui.notify("Selected circle (blurred)")
					else:
						button_AMblrcir.props("color=positive")
					if select_alphamask=="square":
						button_AMsquare.props("color=primary")
						aMask_select=aMask_square
						#ui.notify("Selected square (touching)")
					else:
						button_AMsquare.props("color=positive")
					if select_alphamask=="sqedge":
						button_AMsqedge.props("color=primary")
						aMask_select=aMask_sqedge
						#ui.notify("Selected square (touching)")
					else:
						button_AMsqedge.props("color=positive")
					if select_alphamask=="blrsqr":
						button_AMblrsqr.props("color=primary")
						aMask_select=aMask_blrsqr
						#ui.notify("Selected square (blurred)")
					else:
						button_AMblrsqr.props("color=positive")
					if select_alphamask=="rndrec":
						button_AMrndrec.props("color=primary")
						aMask_select=aMask_rndrec
						#ui.notify("Selected rounded square")
					else:
						button_AMrndrec.props("color=positive")
					if select_alphamask=="blrdrc":
						button_AMblrdrc.props("color=primary")
						aMask_select=aMask_blrdrc
						#ui.notify("Selected rounded square (blurred)")
					else:
						button_AMblrdrc.props("color=positive")
					if select_alphamask=="skdrec":
						button_AMskdrec.props("color=primary")
						aMask_select=aMask_skdrec
						#ui.notify("Selected skewed rectangle")
					else:
						button_AMskdrec.props("color=positive")
					if select_alphamask=="blskrc":
						button_AMblskrc.props("color=primary")
						aMask_select=aMask_blskrc
						#ui.notify("Selected skewed rectangle (blurred)")
					else:
						button_AMblskrc.props("color=positive")

				with ui.row(wrap=True):
					button_AMcircle = ui.button(on_click=lambda:AMset("circle")).style("width:240px; height:240px;")
					button_AMblrcir = ui.button(on_click=lambda:AMset("blrcir")).style("width:240px; height:240px;")
					button_AMsquare = ui.button(on_click=lambda:AMset("square")).style("width:240px; height:240px;")
					button_AMsqedge = ui.button(on_click=lambda:AMset("sqedge")).style("width:240px; height:240px;")
					button_AMblrsqr = ui.button(on_click=lambda:AMset("blrsqr")).style("width:240px; height:240px;")
					button_AMrndrec = ui.button(on_click=lambda:AMset("rndrec")).style("width:240px; height:240px;")
					button_AMblrdrc = ui.button(on_click=lambda:AMset("blrdrc")).style("width:240px; height:240px;")
					button_AMskdrec = ui.button(on_click=lambda:AMset("skdrec")).style("width:240px; height:240px;")
					button_AMblskrc = ui.button(on_click=lambda:AMset("blskrc")).style("width:240px; height:240px;")

				with button_AMcircle:
					ui.image(aMask_circle).props(f"width=200px height=200px")
				with button_AMblrcir:
					ui.image(aMask_blrcir).props(f"width=200px height=200px")
				with button_AMsquare:
					ui.image(aMask_square).props(f"width=200px height=200px")
				with button_AMsqedge:
					ui.image(aMask_sqedge).props(f"width=200px height=200px")
				with button_AMblrsqr:
					ui.image(aMask_blrsqr).props(f"width=200px height=200px")
				with button_AMrndrec:
					ui.image(aMask_rndrec).props(f"width=200px height=200px")
				with button_AMblrdrc:
					ui.image(aMask_blrdrc).props(f"width=200px height=200px")
				with button_AMskdrec:
					ui.image(aMask_skdrec).props(f"width=200px height=200px")
				with button_AMblskrc:
					ui.image(aMask_blskrc).props(f"width=200px height=200px")
				update_AMbuttons()				
				

				ui.separator()
				
				ui.label("04. Generate & export signature:")		
				ui.label("If you like the layout and the photo style, click on 'GENERATE SIGNATURE' to preview the final image(s). You can still change the photo style and re-generate the singature without having to update the layout.").style("max-width:550px;")
				quick_button_genSig()
	
		quick_ui_layoutDisplay()
		
		@ui.refreshable
		def quick_ui_sigDisplay() -> None:
			if sig01:
				ui.label("First Signature Image:")
				ui.image(sig01).style("max-width:550px; max-height:200px;").props("fit=scale-down")
			if sig02:
				ui.label("Second Signature Image:")
				ui.image(sig02).style("max-width:550px; max-height:200px;").props("fit=scale-down")
			if sig01:
				ui.label("Click on ''EXPORT FILES' to save the above signature image(s) in the 'signatures' subfolder. Previously exported files may get overwritten!").style("max-width:550px;")
				quick_button_exportSig()
		
		@ui.refreshable
		def quick_ui_sigExport() -> None:
			if quick_export_flag:
				ui.label("All done! If you don't wish to make any further changes, you can exit now.").style("max-width:550px;")
				ui.button("Exit Application", on_click=lambda: exit_application()).style("width:200px;").props("color=secondary")
				
		quick_ui_sigDisplay()
		quick_ui_sigExport()



		
	with ui.tab_panel("Create New"):
		ui.label("GENERATE A NEW SIGNATURE FROM SCRATCH.")
		
		ui.label("This function is not yet available.")
		
		# new_columns = [
			# {"name":"handle", "label":"Position", "field":"handle", "align":"center"},
			# {"name":"image",  "label":"Image",    "field":"image",  "align":"center"},
			# {"name":"nameE",  "label":"Name",     "field":"nameE",  "align":"left"},
			# {"name":"nameJ",  "label":"Japanese", "field":"nameJ",  "align":"left"},
		# ]
		
		# new_rows = []
		
		# while len(images)<len(namesE):
			# images.append("dummy.JPG")
		
		# if len(namesE)==len(namesJ):
			# handle = 0
			# while handle < len(namesE):
				# new_rows.append({"id": handle, "handle": handle+1, "image":"", "nameE":namesE[handle], "nameJ":namesJ[handle]},)
				# handle = handle+1
		
		
		"""
		new_rows = [
			{"id": 0, "handle": 1, "image":"", "nameE":"Kanata", "nameJ":"彼方"},
			{"id": 1, "handle": 2, "image":"", "nameE":"Kizuna", "nameJ":"きずな"},
			{"id": 2, "handle": 3, "image":"", "nameE":"Saki",   "nameJ":"沙姫"},
		]
		"""
		# new_table = ui.table(columns=new_columns, rows=new_rows, row_key="handle")
		
		
		# for image in images:
			# ui.image(image)
		
		
		"""
		new_table.add_slot('body', r'''
			<q-tr :props="props">
				</q-td>
				<q-td key="nameE" :props="props">
					{{ props.row.nameE }}
					<q-popup-edit v-model="props.row.nameE" v-slot="scope"
						@update:model-value="() => $parent.$emit('rename_char', props.row)"
					>
						<q-input v-model="scope.value" dense autofocus counter @keyup.enter="scope.set" />
					</q-popup-edit>
				</q-td>
				<q-td key="nameJ" :props="props">
					{{ props.row.nameJ }}
					<q-popup-edit v-model="props.row.age" v-slot="scope"
						@update:model-value="() => $parent.$emit('rename_char', props.row)"
					>
						<q-input v-model="scope.value" dense autofocus counter @keyup.enter="scope.set" />
					</q-popup-edit>
				</q-td>
			</q-tr>
		''')
		"""
		
	with ui.tab_panel("Load Config"):
		ui.label("LOAD AND EDIT A PREVIOUSLY SAVED CONFIG FILE.")
		
		ui.label("This function is not yet available.")
				
ui.run() #comment out for building
#ui.run(reload=False, port=native.find_open_port()) #comment in for building
'''
Build with
<your python environment> nicegui-pack --onefile --name "DDsiggen_ver.<version number>" DDsiggen.py
'''
