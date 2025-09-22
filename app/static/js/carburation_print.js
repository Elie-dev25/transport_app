/* ================== FONCTIONS D'IMPRESSION CARBURATION ================== */
/* Fonctions JavaScript pour l'impression des tableaux de carburation */

/**
 * Fonction pour imprimer le tableau de gestion de la carburation
 */
function printCarburationTable() {
    // Créer un en-tête d'impression standardisé UDM
    const printHeader = createMaintenanceHeader('Gestion de la Carburation', 'Suivi du carburant et ravitaillement des véhicules');
    
    // Récupérer le tableau de carburation
    const carburationTable = document.querySelector('#carburationTable table');
    if (!carburationTable) {
        alert('Tableau de carburation non trouvé');
        return;
    }

    // Cloner le tableau pour modification
    const tableClone = carburationTable.cloneNode(true);
    
    // Supprimer la colonne Actions si elle existe
    removeActionsColumn(tableClone);
    
    // Créer le contenu d'impression
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-gas-pump"></i> Gestion de la Carburation</h3>
                <p class="table-container-subtitle">Suivi du carburant et ravitaillement des véhicules</p>
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;
    
    // Lancer l'impression
    printDocument(printContent, 'Gestion de la Carburation - UDM Transport');
}

/**
 * Fonction pour imprimer l'historique des carburations
 */
function printHistoriqueCarburationTable() {
    // Créer un en-tête d'impression standardisé UDM
    const printHeader = createMaintenanceHeader('Historique des Carburations', 'Historique complet des carburations effectuées');
    
    // Récupérer le tableau d'historique
    const historiqueTable = document.querySelector('#historiqueCarbuTable table');
    if (!historiqueTable) {
        alert('Tableau d\'historique non trouvé');
        return;
    }

    // Cloner le tableau pour modification
    const tableClone = historiqueTable.cloneNode(true);
    
    // Récupérer les filtres actifs pour les afficher
    const filtresInfo = getActiveCarburationFilters();
    
    // Créer le contenu d'impression
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-history"></i> Historique des Carburations</h3>
                <p class="table-container-subtitle">Historique complet des carburations effectuées</p>
                ${filtresInfo ? `<p style="font-size: 11px; color: #666; margin-top: 5px;"><strong>Filtres appliqués:</strong> ${filtresInfo}</p>` : ''}
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;
    
    // Lancer l'impression
    printDocument(printContent, 'Historique des Carburations - UDM Transport');
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
 * Supprimer la colonne Actions d'un tableau
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

/**
 * Récupérer les informations sur les filtres actifs pour la carburation
 */
function getActiveCarburationFilters() {
    const filters = [];
    
    // Vérifier le filtre véhicule
    const vehiculeSelect = document.getElementById('carb_numero_select');
    if (vehiculeSelect && vehiculeSelect.value) {
        filters.push(`Véhicule: AED-${vehiculeSelect.value}`);
    }
    
    // Vérifier les filtres de date
    const dateDebut = document.getElementById('carb_date_debut');
    const dateFin = document.getElementById('carb_date_fin');
    
    if (dateDebut && dateDebut.value) {
        filters.push(`Du: ${new Date(dateDebut.value).toLocaleDateString('fr-FR')}`);
    }
    
    if (dateFin && dateFin.value) {
        filters.push(`Au: ${new Date(dateFin.value).toLocaleDateString('fr-FR')}`);
    }
    
    return filters.length > 0 ? filters.join(', ') : null;
}

/**
 * Fonction générique pour imprimer un document
 */
function printDocument(content, title) {
    // Créer une nouvelle fenêtre pour l'impression
    const printWindow = window.open('', '_blank', 'width=800,height=600');
    
    if (!printWindow) {
        alert('Impossible d\'ouvrir la fenêtre d\'impression. Veuillez autoriser les pop-ups.');
        return;
    }
    
    // Construire le document HTML complet
    const fullDocument = `
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>${title}</title>
            <link rel="stylesheet" href="${window.location.origin}/static/css/print.css">
            <link rel="stylesheet" href="${window.location.origin}/static/css/print-header.css">
            <style>
                body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
                .table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 11px; }
                .table th { background-color: #f5f5f5; font-weight: bold; }
                .status-badge { background: none; color: #000; border: 1px solid #000; padding: 2px 6px; border-radius: 3px; font-size: 10px; }
                .table-container { margin-bottom: 30px; }
                .table-container-header h3 { font-size: 16px; margin-bottom: 10px; }
                .table-container-subtitle { font-size: 12px; color: #666; margin-bottom: 15px; }
            </style>
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

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Fonctions d\'impression carburation initialisées');
});
