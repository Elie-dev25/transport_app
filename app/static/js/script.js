// Animation & design JS partagé
function openVidangeModal(busId, numeroVehicule, demandeurNom) {
    window.currentBusId = busId || null;
    window.currentNumeroVehicule = numeroVehicule || '';
    document.getElementById('fiche-numero-demande').textContent = 'DEM-' + (new Date()).getTime();
    const now = new Date();
    document.getElementById('fiche-date-heure').textContent = now.toLocaleDateString() + ' ' + now.toLocaleTimeString();
    document.getElementById('fiche-demandeur').textContent = demandeurNom || '-';
    document.getElementById('fiche-numero-vehicule').textContent = window.currentNumeroVehicule || '-';
    document.getElementById('ficheVidangeModal').classList.add('show');
    document.getElementById('ficheVidangeModal').setAttribute('aria-hidden', 'false');
}

function closeVidangeModal() {
    document.getElementById('ficheVidangeModal').classList.remove('show');
    document.getElementById('ficheVidangeModal').setAttribute('aria-hidden', 'true');
}

function openFormulaireVidange(busId = null) {
    const aedId = busId || window.currentBusId;
    if (!aedId) {
        alert('Erreur : aucun véhicule sélectionné. Veuillez ouvrir la fiche de vidange avant de confirmer.');
        return;
    }
    document.getElementById('numero_aed').value = window.currentNumeroVehicule || '';
    document.getElementById('aed_id_hidden').value = aedId;
    document.getElementById('formulaireVidangeModal').classList.add('show');
    document.getElementById('formulaireVidangeModal').setAttribute('aria-hidden', 'false');
}

function closeFormulaireVidangeModal() {
    document.getElementById('formulaireVidangeModal').classList.remove('show');
    document.getElementById('formulaireVidangeModal').setAttribute('aria-hidden', 'true');
}

function printFicheVidange() {
    const content = document.getElementById('fiche-vidange-content').innerHTML;
    const w = window.open('', '_blank');
    w.document.write('<html><head><title>Fiche Vidange</title>');
    w.document.write('</head><body>');
    w.document.write(content);
    w.document.write('</body></html>');
    w.document.close();
    w.focus();
    setTimeout(() => { w.print(); w.close(); }, 300);
}

// --------- Carburation: UI-only helpers (modale & calcul) ---------
function openCarburationModal(aedId, numeroAED, effectuePar) {
    const aedIdEl = document.getElementById('modalAedId');
    const numeroEl = document.getElementById('modalNumeroAED');
    const effectueParEl = document.getElementById('modalEffectuePar');
    const modal = document.getElementById('carburationModal');
    if (!aedIdEl || !numeroEl || !effectueParEl || !modal) return;
    aedIdEl.value = aedId;
    numeroEl.value = numeroAED;
    effectueParEl.value = effectuePar;
    const fieldsToClear = ['modalKilometrage','modalQuantite','modalPrixUnitaire','modalCoutTotal','modalRemarque'];
    fieldsToClear.forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    modal.style.display = 'flex';
}

function closeCarburationModal() {
    const modal = document.getElementById('carburationModal');
    if (modal) modal.style.display = 'none';
}

function calculateTotal() {
    const qEl = document.getElementById('modalQuantite');
    const pEl = document.getElementById('modalPrixUnitaire');
    const tEl = document.getElementById('modalCoutTotal');
    if (!qEl || !pEl || !tEl) return;
    const quantite = parseFloat(qEl.value) || 0;
    const prixUnitaire = parseFloat(pEl.value) || 0;
    const total = quantite * prixUnitaire;
    tEl.value = total.toFixed(0);
}

async function filterHistorique(numeroAED) {
    const url = new URL(window.location);
    if (numeroAED) url.searchParams.set('numero_aed', numeroAED);
    else url.searchParams.delete('numero_aed');
    // Optional date range for carburation page
    const d1 = document.getElementById('carb_date_debut');
    const d2 = document.getElementById('carb_date_fin');
    const v1 = d1 && d1.value ? d1.value : '';
    const v2 = d2 && d2.value ? d2.value : '';
    if (v1) url.searchParams.set('date_debut', v1); else url.searchParams.delete('date_debut');
    if (v2) url.searchParams.set('date_fin', v2); else url.searchParams.delete('date_fin');

    try {
        setLoadingState('carb', true);
        const fetchUrl = new URL(url.toString());
        fetchUrl.searchParams.set('_', Date.now());
        const res = await fetch(fetchUrl.toString(), { headers: { 'X-Requested-With': 'fetch' }, cache: 'no-store' });
        const html = await res.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTbody = doc.querySelector('#historique-carb-body');
        const currentTbody = document.querySelector('#historique-carb-body');
        if (newTbody && currentTbody) {
            currentTbody.innerHTML = newTbody.innerHTML;
            // Clean URL (without cache-busting param)
            history.pushState({}, '', url);
        } else {
            // Fallback: if selector not found, do full reload
            window.location = url;
        }
    } catch (e) {
        window.location = url;
    } finally {
        setLoadingState('carb', false);
    }
}

