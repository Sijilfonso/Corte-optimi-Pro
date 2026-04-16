"""
CorteÓptimo Pro - Optimizador de Perfiles y Cristales
Versión Kivy con optimización agresiva de cristales
"""

import json
import os
import math
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader

# Configurar tema oscuro
Window.clearcolor = (0.07, 0.07, 0.07, 1)  # #121212

# ============================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================

class TipoElemento(Enum):
    PUERTA = "puerta"
    VENTANA = "ventana"

class TipoCristal(Enum):
    CRISTAL = "cristal"
    ENCHAPE = "enchape"
    REVESTIMIENTO_TUBULAR = "revestimiento_tubular"

@dataclass
class Configuracion:
    largo_barra_perfil: float = 580.0
    corte_sierra: float = 0.5
    rectificado: float = 0.5
    
    descuento_hoja_puerta_ancho: float = 3.9
    descuento_hoja_puerta_alto: float = 2.7
    descuento_hoja_ventana_alto: float = 7.0
    descuento_hoja_ventana_ancho: float = 0.6
    descuento_zocalo: float = 19.6
    descuento_cristal_puerta_ancho: float = 18.0
    descuento_cristal_puerta_sup_alto: float = 122.5
    descuento_cristal_ventana_ancho: float = 11.0
    descuento_cristal_ventana_alto: float = 17.0
    
    descuento_revestimiento_ancho: float = 17.5
    revestimiento_sup_base: float = 122.5
    revestimiento_sup_divisor: float = 11.0
    revestimiento_inf_cantidad: int = 8
    
    ancho_plancha_cristal: float = 244.0
    alto_plancha_cristal: float = 183.0
    ancho_plancha_enchape: float = 244.0
    alto_plancha_enchape: float = 183.0
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class Elemento:
    id: str
    nombre: str
    tipo: TipoElemento
    ancho: float
    alto: float
    cantidad: int
    tipo_cristal_sup: TipoCristal
    tipo_cristal_inf: Optional[TipoCristal] = None
    fecha_creacion: str = ""
    
    def __post_init__(self):
        if not self.fecha_creacion:
            self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo.value,
            'ancho': self.ancho,
            'alto': self.alto,
            'cantidad': self.cantidad,
            'tipo_cristal_sup': self.tipo_cristal_sup.value,
            'tipo_cristal_inf': self.tipo_cristal_inf.value if self.tipo_cristal_inf else None,
            'fecha_creacion': self.fecha_creacion
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            nombre=data['nombre'],
            tipo=TipoElemento(data['tipo']),
            ancho=data['ancho'],
            alto=data['alto'],
            cantidad=data['cantidad'],
            tipo_cristal_sup=TipoCristal(data['tipo_cristal_sup']),
            tipo_cristal_inf=TipoCristal(data['tipo_cristal_inf']) if data.get('tipo_cristal_inf') else None,
            fecha_creacion=data.get('fecha_creacion', '')
        )

@dataclass
class Proyecto:
    id: str
    nombre: str
    elementos: List[Elemento]
    fecha_creacion: str = ""
    fecha_modificacion: str = ""
    
    def __post_init__(self):
        if not self.fecha_creacion:
            self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M")
        if not self.fecha_modificacion:
            self.fecha_modificacion = self.fecha_creacion
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'elementos': [e.to_dict() for e in self.elementos],
            'fecha_creacion': self.fecha_creacion,
            'fecha_modificacion': self.fecha_modificacion
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            nombre=data['nombre'],
            elementos=[Elemento.from_dict(e) for e in data['elementos']],
            fecha_creacion=data.get('fecha_creacion', ''),
            fecha_modificacion=data.get('fecha_modificacion', '')
        )

# ============================================
# OPTIMIZADORES
# ============================================

class OptimizadorPerfiles:
    def __init__(self, config: Configuracion):
        self.config = config
        self.LARGO_MAX = config.largo_barra_perfil
        self.CORTE = config.corte_sierra
        self.MARGEN = config.rectificado * 2
        self.utilizable = self.LARGO_MAX - self.MARGEN
    
    def optimizar(self, piezas: List[float]) -> List[List[float]]:
        piezas_ordenadas = sorted([p for p in piezas if p <= self.utilizable], reverse=True)
        barras = []
        for pieza in piezas_ordenadas:
            encajado = False
            for barra in barras:
                espacio_ocupado = sum(barra) + (len(barra) * self.CORTE)
                if espacio_ocupado + pieza <= self.utilizable:
                    barra.append(pieza)
                    encajado = True
                    break
            if not encajado:
                barras.append([pieza])
        return barras
    
    def calcular_sobrante(self, barra: List[float]) -> float:
        return self.utilizable - (sum(barra) + (len(barra) - 1) * self.CORTE)

