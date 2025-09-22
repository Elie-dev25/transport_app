/* ================== FONCTIONS D'IMPRESSION VIDANGE ================== */
/* Fonctions JavaScript pour l'impression des tableaux de vidange */

/**
 * Fonction pour imprimer le tableau de gestion des vidanges
 */
function printVidangeTable() {
    // Créer un en-tête d'impression standardisé UDM
    const printHeader = createVidangeHeader('Gestion des Vidanges', 'Liste des véhicules nécessitant une vidange');
    
    // Récupérer le tableau de vidange
    const vidangeTable = document.querySelector('#vidangeTable table');
    if (!vidangeTable) {
        alert('Tableau de vidange non trouvé');
        return;
    }

    // Cloner le tableau pour modification
    const tableClone = vidangeTable.cloneNode(true);
    
    // Supprimer la colonne Actions si elle existe
    removeActionsColumn(tableClone);
    
    // Créer le contenu d'impression
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-oil-can"></i> Gestion des Vidanges</h3>
                <p class="table-container-subtitle">Suivi et planification des vidanges de véhicules</p>
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;
    
    // Lancer l'impression
    printDocument(printContent, 'Gestion des Vidanges - UDM Transport');
}

/**
 * Fonction pour imprimer l'historique des vidanges
 */
function printHistoriqueTable() {
    // Créer un en-tête d'impression standardisé UDM
    const printHeader = createVidangeHeader('Historique des Vidanges', 'Historique complet des vidanges effectuées');
    
    // Récupérer le tableau d'historique
    const historiqueTable = document.querySelector('#historiqueTable table');
    if (!historiqueTable) {
        alert('Tableau d\'historique non trouvé');
        return;
    }

    // Cloner le tableau pour modification
    const tableClone = historiqueTable.cloneNode(true);
    
    // Récupérer les filtres actifs pour les afficher
    const filtresInfo = getActiveFilters();
    
    // Créer le contenu d'impression
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-history"></i> Historique des Vidanges</h3>
                <p class="table-container-subtitle">Historique complet des vidanges effectuées</p>
                ${filtresInfo ? `<p style="font-size: 11px; color: #666; margin-top: 5px;"><strong>Filtres appliqués:</strong> ${filtresInfo}</p>` : ''}
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;
    
    // Lancer l'impression
    printDocument(printContent, 'Historique des Vidanges - UDM Transport');
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
 * Récupérer les informations sur les filtres actifs
 */
function getActiveFilters() {
    const filters = [];
    
    // Vérifier le filtre véhicule
    const vehiculeSelect = document.getElementById('numero_udm');
    if (vehiculeSelect && vehiculeSelect.value) {
        filters.push(`Véhicule: AED-${vehiculeSelect.value}`);
    }
    
    // Vérifier les filtres de date
    const dateDebut = document.getElementById('vid_date_debut');
    const dateFin = document.getElementById('vid_date_fin');
    
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

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Fonctions d\'impression vidange initialisées');
});
