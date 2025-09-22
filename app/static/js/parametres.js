/**
 * PARAMETRES.JS - Version propre
 * Gestion de la page des paramètres système
 */

class ParametresManager {
    constructor() {
        this.currentSection = 'audit';
        this.auditData = {
            logs: [],
            stats: {},
            filters: {
                role: '',
                action: '',
                limit: 100
            }
        };
        this.usersData = [];
        this.prestatairesData = [];

        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupAuditSection();
        this.setupUsersSection();
        this.setupPrestatairesSection();
        this.setupCredentialsSection();
        this.setupSessionSection();
        this.loadInitialData();
    }

    loadInitialData() {
        if (this.currentSection === 'audit') {
            this.loadAuditData();
        } else if (this.currentSection === 'users') {
            this.loadUsersData();
        } else if (this.currentSection === 'prestataires') {
            this.loadPrestatairesData();
        }
    }

    // ===== NAVIGATION =====
    setupNavigation() {
        const navItems = document.querySelectorAll('.settings-navigation .nav-item');
        console.log('Navigation setup - Found nav items:', navItems.length);

        navItems.forEach(item => {
            console.log('Setting up nav item:', item.getAttribute('data-section'));
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.getAttribute('data-section');
                console.log('Nav item clicked:', section);
                this.switchSection(section);
            });
        });
    }

    switchSection(sectionName) {
        console.log('Switching to section:', sectionName);

        // Masquer toutes les sections
        document.querySelectorAll('.settings-section').forEach(section => {
            section.classList.remove('active');
        });

        // Désactiver tous les nav items des paramètres
        document.querySelectorAll('.settings-navigation .nav-item').forEach(item => {
            item.classList.remove('active');
        });

        // Activer la section et le nav item
        const targetSection = document.getElementById(`${sectionName}-section`);
        const targetNavItem = document.querySelector(`.settings-navigation [data-section="${sectionName}"]`);

        console.log('Target section:', targetSection);
        console.log('Target nav item:', targetNavItem);

        if (targetSection && targetNavItem) {
            targetSection.classList.add('active');
            targetNavItem.classList.add('active');
            this.currentSection = sectionName;

            console.log('Section activated:', sectionName);

            // Charger les données si nécessaire
            if (sectionName === 'audit') {
                this.loadAuditData();
            } else if (sectionName === 'users') {
                this.loadUsersData();
            } else if (sectionName === 'prestataires') {
                this.loadPrestatairesData();
            }
        } else {
            console.error('Could not find target section or nav item for:', sectionName);
        }
    }

    // ===== SECTION AUDIT =====
    setupAuditSection() {
        const filtersForm = document.getElementById('audit-filters');
        if (filtersForm) {
            filtersForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.applyAuditFilters();
            });
        }

        const resetBtn = document.getElementById('reset-filters');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetAuditFilters();
            });
        }

        const refreshBtn = document.getElementById('refresh-logs');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadAuditData(true);
            });
        }
    }

    async loadAuditData(force = false) {
        if (!force && this.auditData.logs.length > 0) return;

        try {
            this.showAuditLoading();

            // Charger les statistiques
            const statsResponse = await fetch('/admin/parametres/api/audit/stats');
            if (statsResponse.ok) {
                this.auditData.stats = await statsResponse.json();
                this.updateAuditStats();
            }

            // Charger les logs
            const logsResponse = await fetch(`/admin/parametres/api/audit/logs?${this.getAuditFiltersQuery()}`);
            if (logsResponse.ok) {
                const data = await logsResponse.json();
                this.auditData.logs = data.logs;
                this.displayAuditLogs();
            }

        } catch (error) {
            console.error('Erreur lors du chargement des données d\'audit:', error);
            this.showAuditError();
        }
    }

    applyAuditFilters() {
        const form = document.getElementById('audit-filters');
        const formData = new FormData(form);
        
        this.auditData.filters = {
            role: formData.get('role') || '',
            action: formData.get('action') || '',
            limit: parseInt(formData.get('limit')) || 100
        };

        this.loadAuditData(true);
    }

    resetAuditFilters() {
        const form = document.getElementById('audit-filters');
        form.reset();
        form.querySelector('[name="limit"]').value = '100';
        
        this.auditData.filters = {
            role: '',
            action: '',
            limit: 100
        };

        this.loadAuditData(true);
    }

    getAuditFiltersQuery() {
        const params = new URLSearchParams();
        if (this.auditData.filters.role) params.append('role', this.auditData.filters.role);
        if (this.auditData.filters.action) params.append('action', this.auditData.filters.action);
        params.append('limit', this.auditData.filters.limit.toString());
        return params.toString();
    }

    updateAuditStats() {
        const stats = this.auditData.stats;

        // Mettre à jour les compteurs pour les 6 rôles
        const roles = ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR', 'CHARGE', 'CHAUFFEUR', 'MECANICIEN'];

        roles.forEach(role => {
            const roleStats = stats[role] || { total: 0, success_rate: 100, levels: {} };

            // Compteur d'actions
            const countElement = document.getElementById(`${role.toLowerCase()}-count`);
            if (countElement) {
                countElement.textContent = roleStats.total || 0;
            }

            // Taux de succès
            const successElement = document.getElementById(`${role.toLowerCase()}-success`);
            if (successElement) {
                successElement.textContent = `${roleStats.success_rate || 100}%`;
            }

            // Barre de niveau critique
            const criticalBar = document.getElementById(`${role.toLowerCase()}-critical-bar`);
            if (criticalBar && roleStats.levels) {
                const criticalCount = roleStats.levels.CRITICAL || 0;
                const totalCount = roleStats.total || 1;
                const criticalPercent = (criticalCount / totalCount) * 100;

                criticalBar.style.width = `${Math.min(criticalPercent, 100)}%`;
                criticalBar.style.backgroundColor = criticalPercent > 50 ? '#ef4444' :
                                                   criticalPercent > 20 ? '#f59e0b' : '#10b981';
            }
        });

        // Charger les alertes critiques
        this.loadCriticalAlerts();
    }

    // Charger les alertes critiques
    async loadCriticalAlerts() {
        try {
            const response = await fetch('/admin/parametres/api/audit/alerts');
            if (!response.ok) return;

            const alerts = await response.json();

            const alertsContainer = document.getElementById('critical-alerts');
            const alertsCount = document.getElementById('alerts-count');

            if (alerts.length === 0) {
                alertsContainer.innerHTML = `
                    <div class="no-alerts">
                        <i class="fas fa-check-circle"></i>
                        <p>Aucune alerte critique</p>
                    </div>
                `;
                alertsCount.textContent = '0';
            } else {
                const alertsHtml = alerts.slice(0, 5).map(alert => `
                    <div class="alert-item critical">
                        <div class="alert-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="alert-content">
                            <div class="alert-title">${alert.role} - ${alert.timestamp}</div>
                            <div class="alert-message">${alert.log.substring(0, 100)}...</div>
                        </div>
                    </div>
                `).join('');

                alertsContainer.innerHTML = alertsHtml;
                alertsCount.textContent = alerts.length;
            }

        } catch (error) {
            console.error('Erreur lors du chargement des alertes:', error);
        }
    }

    displayAuditLogs() {
        const container = document.getElementById('audit-logs');
        const logs = this.auditData.logs;

        if (logs.length === 0) {
            container.innerHTML = `
                <div class="loading-state">
                    <i class="fas fa-info-circle" style="font-size: 2rem; color: var(--gray-400); margin-bottom: 1rem;"></i>
                    <p>Aucun log trouvé avec les filtres actuels.</p>
                </div>
            `;
            return;
        }

        const logsHtml = logs.map(log => {
            const roleClass = this.getRoleClassFromLog(log);
            const logParts = this.parseLogString(log);
            return `
                <div class="audit-log-item ${roleClass}">
                    <div class="log-info">
                        <div class="log-user">${logParts.user || 'Système'}</div>
                        <div class="log-action">${logParts.action} - ${logParts.function}</div>
                        <div class="log-details">${logParts.details || ''}</div>
                    </div>
                    <div class="log-timestamp">${logParts.timestamp}</div>
                </div>
            `;
        }).join('');

        container.innerHTML = logsHtml;
        document.getElementById('logs-count').textContent = logs.length;
    }

    getRoleClassFromLog(log) {
        if (log.includes('ROLE:ADMIN')) return 'admin';
        if (log.includes('ROLE:RESPONSABLE')) return 'responsable';
        if (log.includes('ROLE:SUPERVISEUR')) return 'superviseur';
        if (log.includes('ROLE:CHARGE')) return 'charge';
        if (log.includes('ROLE:CHAUFFEUR')) return 'chauffeur';
        if (log.includes('ROLE:MECANICIEN')) return 'mecanicien';
        return '';
    }

    parseLogString(logString) {
        const parts = {
            user: 'Système',
            role: '',
            action: '',
            function: '',
            details: '',
            timestamp: new Date().toLocaleString()
        };

        try {
            const segments = logString.split(' | ');
            segments.forEach(segment => {
                const [key, ...valueParts] = segment.split(':');
                const value = valueParts.join(':').trim();
                
                switch(key) {
                    case 'USER':
                        parts.user = value;
                        break;
                    case 'ROLE':
                        parts.role = value;
                        break;
                    case 'ACTION':
                        parts.action = value;
                        break;
                    case 'FUNCTION':
                        parts.function = value;
                        break;
                    case 'DETAILS':
                        parts.details = value;
                        break;
                }
            });
        } catch (error) {
            console.warn('Erreur lors du parsing du log:', error);
            parts.details = logString;
        }

        return parts;
    }

    showAuditLoading() {
        document.getElementById('audit-logs').innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <p>Chargement des logs...</p>
            </div>
        `;
    }

    showAuditError() {
        document.getElementById('audit-logs').innerHTML = `
            <div class="loading-state">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: var(--danger-red); margin-bottom: 1rem;"></i>
                <p>Erreur lors du chargement des logs.</p>
            </div>
        `;
    }

    // ===== UTILITAIRES =====
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    showNotification(message, type = 'info') {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: type === 'success' ? 'Succès' : type === 'error' ? 'Erreur' : 'Information',
                text: message,
                icon: type,
                timer: 3000,
                showConfirmButton: false,
                toast: true,
                position: 'top-end'
            });
        } else {
            alert(message);
        }
    }

    // ===== SECTION IDENTIFIANTS =====
    setupCredentialsSection() {
        const searchBtn = document.getElementById('search-credentials-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.searchUserForCredentials();
            });
        }

        const searchInput = document.getElementById('search-user-credentials');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchUserForCredentials();
                }
            });
        }

        const credentialsForm = document.getElementById('credentials-form');
        if (credentialsForm) {
            credentialsForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateCredentials();
            });
        }

        const cancelBtn = document.getElementById('cancel-credentials');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.cancelCredentialsEdit();
            });
        }
    }

    async searchUserForCredentials() {
        const searchInput = document.getElementById('search-user-credentials');
        const query = searchInput.value.trim();

        if (!query) {
            this.showNotification('Veuillez saisir un terme de recherche', 'warning');
            return;
        }

        try {
            const response = await fetch(`/admin/api/users/search?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const users = await response.json();
                if (users.length > 0) {
                    this.showCredentialsForm(users[0]);
                } else {
                    this.showNotification('Aucun utilisateur trouvé', 'info');
                }
            } else {
                this.showNotification('Erreur lors de la recherche', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    showCredentialsForm(user) {
        document.getElementById('user-id-credentials').value = user.id;
        document.getElementById('current-login').value = user.login;
        document.getElementById('new-login').value = user.login;
        document.getElementById('new-password').value = '';
        document.getElementById('confirm-password').value = '';

        const resultsDiv = document.getElementById('credentials-search-results');
        resultsDiv.classList.remove('hidden');
    }

    cancelCredentialsEdit() {
        document.getElementById('credentials-search-results').classList.add('hidden');
        document.getElementById('search-user-credentials').value = '';
        document.getElementById('credentials-form').reset();
    }

    async updateCredentials() {
        const form = document.getElementById('credentials-form');
        const formData = new FormData(form);

        const userId = formData.get('user_id');
        const newLogin = formData.get('new_login');
        const newPassword = formData.get('new_password');
        const confirmPassword = formData.get('confirm_password');

        if (newPassword !== confirmPassword) {
            this.showNotification('Les mots de passe ne correspondent pas', 'error');
            return;
        }

        try {
            const response = await fetch(`/admin/api/users/${userId}/credentials`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    new_login: newLogin,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Identifiants modifiés avec succès', 'success');
                this.cancelCredentialsEdit();
            } else {
                this.showNotification(result.error || 'Erreur lors de la modification', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    // ===== SECTION SESSION =====
    setupSessionSection() {
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.logout();
            });
        }

        this.updateSessionTime();
        setInterval(() => {
            this.updateSessionTime();
        }, 60000);
    }

    updateSessionTime() {
        const sessionTimeElement = document.getElementById('session-time');
        if (sessionTimeElement) {
            const now = new Date();
            sessionTimeElement.textContent = now.toLocaleString();
        }
    }

    logout() {
        if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
            window.location.href = '/auth/logout';
        }
    }

    // ===== SECTION UTILISATEURS =====
    setupUsersSection() {
        const refreshUsersBtn = document.getElementById('refresh-users');
        if (refreshUsersBtn) {
            refreshUsersBtn.addEventListener('click', () => {
                this.loadUsersData(true);
            });
        }

        const createUserForm = document.getElementById('create-user-form');
        if (createUserForm) {
            createUserForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createUser();
            });
        }

        const editRoleForm = document.getElementById('edit-role-form');
        if (editRoleForm) {
            editRoleForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.editUserRole();
            });
        }
    }

    async loadUsersData(force = false) {
        if (!force && this.usersData.length > 0) return;

        try {
            this.showUsersLoading();

            const response = await fetch('/admin/api/users');
            if (response.ok) {
                this.usersData = await response.json();
                this.displayUsers();
            } else {
                this.showUsersError();
            }
        } catch (error) {
            console.error('Erreur lors du chargement des utilisateurs:', error);
            this.showUsersError();
        }
    }

    async createUser() {
        const form = document.getElementById('create-user-form');
        const formData = new FormData(form);

        const userData = {
            login: formData.get('login'),
            password: formData.get('password'),
            confirm_password: formData.get('confirm_password'),
            nom: formData.get('nom'),
            prenom: formData.get('prenom'),
            role: formData.get('role'),
            email: formData.get('email'),
            telephone: formData.get('telephone')
        };

        try {
            const response = await fetch('/admin/api/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Utilisateur créé avec succès', 'success');
                form.reset();
                if (typeof bootstrap !== 'undefined') {
                    bootstrap.Modal.getInstance(document.getElementById('createUserModal')).hide();
                }
                this.loadUsersData(true);
            } else {
                this.showNotification(result.error || 'Erreur lors de la création', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    displayUsers() {
        const tbody = document.getElementById('users-table-body');
        const users = this.usersData;

        if (users.length === 0) {
            const currentUserRole = document.querySelector('.parametres-container').dataset.userRole || 'SUPERVISEUR';
            const colspan = (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') ? '7' : '6';

            tbody.innerHTML = `
                <tr>
                    <td colspan="${colspan}" class="loading-cell">
                        <div class="loading-state">
                            <i class="fas fa-info-circle" style="font-size: 2rem; color: var(--gray-400); margin-bottom: 1rem;"></i>
                            <p>Aucun utilisateur trouvé.</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        const usersHtml = users.map(user => {
            // Récupérer le rôle de l'utilisateur connecté depuis la page
            const currentUserRole = document.querySelector('.parametres-container').dataset.userRole || 'SUPERVISEUR';

            let actionsHtml = '';

            // Bouton de suppression pour ADMIN et RESPONSABLE uniquement
            if (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') {
                actionsHtml = `
                    <button class="btn btn-sm btn-outline-danger" onclick="parametres.confirmDeleteUser(${user.id}, '${user.nom} ${user.prenom}')" title="Supprimer l'utilisateur">
                        <i class="fas fa-trash"></i>
                    </button>
                `;
            }

            // Construire la ligne avec ou sans colonne Actions selon le rôle
            let rowHtml = `
                <tr>
                    <td>${user.login}</td>
                    <td>${user.nom}</td>
                    <td>${user.prenom}</td>
                    <td><span class="role-badge ${user.role.toLowerCase()}">${user.role}</span></td>
                    <td><span class="badge ${user.active ? 'bg-success' : 'bg-secondary'}">${user.active ? 'Actif' : 'Inactif'}</span></td>
                    <td>${user.derniere_connexion || 'Jamais connecté'}</td>
            `;

            // Ajouter la colonne Actions seulement pour ADMIN et RESPONSABLE
            if (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') {
                rowHtml += `<td>${actionsHtml}</td>`;
            }

            rowHtml += `</tr>`;
            return rowHtml;
        }).join('');

        tbody.innerHTML = usersHtml;
        document.getElementById('users-count').textContent = users.length;
    }

    // Confirmer la suppression d'un utilisateur
    confirmDeleteUser(userId, userName) {
        if (confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur "${userName}" ?\n\nCette action est irréversible.`)) {
            this.deleteUser(userId);
        }
    }

    // Supprimer un utilisateur
    async deleteUser(userId) {
        try {
            const response = await fetch(`/admin/api/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                this.showNotification('Utilisateur supprimé avec succès', 'success');
                // Recharger la liste des utilisateurs
                await this.loadUsersData();
            } else {
                const error = await response.json();
                this.showNotification(error.error || 'Erreur lors de la suppression', 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la suppression:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    showEditRoleModal(user) {
        if (!user) return;

        document.getElementById('edit-role-user-id').value = user.id;
        document.getElementById('edit-role-user-name').value = `${user.nom} ${user.prenom} (${user.login})`;
        document.getElementById('edit-role-current').value = user.role;
        document.getElementById('edit-role-new').value = '';

        if (typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(document.getElementById('editRoleModal'));
            modal.show();
        }
    }

    async editUserRole() {
        const form = document.getElementById('edit-role-form');
        const formData = new FormData(form);

        const userId = formData.get('user_id');
        const newRole = formData.get('new_role');

        try {
            const response = await fetch(`/admin/api/users/${userId}/role`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ new_role: newRole })
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Rôle modifié avec succès', 'success');
                if (typeof bootstrap !== 'undefined') {
                    bootstrap.Modal.getInstance(document.getElementById('editRoleModal')).hide();
                }
                this.loadUsersData(true);
            } else {
                this.showNotification(result.error || 'Erreur lors de la modification', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    showUsersLoading() {
        const currentUserRole = document.querySelector('.parametres-container').dataset.userRole || 'SUPERVISEUR';
        const colspan = (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') ? '7' : '6';

        document.getElementById('users-table-body').innerHTML = `
            <tr>
                <td colspan="${colspan}" class="loading-cell">
                    <div class="loading-state">
                        <div class="loading-spinner"></div>
                        <p>Chargement des utilisateurs...</p>
                    </div>
                </td>
            </tr>
        `;
    }

    showUsersError() {
        const currentUserRole = document.querySelector('.parametres-container').dataset.userRole || 'SUPERVISEUR';
        const colspan = (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') ? '7' : '6';

        document.getElementById('users-table-body').innerHTML = `
            <tr>
                <td colspan="${colspan}" class="loading-cell">
                    <div class="loading-state">
                        <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: var(--danger-red); margin-bottom: 1rem;"></i>
                        <p>Erreur lors du chargement des utilisateurs.</p>
                    </div>
                </td>
            </tr>
        `;
    }

    // ===== SECTION PRESTATAIRES =====
    setupPrestatairesSection() {
        const refreshPrestatairesBtn = document.getElementById('refresh-prestataires');
        if (refreshPrestatairesBtn) {
            refreshPrestatairesBtn.addEventListener('click', () => {
                this.loadPrestatairesData(true);
            });
        }
    }

    async loadPrestatairesData(force = false) {
        if (!force && this.prestatairesData.length > 0) {
            this.renderPrestatairesTable();
            return;
        }

        this.showPrestatairesLoading();

        try {
            const response = await fetch('/admin/api/prestataires');
            if (response.ok) {
                this.prestatairesData = await response.json();
                this.renderPrestatairesTable();
            } else {
                this.showPrestatairesError();
            }
        } catch (error) {
            console.error('Erreur lors du chargement des prestataires:', error);
            this.showPrestatairesError();
        }
    }

    renderPrestatairesTable() {
        const tbody = document.getElementById('prestataires-table-body');
        const countBadge = document.getElementById('prestataires-count');

        if (!tbody || !countBadge) return;

        countBadge.textContent = this.prestatairesData.length;

        if (this.prestatairesData.length === 0) {
            const currentUserRole = document.querySelector('.parametres-container').dataset.userRole || 'SUPERVISEUR';
            const colspan = (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') ? '5' : '4';

            tbody.innerHTML = `
                <tr>
                    <td colspan="${colspan}" class="loading-cell">
                        <div class="loading-state">
                            <i class="fas fa-truck" style="font-size: 2rem; color: var(--gray-400); margin-bottom: 1rem;"></i>
                            <p>Aucun prestataire trouvé.</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        // Récupérer le rôle de l'utilisateur connecté
        const currentUserRole = document.querySelector('.parametres-container').dataset.userRole || 'SUPERVISEUR';

        tbody.innerHTML = this.prestatairesData.map(prestataire => {
            // Bouton de suppression seulement pour ADMIN et RESPONSABLE
            let actionsHtml = '';
            if (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') {
                actionsHtml = `
                    <button class="btn-icon btn-danger" onclick="parametres.confirmDeletePrestataire(${prestataire.id}, '${prestataire.nom_prestataire}')" title="Supprimer">
                        <i class="fas fa-trash"></i>
                    </button>
                `;
            }

            // Construire la ligne avec ou sans colonne Actions selon le rôle
            let rowHtml = `
                <tr>
                    <td>${prestataire.nom_prestataire}</td>
                    <td>${prestataire.telephone || '-'}</td>
                    <td>${prestataire.email || '-'}</td>
                    <td>${prestataire.localisation || '-'}</td>
            `;

            // Ajouter la colonne Actions seulement pour ADMIN et RESPONSABLE
            if (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') {
                rowHtml += `<td>${actionsHtml}</td>`;
            }

            rowHtml += `</tr>`;
            return rowHtml;
        }).join('');
    }

    confirmDeletePrestataire(id, nom) {
        if (confirm(`Êtes-vous sûr de vouloir supprimer le prestataire "${nom}" ?\n\nCette action est irréversible.`)) {
            this.deletePrestataire(id);
        }
    }

    async deletePrestataire(id) {
        try {
            const response = await fetch(`/admin/api/prestataires/${id}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Prestataire supprimé avec succès', 'success');
                this.loadPrestatairesData(true);
            } else {
                this.showNotification(result.error || 'Erreur lors de la suppression', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    showPrestatairesLoading() {
        const currentUserRole = document.querySelector('.parametres-container').dataset.userRole || 'SUPERVISEUR';
        const colspan = (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') ? '5' : '4';

        document.getElementById('prestataires-table-body').innerHTML = `
            <tr>
                <td colspan="${colspan}" class="loading-cell">
                    <div class="loading-state">
                        <div class="loading-spinner"></div>
                        <p>Chargement des prestataires...</p>
                    </div>
                </td>
            </tr>
        `;
    }

    showPrestatairesError() {
        const currentUserRole = document.querySelector('.parametres-container').dataset.userRole || 'SUPERVISEUR';
        const colspan = (currentUserRole === 'ADMIN' || currentUserRole === 'RESPONSABLE') ? '5' : '4';

        document.getElementById('prestataires-table-body').innerHTML = `
            <tr>
                <td colspan="${colspan}" class="loading-cell">
                    <div class="loading-state">
                        <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: var(--danger-red); margin-bottom: 1rem;"></i>
                        <p>Erreur lors du chargement des prestataires.</p>
                    </div>
                </td>
            </tr>
        `;
    }
}

// Fonctions globales pour les modals
function openAddUserModal() {
    const modal = document.getElementById('addUserModal');
    if (modal) {
        modal.classList.add('show');
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
        modal.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';

        // Initialiser les champs chauffeur après ouverture
        setTimeout(() => {
            toggleChauffeurFields();
            updateLoginFromName();
        }, 100);
    }
}

function openCreatePrestataireModal() {
    const modal = document.getElementById('createPrestataireModal');
    if (modal) {
        modal.classList.add('show');
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
        modal.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';
    }
}

// Fonction pour gérer l'affichage des champs spécifiques aux chauffeurs/mécaniciens
function toggleChauffeurFields() {
    const roleSelect = document.getElementById('roleSelectAddUser');
    if (!roleSelect) return;

    const role = roleSelect.value;
    const isPermisRole = (role === 'CHAUFFEUR' || role === 'MECANICIEN');
    const container = document.getElementById('addUserForm');

    if (container) {
        const permisFields = container.querySelectorAll('.permis-only');
        const numeroPermis = container.querySelector('input[name="numero_permis"]');
        const dateDelivrance = container.querySelector('input[name="date_delivrance_permis"]');
        const dateExpiration = container.querySelector('input[name="date_expiration_permis"]');

        if (isPermisRole) {
            // Afficher les champs et les rendre requis
            permisFields.forEach(field => field.style.display = 'block');
            if (numeroPermis) numeroPermis.setAttribute('required', 'required');
            if (dateDelivrance) dateDelivrance.setAttribute('required', 'required');
            if (dateExpiration) dateExpiration.setAttribute('required', 'required');
        } else {
            // Masquer les champs et supprimer l'obligation
            permisFields.forEach(field => field.style.display = 'none');
            if (numeroPermis) numeroPermis.removeAttribute('required');
            if (dateDelivrance) dateDelivrance.removeAttribute('required');
            if (dateExpiration) dateExpiration.removeAttribute('required');
        }
    }
}

// Fonction pour générer automatiquement le login depuis nom + prénom
function updateLoginFromName() {
    const nomInput = document.querySelector('#addUserForm input[name="nom"]');
    const prenomInput = document.querySelector('#addUserForm input[name="prenom"]');
    const loginInput = document.querySelector('#addUserForm input[name="login"]');

    if (!nomInput || !prenomInput || !loginInput) return;

    // Fonction pour nettoyer les chaînes (slugify)
    function slugify(str) {
        return (str || '')
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/[^a-z0-9\.]+/g, '')
            .replace(/\.+/g, '.')
            .replace(/^\.|\.$/g, '');
    }

    function generateLogin() {
        // Ne pas écraser si l'utilisateur a modifié manuellement
        if (loginInput.dataset.userEdited === 'true') return;

        const nom = slugify(nomInput.value);
        const prenom = slugify(prenomInput.value);

        if (nom && prenom) {
            loginInput.value = prenom + '.' + nom;
        }
    }

    // Marquer comme édité manuellement si l'utilisateur tape dans le champ login
    loginInput.addEventListener('input', function() {
        this.dataset.userEdited = 'true';
    });

    // Générer automatiquement quand nom ou prénom change
    nomInput.addEventListener('input', generateLogin);
    prenomInput.addEventListener('input', generateLogin);

    // Réinitialiser le flag d'édition manuelle
    loginInput.dataset.userEdited = 'false';
}

// Initialiser les événements quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    // Écouter les changements de rôle pour afficher/masquer les champs
    const roleSelect = document.getElementById('roleSelectAddUser');
    if (roleSelect) {
        roleSelect.addEventListener('change', toggleChauffeurFields);
    }
});

// Initialisation
let parametres;
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing ParametresManager...');
    parametres = new ParametresManager();
    console.log('ParametresManager initialized:', parametres);
});