class OptimizadorCristales:
    """Optimizador agresivo de cristales usando múltiples estrategias"""
    
    def __init__(self, config: Configuracion):
        self.config = config
    
    def optimizar(self, piezas: List[Dict], ancho_plancha: float, alto_plancha: float) -> Dict:
        """
        Intenta múltiples estrategias y devuelve la mejor
        """
        # Estandarizar piezas
        piezas_estandar = []
        for p in piezas:
            for _ in range(p['cantidad']):
                piezas_estandar.append({
                    'w': max(p['ancho'], p['alto']),
                    'h': min(p['ancho'], p['alto']),
                    'id': p.get('id', '')
                })
        
        # Probar diferentes estrategias
        resultados = []
        
        # Estrategia 1: FFDH por altura descendente
        r1 = self._ffdh(piezas_estandar, ancho_plancha, alto_plancha, 'height')
        resultados.append(r1)
        
        # Estrategia 2: FFDH por área descendente
        r2 = self._ffdh(piezas_estandar, ancho_plancha, alto_plancha, 'area')
        resultados.append(r2)
        
        # Estrategia 3: FFDH por ancho descendente
        r3 = self._ffdh(piezas_estandar, ancho_plancha, alto_plancha, 'width')
        resultados.append(r3)
        
        # Estrategia 4: Best Fit Decreasing
        r4 = self._bfd(piezas_estandar, ancho_plancha, alto_plancha)
        resultados.append(r4)
        
        # Estrategia 5: Guillotina con split horizontal
        r5 = self._guillotina(piezas_estandar, ancho_plancha, alto_plancha, 'horizontal')
        resultados.append(r5)
        
        # Estrategia 6: Guillotina con split vertical
        r6 = self._guillotina(piezas_estandar, ancho_plancha, alto_plancha, 'vertical')
        resultados.append(r6)
        
        # Seleccionar el mejor resultado
        mejor = min(resultados, key=lambda x: x['total_hojas'])
        return mejor
    
    def _ffdh(self, piezas: List[Dict], ancho_plancha: float, alto_plancha: float, 
              orden: str) -> Dict:
        """First Fit Decreasing Height"""
        # Ordenar según criterio
        piezas_copy = piezas.copy()
        if orden == 'height':
            piezas_copy.sort(key=lambda x: x['h'], reverse=True)
        elif orden == 'area':
            piezas_copy.sort(key=lambda x: x['w'] * x['h'], reverse=True)
        elif orden == 'width':
            piezas_copy.sort(key=lambda x: x['w'], reverse=True)
        
        return self._pack_guillotina(piezas_copy, ancho_plancha, alto_plancha)
    
    def _bfd(self, piezas: List[Dict], ancho_plancha: float, alto_plancha: float) -> Dict:
        """Best Fit Decreasing - coloca en la hoja con menos espacio disponible"""
        piezas_copy = sorted(piezas, key=lambda x: x['w'] * x['h'], reverse=True)
        return self._pack_best_fit(piezas_copy, ancho_plancha, alto_plancha)
    
    def _guillotina(self, piezas: List[Dict], ancho_plancha: float, alto_plancha: float,
                    split_mode: str) -> Dict:
        """Algoritmo de guillotina con diferentes modos de división"""
        piezas_copy = sorted(piezas, key=lambda x: x['w'] * x['h'], reverse=True)
        return self._pack_guillotina_avanzada(piezas_copy, ancho_plancha, alto_plancha, split_mode)
    
    def _pack_guillotina(self, piezas: List[Dict], ancho_plancha: float, alto_plancha: float) -> Dict:
        """Packing con guillotina básica"""
        hojas = []
        resultado = []
        
        def crear_hoja():
            return {
                'niveles': [],
                'y_libre': 0,
                'espacios': [{'x': 0, 'y': 0, 'w': ancho_plancha, 'h': alto_plancha}]
            }
        
        for p in piezas:
            ubicado = False
            
            # Intentar en hojas existentes
            for h_idx, hoja in enumerate(hojas):
                # Intentar en niveles existentes
                for nivel in hoja['niveles']:
                    if nivel['x_libre'] + p['w'] <= ancho_plancha and p['h'] <= nivel['alto']:
                        resultado.append({'x': nivel['x_libre'], 'y': nivel['y_inicio'], 
                                        'w': p['w'], 'h': p['h'], 'hoja_idx': h_idx})
                        nivel['x_libre'] += p['w']
                        ubicado = True
                        break
                    
                    # Intentar rotado
                    if nivel['x_libre'] + p['h'] <= ancho_plancha and p['w'] <= nivel['alto']:
                        resultado.append({'x': nivel['x_libre'], 'y': nivel['y_inicio'], 
                                        'w': p['h'], 'h': p['w'], 'hoja_idx': h_idx})
                        nivel['x_libre'] += p['h']
                        ubicado = True
                        break
                
                if ubicado:
                    break
                
                # Crear nuevo nivel
                if hoja['y_libre'] + p['h'] <= alto_plancha:
                    resultado.append({'x': 0, 'y': hoja['y_libre'], 'w': p['w'], 
                                    'h': p['h'], 'hoja_idx': h_idx})
                    hoja['niveles'].append({
                        'y_inicio': hoja['y_libre'],
                        'alto': p['h'],
                        'x_libre': p['w']
                    })
                    hoja['y_libre'] += p['h']
                    ubicado = True
                    break
                
                # Crear nivel rotado
                if hoja['y_libre'] + p['w'] <= alto_plancha and p['h'] <= ancho_plancha:
                    resultado.append({'x': 0, 'y': hoja['y_libre'], 'w': p['h'], 
                                    'h': p['w'], 'hoja_idx': h_idx})
                    hoja['niveles'].append({
                        'y_inicio': hoja['y_libre'],
                        'alto': p['w'],
                        'x_libre': p['h']
                    })
                    hoja['y_libre'] += p['w']
                    ubicado = True
                    break
            
            if not ubicado:
                nueva = crear_hoja()
                hojas.append(nueva)
                resultado.append({'x': 0, 'y': 0, 'w': p['w'], 'h': p['h'], 
                                'hoja_idx': len(hojas) - 1})
                nueva['niveles'].append({'y_inicio': 0, 'alto': p['h'], 'x_libre': p['w']})
                nueva['y_libre'] = p['h']
        
        return {'hojas': hojas, 'piezas': resultado, 'total_hojas': len(hojas)}
    
    def _pack_best_fit(self, piezas: List[Dict], ancho_plancha: float, alto_plancha: float) -> Dict:
        """Best Fit - coloca donde quede menos espacio sobrante"""
        hojas = []
        resultado = []
        
        for p in piezas:
            mejor_hoja = None
            mejor_espacio = float('inf')
            mejor_pos = None
            mejor_rotado = False
            
            for h_idx, hoja in enumerate(hojas):
                # Buscar mejor posición en esta hoja
                for y in range(0, int(alto_plancha - p['h']) + 1, 1):
                    for x in range(0, int(ancho_plancha - p['w']) + 1, 1):
                        if self._puede_colocar(hoja, x, y, p['w'], p['h'], resultado, h_idx, ancho_plancha, alto_plancha):
                            espacio_restante = self._calcular_espacio_restante(hoja, x, y, p['w'], p['h'], ancho_plancha, alto_plancha)
                            if espacio_restante < mejor_espacio:
                                mejor_espacio = espacio_restante
                                mejor_hoja = h_idx
                                mejor_pos = (x, y, p['w'], p['h'])
                                mejor_rotado = False
                
                # Intentar rotado
                for y in range(0, int(alto_plancha - p['w']) + 1, 1):
                    for x in range(0, int(ancho_plancha - p['h']) + 1, 1):
                        if self._puede_colocar(hoja, x, y, p['h'], p['w'], resultado, h_idx, ancho_plancha, alto_plancha):
                            espacio_restante = self._calcular_espacio_restante(hoja, x, y, p['h'], p['w'], ancho_plancha, alto_plancha)
                            if espacio_restante < mejor_espacio:
                                mejor_espacio = espacio_restante
                                mejor_hoja = h_idx
                                mejor_pos = (x, y, p['h'], p['w'])
                                mejor_rotado = True
            
            if mejor_hoja is not None:
                resultado.append({
                    'x': mejor_pos[0], 'y': mejor_pos[1], 
                    'w': mejor_pos[2], 'h': mejor_pos[3], 
                    'hoja_idx': mejor_hoja
                })
            else:
                # Nueva hoja
                hojas.append({'piezas': []})
                resultado.append({
                    'x': 0, 'y': 0, 'w': p['w'], 'h': p['h'], 
                    'hoja_idx': len(hojas) - 1
                })
        
        return {'hojas': hojas, 'piezas': resultado, 'total_hojas': len(hojas)}
    
    def _puede_colocar(self, hoja, x, y, w, h, resultado, hoja_idx, ancho_plancha, alto_plancha) -> bool:
        """Verifica si una pieza puede colocarse sin superponerse"""
        if x + w > ancho_plancha or y + h > alto_plancha:
            return False
        
        for p in resultado:
            if p['hoja_idx'] != hoja_idx:
                continue
            # Verificar superposición
            if not (x + w <= p['x'] or x >= p['x'] + p['w'] or 
                    y + h <= p['y'] or y >= p['y'] + p['h']):
                return False
        
        return True
    
    def _calcular_espacio_restante(self, hoja, x, y, w, h, ancho_plancha, alto_plancha) -> float:
        """Calcula el espacio restante después de colocar una pieza"""
        return (ancho_plancha * alto_plancha) - (w * h)
    
    def _pack_guillotina_avanzada(self, piezas: List[Dict], ancho_plancha: float, 
                                   alto_plancha: float, split_mode: str) -> Dict:
        """Guillotina avanzada con recursión"""
        hojas = []
        resultado = []
        
        class Nodo:
            def __init__(self, x, y, w, h):
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                self.usado = False
                self.izq = None
                self.der = None
            
            def insertar(self, pieza):
                if self.usado:
                    # Intentar en hijos
                    if self.izq:
                        nodo = self.izq.insertar(pieza)
                        if nodo:
                            return nodo
                    if self.der:
                        return self.der.insertar(pieza)
                    return None
                
                # Verificar si cabe
                if pieza['w'] > self.w or pieza['h'] > self.h:
                    # Intentar rotado
                    if pieza['h'] > self.w or pieza['w'] > self.h:
                        return None
                    pieza = {'w': pieza['h'], 'h': pieza['w'], 'id': pieza.get('id', '')}
                
                # Dividir espacio
                self.usado = True
                
                if split_mode == 'horizontal':
                    # Dividir horizontalmente
                    self.izq = Nodo(self.x + pieza['w'], self.y, 
                                   self.w - pieza['w'], pieza['h'])
                    self.der = Nodo(self.x, self.y + pieza['h'], 
                                   self.w, self.h - pieza['h'])
                else:
                    # Dividir verticalmente
                    self.izq = Nodo(self.x, self.y + pieza['h'], 
                                   pieza['w'], self.h - pieza['h'])
                    self.der = Nodo(self.x + pieza['w'], self.y, 
                                   self.w - pieza['w'], self.h)
                
                return self
        
        for p in piezas:
            ubicado = False
            
            for h_idx, raiz in enumerate(hojas):
                nodo = raiz.insertar(p)
                if nodo:
                    resultado.append({
                        'x': nodo.x, 'y': nodo.y,
                        'w': p['w'], 'h': p['h'],
                        'hoja_idx': h_idx
                    })
                    ubicado = True
                    break
            
            if not ubicado:
                nueva_raiz = Nodo(0, 0, ancho_plancha, alto_plancha)
                hojas.append(nueva_raiz)
                nodo = nueva_raiz.insertar(p)
                if nodo:
                    resultado.append({
                        'x': nodo.x, 'y': nodo.y,
                        'w': p['w'], 'h': p['h'],
                        'hoja_idx': len(hojas) - 1
                    })
        
        return {'hojas': hojas, 'piezas': resultado, 'total_hojas': len(hojas)}

