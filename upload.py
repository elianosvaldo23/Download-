import zipfile
import os
import struct
import chardet
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


from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


seg = 0
downlist = {}  # lista de archivos descargados
root = {}  # directorio actual
id_path = {}
seg = 0
cancel_uploads = {}
cancel_upload = {}

GLOBAL_DATA = {
    "host": "http://medisur.sld.cu/index.php/medisur",
    "user": "hxtsoo",
    "pasw": "hxtsoo@telegmail.com",
    "id_art": "46052",
    "cookie": "OJSSID=a04294f60744823ed89d749feacada1d",
    "proxy": "",
    "zips": "7",
}

def update_progress_bar(chunk, filesize, bar_length=20):
    """Genera una barra de progreso visual."""
    percent = chunk / filesize
    filled_length = int(round(bar_length * percent))
    bar = '■' * filled_length + '□' * (bar_length - filled_length) + f" {percent:.2%}"
    return bar

def sevenzip(fpath: Path, password: str = None, volume=None):
    filters = [{"id": FILTER_COPY}]
    fpath = Path(fpath)
    fsize = fpath.stat().st_size
    if not volume:
        volume = fsize + 1024
    ext_digits = len(str(fsize // volume + 1))
    if ext_digits < 3:
        ext_digits = 3
    with MultiVolume(
        fpath.with_name(fpath.name + ".7z"), mode="wb", volume=volume, ext_digits=ext_digits
    ) as archive:
        with SevenZipFile(archive, "w", filters=filters, password=password) as archive_writer:
            if password:
                archive_writer.set_encoded_header_mode(True)
                archive_writer.set_encrypted_header(True)
            archive_writer.write(fpath, fpath.name)
    files = []
    for file in archive._files:
        files.append(file.name)
    print(files)
    return files

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
        self.__read_callback(self.tell(), self.length, self.start, self.filename)
        return super(Progress, self).read(size)

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.2f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.2f%s%s" % (num, 'Yi', suffix)

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
    
####################################################################################################### 
async def upload_rev(bot, path, usid, msg, username):
    user_id = usid
    file_size = os.path.getsize(path)
    cancel_uploads[usid] = False
    cancel_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancelar Subida ❌", callback_data=f"cancel_upload_{usid}")]
    ])
    msg = await bot.send_message(username, "📤 Iniciando subida...", reply_markup=cancel_button)

    host = GLOBAL_DATA["host"]
    user = GLOBAL_DATA["user"]
    pasw = GLOBAL_DATA["pasw"]
    art_id = GLOBAL_DATA["id_art"]
    cookie = GLOBAL_DATA["cookie"]
    proxy = GLOBAL_DATA["proxy"]
    zips = GLOBAL_DATA["zips"]

    if proxy == "":
        connector = None
    else:
        connector = ProxyConnector.from_url(proxy)

    if cookie == False:
        cookie, msg = await extraer_cookie(bot, usid, msg, username)
        GLOBAL_DATA["cookie"] = cookie

    namefileo = os.path.basename(path)
    namefile = os.path.basename(path)
    filesize = Path(path).stat().st_size
    zipssize = 1024 * 1024 * int(zips)
    size = os.path.getsize(path) / (1024 * 1024)
    size = round(size, 2)
    nombre_base = namefile
    name_file = nombre_base.split('.')[0]
    headers = {
        'Cookie': 'OJSSID=g5rjmij12so68g87addhbqaif7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'
    }
    if filesize - 1048 > zipssize:
        async with aiohttp.ClientSession(connector=connector) as session:
            payload = {
                'username': 'mslxm',
                'password': 'mslxm@telegmail.com'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            }
            await msg.edit(f"**Iniciando Sesion**")
            async with session.post("https://medisur.sld.cu/index.php/medisur/login/signIn", data=payload, headers=headers, ssl=False, allow_redirects=False) as response:
                response_text = await response.text()
                print(response.url)
                print(f"Login status: {response.status}")
                cookies = {cookie.key: cookie.value for cookie in session.cookie_jar}
                
            inic = time()
            parts = round(filesize / zipssize)
            file_name = os.path.basename(path)
            await msg.edit(f"**Comprimiendo 📂 {file_name}**")
            files = sevenzip(path, volume=zipssize)
            total_files = len(files)
            total_size = sum(os.path.getsize(file) for file in files)
            total_uploaded = 0
            url = "Enlaces"
            for i, file in enumerate(files):
                namefile = os.path.basename(file)
                try:
                    with open(file, 'rb') as archivo_original:
                        contenido_archivo = archivo_original.read()
                    png_header = b'\x89PNG\r\n\x1a\n'  # Firma PNG
                    ihdr_chunk = b'\x00\x00\x00\x0dIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
                    iend_chunk = b'\x00\x00\x00\x00IEND\xaeB`\x82'
                    contenido_imagen = png_header + ihdr_chunk + contenido_archivo + iend_chunk
                    with open(file+".png", 'wb') as archivo_imagen:
                        archivo_imagen.write(contenido_imagen)
                except Exception as e:
                    print(e)
                art_id = 52794
                fi = Progress(file+".png",lambda current,total,timestart,filename: uploadfile_progres(current,total,timestart,filename,msg))
                payload = aiohttp.FormData()
                payload.add_field('articleId', str(art_id))
                payload.add_field('upload', fi, filename=namefile+".png", content_type='application/octet-stream')
                payload.add_field('submit', 'Cargar')
                upload_url = f"http://medisur.sld.cu/index.php/medisur/author/uploadRevisedVersion"
                try:
                    async with session.post(upload_url, data=payload, headers=headers, ssl=False, cookies=cookies) as resp:
                        html = await resp.text()
               #     with open("html.html","w") as f:
                #        f.write(html)
                #    await bot.send_document(username, "html.html")
                    os.remove(file)
                except Exception as e:
                    await msg.edit(e)
                    
            async with session.get("http://medisur.sld.cu/index.php/medisur/author/submissionReview/52794", headers=headers, cookies=cookies, ssl=False) as dashboard_response:
                print(f"Dashboard status: {dashboard_response.status}")
                html = await dashboard_response.text()
                soup = BeautifulSoup(html, 'html.parser')
            link = ""
            for a_tag in soup.find_all('a', href=True):
                if 'http://medisur.sld.cu/index.php/medisur/author/downloadFile' in a_tag['href']:
                    url = str(a_tag['href'])
                    part = url.split('/')[-1]
                    if len(part) == 1:
                        part = '00' + part
                    elif len(part) == 2:
                        part = '0' + part
                    link += url+"/"+namefileo+f".7z.{part}.png\n"
                    print(a_tag['href'])
            with open(namefileo+".txt","w") as f:
                f.write(link)
            await bot.send_document(username, namefileo+".txt")
            await msg.delete()
                        

    else:
        file = path
        msg = await upload(bot, file ,usid, msg, username)
        #await bot.send_message(username, url)

