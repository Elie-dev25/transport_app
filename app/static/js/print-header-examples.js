/* ================== EXEMPLES D'UTILISATION EN-TÊTE D'IMPRESSION ================== */
/* Exemples d'utilisation de l'en-tête standardisé UDM pour différents types de documents */

/**
 * EXEMPLE 1: En-tête pour page de vidange
 */
function exempleVidange() {
    const header = createVidangeHeader(
        'Gestion des Vidanges',
        'Liste des véhicules nécessitant une vidange'
    );
    return header;
}

/**
 * EXEMPLE 2: En-tête pour rapport de transport
 */
function exempleRapportTransport() {
    const header = createRapportHeader(
        'Rapport Mensuel Transport',
        'Analyse des trajets effectués'
    );
    return header;
}

/**
 * EXEMPLE 3: En-tête pour maintenance
 */
function exempleMaintenance() {
    const header = createMaintenanceHeader(
        'Rapport de Dépannage',
        'Interventions techniques sur véhicules'
    );
    return header;
}

/**
 * EXEMPLE 4: En-tête administratif
 */
function exempleAdmin() {
    const header = createAdminHeader(
        'Rapport Administratif',
        'Gestion des utilisateurs et permissions'
    );
    return header;
}

/**
 * EXEMPLE 5: En-tête personnalisé avec toutes les options
 */
function exemplePersonnalise() {
    const header = generateUDMPrintHeader({
        documentTitle: 'Rapport Personnalisé',
        documentSubtitle: 'Analyse spécifique des données',
        serviceCode: 'DAARFM',
        serviceName: 'SERVICE PERSONNALISÉ',
        theme: 'transport',
        compact: false,
        showDate: true
    });
    return header;
}

/**
 * EXEMPLE 6: En-tête compact
 */
function exempleCompact() {
    const header = generateUDMPrintHeader({
        documentTitle: 'Rapport Compact',
        documentSubtitle: 'Version réduite',
        compact: true,
        theme: 'maintenance'
    });
    return header;
}

/**
 * EXEMPLE 7: Utilisation dans une fonction d'impression complète
 */
function exempleImpressionComplete() {
    // Créer l'en-tête
    const header = createTransportHeader(
        'Liste des Bus UDM',
        'État des véhicules universitaires'
    );
    
    // Récupérer le contenu du tableau
    const table = document.querySelector('#busTable');
    const tableClone = table ? table.cloneNode(true) : '<p>Aucun tableau trouvé</p>';
    
    // Créer le pied de page
    const footer = `
        <div class="print-footer">
            <p>Université des Montagnes - Système de Gestion de Transport</p>
        </div>
    `;
    
    // Assembler le document complet
    const fullDocument = `
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Liste des Bus UDM</title>
            <link rel="stylesheet" href="/static/css/print.css">
            <link rel="stylesheet" href="/static/css/print-header.css">
        </head>
        <body>
            ${header}
            <div class="table-container">
                <div class="table-container-header">
                    <h3>Liste des Véhicules</h3>
                    <p class="table-container-subtitle">État actuel du parc automobile</p>
                </div>
                ${tableClone.outerHTML || tableClone}
            </div>
            ${footer}
        </body>
        </html>
    `;
    
    // Ouvrir la fenêtre d'impression
    const printWindow = window.open('', '_blank');
    printWindow.document.write(fullDocument);
    printWindow.document.close();
    printWindow.print();
    printWindow.close();
}

/**
 * GUIDE D'UTILISATION RAPIDE
 * 
 * 1. Inclure les fichiers CSS et JS dans votre template :
 *    <link rel="stylesheet" href="{{ url_for('static', filename='css/print-header.css') }}">
 *    <script src="{{ url_for('static', filename='js/print-header.js') }}"></script>
 * 
 * 2. Utiliser une fonction prédéfinie :
 *    const header = createVidangeHeader('Mon Titre', 'Mon Sous-titre');
 * 
 * 3. Ou utiliser la fonction générique :
 *    const header = generateUDMPrintHeader({
 *        documentTitle: 'Mon Document',
 *        theme: 'transport'
 *    });
 * 
 * 4. Intégrer dans votre fonction d'impression :
 *    function printMyDocument() {
 *        const header = createTransportHeader('Mon Rapport');
 *        const content = // ... votre contenu
 *        const fullDoc = header + content;
 *        // ... logique d'impression
 *    }
 * 
 * THÈMES DISPONIBLES :
 * - 'transport' : Bleu/vert pour les documents de transport
 * - 'maintenance' : Jaune/orange pour la maintenance
 * - 'admin' : Rouge pour les documents administratifs
 * 
 * TYPES PRÉDÉFINIS :
 * - createVidangeHeader() : Pour les documents de vidange
 * - createRapportHeader() : Pour les rapports
 * - createTransportHeader() : Pour les documents de transport
 * - createMaintenanceHeader() : Pour la maintenance
 * - createAdminHeader() : Pour l'administration
 */
