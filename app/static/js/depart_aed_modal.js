// AJAX submit for Départ AED modal


    const openBtn = document.getElementById('openDepartAedModal');
    const modal = document.getElementById('departAedModal');
    const closeBtn = document.getElementById('closeDepartAedModal');
    const form = document.getElementById('departAedForm');
    const feedback = document.getElementById('departAedFeedback');
    const errorAlert = document.getElementById('departAedError');

    function showModal() {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        if (feedback) feedback.innerHTML = '';
        if (errorAlert) errorAlert.style.display = 'none';
    }
    function hideModal() {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
    if (openBtn) openBtn.addEventListener('click', function(e) { e.preventDefault(); console.log('Clic bouton AED !'); showModal(); });
else console.error('Bouton #openDepartAedModal introuvable !');
    if (closeBtn) closeBtn.addEventListener('click', hideModal);
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) hideModal();
        });
    }
    if (form) {
        form.addEventListener('submit', function(e) {
            // Validation simple exemple :
            const dateHeure = document.getElementById('date_heure_depart').value;
            const pointDepart = document.getElementById('point_depart').value;
            const nombrePlacesInput = form.querySelector('[name="nombre_places_occupees"]');
            const nombrePlaces = nombrePlacesInput ? nombrePlacesInput.value : null;
            if (!dateHeure || !pointDepart || (nombrePlacesInput && !nombrePlaces)) {
                if (errorAlert) {
                    errorAlert.innerHTML = '<ul>' +
                        (!dateHeure ? '<li>Date et heure de départ : Ce champ est requis.</li>' : '') +
                        (!pointDepart ? '<li>Point de départ : Ce champ est requis.</li>' : '') +
                        (nombrePlacesInput && !nombrePlaces ? '<li>Nombre de places occupées : Ce champ est requis.</li>' : '') +
                        '</ul>';
                    errorAlert.style.display = 'block';
                }
                e.preventDefault();
                return;
            }
            if (errorAlert) errorAlert.style.display = 'none';
            // Soumission AJAX
            e.preventDefault();
            feedback.innerHTML = '<div class="loader"></div> <span style="margin-left:10px">Envoi en cours...</span>';
            const formData = new FormData(form);
            fetch(form.action, {  // au lieu de ''
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
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

// Animation CSS loader
if (!document.getElementById('departAedLoaderStyle')) {
    const style = document.createElement('style');
    style.id = 'departAedLoaderStyle';
    style.innerHTML = `.loader {
      display: inline-block;
      width: 18px;
      height: 18px;
      border: 3px solid #01D758;
      border-radius: 50%;
      border-top: 3px solid #e8f4f8;
      animation: spin 0.7s linear infinite;
      vertical-align: middle;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }`;
    document.head.appendChild(style);
}

