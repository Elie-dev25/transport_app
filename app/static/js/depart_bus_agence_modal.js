document.addEventListener('DOMContentLoaded', function() {
// AJAX submit for Départ Prestataire modal

    const openBtn = document.getElementById('openDepartPrestataireModal');
    const modal = document.getElementById('departPrestataireModal');
    const closeBtn = document.getElementById('closeDepartPrestataireModal');
    const form = document.getElementById('departPrestataireForm');
    const feedback = document.getElementById('departPrestataireFeedback');

    if (openBtn) {
        openBtn.addEventListener('click', function(e) {
            e.preventDefault();
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
            if (feedback) feedback.innerHTML = '';
        });
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        });
    }
    // Fermer si clic sur fond (hors contenu)
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('show');
                document.body.style.overflow = '';
            }
        });
    }
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            feedback.innerHTML = '<div class="loader"></div> <span style="margin-left:10px">Envoi en cours...</span>';
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }).then(response => response.json())
              .then(data => {
                if (data.success) {
    modal.classList.remove('show');
    feedback.innerHTML = '';
    // Notification globale (flash-message)
    document.body.insertAdjacentHTML('beforeend', '<div class="flash-message success">' + data.message + '</div>');
    setTimeout(function() {
        let notif = document.querySelector('.flash-message.success');
        if (notif) notif.remove();
        window.location.reload();
    }, 3000);
    form.reset();
} else {
    modal.classList.remove('show');
    feedback.innerHTML = '';
    document.body.insertAdjacentHTML('beforeend', '<div class="flash-message danger">' + (data.message || 'Erreur lors de l\'enregistrement.') + '</div>');
    setTimeout(function() {
        let notif = document.querySelector('.flash-message.danger');
        if (notif) notif.remove();
    }, 3000);
}
              })
              .catch(() => {
                feedback.innerHTML = '<div class="alert alert-danger">Erreur réseau. Veuillez réessayer.</div>';
              });
        });
    }
});

// Animation CSS loader (réutilise celle définie pour l'autre modal)
