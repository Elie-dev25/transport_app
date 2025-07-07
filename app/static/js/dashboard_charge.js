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