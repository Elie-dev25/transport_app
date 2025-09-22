/* ================== FONCTIONS D'IMPRESSION CHAUFFEURS ================== */
/* Fonctions JavaScript pour l'impression des tableaux de chauffeurs */
/* SYSTÈME IDENTIQUE À VIDANGE ET CARBURATION */

/**
 * Fonction pour imprimer le tableau de la liste des chauffeurs
 */
function printChauffeursListeStandardized() {
    // Créer un en-tête d'impression standardisé UDM (identique vidange/carburation)
    const printHeader = createTransportHeader('Liste des Chauffeurs', 'Personnel de conduite des véhicules universitaires');

    // Récupérer le tableau des chauffeurs depuis la zone d'impression (comme vidange)
    const printArea = document.getElementById('printListeArea');
    if (!printArea) {
        alert('Zone d\'impression non trouvée');
        return;
    }

    // Récupérer seulement le tableau, pas toute la zone (comme vidange)
    const chauffeurTable = printArea.querySelector('table');
    if (!chauffeurTable) {
        alert('Tableau des chauffeurs non trouvé');
        return;
    }

    // Cloner le tableau pour modification (comme vidange)
    const tableClone = chauffeurTable.cloneNode(true);

    // Ajouter la classe 'table' pour les styles d'impression
    tableClone.classList.add('table');
    tableClone.classList.remove('print-table');

    // Supprimer la colonne Actions si elle existe (comme vidange)
    removeActionsColumn(tableClone);

    // Créer le contenu d'impression (identique vidange/carburation)
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-user-tie"></i> Liste des Chauffeurs</h3>
                <p class="table-container-subtitle">Personnel de conduite des véhicules universitaires</p>
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;

    // Lancer l'impression (identique vidange/carburation)
    printDocument(printContent, 'Liste des Chauffeurs - UDM Transport');
}

/**
 * Fonction pour imprimer le tableau de planification des chauffeurs
 */
