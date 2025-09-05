/**
 * RAPPORTS & ANALYSES - JavaScript
 * Gestion des graphiques et interactions
 */

// Variables globales
let charts = {};
let currentPeriod = '7';

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventListeners();
    loadInitialData();
});

/**
 * Configuration et initialisation des graphiques
 */
function initializeCharts() {
    // Configuration globale Chart.js
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#495057';

    // Initialiser chaque graphique
    initTrajetsEvolutionChart();
    initPassagersTypeChart();
    initFleetUtilizationChart();
    initFuelCostsChart();
}

/**
 * Graphique d'évolution des trajets
 */
function initTrajetsEvolutionChart() {
    const ctx = document.getElementById('trajetsEvolutionChart');
    if (!ctx) return;

    charts.trajetsEvolution = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#e9ecef'
                    }
                },
                x: {
                    grid: {
                        color: '#e9ecef'
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6
                }
            }
        }
    });
}

/**
 * Graphique répartition des passagers
 */
function initPassagersTypeChart() {
    const ctx = document.getElementById('passagersTypeChart');
    if (!ctx) return;

    charts.passagersType = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

/**
 * Graphique utilisation de la flotte
 */
function initFleetUtilizationChart() {
    const ctx = document.getElementById('fleetUtilizationChart');
    if (!ctx) return;

    charts.fleetUtilization = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#e9ecef'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Graphique coûts carburant
 */
function initFuelCostsChart() {
    const ctx = document.getElementById('fuelCostsChart');
    if (!ctx) return;

    charts.fuelCosts = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#e9ecef'
                    },
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('fr-FR', {
                                minimumFractionDigits: 0
                            }).format(value) + ' FCFA';
                        }
                    }
                },
                x: {
                    grid: {
                        color: '#e9ecef'
                    }
                }
            }
        }
    });
}

/**
 * Configuration des événements
 */
function setupEventListeners() {
    // Bouton actualiser
    const refreshBtn = document.getElementById('refresh-data');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            refreshAllData();
        });
    }

    // Bouton export PDF
    const exportBtn = document.getElementById('export-pdf');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            exportToPDF();
        });
    }

    // Contrôles de période pour les graphiques
    document.querySelectorAll('.chart-controls .btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const period = this.dataset.period;
            if (period) {
                updateChartPeriod(period);

                // Mise à jour des boutons actifs
                this.parentElement.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
}

/**
 * Chargement initial des données
 */
function loadInitialData() {
    showLoading();

    const tasks = [];

    // Ne charger que les graphiques présents
    if (charts.trajetsEvolution) {
        tasks.push(
            loadChartData('trajets_evolution').then(data => updateChart('trajetsEvolution', data))
        );
    }
    if (charts.passagersType) {
        tasks.push(
            loadChartData('passagers_type').then(data => updateChart('passagersType', data))
        );
    }
    if (charts.fleetUtilization) {
        // Charger uniquement si le canvas/graph existe et si l'API est disponible côté serveur
        tasks.push(
            loadChartData('utilisation_flotte').then(data => updateChart('fleetUtilization', data))
        );
    }
    if (charts.fuelCosts) {
        tasks.push(
            loadChartData('couts_carburant').then(data => updateChart('fuelCosts', data))
        );
    }

    if (tasks.length === 0) {
        hideLoading();
        return;
    }

    Promise.all(tasks)
        .then(() => hideLoading())
        .catch(error => {
            console.error('Erreur lors du chargement des données:', error);
            hideLoading();
            // Ne pas afficher d'erreur globale si certaines sections ne sont pas présentes
        });
}

/**
 * Chargement des données via API
 */
async function loadChartData(chartType) {
    try {
        const response = await fetch(`/admin/rapports/api/chart/${chartType}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Erreur lors du chargement de ${chartType}:`, error);
        throw error;
    }
}

/**
 * Mise à jour d'un graphique
 */
function updateChart(chartName, data) {
    const chart = charts[chartName];
    if (!chart || !data) return;

    chart.data = data;
    chart.update('active');
}

/**
 * Actualisation de toutes les données
 */
function refreshAllData() {
    const refreshBtn = document.getElementById('refresh-data');
    const originalText = refreshBtn.innerHTML;

    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualisation...';
    refreshBtn.disabled = true;

    // Actualiser les statistiques
    refreshStats();

    // Actualiser les graphiques
    loadInitialData().finally(() => {
        refreshBtn.innerHTML = originalText;
        refreshBtn.disabled = false;
    });
}

/**
 * Actualisation des statistiques rapides
 */
async function refreshStats() {
    try {
        const periods = ['today', 'week', 'month', 'fleet'];

        for (const period of periods) {
            const response = await fetch(`/admin/rapports/api/stats/${period}`);
            if (response.ok) {
                const data = await response.json();
                updateStatsDisplay(period, data);
            }
        }
    } catch (error) {
        console.error('Erreur lors de l\'actualisation des statistiques:', error);
    }
}

/**
 * Mise à jour de l'affichage des statistiques
 */
function updateStatsDisplay(period, data) {
    const elements = {
        [`${period}-trajets`]: data.total_trajets || 0,
        [`${period}-passagers`]: data.total_passagers || 0
    };

    // Cas spécial pour la flotte
    if (period === 'fleet') {
        elements['fleet-actifs'] = `${data.bus_actifs}/${data.total_bus}`;
        elements['fleet-km'] = new Intl.NumberFormat('fr-FR').format(data.km_total || 0);
    }

    // Mettre à jour les éléments DOM
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

/**
 * Mise à jour de la période des graphiques
 */
function updateChartPeriod(period) {
    currentPeriod = period;
    loadInitialData();
}

/**
 * Export PDF (placeholder)
 */
function exportToPDF() {
    alert('Fonctionnalité d\'export PDF en cours de développement');
}

/**
 * Affichage du loading
 */
function showLoading() {
    // Créer overlay si n'existe pas
    let overlay = document.getElementById('loadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Chargement des données...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    overlay.style.display = 'flex';
}

/**
 * Masquage du loading
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Affichage d'erreur
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        padding: 1rem;
        background: #dc3545;
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        ${message}
        <button type="button" style="background:none;border:none;color:white;margin-left:10px;cursor:pointer;" onclick="this.parentElement.remove()">×</button>
    `;

    document.body.appendChild(errorDiv);

    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}