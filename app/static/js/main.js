/**
 * GESTIONNAIRE UNIFIÉ DES FORMULAIRES MODAUX
 * Système centralisé pour la gestion des confirmations et erreurs
 * Référence : SweetAlert2 pour les succès, erreurs dans formulaire pour les échecs
 */

class FormModalManager {
    /**
     * Soumet un formulaire modal avec gestion unifiée des réponses
     * @param {HTMLFormElement} form - Le formulaire à soumettre
     * @param {string} modalId - ID de la modal à fermer en cas de succès
     * @param {string} errorContainerId - ID du conteneur d'erreur dans le formulaire
     * @param {string} successMessage - Message de succès personnalisé (optionnel)
     */
    static async submitModalForm(form, modalId, errorContainerId, successMessage = null) {
        const errorContainer = document.getElementById(errorContainerId);
        const submitBtn = form.querySelector('button[type="submit"]');

        // Masquer les erreurs précédentes
        if (errorContainer) {
            errorContainer.style.display = 'none';
            errorContainer.textContent = '';
        }

        // Désactiver le bouton de soumission
        if (submitBtn) {
            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Envoi...';
        }

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // ✅ SUCCÈS : Fermer modal + SweetAlert2
                this.closeModal(modalId);
                form.reset();

                Swal.fire({
                    title: 'Succès!',
                    text: successMessage || data.message || 'Opération réalisée avec succès.',
                    icon: 'success',
                    confirmButtonText: 'OK',
                    timer: 3000,
                    timerProgressBar: true
                }).then(() => {
                    // Pour éviter les problèmes de doublement, recharger la page après un court délai
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                });

            } else {
                // ❌ ÉCHEC : Garder modal ouverte + afficher erreur
                this.showFormError(errorContainer, data.message || 'Erreur lors de la soumission.');
            }

        } catch (error) {
            console.error('Erreur réseau:', error);
            this.showFormError(errorContainer, 'Erreur réseau. Veuillez réessayer.');
        } finally {
            // Réactiver le bouton
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        }
    }

    /**
     * Ferme une modal
     */
    static closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            modal.setAttribute('hidden', '');
            document.body.style.overflow = '';
        }
    }

    /**
     * Affiche une erreur dans le formulaire
     */
    static showFormError(errorContainer, message) {
        if (errorContainer) {
            errorContainer.textContent = message;
            errorContainer.style.display = 'block';
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Rafraîchit les données de la page sans rechargement complet
     */
    static refreshPageData() {
        // Rafraîchir les tableaux de données
        const tables = document.querySelectorAll('.table tbody');
        tables.forEach(table => {
            // Ajouter une classe pour indiquer le rafraîchissement
            table.classList.add('refreshing');
        });

        // Rafraîchir les statuts des chauffeurs via AJAX
        this.refreshChauffeurStatuts();

        // Rafraîchir les badges de statut
        const statusBadges = document.querySelectorAll('.status-badge, .statut-clickable');
        statusBadges.forEach(badge => {
            badge.classList.add('updated');
            setTimeout(() => badge.classList.remove('updated'), 1000);
        });

        // Retirer l'indicateur de rafraîchissement après un délai
        setTimeout(() => {
            tables.forEach(table => {
                table.classList.remove('refreshing');
            });
        }, 500);
    }

    /**
     * Rafraîchit les statuts des chauffeurs via AJAX
     */
    static async refreshChauffeurStatuts() {
        try {
            // Récupérer les données mises à jour
            const response = await fetch('/admin/get_chauffeurs_planning_ajax');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.planning) {
                    // Mettre à jour les statuts dans le tableau
                    this.updateChauffeurStatusInTable(data.planning);
                }
            }
        } catch (error) {
            console.log('Rafraîchissement des statuts en arrière-plan échoué:', error);
        }
    }

    /**
     * Met à jour les statuts des chauffeurs dans le tableau
     */
    static updateChauffeurStatusInTable(planningData) {
        planningData.forEach(chauffeur => {
            const rows = document.querySelectorAll(`tr[data-chauffeur-id="${chauffeur.chauffeur_id}"]`);
            rows.forEach(row => {
                const statutCell = row.querySelector('td:nth-child(5)'); // Colonne statut
                const lieuCell = row.querySelector('td:nth-child(6)'); // Colonne lieu

                if (statutCell) {
                    // IMPORTANT: Vider complètement le contenu avant de le remplacer
                    statutCell.innerHTML = '';

                    // Mettre à jour le statut
                    if (chauffeur.statuts && chauffeur.statuts.length > 0) {
                        statutCell.innerHTML = this.generateStatutHTML(chauffeur.statuts);
                    } else {
                        statutCell.innerHTML = '<span class="status-badge secondary"><i class="fas fa-question-circle"></i> Attente</span>';
                    }
                }

                if (lieuCell) {
                    // IMPORTANT: Vider complètement le contenu avant de le remplacer
                    lieuCell.innerHTML = '';

                    if (chauffeur.statuts && chauffeur.statuts.length > 0) {
                        // Mettre à jour le lieu
                        lieuCell.innerHTML = this.generateLieuHTML(chauffeur.statuts);
                    } else {
                        lieuCell.innerHTML = '<span class="text-muted">Attente</span>';
                    }
                }
            });
        });
    }

    /**
     * Génère le HTML pour l'affichage des statuts
     */
    static generateStatutHTML(statuts) {
        return statuts.map(statut => {
            const statutClass = {
                'CONGE': 'warning',
                'PERMANENCE': 'info',
                'SERVICE_WEEKEND': 'secondary',
                'SERVICE_SEMAINE': 'primary'
            }[statut.statut] || 'secondary';

            const statutIcon = {
                'CONGE': 'calendar-times',
                'PERMANENCE': 'clock',
                'SERVICE_WEEKEND': 'calendar-week',
                'SERVICE_SEMAINE': 'calendar-day'
            }[statut.statut] || 'question-circle';

            const statutLabel = {
                'CONGE': 'Congé',
                'PERMANENCE': 'Permanence',
                'SERVICE_WEEKEND': 'Week-end',
                'SERVICE_SEMAINE': 'Semaine'
            }[statut.statut] || statut.statut;

            return `<span class="status-badge ${statutClass} statut-clickable"
                          data-chauffeur-id="${statut.chauffeur_id}"
                          data-statut="${statut.statut}"
                          data-date-debut="${statut.date_debut}"
                          data-date-fin="${statut.date_fin}"
                          style="cursor: pointer;">
                        <i class="fas fa-${statutIcon}"></i> ${statutLabel}
                    </span>`;
        }).join('<br>');
    }

    /**
     * Génère le HTML pour l'affichage des lieux
     */
    static generateLieuHTML(statuts) {
        return statuts.map(statut => {
            if (!statut.lieu) return '<span class="text-muted">Attente</span>';

            if (statut.lieu === 'CUM') {
                return '<i class="fas fa-building"></i> CUM';
            } else if (statut.lieu === 'CAMPUS') {
                return '<i class="fas fa-university"></i> Campus';
            } else if (statut.lieu === 'CONJOINTEMENT') {
                return 'Conjointement';
            } else {
                return `<span class="text-muted">${statut.lieu}</span>`;
            }
        }).join('<br>');
    }

    /**
     * Réattache tous les événements après mise à jour du DOM
     */
    static reattachEventListeners() {
        // Réattacher les événements des boutons de modification de statut
        document.querySelectorAll('.edit-statut-btn').forEach(btn => {
            // Supprimer les anciens événements pour éviter les doublons
            btn.replaceWith(btn.cloneNode(true));
        });

        // Réattacher les nouveaux événements
        document.querySelectorAll('.edit-statut-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const chauffeurId = this.dataset.id;
                const chauffeurNom = this.dataset.nom;
                const chauffeurPrenom = this.dataset.prenom;

                // Remplir le formulaire
                document.getElementById('chauffeurId').value = chauffeurId;

                // Ouvrir la modal
                const modal = document.getElementById('editStatutChauffeurModal');
                if (modal) {
                    modal.classList.add('show');
                    modal.style.display = 'flex';
                    modal.removeAttribute('hidden');
                    modal.setAttribute('aria-hidden', 'false');
                }
            });
        });

        // Réattacher les événements des statuts cliquables
        document.querySelectorAll('.statut-clickable').forEach(element => {
            element.replaceWith(element.cloneNode(true));
        });

        document.querySelectorAll('.statut-clickable').forEach(element => {
            element.addEventListener('click', function() {
                // Logique pour afficher les détails du statut si nécessaire
                console.log('Statut cliqué:', this.dataset.statut);
            });
        });

        console.log('✅ Événements réattachés avec succès');
    }

    /**
     * Initialise la gestion d'un formulaire modal
     */
    static initModalForm(formId, modalId, errorContainerId, successMessage = null) {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.submitModalForm(form, modalId, errorContainerId, successMessage);
            });
        }
    }
}

// Fonction pour afficher/masquer le menu utilisateur
function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    if (menu) {
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    }
}

// Fermer le menu si on clique ailleurs
document.addEventListener('click', function(event) {
    const menu = document.getElementById('userMenu');
    const trigger = document.querySelector('.user-menu-trigger');

    if (menu && trigger && !trigger.contains(event.target) && !menu.contains(event.target)) {
        menu.style.display = 'none';
    }
});

// Fonction pour fermer les alertes
function closeAlert(element) {
    element.parentNode.removeChild(element);
}