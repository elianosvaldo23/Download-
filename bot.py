from yt import descargar_video_youtube
from yt import obtener_info_video
from yt import mostrar_info_video
from downurl import descargar_video_url
from upload import upload_rev
from upload import deletecloud
#from medisur_api import upload_medisur
#from deleteall import delete_rev_all
import struct
from collections import deque
import chardet
import tldextract
from urllib import request
from urllib.parse import urlparse
import urllib.parse
from math import floor
from aiohttp import FormData
from aiohttp_socks import ProxyConnector
import aiohttp_socks
from os import unlink
from time import sleep
from pathlib import Path
from time import localtime
from time import time
from datetime import datetime
from datetime import timedelta
import os
import math
import psutil
import aiohttp
import asyncio
import aiomysql
from pyrogram import Client, filters
import json  # Importar para manejar JSON
import re
import random
from random import randint
from bs4 import BeautifulSoup
from io import BufferedReader
from io import FileIO
from py7zr import SevenZipFile
from py7zr import FILTER_COPY
from multivolumefile import MultiVolume
import shutil
from pyrogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.handlers import CallbackQueryHandler
import unicodedata
import openai
from openai import OpenAI

#openai.api_key = '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'  # Reemplaza con tu clave API de OpenAI
client_openai = OpenAI(api_key="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")  # Clave en entorno

