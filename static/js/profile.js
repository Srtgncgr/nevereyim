document.addEventListener('DOMContentLoaded', function() {
    // Tab menü tıklama işlemleri
    const profileMenuItems = document.querySelectorAll('.profile-menu-item');
    
    profileMenuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Aktif menü stilini güncelle
            profileMenuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // İlgili tab'ı göster
            const targetId = this.getAttribute('href').replace('#', '');
            const tabs = document.querySelectorAll('.tab-pane');
            tabs.forEach(tab => {
                tab.classList.remove('show', 'active');
                if (tab.id === targetId) {
                    tab.classList.add('show', 'active');
                }
            });
        });
    });
});