function printPlanningTableStandardized() {
    // Créer un en-tête d'impression standardisé UDM (identique vidange/carburation)
    const printHeader = createTransportHeader('Planification des Chauffeurs', 'Organisation et affectation du personnel de conduite');

    // Récupérer le tableau de planification depuis la zone d'impression
    const printArea = document.getElementById('printPlanningArea');
    if (!printArea) {
        alert('Zone d\'impression de planification non trouvée');
        return;
    }

    // Récupérer seulement le tableau, pas toute la zone (comme vidange)
    const planningTable = printArea.querySelector('table');
    if (!planningTable) {
        alert('Tableau de planification non trouvé');
        return;
    }

    // Vérifier qu'il y a des données dans le tableau
    const tbody = planningTable.querySelector('tbody');
    if (!tbody || tbody.children.length === 0) {
        alert('Aucune donnée de planification à imprimer');
        return;
    }

    // Cloner le tableau pour modification (comme vidange)
    const tableClone = planningTable.cloneNode(true);

    // Ajouter la classe 'table' pour les styles d'impression
    tableClone.classList.add('table');
    tableClone.classList.remove('print-table');

    // Supprimer la colonne Actions si elle existe (comme vidange)
    removeActionsColumn(tableClone);

    // Créer le contenu d'impression (identique vidange/carburation)
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3><i class="fas fa-calendar-alt"></i> Planification des Chauffeurs</h3>
                <p class="table-container-subtitle">Organisation et affectation du personnel de conduite</p>
            </div>
            ${tableClone.outerHTML}
        </div>
        ${createPrintFooter()}
    `;

    // Lancer l'impression (identique vidange/carburation)
    printDocument(printContent, 'Planification des Chauffeurs - UDM Transport');
}

/**
 * Créer un pied de page d'impression (identique vidange/carburation)
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

    // Construire le document HTML complet (EXACTEMENT identique vidange/carburation)
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

    // Attendre que le contenu soit chargé puis imprimer (identique vidange/carburation)
    printWindow.onload = function() {
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 250);
    };
}

/**
 * Générer le tableau de planification à partir des données AJAX
 */
function generatePlanningTableFromAjax(planningData) {
    const tbody = document.getElementById('planningTableBody');
    tbody.innerHTML = '';

    if (!planningData || planningData.length === 0) {
        const newRow = tbody.insertRow();
        newRow.innerHTML = `
            <td colspan="5" style="text-align: center; font-style: italic;">
                Aucune donnée de planification disponible
            </td>
        `;
        return;
    }

    planningData.forEach(function(chauffeur) {
        const chauffeurNom = `${chauffeur.nom} ${chauffeur.prenom}`;

        if (chauffeur.statuts && chauffeur.statuts.length > 0) {
            // Créer une ligne pour chaque statut du chauffeur
            chauffeur.statuts.forEach(function(statut) {
                const newRow = tbody.insertRow();

                // Formater le statut pour l'affichage
                let statutLabel = statut.statut;
                if (statut.statut === 'CONGE') statutLabel = 'Congé';
                else if (statut.statut === 'PERMANENCE') statutLabel = 'Permanence';
                else if (statut.statut === 'SERVICE_WEEKEND') statutLabel = 'Week-end';
                else if (statut.statut === 'SERVICE_SEMAINE') statutLabel = 'Semaine';

                // Ajouter le lieu au statut
                let lieuLabel = '';
                if (statut.lieu === 'CUM') lieuLabel = ' (CUM)';
                else if (statut.lieu === 'CAMPUS') lieuLabel = ' (Campus)';
                else if (statut.lieu === 'CONJOINTEMENT') lieuLabel = ' (Conjointement)';

                newRow.innerHTML = `
                    <td>${chauffeurNom}</td>
                    <td>${statutLabel}${lieuLabel}</td>
                    <td>${statut.date_debut_formatted}</td>
                    <td>${statut.date_fin_formatted}</td>
                    <td>${statut.duree}</td>
                `;
            });
        } else {
            // Chauffeur sans statut
            const newRow = tbody.insertRow();
            newRow.innerHTML = `
                <td>${chauffeurNom}</td>
                <td>Attente</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
            `;
        }
    });
}

/**
 * Générer le tableau de planification à partir des données de la page
 */
function generatePlanningFromPage() {
    const tbody = document.getElementById('planningTableBody');
    if (!tbody) {
        console.error('Tableau de planification non trouvé');
        return;
    }

    tbody.innerHTML = '';

    // Parcourir tous les chauffeurs visibles dans le tableau principal
    const chauffeurRows = document.querySelectorAll('.table-container tbody tr');

    if (chauffeurRows.length === 0) {
        console.warn('Aucune ligne de chauffeur trouvée');
        // Ajouter une ligne par défaut
        const newRow = tbody.insertRow();
        newRow.innerHTML = `
            <td colspan="5" style="text-align: center; font-style: italic;">
                Aucune donnée de planification disponible
            </td>
        `;
        return;
    }

    chauffeurRows.forEach(function(row) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 5) {
            const nom = cells[0].textContent.trim();
            const prenom = cells[1].textContent.trim();
            const statutCell = cells[4]; // Colonne Statut est à l'index 4

            // Récupérer les statuts cliquables
            const statutsClickables = statutCell.querySelectorAll('.statut-clickable');

            if (statutsClickables.length > 0) {
                statutsClickables.forEach(function(statutSpan) {
                    const statut = statutSpan.dataset.statut || 'ATTENTE';
                    const dateDebut = statutSpan.dataset.dateDebut || 'Non définie';
                    const dateFin = statutSpan.dataset.dateFin || 'Non définie';

                    // Calculer la durée
                    let duree = 'Non définie';
                    if (dateDebut !== 'Non définie' && dateFin !== 'Non définie') {
                        const debut = new Date(dateDebut);
                        const fin = new Date(dateFin);
                        const diffTime = Math.abs(fin - debut);
                        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
                        duree = `${diffDays} jour${diffDays > 1 ? 's' : ''}`;
                    }

                    // Formater les dates
                    const dateDebutFormatted = dateDebut !== 'Non définie' ?
                        new Date(dateDebut).toLocaleDateString('fr-FR') : 'Non définie';
                    const dateFinFormatted = dateFin !== 'Non définie' ?
                        new Date(dateFin).toLocaleDateString('fr-FR') : 'Non définie';

                    // Mapper les statuts pour un affichage plus lisible
                    const statutDisplay = {
                        'CONGE': 'Congé',
                        'PERMANENCE': 'Permanence',
                        'SERVICE_WEEKEND': 'Week-end',
                        'SERVICE_SEMAINE': 'Semaine',
                        'ATTENTE': 'Attente'
                    }[statut] || statut;

                    // Ajouter la ligne au tableau
                    const newRow = tbody.insertRow();
                    newRow.innerHTML = `
                        <td>${nom} ${prenom}</td>
                        <td>${statutDisplay}</td>
                        <td>${dateDebutFormatted}</td>
                        <td>${dateFinFormatted}</td>
                        <td>${duree}</td>
                    `;
                });
            } else {
                // Chauffeur sans statut spécifique
                const newRow = tbody.insertRow();
                newRow.innerHTML = `
                    <td>${nom} ${prenom}</td>
                    <td>Attente</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                `;
            }
        }
    });
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

// Initialisation au chargement de la page (identique vidange/carburation)
document.addEventListener('DOMContentLoaded', function() {
    console.log('Fonctions d\'impression chauffeurs initialisées');
});
