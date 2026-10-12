import requests

API = "http://127.0.0.1:5000"

usuario_actual = None


def registrarse():
    usuario = input("Usuario: ")
    contraseña = input("Contraseña: ")

    respuesta = requests.post(
        f"{API}/registro", json={"usuario": usuario, "contraseña": contraseña}
    )

    print(respuesta.status_code, respuesta.json())


def iniciar_sesion():
    global usuario_actual
    usuario = input("Usuario: ")
    contraseña = input("contraseña:")

    respuesta = requests.post(
        f"{API}/login", json={"usuario": usuario, "contraseña": contraseña}
    )

    print(respuesta.status_code, respuesta.json())

    if respuesta.status_code == 200:
        usuario_actual = usuario
        print(f"Sesión iniciada como {usuario}")


def crear_tarea():
    titulo = input("titulo: ")

    respuesta = requests.post(
        f"{API}/api/tareas", json={"usuario": usuario_actual, "titulo": titulo}
    )

    print(respuesta.status_code, respuesta.json())


def obtener_tareas():
    respuesta = requests.get(f"{API}/api/tareas", params={"usuario": usuario_actual})

    print(respuesta.status_code, respuesta.json())


def completar_tarea():
    id_tarea = input("id de la tarea: ")

    respuesta = requests.put(
        f"{API}/api/tareas/{id_tarea}", json={"usuario": usuario_actual}
    )

    print(respuesta.status_code, respuesta.json())


def borrar_tarea():
    id_tarea = input("Id de la tarea: ")

    respuesta = requests.delete(
        f"{API}/api/tareas/{id_tarea}", json={"usuario": usuario_actual}
    )

    print(respuesta.status_code, respuesta.json())


def main():
    while True:
        print("\nGESTOR DE TAREAS\n")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Crear tarea")
        print("4. Obtener tareas")
        print("5. Completar tarea")
        print("6. Borrar tarea")
        print("0. salir\n")

        opcion = input("Opción: ")

        if opcion == "1":
            registrarse()
        elif opcion == "2":
            iniciar_sesion()
        elif opcion in ("3", "4", "5", "6") and usuario_actual is None:
            print("Inicie sesión para utilizar esta función")
        elif opcion == "3":
            crear_tarea()
        elif opcion == "4":
            obtener_tareas()
        elif opcion == "5":
            completar_tarea()
        elif opcion == "6":
            borrar_tarea()
        elif opcion == "0":
            break
        else:
            print("Opción inválida")


if __name__ == "__main__":
    main()
