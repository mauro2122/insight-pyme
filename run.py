# run.py  (en la carpeta raíz)
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Si luego quieres que sea visible desde otros equipos usa host="0.0.0.0"
    app.run(debug=True)  # puerto por defecto: 5000
