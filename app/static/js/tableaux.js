/**
 * ================== SYSTÈME DE TABLEAUX UNIFIÉ ==================
 * JavaScript pour la gestion des tableaux modernes
 * Fonctionnalités : recherche, tri, pagination, filtres
 */

class TableauManager {
    constructor() {
        this.tables = new Map();
        this.init();
    }

    /**
     * Initialisation du gestionnaire de tableaux
     */
    init() {
        // Initialiser tous les tableaux au chargement de la page
        document.addEventListener('DOMContentLoaded', () => {
            this.initAllTables();
            this.setupGlobalEvents();
        });
    }

    /**
     * Initialiser tous les tableaux de la page
     */
    initAllTables() {
        const tableContainers = document.querySelectorAll('.table-container');
        tableContainers.forEach((container, index) => {
            const tableId = container.id || `table-${index}`;
            this.initTable(tableId, container);
        });
    }

    /**
     * Initialiser un tableau spécifique
     */
    initTable(tableId, container) {
        const table = container.querySelector('table');
        if (!table) return;

        const config = {
            container: container,
            table: table,
            searchInput: container.querySelector('.search-input'),
            rows: table.querySelectorAll('tbody tr'),
            headers: table.querySelectorAll('thead th'),
            sortable: table.classList.contains('sortable'),
            searchable: container.querySelector('.search-input') !== null
        };

        this.tables.set(tableId, config);

        // Configurer la recherche
        if (config.searchable) {
            this.setupSearch(tableId);
        }

        // Configurer le tri
        if (config.sortable) {
            this.setupSort(tableId);
        }

        // Ajouter les animations
        this.setupAnimations(tableId);
    }

