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
import requests
#import imageio as iio

#Version Number
version_no = "1.16"



## Functions

#Import Images (quick sig)

def import_quick(wait_dialog):
	global quick_updated_flag
	global quick_undoable_flag
	global I_quick
	global I_quick_bak
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

	I_quick = []
	for image in I_fullscale:
		ImageOps.exif_transpose(image=image, in_place=True)
		I_quick.append(ImageOps.fit(image=image, size=[200,200], method=Image.Resampling.LANCZOS, centering=[0.5,0.0]))

	I_quick_bak = I_quick.copy()
	images_bak = images.copy()
	quick_ui_imgSettings.refresh()
	quick_update_buttons()
	wait_dialog.close()
	ui.notify(f"{len(I_quick)} photos found")
	print("Quick Import Completed!")

def import_quick_launch():
	with ui.dialog().props("persistent") as wait_dialog, ui.card():
		with ui.row():
			ui.spinner()
			ui.label("Importing...")
	wait_dialog.on("show",lambda:import_quick(wait_dialog))
	wait_dialog.open()

async def import_quick_alert():
	with ui.dialog().props("persistent") as import_quick_dialog, ui.card():
		ui.label("Any changes to the list of photos (Step 01.) will be lost. \n This cannot be undone!").style("white-space:pre-wrap;")
		with ui.row():
			ui.button("Re-Scan",on_click=lambda: import_quick_dialog.submit(True)).style("width:200px;")
			ui.button("Cancel",on_click=lambda: import_quick_dialog.submit(False)).props("color=positive").style("width:200px;")
	is_continue = await import_quick_dialog
	if is_continue:
		import_quick_launch()


#Import Images (create new)

def import_new(wait_dialog, import_mode):
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	new_updated_flag = False
	new_undoable_flag = True
	I_new_undo = I_new.copy()
	namesE_undo = namesE.copy()
	namesJ_undo = namesJ.copy()

	print("Importing...")
	images = []
	f_images = os.listdir(".")
	for file in f_images:
		if file.endswith((".jpg", ".png", ".jpeg", ".JPG", ".PNG", ".JPEG")):
			images.append(file)

	I_fullscale = []
	for image in images:
		I_fullscale.append(Image.open(image))

	if import_mode == "Overwrite":
		I_new = []
	for image in I_fullscale:
		ImageOps.exif_transpose(image=image, in_place=True)
		I_new.append(ImageOps.fit(image=image, size=[200,200], method=Image.Resampling.LANCZOS, centering=[0.5,0.0]))

	I_new_padnames()
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()
	new_ui_siglayout.refresh()
	wait_dialog.close()
	#ui.notify(f"{len(I_new)} photos found")
	print("New Import Completed!")

async def import_new_launch():
	with ui.dialog().props("persistent") as import_mode_dialog, ui.card():
		with ui.column().classes("items-center"):
			ui.label("Entries already exist in the photo column. How do you wish to import the new photos?").style("max-width:300px;")
			ui.button("Overwrite",on_click=lambda: import_mode_dialog.submit("Overwrite")).style("width:200px;")
			ui.button("Append",on_click=lambda: import_mode_dialog.submit("Append")).style("width:200px;")
			ui.button("Cancel",on_click=lambda: import_mode_dialog.submit("Cancel")).props("color=positive").style("width:200px;")
	with ui.dialog().props("persistent") as wait_dialog, ui.card():
		with ui.row():
			ui.spinner()
			ui.label("Importing...")
	if I_new:
		import_mode = await import_mode_dialog
	else:
		import_mode = "Overwrite"
	if import_mode == "Cancel":
		return()
	wait_dialog.on("show",lambda:import_new(wait_dialog, import_mode))
	wait_dialog.open()


def image_from_url(image_url):
	print(f"Importing {image_url} ...")
	url_response = requests.get(image_url)
	print("Connecting ...")
	try:
		new_image = Image.open(BytesIO(url_response.content))
	except:
		ui.notify("URL is not an image!")
		print("Aborting ...")
		return(False)
	else:
		print("Extracting Image ...")
		ImageOps.exif_transpose(image=new_image, in_place=True)
		print("Transposing ...")
		scaled_image = ImageOps.fit(image=new_image, size=[200,200], method=Image.Resampling.LANCZOS, centering=[0.5,0.0])
		print("Rescaling ...")
		return(scaled_image)

async def import_from_url():
	with ui.dialog().props("persistent") as import_url_dialog, ui.card():
		newurl = ui.input(label="Enter image URL:")
		with ui.row():
			ui.button("Import",on_click=lambda: import_url_dialog.submit(newurl.value)).style("width:200px;")
			ui.button("Cancel",on_click=lambda: import_url_dialog.submit(False)).props("color=positive").style("width:200px;")

	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	image_url = await import_url_dialog
	if image_url:
		scaled_image = image_from_url(image_url)
		if scaled_image:
			print("Adding to image list ...")
			new_updated_flag = False
			I_new_undo = I_new.copy()
			namesE_undo = namesE.copy()
			namesJ_undo = namesJ.copy()
			I_new.append(scaled_image)
			I_new_padnames()
			new_undoable_flag = True
			print("Import from URL completed!")
		else:
			print("URL is not an image!")
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()
	new_ui_siglayout.refresh()


async def import_local():
	with ui.dialog().props("persistent") as import_local_dialog, ui.card():
		ui.label("Drag & drop your photo into the area below or click the '+' button to open the file picker.").style("max-width:300px;")
		ui.upload(auto_upload=True, on_upload=lambda e: import_local_dialog.submit(e.content))#handle_upload)
		ui.button("Cancel",on_click=lambda: import_local_dialog.submit(False)).props("color=positive").style("width:200px;")

	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	new_file = await import_local_dialog
	#print(f"{new_file}")
	if new_file:
		try:
			new_image = Image.open(new_file)
		except:
			ui.notify("File is not an image!")
			print("File is not an image!")
		else:
			new_updated_flag = False
			I_new_undo = I_new.copy()
			namesE_undo = namesE.copy()
			namesJ_undo = namesJ.copy()
			ImageOps.exif_transpose(image=new_image, in_place=True)
			scaled_image = ImageOps.fit(image=new_image, size=[200,200], method=Image.Resampling.LANCZOS, centering=[0.5,0.0])
			I_new.append(scaled_image)
			I_new_padnames()
			new_undoable_flag = True
			print("Local import completed!")
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()
	new_ui_siglayout.refresh()



#Import other data

async def import_namesE():
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	with ui.dialog().props("persistent") as import_mode_dialog, ui.card():
		with ui.column().classes("items-center"):
			ui.label("Entries already exist in the name column. How do you wish to import the new names?").style("max-width:300px;")
			ui.button("Overwrite",on_click=lambda: import_mode_dialog.submit("Overwrite")).style("width:200px;")
			ui.button("Append",on_click=lambda: import_mode_dialog.submit("Append")).style("width:200px;")
			ui.button("Cancel",on_click=lambda: import_mode_dialog.submit("Cancel")).props("color=positive").style("width:200px;")

	if I_new_checkemptynames(namesE):
		import_mode = await import_mode_dialog
	else:
		import_mode = "Overwrite"
	if import_mode == "Cancel":
		return()
	I_new_undo = I_new.copy()
	namesE_undo = namesE.copy()
	namesJ_undo = namesJ.copy()
	if import_mode == "Append":
		while len(namesE)>0:
			if namesE[len(namesE)-1]=="":
				namesE.pop(len(namesE)-1)
			else:
				break
	else:
		namesE = []
	try:
		f_namesE = open("names.txt","r",encoding="utf-8")
	except:
		ui.notify("File 'names.txt' was not found!")
	else:
		new_namesE = f_namesE.readlines()
		new_namesE = [i.rstrip() for i in new_namesE]
		namesE = namesE+new_namesE
	I_new_padnames()
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()


async def import_namesJ():
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	with ui.dialog().props("persistent") as import_mode_dialog, ui.card():
		with ui.column().classes("items-center"):
			ui.label("Entries already exist in the epithet column. How do you wish to import the new epithets?").style("max-width:300px;")
			ui.button("Overwrite",on_click=lambda: import_mode_dialog.submit("Overwrite")).style("width:200px;")
			ui.button("Append",on_click=lambda: import_mode_dialog.submit("Append")).style("width:200px;")
			ui.button("Cancel",on_click=lambda: import_mode_dialog.submit("Cancel")).props("color=positive").style("width:200px;")

	if I_new_checkemptynames(namesJ):
		import_mode = await import_mode_dialog
	else:
		import_mode = "Overwrite"
	if import_mode == "Cancel":
		return()
	I_new_undo = I_new.copy()
	namesE_undo = namesE.copy()
	namesJ_undo = namesJ.copy()
	if import_mode == "Append":
		while len(namesJ)>0:
			if namesJ[len(namesJ)-1]=="":
				namesJ.pop(len(namesJ)-1)
			else:
				break
	else:
		namesJ = []
	try:
		f_namesJ = open("epithets.txt","r",encoding="utf-8")
	except:
		ui.notify("File 'epithets.txt' was not found!")
	else:
		new_namesJ = f_namesJ.readlines()
		new_namesJ = [i.rstrip() for i in new_namesJ]
		namesJ = namesJ+new_namesJ
	I_new_padnames()
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()

def I_new_padnames():
	global I_new
	global namesE
	global namesJ
	while len(namesE)<len(I_new):
		namesE.append("")
	while len(namesJ)<len(I_new):
		namesJ.append("")
		
def I_new_reducenames():
	global namesE
	global namesJ
	while len(namesE)>len(I_new):
		if namesE[len(namesE)-1]=="":
			namesE.pop(len(namesE)-1)
		else:
			break
	while len(namesJ)>len(I_new):
		if namesJ[len(namesJ)-1]=="":
			namesJ.pop(len(namesJ)-1)
		else:
			break

