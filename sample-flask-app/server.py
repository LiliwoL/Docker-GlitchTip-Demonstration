from flask import Flask, jsonify, request, render_template_string
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import logging

#-----------------------------
# Lecture du .env
#-----------------------------

from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis un fichier .env à la racine du projet
load_dotenv()
# Récupérer la variable DSN qui sera utilisée pour initialiser Sentry
dsn = os.getenv("DSN")


#-----------------------------
# Initialiser Sentry/GlitchTip
#-----------------------------
sentry_sdk.init(
    dsn=dsn,
    integrations=[FlaskIntegration()]
)

app = Flask(__name__)

# Configurer le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    logger.info("Accès à la route principale")
    return """
    <h1>Bienvenue sur l'application Flask !</h1>
    <ul>
        <li><a href="/debug-glitchtip">Déclencher une erreur</a></li>
        <li><a href="/log-message">Enregistrer un message de log</a></li>
        <li><a href="/log-warning">Enregistrer un message d'avertissement</a></li>
        <li><a href="/log-error">Enregistrer une erreur</a></li>
        <li><a href="/admin-login">Connexion admin</a></li>
    </ul>
    """

@app.route('/debug-glitchtip')
def trigger_error():
    logger.error("Erreur de division par zéro")
    division_by_zero = 1 / 0


# Route d'authentification admin
# GET: affiche le formulaire
# POST: vérifie le mot de passe et journalise vers GlitchTip
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    form_html = '''
    <h2>Connexion Admin</h2>
    <form method="post">
      <label>Mot de passe: <input type="password" name="password"/></label>
      <button type="submit">Se connecter</button>
    </form>
    '''

    if request.method == 'GET':
        return render_template_string(form_html)

    # POST: vérifier le mot de passe
    password = request.form.get('password', '')
    remote = request.remote_addr or 'unknown'
    if password == 'azertysio':
        msg = f"Admin login successful from {remote}"
        logger.info(msg)
        sentry_sdk.capture_message(msg, level='info')
        return render_template_string('<p>Connexion réussie</p>')
    else:
        msg = f"Admin login failed from {remote}"
        logger.warning(msg)
        sentry_sdk.capture_message(msg, level='warning')
        return render_template_string('<p>Mot de passe incorrect</p>'), 401

@app.route('/log-message')
def log_message():
    logger.info("Ceci est un message de log d'information")
    return jsonify(message="Message de log enregistré")

@app.route('/log-warning')
def log_warning():
    logger.warning("Ceci est un message d'avertissement")
    sentry_sdk.capture_exception(ValueError("Ceci est un message d'avertissement"))
    return jsonify(message="Message d'avertissement enregistré")

@app.route('/log-error')
def log_error():
    try:
        # Simuler une erreur
        raise ValueError("Ceci est une erreur simulée")
    except ValueError as e:
        logger.error(f"Erreur capturée : {e}")
        sentry_sdk.capture_exception(e)
        return jsonify(message="Erreur enregistrée"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
