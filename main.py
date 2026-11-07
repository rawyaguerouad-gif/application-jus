from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def afficher_formulaire():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Calcul du procédé du jus</title>
    </head>
    <body>
        <h1>Modélisation du procédé du jus</h1>
        <p>Entrez les données du procédé. Les fractions sont des nombres
        décimaux : 10 % s'écrit 0.10.</p>

        <form action="/calculer" method="get">
            <label>Débit de jus brut (kg/h) :
                <input type="number" name="m0" value="1000" step="any">
            </label>
            <br><br>

            <label>Fraction insoluble (2 % = 0.02) :
                <input type="number" name="x0" value="0.02"
                       step="any" min="0" max="1">
            </label>
            <br><br>

            <label>Fraction soluble (10 % = 0.10) :
                <input type="number" name="y0" value="0.10"
                       step="any" min="0" max="1">
            </label>
            <br><br>

            <label>Débit de jus concentré ajouté (kg/h) :
                <input type="number" name="mR" value="100" step="any">
            </label>
            <br><br>

            <label>Fraction soluble du jus ajouté (40 % = 0.40) :
                <input type="number" name="yR" value="0.40"
                       step="any" min="0" max="1">
            </label>
            <br><br>

            <label>Température d'entrée (°C) :
                <input type="number" name="T2" value="20" step="any">
            </label>
            <br><br>

            <label>Température après chauffage (°C) :
                <input type="number" name="T3" value="80" step="any">
            </label>
            <br><br>

            <button type="submit">Calculer</button>
        </form>
    </body>
    </html>
    """


@app.get("/calculer", response_class=HTMLResponse)
def calculer(
    m0: float = 1000,
    x0: float = 0.02,
    y0: float = 0.10,
    mR: float = 100,
    yR: float = 0.40,
    T2: float = 20,
    T3: float = 80,
):
    # Vérifications simples pour éviter des données impossibles
    if m0 <= 0 or mR < 0:
        return "<h1>Erreur</h1><p>Les débits saisis ne sont pas valides.</p>"

    if not (0 <= x0 <= 1 and 0 <= y0 <= 1 and 0 <= yR <= 1):
        return "<h1>Erreur</h1><p>Les fractions doivent être entre 0 et 1.</p>"

    if x0 + y0 > 1:
        return "<h1>Erreur</h1><p>Les fractions insoluble et soluble dépassent 100 %.</p>"

    # 1. Filtration : les insolubles sont retirés
    residus = m0 * x0
    m1 = m0 - residus

    # Les matières solubles restent dans le jus
    solubles1 = m0 * y0
    y1 = solubles1 / m1

    # 2. Mélange avec le jus concentré ajouté
    m2 = m1 + mR
    solubles2 = solubles1 + mR * yR
    y2 = solubles2 / m2

    # 3. Chauffage : le résultat est en kW
    cp = 3.8
    q3 = m2 * cp * (T3 - T2) / 3600

    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Résultats</title>
    </head>
    <body>
        <h1>Résultats des calculs</h1>

        <h2>Après filtration</h2>
        <p>Débit filtré : {m1:.2f} kg/h</p>
        <p>Débit de résidus insolubles : {residus:.2f} kg/h</p>
        <p>Fraction soluble : {y1 * 100:.2f} %</p>

        <h2>Après mélange</h2>
        <p>Débit du mélange : {m2:.2f} kg/h</p>
        <p>Matières solubles : {solubles2:.2f} kg/h</p>
        <p>Fraction soluble du mélange : {y2 * 100:.2f} %</p>

        <h2>Chauffage</h2>
        <p>Puissance nécessaire : {q3:.2f} kW</p>

        <p><a href="/">Revenir au formulaire</a></p>
    </body>
    </html>
    """
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)