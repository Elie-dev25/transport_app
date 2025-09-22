/* ================== GÉNÉRATEUR D'EN-TÊTE D'IMPRESSION ================== */
/* Fonction réutilisable pour créer l'en-tête standardisé UDM */

/**
 * Génère l'en-tête d'impression standardisé UDM
 * @param {Object} options - Options de configuration
 * @param {string} options.documentTitle - Titre du document
 * @param {string} options.documentSubtitle - Sous-titre du document (optionnel)
 * @param {string} options.serviceCode - Code du service (par défaut: DAARFM)
 * @param {string} options.serviceName - Nom du service (par défaut: SERVICE DES RESSOURCES MATÉRIELLES)
 * @param {string} options.theme - Thème de couleur (transport, maintenance, admin)
 * @param {boolean} options.compact - Version compacte de l'en-tête
 * @param {boolean} options.showDate - Afficher la date de génération
 * @returns {string} HTML de l'en-tête
 */
function generateUDMPrintHeader(options = {}) {
    // Valeurs par défaut
    const config = {
        documentTitle: options.documentTitle || 'Document UDM',
        documentSubtitle: options.documentSubtitle || '',
        serviceCode: options.serviceCode || 'DAARFM',
        serviceName: options.serviceName || 'SERVICE DES RESSOURCES MATÉRIELLES',
        theme: options.theme || 'transport',
        compact: options.compact || false,
        showDate: options.showDate !== false, // true par défaut
        logoPath: options.logoPath || '/static/img/Logo_Université_des_Montagnes.jpg'
    };

    // Générer la date actuelle
    const currentDate = new Date().toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    // Classes CSS
    const headerClasses = [
        'udm-print-header',
        config.compact ? 'compact' : '',
        config.theme ? `theme-${config.theme}` : ''
    ].filter(Boolean).join(' ');

    // Construire l'HTML de l'en-tête
    return `
        <div class="${headerClasses}">
            <div class="udm-print-header-content">
                <!-- Section gauche: Logo et Université -->
                <div class="udm-header-left">
                    <img src="${config.logoPath}" alt="Logo UDM" class="udm-logo">
                    <div class="udm-university-info">
                        <h1 class="udm-university-name">Université des Montagnes</h1>
                        <p class="udm-university-subtitle">Semper Altissima Ascendere</p>
                    </div>
                </div>
                
                <!-- Section droite: Service -->
                <div class="udm-header-right">
                    <div class="udm-service-code">${config.serviceCode}</div>
                    <div class="udm-service-name">${config.serviceName}</div>
                </div>
            </div>
            
            <!-- Informations du document -->
            <div class="udm-document-info">
                <div class="udm-document-title">
                    ${config.documentTitle}
                    ${config.documentSubtitle ? ` - ${config.documentSubtitle}` : ''}
                </div>
                ${config.showDate ? `<div class="udm-document-date">Généré le ${currentDate}</div>` : ''}
            </div>
        </div>
    `;
}

/**
 * Configurations prédéfinies pour différents types de documents
 */
const UDM_PRINT_CONFIGS = {
    // Configuration pour les documents de transport
    transport: {
        serviceCode: 'DAARFM',
        serviceName: 'SERVICE DES RESSOURCES MATÉRIELLES',
        theme: 'transport'
    },
    
    // Configuration pour les documents de maintenance
    maintenance: {
        serviceCode: 'DAARFM',
        serviceName: 'SERVICE DE MAINTENANCE',
        theme: 'maintenance'
    },
    
    // Configuration pour les documents administratifs
    admin: {
        serviceCode: 'DAARFM',
        serviceName: 'SERVICE ADMINISTRATIF',
        theme: 'admin'
    },
    
    // Configuration pour les rapports
    rapports: {
        serviceCode: 'DAARFM',
        serviceName: 'SERVICE DES RESSOURCES MATÉRIELLES',
        theme: 'transport'
    },
    
    // Configuration pour la gestion des véhicules
    vehicules: {
        serviceCode: 'DAARFM',
        serviceName: 'GESTION DES VÉHICULES',
        theme: 'transport'
    },
    
    // Configuration pour les vidanges
    vidange: {
        serviceCode: 'DAARFM',
        serviceName: 'SERVICE DE MAINTENANCE',
        theme: 'maintenance'
    },
    
    // Configuration pour les dépannages
    depannage: {
        serviceCode: 'DAARFM',
        serviceName: 'SERVICE DE DÉPANNAGE',
        theme: 'maintenance'
    }
};

/**
 * Fonction simplifiée pour générer un en-tête avec configuration prédéfinie
 * @param {string} type - Type de document (transport, maintenance, admin, etc.)
 * @param {string} documentTitle - Titre du document
 * @param {string} documentSubtitle - Sous-titre du document (optionnel)
 * @param {Object} customOptions - Options personnalisées supplémentaires
 * @returns {string} HTML de l'en-tête
 */
function generateUDMHeaderByType(type, documentTitle, documentSubtitle = '', customOptions = {}) {
    const baseConfig = UDM_PRINT_CONFIGS[type] || UDM_PRINT_CONFIGS.transport;
    
    const options = {
        ...baseConfig,
        documentTitle,
        documentSubtitle,
        ...customOptions
    };
    
    return generateUDMPrintHeader(options);
}

/**
 * Fonction pour créer un en-tête de vidange
 */
function createVidangeHeader(title, subtitle = '') {
    return generateUDMHeaderByType('vidange', title, subtitle);
}

/**
 * Fonction pour créer un en-tête de rapport
 */
function createRapportHeader(title, subtitle = '') {
    return generateUDMHeaderByType('rapports', title, subtitle);
}

/**
 * Fonction pour créer un en-tête de transport
 */
function createTransportHeader(title, subtitle = '') {
    return generateUDMHeaderByType('transport', title, subtitle);
}

/**
 * Fonction pour créer un en-tête de maintenance
 */
function createMaintenanceHeader(title, subtitle = '') {
    return generateUDMHeaderByType('maintenance', title, subtitle);
}

/**
 * Fonction pour créer un en-tête administratif
 */
function createAdminHeader(title, subtitle = '') {
    return generateUDMHeaderByType('admin', title, subtitle);
}

// Export des fonctions pour utilisation dans d'autres fichiers
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generateUDMPrintHeader,
        generateUDMHeaderByType,
        createVidangeHeader,
        createRapportHeader,
        createTransportHeader,
        createMaintenanceHeader,
        createAdminHeader,
        UDM_PRINT_CONFIGS
    };
}
