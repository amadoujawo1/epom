// Client-side cache buster for Railway deployment
export const CACHE_BUSTER = {
  version: '2025-04-25-23-00-ROLES-FIX',
  buildHash: 'CACHE-BUST-2025-04-25-23-00-ROLES-FIX',
  forceRefresh: () => {
    // Force browser cache refresh
    const currentHash = localStorage.getItem('app-build-hash');
    const newHash = CACHE_BUSTER.buildHash;
    
    if (currentHash !== newHash) {
      console.log('🔄 Cache buster triggered - forcing refresh');
      localStorage.setItem('app-build-hash', newHash);
      
      // Clear all caches
      if ('caches' in window) {
        caches.keys().then(names => {
          names.forEach(name => {
            caches.delete(name);
          });
        });
      }
      
      // Force reload with cache busting
      const url = new URL(window.location.href);
      url.searchParams.set('_v', newHash);
      window.location.href = url.toString();
    }
  },
  init: () => {
    CACHE_BUSTER.forceRefresh();
  }
};

// Auto-initialize
CACHE_BUSTER.init();
