/* ================== FONCTIONS D'IMPRESSION BUS DÉTAIL ================== */
/* Fonctions JavaScript pour l'impression des tableaux de la page bus détail */
/* SYSTÈME IDENTIQUE À VIDANGE ET CARBURATION */

/**
 * Fonction pour imprimer l'historique des trajets
 */
function printTrajetsTable(busNumero) {
    // Créer un en-tête d'impression standardisé UDM
    const printHeader = createTransportHeader(`Historique des Trajets - Bus ${busNumero}`, `Tous les trajets effectués par le véhicule ${busNumero}`);

    // Récupérer le tableau des trajets
    const trajetsTable = document.querySelector('#trajetsTable table');
    if (!trajetsTable) {
        alert('Tableau des trajets non trouvé');
        return;
    }

    // Cloner le tableau pour modification
    const tableClone = trajetsTable.cloneNode(true);

    // Ajouter la classe 'table' pour les styles d'impression
    tableClone.classList.add('table');

    // Supprimer la colonne Actions si elle existe
    removeActionsColumn(tableClone);

    // Créer le contenu d'impression
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-road"></i> Historique des Trajets - Bus ${busNumero}</h3>
                <p class="table-container-subtitle">Tous les trajets effectués par le véhicule ${busNumero}</p>
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;

    // Lancer l'impression
    printDocument(printContent, `Historique des Trajets - Bus ${busNumero} - UDM Transport`);
}

/**
 * Fonction pour imprimer l'historique des carburations
 */
function printCarburationsTable(busNumero) {
    // Créer un en-tête d'impression standardisé UDM
    const printHeader = createTransportHeader(`Historique des Carburations - Bus ${busNumero}`, `Historique complet des ravitaillements en carburant du véhicule ${busNumero}`);

    // Récupérer le tableau des carburations
    const carburationsTable = document.querySelector('#carburationsTable table');
    if (!carburationsTable) {
        alert('Tableau des carburations non trouvé');
        return;
    }

    // Cloner le tableau pour modification
    const tableClone = carburationsTable.cloneNode(true);

    // Ajouter la classe 'table' pour les styles d'impression
    tableClone.classList.add('table');

    // Supprimer la colonne Actions si elle existe
    removeActionsColumn(tableClone);

    // Créer le contenu d'impression
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-gas-pump"></i> Historique des Carburations - Bus ${busNumero}</h3>
                <p class="table-container-subtitle">Historique complet des ravitaillements en carburant du véhicule ${busNumero}</p>
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;

    // Lancer l'impression
    printDocument(printContent, `Historique des Carburations - Bus ${busNumero} - UDM Transport`);
}

/**
 * Fonction pour imprimer l'historique des vidanges
 */
function printVidangesTable(busNumero) {
    // Créer un en-tête d'impression standardisé UDM
    const printHeader = createTransportHeader(`Historique des Vidanges - Bus ${busNumero}`, `Historique complet des vidanges et maintenances du véhicule ${busNumero}`);

    // Récupérer le tableau des vidanges
    const vidangesTable = document.querySelector('#vidangesTable table');
    if (!vidangesTable) {
        alert('Tableau des vidanges non trouvé');
        return;
    }

    // Cloner le tableau pour modification
    const tableClone = vidangesTable.cloneNode(true);

    // Ajouter la classe 'table' pour les styles d'impression
    tableClone.classList.add('table');

    // Supprimer la colonne Actions si elle existe
    removeActionsColumn(tableClone);

    // Créer le contenu d'impression
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-oil-can"></i> Historique des Vidanges - Bus ${busNumero}</h3>
                <p class="table-container-subtitle">Historique complet des vidanges et maintenances du véhicule ${busNumero}</p>
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;

    // Lancer l'impression
    printDocument(printContent, `Historique des Vidanges - Bus ${busNumero} - UDM Transport`);
}

/**
 * Fonction pour imprimer l'historique des pannes
 */
function printPannesTable(busNumero) {
    // Créer un en-tête d'impression standardisé UDM
    const printHeader = createTransportHeader(`Historique des Pannes - Bus ${busNumero}`, `Historique complet des pannes et réparations du véhicule ${busNumero}`);

    // Récupérer le tableau des pannes
    const pannesTable = document.querySelector('#pannesTable table');
    if (!pannesTable) {
        alert('Tableau des pannes non trouvé');
        return;
    }

    // Cloner le tableau pour modification
    const tableClone = pannesTable.cloneNode(true);

    // Ajouter la classe 'table' pour les styles d'impression
    tableClone.classList.add('table');

    // Supprimer la colonne Actions si elle existe
    removeActionsColumn(tableClone);

    // Créer le contenu d'impression
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-exclamation-triangle"></i> Historique des Pannes - Bus ${busNumero}</h3>
                <p class="table-container-subtitle">Historique complet des pannes et réparations du véhicule ${busNumero}</p>
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;

    // Lancer l'impression
    printDocument(printContent, `Historique des Pannes - Bus ${busNumero} - UDM Transport`);
}

/**
 * Créer un pied de page d'impression
 */
function createPrintFooter() {
    return `
        <div class="print-footer">
            <p>Université des Montagnes - Système de Gestion de Transport</p>
        </div>
    `;
}

/**
 * Fonction générique pour imprimer un document (identique vidange/carburation)
 */
function printDocument(content, title) {
    // Créer une nouvelle fenêtre pour l'impression
    const printWindow = window.open('', '_blank', 'width=800,height=600');
    
    if (!printWindow) {
        alert('Impossible d\'ouvrir la fenêtre d\'impression. Veuillez autoriser les pop-ups.');
        return;
    }
    
    // Construire le document HTML complet (identique vidange/carburation)
    const fullDocument = `
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>${title}</title>
            <link rel="stylesheet" href="${window.location.origin}/static/css/print.css">
            <link rel="stylesheet" href="${window.location.origin}/static/css/print-header.css">
            <script src="${window.location.origin}/static/js/print-header.js"></script>
        </head>
        <body>
            ${content}
        </body>
        </html>
    `;
    
    // Écrire le contenu dans la nouvelle fenêtre
    printWindow.document.write(fullDocument);
    printWindow.document.close();
    
    // Attendre que le contenu soit chargé puis imprimer
    printWindow.onload = function() {
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 250);
    };
}

/**
 * Supprimer la colonne Actions d'un tableau (identique vidange/carburation)
 */
function removeActionsColumn(table) {
    // Trouver l'index de la colonne Actions
    const headers = table.querySelectorAll('thead th');
    let actionsIndex = -1;
    
    headers.forEach((header, index) => {
        if (header.textContent.trim().toLowerCase() === 'actions') {
            actionsIndex = index;
        }
    });
    
    if (actionsIndex !== -1) {
        // Supprimer l'en-tête
        headers[actionsIndex].remove();
        
        // Supprimer les cellules de la colonne dans toutes les lignes
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells[actionsIndex]) {
                cells[actionsIndex].remove();
            }
        });
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Fonctions d\'impression bus détail initialisées');
});
