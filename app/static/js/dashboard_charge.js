 function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.querySelector('.overlay');
            
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        }

        // Toggle Notifications
        function toggleNotifications() {
            const panel = document.getElementById('notificationPanel');
            panel.classList.toggle('active');
        }

        // Set Active Menu
        function setActiveMenu(element) {
            // Remove active class from all links
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            
            // Add active class to clicked link
            element.classList.add('active');
            
            // Update page title
            const title = element.textContent.trim();
            document.querySelector('.page-title').textContent = title;
            
            // Close sidebar on mobile
            if (window.innerWidth <= 768) {
                toggleSidebar();
            }
        }

        // Logout function
        function logout() {
            if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
                // Simulation de déconnexion
                alert('Déconnexion réussie !');
                // Redirection vers la page de connexion
                // window.location.href = '/login';
            }
        }

        // Close notifications when clicking outside
        document.addEventListener('click', function(event) {
            const panel = document.getElementById('notificationPanel');
            const bell = document.querySelector('.notification-bell');
            
            if (!panel.contains(event.target) && !bell.contains(event.target)) {
                panel.classList.remove('active');
            }
        });

        // (Désactivé) Update statistics periodically (simulation)
// function updateStats() {
//     const statsValues = document.querySelectorAll('.stat-value');
//     statsValues.forEach(stat => {
//         const currentValue = parseInt(stat.textContent);
//         const change = Math.floor(Math.random() * 3) - 1; // -1, 0, or 1
//         if (change !== 0) {
//             stat.textContent = Math.max(0, currentValue + change);
//         }
//     });
// }

// setInterval(updateStats, 30000);

        // Real-time clock
        function updateClock() {
            const now = new Date();
            const timeString = now.toLocaleTimeString('fr-FR');
            const dateString = now.toLocaleDateString('fr-FR');
            
            // You can add a clock element if needed
            document.title = `UDM Transport - ${timeString}`;
        }

        setInterval(updateClock, 1000);

        // Responsive handling
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                document.getElementById('sidebar').classList.remove('active');
                document.querySelector('.overlay').classList.remove('active');
            }
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Set initial active menu
            console.log('Dashboard loaded successfully');
            
            // Simulate real-time data updates
            setTimeout(() => {
                const badge = document.querySelector('.notification-badge');
                if (badge) {
                    badge.textContent = '4';
                    badge.style.animation = 'pulse 2s infinite';
                }
            }, 10000);
        });

        // CSS animation for pulse effect
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.2); }
                100% { transform: scale(1); }
            }
        `;
        document.head.appendChild(style);

        // Gestion des modales de trajets
        initTrajetModals();

        // Fonction pour initialiser les modales de trajets
        function initTrajetModals() {
            // Modal Trajet Interne Bus UdM
            const openTrajetInterneBtn = document.getElementById('openTrajetInterneBusUdMModal');
            const trajetInterneModal = document.getElementById('trajetInterneBusUdMModal');
            const closeTrajetInterneBtn = document.getElementById('closeTrajetInterneBusUdMModal');

            if (openTrajetInterneBtn && trajetInterneModal) {
                openTrajetInterneBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    trajetInterneModal.classList.add('show');
                });
            }

            if (closeTrajetInterneBtn && trajetInterneModal) {
                closeTrajetInterneBtn.addEventListener('click', function() {
                    trajetInterneModal.classList.remove('show');
                });
            }

            // Modal Trajet Prestataire
            const openTrajetPrestataireBtn = document.getElementById('openTrajetPrestataireModerniseModal');
            const trajetPrestataireModal = document.getElementById('trajetPrestataireModerniseModal');
            const closeTrajetPrestataireBtn = document.getElementById('closeTrajetPrestataireModerniseModal');

            if (openTrajetPrestataireBtn && trajetPrestataireModal) {
                openTrajetPrestataireBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    trajetPrestataireModal.classList.add('show');
                });
            }

            if (closeTrajetPrestataireBtn && trajetPrestataireModal) {
                closeTrajetPrestataireBtn.addEventListener('click', function() {
                    trajetPrestataireModal.classList.remove('show');
                });
            }

            // Modal Autres Trajets
            const openAutresTrajetsBtn = document.getElementById('openAutresTrajetsModal');
            const autresTrajetsModal = document.getElementById('autresTrajetsModal');
            const closeAutresTrajetsBtn = document.getElementById('closeAutresTrajetsModal');

            if (openAutresTrajetsBtn && autresTrajetsModal) {
                openAutresTrajetsBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    autresTrajetsModal.classList.add('show');
                });
            }

            if (closeAutresTrajetsBtn && autresTrajetsModal) {
                closeAutresTrajetsBtn.addEventListener('click', function() {
                    autresTrajetsModal.classList.remove('show');
                });
            }

            // Fermer les modales en cliquant à l'extérieur
            document.addEventListener('click', function(e) {
                if (e.target.classList.contains('modal')) {
                    e.target.classList.remove('show');
                }
            });

            // Gestion AJAX des formulaires
            initTrajetFormsAjax();
        }

        // Fonction pour initialiser les soumissions AJAX des formulaires
        function initTrajetFormsAjax() {
            // ⚠️ DÉSACTIVÉ - Les formulaires utilisent maintenant FormModalManager unifié
            // Les gestionnaires sont dans main.js via init_modal_form()
            console.log('Anciens gestionnaires AJAX désactivés - utilisation de FormModalManager');
        }

        // Fonction générique pour soumettre les formulaires de trajets
        function submitTrajetForm(form, modalId, errorId) {
            const formData = new FormData(form);
            const errorDiv = document.getElementById(errorId);

            // Masquer les erreurs précédentes
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Fermer la modale
                    document.getElementById(modalId).classList.remove('show');

                    // Afficher le message de succès
                    showSuccessMessage(data.message);

                    // Réinitialiser le formulaire
                    form.reset();
                } else {
                    // Afficher l'erreur
                    if (errorDiv) {
                        errorDiv.textContent = data.message;
                        errorDiv.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                if (errorDiv) {
                    errorDiv.textContent = 'Une erreur est survenue. Veuillez réessayer.';
                    errorDiv.style.display = 'block';
                }
            });
        }

        // Fonction pour afficher un message de succès
        function showSuccessMessage(message) {
            const successDiv = document.createElement('div');
            successDiv.className = 'flash-message success';
            successDiv.textContent = message;
            document.body.appendChild(successDiv);

            // Supprimer le message après 5 secondes
            setTimeout(() => {
                successDiv.style.opacity = '0';
                setTimeout(() => {
                    if (successDiv.parentNode) {
                        successDiv.parentNode.removeChild(successDiv);
                    }
                }, 500);
            }, 5000);
        }