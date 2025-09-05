// Gestion des dépannages
document.addEventListener('DOMContentLoaded', function() {
    console.log('Module dépannage chargé');

    // Initialiser les événements de la modale de dépannage
    initDepannageModal();

    // Initialiser le formulaire de dépannage
    initDepannageForm();

    // Fermer avec la touche Echap
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal('formulaireDepannageModal');
        }
    });
});

function initDepannageModal() {
    // Boutons pour ouvrir la modale
    const buttons = document.querySelectorAll('.btn-open-depannage');
    console.log('Boutons dépannage trouvés:', buttons.length);
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            console.log('Ouverture modale dépannage');
            
            const panneId = this.dataset.panneId;
            const numero = this.dataset.numero;
            const immat = this.dataset.immatriculation || '';
            
            // Remplir les champs
            document.getElementById('panne_id_hidden').value = panneId || '';
            document.getElementById('numero_bus_udm_dep').value = numero || '';
            document.getElementById('immatriculation_dep').value = immat;
            document.getElementById('kilometrage_dep').value = '';
            document.getElementById('cout_reparation_dep').value = '';
            document.getElementById('description_panne_dep').value = '';
            document.getElementById('cause_panne_dep').value = '';
            
            // Ouvrir la modale
            openModal('formulaireDepannageModal');
        });
    });

    // Délégation d'événement (sécurité si les boutons sont ajoutés dynamiquement)
    document.addEventListener('click', function(e) {
        const trigger = e.target.closest('.btn-open-depannage');
        if (!trigger) return;
        console.log('[Delegated] Ouverture modale dépannage');

        const panneId = trigger.dataset.panneId;
        const numero = trigger.dataset.numero;
        const immat = trigger.dataset.immatriculation || '';

        const hid = document.getElementById('panne_id_hidden');
        const num = document.getElementById('numero_bus_udm_dep');
        const imm = document.getElementById('immatriculation_dep');
        if (!hid || !num || !imm) {
            console.error('Champs du formulaire de dépannage introuvables');
            return;
        }

        hid.value = panneId || '';
        num.value = numero || '';
        imm.value = immat;
        const kilo = document.getElementById('kilometrage_dep');
        const cout = document.getElementById('cout_reparation_dep');
        const desc = document.getElementById('description_panne_dep');
        const cause = document.getElementById('cause_panne_dep');
        if (kilo) kilo.value = '';
        if (cout) cout.value = '';
        if (desc) desc.value = '';
        if (cause) cause.value = '';

        openModal('formulaireDepannageModal');
    });
    
    // Bouton fermer
    const closeBtn = document.getElementById('closeDepannageModal');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            closeModal('formulaireDepannageModal');
        });
    }

    // Fermer en cliquant sur l'arrière-plan
    const modal = document.getElementById('formulaireDepannageModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal('formulaireDepannageModal');
            }
        });
    } else {
        console.warn('Modale formulaireDepannageModal introuvable dans le DOM');
    }
}

function initDepannageForm() {
    const form = document.getElementById('formulaire-depannage');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        // Fermer immédiatement la modale pour une meilleure UX
        closeModal('formulaireDepannageModal');
        // Désactiver le bouton pour éviter les doubles clics
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        
        const payload = {
            panne_id: document.getElementById('panne_id_hidden').value,
            numero_bus_udm: document.getElementById('numero_bus_udm_dep').value,
            immatriculation: document.getElementById('immatriculation_dep').value,
            kilometrage: document.getElementById('kilometrage_dep').value,
            cout_reparation: document.getElementById('cout_reparation_dep').value,
            description_panne: document.getElementById('description_panne_dep').value,
            cause_panne: document.getElementById('cause_panne_dep').value
        };
        
        try {
            const response = await fetch('/admin/enregistrer_depannage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                Swal.fire({
                    title: 'Succès!',
                    text: 'Réparation enregistrée avec succès.',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    location.reload();
                });
            } else {
                Swal.fire({
                    title: 'Erreur!',
                    text: data.message || 'Erreur lors de l\'enregistrement.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        } catch (error) {
            console.error('Erreur:', error);
            Swal.fire({
                title: 'Erreur!',
                text: 'Erreur réseau.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        } finally {
            if (submitBtn) submitBtn.disabled = false;
        }
    });
}

// Helpers génériques d'ouverture/fermeture de modale (fallback si non définis globalement)
function openModal(id) {
    const el = document.getElementById(id);
    if (!el) {
        console.error('openModal: élément non trouvé pour id =', id);
        return;
    }
    // Utiliser le système CSS: .modal.show + aria-hidden="false"
    el.classList.add('show');
    el.setAttribute('aria-hidden', 'false');
    // Retirer l'attribut hidden pour éviter tout masquage par le navigateur
    if (el.hasAttribute('hidden')) {
        el.removeAttribute('hidden');
    }
    // Fallback pour anciens styles si nécessaires
    el.style.display = 'flex';
    document.body.classList.add('modal-open');
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (!el) {
        console.error('closeModal: élément non trouvé pour id =', id);
        return;
    }
    el.classList.remove('show');
    el.setAttribute('aria-hidden', 'true');
    // Fallback
    el.style.display = 'none';
    // Ré-appliquer l'attribut hidden pour éviter le flash au prochain chargement
    if (!el.hasAttribute('hidden')) {
        el.setAttribute('hidden', '');
    }
    document.body.classList.remove('modal-open');
}

// Filtrage de l'historique des dépannages
function filterHistoriqueDepannage(selectedBus) {
    const dateDebut = document.getElementById('dep_date_debut').value;
    const dateFin = document.getElementById('dep_date_fin').value;
    const loader = document.getElementById('dep_loader');
    
    loader.style.display = 'flex';
    
    setTimeout(() => {
        const rows = document.querySelectorAll('#depannages-table tbody tr');
        rows.forEach(row => {
            const bus = row.dataset.bus;
            const date = row.dataset.date;
            
            let showRow = true;
            
            if (selectedBus && bus !== selectedBus) {
                showRow = false;
            }
            
            if (dateDebut && date < dateDebut) {
                showRow = false;
            }
            if (dateFin && date > dateFin) {
                showRow = false;
            }
            
            row.style.display = showRow ? '' : 'none';
        });
        
        loader.style.display = 'none';
    }, 200);
}

function clearHistoriqueDepannageFilters() {
    document.getElementById('dep_numero_select').value = '';
    document.getElementById('dep_date_debut').value = '';
    document.getElementById('dep_date_fin').value = '';
    filterHistoriqueDepannage('');
}