    /**
     * Configurer la recherche dans un tableau
     */
    setupSearch(tableId) {
        const config = this.tables.get(tableId);
        if (!config || !config.searchInput) return;

        // Ajouter l'icône de recherche si elle n'existe pas
        this.addSearchIcon(config.searchInput);

        // Événement de recherche avec debounce
        let searchTimeout;
        config.searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(tableId, e.target.value);
            }, 300);
        });

        // Placeholder dynamique
        config.searchInput.placeholder = 'Rechercher dans le tableau...';
    }

    /**
     * Ajouter l'icône de recherche
     */
    addSearchIcon(input) {
        if (input.parentElement.classList.contains('search-container')) return;

        const container = document.createElement('div');
        container.className = 'search-container';
        input.parentNode.insertBefore(container, input);
        container.appendChild(input);
    }

    /**
     * Effectuer la recherche
     */
    performSearch(tableId, searchTerm) {
        const config = this.tables.get(tableId);
        if (!config) return;

        const term = searchTerm.toLowerCase().trim();
        let visibleCount = 0;

        config.rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const isVisible = term === '' || text.includes(term);
            
            row.style.display = isVisible ? '' : 'none';
            
            if (isVisible) {
                visibleCount++;
                // Animation d'apparition
                row.style.opacity = '0';
                row.style.transform = 'translateY(10px)';
                setTimeout(() => {
                    row.style.transition = 'all 0.3s ease';
                    row.style.opacity = '1';
                    row.style.transform = 'translateY(0)';
                }, visibleCount * 50);
            }
        });

        // Afficher un message si aucun résultat
        this.updateEmptyState(tableId, visibleCount, searchTerm);
    }

    /**
     * Mettre à jour l'état vide du tableau
     */
    updateEmptyState(tableId, visibleCount, searchTerm) {
        const config = this.tables.get(tableId);
        if (!config) return;

        let emptyRow = config.table.querySelector('.table-empty-row');
        
        if (visibleCount === 0 && searchTerm) {
            if (!emptyRow) {
                emptyRow = document.createElement('tr');
                emptyRow.className = 'table-empty-row';
                emptyRow.innerHTML = `
                    <td colspan="100%" class="table-empty">
                        <i class="fas fa-search"></i>
                        <h5>Aucun résultat trouvé</h5>
                        <p>Essayez avec d'autres mots-clés</p>
                    </td>
                `;
                config.table.querySelector('tbody').appendChild(emptyRow);
            }
            emptyRow.style.display = '';
        } else if (emptyRow) {
            emptyRow.style.display = 'none';
        }
    }

    /**
     * Configurer le tri des colonnes
     */
    setupSort(tableId) {
        const config = this.tables.get(tableId);
        if (!config) return;

        config.headers.forEach((header, index) => {
            if (header.classList.contains('no-sort')) return;

            header.style.cursor = 'pointer';
            header.style.userSelect = 'none';
            header.innerHTML += ' <i class="fas fa-sort sort-icon"></i>';

            header.addEventListener('click', () => {
                this.sortTable(tableId, index);
            });
        });
    }

    /**
     * Trier le tableau
     */
    sortTable(tableId, columnIndex) {
        const config = this.tables.get(tableId);
        if (!config) return;

        const tbody = config.table.querySelector('tbody');
        const rows = Array.from(config.rows);
        const header = config.headers[columnIndex];
        const sortIcon = header.querySelector('.sort-icon');

        // Déterminer la direction du tri
        let ascending = true;
        if (header.classList.contains('sort-asc')) {
            ascending = false;
            header.classList.remove('sort-asc');
            header.classList.add('sort-desc');
            sortIcon.className = 'fas fa-sort-down sort-icon';
        } else {
            // Réinitialiser tous les autres headers
            config.headers.forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
                const icon = h.querySelector('.sort-icon');
                if (icon) icon.className = 'fas fa-sort sort-icon';
            });
            
            header.classList.add('sort-asc');
            sortIcon.className = 'fas fa-sort-up sort-icon';
        }

        // Trier les lignes
        rows.sort((a, b) => {
            const aText = a.cells[columnIndex].textContent.trim();
            const bText = b.cells[columnIndex].textContent.trim();

            // Détecter si c'est un nombre
            const aNum = parseFloat(aText.replace(/[^\d.-]/g, ''));
            const bNum = parseFloat(bText.replace(/[^\d.-]/g, ''));

            if (!isNaN(aNum) && !isNaN(bNum)) {
                return ascending ? aNum - bNum : bNum - aNum;
            }

            // Tri alphabétique
            return ascending ? 
                aText.localeCompare(bText, 'fr', { numeric: true }) :
                bText.localeCompare(aText, 'fr', { numeric: true });
        });

        // Réorganiser le DOM
        rows.forEach(row => tbody.appendChild(row));

        // Animation de tri
        this.animateSortedRows(rows);
    }

    /**
     * Animer les lignes après tri
     */
    animateSortedRows(rows) {
        rows.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                row.style.transition = 'all 0.3s ease';
                row.style.opacity = '1';
                row.style.transform = 'translateX(0)';
            }, index * 30);
        });
    }

    /**
     * Configurer les animations
     */
    setupAnimations(tableId) {
        const config = this.tables.get(tableId);
        if (!config) return;

        // Animation d'apparition des lignes
        config.rows.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                row.style.transition = 'all 0.5s ease';
                row.style.opacity = '1';
                row.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Animation des boutons d'action
        const actionButtons = config.table.querySelectorAll('.table-btn');
        actionButtons.forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-2px) scale(1.05)';
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    /**
     * Configurer les événements globaux
     */
    setupGlobalEvents() {
        // Gestion des modales de confirmation pour les suppressions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-btn') || 
                e.target.closest('.delete-btn')) {
                e.preventDefault();
                this.showDeleteConfirmation(e.target);
            }
        });

        // Gestion du redimensionnement
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    /**
     * Afficher la confirmation de suppression
     */
    showDeleteConfirmation(button) {
        const confirmed = confirm('Êtes-vous sûr de vouloir supprimer cet élément ?');
        if (confirmed) {
            // Ici vous pouvez ajouter la logique de suppression
            console.log('Suppression confirmée');
        }
    }

    /**
     * Gérer le redimensionnement
     */
    handleResize() {
        // Ajuster les tableaux pour mobile
        const isMobile = window.innerWidth <= 768;
        
        this.tables.forEach((config, tableId) => {
            if (isMobile) {
                config.container.classList.add('mobile-view');
            } else {
                config.container.classList.remove('mobile-view');
            }
        });
    }

    /**
     * Méthodes publiques pour l'API
     */
    
    /**
     * Rafraîchir un tableau
     */
    refreshTable(tableId) {
        const config = this.tables.get(tableId);
        if (!config) return;

        // Réinitialiser les lignes
        config.rows = config.table.querySelectorAll('tbody tr');
        
        // Réappliquer les animations
        this.setupAnimations(tableId);
    }

    /**
     * Ajouter une nouvelle ligne
     */
    addRow(tableId, rowHtml) {
        const config = this.tables.get(tableId);
        if (!config) return;

        const tbody = config.table.querySelector('tbody');
        const newRow = document.createElement('tr');
        newRow.innerHTML = rowHtml;
        
        // Animation d'ajout
        newRow.style.opacity = '0';
        newRow.style.transform = 'translateY(-20px)';
        tbody.appendChild(newRow);
        
        setTimeout(() => {
            newRow.style.transition = 'all 0.5s ease';
            newRow.style.opacity = '1';
            newRow.style.transform = 'translateY(0)';
        }, 100);

        // Mettre à jour la configuration
        this.refreshTable(tableId);
    }

    /**
     * Supprimer une ligne
     */
    removeRow(tableId, rowElement) {
        // Animation de suppression
        rowElement.style.transition = 'all 0.3s ease';
        rowElement.style.opacity = '0';
        rowElement.style.transform = 'translateX(100px)';
        
        setTimeout(() => {
            rowElement.remove();
            this.refreshTable(tableId);
        }, 300);
    }
}

// Initialiser le gestionnaire de tableaux
const tableauManager = new TableauManager();

// Exporter pour utilisation globale
window.TableauManager = tableauManager;
