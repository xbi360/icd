from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Configuración de la conexión a MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://lm:lm@localhost/gestor_tareas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definir el modelo actualizado
class Tarea(db.Model):
    __tablename__ = 'tareas'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    completada = db.Column(db.Boolean, default=False)  # Nuevo campo para el estado

@app.route('/')
def index():
    lista_tareas = Tarea.query.all()
    return render_template('index.html', tareas=lista_tareas)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre_tarea = request.form['nom']
    desc_tarea = request.form['descripcion']
    
    nueva_tarea = Tarea(nom=nombre_tarea, descripcion=desc_tarea, completada=False)
    db.session.add(nueva_tarea)
    db.session.commit()
    
    return redirect(url_for('index'))

# Nueva ruta para alternar el estado (marcar/desmarcar)
@app.route('/completar/<int:id>')
def completar(id):
    tarea = Tarea.query.get_or_404(id)
    # Cambia el estado actual al contrario (True pasa a False, y viceversa)
    tarea.completada = not tarea.completada
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    tarea_a_eliminar = Tarea.query.get_or_404(id)
    db.session.delete(tarea_a_eliminar)
    db.session.commit()
    
    # Comprobamos si la tabla se quedó sin registros
    if Tarea.query.count() == 0:
        db.session.execute(text("ALTER TABLE tareas AUTO_INCREMENT = 1"))
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="192.168.10.5", debug=True, port=5000)
