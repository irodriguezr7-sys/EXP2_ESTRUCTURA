"""Ejercicios de la sección 15 de la guía.

Se ejecuta aparte del menú:  python practica.py

Los ejercicios 6, 8 y 10 modifican el proyecto, así que viven dentro de
models.py, views.py y main.py (están marcados con "EJERCICIO n").
Aquí solo se prueban.
"""
from models import Cliente, Producto, Venta, Proveedor
from views import ClienteController


# ---------------------------------------------------------------------
# SOBRE COLECCIONES
# ---------------------------------------------------------------------
def ejercicio_1():
    # Quitar duplicados conservando el orden
    ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]
    vistas = set()      # conjunto de control: para preguntar rápido si ya apareció
    unicas = []         # lista de resultado: conserva el orden
    for ciudad in ciudades:
        if ciudad not in vistas:
            vistas.add(ciudad)
            unicas.append(ciudad)
    print(unicas)   # ['Quito', 'Guayaquil', 'Cuenca']


def ejercicio_2():
    # Contar con un diccionario
    ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]
    conteo = {}
    for ciudad in ciudades:
        conteo[ciudad] = conteo.get(ciudad, 0) + 1     # .get evita el KeyError la primera vez
    print(conteo)
    # El más repetido:
    mas_repetida = max(conteo, key=conteo.get)
    print(mas_repetida)


def ejercicio_3():
    # Conjuntos en acción
    inscritos_matematica = {"Ana", "Luis", "Sol", "Marco"}
    inscritos_ingles = {"Luis", "Marco", "Ruth"}
    ambas = inscritos_matematica & inscritos_ingles          # {'Luis','Marco'}
    solo_mate = inscritos_matematica - inscritos_ingles      # {'Ana','Sol'}
    total = len(inscritos_matematica | inscritos_ingles)     # 5
    print(sorted(ambas), sorted(solo_mate), total)


def ejercicio_4():
    # De lista de diccionarios a índice
    clientes = [{"id": 1, "nombre": "Ana"}, {"id": 2, "nombre": "Luis"}]
    indice = {cliente["id"]: cliente for cliente in clientes}
    print(indice[2]["nombre"])       # 'Luis'
    # Diferencia de costo:
    # recorrer la lista  -> revisa hasta N registros
    # indice[2]          -> una sola operación, sin importar cuántos haya


def ejercicio_5():
    # Tuplas como registros inmutables
    ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)]
    total = sum(monto for _mes, monto in ventas)
    mejor_mes, mejor_monto = max(ventas, key=lambda venta: venta[1])
    print(f"Total: {total}")
    print(f"Mejor mes: {mejor_mes} con {mejor_monto}")
    for mes, monto in ventas:              # desempaquetado en el for
        print(f"{mes:<10} {monto}")


def ejercicio_6():
    # Sobre el proyecto: clientes_por_ciudad() está en ClienteController (views.py)
    # y en el menú Clientes, opción 7. Lee data/clientes.json.
    controlador = ClienteController()
    agrupados = controlador.clientes_por_ciudad()
    if not agrupados:
        print("No hay clientes todavía: créelos en main.py")
    for ciudad, nombres in agrupados.items():
        print(f"{ciudad}: {nombres}")


# ---------------------------------------------------------------------
# SOBRE HERENCIA, POLIMORFISMO Y LO ESTÁTICO
# ---------------------------------------------------------------------
def ejercicio_7():
    # ¿Instancia, de clase o estático?
    respuestas = {
        "(a) calcular el total de una venta": "De instancia: usa self.cantidad y self.precio_unitario de ESA venta.",
        "(b) crear un Producto desde un diccionario": "De clase: no hay objeto todavía, lo fabrica con return cls(...). Es desde_diccionario().",
        "(c) saber si un precio es válido": "Estático: la regla 'mayor a 0' no depende de ningún producto concreto.",
        "(d) saber si un producto tiene stock bajo": "De instancia: compara self.stock con el atributo estático STOCK_MINIMO.",
        "(e) calcular el IVA de cualquier monto": "Estático: recibe un monto cualquiera y devuelve otro.",
    }
    for caso, respuesta in respuestas.items():
        print(f"{caso}\n    -> {respuesta}")


def ejercicio_8():
    # Un modelo nuevo con herencia: Proveedor (está en models.py)
    # desde_diccionario() ya funciona sin escribir nada
    p = Proveedor.desde_diccionario({"id": 1, "nombre": "Luis", "apellido": "Mora",
                                     "email": "luis@x.com", "ruc": "0912345678001",
                                     "empresa": "Importadora Sur"})
    print(p)     # usa __str__ de ModeloBase -> etiqueta() de Proveedor


def describir(objeto):
    # Ejercicio 9: cada clase ya sabe describirse, solo hay que preguntarle.
    return objeto.etiqueta()


def ejercicio_9():
    # Polimorfismo sin if
    cliente = Cliente(1, "Ana", "Pérez", "ana@x.com", "0999999999", "Quito")
    producto = Producto(1, "Teclado", 25.5, 10)
    venta = Venta(1, 1, 1, 2, 25.5)
    for objeto in (cliente, producto, venta):
        print(describir(objeto))
    print(venta)     # __str__ de ModeloBase llama a etiqueta()


def ejercicio_10():
    # Atributo estático nuevo: Producto.DESCUENTO_MAYORISTA y precio_mayorista()
    # (están en models.py y se usan en VentaController.crear de views.py)
    print(Producto.precio_mayorista(10, 5))     # 10    (menos de 12: sin descuento)
    print(Producto.precio_mayorista(10, 12))    # 9.0   (12 o más: 10 % de descuento)


if __name__ == "__main__":
    for numero, ejercicio in enumerate(
        (ejercicio_1, ejercicio_2, ejercicio_3, ejercicio_4, ejercicio_5,
         ejercicio_6, ejercicio_7, ejercicio_8, ejercicio_9, ejercicio_10), start=1
    ):
        print(f"\n--- Ejercicio {numero} ---")
        ejercicio()
