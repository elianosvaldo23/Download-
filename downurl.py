import yt_dlp
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
    
    return nombre.strip()

async def descargar_video_url(url, msg, ruta_descarga):
    # Opciones para yt-dlp
    ydl_opts = {
        'format': 'best',  # Descargar el mejor formato disponible
        'outtmpl': os.path.join(ruta_descarga, f'%(title)s.%(ext)s'),  # Nombre del archivo de salida
        'quiet': False,  # Mostrar información en la consola
        'no_warnings': False,  # Mostrar advertencias
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Descargar el video
            ydl.download([url])
            await msg.edit("Descarga completada!")
        except Exception as e:
            await msg.edit(f"Error al descargar el video: {e}")
