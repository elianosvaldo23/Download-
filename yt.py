from yt_dlp import YoutubeDL
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from pathlib import Path

# Función para obtener la información del video y generar el mensaje
async def obtener_info_video(url):
    opciones = {
        'format': 'best',  # Solo para obtener información
        'quiet': True,      # Evitar salida innecesaria
        'cookiefile': 'cokie.txt',
    }
    with YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)

        # Extraer información relevante
        titulo = info.get('title', 'Sin título')
        duracion = info.get('duration', 0)
        autor = info.get('uploader', 'Desconocido')
        vistas = info.get('view_count', 0)
        thumbnail = info.get('thumbnail', '')  # URL de la miniatura

        # Obtener calidades disponibles
        formatos = info.get('formats', [])
        calidades_disponibles = {}
        for formato in formatos:
            if formato.get('height'):
                calidad = f"{formato['height']}p"
                if calidad in ['144p', '240p', '360p', '720p', '1080p']:
                    tamaño = formato.get('filesize') or formato.get('filesize_approx')
                    if tamaño:
                        tamaño_mb = round(tamaño / (1024 * 1024), 2)
                        calidades_disponibles[calidad] = f"{calidad} {tamaño_mb}MB"

        # Añadir opción de audio
        for formato in formatos:
            if formato.get('acodec') != 'none' and formato.get('vcodec') == 'none':
                tamaño = formato.get('filesize') or formato.get('filesize_approx')
                if tamaño:
                    tamaño_mb = round(tamaño / (1024 * 1024), 2)
                    calidades_disponibles['mp3'] = f"Audio {tamaño_mb}MB"
                break

        return {
            'titulo': titulo,
            'duracion': duracion,
            'autor': autor,
            'vistas': vistas,
            'thumbnail': thumbnail,
            'calidades': calidades_disponibles,
        }

# Función para mostrar el mensaje con la información del video
async def mostrar_info_video(client, message, info, url):
    # Crear botones para seleccionar la calidad
    botones = []
    for calidad, texto in info['calidades'].items():
        botones.append([InlineKeyboardButton(texto, callback_data=f"yt_{calidad}_{url}")])

    teclado = InlineKeyboardMarkup(botones)

    # Crear el mensaje con la información del video
    mensaje = (
        f"**🎥 Título:** {info['titulo']}\n"
        f"**⏳ Duración:** {info['duracion']} segundos\n"
        f"**👤 Autor:** {info['autor']}\n"
        f"**👀 Vistas:** {info['vistas']}\n\n"
        "Selecciona la calidad de descarga:"
    )

    # Enviar el mensaje con la miniatura y los botones
    await client.send_photo(
        chat_id=message.chat.id,
        photo=info['thumbnail'],
        caption=mensaje,
        reply_markup=teclado,
    )

# Función para mostrar el progreso de la descarga
async def progreso_descarga(d, msg):
    if d['status'] == 'downloading':
        porcentaje = d['_percent_str']
        velocidad = d['_speed_str']
        eta = d['_eta_str']
        progreso_texto = (
            f"**Descargando...**\n"
            f"**Progreso:** {porcentaje}\n"
            f"**Velocidad:** {velocidad}\n"
            f"**ETA:** {eta}"
        )
        try:
            await msg.edit_text(progreso_texto)
        except Exception as e:
            await msg.edit_text(f"No se pudo actualizar el mensaje de progreso: {e}")


import os
import re
import unicodedata

# Función para limpiar el nombre del archivo
def limpiar_nombre(nombre):
    # Normalizar tildes y caracteres especiales
    nombre = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('ASCII')
    
    # Eliminar caracteres especiales (excepto letras, números, espacios y guiones)
    nombre = re.sub(r'[^\w\s.-]', '', nombre)
    
    # Reemplazar espacios en blanco por guiones
    nombre = nombre.replace(' ', '-')
    
    # Convertir a minúsculas (opcional)
    nombre = nombre.lower()
    
    return nombre

# Función para descargar el video en la calidad seleccionada
async def descargar_video_youtube(url, ruta_descarga, message, calidad):
    try:
        msg = await message.reply_text(f"**Por Favor Espere**")
        
        # Obtener información del video sin descargarlo
        with YoutubeDL({'cookiefile': 'cokie.txt'}) as ydl:
            info = ydl.extract_info(url, download=False)
            titulo = info['title']
            duracion = info['duration']
            autor = info['uploader']
            vistas = info['view_count']

            # Limpiar el título del video
            titulo_limpio = limpiar_nombre(titulo)

            # Configurar opciones de descarga
            opciones = {
                'outtmpl': os.path.join(ruta_descarga, f'{titulo_limpio}.%(ext)s'),
                'progress_hooks': [lambda d: progreso_descarga(d, msg)],
                'cookiefile': 'cokie.txt',  # Asegúrate de tener las cookies
                'merge_output_format': 'mp4',
            }

            # Seleccionar formato según la calidad
            if calidad == 'mp3':
                opciones['format'] = 'bestaudio/best'
                opciones['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                opciones['format'] = f'bestvideo[height<={calidad[:-1]}]+bestaudio/best[height<={calidad[:-1]}]'

            # Enviar información del video al usuario
            await msg.edit_text(
                f"**Título:** {titulo}\n"
                f"**Duración:** {duracion} segundos\n"
                f"**Autor:** {autor}\n"
                f"**Vistas:** {vistas}\n\n"
                f"**Descargando en {calidad}...**"
            )

            # Descargar el video
            with YoutubeDL(opciones) as ydl:
                ydl.download([url])

        await msg.edit_text(f"¡Descarga completada en {calidad}!")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
