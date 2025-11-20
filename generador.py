import random
import json
import time
from datetime import datetime

class GeneradorCasosPrueba:
    """Generador automático de casos de prueba desde gramática libre de contexto."""
    
    TIPOS_MUTACION = ["eliminar", "duplicar", "insertar", "reemplazar"]
    TOKENS_BASURA = ["+", "*", "(", ")", "ERROR", "##", "??", "NULL"]
    
    def __init__(self):
        self.gramatica = {}
        self.resultados = []
        self.estadisticas = {"valida": 0, "invalida": 0, "extrema": 0}
        self.tiempo_inicio = 0
        self.tiempos_por_tipo = {"valida": [], "invalida": [], "extrema": []}
        self.config = {
            "prof_max": 5,
            "long_max": 50,
            "dist_valida": 50,
            "dist_invalida": 30
        }
        
    def cargar_gramatica(self, nombre_archivo):
        """Carga gramática desde archivo .txt"""
        self.gramatica = {}
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea or "->" not in linea:
                        continue
                    
                    izq, der = linea.split("->", 1)
                    clave = izq.strip()
                    opciones = [op.strip().split() for op in der.split("|")]
                    self.gramatica[clave] = opciones
            return bool(self.gramatica)
        except FileNotFoundError:
            return False
    
    def derivar(self, simbolo, prof_actual=0):
        """Deriva recursivamente desde un símbolo. Retorna cadena."""
        if simbolo not in self.gramatica:
            return simbolo
        
        prof_max = self.config["prof_max"]
        
        # Evitar recursión infinita
        if prof_actual >= prof_max:
            opciones = [op for op in self.gramatica[simbolo] if simbolo not in op]
            produccion = random.choice(opciones) if opciones else ["id"]
        else:
            produccion = random.choice(self.gramatica[simbolo])
        
        return " ".join(self.derivar(s, prof_actual + 1) for s in produccion)
    
    def generar_valida(self):
        """Genera cadena válida según gramática."""
        cadena = self.derivar("E")
        tokens = cadena.split()
        
        # Validar longitud máxima
        if len(tokens) > self.config["long_max"]:
            tokens = tokens[:self.config["long_max"]]
        
        return " ".join(tokens)
    
    def generar_invalida(self):
        """Genera cadena inválida por mutación sintáctica."""
        cadena = self.generar_valida()
        tokens = cadena.split()
        
        if not tokens:
            return "id +", "fallback"
        
        tipo = random.choice(self.TIPOS_MUTACION)
        idx = random.randint(0, len(tokens) - 1)
        
        mutaciones = {
            "eliminar": lambda: tokens.pop(idx) or tokens,
            "duplicar": lambda: tokens.insert(idx, tokens[idx]) or tokens,
            "insertar": lambda: tokens.insert(idx, random.choice(self.TOKENS_BASURA)) or tokens,
            "reemplazar": lambda: tokens.__setitem__(idx, random.choice(["??", "ERROR", "NULL"])) or tokens
        }
        
        mutaciones[tipo]()
        return " ".join(tokens), tipo
    
    def generar_extrema(self):
        """Genera caso extremo con profundidad o longitud agresiva."""
        criterio = random.choice(["profundidad", "longitud"])
        self.config["prof_max"] = 20 if criterio == "profundidad" else 15
        cadena = self.generar_valida()
        self.config["prof_max"] = 5  # Restaurar
        return cadena, criterio
    
    def analizar_cadena(self, cadena):
        """Extrae métricas de una cadena generada."""
        tokens = cadena.split()
        operadores = {op: tokens.count(op) for op in ["+", "-", "*", "/"]}
        
        prof_max = prof_actual = 0
        for t in tokens:
            if t == "(":
                prof_actual += 1
                prof_max = max(prof_max, prof_actual)
            elif t == ")":
                prof_actual -= 1
        
        return {
            "longitud_tokens": len(tokens),
            "profundidad_estimada": prof_max,
            "conteo_operadores": operadores,
            "nivel_anidamiento": prof_max
        }
    
    def clasificar_automatico(self, cadena, tipo_generado):
        """Clasifica automáticamente una cadena generada."""
        metricas = self.analizar_cadena(cadena)
        tokens = cadena.split()
        
        # Validación básica de estructura
        parentesis_balance = tokens.count("(") == tokens.count(")")
        tiene_tokens_invalidos = any(t in self.TOKENS_BASURA for t in tokens)
        
        clasificacion = {
            "tipo_declarado": tipo_generado,
            "parentesis_balanceados": parentesis_balance,
            "contiene_tokens_invalidos": tiene_tokens_invalidos,
            "es_extremo": metricas["longitud_tokens"] > 30 or metricas["profundidad_estimada"] > 10
        }
        
        return clasificacion
    
    def generar_casos(self, cantidad):
        """Genera todos los casos según configuración."""
        self.resultados = []
        self.estadisticas = {"valida": 0, "invalida": 0, "extrema": 0}
        self.tiempos_por_tipo = {"valida": [], "invalida": [], "extrema": []}
        self.tiempo_inicio = time.time()
        
        for i in range(cantidad):
            inicio = time.time()
            r = random.random() * 100
            dist_v = self.config["dist_valida"]
            dist_i = self.config["dist_invalida"]
            
            # Determinar tipo y generar
            if r < dist_v:
                tipo, cadena, meta = "valida", self.generar_valida(), "derivacion_directa"
            elif r < dist_v + dist_i:
                tipo = "invalida"
                cadena, meta = self.generar_invalida()
            else:
                tipo = "extrema"
                cadena, meta = self.generar_extrema()
            
            tiempo = time.time() - inicio
            self.tiempos_por_tipo[tipo].append(tiempo)
            self.estadisticas[tipo] += 1
            
            caso = {
                "id": i + 1,
                "tipo": tipo,
                "cadena": cadena,
                "detalle_generacion": meta,
                "metricas": self.analizar_cadena(cadena),
                "clasificacion": self.clasificar_automatico(cadena, tipo)
            }
            self.resultados.append(caso)
    
    def configurar(self, prof_max=5, long_max=50, dist_valida=50, dist_invalida=30):
        """Configura parámetros de generación."""
        self.config.update({
            "prof_max": prof_max,
            "long_max": long_max,
            "dist_valida": dist_valida,
            "dist_invalida": dist_invalida
        })
    
    def exportar_json(self, nombre_archivo):
        """Exporta casos a JSON."""
        with open(nombre_archivo, "w", encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=4, ensure_ascii=False)
    
    def generar_reporte(self):
        """Genera reporte estadístico completo."""
        if not self.resultados:
            return {}
        
        total = len(self.resultados)
        tiempo_total = time.time() - self.tiempo_inicio
        
        longitudes = [r["metricas"]["longitud_tokens"] for r in self.resultados]
        profundidades = [r["metricas"]["profundidad_estimada"] for r in self.resultados]
        
        operadores_total = {op: 0 for op in ["+", "-", "*", "/"]}
        mutaciones_por_tipo = {}
        
        for r in self.resultados:
            for op, count in r["metricas"]["conteo_operadores"].items():
                operadores_total[op] += count
            
            if r["tipo"] == "invalida" and r["detalle_generacion"] != "N/A":
                tipo_mut = r["detalle_generacion"]
                mutaciones_por_tipo[tipo_mut] = mutaciones_por_tipo.get(tipo_mut, 0) + 1
        
        tiempos_prom = {t: (sum(ts)/len(ts) if ts else 0) for t, ts in self.tiempos_por_tipo.items()}
        
        return {
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_casos": total,
            "distribucion_porcentual": {
                f"{k}s": f"{(v/total)*100:.2f}%" for k, v in self.estadisticas.items()
            },
            "distribucion_numerica": self.estadisticas,
            "longitud_promedio_tokens": sum(longitudes) / total,
            "longitud_maxima_tokens": max(longitudes),
            "profundidad_maxima_arbol": max(profundidades),
            "profundidad_promedio_arbol": sum(profundidades) / total,
            "nivel_anidamiento_promedio": sum(r["metricas"]["nivel_anidamiento"] for r in self.resultados) / total,
            "operadores_generados_total": operadores_total,
            "mutaciones_aplicadas": mutaciones_por_tipo,
            "tiempo_ejecucion_total_segundos": round(tiempo_total, 4),
            "tiempo_promedio_por_tipo_segundos": {k: round(v, 4) for k, v in tiempos_prom.items()},
            "configuracion_usada": self.config
        }
    
    def exportar_reporte_txt(self, nombre_archivo):
        """Exporta reporte en texto legible."""
        reporte = self.generar_reporte()
        
        with open(nombre_archivo, "w", encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("   REPORTE ESTADÍSTICO - GENERADOR DE CASOS DE PRUEBA\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Fecha: {reporte['fecha_generacion']}\n")
            f.write(f"Total: {reporte['total_casos']} casos\n\n")
            
            f.write("DISTRIBUCIÓN\n" + "-"*70 + "\n")
            for tipo, porc in reporte['distribucion_porcentual'].items():
                num = reporte['distribucion_numerica'][tipo.replace('s', '')]
                f.write(f"  {tipo.capitalize()}: {num} ({porc})\n")
            
            f.write("\nMÉTRICAS\n" + "-"*70 + "\n")
            f.write(f"  Longitud promedio: {reporte['longitud_promedio_tokens']:.2f} tokens\n")
            f.write(f"  Longitud máxima: {reporte['longitud_maxima_tokens']} tokens\n")
            f.write(f"  Profundidad máxima: {reporte['profundidad_maxima_arbol']}\n")
            f.write(f"  Profundidad promedio: {reporte['profundidad_promedio_arbol']:.2f}\n")
            f.write(f"  Nivel anidamiento promedio: {reporte['nivel_anidamiento_promedio']:.2f}\n")
            
            f.write("\nOPERADORES\n" + "-"*70 + "\n")
            for op, count in reporte['operadores_generados_total'].items():
                f.write(f"  {op}: {count}\n")
            
            if reporte['mutaciones_aplicadas']:
                f.write("\nMUTACIONES\n" + "-"*70 + "\n")
                for mut, count in reporte['mutaciones_aplicadas'].items():
                    f.write(f"  {mut}: {count}\n")
            
            f.write("\nTIEMPOS\n" + "-"*70 + "\n")
            f.write(f"  Total: {reporte['tiempo_ejecucion_total_segundos']}s\n")
            for tipo, tiempo in reporte['tiempo_promedio_por_tipo_segundos'].items():
                f.write(f"  {tipo}: {tiempo}s\n")
            
            f.write("\nCONFIGURACIÓN\n" + "-"*70 + "\n")
            for k, v in reporte['configuracion_usada'].items():
                f.write(f"  {k}: {v}\n")
            
            f.write("\n" + "="*70 + "\n")