# ============================================
# CALCULADORA DE MATERIALES
# ============================================

class CalculadoraMateriales:
    def __init__(self, config: Configuracion):
        self.config = config
    
    def calcular_puerta(self, ancho, alto, tipo_cristal_sup, tipo_cristal_inf):
        perfiles = {
            'Puerta - Hoja': [
                ancho - self.config.descuento_hoja_puerta_ancho,
                alto - self.config.descuento_hoja_puerta_alto,
                alto - self.config.descuento_hoja_puerta_alto
            ],
            'Puerta - Marco': [
                alto, alto, ancho
            ],
            'Puerta - Zócalo': [
                ancho - self.config.descuento_zocalo,
                ancho - self.config.descuento_zocalo
            ],
        }
        
        revestimiento = []
        if tipo_cristal_sup == TipoCristal.REVESTIMIENTO_TUBULAR or \
           tipo_cristal_inf == TipoCristal.REVESTIMIENTO_TUBULAR:
            ancho_revest = ancho - self.config.descuento_revestimiento_ancho
            
            if tipo_cristal_sup == TipoCristal.REVESTIMIENTO_TUBULAR:
                cant_sup = math.ceil((alto - self.config.revestimiento_sup_base) / 
                                    self.config.revestimiento_sup_divisor)
                revestimiento.extend([ancho_revest] * cant_sup)
            
            if tipo_cristal_inf == TipoCristal.REVESTIMIENTO_TUBULAR:
                cant_inf = self.config.revestimiento_inf_cantidad
                revestimiento.extend([ancho_revest] * cant_inf)
        
        if revestimiento:
            perfiles['Puerta - Revestimiento Tubular'] = revestimiento
        
        cristales = []
        if tipo_cristal_sup in [TipoCristal.CRISTAL, TipoCristal.ENCHAPE]:
            cristales.append({
                'tipo': tipo_cristal_sup.value,
                'seccion': 'superior',
                'ancho': ancho - self.config.descuento_cristal_puerta_ancho,
                'alto': alto - self.config.descuento_cristal_puerta_sup_alto,
                'cantidad': 1
            })
        
        if tipo_cristal_inf in [TipoCristal.CRISTAL, TipoCristal.ENCHAPE]:
            cristales.append({
                'tipo': tipo_cristal_inf.value,
                'seccion': 'inferior',
                'ancho': ancho - self.config.descuento_cristal_puerta_ancho,
                'alto': 92,
                'cantidad': 1
            })
        
        return {'perfiles': perfiles, 'cristales': cristales}
    
    def calcular_ventana(self, ancho, alto, tipo_cristal):
        ancho_hoja = (ancho / 2) - self.config.descuento_hoja_ventana_ancho
        alto_hoja = alto - self.config.descuento_hoja_ventana_alto
        
        perfiles = {
            'Ventana - Hoja': [
                alto_hoja, alto_hoja, alto_hoja, alto_hoja,
                ancho_hoja, ancho_hoja, ancho_hoja, ancho_hoja
            ],
            'Ventana - Marco': [
                alto, alto, ancho, ancho
            ],
            'Ventana - Perfil de cruce': [
                alto_hoja, alto_hoja
            ],
        }
        
        cristales = []
        if tipo_cristal in [TipoCristal.CRISTAL, TipoCristal.ENCHAPE]:
            ancho_cristal = (ancho / 2) - self.config.descuento_cristal_ventana_ancho
            alto_cristal = alto - self.config.descuento_cristal_ventana_alto
            cristales.append({
                'tipo': tipo_cristal.value,
                'ancho': ancho_cristal,
                'alto': alto_cristal,
                'cantidad': 2
            })
        
        return {'perfiles': perfiles, 'cristales': cristales}

