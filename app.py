from flask import Flask, render_template, request, redirect
import csv
import os
import random

app = Flask(__name__)

ADMIN_PASSWORD = "moc"  # cámbiala si quieres


# ---------------------------
# Cargar lista de nombres
# ---------------------------
def cargar_familia():
    with open('familia.csv', newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row['nombre'] for row in reader]


# ---------------------------
# Cargar asignaciones
# ---------------------------
def cargar_asignaciones():
    asignados = {}
    if os.path.exists('asignaciones.csv'):
        with open('asignaciones.csv', newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                asignados[row['persona']] = row['asignado']
    return asignados


# ---------------------------
# Guardar asignaciones
# ---------------------------
def guardar_asignaciones(asignados):
    with open('asignaciones.csv', 'w', newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=['persona', 'asignado'])
        writer.writeheader()
        for persona, asignado in asignados.items():
            writer.writerow({'persona': persona, 'asignado': asignado})


# ---------------------------
#    PANTALLA PRINCIPAL
# ---------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    familia = cargar_familia()

    if request.method == 'POST':
        persona = request.form.get('persona')
        excluidos = request.form.getlist('excluir')

        asignados = cargar_asignaciones()

        # Si ya tiene asignación → se muestra
        if persona in asignados:
            return render_template(
                "resultado.html",
                resultado=f"Ya te tocó: {asignados[persona]}"
            )

        # Generar lista de candidatos
        posibles = [
            f for f in familia
            if f != persona
            and f not in excluidos
            and f not in asignados.values()
        ]

        if not posibles:
            return render_template(
                "resultado.html",
                resultado="No hay personas disponibles. Prueba quitando exclusiones."
            )

        random.shuffle(posibles)
        elegido = posibles[0]

        # Guardar
        asignados[persona] = elegido
        guardar_asignaciones(asignados)

        return render_template("resultado.html", resultado=f"Te ha tocado: {elegido}")

    return render_template("index.html", familia=familia)


# ---------------------------
#        ADMIN
# ---------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    asignaciones = cargar_asignaciones()

    if request.method == 'POST':
        password = request.form.get('password')
        accion = request.form.get('accion')

        if password != ADMIN_PASSWORD:
            return render_template(
                "admin.html",
                error="Contraseña incorrecta.",
                asignaciones={},
                mostrar=False
            )

        if accion == "ver":
            return render_template(
                "admin.html",
                asignaciones=asignaciones,
                mostrar=True,
                mensaje="Asignaciones actuales:"
            )

        if accion == "reiniciar":
            if os.path.exists('asignaciones.csv'):
                os.remove('asignaciones.csv')
            return render_template(
                "admin.html",
                mostrar=False,
                mensaje="Sorteo reiniciado correctamente.",
                asignaciones={}
            )

    return render_template("admin.html", mostrar=False, asignaciones={})


if __name__ == '__main__':
    app.run(debug=True)