def I_new_checkemptynames(namelist):
	anynames_flag = False
	for name in namelist:
		if name != "":
			anynames_flag = True
	return(anynames_flag)


def scan_fonts():
	global fonts_list

	fonts_list = [False]
	try:
		f_fonts = os.listdir("./fonts")
	except:
		ui.notify("Folder 'fonts' not found!")
	else:
		for file in f_fonts:
			if file.endswith((".ttf", ".otf", ".TTF", ".OTF")):
				fonts_list.append(file)
	#print(fonts_list)


def rescan_fonts():
	scan_fonts()
	new_ui_fontEselect.refresh()
	new_ui_fontJselect.refresh()
	update_textsample()
	ui.notify("Fonts updated!")

#Rename

async def I_new_renameE(current_idx) -> None:

	with ui.dialog().props("persistent") as rename_dialog, ui.card():
		newname = ui.input(label="Enter new name:")
		ui.button("Set New Name",on_click=lambda: rename_dialog.submit(newname.value)).style("width:200px;")
		ui.button("Clear Name",on_click=lambda: rename_dialog.submit("")).props("color=positive").style("width:200px;")
		ui.button("Cancel",on_click=lambda: rename_dialog.submit(currentnameE)).props("color=positive").style("width:200px;")

	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	currentnameE = namesE[current_idx]
	newnameE = await rename_dialog
	if newnameE!=currentnameE:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		namesE[current_idx] = newnameE
		I_new_reducenames()
		new_undoable_flag = True
		ui.notify(f"Name set to '{newnameE}'.")
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()


async def I_new_renameJ(current_idx) -> None:

	with ui.dialog().props("persistent") as rename_dialog, ui.card():
		newname = ui.input(label="Enter new epithet:")
		ui.button("Set New Epithet",on_click=lambda: rename_dialog.submit(newname.value)).style("width:200px;")
		ui.button("Clear Epithet",on_click=lambda: rename_dialog.submit("")).props("color=positive").style("width:200px;")
		ui.button("Cancel",on_click=lambda: rename_dialog.submit(currentnameJ)).props("color=positive").style("width:200px;")

	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	currentnameJ = namesJ[current_idx]
	newnameJ = await rename_dialog
	if newnameJ!=currentnameJ:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		namesJ[current_idx] = newnameJ
		I_new_reducenames()
		new_undoable_flag = True
		ui.notify(f"Name set to '{newnameJ}'.")
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()


#Reorder Images (quick sig)

def I_quick_moveup(current_idx) -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_quick
	global I_quick_undo
	global images
	global images_undo
	if current_idx>0:
		quick_updated_flag = False
		#ui.notify(f"Moved down {current_idx}.")
		I_quick_undo = I_quick.copy()
		images_undo = images.copy()
		I_quick.insert(current_idx-1, I_quick.pop(current_idx))
		images.insert(current_idx-1, images.pop(current_idx))
		quick_undoable_flag = True
	quick_list_imgDisplay.refresh()
	quick_update_buttons()
		
def I_quick_movedn(current_idx) -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_quick
	global I_quick_undo
	global images
	global images_undo
	if current_idx<len(I_quick)-1:
		quick_updated_flag = False
		#ui.notify(f"Moved up {current_idx}.")
		I_quick_undo = I_quick.copy()
		images_undo = images.copy()
		I_quick.insert(current_idx+1, I_quick.pop(current_idx))
		images.insert(current_idx+1, images.pop(current_idx))
		quick_undoable_flag = True
	quick_list_imgDisplay.refresh()
	quick_update_buttons()
	
def I_quick_delete(current_idx) -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_quick
	global I_quick_undo
	global images
	global images_undo
	quick_updated_flag = False
	#ui.notify(f"Deleted {current_idx}.")
	I_quick_undo = I_quick.copy()
	images_undo = images.copy()
	I_quick.pop(current_idx)
	images.pop(current_idx)
	ui.notify("Photo removed from list")
	quick_undoable_flag = True
	quick_list_imgDisplay.refresh()
	quick_update_buttons()
	
def I_quick_reset() -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_quick
	global I_quick_undo
	global I_quick_bak
	global images
	global images_undo
	global images_bak
	quick_updated_flag = False
	I_quick_undo = I_quick.copy()
	images_undo = images.copy()
	I_quick = I_quick_bak.copy()
	images = images_bak.copy()
	ui.notify("List of photos was reset")
	quick_undoable_flag = True
	quick_list_imgDisplay.refresh()
	quick_update_buttons()

def I_quick_undofunc() -> None:
	global quick_updated_flag
	global quick_undoable_flag
	global I_quick
	global I_quick_undo
	global images
	global images_undo
	quick_updated_flag = False
	quick_undoable_flag = False
	I_quick = I_quick_undo.copy()
	images = images_undo.copy()
	ui.notify("Last operation undone")
	quick_list_imgDisplay.refresh()
	quick_update_buttons()
	

#Reorder Images (create new)

def row_new_moveup(current_idx) -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	if current_idx>0:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		I_new.insert(current_idx-1, I_new.pop(current_idx))
		namesE.insert(current_idx-1, namesE.pop(current_idx))
		namesJ.insert(current_idx-1, namesJ.pop(current_idx))
		new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()

def row_new_movedn(current_idx) -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	if current_idx<len(I_new)-1:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		I_new.insert(current_idx+1, I_new.pop(current_idx))
		namesE.insert(current_idx+1, namesE.pop(current_idx))
		namesJ.insert(current_idx+1, namesJ.pop(current_idx))
		new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()

def row_new_delete(current_idx) -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	new_updated_flag = False
	I_new_undo = I_new.copy()
	namesE_undo = namesE.copy()
	namesJ_undo = namesJ.copy()
	I_new.pop(current_idx)
	namesE.pop(current_idx)
	namesJ.pop(current_idx)
	ui.notify("Row removed from list")
	new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()
	new_ui_siglayout.refresh()

def I_new_moveup(current_idx) -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	if current_idx>0:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		I_new.insert(current_idx-1, I_new.pop(current_idx))
		new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()

def I_new_movedn(current_idx) -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	if current_idx<len(I_new)-1:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		I_new.insert(current_idx+1, I_new.pop(current_idx))
		new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()
	
async def I_new_clear():
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	with ui.dialog().props("persistent") as confirm_clear_dialog, ui.card():
		ui.label("Clear all photos?")
		with ui.row():
			ui.button("Continue",on_click=lambda: confirm_clear_dialog.submit(True)).style("width:200px;")
			ui.button("Cancel",on_click=lambda: confirm_clear_dialog.submit(False)).props("color=positive").style("width:200px;")

	if I_new:
		is_continue = await confirm_clear_dialog
		if is_continue:
			new_updated_flag = False
			I_new_undo = I_new.copy()
			namesE_undo = namesE.copy()
			namesJ_undo = namesJ.copy()
			I_new = []
			I_new_reducenames()
			new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()
	new_ui_siglayout.refresh()

def namesE_moveup(current_idx) -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	if current_idx>0:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		namesE.insert(current_idx-1, namesE.pop(current_idx))
		new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()

def namesE_movedn(current_idx) -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	if current_idx<len(namesE)-1:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		namesE.insert(current_idx+1, namesE.pop(current_idx))
		new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()
	
async def namesE_clear():
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	with ui.dialog().props("persistent") as confirm_clear_dialog, ui.card():
		ui.label("Clear all names?")
		with ui.row():
			ui.button("Continue",on_click=lambda: confirm_clear_dialog.submit(True)).style("width:200px;")
			ui.button("Cancel",on_click=lambda: confirm_clear_dialog.submit(False)).props("color=positive").style("width:200px;")

	if I_new_checkemptynames(namesE):
		#new_updated_flag = False
		is_continue = await confirm_clear_dialog
		if is_continue:
			I_new_undo = I_new.copy()
			namesE_undo = namesE.copy()
			namesJ_undo = namesJ.copy()
			namesE = []
			I_new_padnames()
			new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()

def namesJ_moveup(current_idx) -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	if current_idx>0:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		namesJ.insert(current_idx-1, namesJ.pop(current_idx))
		new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()

def namesJ_movedn(current_idx) -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	if current_idx<len(namesE)-1:
		#new_updated_flag = False
		I_new_undo = I_new.copy()
		namesE_undo = namesE.copy()
		namesJ_undo = namesJ.copy()
		namesJ.insert(current_idx+1, namesJ.pop(current_idx))
		new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()
	
async def namesJ_clear():
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo

	with ui.dialog().props("persistent") as confirm_clear_dialog, ui.card():
		ui.label("Clear all epithets?")
		with ui.row():
			ui.button("Continue",on_click=lambda: confirm_clear_dialog.submit(True)).style("width:200px;")
			ui.button("Cancel",on_click=lambda: confirm_clear_dialog.submit(False)).props("color=positive").style("width:200px;")

	if I_new_checkemptynames(namesJ):
		#new_updated_flag = False
		is_continue = await confirm_clear_dialog
		if is_continue:
			I_new_undo = I_new.copy()
			namesE_undo = namesE.copy()
			namesJ_undo = namesJ.copy()
			namesJ = []
			I_new_padnames()
			new_undoable_flag = True
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()

def I_new_undofunc() -> None:
	global new_updated_flag
	global new_undoable_flag
	global I_new
	global I_new_undo
	global namesE
	global namesE_undo
	global namesJ
	global namesJ_undo
	new_updated_flag = False
	new_undoable_flag = False
	I_new = I_new_undo.copy()
	namesE = namesE_undo.copy()
	namesJ = namesJ_undo.copy()
	ui.notify("Last operation undone")
	new_ui_characterlist.refresh()
	new_button_undoDisplay.refresh()
	new_ui_siglayout.refresh()


#Generate Quick Layout

