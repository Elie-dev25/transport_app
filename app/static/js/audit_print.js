/**
 * Système d'audit pour les impressions
 * Enregistre automatiquement toutes les impressions dans les logs d'audit
 */

/**
 * Fonction pour auditer une impression
 * @param {string} documentType - Type de document (vidange, carburation, rapport, etc.)
 * @param {string} documentId - ID du document (optionnel)
 * @param {string} details - Détails supplémentaires (optionnel)
 */
function auditPrint(documentType, documentId = null, details = null) {
    // Construire les données d'audit
    const auditData = {
        document_type: documentType,
        document_id: documentId,
        details: details,
        timestamp: new Date().toISOString(),
        page_url: window.location.pathname
    };
    
    // Envoyer l'audit au serveur
    fetch('/admin/api/audit/print', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(auditData)
    })
    .then(response => {
        if (!response.ok) {
            console.warn('Audit d\'impression échoué:', response.status);
        }
    })
    .catch(error => {
        console.warn('Erreur audit impression:', error);
    });
}

/**
 * Wrapper pour window.print() avec audit automatique
 * @param {string} documentType - Type de document
 * @param {string} documentId - ID du document (optionnel)
 * @param {string} details - Détails supplémentaires (optionnel)
 */
function auditedPrint(documentType, documentId = null, details = null) {
    // Auditer l'impression
    auditPrint(documentType, documentId, details);
    
    // Lancer l'impression
    window.print();
}

/**
 * Wrapper pour printDocument() avec audit automatique
 * @param {string} content - Contenu à imprimer
 * @param {string} title - Titre du document
 * @param {string} documentType - Type de document pour l'audit
 * @param {string} documentId - ID du document (optionnel)
 */
function auditedPrintDocument(content, title, documentType, documentId = null) {
    // Auditer l'impression
    auditPrint(documentType, documentId, `Title: ${title}`);
    
    // Lancer l'impression avec la fonction existante
    if (typeof printDocument === 'function') {
        printDocument(content, title);
    } else {
        // Fallback si printDocument n'existe pas
        const printWindow = window.open('', '_blank', 'width=800,height=600');
        if (printWindow) {
            printWindow.document.write(`
                <!DOCTYPE html>
                <html lang="fr">
                <head>
                    <meta charset="UTF-8">
                    <title>${title}</title>
                    <link rel="stylesheet" href="/static/css/print.css">
                </head>
                <body>
                    ${content}
                </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.onload = function() {
                setTimeout(() => {
                    printWindow.print();
                    printWindow.close();
                }, 250);
            };
        }
    }
}

/**
 * Détection automatique du type de document basé sur l'URL et le contenu
 */
function detectDocumentType() {
    const path = window.location.pathname;
    const title = document.title;
    
    if (path.includes('vidange') || title.includes('Vidange')) {
        return 'vidange';
    } else if (path.includes('carburation') || title.includes('Carburation')) {
        return 'carburation';
    } else if (path.includes('chauffeur') || title.includes('Chauffeur')) {
        return 'chauffeur';
    } else if (path.includes('bus') || title.includes('Bus')) {
        return 'bus';
    } else if (path.includes('rapport') || title.includes('Rapport')) {
        return 'rapport';
    } else if (path.includes('depanage') || title.includes('Dépannage')) {
        return 'depanage';
    } else if (path.includes('trajet') || title.includes('Trajet')) {
        return 'trajet';
    } else {
        return 'document';
    }
}

/**
 * Intercepter tous les appels à window.print() pour audit automatique
 */
(function() {
    // Sauvegarder la fonction originale
    const originalPrint = window.print;
    
    // Remplacer par une version auditée
    window.print = function() {
        // Détecter automatiquement le type de document
        const documentType = detectDocumentType();
        
        // Auditer l'impression
        auditPrint(documentType, null, 'Direct window.print() call');
        
        // Appeler la fonction originale
        return originalPrint.call(this);
    };
})();

/**
 * Fonctions spécialisées pour chaque type d'impression
 */

// Vidange
function auditedPrintVidange(tableType = 'gestion') {
    const busNumero = getBusNumeroFromPage();
    auditPrint('vidange', busNumero, `Table type: ${tableType}`);
}

// Carburation
function auditedPrintCarburation(tableType = 'gestion') {
    const busNumero = getBusNumeroFromPage();
    auditPrint('carburation', busNumero, `Table type: ${tableType}`);
}

// Chauffeurs
function auditedPrintChauffeurs(tableType = 'liste') {
    auditPrint('chauffeur', null, `Table type: ${tableType}`);
}

// Bus
function auditedPrintBus(busNumero = null, tableType = 'detail') {
    auditPrint('bus', busNumero, `Table type: ${tableType}`);
}

// Rapports
function auditedPrintRapport(entityName = null) {
    auditPrint('rapport', entityName, `Entity: ${entityName || 'unknown'}`);
}

/**
 * Utilitaires
 */
function getBusNumeroFromPage() {
    // Essayer de récupérer le numéro de bus depuis différents endroits
    const urlParams = new URLSearchParams(window.location.search);
    const busId = urlParams.get('bus_id');
    
    if (busId) return busId;
    
    // Chercher dans le titre de la page
    const title = document.title;
    const busMatch = title.match(/Bus\s+(\w+)/i);
    if (busMatch) return busMatch[1];
    
    // Chercher dans les éléments de la page
    const busElement = document.querySelector('[data-bus-numero]');
    if (busElement) return busElement.getAttribute('data-bus-numero');
    
    return null;
}

/**
 * Initialisation
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Système d\'audit d\'impression initialisé');
    
    // Ajouter des listeners aux boutons d'impression existants
    const printButtons = document.querySelectorAll('button[onclick*="print"], a[onclick*="print"]');
    printButtons.forEach(button => {
        const originalOnclick = button.getAttribute('onclick');
        if (originalOnclick && !originalOnclick.includes('auditPrint')) {
            // Modifier l'onclick pour inclure l'audit
            const documentType = detectDocumentType();
            button.setAttribute('onclick', `auditPrint('${documentType}'); ${originalOnclick}`);
        }
    });
});

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        auditPrint,
        auditedPrint,
        auditedPrintDocument,
        detectDocumentType
    };
}