async def get_gpt_response(prompt: str) -> str:
    try:
        response = client_openai.chat.completions.create(
            model="gpt-3.5-turbo",  # o "gpt-4" si tienes acceso
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"🚨 Error: {str(e)}"


# BoT Configuration Variables
api_id = 13876032
api_hash = "c87c88faace9139628f6c7ffc2662bff"
bot_token = "7716154596:AAFy5dMzQEithATmAM53BTQhfCY6xGl2Gw0"
downlist = {} #lista de archivos descargados
root = {} #directorio actua
id_path = {}
seg = 0
cancel_uploads = {} 
cancel_upload = {} 
bot = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


USERS = [RoxanaArias6]
ADM = ["Osvaldo20032"]


async def create_db_connection():
    return await aiomysql.connect(host=db_host, port=3306, user=db_user, password=db_password, db=db_name)

# Cola global de descargas
download_queue = deque()
download_in_progress = False


# Manejador para la selección de calidad
@bot.on_callback_query(filters.regex(r"^yt_"))
async def seleccionar_calidad(client, callback_query):
    datos = callback_query.data.split("_")
    calidad = datos[1]
    url = "_".join(datos[2:])  # Recuperar la URL completa

    username = callback_query.from_user.username or str(callback_query.from_user.id)
    ruta_descarga = root[username]["actual_root"]

    await callback_query.answer(f"Descargando Video en {calidad}...")
    asyncio.create_task(descargar_video_youtube(url, ruta_descarga, callback_query.message, calidad))
    #await descargar_video_youtube(url, ruta_descarga, callback_query.message, calidad)


# Función para obtener el uso de recursos del sistema
def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')
    
    return (
        f"**Uso de CPU:** {cpu_usage}%\n"
        f"**Uso de RAM:** {ram_info.percent}%\n"
        f"**RAM Total:** {ram_info.total / (1024 ** 3):.2f} GB\n"
        f"**RAM Usada:** {ram_info.used / (1024 ** 3):.2f} GB\n"
        f"**RAM ibre:** {ram_info.free / (1024 ** 3):.2f} GB\n"
        f"**Disco Total:** {disk_info.total / (1024 ** 3):.2f} GB\n"
        f"**Disco Usado:** {disk_info.used / (1024 ** 3):.2f} GB\n"
        f"**Disco Libre:** {disk_info.free / (1024 ** 3):.2f} GB\n"
    )

# Función para mostrar el progreso de la descarga
async def download_progress(current, total, msg, start_time, position):
    global seg
    now = datetime.now().timestamp()
    elapsed = now - start_time
    speed = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / speed if speed > 0 else 0

    progress_bar = "[" + "■" * int((current / total) * 20) + "□" * (20 - int((current / total) * 20)) + "]"
    progress_text = (
        f"**Task is being Processed!**\n"
        f"{progress_bar} {current / total * 100:.2f}%\n"
        f"┠ **Processed:** {sizeof_fmt(current)} of {sizeof_fmt(total)}\n"
        f"┠ **Status:** #Cola\n"
        f"┠ **Posición:** #{position}\n"
        f"┠ **ETA:** {eta_fmt(eta)}\n"
        f"┠ **Speed:** {sizeof_fmt(speed)}/s\n"
        f"┠ **Elapsed:** {eta_fmt(elapsed)}\n"
     #   f"┖ **Engine:** Hackeroto2C\n"
    )
    if seg != localtime().tm_sec:
        try:
           await msg.edit(progress_text)
        except:pass
    seg = localtime().tm_sec
    

# Función para manejar la cola de descargas
async def process_download_queue():
    global download_in_progress
    while download_queue:
        download_in_progress = True
        task = download_queue.popleft()
        await task
    download_in_progress = False

# Función para agregar una tarea a la cola
async def add_to_queue(client: Client, message: Message, username: str, send):
    user_id = message.chat.id
    position = len(download_queue) + 1
    msg = await send(f"**Tu archivo ha sido añadido a la cola.\nPosición: #{position}**", quote=True)

    async def download_task():
        await process_download(client, message, username, send)
    
    download_queue.append(download_task())
    if not download_in_progress:
        asyncio.create_task(process_download_queue())

# Función para descargar archivos desde enlaces directos
async def download_from_url(msg, client: Client, message: Message, url: str, username: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    filename = url.split("/")[-1]
                    filepath = f"downloads/{username}/{filename}"
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded_size = 0
                    start_time = datetime.now().timestamp()

                    with open(filepath, "wb") as f:
                        async for chunk in response.content.iter_chunked(1024):
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            await download_progress(downloaded_size, total_size, msg, start_time, 1)
                    
                    await message.reply(f"**Descarga completada:** `{filename}`")
                else:
                    await message.reply("**Error: No se pudo descargar el archivo.**")
    except Exception as e:
        await message.reply(f"**Error:** {str(e)}")
        return

# Manejador para enlaces directos
async def progress_callback(current, total, message, start_time):
    """Función de callback para mostrael progreso de subida."""
    global seg
    now = time()
    user_id = message.chat.id
    diff = now - start_time
    if diff == 0:
        return
    if user_id in cancel_uploads and cancel_uploads[user_id]:  # Verifica si el usuario canceló
        await message.edit("**🚫  Subida cancelada  🚫**")
        return
    speed = current / diff
    percent = current * 100 / total
    speed_human = convert_bytes_to_human(speed)
    uploaded_human = convert_bytes_to_human(current)
    # **Archivo:** {os.path.basename(message.document.file_name)}
    total_human = convert_bytes_to_human(total)
    progress_text = f"""
    **Subiendo...**
    **┠ Processed:** {uploaded_human} of {total_human} | {percent:.2f}%
    **┠ Speed:** {speed_human}/s
    """
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Cancelar", callback_data=f"cancel_upload_{user_id}")]])
    if seg != localtime().tm_sec:
        try:
           await message.edit(progress_text, reply_markup=keyboard)
        except:pass
    seg = localtime().tm_sec

def convert_bytes_to_human(size):
    """Convierte bytes a una forma legible por humanos (KB, MB, GB, etc.)"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"

async def handle_callback_query(client, callback_query):
    user_id = callback_query.message.chat.id    
    if callback_query.data == f"cancel_upload_{user_id}":
        cancel_uploads[user_id] = True
        await callback_query.answer("🚫Task canceled🚫")
        return
    elif callback_query.data == f"cancel_uploa_{user_id}":
        cancel_upload[user_id] = True
        await callback_query.answer("🚫Task canceled🚫")
        return
        

def files_formatter(path, username):
    filespath = Path(path)
    result = sorted([p.name for p in filespath.glob("*") if p.is_file()])
    dirc = sorted([p.name for p in filespath.glob("*") if p.is_dir()])
    sizee = 0
    
    msg = f'**Plan Free Server | {sizeof_fmt(104857600)}/days**\nDirectorio Actual: `{path.split("downloads/")[-1]}`\n/back Volver Atras\n/delete_all Borrar todo el directorio\n'
    final = dirc + result

    if not final:
        msg += f'`➣➣Tolal Storage: {sizeof_fmt(sizee)}`\n\n'
        return msg, final
    for i, n in enumerate(final):
        sizee += Path(path, n).stat().st_size
    msg += f'`➣➣Tolal Storage: {sizeof_fmt(sizee)}`\n\n'
    for i, n in enumerate(final):
        size = Path(path, n).stat().st_size   
        if not "." in n:
            msg += f"{i} 📂 `{n}`\n"
        else:
            msg += f"{i} `📃 {n} | {sizeof_fmt(size)}`\n"
    return msg, final


  
async def limite_msg(text,username):
    lim_ch = 1500
    text = text.splitlines() 
    msg = ''
    msg_ult = '' 
    c = 0
    for l in text:
        if len(msg +"\n" + l) > lim_ch:		
            msg_ult = msg
            await bot.send_message(username,msg)	
            msg = ''
        if msg == '':	
            msg+= l
        else:		
            msg+= "\n" +l	
        c += 1
        if len(text) == c and msg_ult != msg:
            await bot.send_message(username,msg)

def limpiar_texto(filename):
    nombre = filename
    # Normalizar tildes y caracteres especiales
    nombre = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('ASCII')
    
    # Eliminar caracteres especiales (excepto letras, números, espacios y guiones)
    nombre = re.sub(r'[^\w\s.-]', '', nombre)
    
    # Reemplazar espacios en blanco por guiones
    nombre = nombre.replace(' ', '-')
    
    # Convertir a minúsculas (opcional)
    nombre = nombre.lower()
    texto_limpio = nombre
    return texto_limpio
    
def limpiar_textoj(texto):
    # Diccionario de reemplazos
    reemplazos = str.maketrans(
        'áéíúñÁÉÍÚÑ',
        'aeiunAEIUN'
    )
    texto_limpio = re.sub(r'[^\w\s]', '', texto).translate(reemplazos).replace(' ', '_')
    if '.' in texto:
        texto_limpio += texto[texto.rfind('.'):]  # Asumiendo que deseas conservar el '.' y todo lo que sigue
    return texto_limpio
  
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
           return "%3.2f%s%s" % (num, unit, suffix)
        num /= 1024.0 
    return "%.2f%s%s" % (num, 'Yi', suffix)

def update_progress_bar(chunk, filesize, bar_length=20):
    """Genera una barra de progreso visual."""
    percent = chunk / filesize
    filled_length = int(round(bar_length * percent))
    bar = '■' * filled_length + '□' * (bar_length - filled_length)+ f" {percent:.2%}"
    return bar
  
def eta_fmt(seconds):
   """Convierte segundos a un formato de tiempo legible (HH:MM:SS)"""
   if seconds < 0:
     return "00:00:00"
   hours = floor(seconds / 3600)
   minutes = floor((seconds % 3600) / 60)
   seconds = floor(seconds % 60)

   return f"{hours:02}:{minutes:02}:{seconds:02}"
  
async def downloadmessage_progres(chunk, filesize, filename, start, message):
    global seg
    user_id = message.chat.id
    if user_id in cancel_upload and cancel_upload[user_id]:  # Verifica si el usuario canceló
        await message.edit("**Download Stopped!\n┠ Plan: Free\n┠ \n┖ Reason: Cancelled by user!**")
        return
    now = time()
    diff = now - start
    if diff <= 0: #Evitamos la division por cero
       diff = 1
    mbs = chunk / diff
    percent = update_progress_bar(chunk, filesize)
    processed_size = sizeof_fmt(chunk)
    total_size = sizeof_fmt(filesize)
    speed = sizeof_fmt(mbs) + "/s"
    eta_seconds = (filesize - chunk) / mbs if mbs > 0 else 0
    eta = eta_fmt(eta_seconds)

    msg = "Task is being Processed!\n"
    msg += f"┠ File: {filename}\n"
    msg += f"┃ {update_progress_bar(chunk, filesize, 15)}\n"
    msg += f"┠ Processed: {processed_size} of {total_size}\n"
    msg += f"┖ Speed: {speed} | ETA: {eta}\n"
    msg += f"┠ Status: #TelegramDownload"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Cancelar", callback_data=f"cancel_uploa_{user_id}")]])
    if seg != localtime().tm_sec:
        try:
           await message.edit(msg, reply_markup=keyboard)
        except:pass
    seg = localtime().tm_sec

  
async def process_download(client: Client, message: Message, username: str, send):
    user_id = message.chat.id
    msg = await send("Verificando Archivo ", quote=True)
    
    if username not in root:
        root[username] = {"actual_root": f"downloads/{username}"}

    # Verificar si el mensaje es un archivo multimedia o un enlace directo
    if message.media:  # Si es un archivo multimedia
        try:
            filesize = int(str(message).split('"file_size":')[1].split(",")[0])
            match = re.search(r'"file_name": "([^"]+)"', str(message))
            if match:
                filename = match.group(1)  # Obtener el nombre del archivo
            filename = limpiar_texto(filename)
        except Exception as e:
            filename = str(randint(11111, 999999)) + ".mp4"
            filesize = 0  # Tamaño desconocido

        start = time()
        await msg.edit(f"**Iniciando Descarga...**\n\n`{filename}`")

        try:
            a = await message.download(
                file_name=str(root[username]["actual_root"]) + "/" + filename,
                progress=downloadmessage_progres,
                progress_args=(filename, start, msg),
            )
            cancel_upload[user_id] = False
            if Path(str(root[username]["actual_root"]) + "/" + filename).stat().st_size == filesize:
                await msg.edit("**Descarga Finalizada**")
            else:
                file_name = str(root[username]["actual_root"]) + "/" + filename
                unlink(file_name)
        except Exception as ex:
            if "[400 MESSAGE_ID_INVALID]" not in str(ex):
                await client.send_message(username, ex)

    else:  # Si es un enlace directo
        url = message.text.split(" ")[1]
        await download_from_url(msg, client, message, url, username)
        
    msgg = files_formatter(str(root[username]["actual_root"]), username)
    await limite_msg(msgg[0], username)


@bot.on_message(filters.media & filters.private)
async def down_media(client: Client, message: Message):
    username = message.from_user.username or str(message.from_user.id)
    await add_to_queue(client, message, username, message.reply)

# Función para formatear el tamaño de archivo
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return f"{num:.2f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.2f} Yi{suffix}"

# Función para formatear el tiempo
def eta_fmt(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
          
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant

# ID del canal al que los usuarios deben unirse
CANAL_ID = -1002302159104  # Reemplaza con el ID de tu canal

@bot.on_message(filters.private)
async def handle_message(client, message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    mss = message.text
        
    if username not in downlist:
        downlist[username] = []
    if username not in root:
        root[username] = {"actual_root": f"downloads/{username}"}

  #  if username not in USERS or username not in ADM:
  #      await message.reply_text("No tienes acceso a este Bot\nContacta a @Stvz20")
    
    if message.text.startswith('/start'):
        # Mensaje de bienvenida con botones
        welcome_message = (
            "¡Bienvenido al bot de descargas!\n\n"
            "Aquí puedes descargar y subir archivos de manera gratuita.\n\n"
        )
        # Enviar el mensaje con los botones
        await message.reply_text(welcome_message)   
    elif '/wget' in mss:
        try:
            list = message.text.split(" ")[1]
            await add_to_queue(client, message, username, message.reply)
        except Exception as e:
            await bot.send_message(username, e)
        
    elif message.text.startswith('/dl'):
        cancel_uploads[user_id] = False
        try:
            i = int(message.text.split(" ")[1])
            msgh = files_formatter(str(root[username]["actual_root"]),username)
            path = str(root[username]["actual_root"]+"/")+msgh[1][i]
            start_time = time() # Guarda el tiempo de inicio
            msg = await message.reply_text("Iniciando subida...")  # Envía un mensaje de inicio
            await client.send_document(
                username,
                document=path,
                caption=f"Archivo subido por {username}.",
                progress=progress_callback,  # Función callback para el progreso
                progress_args=(msg,start_time)  # Pasamos el mensaje y el tiempo de inicio
            )
            cancel_uploads[user_id] = False
            await msg.delete() # Elimina el mensaje de progreso
        except Exception as e:
            await message.reply_text(f"Error al descargar: {e}")
            return      
    elif message.text.startswith('/rm'):
        list = message.text.split(" ")[1]	
        msgh = files_formatter(str(root[username]["actual_root"]),username)
        try:
            unlink(str(root[username]["actual_root"])+"/"+msgh[1][int(list)])
            msg = files_formatter(str(root[username]["actual_root"])+"/",username)
            await limite_msg(msg[0],username)
        except Exception as ex:
            await bot.send_message(username,ex)
    
    elif message.text.startswith('/delete_all'):
        user_dir_path = Path(root[username]["actual_root"])
        try:
            shutil.rmtree(user_dir_path)
            root[username] = {"actual_root": f"downloads/{username}"} 
            Path(root[username]["actual_root"]).mkdir(parents=True, exist_ok=True)
            await message.reply(f"El directorio de descargas ha sido eliminado. \n\nAhora tienes {sizeof_fmt(0)} de uso")  # Notificar al usuario
        except Exception as e:
            await message.reply(f"Error al eliminar el directorio: {e}")



    elif "youtube.com" in mss:
        url = message.text # Obtener la URL del video de YouTube
        info = await obtener_info_video(url)
        if not info:
            await message.reply_text("No se pudo obtener la información del video.")
            return
        # Mostrar la información del video y los botones de calidad
        await mostrar_info_video(client, message, info, url)

    elif "www.instagram.com" in mss:
        ruta_descarga = root[username]["actual_root"]
        url = message.text
        msg = await bot.send_message(username, "Opteniendo Informacion del Video")
        await descargar_video_url(url, msg, ruta_descarga)
        
    elif "www.facebook.com" in mss:
        ruta_descarga = root[username]["actual_root"]
        url = message.text
        msg = await bot.send_message(username, "Opteniendo Informacion del Video")
        await descargar_video_url(url, msg, ruta_descarga)
        
    elif 'www.xvideos.com' in mss:
        ruta_descarga = root[username]["actual_root"]
        url = message.text
        msg = await bot.send_message(username, "Opteniendo Informacion del Video")
        await descargar_video_url(url, msg, ruta_descarga)
        
    elif "/help" in mss:
        help_message = """
        **📚 Guía Completa del Bot 🤖**

        Para ver una explicación detallada de todos los comandos y funcionalidades del bot, visita la siguiente página:

        ¡Gracias por usar nuestro bot! 🤖
        """

    # Crear el botón con la URL
        keyboard = InlineKeyboardMarkup(
            [
            [InlineKeyboardButton("📖 Ver Guía Completa", url="https://telegra.ph/Gu%C3%ADa-Completa-del-Bot-02-25")]
            ]
        )

    # Enviar el mensaje con el botón
        await bot.send_message(
            username,
            help_message,
            reply_markup=keyboard,
            disable_web_page_preview=False
        )
        
    elif '/cd' in mss:
        list = message.text.split(" ")[1]
        filespath = Path(str(root[username]["actual_root"]) + "/")
        msgh = files_formatter(str(root[username]["actual_root"]), username)
        path_to_remove = str(root[username]["actual_root"]) + "/" + msgh[1][int(list)]
        try:
            if os.path.isdir(path_to_remove):
                root[username]["actual_root"] = path_to_remove
                msg = f"Has cambiado a la carpeta: {path_to_remove}"
                await bot.send_message(username, msg)
                msg = files_formatter(str(root[username]["actual_root"]) + "/", username)
                await limite_msg(msg[0], username)
            else:
                await bot.send_message(username, "El directorio especificado no existe.")
        except Exception as ex:
            await bot.send_message(username, str(ex))

    elif '/back' in mss:
        root[username] = {"actual_root": f"downloads/{username}"}
        msg = files_formatter(str(root[username]["actual_root"]) + "/", username)
        await limite_msg(msg[0], username)

              
    elif '/move' in mss:
        try:
            list = message.text.split(" ")[1]
            des = message.text.split(" ")[2]  # Suponiendo que la carpeta de destino está en el mensaje
        except:
            await bot.send_message(username, f"**La forma correcta de utilizar el comando es /move archivo carpeta (sus numeros correspondientes)**")
            return
        filespath = Path(str(root[username]["actual_root"]) + "/")
        msgh = files_formatter(str(root[username]["actual_root"]), username)

        try:
            path_to_move = str(root[username]["actual_root"]) + "/" + msgh[1][int(list)]
            destination_path = str(root[username]["actual_root"]) + "/" + msgh[1][int(des)]

        # Verificar si el archivo existe
            if not os.path.isfile(path_to_move):
                await bot.send_message(username, "El archivo especificado no existe.")
                return

        # Verificar si la carpeta de destino existe, si no, crearla
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)

        # Mover el archivo
            shutil.move(path_to_move, destination_path)
            await bot.send_message(username, f"El archivo ha sido movido a {destination_path}")
        
        except Exception as ex:
            await bot.send_message(username, str(ex))
            
    elif '/rdir' in mss:
        list = message.text.split("_")[1]
        filespath = Path(str(root[username]["actual_root"]) + "/")
        msgh = files_formatter(str(root[username]["actual_root"]), username)
    
        try:
            path_to_remove = str(root[username]["actual_root"]) + "/" + msgh[1][int(list)]
        
            if os.path.isdir(path_to_remove):
                shutil.rmtree(path_to_remove)
                msg = files_formatter(str(root[username]["actual_root"]) + "/", username)
                await limite_msg(msg[0], username)
            else:
                await bot.send_message(username, "La ruta especificada no es un directorio.")
        except Exception as ex:
            await bot.send_message(username, str(ex))
            
    elif '/mkdir' in mss:
        name = message.text.split(" ")[1]
        if "." in name or "/" in name or "*" in name:
            await bot.send_message(username,"**El nombre no puede contener Caracteres Especiales**")
            return
        rut = root[username]["actual_root"]
        try:
            os.mkdir(f"{rut}/{name}")
        except Exception as a:
            await bot.send_message(username, a)
        await bot.send_message(username, f"**Carpeta Creada**\n\n`/{name}`")
        msg = files_formatter(str(root[username]["actual_root"]),username)
        await limite_msg(msg[0],username)
        
    elif "/split" in mss:
        try:
            i = int(message.text.split(" ")[1])
            zips = int(message.text.split(" ")[2])
        except Exception as e:
            await bot.send_message(username, e)
        msgh = files_formatter(str(root[username]["actual_root"]), username)
        path = str(root[username]["actual_root"] + "/") + msgh[1][i]
        # Verifica si la ruta es un archivo o un directorio
        if os.path.isfile(path):
            filesize = Path(path).stat().st_size
        elif os.path.isdir(path):
            total_size = sum(os.path.getsize(os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
            filesize = total_size
            print("")
            output_name = os.path.basename(path)
            with zipfile.ZipFile(output_name + ".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root_folder, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root_folder, file)
                        arcname = os.path.relpath(file_path, path)  # Relativiza la ruta
                        zipf.write(file_path, arcname)
        else:
            await bot.send_message(username, "La ruta especificada no es un archivo ni un directorio.")
            return

        zipssize = 1024 * 1024 * int(zips)
        msg = await bot.send_message(username, "Comprimiendo")
        # Llama a la función sevenzip, asegurándote de que pueda manejar grupos de archivos
        files = sevenzip(path, volume=zipssize)
        await msg.edit("Archivo o carpeta comprimido")
        return
      
    elif message.text.startswith('/zip'):
        msg = await bot.send_message(username, 'Por Favor espere')
        args = message.text.split()
        if len(args) < 2:
            await msg.edit("Por favor, proporciona los datos.")
            return
        conn = await create_db_connection()
        a = str(message.text.split(" ")[1])
        async with conn.cursor() as cursor:
                        await cursor.execute('SELECT additional_info FROM usuarios WHERE user_id = %s', (user_id,))
                        user_data = await cursor.fetchone()
                        if user_data:
                            additional_info = json.loads(user_data[0])
                            additional_info['zips'] = float(a)
                            updated_info = json.dumps(additional_info)

                            await cursor.execute('UPDATE usuarios SET additional_info = %s WHERE user_id = %s',
                                         (updated_info, user_id))
                            await conn.commit()
        
        await msg.edit(f"**Tamaño de zips establecido en {a} **")
    
    elif message.text.startswith('/proxy'):
        msg = await bot.send_message(username, 'Por Favor espere')
        conn = await create_db_connection()
        args = message.text.split()
        if len(args) < 2:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT additional_info FROM usuarios WHERE user_id = %s', (user_id,))
                user_data = await cursor.fetchone()
                if user_data:
                    additional_info = json.loads(user_data[0])
                    additional_info['proxy'] = ''
                    updated_info = json.dumps(additional_info)
                    await cursor.execute('UPDATE usuarios SET additional_info = %s WHERE user_id = %s',
                                 (updated_info, user_id))
                    await conn.commit()
                    await msg.edit(f"**Proxy Default**")
            return
        
        a = str(message.text.split(" ")[1])
        async with conn.cursor() as cursor:
                        await cursor.execute('SELECT additional_info FROM usuarios WHERE user_id = %s', (user_id,))
                        user_data = await cursor.fetchone()
                        if user_data:
                            additional_info = json.loads(user_data[0])
                            additional_info['proxy'] = a
                            updated_info = json.dumps(additional_info)

                            await cursor.execute('UPDATE usuarios SET additional_info = %s WHERE user_id = %s',
                                         (updated_info, user_id))
                            await conn.commit()
        
        await msg.edit(f"Proxy establecido:** {a} **")
        
        
    elif message.text.startswith('/data'):
        if username != 'Stvz20' and username != 'JAGB2021':
            msg = await bot.send_message(username, 'No puedes usar este comando')
            return
        else:pass
        msg = await bot.send_message(username, 'Por Favor espere')
        args = message.text.split()
        try:
            a = str(message.text.split(" ")[1])
            b = str(message.text.split(" ")[2])
            c = str(message.text.split(" ")[3])
            d  = 299577
            e  = int(message.text.split(" ")[4])
        except Exception as e:
            await msg.edit(f"**La forma correca es host user pasw id id**")    
        conn = await create_db_connection()
        async with conn.cursor() as cursor:
                        await cursor.execute('SELECT additional_info FROM usuarios WHERE user_id = %s', (user_id,))
                        user_data = await cursor.fetchone()
                        if user_data:
                            additional_info = json.loads(user_data[0])
                            additional_info['host'] = a
                            additional_info['userp'] = b
                            additional_info['pasw'] = c
                            additional_info['idsub'] = d
                            additional_info['art'] = e
                            updated_info = json.dumps(additional_info)

                            await cursor.execute('UPDATE usuarios SET additional_info = %s WHERE user_id = %s',
                                         (updated_info, user_id))
                            await conn.commit()
        
        await msg.edit(f"**Datos Guardados✅\n\nhost: {a}\nUser: {b}\nPasw:{c}\nID Art: {e}**")

    elif message.text.startswith('/set_data'):
        try:
            args = message.text.split(" ")
            if len(args) < 6:
                await message.reply("Uso correcto: `/setdata host user pasw id_art cookie`")
                return
        
            GLOBAL_DATA["host"] = args[1]
            GLOBAL_DATA["user"] = args[2]
            GLOBAL_DATA["pasw"] = args[3]
            GLOBAL_DATA["id_art"] = args[4]
            GLOBAL_DATA["cookie"] = args[5]

            await message.reply("✅ Datos globales actualizados correctamente.")
        except Exception as e:
            await message.reply(f"Error: {str(e)}")

        
    elif message.text.startswith('/ls'):
        msg = files_formatter(str(root[username]["actual_root"]), username)
        await limite_msg(msg[0], username)
        
        
    elif message.text.startswith('/usuarios'):
        msg = await bot.send_message(username, 'Por Favor espere')
        conn = await create_db_connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT username FROM usuarios')
                users = await cursor.fetchall()
                if users:
                    user_list = "\n".join(user[0] for user in users)
                    await msg.edit(f"Usuarios registrados:\n{user_list}")
                else:
                    await message.reply_text("No hay usuarios registrados.")
        finally:
            conn.close()

    elif "/files_del" in mss:
        usid = user_id
        msg = await bot.send_message(username, "Por Favor Espere⏳...")
        await deletecloud(bot, usid, msg, username)
    elif '/up' in mss:
        id_path[username] = {"id": "", "user_id": ""}
        try:
            msg = await bot.send_message(username, "Por Favor Espere⏳...")
            range_str = message.text.split(" ")[1]
            range_parts = range_str.split("-")
            start = int(range_parts[0])
        except Exception as e:
            await msg.edit(e)
        usid = user_id    
        try:
            end = int(range_parts[1])
        except:
            end = start
        msgh = files_formatter(str(root[username]["actual_root"]), username)
        selected_files = []
    
        for i in range(start, end + 1):
            path = str(root[username]["actual_root"] + "/") + msgh[1][i]    
            selected_files.append(path)
            size = os.path.getsize(path)/(1024 * 1024)
       
        if len(selected_files) == 0:
            await msg.edit(" No se encontraron archivos en el rango especificado.**\nTenga en cuenta que el comando se usa:\n/up_#nombre_del_archivo para un archivo simple\nPor rango /up_#archivo1-#archivo2 ej: /up_0-5 ahí se subirán los archivos del 0 al 5 del servidor a la nube.")
            return
        elif len(selected_files) == 1:
            file_name = os.path.basename(selected_files[0])
            await msg.edit(f"**Archivo Seleccionado: {file_name}")
            id_path[username] = {"id": selected_files, "user_id": user_id}
            path = selected_files[0]
            await upload_rev(bot, path,usid,msg,username)
            await msg.delete()
            return 
        else:
            await msg.edit(f"**Archivos Seleccionados: {len(selected_files)}")
            id_path[username] = {"id": selected_files, "user_id": user_id}
            for path in selected_files:
                await upload_rev(bot, path,usid,msg,username)
            await msg.delete()
            return
            
          
class Progress(BufferedReader):
    def __init__(self, filename, read_callback):
        f = open(filename, "rb")
        self.filename = Path(filename).name
        self.__read_callback = read_callback
        super().__init__(raw=f)
        self.start = time()
        self.length = Path(filename).stat().st_size

    def read(self, size=None):
        calc_sz = size
        if not calc_sz:
            calc_sz = self.length - self.tell()
        self.__read_callback(self.tell(), self.length,self.start,self.filename)
        return super(Progress, self).read(size)
              
    
def uploadfile_progres(chunk, filesize, start, filename, message):
    global seg # Se necesita la global para modificarla
    now = time()
    diff = now - start
    mbs = chunk / diff
    
    # Calculamos el porcentaje de progreso para la barra
    percentage = (chunk / filesize) * 100
    
    # Calculamos el tiempo restante (ETA)
    elapsed_time = now - start
    if mbs > 0:
        remaining_bytes = filesize - chunk
        eta_seconds = remaining_bytes / mbs
        eta_minutes = int(eta_seconds / 60)
        eta_seconds = int(eta_seconds % 60)
        eta_hours = int(eta_minutes / 60)
        eta_minutes = int(eta_minutes % 60)
        eta_formatted = f"{eta_hours:02}:{eta_minutes:02}:{eta_seconds:02}"
    else:
        eta_formatted = "Unknown"
    
    # Construimos el mensaje con el formato deseado
    msg = "Task is being Processed!\n"
    msg += f"┠ File: {filename}\n"
    msg += f"┃ {update_progress_bar(chunk, filesize, 15)}\n"
    msg += f"┠ Processed: {sizeof_fmt(chunk)} of {sizeof_fmt(filesize)}\n"
    msg += f"┖ Speed: {sizeof_fmt(mbs)}/s | ETA: {eta_formatted}\n"
    msg += f"┠ Status: #TelegramUploadCloud"
    
    if seg != localtime().tm_sec: 
        message.edit(msg)
    seg = localtime().tm_sec
    
def sevenzip(fpath: Path, password: str = None, volume = None):
    filters = [{"id": FILTER_COPY}]
    fpath = Path(fpath)
    fsize = fpath.stat().st_size
    if not volume:
        volume = fsize + 1024
    ext_digits = len(str(fsize // volume + 1))
    if ext_digits < 3:
        ext_digits = 3
    with MultiVolume(
        fpath.with_name(fpath.name+".7z"), mode="wb", volume=volume, ext_digits=ext_digits
    ) as archive:
        with SevenZipFile(archive, "w", filters=filters, password=password) as archive_writer:
            if password:
                archive_writer.set_encoded_header_mode(True)
                archive_writer.set_encrypted_header(True)
            archive_writer.write(fpath, fpath.name)
    files = []
    for file in archive._files:
        files.append(file.name)
    return files


# --- Funciones de Descarga ---
def get_downloadable_info(url):
    print(f"Parsing video URL from {url}")
    urls = []
    try:
        req = request.Request(url)
        r = request.urlopen(req)
        for line in r.read().decode(r.headers.get_content_charset()).splitlines():
            if "html5player.setVideoUrl" in line:
                urls.append(line)
    except Exception as e:
        print(f"Error al obtener la URL: {e}")
        return None
    return urls

def download_progresss(block_num, block_size, total_size, message):
    downloaded = block_num * block_size
    percentage = min((downloaded / total_size) * 100, 100)
    if percentage % 1 == 0:  # Solo actualizar cada 5%
        try:
            message.edit_text(f"Descargando video... {percentage:.2f}% completo")
        except Exception as e:
            print(f"No se pudo editar el mensaje: {e}")

def download_videos(urls, download_folder, message):
    if not urls:
        return None

    url = urls[0] if "setVideoUrlHigh" in urls[0] else urls[1]
    url = url.split("'")[1]
    file_name = urlparse(url).path.split("/")[-1]
    if not download_folder.endswith("/"):
        download_folder += "/"
    download_dest = download_folder + file_name

    try:
        print(f"Downloading at {download_dest}")
        total_size = int(request.urlopen(url).info().get("Content-Length", -1))
        print(total_size)
        if total_size == -1:
            raise ValueError("No se pudo obtener el tamaño del archivo.")

        request.urlretrieve(url, download_dest, lambda blocks, block_size, total_size: download_progress(blocks, block_size, total_size, message))

        return download_dest
    except Exception as e:
        print(f"Error al descargar el video: {e}")
        return None

def handle_download(url, download_folder, message):
    return download_videos(get_downloadable_info(url), download_folder, message)

# --- Funciones de Pyrogram ---
async def download_and_send(client, message, url, path):
    try:
        # Enviar el mensaje de inicio de descarga
        progress_message = await message.reply_text("Descargando video...")
        download_path = await asyncio.get_running_loop().run_in_executor(None, handle_download, url, path, progress_message)

        if download_path:
            await message.reply_text("¡Video descargado!")
            await progress_message.delete()  # Opcional: eliminar el mensaje de progreso
        else:
            await message.reply_text("Hubo un error al descargar el video.")
            await progress_message.delete()  # Opcional: eliminar el mensaje de progreso
    except Exception as e:
        print(e)
        await message.reply_text(e)

bot.add_handler(CallbackQueryHandler(handle_callback_query))
bot.start()  
bot.send_message(1742433244,'**BoT Iniciado preiona /start y disfruta de tu estadia**')
print("Bot  Iniciado")
bot.loop.run_forever()
