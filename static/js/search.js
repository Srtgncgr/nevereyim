document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('navbar-search-form');
    const searchInput = document.getElementById('navbar-search-input');

    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', performSearch);
    }
});

function performSearch(event) {
    event.preventDefault();
    const searchQuery = event.target.querySelector('input').value;
    
    console.log('Search Query:', searchQuery);  // Debug log
    
    if (searchQuery.trim() === '') {
        return;
    }

    // Arama sonuçları sayfasına yönlendir
    const searchUrl = `/search/?search=${encodeURIComponent(searchQuery)}`;
    console.log('Redirecting to:', searchUrl);  // Debug log
    
    window.location.href = searchUrl;
}