def generate_quicklayout():
	global layout_images_target
	global quick_updated_flag
	global quick_generated_flag
	global layout_images
	global layout_columns
	global layout_rows
	global layout_pad
	nchar = len(I_quick)
	
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
	
	nchar_img=math.ceil(nchar/layout_images)

	layout_rows=1
	while math.floor(550/math.ceil(nchar_img/layout_rows))<math.floor(200/(layout_rows+1)):
		layout_rows=layout_rows+1
	layout_columns=math.ceil(nchar_img/layout_rows)
	'''
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
	'''
	layout_pad=(layout_rows*layout_columns*layout_images)-nchar
	if layout_images==1:
		ui.notify(f"{layout_images} image with {layout_columns} by {layout_rows} photos. {layout_pad} padding.")
	else:
		ui.notify(f"{layout_images} images with {layout_columns} by {layout_rows} photos, {layout_pad} padding.")
	quick_updated_flag = True
	quick_generated_flag = False
	quick_ui_layoutDisplay.refresh()
	quick_update_buttons()
	#return(layout_images,layout_rows,layout_columns,layout_pad)

def force_quicklayout():
	global quick_updated_flag
	quick_updated_flag = False
	quick_update_buttons()


#Generate New Layout

def generate_newlayout(image_layout, custom_columns, custom_rows):
	global new_updated_flag
	global new_generated_flag
	global new_layout_images
	global new_layout_columns
	global new_layout_rows
	global new_layout_pad
	nchar = len(I_new)

	if nchar==0:
		new_layout_images=0
		new_layout_rows=0
		new_layout_columns=0
		new_layout_pad=0
		ui.notify("No layout available.")
		new_ui_layoutSample.refresh()
		return()
	elif image_layout=="Custom":
		new_layout_images=math.ceil(nchar/(custom_columns*custom_rows))
		new_layout_columns=custom_columns
		new_layout_rows=custom_rows
	else:
		if image_layout=="Auto: One Image" or nchar==1:
			new_layout_images=1
		elif image_layout=="Auto: Two Images":
			new_layout_images=2
		elif nchar<6:
			new_layout_images=1
		else:
			new_layout_images=2

		nchar_img=math.ceil(nchar/new_layout_images)
		new_layout_rows=1
		while math.floor(550/math.ceil(nchar_img/new_layout_rows))<math.floor(200/(new_layout_rows+1)):
			new_layout_rows=new_layout_rows+1
		new_layout_columns=math.ceil(nchar_img/new_layout_rows)

	new_layout_pad=(new_layout_rows*new_layout_columns*new_layout_images)-nchar
	if layout_images==1:
		ui.notify(f"{new_layout_images} image with {new_layout_columns} by {new_layout_rows} photos. {new_layout_pad} padding.")
	else:
		ui.notify(f"{new_layout_images} images with {new_layout_columns} by {new_layout_rows} photos. {new_layout_pad} padding.")
	new_updated_flag = True
	new_generated_flag = False
	new_ui_siglayout.refresh()
	new_ui_layoutSample.refresh()


def force_newlayout():
	global new_updated_flag
	new_updated_flag = False
	new_ui_siglayout.refresh()

#Generate Quick Signature

def generate_quicksig():
	global quick_generated_flag
	I_masked=mask_images()
	combine_images(I_masked)
	scale_signature()
	quick_generated_flag=True
	quick_ui_sigDisplay.refresh()

def mask_images():
	I_masked=[]
	for image in I_quick:
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


#Generate New Signature

def generate_newsig():
	global new_generated_flag
	global I_new_withtext
	I_new_withtext=applytext_I_new()
	new_combine_images(I_new_withtext)
	new_scale_signature()
	new_generated_flag=True
	new_ui_sigDisplay.refresh()

def new_combine_images(I_new_withtext):
	global new_sig
	new_sig=[]
	n_char=len(I_new_withtext)
	i_char=0
	i_images=0
	while i_images<new_layout_images:
		sig_image=Image.new("RGBA",(200*new_layout_columns,200*new_layout_rows),(0,0,0,0))
		i_rows=0
		while i_rows<new_layout_rows:
			i_columns=0
			while i_columns<new_layout_columns:
				if i_char<n_char:
					sig_image.paste(I_new_withtext[i_char],(200*i_columns,200*i_rows))
					i_char=i_char+1
				i_columns=i_columns+1
			i_rows=i_rows+1
		new_sig.append(sig_image)
		i_images=i_images+1

def new_scale_signature():
	global new_sig_scaled
	new_sig_scaled=[]
	for sig_image in new_sig:
		imagebuffer=sig_image.copy()
		imagebuffer=ImageOps.contain(image=imagebuffer, size=[550,200], method=Image.Resampling.LANCZOS)
		new_sig_scaled.append(imagebuffer)

def applytext_I_new():
	image_no=0
	I_new_withtext=[]
	while image_no<len(I_new):
		textlayerE, textlayerJ = new_generate_textlayers(image_no)
		image_withtext = new_generate_textimage(image_no,textlayerE,textlayerJ)
		I_new_withtext.append(image_withtext)
		image_no=image_no+1
	return(I_new_withtext)

def new_generate_textlayers(text_no):
	if fontE.value and namesE[text_no]:
		if colorEoutline:
			textEheight = math.floor(sizeEmain*1.5)+math.floor(2*sizeEoutline)
		else:
			textEheight = math.floor(sizeEmain*1.5)
		textlayerE = Image.new("RGBA",(800,textEheight),(0,0,0,0))
		dd = ImageDraw.Draw(textlayerE)
		if colorEoutline:
			dd.text((sizeEoutline,sizeEoutline), namesE[text_no], fill=colorEmain+transpEmain, stroke_width=sizeEoutline, stroke_fill=colorEoutline+transpEoutline, font=ImageFont.truetype(f"./fonts/{fontE.value}", sizeEmain))
		else:
			dd.text((0,0),namesE[text_no], fill=colorEmain+transpEmain, font=ImageFont.truetype(f"./fonts/{fontE.value}", sizeEmain))
	else:
		textlayerE=False
	if fontJ.value and namesJ[text_no]:
		if colorJoutline:
			textJheight = math.floor(sizeJmain*1.5)+math.floor(2*sizeJoutline)
		else:
			textJheight = math.floor(sizeJmain*1.5)
		textlayerJ = Image.new("RGBA",(800,textJheight),(0,0,0,0))
		dd = ImageDraw.Draw(textlayerJ)
		if colorJoutline:
			dd.text((sizeJoutline,sizeJoutline), namesJ[text_no], fill=colorJmain+transpJmain, stroke_width=sizeJoutline, stroke_fill=colorJoutline+transpJoutline, font=ImageFont.truetype(f"./fonts/{fontJ.value}", sizeJmain))
		else:
			dd.text((0,0),namesJ[text_no], fill=colorJmain+transpJmain, font=ImageFont.truetype(f"./fonts/{fontJ.value}", sizeJmain))
		#textlayerJ.show()
	else:
		textlayerJ=False
	return(textlayerE, textlayerJ)

def sig_textcropper(textimage):
	textimage2 = textimage.copy()
	cropheight = textimage2.size[1]
	try:
		cropwidth = textimage2.getbbox()[2]+textimage2.getbbox()[0]
	except:
		cropwidth = 50
		print("Text layer is empty!")
	textimage2 = textimage2.crop((0,0,cropwidth,cropheight))
	if textimage2.size[0]>200 and new_handle_oversize.value=="Squish":
		textimage2=textimage2.resize(size=(200,cropheight),resample=Image.Resampling.LANCZOS)
	if textimage2.size[0]>200 and new_handle_oversize.value=="Shrink":
		textimage2=ImageOps.contain(image=textimage2, size=[200,200], method=Image.Resampling.LANCZOS)
	return(textimage2)

def new_generate_textimage(image_no,textlayerE,textlayerJ):
	try:
		I_new[image_no]
	except:
		textimage = []
		print("No image available!")
	else:
		imagebuffer = I_new[image_no]
		textimage = imagebuffer.copy()
		textimage.putalpha(new_alphamask)
		if fontE.value and textlayerE:
			textlayerE_cropped = sig_textcropper(textlayerE)
			if nameEalignX == "right":
				nameEposX = 200-textlayerE_cropped.size[0]+nameEoffsetX
			elif nameEalignX == "center":
				nameEposX = 100-math.floor(textlayerE_cropped.size[0]*0.5)+nameEoffsetX
			else:
				nameEposX = 0+nameEoffsetX
			if nameEalignY == "top":
				nameEposY = 0-nameEoffsetY
			elif nameEalignY == "center":
				nameEposY = 100-math.floor(textlayerE_cropped.size[1]*0.5)-nameEoffsetY
			else:
				nameEposY = 200-textlayerE_cropped.size[1]-nameEoffsetY
		if fontJ.value and textlayerJ:
			textlayerJ_cropped = sig_textcropper(textlayerJ)
			if nameJalignX == "right":
				nameJposX = 200-textlayerJ_cropped.size[0]+nameJoffsetX
			elif nameJalignX == "center":
				nameJposX = 100-math.floor(textlayerJ_cropped.size[0]*0.5)+nameJoffsetX
			else:
				nameJposX = 0+nameJoffsetX
			if nameJalignY == "top":
				nameJposY = 0-nameJoffsetY
			elif nameJalignY == "center":
				nameJposY = 100-math.floor(textlayerJ_cropped.size[1]*0.5)-nameJoffsetY
			else:
				nameJposY = 200-textlayerJ_cropped.size[1]-nameJoffsetY

		if names_priority.value == "Name":
			if fontJ.value and textlayerJ:
				textimage.paste(textlayerJ_cropped,(nameJposX,nameJposY), mask=textlayerJ_cropped)
			if fontE.value and textlayerE:
				textimage.paste(textlayerE_cropped,(nameEposX,nameEposY), mask=textlayerE_cropped)
		elif names_priority.value == "Epithet":
			if fontE.value and textlayerE:
				textimage.paste(textlayerE_cropped,(nameEposX,nameEposY), mask=textlayerE_cropped)
			if fontJ.value and textlayerJ:
				textimage.paste(textlayerJ_cropped,(nameJposX,nameJposY), mask=textlayerJ_cropped)
		else:
			print("Error: Check text layer priority!")
	return(textimage)