# ============================================
# GESTOR DE DATOS
# ============================================

class GestorDatos:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        self.proyectos_file = os.path.join(self.data_dir, 'proyectos.json')
        self.config_file = os.path.join(self.data_dir, 'config.json')
    
    def guardar_proyecto(self, proyecto):
        proyectos = self.cargar_proyectos_raw()
        proyectos_dict = {p['id']: p for p in proyectos}
        proyectos_dict[proyecto.id] = proyecto.to_dict()
        
        with open(self.proyectos_file, 'w', encoding='utf-8') as f:
            json.dump(list(proyectos_dict.values()), f, ensure_ascii=False, indent=2)
    
    def cargar_proyectos_raw(self):
        if os.path.exists(self.proyectos_file):
            with open(self.proyectos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def cargar_proyectos(self):
        return [Proyecto.from_dict(p) for p in self.cargar_proyectos_raw()]
    
    def eliminar_proyecto(self, proyecto_id):
        proyectos = self.cargar_proyectos_raw()
        proyectos = [p for p in proyectos if p['id'] != proyecto_id]
        
        with open(self.proyectos_file, 'w', encoding='utf-8') as f:
            json.dump(proyectos, f, ensure_ascii=False, indent=2)
    
    def guardar_config(self, config):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)
    
    def cargar_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return Configuracion.from_dict(json.load(f))
        return Configuracion()

