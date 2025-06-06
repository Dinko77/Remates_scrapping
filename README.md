# 🏠 Remates Scraper

**Automatización de búsqueda de remates inmobiliarios en Chile**

Un script de web scraping que extrae automáticamente información de remates de casas y departamentos desde [preremates.cl](https://preremates.cl/content/proximos-remates), filtrando por fechas y generando un archivo Excel organizado con toda la información relevante.

## 📋 Características

- ✅ **Filtrado inteligente**: Solo remates de casas y departamentos
- ✅ **Rango temporal**: Remates de los próximos 1-2 meses
- ✅ **Extracción completa**: Fecha, hora, juzgado, rol, ubicación, precio y contacto
- ✅ **Formato Excel**: Archivo `.xlsx` con columnas organizadas
- ✅ **Sin paginación manual**: Obtiene todos los datos automáticamente

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Remates_scrapping
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Ejecución básica
```bash
python remates_scraper.py
```

### Archivo generado
El script creará un archivo Excel en:
```
C:\Users\dinko\OneDrive\Escritorio\Remates\remates_inmuebles_YYYYMMDD.xlsx
```

## 📊 Datos Extraídos

El archivo Excel incluye las siguientes columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| **Fecha_Remate** | Fecha del remate | 2025-06-24 |
| **Hora** | Hora del remate | 14:30 |
| **Juzgado** | Tribunal responsable | 1º Juzgado Civil de Puente Alto |
| **Rol** | Número de causa | C-9964-2024 |
| **Tipo_Inmueble** | Casa o Departamento | Departamento |
| **Comuna** | Comuna del inmueble | Las Condes |
| **Direccion** | Dirección del inmueble | Martín de Zamora 3443 |
| **Precio_Minimo** | Precio base del remate | $87.450.577 |
| **Email_Contacto** | Email del juzgado | juzgado@pjud.cl |
| **Descripcion_Completa** | Texto completo (resumido) | Descripción del inmueble... |

## 🛠️ Requisitos Técnicos

- **Python**: 3.7 o superior
- **Sistema Operativo**: Windows, macOS, Linux
- **Conexión a Internet**: Requerida para el web scraping

### Dependencias
- `requests` >= 2.31.0
- `beautifulsoup4` >= 4.12.0
- `pandas` >= 2.0.0
- `openpyxl` >= 3.1.0

## 📁 Estructura del Proyecto

```
Remates_scrapping/
├── README.md
├── requirements.txt
├── remates_scraper.py
└── Remates/
    └── remates_inmuebles_YYYYMMDD.xlsx
```

## 🎯 Filtros Aplicados

### Por Tipo de Inmueble
- Casa
- Departamento
- Depto / Dpto
- Vivienda

### Por Fechas
- **Desde**: Fecha actual
- **Hasta**: 2 meses en el futuro
- **Formato**: Solo fechas válidas y parseables

## 📝 Ejemplo de Salida

```
=== SCRAPER DE REMATES INMUEBLES ===
Buscando remates de casas y departamentos para los próximos 1-2 meses...

Obteniendo datos de preremates.cl...
Se encontraron 45 bloques de texto potenciales
Remate encontrado: 2025-06-24 - Casa en Puente Alto
Remate encontrado: 2025-07-15 - Departamento en Las Condes

=== RESUMEN ===
Archivo Excel generado: remates_inmuebles_20250604.xlsx
Remates encontrados: 8
  - Casa: 3
  - Departamento: 5
```

## ⚠️ Consideraciones

- **Legalidad**: Este script está diseñado para uso educativo y de investigación
- **Frecuencia**: Recomendamos no ejecutar más de una vez por día para evitar sobrecarga del servidor
- **Datos**: La información extraída proviene de fuentes públicas disponibles en preremates.cl

## 🐛 Solución de Problemas

### Error de conexión
```bash
Error al obtener el contenido web: ConnectionError
```
**Solución**: Verificar conexión a internet y reintentar

### No se encuentran remates
```bash
No se encontraron remates de inmuebles en el rango de fechas especificado.
```
**Solución**: Normal si no hay remates programados en las próximas 8 semanas

### Error de permisos
```bash
PermissionError: [Errno 13]
```
**Solución**: Cerrar el archivo Excel si está abierto y reintentar

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Contacto

**Autor**: Dinko  
**Email**: [tu-email@ejemplo.com]  
**Proyecto**: [URL del repositorio]

---

⭐ Si este proyecto te fue útil, ¡considera darle una estrella!