#Export New Signature

def save_newsig_scaled():
	os.makedirs("./signatures", exist_ok=True)
	i_image=1
	for sig_image in new_sig_scaled:
		sig_image.save(f"./signatures/new_sig_{i_image:03d}.png")
		ui.notify(f"Image #{i_image} saved as 'new_sig_{i_image:03d}.png' in 'signatures'.")
		i_image=i_image+1

def save_newsig_fullsize():
	os.makedirs("./signatures", exist_ok=True)
	i_image=1
	for sig_image in new_sig:
		sig_image.save(f"./signatures/new_sig_fullscale_{i_image:03d}.png")
		ui.notify(f"Image #{i_image} saved as 'new_sig_fullscale_{i_image:03d}.png' in 'signatures'.")
		i_image=i_image+1

def save_newsig_single():
	os.makedirs("./signatures", exist_ok=True)
	i_image=1
	for sig_image in I_new_withtext:
		try:
			sig_name=namesE[i_image-1]
		except:
			sig_name="NONAME"
		sig_image.save(f"./signatures/individual_{i_image:03d}_{sig_name}.png")
		i_image=i_image+1
	ui.notify(f"{i_image-1} individual images saved in 'signatures'.")


#Extra Functionality

def quick_update_buttons():
	quick_button_undoDisplay.refresh()
	quick_button_updateLayout.refresh()
	quick_button_genSig.refresh()
	quick_button_exportSig.refresh()

def update_textsample():
	global sampleE
	global sampleJ
	global textsample_no
	global sizeEmain
	global sizeEoutline
	global transpEmain
	global transpEoutline
	global sizeJmain
	global sizeJoutline
	global transpJmain
	global transpJoutline
	textsample_no = select_textsample_no.value
	sizeEmain=slider_sizeEmain.value
	sizeEoutline=slider_sizeEoutline.value
	transpEmain=format(math.ceil(slider_transpEmain.value*2.55),"02x")
	transpEoutline=format(math.ceil(slider_transpEoutline.value*2.55),"02x")
	sizeJmain=slider_sizeJmain.value
	sizeJoutline=slider_sizeJoutline.value
	transpJmain=format(math.ceil(slider_transpJmain.value*2.55),"02x")
	transpJoutline=format(math.ceil(slider_transpJoutline.value*2.55),"02x")
	textlayerE, textlayerJ = new_generate_textlayers(textsample_no-1)
	try:
		sampleE = textlayerE.copy()
	except:
		sampleE = False
	try:
		sampleJ = textlayerJ.copy()
	except:
		sampleJ = False
	update_imagesample()
	new_ui_fontSamples.refresh()

def update_imagesample():
	global imagesample
	global nameEoffsetX
	global nameEoffsetY
	global nameJoffsetX
	global nameJoffsetY
	nameEoffsetX = slider_nameEoffsetx.value
	nameEoffsetY = slider_nameEoffsety.value
	nameJoffsetX = slider_nameJoffsetx.value
	nameJoffsetY = slider_nameJoffsety.value
	imagesample = new_generate_textimage(textsample_no-1,sampleE,sampleJ)
	new_ui_imageSample.refresh()


def exit_application():
	with ui.dialog().props("persistent maximized") as exit_dialog, ui.card():
		ui.label("Application terminated! You can now close this browser tab.")
	exit_dialog.open()
	app.shutdown()


## Script starts here ############################################################	

print("Please wait a moment while the application is starting...")


## Initialize Globals and Flags

quick_undoable_flag = False
quick_updated_flag = False
quick_generated_flag = False
quick_export_flag = False

new_updated_flag = False
new_undoable_flag = False
new_generated_flag = False
new_table_index = []

select_alphamask = "circle"

namesE = []
namesJ = []
fonts_list = []

images = []
images_undo = []
images_bak = []
I_quick = []
I_quick_undo = []
I_quick_bak = []
I_new = []
I_new_undo = []
new_sig_scaled = []
layout_images = 0
layout_rows = 0
layout_columns = 0
layout_pad = 0
sig01 = 0
sig02 = 0

custom_columns = 4
custom_rows = 1

new_layout_images = 0
new_layout_rows = 0
new_layout_columns = 0
new_layout_pad = 0

colorEmain = "#ff6065"
sizeEmain = 30
colorEoutline = False
sizeEoutline = 2
colorJmain = "#ff6065"
sizeJmain = 30
colorJoutline = False
sizeJoutline = 2

textsample_no = 1
imagesample = []
sampleE = False
sampleJ = False

nameEalignX = "left"
nameEalignY = "bottom"
nameEoffsetX = 0
nameEoffsetY = 0
nameJalignX = "left"
nameJalignY = "bottom"
nameJoffsetX = 0
nameJoffsetY = 0

# Import local files
scan_fonts()


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
new_alphamask = aMask_circle

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

ui.page_title("DDsiggen")

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

with ui.tab_panels(modeSelect, value="Quick Sig").classes("w-full"):


## Quick Sig Panel

	with ui.tab_panel("Quick Sig"):
		ui.label("QUICKLY GENERATE A SIMPLE SIGNATURE.")
		with ui.row(wrap=True):
			ui.label("How to use:")
			ui.label("Copy the photos that you want to use in your signature into the same folder as this executable, then click 'SCAN FOLDER'. If your photos show up below, you're good to go.").style("max-width:450px;")
		
		@ui.refreshable
		def quick_button_undoDisplay () -> None:
			if quick_undoable_flag:
				ui.button("Undo", icon="o_undo", on_click=lambda:I_quick_undofunc()).style("width:200px;")
			else:
				with ui.button("Undo", icon="o_undo", color="accent").style("width:200px;").props("disable"):
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
				for idx, image in enumerate(I_quick):
					with ui.grid(columns="80px 40px 80px").classes("gap-0"):
						ui.image(image).props(f"width=200px height=200px").classes("col-span-full")
						with ui.button_group().style("width: 200px;"):
							if idx==0:
								ui.button(icon="o_chevron_left", color="accent").style("width:80px;").props("disable")
							else:
								ui.button(icon="o_chevron_left", on_click=lambda iid=idx:I_quick_moveup(iid)).style("width:80px;")
							if len(I_quick)<=1:
								ui.button(icon="o_delete", color="accent").style("width:40px;").props("disable")
							else:
								with ui.button(icon="o_delete", color="secondary", on_click=lambda iid=idx:I_quick_delete(iid)).style("width:40px;"):
									ui.tooltip("Remove photo from list").classes("default_tooltip")
							if idx==len(I_quick)-1:
								ui.button(icon="o_chevron_right", color="accent").style("width:80px;").props("disable")
							else:
								ui.button(icon="o_chevron_right", on_click=lambda iid=idx:I_quick_movedn(iid)).style("width:80px;")

		@ui.refreshable
		def quick_ui_imgSettings() -> None:
			global layout_images_target
			if I_quick:
				with ui.button("Re-Scan",on_click=lambda:import_quick_alert()).style("width:200px;"):
					ui.tooltip("If you have changed any photo files in the folder, use this to update the list of photos.").props("max-width='200px'").classes("default_tooltip")
			else:
				ui.button("Scan Folder",on_click=lambda:import_quick_launch()).style("width:200px;")
			
			ui.separator()

			if I_quick:
				ui.label("01. Reorder or remove photos:")
				ui.label("Use the arrow buttons to reorder photos in the list as desired. Unwanted photos can be removed with the 'Trash' button. If you would like to start over, use the 'RESET LIST' button. The most recent action can be undone.").style("max-width:550px;")
				quick_list_imgDisplay()
				with ui.row(wrap=True):
					quick_button_undoDisplay()
					with ui.button("Reset List", on_click=lambda:I_quick_reset()).style("width:200px;"):
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
			if layout_images>0 and I_quick:
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
									if imgN<len(I_quick):
										ui.image(I_quick[imgN]).props(f"width={imgsize}px height={imgsize}px")
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
						ui.label(f"Individual photo size: {imgsize}px by {imgsize}px")
					
				if layout_images>1:
					ui.label("Second Signature Image:")
					with ui.row(wrap=True):
						imgY=1
						with ui.column():
							while imgY<=layout_rows:
								imgX=1
								with ui.row():
									while imgX<=layout_columns:
										if imgN<len(I_quick):
											ui.image(I_quick[imgN]).props(f"width={imgsize}px height={imgsize}px")
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
							ui.label(f"Individual photo size: {imgsize}px by {imgsize}px")
								
				ui.separator()

				ui.label("03. Select alpha mask:")
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
					button_AMcircle = ui.button(on_click=lambda:AMset("circle")).style("width:200px; height:200px;")
					button_AMblrcir = ui.button(on_click=lambda:AMset("blrcir")).style("width:200px; height:200px;")
					button_AMsquare = ui.button(on_click=lambda:AMset("square")).style("width:200px; height:200px;")
					button_AMsqedge = ui.button(on_click=lambda:AMset("sqedge")).style("width:200px; height:200px;")
					button_AMblrsqr = ui.button(on_click=lambda:AMset("blrsqr")).style("width:200px; height:200px;")
					button_AMrndrec = ui.button(on_click=lambda:AMset("rndrec")).style("width:200px; height:200px;")
					button_AMblrdrc = ui.button(on_click=lambda:AMset("blrdrc")).style("width:200px; height:200px;")
					button_AMskdrec = ui.button(on_click=lambda:AMset("skdrec")).style("width:200px; height:200px;")
					button_AMblskrc = ui.button(on_click=lambda:AMset("blskrc")).style("width:200px; height:200px;")

				with button_AMcircle:
					ui.image(aMask_circle).props(f"width=170px height=170px")
				with button_AMblrcir:
					ui.image(aMask_blrcir).props(f"width=170px height=170px")
				with button_AMsquare:
					ui.image(aMask_square).props(f"width=170px height=170px")
				with button_AMsqedge:
					ui.image(aMask_sqedge).props(f"width=170px height=170px")
				with button_AMblrsqr:
					ui.image(aMask_blrsqr).props(f"width=170px height=170px")
				with button_AMrndrec:
					ui.image(aMask_rndrec).props(f"width=170px height=170px")
				with button_AMblrdrc:
					ui.image(aMask_blrdrc).props(f"width=170px height=170px")
				with button_AMskdrec:
					ui.image(aMask_skdrec).props(f"width=170px height=170px")
				with button_AMblskrc:
					ui.image(aMask_blskrc).props(f"width=170px height=170px")
				update_AMbuttons()				
				

				ui.separator()
				
				ui.label("04. Generate & export signature:")		
				ui.label("If you like the layout and the alpha mask, click on 'GENERATE SIGNATURE' to preview the final image(s). You can still change the alpha mask and re-generate the singature without having to update the layout.").style("max-width:550px;")
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


