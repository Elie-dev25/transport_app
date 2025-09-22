// ===== IMPRESSION FICHE D'EMBARQUEMENT =====

function printReport() {
    // Récupérer les données de la page
    const entityName = document.querySelector('.rapport-entity-container').getAttribute('data-entity') || 'Noblesse';

    // Créer l'en-tête standardisé UDM
    const printHeader = createRapportHeader(`Rapport ${entityName}`, 'Analyse détaillée des trajets');

    // Récupérer le type et la date depuis la section "Période d'Analyse"
    // Chercher tous les éléments info-item et trouver ceux avec "Type :" et "Dates :"
    const infoItems = document.querySelectorAll('.info-item');
    let typeText = 'Mensuelle';
    let dateText = new Date().toLocaleDateString('fr-FR');

    infoItems.forEach(item => {
        const label = item.querySelector('.info-label');
        const value = item.querySelector('.info-value');

        if (label && value) {
            if (label.textContent.trim() === 'Type :') {
                const badge = value.querySelector('.status-badge');
                if (badge) {
                    typeText = badge.textContent.trim();
                }
            } else if (label.textContent.trim() === 'Dates :') {
                const dateSpan = value.querySelector('.d-flex span');
                if (dateSpan) {
                    dateText = dateSpan.textContent.trim();
                }
            }
        }
    });
    
    // Récupérer les données du tableau
    const tableRows = document.querySelectorAll('#trajetsTable .table tbody tr');
    let tableContent = '';
    
    tableRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length > 0) {
            tableContent += '<tr>';
            cells.forEach(cell => {
                // Nettoyer le contenu des cellules (supprimer les icônes, etc.)
                let cellText = cell.textContent.trim();
                tableContent += `<td>${cellText}</td>`;
            });
            tableContent += '</tr>';
        }
    });
    
    // Récupérer les en-têtes du tableau
    const tableHeaders = document.querySelectorAll('#trajetsTable .table thead th');
    let headerContent = '<tr>';
    tableHeaders.forEach(header => {
        headerContent += `<th>${header.textContent.trim()}</th>`;
    });
    headerContent += '</tr>';
    
    // Créer le contenu HTML de la fiche avec l'en-tête standardisé
    const printContent = `
        ${printHeader}
        <div class="table-container">
            <div class="table-container-header">
                <h3>Rapport ${entityName} - Fiche d'Embarquement</h3>
                <p class="table-container-subtitle">Type: ${typeText} | Date: ${dateText}</p>
            </div>
            <table class="table">
                <thead>
                    ${headerContent}
                </thead>
                <tbody>
                    ${tableContent}
                </tbody>
            </table>
            <div class="print-signature" style="margin-top: 30px; text-align: right; font-size: 12px;">
                Signature: ________________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Date: _______________
            </div>
        </div>
        <div class="print-footer">
            <p>Université des Montagnes - Système de Gestion de Transport</p>
        </div>
    `;
    
    // Créer une nouvelle fenêtre pour l'impression avec les nouveaux styles
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <title>Rapport ${entityName} - UDM Transport</title>
            <link rel="stylesheet" href="${window.location.origin}/static/css/print.css">
            <link rel="stylesheet" href="${window.location.origin}/static/css/print-header.css">
            <style>
                @page {
                    size: A4;
                    margin: 2cm;
                }
                .print-signature {
                    margin-top: 30px;
                    text-align: right;
                    font-size: 12px;
                    border-top: 1px solid #ddd;
                    padding-top: 15px;
            </style>
        </head>
        <body>
            ${printContent}
        </body>
        </html>
    `);

    printWindow.document.close();
    printWindow.focus();

    // Attendre que le contenu soit chargé puis imprimer
    printWindow.onload = function() {
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 250);
    };
}

// Initialiser quand la page est chargée
document.addEventListener('DOMContentLoaded', function() {
    // Remplacer le onclick du bouton d'impression
    const printBtn = document.querySelector('button[onclick="window.print()"]');
    if (printBtn) {
        printBtn.setAttribute('onclick', 'printReport()');
    }
});
