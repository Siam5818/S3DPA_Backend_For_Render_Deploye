from app.routes import (
    auth_routes,
    capteur_routes,
    medecin_routes,
    patient_routes,
    proche_routes,
    alerte_routes,
    donnees_medicales_route
)

def register_routes(app):
    app.register_blueprint(auth_routes.auth_bp)
    app.register_blueprint(capteur_routes.capteur_bp)
    app.register_blueprint(medecin_routes.medecin_bp)
    app.register_blueprint(patient_routes.patient_bp)
    app.register_blueprint(proche_routes.proche_bp)
    app.register_blueprint(alerte_routes.alerte_bp)
    app.register_blueprint(donnees_medicales_route.donnees_bp)
    