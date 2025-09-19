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
                    // Rafraîchir les données si fonction disponible
                    if (typeof refreshDashboardStats === 'function') {
                        refreshDashboardStats();
                    } else {
                        location.reload();
                    }
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