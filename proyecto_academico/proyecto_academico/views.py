from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
# Solo dice QUÉ métodos debe tener todo controlador.
# CÓMO se hace cada uno lo escribe cada controlador, de la forma más simple.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE ESTUDIANTES
# =====================================================================
class EstudianteController(CrudBase):

    # TUPLA: los campos donde se busca son fijos, por eso no es una lista
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet", "carrera")

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)

        # Leemos el JSON y convertimos cada diccionario en un objeto Estudiante
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for estudiante in self.lista:
            datos.append(estudiante.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Devuelve un mensaje de error, o None si todo está bien."""
        # Al crear hay que traer los cuatro obligatorios; al actualizar, solo lo que cambia
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO con los emails de los OTROS estudiantes: preguntar 'in' es instantáneo
            usados = {e.email for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            if carnet == "":
                return "El carnet no puede quedar vacío"
            # CONJUNTO de carnets ya usados: el carnet debe ser único
            carnets = {e.carnet for e in self.lista if e.id != id_actual}
            if carnet in carnets:
                return f"El carnet {carnet} ya está registrado"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for estudiante in self.lista:
            for campo in self.CAMPOS_BUSCABLES:        # recorro la TUPLA de campos
                if texto in str(getattr(estudiante, campo)).lower():
                    encontrados.append(estudiante)
                    break                              # ya coincidió: paso al siguiente
        return encontrados

    def siguiente(self):
        mayor = 0
        for estudiante in self.lista:
            if estudiante.id > mayor:
                mayor = estudiante.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error      # TUPLA (exito, mensaje): devuelve dos valores juntos

        estudiante = Estudiante(self.siguiente(),
                                str(datos["nombre"]).strip().title(),
                                str(datos["apellido"]).strip().title(),
                                str(datos["email"]).strip().lower(),
                                str(datos["carnet"]).strip().upper(),
                                str(datos.get("carrera", "")).strip().title())
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        # DIFERENCIA de conjuntos: campos que no existen en un estudiante
        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        # Se valida ANTES de tocar el objeto: si algo falla, no cambia nada
        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    # --- propio de estudiantes ---
    def carreras(self):
        """CONJUNTO de carreras: sin repetidos. sorted() lo devuelve como lista."""
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


# =====================================================================
# CONTROLADOR DE MATERIAS
# =====================================================================
class MateriaController(CrudBase):

    # TUPLA: campos donde se busca (fijos)
    CAMPOS_BUSCABLES = ("nombre", "codigo")

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for materia in self.lista:
            datos.append(materia.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo", "creditos", "cupos"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            if codigo == "":
                return "El código no puede quedar vacío"
            # CONJUNTO de códigos de las OTRAS materias: el código debe ser único
            codigos = {m.codigo for m in self.lista if m.id != id_actual}
            if codigo in codigos:
                return f"El código {codigo} ya está registrado"

        if "nombre" in datos and str(datos["nombre"]).strip() == "":
            return "El nombre no puede quedar vacío"

        if "creditos" in datos:
            creditos = str(datos["creditos"]).strip()
            if not creditos.isdigit() or not 1 <= int(creditos) <= 10:
                return "Los créditos deben ser un número entero entre 1 y 10"

        if "cupos" in datos:
            cupos = str(datos["cupos"]).strip()
            if not cupos.isdigit() or int(cupos) > Materia.CUPOS_MAXIMOS:
                return f"Los cupos deben ser un entero entre 0 y {Materia.CUPOS_MAXIMOS}"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for materia in self.lista:
            for campo in self.CAMPOS_BUSCABLES:        # recorro la TUPLA de campos
                if texto in str(getattr(materia, campo)).lower():
                    encontrados.append(materia)
                    break
        return encontrados

    def siguiente(self):
        mayor = 0
        for materia in self.lista:
            if materia.id > mayor:
                mayor = materia.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        materia = Materia(self.siguiente(),
                          str(datos["nombre"]).strip().title(),
                          str(datos["codigo"]).strip().upper(),
                          int(datos["creditos"]),
                          int(datos["cupos"]))
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"

        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    # --- propio de materias ---
    def materias_sin_cupo(self):
        sin_cupo = []
        for materia in self.lista:
            if not materia.hay_cupo():
                sin_cupo.append(materia)
        return sin_cupo


# =====================================================================
# CONTROLADOR DE MATRÍCULAS
# =====================================================================
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        # La matrícula USA a los otros dos controladores.
        # Hay que pasarle los MISMOS que usa main.py.
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for matricula in self.lista:
            datos.append(matricula.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números enteros"

        periodo = str(datos.get("periodo", "")).strip()
        if periodo == "":
            return "El periodo es obligatorio (ej: 2026-1)"

        # CONJUNTOS de ids existentes: saber si un id existe es instantáneo
        ids_estudiantes = {e.id for e in self.estudiantes.leer()}
        ids_materias = {m.id for m in self.materias.leer()}
        if estudiante_id not in ids_estudiantes:
            return f"No existe un estudiante con id {estudiante_id}"
        if materia_id not in ids_materias:
            return f"No existe una materia con id {materia_id}"

        # No matricular dos veces: se comparan estudiante, materia y periodo JUNTOS
        for matricula in self.lista:
            if (matricula.estudiante_id, matricula.materia_id, matricula.periodo) == \
                    (estudiante_id, materia_id, periodo):
                return "Ese estudiante ya está matriculado en esa materia en ese periodo"

        materia = self.materias.obtener(materia_id)
        if not materia.hay_cupo():
            return f"La materia {materia.nombre} no tiene cupos disponibles"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for matricula in self.lista:
            if matricula.id == id_matricula:
                return matricula
        return None

    def buscar(self, texto):
        # Las matrículas se buscan por periodo, ej: "2026-1"
        texto = texto.strip()
        encontradas = []
        if texto == "":
            return encontradas

        for matricula in self.lista:
            if texto in matricula.periodo:
                encontradas.append(matricula)
        return encontradas

    def siguiente(self):
        mayor = 0
        for matricula in self.lista:
            if matricula.id > mayor:
                mayor = matricula.id
        return mayor + 1

    def crear(self, datos):
        # datos = {"estudiante_id": 1, "materia_id": 2, "periodo": "2026-1"}
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = self.estudiantes.obtener(int(datos["estudiante_id"]))
        materia = self.materias.obtener(int(datos["materia_id"]))
        matricula = Matricula(self.siguiente(),
                              estudiante.id,
                              materia.id,
                              str(datos["periodo"]).strip())

        materia.ocupar_cupo()
        self.materias.guardar()                 # guarda el cupo nuevo en materias.json
        self.lista.append(matricula)
        self.guardar()                          # guarda la matrícula en matriculas.json
        return True, (f"Matrícula {matricula.id} registrada: "
                      f"{estudiante.nombre_completo()} en {materia.nombre}")

    def actualizar(self, id_matricula, datos):
        # Una matrícula no se modifica: se registra la nota o se retira la matrícula
        return False, "Las matrículas no se modifican: registre la nota o retírela"

    def eliminar(self, id_matricula):
        """Retirar una matrícula: se borra y el cupo vuelve a la materia."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula {id_matricula} retirada y cupo liberado"

    # --- propio de matrículas ---
    def registrar_nota(self, id_matricula, nota):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"
        # es_nota_valida es el método ESTÁTICO de Materia
        if not Materia.es_nota_valida(nota):
            return False, f"Nota inválida: '{nota}' (debe ser un número entre 0 y 20)"

        matricula.nota = float(nota)
        self.guardar()
        return True, f"Nota {matricula.nota:g} registrada: {matricula.estado()}"

    def certificado(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None

        # DICCIONARIOS ÍNDICE {id: objeto}: encuentro cada dato sin recorrer listas
        indice_estudiantes = {e.id: e for e in self.estudiantes.leer()}
        indice_materias = {m.id: m for m in self.materias.leer()}
        estudiante = indice_estudiantes.get(matricula.estudiante_id)
        materia = indice_materias.get(matricula.materia_id)

        nota = "sin registrar" if matricula.nota is None else f"{matricula.nota:g}"
        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        if estudiante:
            texto += f"Estudiante: {estudiante.nombre_completo()}   ({estudiante.carnet})\n"
        else:
            texto += "Estudiante: eliminado\n"
        if materia:
            texto += f"Materia   : {materia.nombre}   ({materia.codigo}) · {materia.creditos} créditos\n"
        else:
            texto += "Materia   : eliminada\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {nota}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        """DICCIONARIO de LISTAS: {estudiante_id: [matrículas de ese estudiante]}."""
        agrupadas = {}
        for matricula in self.lista:
            # setdefault: si el estudiante no estaba, crea la lista vacía y luego agrega
            agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        """Promedio de las notas ya registradas de un estudiante (None si no tiene)."""
        notas = []
        for matricula in self.matriculas_por_estudiante().get(id_estudiante, []):
            if matricula.nota is not None:
                notas.append(matricula.nota)
        if not notas:
            return None
        return round(sum(notas) / len(notas), 2)

    def total_aprobadas(self):
        total = 0
        for matricula in self.lista:
            if matricula.esta_aprobada():
                total += 1
        return total