async def uploaddd(bot, file ,usid, msg, username):
    connector = None
    namefile = os.path.basename(file)
    async with aiohttp.ClientSession(connector=connector) as session:
        await msg.edit(f"**Iniciando Subida de Archivo**")
        headers = {
            'Cookie': 'OJSSID=bec40b6bb431f29f5092d71ec3aed0cb',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        }
        try:
            with open(file, 'rb') as archivo_original:
                contenido_archivo = archivo_original.read()
            png_header = b'\x89PNG\r\n\x1a\n'  # Firma PNG
            ihdr_chunk = b'\x00\x00\x00\x0dIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            iend_chunk = b'\x00\x00\x00\x00IEND\xaeB`\x82'
            contenido_imagen = png_header + ihdr_chunk + contenido_archivo + iend_chunk
            with open(file+".png", 'wb') as archivo_imagen:
                archivo_imagen.write(contenido_imagen)
        except Exception as e:
            print(e)
        art_id = 52790
        fi = Progress(file+".png",lambda current,total,timestart,filename: uploadfile_progres(current,total,timestart,filename,msg))
        payload = aiohttp.FormData()
        payload.add_field('articleId', str(art_id))
        payload.add_field('formLocale', 'es_ES')
        payload.add_field('title[es_ES]', 'Sin título')
        payload.add_field('creator[es_ES]', '')  # Empty field
        payload.add_field('subject[es_ES]', '')  # Empty field
        payload.add_field('type', 'Instrumento de investigación')
        payload.add_field('typeOther[es_ES]', '')  # Empty field
        payload.add_field('description[es_ES]', '')  # Empty field
        payload.add_field('publisher[es_ES]', '')  # Empty field
        payload.add_field('sponsor[es_ES]', '')  # Empty field
        payload.add_field('dateCreated', '2025-01-23')
        payload.add_field('source[es_ES]', '')  # Empty field
        payload.add_field('language', '')  # Empty fieldateCreated"] = "2025-01-21"
        payload.add_field('uploadSuppFile', fi, filename=namefile+".png", content_type="application/octet-stream")
        upload_url = f"http://medisur.sld.cu/index.php/medisur/author/saveSubmitSuppFile/485429"
        try:
            async with session.post(upload_url, data=payload, headers=headers, ssl=False) as resp:
                html = await resp.text()
            with open("html.html","w") as f:
                f.write(html)
            await bot.send_document(username, "html.html")
            os.remove(file)
        except Exception as e:
            await msg.edit(e)
        try:
            url = ""
            payload = aiohttp.FormData()
            payload.add_field('articleId', str(art_id))
            async with session.get(f"http://medisur.sld.cu/index.php/medisur/author/submit/5?articleId={art_id}", data=payload, headers=headers, ssl=False) as response:
                cookies = response.cookies
                for key, cookie in cookies.items():
                    print(f'Cookie: {key} = {cookie.value}')
                    url = f'{key}={cookie.value}'
                raw_content = await response.read()
                detected_encoding = chardet.detect(raw_content)
                encoding = detected_encoding['encoding']
                html = raw_content.decode(encoding)
            soup = BeautifulSoup(html, 'html.parser')
            filename = namefile
            print(filename)
            files = soup.find_all('a', class_='file')
            for link in files:
                if link and link.has_attr('href') and link.text:
                    if re.search(namefile, link.text, re.IGNORECASE):
                        filename = link.text.strip()
                        download_url = link['href']
                        resultado = re.search(r'author/download/(\d+)/(\d+)', download_url)
                        print(resultado)
                        nuevo_enlace = f"{resultado.group(1)}/{resultado.group(2)}"
                        if filename in url:pass
                        else:
                            url += "\n"+nuevo_enlace+"/"+filename
                            
        except Exception as e:
            await msg.edit(e)
            return
        await msg.delete()
        return msg, url

async def upload(bot, file ,usid, msg, username):
    connector = None
    namefile = os.path.basename(file)
    payload = {
        'username': 'mslxm',
        'password': 'mslxm@telegmail.com'
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8,gl;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'medisur.sld.cu',
        'Origin': 'http://medisur.sld.cu',
        'Referer': 'http://medisur.sld.cu/',
        'Sec-CH-UA': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    async with aiohttp.ClientSession(connector=connector) as session:
        await msg.edit(f"**Iniciando Sesion**")
        async with session.post("https://medisur.sld.cu/index.php/medisur/login/signIn", data=payload, headers=headers, ssl=False, allow_redirects=False) as response:
            response_text = await response.text()
            print(response.url)
            print(f"Login status: {response.status}")
            cookies = {cookie.key: cookie.value for cookie in session.cookie_jar}
        
        headers = {
            'Cookie': 'OJSSID=95e3eb70895fc9c071d119b031455258',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        }
        try:
            with open(file, 'rb') as archivo_original:
                contenido_archivo = archivo_original.read()
            png_header = b'\x89PNG\r\n\x1a\n'  # Firma PNG
            ihdr_chunk = b'\x00\x00\x00\x0dIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            iend_chunk = b'\x00\x00\x00\x00IEND\xaeB`\x82'
            contenido_imagen = png_header + ihdr_chunk + contenido_archivo + iend_chunk
            with open(file+".png", 'wb') as archivo_imagen:
                archivo_imagen.write(contenido_imagen)
        except Exception as e:
            print(e)
        art_id = 52794
        fi = Progress(file+".png",lambda current,total,timestart,filename: uploadfile_progres(current,total,timestart,filename,msg))
        payload = aiohttp.FormData()
        payload.add_field('articleId', str(art_id))
        payload.add_field('upload', fi, filename=namefile+".png", content_type='application/octet-stream')
        payload.add_field('submit', 'Cargar')
        upload_url = f"http://medisur.sld.cu/index.php/medisur/author/uploadRevisedVersion"
        try:
            async with session.post(upload_url, data=payload, headers=headers, ssl=False, cookies=cookies) as resp:
                html = await resp.text()
          #  with open("html.html","w") as f:
           #     f.write(html)
            #await bot.send_document(username, "html.html")
            os.remove(file)
        except Exception as e:
            await msg.edit(e)
        
        async with session.get("http://medisur.sld.cu/index.php/medisur/author/submissionReview/52794", headers=headers, cookies=cookies, ssl=False) as dashboard_response:
            print(f"Dashboard status: {dashboard_response.status}")
            html = await dashboard_response.text()
        soup = BeautifulSoup(html, 'html.parser')
        link = ""
        for a_tag in soup.find_all('a', href=True):
            if 'http://medisur.sld.cu/index.php/medisur/author/downloadFile' in a_tag['href']:
                url = str(a_tag['href'])
                part = url.split('/')[-1]
                if len(part) == 1:
                    part = '00' + part
                elif len(part) == 2:
                    part = '0' + part
                link += url+"/"+namefile+".png"
                print(a_tag['href'])
        with open(namefile+".txt","w") as f:
            f.write(link)
        await bot.send_document(username, namefile+".txt") 
        await msg.delete()
        return


