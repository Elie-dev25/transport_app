/**
 * Gestion de la modal Trajet Interne UdM
 */

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('trajetInterneModal');
    const openBtn = document.getElementById('openTrajetInterneModal');
    const closeBtn = document.getElementById('closeTrajetInterneModal');
    const cancelBtn = document.getElementById('cancelTrajetInterne');
    const form = document.getElementById('trajetInterneForm');

    // Ouvrir la modal
    if (openBtn) {
        openBtn.addEventListener('click', function(e) {
            e.preventDefault();
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
    }

    // Fermer la modal
    function closeModal() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        // Réinitialiser le formulaire
        if (form) {
            form.reset();
        }
        // Masquer les erreurs
        const errorDiv = document.getElementById('trajetInterneError');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeModal);
    }

    // Fermer en cliquant à l'extérieur
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Fermer avec Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
    });

    // Gestion de la soumission du formulaire
    if (form) {
        form.addEventListener('submit', function(e) {
            // Validation basique
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                const errorDiv = document.getElementById('trajetInterneError');
                if (errorDiv) {
                    errorDiv.textContent = 'Veuillez remplir tous les champs obligatoires.';
                    errorDiv.style.display = 'block';
                }
                return false;
            }

            // Si validation OK, le formulaire sera soumis normalement
        });
    }
});
