// JS pour la modale Départ de Banekane (Retour)
// Affichage dynamique des champs selon le type de bus sélectionné

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('departBanekaneRetourModal');
    const openBtn = document.querySelector('a[href="#"], .action-btn'); // à adapter si besoin
    const closeBtn = document.getElementById('closeDepartBanekaneRetourModal');
    const form = document.getElementById('departBanekaneRetourForm');
    const feedback = document.getElementById('departBanekaneRetourFeedback');
    const errorAlert = document.getElementById('departBanekaneRetourError');
    const typeBusRadios = form.querySelectorAll('input[name="type_bus"]');

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
    if (closeBtn) closeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        hideModal();
    });
    // Ouvre la modale sur clic bouton (corriger le sélecteur si besoin)
    const openBanekaneBtn = document.querySelector('#openDepartBanekaneRetourModal');
    if (openBanekaneBtn) openBanekaneBtn.addEventListener('click', function(e) {
        e.preventDefault();
        showModal();
    });
    // Affichage dynamique des champs selon type de bus
    function getSelectedTypeBus() {
        let val = null;
        typeBusRadios.forEach(radio => {
            if (radio.checked) val = radio.value;
        });
        return val;
    }
    function updateFields() {
        const typeBus = getSelectedTypeBus();
        // Masquer tous les champs spécifiques d'abord
        document.querySelectorAll('.aed-only').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.agence-only').forEach(el => {
            el.style.display = 'none';
        });
        // Afficher uniquement ceux du type sélectionné
        if (typeBus === 'AED') {
            document.querySelectorAll('.aed-only').forEach(el => {
                el.style.display = '';
            });
        } else if (typeBus === 'AGENCE') {
            document.querySelectorAll('.agence-only').forEach(el => {
                el.style.display = '';
            });
        }
    }
    if (typeBusRadios.length > 0) {
        typeBusRadios.forEach(radio => {
            radio.addEventListener('change', updateFields);
        });
        updateFields(); // initial
    }
    // Gestion submit AJAX
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
    // Animation CSS loader si pas déjà présent
    if (!document.getElementById('departBanekaneRetourLoaderStyle')) {
        const style = document.createElement('style');
        style.id = 'departBanekaneRetourLoaderStyle';
        style.innerHTML = `.loader {\n  display: inline-block;\n  width: 18px;\n  height: 18px;\n  border: 3px solid #01D758;\n  border-radius: 50%;\n  border-top: 3px solid #e8f4f8;\n  animation: spin 0.7s linear infinite;\n  vertical-align: middle;\n}\n@keyframes spin {\n  0% { transform: rotate(0deg); }\n  100% { transform: rotate(360deg); }\n}`;
        document.head.appendChild(style);
    }
});