async function filterHistoriqueVidange(numeroAED) {
    const url = new URL(window.location);
    if (numeroAED) url.searchParams.set('numero_aed', numeroAED);
    else url.searchParams.delete('numero_aed');
    // Optional date range for vidange page
    const d1 = document.getElementById('vid_date_debut');
    const d2 = document.getElementById('vid_date_fin');
    const v1 = d1 && d1.value ? d1.value : '';
    const v2 = d2 && d2.value ? d2.value : '';
    if (v1) url.searchParams.set('date_debut', v1); else url.searchParams.delete('date_debut');
    if (v2) url.searchParams.set('date_fin', v2); else url.searchParams.delete('date_fin');

    try {
        setLoadingState('vid', true);
        const fetchUrl = new URL(url.toString());
        fetchUrl.searchParams.set('_', Date.now());
        const res = await fetch(fetchUrl.toString(), { headers: { 'X-Requested-With': 'fetch' }, cache: 'no-store' });
        const html = await res.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTbody = doc.querySelector('#historique-vid-body');
        const currentTbody = document.querySelector('#historique-vid-body');
        if (newTbody && currentTbody) {
            currentTbody.innerHTML = newTbody.innerHTML;
            history.pushState({}, '', url);
        } else {
            window.location = url;
        }
    } catch (e) {
        window.location = url;
    } finally {
        setLoadingState('vid', false);
    }
}

function setLoadingState(scope, loading) {
    const loader = document.getElementById(scope === 'carb' ? 'carb_loader' : 'vid_loader');
    if (loader) loader.style.display = loading ? 'inline-flex' : 'none';
    // disable relevant inputs
    if (scope === 'carb') {
        const select = document.getElementById('carb_numero_select');
        const d1 = document.getElementById('carb_date_debut');
        const d2 = document.getElementById('carb_date_fin');
        [select, d1, d2].forEach(el => { if (el) el.disabled = loading; });
    } else {
        const select = document.getElementById('numero_aed');
        const d1 = document.getElementById('vid_date_debut');
        const d2 = document.getElementById('vid_date_fin');
        [select, d1, d2].forEach(el => { if (el) el.disabled = loading; });
    }
}

function clearHistoriqueFilters() {
    const baseUrl = window.location.origin + window.location.pathname;
    window.location = baseUrl; // force full reload without any params
}

function clearHistoriqueVidangeFilters() {
    const baseUrl = window.location.origin + window.location.pathname;
    window.location = baseUrl;
}

// Safe bindings for inputs (only if present on the page)
document.addEventListener('DOMContentLoaded', () => {
    const qEl = document.getElementById('modalQuantite');
    const pEl = document.getElementById('modalPrixUnitaire');
    if (qEl) qEl.addEventListener('input', calculateTotal);
    if (pEl) pEl.addEventListener('input', calculateTotal);

    // Bind carburation buttons (no inline onclick)
    const carbBtns = document.querySelectorAll('.btn-carburation[data-aed-id]');
    carbBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const aedId = btn.getAttribute('data-aed-id');
            const numero = btn.getAttribute('data-numero');
            const effectuePar = btn.getAttribute('data-effectue-par');
            openCarburationModal(aedId, numero, effectuePar);
        });
    });

    // Bind vidange buttons (no inline onclick)
    const vidangeBtns = document.querySelectorAll('button[data-open-vidange="1"][data-bus-id]');
    vidangeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const busId = btn.getAttribute('data-bus-id');
            const numero = btn.getAttribute('data-numero');
            const demandeur = btn.getAttribute('data-demandeur');
            openVidangeModal(busId, numero, demandeur);
        });
    });

    // Carburation modal close bindings
    const closeCarbBtn = document.querySelector('[data-close-carburation="1"]');
    if (closeCarbBtn) closeCarbBtn.addEventListener('click', closeCarburationModal);

    const carbOverlay = document.getElementById('carburationModal');
    if (carbOverlay) {
        carbOverlay.addEventListener('click', (e) => {
            if (e.target === carbOverlay) closeCarburationModal();
        });
    }

    // Delegated handler (robust in case of dynamic renderings)
    document.addEventListener('click', (e) => {
        // Close by data attribute
        const closeBtn = e.target.closest('[data-close-carburation="1"]');
        if (closeBtn) {
            e.preventDefault();
            return closeCarburationModal();
        }
        // Close by .modal-close inside the carburation modal
        const carbModal = document.getElementById('carburationModal');
        if (carbModal && carbModal.contains(e.target)) {
            const closeIcon = e.target.closest('.modal-close');
            if (closeIcon) {
                e.preventDefault();
                return closeCarburationModal();
            }
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeCarburationModal();
    });
});