# ============================================
# UI - WIDGETS PERSONALIZADOS
# ============================================

class DarkCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(8)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        with self.canvas.before:
            Color(0.118, 0.118, 0.118, 1)  # #1E1E1E
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class DarkButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.129, 0.588, 0.953, 1)  # #2196F3
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(48)

class DarkTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.173, 0.173, 0.173, 1)  # #2C2C2C
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(48)
        self.multiline = False

class DarkLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(24)

class PlanchaVisual(Widget):
    def __init__(self, ancho_plancha, alto_plancha, piezas, **kwargs):
        super().__init__(**kwargs)
        self.ancho_plancha = ancho_plancha
        self.alto_plancha = alto_plancha
        self.piezas = piezas
        self.size_hint_y = None
        self.height = dp(200)
        
        with self.canvas:
            Color(0.173, 0.173, 0.173, 1)
            self.fondo = Rectangle(pos=self.pos, size=self.size)
            
            # Dibujar piezas
            escala = min(self.width / ancho_plancha, self.height / alto_plancha) if ancho_plancha > 0 else 1
            for p in piezas:
                Color(0.298, 0.686, 0.314, 0.3)  # Verde transparente
                Rectangle(
                    pos=(self.x + p['x'] * escala, self.y + p['y'] * escala),
                    size=(p['w'] * escala, p['h'] * escala)
                )
                Color(0.298, 0.686, 0.314, 1)  # Borde verde
                Line(
                    rectangle=(self.x + p['x'] * escala, self.y + p['y'] * escala,
                              p['w'] * escala, p['h'] * escala),
                    width=1
                )
        
        self.bind(pos=self._update_canvas, size=self._update_canvas)
    
    def _update_canvas(self, instance, value):
        self.fondo.pos = instance.pos
        self.fondo.size = instance.size
        self.canvas.clear()
        with self.canvas:
            Color(0.173, 0.173, 0.173, 1)
            self.fondo = Rectangle(pos=self.pos, size=self.size)
            
            escala = min(self.width / self.ancho_plancha, self.height / self.alto_plancha) if self.ancho_plancha > 0 else 1
            for p in self.piezas:
                Color(0.298, 0.686, 0.314, 0.3)
                Rectangle(
                    pos=(self.x + p['x'] * escala, self.y + p['y'] * escala),
                    size=(p['w'] * escala, p['h'] * escala)
                )
                Color(0.298, 0.686, 0.314, 1)
                Line(
                    rectangle=(self.x + p['x'] * escala, self.y + p['y'] * escala,
                              p['w'] * escala, p['h'] * escala),
                    width=1
                )

# ============================================
# UI - SCREENS
# ============================================

class ProyectosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(56))
        title = DarkLabel(
            text='CorteÓptimo Pro',
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(56)
        )
        header.add_widget(title)
        layout.add_widget(header)
        
        # Lista de proyectos
        self.scroll = ScrollView()
        self.lista_container = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        self.lista_container.bind(minimum_height=self.lista_container.setter('height'))
        self.scroll.add_widget(self.lista_container)
        layout.add_widget(self.scroll)
        
        # Botón nuevo
        btn_nuevo = DarkButton(
            text='+ Nuevo Proyecto',
            on_press=self.nuevo_proyecto
        )
        layout.add_widget(btn_nuevo)
        
        self.add_widget(layout)
        self.actualizar_lista()
    
    def actualizar_lista(self):
        self.lista_container.clear_widgets()
        app = App.get_running_app()
        proyectos = app.gestor.cargar_proyectos()
        
        if not proyectos:
            empty = DarkLabel(
                text='No hay proyectos\nCrea uno nuevo para comenzar',
                halign='center'
            )
            self.lista_container.add_widget(empty)
            return
        
        for proyecto in proyectos:
            card = DarkCard()
            
            info = BoxLayout(orientation='horizontal')
            nombre = DarkLabel(
                text=f"{proyecto.nombre}\n{len(proyecto.elementos)} elementos",
                halign='left'
            )
            info.add_widget(nombre)
            
            btn_ver = DarkButton(
                text='Ver',
                size_hint_x=None,
                width=dp(80),
                on_press=lambda x, p=proyecto: self.ver_resultados(p)
            )
            info.add_widget(btn_ver)
            
            btn_editar = DarkButton(
                text='Editar',
                size_hint_x=None,
                width=dp(80),
                on_press=lambda x, p=proyecto: self.editar_proyecto(p)
            )
            info.add_widget(btn_editar)
            
            btn_eliminar = DarkButton(
                text='X',
                size_hint_x=None,
                width=dp(48),
                background_color=(0.957, 0.263, 0.212, 1),
                on_press=lambda x, p=proyecto: self.eliminar_proyecto(p)
            )
            info.add_widget(btn_eliminar)
            
            card.add_widget(info)
            self.lista_container.add_widget(card)
    
    def nuevo_proyecto(self, instance):
        app = App.get_running_app()
        app.proyecto_actual = None
        app.elementos_temp = []
        self.manager.current = 'proyecto_edit'
    
    def editar_proyecto(self, proyecto):
        app = App.get_running_app()
        app.proyecto_actual = proyecto
        app.elementos_temp = list(proyecto.elementos)
        self.manager.current = 'proyecto_edit'
    
    def ver_resultados(self, proyecto):
        app = App.get_running_app()
        app.proyecto_actual = proyecto
        app.elementos_temp = list(proyecto.elementos)
        self.manager.current = 'resultados'
    
    def eliminar_proyecto(self, proyecto):
        app = App.get_running_app()
        app.gestor.eliminar_proyecto(proyecto.id)
        self.actualizar_lista()
    
    def on_enter(self):
        self.actualizar_lista()

class ProyectoEditScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
        btn_volver = DarkButton(
            text='←',
            size_hint_x=None,
            width=dp(48),
            on_press=lambda x: setattr(self.manager, 'current', 'proyectos')
        )
        header.add_widget(btn_volver)
        
        self.titulo = DarkLabel(
            text='Nuevo Proyecto',
            font_size=dp(20),
            bold=True
        )
        header.add_widget(self.titulo)
        
        btn_guardar = DarkButton(
            text='Guardar',
            size_hint_x=None,
            width=dp(100),
            background_color=(0.298, 0.686, 0.314, 1),
            on_press=self.guardar_proyecto
        )
        header.add_widget(btn_guardar)
        
        layout.add_widget(header)
        
        # Nombre
        layout.add_widget(DarkLabel(text='Nombre del Proyecto:'))
        self.txt_nombre = DarkTextInput(hint_text='Ej: Proyecto Casa')
        layout.add_widget(self.txt_nombre)
        
        # Elementos
        layout.add_widget(DarkLabel(text='Elementos:'))
        btn_agregar = DarkButton(
            text='+ Agregar Elemento',
            on_press=self.agregar_elemento
        )
        layout.add_widget(btn_agregar)
        
        self.scroll = ScrollView()
        self.lista_elementos = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.lista_elementos.bind(minimum_height=self.lista_elementos.setter('height'))
        self.scroll.add_widget(self.lista_elementos)
        layout.add_widget(self.scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        app = App.get_running_app()
        if app.proyecto_actual:
            self.titulo.text = 'Editar Proyecto'
            self.txt_nombre.text = app.proyecto_actual.nombre
        else:
            self.titulo.text = 'Nuevo Proyecto'
            self.txt_nombre.text = ''
        self.actualizar_elementos()
    
    def actualizar_elementos(self):
        self.lista_elementos.clear_widgets()
        app = App.get_running_app()
        
        for i, elem in enumerate(app.elementos_temp):
            card = DarkCard()
            
            tipo_text = 'Puerta' if elem.tipo == TipoElemento.PUERTA else 'Ventana'
            info = DarkLabel(
                text=f"{tipo_text} - {elem.ancho}×{elem.alto} cm (x{elem.cantidad})"
            )
            card.add_widget(info)
            
            btn_eliminar = DarkButton(
                text='Eliminar',
                size_hint_y=None,
                height=dp(36),
                background_color=(0.957, 0.263, 0.212, 1),
                on_press=lambda x, idx=i: self.eliminar_elemento(idx)
            )
            card.add_widget(btn_eliminar)
            
            self.lista_elementos.add_widget(card)
    
    def agregar_elemento(self, instance):
        self.manager.current = 'elemento_form'
    
    def eliminar_elemento(self, idx):
        app = App.get_running_app()
        app.elementos_temp.pop(idx)
        self.actualizar_elementos()
    
    def guardar_proyecto(self, instance):
        nombre = self.txt_nombre.text.strip()
        if not nombre:
            return
        
        app = App.get_running_app()
        
        if app.proyecto_actual:
            proyecto = app.proyecto_actual
            proyecto.nombre = nombre
            proyecto.elementos = app.elementos_temp
            proyecto.fecha_modificacion = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            proyecto = Proyecto(
                id=str(datetime.now().timestamp()),
                nombre=nombre,
                elementos=app.elementos_temp
            )
        
        app.gestor.guardar_proyecto(proyecto)
        self.manager.current = 'proyectos'

class ElementoFormScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        layout.add_widget(DarkLabel(text='Tipo:', font_size=dp(18), bold=True))
        
        self.spinner_tipo = Spinner(
            text='Puerta',
            values=['Puerta', 'Ventana'],
            size_hint_y=None,
            height=dp(48),
            background_color=(0.173, 0.173, 0.173, 1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.spinner_tipo)
        
        layout.add_widget(DarkLabel(text='Ancho (cm):'))
        self.txt_ancho = DarkTextInput(hint_text='90')
        layout.add_widget(self.txt_ancho)
        
        layout.add_widget(DarkLabel(text='Alto (cm):'))
        self.txt_alto = DarkTextInput(hint_text='210')
        layout.add_widget(self.txt_alto)
        
        layout.add_widget(DarkLabel(text='Cantidad:'))
        self.txt_cantidad = DarkTextInput(text='1')
        layout.add_widget(self.txt_cantidad)
        
        layout.add_widget(DarkLabel(text='Material Superior:'))
        self.spinner_mat_sup = Spinner(
            text='Cristal',
            values=['Cristal', 'Enchape', 'Revestimiento Tubular'],
            size_hint_y=None,
            height=dp(48),
            background_color=(0.173, 0.173, 0.173, 1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.spinner_mat_sup)
        
        layout.add_widget(DarkLabel(text='Material Inferior:'))
        self.spinner_mat_inf = Spinner(
            text='Cristal',
            values=['Cristal', 'Enchape', 'Revestimiento Tubular'],
            size_hint_y=None,
            height=dp(48),
            background_color=(0.173, 0.173, 0.173, 1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.spinner_mat_inf)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        
        btn_cancelar = DarkButton(
            text='Cancelar',
            background_color=(0.459, 0.459, 0.459, 1),
            on_press=lambda x: setattr(self.manager, 'current', 'proyecto_edit')
        )
        btn_layout.add_widget(btn_cancelar)
        
        btn_guardar = DarkButton(
            text='Guardar',
            background_color=(0.298, 0.686, 0.314, 1),
            on_press=self.guardar
        )
        btn_layout.add_widget(btn_guardar)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
    
    def guardar(self, instance):
        try:
            tipo = TipoElemento.PUERTA if self.spinner_tipo.text == 'Puerta' else TipoElemento.VENTANA
            ancho = float(self.txt_ancho.text)
            alto = float(self.txt_alto.text)
            cantidad = int(self.txt_cantidad.text)
            
            mat_sup_map = {
                'Cristal': TipoCristal.CRISTAL,
                'Enchape': TipoCristal.ENCHAPE,
                'Revestimiento Tubular': TipoCristal.REVESTIMIENTO_TUBULAR
            }
            
            elemento = Elemento(
                id=str(datetime.now().timestamp()),
                nombre=f"{self.spinner_tipo.text}_{len(App.get_running_app().elementos_temp) + 1}",
                tipo=tipo,
                ancho=ancho,
                alto=alto,
                cantidad=cantidad,
                tipo_cristal_sup=mat_sup_map[self.spinner_mat_sup.text],
                tipo_cristal_inf=mat_sup_map[self.spinner_mat_inf.text] if tipo == TipoElemento.PUERTA else None
            )
            
            App.get_running_app().elementos_temp.append(elemento)
            self.manager.current = 'proyecto_edit'
            
        except ValueError:
            pass

class ResultadosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
        btn_volver = DarkButton(
            text='←',
            size_hint_x=None,
            width=dp(48),
            on_press=lambda x: setattr(self.manager, 'current', 'proyectos')
        )
        header.add_widget(btn_volver)
        
        titulo = DarkLabel(
            text='Resultados',
            font_size=dp(20),
            bold=True
        )
        header.add_widget(titulo)
        
        layout.add_widget(header)
        
        # Tabs
        tabs = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        
        btn_perfiles = DarkButton(
            text='Perfiles',
            on_press=lambda x: self.mostrar_tab('perfiles')
        )
        tabs.add_widget(btn_perfiles)
        
        btn_cristales = DarkButton(
            text='Cristales',
            on_press=lambda x: self.mostrar_tab('cristales')
        )
        tabs.add_widget(btn_cristales)
        
        layout.add_widget(tabs)
        
        # Contenido
        self.scroll = ScrollView()
        self.contenido = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        self.contenido.bind(minimum_height=self.contenido.setter('height'))
        self.scroll.add_widget(self.contenido)
        layout.add_widget(self.scroll)
        
        self.add_widget(layout)
        self.tab_actual = 'perfiles'
    
    def on_enter(self):
        self.calcular_resultados()
    
    def mostrar_tab(self, tab):
        self.tab_actual = tab
        self.calcular_resultados()
    
    def calcular_resultados(self):
        self.contenido.clear_widgets()
        
        app = App.get_running_app()
        elementos = app.elementos_temp
        
        if not elementos:
            self.contenido.add_widget(DarkLabel(text='No hay elementos'))
            return
        
        # Calcular materiales
        calculadora = CalculadoraMateriales(app.config)
        todas_piezas_perfiles = {}
        todas_piezas_cristales = []
        
        for elem in elementos:
            if elem.tipo == TipoElemento.PUERTA:
                materiales = calculadora.calcular_puerta(
                    elem.ancho, elem.alto,
                    elem.tipo_cristal_sup, elem.tipo_cristal_inf
                )
            else:
                materiales = calculadora.calcular_ventana(
                    elem.ancho, elem.alto, elem.tipo_cristal_sup
                )
            
            for tipo, medidas in materiales['perfiles'].items():
                if tipo not in todas_piezas_perfiles:
                    todas_piezas_perfiles[tipo] = []
                for m in medidas:
                    for _ in range(elem.cantidad):
                        todas_piezas_perfiles[tipo].append(m)
            
            for c in materiales['cristales']:
                for _ in range(c['cantidad'] * elem.cantidad):
                    todas_piezas_cristales.append({
                        'tipo': c['tipo'],
                        'ancho': c['ancho'],
                        'alto': c['alto'],
                        'cantidad': 1
                    })
        
        if self.tab_actual == 'perfiles':
            self.mostrar_perfiles(todas_piezas_perfiles, app)
        else:
            self.mostrar_cristales(todas_piezas_cristales, app)
    
    def mostrar_perfiles(self, todas_piezas_perfiles, app):
        optimizador = OptimizadorPerfiles(app.config)
        
        for tipo_perfil, piezas in todas_piezas_perfiles.items():
            barras = optimizador.optimizar(piezas)
            
            card = DarkCard()
            card.add_widget(DarkLabel(
                text=f'🔹 {tipo_perfil}',
                font_size=dp(16),
                bold=True
            ))
            card.add_widget(DarkLabel(
                text=f'Barras necesarias: {len(barras)}',
                color=(0.129, 0.588, 0.953, 1)
            ))
            
            for i, barra in enumerate(barras):
                sobrante = optimizador.calcular_sobrante(barra)
                card.add_widget(DarkLabel(
                    text=f'  Barra {i+1}: {barra} | Sobrante: {sobrante:.1f}cm',
                    font_size=dp(12)
                ))
            
            self.contenido.add_widget(card)
    
    def mostrar_cristales(self, todas_piezas_cristales, app):
        # Agrupar por tipo
        cristales_por_tipo = {}
        for c in todas_piezas_cristales:
            key = c['tipo']
            if key not in cristales_por_tipo:
                cristales_por_tipo[key] = []
            cristales_por_tipo[key].append(c)
        
        optimizador = OptimizadorCristales(app.config)
        
        for tipo_cristal, lista in cristales_por_tipo.items():
            piezas_opt = [{'ancho': c['ancho'], 'alto': c['alto'], 'cantidad': 1} for c in lista]
            
            if tipo_cristal == 'enchape':
                ancho_plancha = app.config.ancho_plancha_enchape
                alto_plancha = app.config.alto_plancha_enchape
            else:
                ancho_plancha = app.config.ancho_plancha_cristal
                alto_plancha = app.config.alto_plancha_cristal
            
            resultado = optimizador.optimizar(piezas_opt, ancho_plancha, alto_plancha)
            
            card = DarkCard()
            card.add_widget(DarkLabel(
                text=f'🔹 {tipo_cristal.upper()}',
                font_size=dp(16),
                bold=True
            ))
            card.add_widget(DarkLabel(
                text=f'Planchas necesarias: {resultado["total_hojas"]}',
                color=(0.129, 0.588, 0.953, 1)
            ))
            card.add_widget(DarkLabel(
                text=f'Dimensiones: {ancho_plancha}×{alto_plancha} cm',
                font_size=dp(12)
            ))
            
            # Visualización de planchas
            for i in range(resultado['total_hojas']):
                piezas_hoja = [p for p in resultado['piezas'] if p['hoja_idx'] == i]
                
                card.add_widget(DarkLabel(
                    text=f'Plancha #{i+1} - {len(piezas_hoja)} piezas',
                    font_size=dp(14)
                ))
                
                # Info de piezas
                for p in piezas_hoja:
                    card.add_widget(DarkLabel(
                        text=f'  {p["w"]:.1f}×{p["h"]:.1f} cm',
                        font_size=dp(11)
                    ))
            
            self.contenido.add_widget(card)

# ============================================
# APP PRINCIPAL
# ============================================

class CorteOptimoApp(App):
    def build(self):
        self.gestor = GestorDatos()
        self.config = self.gestor.cargar_config()
        self.proyecto_actual = None
        self.elementos_temp = []
        
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(ProyectosScreen(name='proyectos'))
        sm.add_widget(ProyectoEditScreen(name='proyecto_edit'))
        sm.add_widget(ElementoFormScreen(name='elemento_form'))
        sm.add_widget(ResultadosScreen(name='resultados'))
        
        return sm

if __name__ == '__main__':
    CorteOptimoApp().run()