## Create New Panel
		
	with ui.tab_panel("Create New"):
		ui.label("GENERATE A NEW SIGNATURE FROM SCRATCH.")

		ui.label("You can load photos into the table below and import or apply custom text on top. Use the '?' buttons next to some options to see more details about how to use them. You can only undo your most recent action.").style("max-width:550px;")

		with ui.dialog() as help_new_photos_dialog, ui.card():
			with ui.column().classes("items-center"):
				ui.icon("o_info", size="100px")
				ui.label("All photos listed in the photo table will be combined into your signature image(s). You can add photos to the photo table in three ways:").style("max-width:450px;")
				ui.label("(1) Like in the 'Quick Sig' panel, you can import multiple local images at once. Copy the photos you want to use in your signature into the same folder as this executable (the 'working directory'), then click the 'SCAN FOLDER' button. This will add all image files in the working directory to the list. Supported are .jpg, .png, .jpeg, .JPG, .PNG, and .JPEG image files.").style("max-width:450px;")
				ui.label("(2) You can import images one by one from anywhere on cour computer. Use the 'Add photo: +' button on the bottom of the list, then browse your files or drag & drop in an image file.").style("max-width:450px;")
				ui.label("(3) You can import images one by one from the web. Use the 'Add photo: Web' button on the bottom of the list, then enter the URL to an image file.").style("max-width:450px;")
				with ui.row():
					ui.icon("o_announcement",color="primary", size="25px")
					ui.label("All rows that contain photos will be included in your signature. Rows that contain only text (names/epithets) will be ignored when generating a signature.").style("max-width:350px;")
				ui.button("Close", on_click=help_new_photos_dialog.close, color="positive")

		with ui.dialog() as help_new_names_dialog, ui.card():
			with ui.column().classes("items-center"):
				ui.icon("o_info", size="100px")
				ui.label("You can add text in the name column that will be be applied on top of your photos. This could be the name of the character in the photo, but effectively you can use it for any short string of text. If there is a photo present in the photo column, you can use the 'Add/edit name' button in the corresponding row to enter the name text.").style("max-width:450px;")
				with ui.row():
					ui.icon("o_announcement",color="primary", size="25px")
					ui.label("The text may not contain any line breaks. Too long text strings may not get applied correctly.").style("max-width:350px;")
				ui.label("If you don't want to enter names into the table one by one, you can import them from a text file instead:").style("max-width:450px;")
				ui.label("You can enter the names you want to use into the 'names.txt' text file that is located in the same folder as this executable. (Delete the sample text inside the file first.) Put every name you want to enter on a separate line. Save the file, then click the 'READ NAMES.TXT' button.").style("max-width:450px;")
				ui.label("If you don't have a 'names.txt' file, you can create it yourself. Just make sure it's a plain text (.txt) file, preferrably with Unicode (UTF-8) encoding.").style("max-width:450px;")
				with ui.row():
					ui.icon("o_announcement",color="primary", size="25px")
					ui.label("Rows that contain only text (names/epithets) will be ignored when generating a signature.").style("max-width:350px;")
				ui.button("Close", on_click=help_new_names_dialog.close, color="positive")

		with ui.dialog() as help_new_epithets_dialog, ui.card():
			with ui.column().classes("items-center"):
				ui.icon("o_info", size="100px")
				ui.label("You can add text in the epithet column that will be be applied on top of your photos. This works just the same as for the name text. The epithet is intended to give you a second text layer to add onto the name. It can be used for any short string of text, e.g. to add a nickname or epithet, to split the first and last name between layers or to write the name in an alternate script.  If there is a photo present in the photo column, you can use the 'Add/edit epithet' button in the corresponding row to enter the epithet text.").style("max-width:450px;")
				with ui.row():
					ui.icon("o_announcement",color="primary", size="25px")
					ui.label("The text may not contain any line breaks. Too long text strings may not get applied correctly.").style("max-width:350px;")
				ui.label("If you don't want to enter epithets into the table one by one, you can import them from a text file instead:").style("max-width:450px;")
				ui.label("You can enter the epithets you want to use into the 'epithets.txt' text file that is located in the same folder as this executable. (Delete the sample text inside the file first.) Put every epithet you want to enter on a separate line. Save the file, then click the 'READ EPITHETS.TXT' button.").style("max-width:450px;")
				ui.label("If you don't have an 'epithets.txt' file, you can create it yourself. Just make sure it's a plain text (.txt) file, preferrably with Unicode (UTF-8) encoding.").style("max-width:450px;")
				with ui.row():
					ui.icon("o_announcement",color="primary", size="25px")
					ui.label("Rows that contain only text (names/epithets) will be ignored when generating a signature.").style("max-width:350px;")
				ui.button("Close", on_click=help_new_epithets_dialog.close, color="positive")

		with ui.dialog() as help_new_fonts_dialog, ui.card():
			with ui.column().classes("items-center"):
				ui.icon("o_info", size="100px")
				ui.label("You can select which fonts to apply to your name and epithet texts. The application comes bundled with a few fonts in the 'fonts' subfolder.").style("max-width:450px;")
				ui.label("If you would like to use other fonts, you can copy any of your own font files into the 'fonts' subfolder and then click on 'SCAN FONTS' below. Supported are .ttf, .otf, .TTF and .OTF font files.").style("max-width:450px;")
				ui.button("Scan Fonts", on_click=lambda: rescan_fonts())
				with ui.row():
					ui.icon("o_announcement",color="primary", size="25px")
					ui.label("If you're using non-alphanumeric scripts (e.g. Chinese, Japanese, Korean, ...)' as names/epithets, make sure you use a font that supports the corresponding script. The fonts bundled with this application support Japanese scripts, but please provide your own font(s) if you wish to use other scripts. If glyphs in the sample images below appear garbled, missing or as rectangles, this usually indicates that the selected font does not support the current script.").style("max-width:350px;")
				ui.button("Close", on_click=help_new_fonts_dialog.close, color="positive")

		with ui.dialog() as help_new_alignment_dialog, ui.card():
			with ui.column().classes("items-center"):
				ui.icon("o_info", size="100px")
				ui.label("You can select the edge/corner of the photo to which names and epithets will automatically align to. Since every font uses slightly different spacing, you can use the 'Offset' horizontal and vertical sliders to fine-tune the position afterwards. Change the 'Sample from entry #' above, to check how your settings look on any of your entries in the photo table.").style("max-width:450px;")
				with ui.row():
					ui.icon("o_announcement",color="primary", size="25px")
					ui.label("The 'Squish' and 'Shrink' settings above will produce best results with a horizontal 'Offset' of 0.").style("max-width:350px;")
				ui.button("Close", on_click=help_new_alignment_dialog.close, color="positive")

		
		@ui.refreshable
		def new_button_undoDisplay() -> None:
			if new_undoable_flag:
				with ui.button(icon="o_undo", on_click=lambda:I_new_undofunc()).style("width:50px;"):
					ui.tooltip("Undo").classes("default_tooltip")
			else:
				with ui.button(icon="o_undo", color="accent").style("width:50px;").props("disable"):
					ui.tooltip("Cannot undo any further.").classes("default_tooltip")

		@ui.refreshable
		def new_ui_characterlist() -> None:
			global new_table_index
			new_table_length = max(1+len(I_new),len(namesE),len(namesJ))
			new_id = 0
			new_table_index=[]
			with ui.grid(columns="50px 160px 35px 160px 35px 160px 35px 50px").classes("items-center"):
				with ui.column().classes("items-center"):
					ui.label("#")
				with ui.column().classes("items-center"):
					ui.label("Photo")
				with ui.button(icon="o_delete", on_click=lambda: I_new_clear(), color="secondary").style("width:35px;"):
					ui.tooltip("Clear all photos").classes("default_tooltip")
				with ui.row().classes("items-center"):
					ui.space()
					ui.label("Name")
				with ui.button(icon="o_delete", on_click=lambda: namesE_clear(), color="secondary").style("width:35px;"):
					ui.tooltip("Clear all names").classes("default_tooltip")
				with ui.row().classes("items-center"):
					ui.space()
					ui.label("Epithet")
				with ui.button(icon="o_delete", on_click=lambda: namesJ_clear(), color="secondary").style("width:35px;"):
					ui.tooltip("Clear all epithets").classes("default_tooltip")
				#with ui.column().classes("items-center"):
				#	ui.label("Delete row")
				ui.label(" ")

				#table of photos & names
				while new_id<new_table_length:

					#buttons to move entire row
					with ui.column().classes("items-center"):
						if new_id<1 or new_id>=len(I_new):
							ui.button(icon="o_expand_less", color="accent").style("width:50px;").props("disable")
						else:
							with ui.button(icon="o_expand_less", on_click=lambda iid=new_id:row_new_moveup(iid)).style("width:50px;"):
								ui.tooltip("Move entire row").props("max-width='200px'").classes("default_tooltip")
						ui.label(new_id+1)
						if new_id>=new_table_length-1 or new_id>=len(I_new)-1:
							ui.button(icon="o_expand_more", color="accent").style("width:50px;").props("disable")
						else:
							with ui.button(icon="o_expand_more", on_click=lambda iid=new_id:row_new_movedn(iid)).style("width:50px;"):
								ui.tooltip("Move entire row").props("max-width='200px'").classes("default_tooltip")

					#buttons to move images
					if len(I_new)>new_id:
						ui.image(I_new[new_id]).props(f"width=150px height=150px")
						with ui.column().classes("items-center gap-0"):
							if new_id<1:
								ui.button(icon="o_expand_less", color="accent").style("width:35px; height:30px;").props("disable")
							else:
								ui.button(icon="o_expand_less", on_click=lambda iid=new_id:I_new_moveup(iid)).style("width:35px; height:30px;")
							ui.element("spacer").style("height:38px;")
							if new_id>=len(I_new)-1:
								ui.button(icon="o_expand_more", color="accent").style("width:35px; height:30px;").props("disable")
							else:
								ui.button(icon="o_expand_more", on_click=lambda iid=new_id:I_new_movedn(iid)).style("width:35px; height:30px;")
					elif len(I_new)==new_id:
						with ui.column().classes("items-center gap-0"):
							ui.label("Add Photo:")
							with ui.button_group():
								with ui.button(icon="o_add_circle_outline", on_click=lambda: import_local()).style("width:65px; height:65px;"):
									ui.tooltip("Import a single image stored on your PC.").props("max-width='200px'").classes("default_tooltip")
								with ui.button(icon="o_language", on_click=lambda: import_from_url()).style("width:65px; height:65px;"):
									ui.tooltip("Import a single image from the web.").props("max-width='200px'").classes("default_tooltip")
						ui.label(" ")
					else:
						ui.label("No Photo")
						ui.label(" ")

					#buttons to move EN names
					if len(namesE)>new_id:
						with ui.row().classes("items-center"):
							ui.space()
							ui.label(f"{namesE[new_id]}")
						with ui.column().classes("items-center gap-0"):
							if new_id<1:
								ui.button(icon="o_expand_less", color="accent").style("width:35px; height:30px;").props("disable")
							else:
								ui.button(icon="o_expand_less", on_click=lambda iid=new_id:namesE_moveup(iid)).style("width:35px; height:30px;")
							with ui.button(icon="o_edit", on_click=lambda iid=new_id:I_new_renameE(iid)).style("width:35px; height:30px;"):
								ui.tooltip("Add/edit name").classes("default_tooltip")
							if new_id>=len(namesE)-1:
								ui.button(icon="o_expand_more", color="accent").style("width:35px; height:30px;").props("disable")
							else:
								ui.button(icon="o_expand_more", on_click=lambda iid=new_id:namesE_movedn(iid)).style("width:35px; height:30px;")
					else:
						ui.label(" ")
						ui.label(" ")

					#buttons to move JP names
					if len(namesJ)>new_id:
						with ui.row().classes("items-center"):
							ui.space()
							ui.label(f"{namesJ[new_id]}")
						with ui.column().classes("items-center gap-0"):
							if new_id<1:
								ui.button(icon="o_expand_less", color="accent").style("width:35px; height:30px;").props("disable")
							else:
								ui.button(icon="o_expand_less", on_click=lambda iid=new_id:namesJ_moveup(iid)).style("width:35px; height:30px;")
							with ui.button(icon="o_edit", on_click=lambda iid=new_id:I_new_renameJ(iid)).style("width:35px; height:30px;"):
								ui.tooltip("Add/edit epithet").classes("default_tooltip")
							if new_id>=len(namesJ)-1:
								ui.button(icon="o_expand_more", color="accent").style("width:35px; height:30px;").props("disable")
							else:
								ui.button(icon="o_expand_more", on_click=lambda iid=new_id:namesJ_movedn(iid)).style("width:35px; height:30px;")
					else:
						ui.label(" ")
						ui.label(" ")

					# button to delete row
					if len(I_new)>new_id:
						with ui.button(icon="o_delete", on_click=lambda iid=new_id:row_new_delete(iid), color="secondary").style("width:50px; height:50px;"):
							ui.tooltip("Remove entire row").classes("default_tooltip")
					else:
						ui.button(icon="o_delete", color="accent").style("width:50px; height:50px;").props("disable")
					new_id=new_id+1
					new_table_index.append(new_id)
			while len(new_table_index)>len(namesE):
				new_table_index.pop(len(new_table_index)-1)


		@ui.refreshable
		def new_ui_imgSettings() -> None:
			with ui.grid(columns="50px 160px 35px 160px 35px 160px 35px 50px").classes("items-center"):
				ui.label(" ")
				with ui.button_group().classes("col-span-2"):
					with ui.button("Scan Folder",on_click=lambda:import_new_launch()).style("width:178px;"):
						ui.tooltip("Scan for images in the working directory.").props("max-width='200px'").classes("default_tooltip")
					ui.button(icon="o_help_outline", on_click=help_new_photos_dialog.open, color="positive").style("width:35px;")
				with ui.button_group().classes("col-span-2"):
					with ui.button("Read 'names.txt'",on_click=lambda:import_namesE()).style("width:178px;"):
						ui.tooltip("Read in names from the 'names.txt' file.").props("max-width='200px'").classes("default_tooltip")
					ui.button(icon="o_help_outline", on_click=help_new_names_dialog.open, color="positive").style("width:35px;")
				with ui.button_group().classes("col-span-2"):
					with ui.button("Read 'epithets.txt'",on_click=lambda:import_namesJ()).style("width:178px;"):
						ui.tooltip("Read in text from the 'epithets.txt' file.").props("max-width='200px'").classes("default_tooltip")
					ui.button(icon="o_help_outline", on_click=help_new_epithets_dialog.open, color="positive").style("width:35px;")
				new_button_undoDisplay()
			new_ui_characterlist()

		new_ui_imgSettings()


		def set_colorEmain(colorEmain_new):
			global colorEmain
			colorEmain=colorEmain_new
			update_textsample()

		def set_colorEoutline(colorEoutline_new):
			global colorEoutline
			colorEoutline=colorEoutline_new
			update_textsample()

		def set_colorJmain(colorJmain_new):
			global colorJmain
			colorJmain=colorJmain_new
			update_textsample()

		def set_colorJoutline(colorJoutline_new):
			global colorJoutline
			colorJoutline=colorJoutline_new
			update_textsample()

		ui.separator()

		ui.label("Chose what appearance the individual photos should have in your signature. (Black areas will become transparent.)").style("max-width:550px;")

		def set_new_alphamask(new_aMask_select):
			global new_alphamask

			new_alphamask = new_aMask_select

			if new_alphamask==aMask_circle:
				button_new_AMcircle.props("color=primary")
			else:
				button_new_AMcircle.props("color=positive")
			if new_alphamask==aMask_blrcir:
				button_new_AMblrcir.props("color=primary")
			else:
				button_new_AMblrcir.props("color=positive")
			if new_alphamask==aMask_square:
				button_new_AMsquare.props("color=primary")
			else:
				button_new_AMsquare.props("color=positive")
			if new_alphamask==aMask_sqedge:
				button_new_AMsqedge.props("color=primary")
			else:
				button_new_AMsqedge.props("color=positive")
			if new_alphamask==aMask_blrsqr:
				button_new_AMblrsqr.props("color=primary")
			else:
				button_new_AMblrsqr.props("color=positive")
			if new_alphamask==aMask_rndrec:
				button_new_AMrndrec.props("color=primary")
			else:
				button_new_AMrndrec.props("color=positive")
			if new_alphamask==aMask_blrdrc:
				button_new_AMblrdrc.props("color=primary")
			else:
				button_new_AMblrdrc.props("color=positive")
			if new_alphamask==aMask_skdrec:
				button_new_AMskdrec.props("color=primary")
			else:
				button_new_AMskdrec.props("color=positive")
			if new_alphamask==aMask_blskrc:
				button_new_AMblskrc.props("color=primary")
			else:
				button_new_AMblskrc.props("color=positive")
			update_imagesample()

		with ui.row(wrap=True):
			with ui.button(on_click=lambda: set_new_alphamask(aMask_circle)).style("width:200px; height:200px;") as button_new_AMcircle:
				ui.image(aMask_circle).props("width=170px height=170px")
			with ui.button(on_click=lambda: set_new_alphamask(aMask_blrcir)).style("width:200px; height:200px;").props("color=positive") as button_new_AMblrcir:
				ui.image(aMask_blrcir).props("width=170px height=170px")
			with ui.button(on_click=lambda: set_new_alphamask(aMask_square)).style("width:200px; height:200px;").props("color=positive") as button_new_AMsquare:
				ui.image(aMask_square).props("width=170px height=170px")
			with ui.button(on_click=lambda: set_new_alphamask(aMask_sqedge)).style("width:200px; height:200px;").props("color=positive") as button_new_AMsqedge:
				ui.image(aMask_sqedge).props("width=170px height=170px")
			with ui.button(on_click=lambda: set_new_alphamask(aMask_blrsqr)).style("width:200px; height:200px;").props("color=positive") as button_new_AMblrsqr:
				ui.image(aMask_blrsqr).props("width=170px height=170px")
			with ui.button(on_click=lambda: set_new_alphamask(aMask_rndrec)).style("width:200px; height:200px;").props("color=positive") as button_new_AMrndrec:
				ui.image(aMask_rndrec).props("width=170px height=170px")
			with ui.button(on_click=lambda: set_new_alphamask(aMask_blrdrc)).style("width:200px; height:200px;").props("color=positive") as button_new_AMblrdrc:
				ui.image(aMask_blrdrc).props("width=170px height=170px")
			with ui.button(on_click=lambda: set_new_alphamask(aMask_skdrec)).style("width:200px; height:200px;").props("color=positive") as button_new_AMskdrec:
				ui.image(aMask_skdrec).props("width=170px height=170px")
			with ui.button(on_click=lambda: set_new_alphamask(aMask_blskrc)).style("width:200px; height:200px;").props("color=positive") as button_new_AMblskrc:
				ui.image(aMask_blskrc).props("width=170px height=170px")


		ui.separator()

		@ui.refreshable
		def new_ui_fontEselect():
			global fontE
			with ui.column().classes("col-span-2 gap-0"):
				ui.label("Name Font:")
				fontE = ui.select(fonts_list, value=False, on_change=lambda:update_textsample()).style("width:200px;")
			#return(fontE)

		@ui.refreshable
		def new_ui_fontJselect():
			global fontJ
			with ui.column().classes("col-span-2 gap-0"):
				ui.label("Epithet Font:")
				fontJ = ui.select(fonts_list, value=False, on_change=lambda:update_textsample()).style("width:200px;")
			#return(fontJ)

		ui.label("If you want to apply name and/or epithet text to your photos, select a font below. Selecting 'false' means that no corresponding text will be applied.").style("max-width:550px;")
		with ui.grid(columns="50px 160px 35px 160px 35px 160px 35px 50px"):#.classes("items-center"):
			ui.label(" ")
			with ui.column().classes("col-span-2 gap-0"):
				ui.label("Which layer on top?")
				names_priority = ui.radio(["Name", "Epithet"], value="Name", on_change=lambda:update_textsample())#.props("inline")
			new_ui_fontEselect()
			new_ui_fontJselect()
			ui.button(icon="o_help_outline", on_click=help_new_fonts_dialog.open , color="positive").style("width:35px; height:35px;")

			ui.label(" ").classes("col-span-3")
			with ui.column().classes("col-span-2"):
				with ui.button_group(): #with ui.row().classes("gap-0"):
					with ui.button("Text Color", icon="o_format_color_text").style("width:150px;"):
						ui.color_picker(on_pick=lambda e: set_colorEmain(e.color))
					with ui.button(icon="o_palette", on_click=lambda:set_colorEmain("#ff6065"), color="positive").style("width:50px;"):
						ui.tooltip("Default color").props("max-width='200px'").classes("default_tooltip")
			with ui.column().classes("col-span-2"):
				with ui.button_group():
					with ui.button("Text Color", icon="o_format_color_text").style("width:150px;"):
						ui.color_picker(on_pick=lambda e: set_colorJmain(e.color))
					with ui.button(icon="o_content_copy", on_click=lambda:set_colorJmain(colorEmain), color="positive").style("width:50px;"):
						ui.tooltip("Copy current fill color from names").props("max-width='200px'").classes("default_tooltip")
			ui.label(" ")
	
			ui.label(" ")
			with ui.column().classes("col-span-2 gap-0"):
				ui.element("spacer").style("height:5px;")
				with ui.row().classes("items-center"):
					ui.space()
					ui.label("Text Opacity:")
				ui.element("spacer").style("height:20px;")
				with ui.row().classes("items-center"):
					ui.space()
					ui.label("Text Size:")
			with ui.column().classes("col-span-2"):
				with ui.row().classes("items-center"):
					slider_transpEmain = ui.slider(min=5,max=100,step=5,value=100, on_change=lambda:update_textsample()).style("width:160px;")
					ui.label().bind_text_from(slider_transpEmain,"value")
				with ui.row().classes("items-center"):
					slider_sizeEmain = ui.slider(min=6,max=88,value=30, on_change=lambda:update_textsample()).style("width:160px;")
					ui.label().bind_text_from(slider_sizeEmain,"value")
				with ui.button_group():
					with ui.button("Outline", icon="o_border_color").style("width:150px;"):
						ui.color_picker(on_pick=lambda e: set_colorEoutline(e.color))
					with ui.button(icon="o_format_color_reset", on_click=lambda:set_colorEoutline(False), color="secondary").style("width:50px;"):
						ui.tooltip("No text outline").props("max-width='200px'").classes("default_tooltip")
			with ui.column().classes("col-span-2"):
				with ui.row().classes("items-center"):
					slider_transpJmain = ui.slider(min=5,max=100,step=5,value=100, on_change=lambda:update_textsample()).style("width:160px;")
					ui.label().bind_text_from(slider_transpJmain,"value")
				with ui.row().classes("items-center"):
					slider_sizeJmain = ui.slider(min=6,max=88,value=30, on_change=lambda:update_textsample()).style("width:160px;")
					ui.label().bind_text_from(slider_sizeJmain,"value")
				with ui.button_group():
					with ui.button("Outline", icon="o_border_color").style("width:130px;"):
						ui.color_picker(on_pick=lambda e: set_colorJoutline(e.color))
					with ui.button(icon="o_content_copy", on_click=lambda:set_colorJoutline(colorEoutline), color="positive").style("width:35px;"):
						ui.tooltip("Copy current outline color from names").props("max-width='200px'").classes("default_tooltip")
					with ui.button(icon="o_format_color_reset", on_click=lambda:set_colorJoutline(False), color="secondary").style("width:35px;"):
						ui.tooltip("No text outline").props("max-width='200px'").classes("default_tooltip")
			ui.label(" ")

			ui.label(" ")
			with ui.column().classes("col-span-2 gap-0"):
				ui.element("spacer").style("height:5px;")
				with ui.row().classes("items-center"):
					ui.space()
					ui.label("Outline Opacity:")
				ui.element("spacer").style("height:20px;")
				with ui.row().classes("items-center"):
					ui.space()
					ui.label("Outline Thickness:")
			with ui.column().classes("col-span-2"):
				with ui.row().classes("items-center"):
					slider_transpEoutline = ui.slider(min=5,max=100,step=5,value=100, on_change=lambda:update_textsample()).style("width:160px;")
					ui.label().bind_text_from(slider_transpEoutline,"value")
				with ui.row().classes("items-center"):
					slider_sizeEoutline = ui.slider(min=1,max=10,value=2, on_change=lambda:update_textsample()).style("width:160px;")
					ui.label().bind_text_from(slider_sizeEoutline,"value")
			with ui.column().classes("col-span-2"):
				with ui.row().classes("items-center"):
					slider_transpJoutline = ui.slider(min=5,max=100,step=5,value=100, on_change=lambda:update_textsample()).style("width:160px;")
					ui.label().bind_text_from(slider_transpJoutline,"value")
				with ui.row().classes("items-center"):
					slider_sizeJoutline = ui.slider(min=1,max=10,value=2, on_change=lambda:update_textsample()).style("width:160px;")
					ui.label().bind_text_from(slider_sizeJoutline,"value")

		@ui.refreshable
		def new_ui_imageSample() -> None:
			if imagesample:
				ui.image(imagesample).props(f"width={200}px height={200}px").classes("col-span-2").props("no-transition no spinner")
			else:
				ui.label("No preview image").classes("col-span-2")

		def set_nameEalign(positionX,positionY):
			global nameEalignX
			global nameEalignY
			if nameEalignX != positionX:
				slider_nameEoffsetx.value=0
			if nameEalignY != positionY:
				slider_nameEoffsety.value=0
			nameEalignX = positionX
			nameEalignY = positionY
			update_imagesample()

		def set_nameJalign(positionX,positionY):
			global nameJalignX
			global nameJalignY
			if nameJalignX != positionX:
				slider_nameJoffsetx.value=0
			if nameJalignY != positionY:
				slider_nameJoffsety.value=0
			nameJalignX = positionX
			nameJalignY = positionY
			update_imagesample()

		@ui.refreshable
		def new_ui_fontSamples() -> None:
			global select_textsample_no
			with ui.grid(columns="50px 160px 35px 160px 35px 160px 35px 50px"): #.classes("items-center"):
				ui.label(" ")
				with ui.column().classes("col-span-2 gap-0"):
					ui.label("Sample from entry #:")
					if new_table_index:
						select_textsample_no = ui.select(new_table_index, value=textsample_no, on_change=lambda:update_textsample())
					else:
						select_textsample_no = ui.select([1], value=1).props("disable")
					ui.element("spacer").style("height:80px;")
					ui.label("How to handle oversized text?")
				if fontE.value and namesE[textsample_no-1]:
					with ui.column().classes("col-span-2 gap-0"):
						ui.label("Sample:")
						sampleE2 = sampleE.copy()
						cropheight = sampleE2.size[1]
						sampleE2 = sampleE2.crop((0,0,200,cropheight))
						ui.image(sampleE2).props(f"width={200}px height={sampleE2.size[1]}px no-transition no spinner")
				else:
					ui.label(" ").classes("col-span-2")
				if fontJ.value and namesJ[textsample_no-1]:
					with ui.column().classes("col-span-2 gap-0"):
						ui.label("Sample:")
						sampleJ2 = sampleJ.copy()
						cropheight = sampleJ2.size[1]
						sampleJ2 = sampleJ2.crop((0,0,200,cropheight))
						ui.image(sampleJ2).props(f"width={200}px height={sampleJ2.size[1]}px no-transition no spinner")
				else:
					ui.label(" ").classes("col-span-2")
				ui.label(" ")

		new_ui_fontSamples()
		with ui.row():
			ui.element("spacer").style("width:50px;")
			new_handle_oversize = ui.radio(["Squish", "Shrink", "Ignore (Crop)"], value="Squish", on_change=lambda:update_textsample()).props("inline")
		
		def new_reset_offset():
			slider_nameEoffsetx.value=0
			slider_nameEoffsety.value=0
			slider_nameJoffsetx.value=0
			slider_nameJoffsety.value=0
			update_imagesample()
		
		with ui.grid(columns = "50px 160px 35px 160px 35px 160px 35px 50px").classes("items-center"):
			ui.label(" ")
			new_ui_imageSample()
			with ui.column().classes("gap-0"):
				ui.label("Set alignment for Name")
				ui.element("spacer").style("height:5px;")
				with ui.row().classes("gap-0"):
					ui.button(icon="o_north_west", on_click=lambda:set_nameEalign("left","top")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_north", on_click=lambda:set_nameEalign("center","top")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_north_east", on_click=lambda:set_nameEalign("right","top")).style("width:40px; height:40px;")
				ui.element("spacer").style("height:20px;")
				with ui.row().classes("gap-0"):
					ui.button(icon="o_west", on_click=lambda:set_nameEalign("left","center")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_zoom_in_map", on_click=lambda:set_nameEalign("center","center")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_east", on_click=lambda:set_nameEalign("right","center")).style("width:40px; height:40px;")
				ui.element("spacer").style("height:20px;")
				with ui.row().classes("gap-0"):
					ui.button(icon="o_south_west", on_click=lambda:set_nameEalign("left","bottom")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_south", on_click=lambda:set_nameEalign("center","bottom")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_south_east", on_click=lambda:set_nameEalign("right","bottom")).style("width:40px; height:40px;")
			with ui.column().classes("gap-0"):
				slider_nameEoffsety = ui.slider(min=-50,max=50,value=0, on_change=lambda:update_imagesample()).props("vertical reverse").style("height:160px;")
				ui.element("spacer").style("height:5px;")
				ui.label().bind_text_from(slider_nameEoffsety,'value')
			with ui.column().classes("gap-0"):
				ui.label("Set alignment for Epithet")
				ui.element("spacer").style("height:5px;")
				with ui.row().classes("gap-0"):
					ui.button(icon="o_north_west", on_click=lambda:set_nameJalign("left","top")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_north", on_click=lambda:set_nameJalign("center","top")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_north_east", on_click=lambda:set_nameJalign("right","top")).style("width:40px; height:40px;")
				ui.element("spacer").style("height:20px;")
				with ui.row().classes("gap-0"):
					ui.button(icon="o_west", on_click=lambda:set_nameJalign("left","center")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_zoom_in_map", on_click=lambda:set_nameJalign("center","center")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_east", on_click=lambda:set_nameJalign("right","center")).style("width:40px; height:40px;")
				ui.element("spacer").style("height:20px;")
				with ui.row().classes("gap-0"):
					ui.button(icon="o_south_west", on_click=lambda:set_nameJalign("left","bottom")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_south", on_click=lambda:set_nameJalign("center","bottom")).style("width:40px; height:40px;")
					ui.element("spacer").style("width:20px;")
					ui.button(icon="o_south_east", on_click=lambda:set_nameJalign("right","bottom")).style("width:40px; height:40px;")
			with ui.column().classes("gap-0"):
				slider_nameJoffsety = ui.slider(min=-50,max=50,value=0, on_change=lambda:update_imagesample()).props("vertical reverse").style("height:160px;")
				ui.element("spacer").style("height:5px;")
				ui.label().bind_text_from(slider_nameJoffsety,'value')
			ui.button(icon="o_help_outline", on_click=help_new_alignment_dialog.open, color="positive").style("width:35px; height:35px;")
			ui.label(" ")
			ui.label("Offset (Sliders):").classes("col-span-2")
			slider_nameEoffsetx = ui.slider(min=-50,max=50,value=0, on_change=lambda:update_imagesample())
			ui.label().bind_text_from(slider_nameEoffsetx,'value')
			slider_nameJoffsetx = ui.slider(min=-50,max=50,value=0, on_change=lambda:update_imagesample())
			ui.label().bind_text_from(slider_nameJoffsetx,'value')
			with ui.button(icon="o_replay", on_click=lambda: new_reset_offset(), color="secondary").style("width:35px; height:35px;"):
				ui.tooltip("Reset offset to zero").props("max-width='200px'").classes("default_tooltip")


		ui.separator()

		ui.label("Select the preferred arrangement of photos in the signature.").style("max-width:550px;")
		new_image_layout = ui.radio(["Full Auto", "Auto: One Image", "Auto: Two Images", "Custom"], value="Full Auto", on_change=lambda:force_newlayout()).props("inline")

		def set_custom_columns(n_columns):
			global custom_columns
			global new_updated_flag
			custom_columns = math.floor(n_columns)
			new_updated_flag = False
			new_ui_siglayout.refresh()

		def set_custom_rows(n_rows):
			global custom_rows
			global new_updated_flag
			custom_rows = math.floor(n_rows)
			new_updated_flag = False
			new_ui_siglayout.refresh()

		@ui.refreshable
		def new_ui_layoutSample() -> None:
			if new_layout_images>0 and I_new:
				imgsizeX=math.floor(550/new_layout_columns)
				imgsizeY=math.floor(200/new_layout_rows)
				imgsize=min([imgsizeX,imgsizeY])
				imgsizeXX=imgsize*new_layout_columns
				imgsizeYY=imgsize*new_layout_rows
				img_unpadded=len(I_new)-((new_layout_images-1)*new_layout_rows*new_layout_columns)

				with ui.row():
					imgN=0
					imgY=1
					with ui.column().classes("gap-0 border p-1"):
						while imgY<=new_layout_rows:
							imgX=1
							with ui.row(wrap=False).classes("gap-0"):
								while imgX<=new_layout_columns:
									if imgN<img_unpadded:
										ui.icon("square",color="primary", size=f"{imgsize}px")#.style(f"width:{imgsize}px; height:{imgsize}px;")
									else:
										ui.icon("square",color="positive", size=f"{imgsize}px")#.style(f"width:{imgsize}px; height:{imgsize}px;")
									imgN=imgN+1
									imgX=imgX+1
							imgY=imgY+1
					ui.element("spacer").style("width:15px;")
					with ui.column():
						with ui.row():
							if new_layout_images==1:
								ui.label(f"{new_layout_images} signature image in total.")
							else:
								ui.label(f"{new_layout_images} signature images in total.")
							ui.label(f"{new_layout_columns * new_layout_rows} photos per image, arranged {new_layout_columns} by {new_layout_rows}.")
						ui.label(f"{new_layout_pad} padding on the final image (marked in grey).")
						ui.label(f"Signature image size: {new_layout_columns*imgsize}px by {new_layout_rows*imgsize}px")
						ui.label(f"Individual photo size: {imgsize}px by {imgsize}px")
						if new_layout_images>2:
							with ui.row().classes("items-center"):
								ui.icon("o_announcement",color="primary", size="25px")
								ui.label("You can only use a maximum of two images at a time in your signature!")

		@ui.refreshable
		def new_ui_siglayout() -> None:
			with ui.row().classes("items-center"):
				if new_updated_flag:
					with ui.button("Update Layout", color="accent").style("width:200px;").props("disable"):
						ui.tooltip("Already up to date").classes("default_tooltip")
				else:
					ui.button("Update Layout", on_click=lambda:generate_newlayout(new_image_layout.value, custom_columns, custom_rows)).style("width:200px;")
				if new_image_layout.value == "Custom":
					new_select_columns = ui.number(label="How many photos per row?", value=custom_columns, min=1, max=250, precision=0, on_change=lambda e: set_custom_columns(e.value)).style("width:220px;")
					new_select_rows = ui.number(label="How many rows per signature image?", value=custom_rows, min=1, max=100, precision=0, on_change=lambda e: set_custom_rows(e.value)).style("width:220px;")
			new_ui_layoutSample()
			ui.separator()

			ui.label("If all above settings are to your liking, generate a preview of the final signature images.").style("max-width:550px;")
			if new_updated_flag:
				ui.button("Generate Signature", on_click=lambda:generate_newsig()).style("width:200px;")
			else:
				with ui.button("Generate Signature", color="accent").style("width:200px;").props("disable"):
						ui.tooltip("Please update the layout!").classes("default_tooltip")

		new_ui_siglayout()


		@ui.refreshable
		def new_ui_sigDisplay() -> None:
			with ui.column():
				i_sig=1
				for sig_image in new_sig_scaled:
					ui.label(f"Signature Image #{i_sig:03d}:")
					ui.image(sig_image).style(f"width:{sig_image.size[0]}px; height:{sig_image.size[1]}px;")
					i_sig=i_sig+1
			if new_updated_flag and new_generated_flag:
				ui.label("Use the buttons below to save your preferred version of the signature image(s) in the 'signatures' subfolder. Previously exported files may get overwritten!").style("max-width:550px;")
				with ui.row():
					with ui.button("Export Default", icon="o_save", on_click=lambda:save_newsig_scaled()).style("width:200px;"):
						ui.tooltip("Export the images in a size that can be used as a signature.").props("max-width='200px'").classes("default_tooltip")
					with ui.button("Export Full Size", color="positive", on_click=lambda:save_newsig_fullsize()).style("width:200px;"):
						ui.tooltip("Export the images in full resolution. You may not be able to use them as a signature like this!").props("max-width='200px'").classes("default_tooltip")
					with ui.button("Export Individual", color="positive", on_click=lambda:save_newsig_single()).style("width:200px;"):
						ui.tooltip("Export all individual sub-images in full resolution. - For use in other software. You may not be able to use them as a signature like this!").props("max-width='200px'").classes("default_tooltip")

		new_ui_sigDisplay()

		ui.element("spacer").style("height:200px;")



## Load Config Panel
		
	with ui.tab_panel("Load Config"):
		ui.label("LOAD AND EDIT A PREVIOUSLY SAVED CONFIG FILE.")
		
		ui.label("This function is not yet available.")
				
ui.run() #comment out for building
#ui.run(reload=False, port=native.find_open_port()) #comment in for building
'''
Build with
nicegui-pack --onefile --icon ./icon/DDicon.png --name "DDsiggen_ver.<version number>" DDsiggen.py
'''
