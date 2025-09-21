// ===== IMPRESSION FICHE D'EMBARQUEMENT =====

function printReport() {
    // Récupérer les données de la page
    const entityName = document.querySelector('.rapport-entity-container').getAttribute('data-entity') || 'Noblesse';

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
    
    // Créer le contenu HTML de la fiche
    const printContent = `
        <div class="print-content">
            <div class="print-header">
                <div class="print-title">RAPPORT ${entityName.toUpperCase()}</div>
                <div class="print-info">
                    Type: ${typeText}<br>
                    Date: ${dateText}
                </div>
                <div class="print-subtitle">FICHE D'EMBARQUEMENT</div>
            </div>
            
            <table class="print-table">
                <thead>
                    ${headerContent}
                </thead>
                <tbody>
                    ${tableContent}
                </tbody>
            </table>
            
            <div class="print-signature">
                Signature: ________________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Date: _______________
            </div>
        </div>
    `;
    
    // Créer une nouvelle fenêtre pour l'impression avec styles intégrés
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fiche d'embarquement - ${entityName}</title>
            <style>
                @page {
                    size: A4;
                    margin: 2cm;
                }

                body {
                    margin: 0;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    color: #000;
                    background: #fff;
                }

                .print-content {
                    width: 100%;
                }

                .print-header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #000;
                }

                .print-title {
                    font-size: 18px;
                    font-weight: bold;
                    text-transform: uppercase;
                    margin-bottom: 20px;
                }

                .print-info {
                    font-size: 14px;
                    line-height: 1.8;
                }

                .print-subtitle {
                    font-size: 16px;
                    font-weight: bold;
                    text-transform: uppercase;
                    margin-top: 15px;
                }

                .print-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    font-size: 11px;
                }

                .print-table th {
                    border: 2px solid #000;
                    padding: 12px 8px;
                    text-align: center;
                    vertical-align: middle;
                    background: #f8f8f8;
                    font-weight: bold;
                    text-transform: uppercase;
                    height: 35px;
                }

                .print-table td {
                    border: 1px solid #000;
                    padding: 10px 8px;
                    text-align: center;
                    vertical-align: top;
                    height: 50px;
                    background: #fff;
                }

                .print-table th:nth-child(1), .print-table td:nth-child(1) { width: 18%; }
                .print-table th:nth-child(2), .print-table td:nth-child(2) { width: 15%; }
                .print-table th:nth-child(3), .print-table td:nth-child(3) { width: 15%; }
                .print-table th:nth-child(4), .print-table td:nth-child(4) { width: 17%; }
                .print-table th:nth-child(5), .print-table td:nth-child(5) { width: 12%; }
                .print-table th:nth-child(6), .print-table td:nth-child(6) { width: 23%; }

                .print-signature {
                    margin-top: 50px;
                    text-align: right;
                    border-top: 1px solid #ccc;
                    padding-top: 20px;
                    font-size: 12px;
                }

                @media print {
                    body { padding: 0; }
                }
            </style>
        </head>
        <body>
            ${printContent}
        </body>
        </html>
    `);
    
    printWindow.document.close();
    
    // Attendre que le contenu soit chargé puis imprimer
    printWindow.onload = function() {
        printWindow.print();
        printWindow.close();
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
