import os
import numpy as np
from PIL import Image
from midvoxio.voxio import vox_to_arr

def extraer_caras_vox(input_vox, carpeta_salida, nombre_base, model_index=0):
    """
    Extrae las 6 caras de un modelo MagicaVoxel y las guarda en una carpeta. El archivo tiene que estar en la misma carpeta del código.
    """
    vox_array = vox_to_arr(input_vox, model_index)
    size_x, size_y, size_z, _ = vox_array.shape
    
    caras = ['front', 'back', 'left', 'right', 'top', 'bottom']
    
    for cara in caras:
        # 1. Configurar el tamaño del lienzo
        if cara in ['front', 'back']:
            img = Image.new('RGBA', (size_x, size_z), (0, 0, 0, 0))
        elif cara in ['left', 'right']:
            img = Image.new('RGBA', (size_y, size_z), (0, 0, 0, 0))
        else: # top, bottom
            img = Image.new('RGBA', (size_x, size_y), (0, 0, 0, 0))
            
        pixels = img.load()

        # 2. Mapear coordenadas y escanear píxeles
        for img_x in range(img.width):
            for img_y in range(img.height):
                
                if cara == 'front':
                    x, z = img_x, (size_z - 1) - img_y
                    rango_profundidad = range(size_y)
                elif cara == 'back':
                    x, z = (size_x - 1) - img_x, (size_z - 1) - img_y
                    rango_profundidad = range(size_y - 1, -1, -1)
                elif cara == 'left':
                    y, z = img_x, (size_z - 1) - img_y
                    rango_profundidad = range(size_x)
                elif cara == 'right':
                    y, z = (size_y - 1) - img_x, (size_z - 1) - img_y
                    rango_profundidad = range(size_x - 1, -1, -1)
                elif cara == 'top':
                    x, y = img_x, (size_y - 1) - img_y
                    rango_profundidad = range(size_z - 1, -1, -1)
                elif cara == 'bottom':
                    x, y = img_x, img_y
                    rango_profundidad = range(size_z)

                # 3. Buscamos el primer voxel visible
                for d in rango_profundidad:
                    if cara in ['front', 'back']:
                        voxel = vox_array[x, d, z]
                    elif cara in ['left', 'right']:
                        voxel = vox_array[d, y, z]
                    else:
                        voxel = vox_array[x, y, d]

                    if voxel[3] > 0:
                        if max(voxel) <= 1.0:
                            color = tuple(int(round(c * 255)) for c in voxel)
                        else:
                            color = tuple(int(c) for c in voxel)
                            
                        pixels[img_x, img_y] = color
                        break 

        # 4. Guarda la imagen en la carpeta creada
        nombre_archivo = f"{nombre_base}_{cara}.png"
        ruta_salida = os.path.join(carpeta_salida, nombre_archivo)
        img.save(ruta_salida)
        print(f"  -> Exportado: {ruta_salida}")

# --- Ejecución ---
if __name__ == "__main__":
    archivo_entrada = input("Introduce el nombre del archivo .vox (ejemplo: mi_modelo.vox): ")
    
    if not os.path.exists(archivo_entrada):
        print(f"Error: No se encontró el archivo :( '{archivo_entrada}'.") # Por alguna razón el código se rompe una que otra vez aquí
    else:
        nombre_base = archivo_entrada.lower().replace('.vox', '')
        carpeta_salida = f"{nombre_base}_export"
        
        # Crear la carpeta contenedora si no existe
        os.makedirs(carpeta_salida, exist_ok=True)
        print(f"\nCarpeta destino: ./{carpeta_salida}/")
        
        print(f"Procesando {archivo_entrada}...")
        for i in range(4): 
            try:
                _ = vox_to_arr(archivo_entrada, i) 
                print(f"\nObjeto {i}:")
                extraer_caras_vox(archivo_entrada, carpeta_salida, f"{nombre_base}_obj{i}", model_index=i)
            except IndexError:
                break 
        
        print("\n¡Epa!")