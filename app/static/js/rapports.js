// Rapports JavaScript - Gestion des graphiques et interactions
class RapportsManager {
    constructor() {
        this.charts = {};
        this.currentData = null;
        this.currentPeriode = 'mois';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadData();
    }

    setupEventListeners() {
        // Filtres de période
        document.getElementById('periode-select').addEventListener('change', (e) => {
            this.currentPeriode = e.target.value;
            this.loadData();
        });

        // Bouton actualiser
        document.getElementById('refresh-data').addEventListener('click', () => {
            this.loadData();
        });

        // Bouton export PDF
        document.getElementById('export-pdf').addEventListener('click', () => {
            this.exportToPDF();
        });

        // Toggles des sections
        document.querySelectorAll('.btn-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.target.closest('.btn-toggle').dataset.target;
                this.toggleSection(target, btn);
            });
        });
    }

    async loadData() {
        try {
            this.showLoading(true);
            console.log('Debug: Chargement des données pour la période:', this.currentPeriode);
            
            // Utiliser l'API de test temporairement pour diagnostiquer
            const response = await fetch(`/admin/api/rapports/test`);
            
            console.log('Debug: Réponse reçue, status:', response.status);
            
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            this.currentData = await response.json();
            console.log('Debug: Données reçues:', this.currentData);
            
            if (this.currentData.error) {
                throw new Error(this.currentData.error);
            }
            
            this.renderAllCharts();
            this.updateSummary();
            
        } catch (error) {
            console.error('Erreur lors du chargement des données:', error);
            this.showError('Erreur lors du chargement des données: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(show) {
        const loader = document.getElementById('loading-indicator');
        const sections = document.querySelectorAll('.rapport-section');
        
        if (show) {
            loader.classList.add('show');
            sections.forEach(section => section.style.opacity = '0.5');
        } else {
            loader.classList.remove('show');
            sections.forEach(section => section.style.opacity = '1');
        }
    }

    showError(message) {
        // Créer une notification d'erreur
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        
        const container = document.querySelector('.rapports-container');
        container.insertBefore(errorDiv, container.firstChild);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }

    renderAllCharts() {
        if (!this.currentData) return;

        // Détruire les graphiques existants
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};

        // Créer tous les graphiques
        this.createPerformanceChauffeurs();
        this.createPerformancePrestataires();
        this.createSuiviKilometrage();
        this.createUtilisationBus();
        this.createCoutsCarburant();
        this.createConsommationMoyenne();
        this.createROIBus();
        this.createHistoriquePannes();
        this.updateTableVidanges();
        this.updateTablePannes();
    }

    createPerformanceChauffeurs() {
        const ctx = document.getElementById('chart-chauffeurs');
        if (!ctx) return;

        const data = this.currentData.performance_chauffeurs || [];
        
        this.charts.chauffeurs = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.nom),
                datasets: [{
                    label: 'Nombre de trajets',
                    data: data.map(item => item.nb_trajets),
                    backgroundColor: 'rgba(37, 99, 235, 0.8)',
                    borderColor: 'rgba(37, 99, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.parsed.y} trajets`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });

        // Mettre à jour les statistiques
        this.updateChartStats('stats-chauffeurs', data, 'nb_trajets', 'trajets');
    }

    createPerformancePrestataires() {
        const ctx = document.getElementById('chart-prestataires');
        if (!ctx) return;

        const data = this.currentData.performance_prestataires || [];
        
        this.charts.prestataires = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.nom_agence),
                datasets: [{
                    data: data.map(item => item.nb_trajets),
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(6, 182, 212, 0.8)',
                        'rgba(139, 92, 246, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.label}: ${context.parsed} trajets`
                        }
                    }
                }
            }
        });

        this.updateChartStats('stats-prestataires', data, 'nb_trajets', 'trajets');
    }

    createSuiviKilometrage() {
        const ctx = document.getElementById('chart-kilometrage');
        if (!ctx) return;

        const data = this.currentData.suivi_kilometrage || [];
        
        this.charts.kilometrage = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.numero),
                datasets: [{
                    label: 'Kilométrage actuel',
                    data: data.map(item => item.kilometrage_actuel),
                    backgroundColor: 'rgba(6, 182, 212, 0.8)',
                    borderColor: 'rgba(6, 182, 212, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.parsed.y.toLocaleString()} km`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => `${value.toLocaleString()} km`
                        }
                    }
                }
            }
        });

        this.updateChartStats('stats-kilometrage', data, 'kilometrage_actuel', 'km');
    }

    createUtilisationBus() {
        const ctx = document.getElementById('chart-utilisation');
        if (!ctx) return;

        const data = this.currentData.utilisation_bus || [];
        
        this.charts.utilisation = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.numero),
                datasets: [{
                    label: 'Nombre de trajets',
                    data: data.map(item => item.nb_trajets),
                    backgroundColor: 'rgba(139, 92, 246, 0.8)',
                    borderColor: 'rgba(139, 92, 246, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });

        this.updateChartStats('stats-utilisation', data, 'nb_trajets', 'trajets');
    }

    createCoutsCarburant() {
        const ctx = document.getElementById('chart-carburant');
        if (!ctx) return;

        const data = this.currentData.couts_carburant?.par_bus || [];
        
        this.charts.carburant = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.numero),
                datasets: [{
                    label: 'Coût carburant (€)',
                    data: data.map(item => item.cout_total),
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    borderColor: 'rgba(245, 158, 11, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.parsed.y.toFixed(2)} €`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => `${value} €`
                        }
                    }
                }
            }
        });

        // Mettre à jour le coût total global
        const coutGlobal = this.currentData.couts_carburant?.cout_global || 0;
        document.getElementById('cout-total-global').textContent = `${coutGlobal.toFixed(2)} €`;
    }

    createConsommationMoyenne() {
        const ctx = document.getElementById('chart-consommation');
        if (!ctx) return;

        const data = this.currentData.consommation_moyenne || [];
        
        this.charts.consommation = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.numero),
                datasets: [
                    {
                        label: 'Consommation théorique',
                        data: data.map(item => item.consommation_theorique),
                        borderColor: 'rgba(16, 185, 129, 1)',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        fill: false
                    },
                    {
                        label: 'Consommation moyenne',
                        data: data.map(item => item.consommation_moyenne),
                        borderColor: 'rgba(239, 68, 68, 1)',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        borderWidth: 2,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.dataset.label}: ${context.parsed.y.toFixed(2)} L`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => `${value} L`
                        }
                    }
                }
            }
        });
    }

    createROIBus() {
        const ctx = document.getElementById('chart-roi');
        if (!ctx) return;

        const data = this.currentData.roi_bus || [];
        
        this.charts.roi = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'ROI (Trajets/Coût)',
                    data: data.map(item => ({
                        x: item.cout_carburant,
                        y: item.nb_trajets,
                        label: item.numero
                    })),
                    backgroundColor: 'rgba(37, 99, 235, 0.6)',
                    borderColor: 'rgba(37, 99, 235, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const point = context.raw;
                                return `${point.label}: ${point.y} trajets, ${point.x.toFixed(2)} € carburant`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Coût carburant (€)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Nombre de trajets'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createHistoriquePannes() {
        const ctx = document.getElementById('chart-pannes');
        if (!ctx) return;

        const data = this.currentData.budget_maintenance?.par_criticite || [];
        
        this.charts.pannes = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.map(item => item.criticite),
                datasets: [{
                    data: data.map(item => item.nb_pannes),
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',   // HAUTE
                        'rgba(245, 158, 11, 0.8)',  // MOYENNE
                        'rgba(6, 182, 212, 0.8)'    // FAIBLE
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.label}: ${context.parsed} pannes`
                        }
                    }
                }
            }
        });
    }

    updateTableVidanges() {
        const tbody = document.getElementById('tbody-vidanges');
        const data = this.currentData.planning_vidanges || [];
        
        tbody.innerHTML = '';
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">Aucune vidange urgente</td></tr>';
            return;
        }

        data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.numero}</td>
                <td>${item.kilometrage_actuel.toLocaleString()} km</td>
                <td>${item.km_critique.toLocaleString()} km</td>
                <td>${item.km_restants.toLocaleString()} km</td>
                <td>${item.derniere_vidange}</td>
                <td><span class="badge badge-${item.urgence.toLowerCase()}">${item.urgence}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    updateTablePannes() {
        const tbody = document.getElementById('tbody-pannes');
        const data = this.currentData.historique_pannes || [];
        
        tbody.innerHTML = '';
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">Aucune panne récente</td></tr>';
            return;
        }

        data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.numero_aed}</td>
                <td>${item.date_heure}</td>
                <td><span class="badge badge-${item.criticite.toLowerCase()}">${item.criticite}</span></td>
                <td>${item.description}</td>
                <td>${item.immobilisation ? '<i class="fas fa-check text-danger"></i>' : '<i class="fas fa-times text-success"></i>'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    updateChartStats(containerId, data, valueKey, unit) {
        const container = document.getElementById(containerId);
        if (!container || !data.length) return;

        const values = data.map(item => item[valueKey]);
        const total = values.reduce((sum, val) => sum + val, 0);
        const average = total / values.length;
        const max = Math.max(...values);
        const min = Math.min(...values);

        container.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">Total :</span>
                <span class="stat-value">${total.toLocaleString()} ${unit}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Moyenne :</span>
                <span class="stat-value">${average.toFixed(1)} ${unit}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Maximum :</span>
                <span class="stat-value">${max.toLocaleString()} ${unit}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Minimum :</span>
                <span class="stat-value">${min.toLocaleString()} ${unit}</span>
            </div>
        `;
    }

    updateSummary() {
        if (!this.currentData) return;

        // Flotte active
        const flotteActive = this.currentData.suivi_kilometrage?.length || 0;
        document.getElementById('resume-flotte').textContent = flotteActive;

        // Trajets période
        const trajetsTotal = (this.currentData.performance_chauffeurs || [])
            .reduce((sum, item) => sum + item.nb_trajets, 0);
        document.getElementById('resume-trajets').textContent = trajetsTotal;

        // Coût carburant
        const coutTotal = this.currentData.couts_carburant?.cout_global || 0;
        document.getElementById('resume-cout').textContent = `${coutTotal.toFixed(0)} €`;

        // Alertes maintenance
        const alertes = this.currentData.planning_vidanges?.length || 0;
        document.getElementById('resume-alertes').textContent = alertes;
    }

    toggleSection(targetId, button) {
        const content = document.getElementById(targetId);
        const isCollapsed = content.classList.contains('collapsed');
        
        if (isCollapsed) {
            content.classList.remove('collapsed');
            button.classList.remove('collapsed');
        } else {
            content.classList.add('collapsed');
            button.classList.add('collapsed');
        }
    }

    exportToPDF() {
        // Fonction d'export PDF (nécessiterait une librairie comme jsPDF)
        alert('Fonctionnalité d\'export PDF à implémenter avec jsPDF');
    }
}

// Initialiser l'application quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    new RapportsManager();
});