async def deletecloud(bot, usid, msg, username):
    connector = None
  #  namefile = os.path.basename(file)
    payload = {
        'username': 'mslxm',
        'password': 'mslxm@telegmail.com'
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8,gl;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'medisur.sld.cu',
        'Origin': 'http://medisur.sld.cu',
        'Referer': 'http://medisur.sld.cu/',
        'Sec-CH-UA': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    async with aiohttp.ClientSession(connector=connector) as session:
        await msg.edit(f"**Iniciando Sesion**")
        async with session.post("https://medisur.sld.cu/index.php/medisur/login/signIn", data=payload, headers=headers, ssl=False, allow_redirects=False) as response:
            response_text = await response.text()
            print(response.url)
            print(f"Login status: {response.status}")
            cookies = {cookie.key: cookie.value for cookie in session.cookie_jar}
        
        headers = {
            'Cookie': 'OJSSID=95e3eb70895fc9c071d119b031455258',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        }
        async with session.get("http://medisur.sld.cu/index.php/medisur/author/submissionReview/52794", headers=headers, cookies=cookies, ssl=False) as dashboard_response:
            print(f"Dashboard status: {dashboard_response.status}")
            html = await dashboard_response.text()
        soup = BeautifulSoup(html, 'html.parser')
      #  links = []
        for a_tag in soup.find_all('a', href=True):
            if 'http://medisur.sld.cu/index.php/medisur/author/deleteArticleFile' in a_tag['href']:
             #   links.append(a_tag['href'])
                print(a_tag['href'])
                url = str(a_tag['href'])
                part = url.split('/')[-1]
                await msg.edit(f"**Eliminando Archivos: {part}**")
                async with session.get(a_tag['href'], headers=headers, cookies=cookies, ssl=False) as dashboard_response:
                    print(f"Dashboard status: {dashboard_response.status}")
        await msg.edit(f"**Todos Los Archivos han sido eliminados**")
        
