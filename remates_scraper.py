import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import time

class RematesScraper:
    def __init__(self):
        self.base_url = "https://preremates.cl/content/proximos-remates?page=all"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def obtener_contenido_web(self):
        """Obtiene el contenido HTML de la página de remates"""
        try:
            print("Obteniendo datos de preremates.cl...")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener el contenido web: {e}")
            return None
            
    def extraer_fecha_hora(self, texto_remate):
        """Extrae fecha y hora del texto del remate"""
        # Patrones de fecha comunes en el sitio
        patrones_fecha = [
            r'(\w+)\s+(\d{1,2})\s+(\w+)\s+(\d{4}),\s+(\d{1,2}):(\d{2})',  # Martes 24 jun 2025, 14:30
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\s+a\s+las\s+(\d{1,2}):(\d{2})',  # 24 de junio de 2025 a las 14:30
        ]
        
        meses = {
            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
            'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
            'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
            'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
        }
        
        for patron in patrones_fecha:
            match = re.search(patron, texto_remate, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 6:  # Primer patrón
                    dia = groups[1].zfill(2)
                    mes = meses.get(groups[2].lower(), '01')
                    año = groups[3]
                    hora = f"{groups[4].zfill(2)}:{groups[5]}"
                    fecha = f"{año}-{mes}-{dia}"
                    return fecha, hora
                elif len(groups) == 5:  # Segundo patrón
                    dia = groups[0].zfill(2)
                    mes = meses.get(groups[1].lower(), '01')
                    año = groups[2]
                    hora = f"{groups[3].zfill(2)}:{groups[4]}"
                    fecha = f"{año}-{mes}-{dia}"
                    return fecha, hora
        
        return None, None
    
    def extraer_juzgado(self, texto_remate):
        """Extrae información del juzgado"""
        patrones_juzgado = [
            r'Remate[:\s]*([^,]+Juzgado[^,]+)',
            r'([^,]*Juzgado[^,]*)',
            r'Tribunal[:\s]*([^,]+)',
        ]
        
        for patron in patrones_juzgado:
            match = re.search(patron, texto_remate, re.IGNORECASE)
            if match:
                juzgado = match.group(1).strip()
                # Limpiar texto innecesario
                juzgado = re.sub(r'^(Remate[:\s]*|Se\s+rematará[^,]*,?\s*)', '', juzgado, flags=re.IGNORECASE)
                return juzgado
        
        return "No especificado"
    
    def extraer_rol(self, texto_remate):
        """Extrae el rol de la causa"""
        patrones_rol = [
            r'Rol\s*N?º?\s*([A-Z]?-?\d+-\d+)',
            r'caratulados\s+[^,]+,\s*Rol\s*N?º?\s*([A-Z]?-?\d+-\d+)',
            r'causa\s+[^,]+,?\s*Rol\s*N?º?\s*([A-Z]?-?\d+-\d+)',
        ]
        
        for patron in patrones_rol:
            match = re.search(patron, texto_remate, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "No especificado"
    
    def extraer_tipo_inmueble(self, texto_remate):
        """Identifica si es casa o departamento"""
        texto_lower = texto_remate.lower()
        
        # Buscar palabras clave
        if any(palabra in texto_lower for palabra in ['departamento', 'depto', 'dpto']):
            return "Departamento"
        elif any(palabra in texto_lower for palabra in ['casa', 'vivienda']):
            return "Casa"
        
        return "Inmueble"
    
    def extraer_ubicacion(self, texto_remate):
        """Extrae información de ubicación"""
        # Buscar comuna
        patron_comuna = r'comuna\s+de\s+([^,]+)'
        match_comuna = re.search(patron_comuna, texto_remate, re.IGNORECASE)
        comuna = match_comuna.group(1).strip() if match_comuna else "No especificada"
        
        # Buscar dirección
        patrones_direccion = [
            r'ubicado\s+en\s+([^,]+(?:número?\s*\d+[^,]*)?)',
            r'calle\s+([^,]+(?:número?\s*\d+[^,]*)?)',
            r'pasaje\s+([^,]+(?:número?\s*\d+[^,]*)?)',
        ]
        
        direccion = "No especificada"
        for patron in patrones_direccion:
            match = re.search(patron, texto_remate, re.IGNORECASE)
            if match:
                direccion = match.group(1).strip()
                # Limpiar texto innecesario
                direccion = re.sub(r'\s*,?\s*comuna\s+de.*$', '', direccion, flags=re.IGNORECASE)
                break
        
        return comuna, direccion
    
    def extraer_precio(self, texto_remate):
        """Extrae el precio mínimo"""
        patrones_precio = [
            r'Mínimo\s+[^$]*\$\s*([\d.,]+)',
            r'precio\s+mínimo[^$]*\$\s*([\d.,]+)',
            r'U\.?F\.?\s*([\d.,]+)',
            r'mínimo\s+para\s+las\s+posturas\s*\$\s*([\d.,]+)',
        ]
        
        for patron in patrones_precio:
            match = re.search(patron, texto_remate, re.IGNORECASE)
            if match:
                precio = match.group(1)
                if 'U.F.' in match.group(0) or 'UF' in match.group(0):
                    return f"UF {precio}"
                else:
                    return f"${precio}"
        
        return "No especificado"
    
    def extraer_email(self, texto_remate):
        """Extrae email de contacto"""
        patron_email = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(patron_email, texto_remate)
        return match.group(1) if match else "No especificado"
    
    def es_fecha_en_rango(self, fecha_str):
        """Verifica si la fecha está en el rango de 1-2 meses"""
        if not fecha_str:
            return False
            
        try:
            fecha_remate = datetime.strptime(fecha_str, '%Y-%m-%d')
            fecha_actual = datetime.now()
            fecha_limite = fecha_actual + timedelta(days=60)  # 2 meses
            
            return fecha_actual <= fecha_remate <= fecha_limite
        except:
            return False
    
    def es_inmueble_relevante(self, texto_remate):
        """Verifica si contiene palabras clave de inmuebles"""
        texto_lower = texto_remate.lower()
        palabras_clave = ['casa', 'departamento', 'depto', 'dpto', 'vivienda']
        
        return any(palabra in texto_lower for palabra in palabras_clave)
    
    def procesar_remates(self, html_content):
        """Procesa el HTML y extrae información de remates"""
        soup = BeautifulSoup(html_content, 'html.parser')
        remates_data = []
        
        # Buscar bloques de texto que contengan información de remates
        # El contenido parece estar en elementos de texto largo
        texto_completo = soup.get_text()
        
        # Dividir por patrones que indican el inicio de un nuevo remate
        patron_division = r'(?=\w+\s+\d{1,2}\s+\w+\s+\d{4},\s+\d{1,2}:\d{2})'
        bloques_remate = re.split(patron_division, texto_completo)
        
        print(f"Se encontraron {len(bloques_remate)} bloques de texto potenciales")
        
        for i, bloque in enumerate(bloques_remate):
            if len(bloque.strip()) < 100:  # Filtrar bloques muy cortos
                continue
                
            # Verificar si es un inmueble relevante
            if not self.es_inmueble_relevante(bloque):
                continue
                
            # Extraer información
            fecha, hora = self.extraer_fecha_hora(bloque)
            
            # Verificar si está en el rango de fechas
            if not self.es_fecha_en_rango(fecha):
                continue
                
            juzgado = self.extraer_juzgado(bloque)
            rol = self.extraer_rol(bloque)
            tipo_inmueble = self.extraer_tipo_inmueble(bloque)
            comuna, direccion = self.extraer_ubicacion(bloque)
            precio = self.extraer_precio(bloque)
            email = self.extraer_email(bloque)
            
            remate_info = {
                'Fecha_Remate': fecha,
                'Hora': hora,
                'Juzgado': juzgado,
                'Rol': rol,
                'Tipo_Inmueble': tipo_inmueble,
                'Comuna': comuna,
                'Direccion': direccion,
                'Precio_Minimo': precio,
                'Email_Contacto': email,
                'Descripcion_Completa': bloque.strip()[:500] + "..." if len(bloque.strip()) > 500 else bloque.strip()
            }
            
            remates_data.append(remate_info)
            print(f"Remate encontrado: {fecha} - {tipo_inmueble} en {comuna}")
        
        return remates_data
    
    def guardar_excel(self, datos, nombre_archivo=None, ruta_destino=None):
        """Guarda los datos en un archivo Excel"""
        if not datos:
            print("No se encontraron remates para guardar.")
            return None
            
        if not nombre_archivo:
            fecha_actual = datetime.now().strftime('%Y%m%d')
            nombre_archivo = f'remates_inmuebles_{fecha_actual}.xlsx'
        
        # Si se especifica una ruta de destino, usarla
        if ruta_destino:
            import os
            if not os.path.exists(ruta_destino):
                os.makedirs(ruta_destino)
            nombre_archivo = os.path.join(ruta_destino, nombre_archivo)
        
        df = pd.DataFrame(datos)
        
        # Crear archivo Excel con formato
        with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Remates Inmuebles', index=False)
            
            # Obtener la hoja para dar formato
            worksheet = writer.sheets['Remates Inmuebles']
            
            # Ajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Archivo guardado como: {nombre_archivo}")
        print(f"Total de remates encontrados: {len(datos)}")
        return nombre_archivo
    
    def ejecutar_scraping(self):
        """Ejecuta el proceso completo de scraping"""
        print("=== SCRAPER DE REMATES INMUEBLES ===")
        print("Buscando remates de casas y departamentos para los próximos 1-2 meses...\n")
        
        # Obtener contenido
        html_content = self.obtener_contenido_web()
        if not html_content:
            print("Error: No se pudo obtener el contenido de la página.")
            return None
        
        # Procesar remates
        datos_remates = self.procesar_remates(html_content)
        
        if not datos_remates:
            print("No se encontraron remates de inmuebles en el rango de fechas especificado.")
            return None
        
        # Guardar archivo en la ruta especificada
        ruta_destino = r"C:\Users\dinko\OneDrive\Escritorio\Remates"
        archivo_excel = self.guardar_excel(datos_remates, ruta_destino=ruta_destino)
        
        print(f"\n=== RESUMEN ===")
        print(f"Archivo Excel generado: {archivo_excel}")
        print(f"Remates encontrados: {len(datos_remates)}")
        print("\nDetalles por tipo:")
        tipos = {}
        for remate in datos_remates:
            tipo = remate['Tipo_Inmueble']
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        for tipo, cantidad in tipos.items():
            print(f"  - {tipo}: {cantidad}")
        
        return archivo_excel

def main():
    """Función principal"""
    scraper = RematesScraper()
    archivo_generado = scraper.ejecutar_scraping()
    
    if archivo_generado:
        print(f"\n¡Proceso completado exitosamente!")
        print(f"Revisa el archivo: {archivo_generado}")
    else:
        print("\nEl proceso no pudo completarse.")

if __name__ == "__main__":
    # Instalar dependencias necesarias (ejecutar en terminal):
    # pip install requests beautifulsoup4 pandas openpyxl
    
    main()