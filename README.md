# CorteÓptimo Pro - Kivy

Optimizador de perfiles de aluminio y cristales con optimización agresiva.

## Características

- ✅ **Optimización agresiva de cristales**: Usa 6 estrategias diferentes y selecciona la mejor
  - FFDH por altura
  - FFDH por área
  - FFDH por ancho
  - Best Fit Decreasing
  - Guillotina horizontal
  - Guillotina vertical
- ✅ **Optimización de perfiles**: Algoritmo FFD con agrupación
- ✅ **Tema oscuro**: Interfaz moderna y fácil de usar
- ✅ **100% offline**: Funciona sin conexión a internet

## Optimización de Cristales

El algoritmo prueba múltiples estrategias de empaquetado:

1. **FFDH (First Fit Decreasing Height)**: Ordena por altura descendente
2. **FFDH por área**: Ordena por área descendente
3. **FFDH por ancho**: Ordena por ancho descendente
4. **BFD (Best Fit Decreasing)**: Coloca donde quede menos espacio
5. **Guillotina horizontal**: Divide el espacio horizontalmente
6. **Guillotina vertical**: Divide el espacio verticalmente

El sistema selecciona automáticamente la mejor distribución (menos planchas).

## Compilación

### Opción 1: GitHub Actions (Recomendado)

1. Sube este repositorio a GitHub
2. Ve a Actions → Build Android APK
3. Click en "Run workflow"
4. Descarga el APK desde Artifacts

### Opción 2: Local

```bash
# Instalar dependencias
sudo apt install openjdk-17-jdk python3-pip
pip install buildozer cython

# Compilar
buildozer -v android debug
```

## Fórmulas

### Puerta
- **Hoja**: Ancho - 3.9 (1p), Alto - 2.7 (2p)
- **Marco**: Alto (2p), Ancho (1p)
- **Zócalo**: Ancho - 19.6 (2p)
- **Revestimiento Superior**: ⌈(Alto - 122.5) / 11⌉ piezas de (Ancho - 17.5)
- **Revestimiento Inferior**: 8 piezas de (Ancho - 17.5)
- **Cristal Superior**: (Ancho - 18) × (Alto - 122.5)
- **Cristal Inferior**: (Ancho - 18) × 92

### Ventana
- **Hoja**: Alto - 7 (4p), (Ancho/2) - 0.6 (4p)
- **Marco**: Alto (2p), Ancho (2p)
- **Perfil de cruce**: Alto - 7 (2p)
- **Cristal**: ((Ancho/2) - 11) × (Alto - 17) (2p)

## Licencia

MIT
