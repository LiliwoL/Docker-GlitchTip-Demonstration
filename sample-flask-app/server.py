from flask import Flask, jsonify
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import logging

# Initialiser Sentry/GlitchTip
sentry_sdk.init(
    dsn="http://28ee25200f04412b9f6d7d4140948973@localhost:8000/2",
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
    </ul>
    """

@app.route('/debug-glitchtip')
def trigger_error():
    logger.error("Erreur de division par zéro")
    division_by_zero = 1 / 0

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
    app.run(debug=True, port=5000)
