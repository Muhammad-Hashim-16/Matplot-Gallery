/**
 * MatplotGallery - Main Application Logic
 * 
 * ANTI-FLICKER FIX REMINDER:
 * Ensure this inline script is the very first script in the <head> of index.html:
 * <script>
 *   (function() {
 *     const theme = localStorage.getItem('matplotgallery-theme') || 'dark';
 *     document.documentElement.setAttribute('data-theme', theme);
 *   })();
 * </script>
 */

// 1. CONSTANTS AND CONFIGURATION
const CONFIG = {
    dataFile: './data.json',
    figuresDir: './figures/',
    codeSnippetsDir: './code_snippets/',
    animationStagger: 50,
    scrollTopThreshold: 400,
    toastDuration: 2000,
    searchDebounce: 250
};

// 2. STATE MANAGEMENT
const state = {
    plots: [],
    filteredPlots: [],
    currentModalIndex: -1,
    activeFilters: {
        difficulty: 'all',
        tags: [],
        search: ''
    },
    theme: 'dark',
    sortOrder: 'default'
};

// Track animated cards to prevent re-animation on filter (FIX 8)
const renderedPlotIds = new Set();
let deferredPrompt;

// UTILITY FUNCTIONS
function debounce(fn, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}

function throttle(fn, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            fn.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function sanitizeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function getDifficultyOrder(difficulty) {
    switch (difficulty.toLowerCase()) {
        case 'beginner': return 0;
        case 'intermediate': return 1;
        case 'advanced': return 2;
        default: return 3;
    }
}

// 3. INITIALIZATION
document.addEventListener('DOMContentLoaded', () => {
    // Theme Init
    const savedTheme = localStorage.getItem('matplotgallery-theme') || 'dark';
    state.theme = savedTheme;
    document.documentElement.setAttribute('data-theme', state.theme);
    updateThemeIcon();

    // Data Load
    loadData();

    // Event Listeners setup
    setupEventListeners();

    // PWA Prompt setup
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        const banner = document.getElementById('install-banner');
        if (banner) {
            banner.style.display = 'flex';
        }
    });

    lucide.createIcons();
});

// 4. DATA LOADING
async function loadData() {
    try {
        const response = await fetch(CONFIG.dataFile); // FIX 5
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        state.plots = data;
        state.filteredPlots = [...data];

        renderStats();
        renderFilterPills();
        renderGrid();
        
        document.getElementById('loading-skeletons').classList.add('hidden');
    } catch (error) {
        console.error('Failed to load data:', error);
        const gridContainer = document.getElementById('plots-grid-container');
        document.getElementById('loading-skeletons').classList.add('hidden');
        
        const errorMsg = document.createElement('div');
        errorMsg.style.gridColumn = '1 / -1';
        errorMsg.style.padding = '80px 20px';
        errorMsg.style.textAlign = 'center';
        errorMsg.innerHTML = `
            <i data-lucide="alert-circle" style="width:64px;height:64px;color:var(--text-muted);margin-bottom:16px;"></i>
            <h2 style="margin-bottom:8px;">Failed to load gallery data</h2>
            <p style="color:var(--text-muted);margin-bottom:24px;">Please ensure you have generated the data by running the following commands in your project root:</p>
            <code style="background:var(--bg-tertiary);padding:8px 16px;border-radius:var(--radius-sm);display:inline-block;">python splitter.py</code>
        `;
        gridContainer.appendChild(errorMsg);
        lucide.createIcons();
    }
}

// 5. STATS RENDERING
function renderStats() {
    const plotCountEl = document.getElementById('stat-plots-count');
    if (plotCountEl) plotCountEl.textContent = state.plots.length;
    
    const uniqueTags = new Set();
    state.plots.forEach(plot => {
        plot.tags.forEach(tag => uniqueTags.add(tag));
    });
    const typeCountEl = document.getElementById('stat-chart-types');
    if (typeCountEl) typeCountEl.textContent = uniqueTags.size;
}

// 6. FILTER PILLS RENDERING
function renderFilterPills() {
    const container = document.getElementById('filter-pills');
    if (!container) return;

    const uniqueTags = new Set();
    state.plots.forEach(plot => plot.tags.forEach(tag => uniqueTags.add(tag)));
    
    const sortedTags = Array.from(uniqueTags).sort();
    
    sortedTags.forEach(tag => {
        const pill = document.createElement('button');
        pill.className = 'filter-pill';
        pill.dataset.filter = tag;
        pill.dataset.type = 'tag';
        pill.textContent = tag;
        container.appendChild(pill);
    });

    container.addEventListener('click', handleFilterPillClick);
}

// 7. GRID RENDERING
function renderGrid() {
    const grid = document.getElementById('plots-grid');
    const emptyState = document.getElementById('empty-state');
    const resultsText = document.getElementById('results-count-text');
    
    if (!grid) return;
    grid.innerHTML = '';
    
    if (state.filteredPlots.length === 0) {
        grid.classList.add('hidden');
        if (emptyState) emptyState.classList.remove('hidden');
        if (resultsText) resultsText.textContent = `Showing 0 of ${state.plots.length} plots`;
        return;
    }
    
    grid.classList.remove('hidden');
    if (emptyState) emptyState.classList.add('hidden');
    if (resultsText) resultsText.textContent = `Showing ${state.filteredPlots.length} of ${state.plots.length} plots`;

    state.filteredPlots.forEach((plot, index) => {
        const card = createCardElement(plot, index);
        grid.appendChild(card);
    });
}

// 8. CARD CREATION
function createCardElement(plot, index) {
    const card = document.createElement('article');
    card.className = 'plot-card';
    card.dataset.id = plot.id;
    card.dataset.difficulty = plot.difficulty;
    card.dataset.name = plot.name;
    card.dataset.tags = plot.tags.join(',');
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.setAttribute('aria-label', `View plot: ${plot.name}`);

    // FIX 8 — Card animation only plays once
    if (!renderedPlotIds.has(plot.id)) {
        card.classList.add('fade-in-up');
        card.style.animationDelay = `${index * CONFIG.animationStagger}ms`;
        renderedPlotIds.add(plot.id);
    } else {
        card.style.animationDelay = '0ms';
    }

    const badgeClass = `diff-badge-${plot.difficulty.toLowerCase()}`;
    
    let tagsHtml = '';
    const displayTags = plot.tags.slice(0, 3);
    displayTags.forEach(tag => {
        tagsHtml += `<span class="tag-pill">${sanitizeHTML(tag)}</span>`;
    });
    if (plot.tags.length > 3) {
        tagsHtml += `<span class="tag-pill">+${plot.tags.length - 3} more</span>`;
    }

    card.innerHTML = `
        <div class="card-image-wrapper">
            <img src="${CONFIG.figuresDir}${plot.id}.png" alt="${sanitizeHTML(plot.name)}" loading="lazy" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
            <div class="image-fallback" style="display:none; width:100%; height:100%; align-items:center; justify-content:center; flex-direction:column; background:var(--bg-tertiary); color:var(--text-muted);">
                <i data-lucide="bar-chart-2" style="width:48px;height:48px;margin-bottom:8px;"></i>
                <span>Plot #${plot.id}</span>
            </div>
            <div class="card-overlay">
                <span class="expand-hint">Click to expand</span>
            </div>
            <span class="difficulty-badge ${badgeClass}">${sanitizeHTML(plot.difficulty)}</span>
        </div>
        <div class="card-body">
            <span class="plot-number">#${plot.id}</span>
            <h3 class="plot-name">${sanitizeHTML(plot.name)}</h3>
            <div class="card-tags">
                ${tagsHtml}
            </div>
        </div>
    `;

    card.addEventListener('click', () => openModal(plot.id));
    card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openModal(plot.id);
        }
    });

    return card;
}

// 9. FILTERING LOGIC
function applyFilters() {
    let results = [...state.plots];

    if (state.activeFilters.difficulty !== 'all') {
        results = results.filter(p => p.difficulty === state.activeFilters.difficulty);
    }

    if (state.activeFilters.tags.length > 0) {
        results = results.filter(p => {
            return state.activeFilters.tags.some(activeTag => p.tags.includes(activeTag));
        });
    }

    if (state.activeFilters.search && window.MatplotSearch) {
        results = window.MatplotSearch.filter(results, state.activeFilters.search);
    }

    if (state.sortOrder !== 'default') {
        results.sort((a, b) => {
            const rankA = getDifficultyOrder(a.difficulty);
            const rankB = getDifficultyOrder(b.difficulty);
            
            if (state.sortOrder === 'beginner') {
                if (rankA !== rankB) return rankA - rankB;
            } else if (state.sortOrder === 'advanced') {
                if (rankA !== rankB) return rankB - rankA;
            }
            return a.id - b.id;
        });
    }

    state.filteredPlots = results;
    renderGrid();
    
    // Accessibility: aria-live region
    const resultsInfo = document.getElementById('results-count-text');
    if (resultsInfo) {
        resultsInfo.setAttribute('aria-live', 'polite');
    }
}

// 10. FILTER EVENT HANDLING
function handleFilterPillClick(e) {
    const pill = e.target.closest('.filter-pill');
    if (!pill) return;

    const filterVal = pill.dataset.filter;
    const filterType = pill.dataset.type || 'all';

    if (filterType === 'all') {
        state.activeFilters.difficulty = 'all';
        state.activeFilters.tags = [];
        state.activeFilters.search = '';
        
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.value = '';
        const clearBtn = document.getElementById('clear-search-btn');
        if (clearBtn) clearBtn.classList.add('hidden');
        
        document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
    } 
    else if (filterType === 'difficulty') {
        state.activeFilters.difficulty = state.activeFilters.difficulty === filterVal ? 'all' : filterVal;
        
        document.querySelectorAll('.filter-pill[data-type="difficulty"]').forEach(p => p.classList.remove('active'));
        document.querySelector('.filter-pill[data-filter="all"]').classList.remove('active');
        
        if (state.activeFilters.difficulty !== 'all') {
            pill.classList.add('active');
        } else if (state.activeFilters.tags.length === 0) {
            document.querySelector('.filter-pill[data-filter="all"]').classList.add('active');
        }
    }
    else if (filterType === 'tag') {
        const index = state.activeFilters.tags.indexOf(filterVal);
        if (index > -1) {
            state.activeFilters.tags.splice(index, 1);
            pill.classList.remove('active');
        } else {
            state.activeFilters.tags.push(filterVal);
            pill.classList.add('active');
        }
        
        document.querySelector('.filter-pill[data-filter="all"]').classList.remove('active');
        if (state.activeFilters.difficulty === 'all' && state.activeFilters.tags.length === 0) {
            document.querySelector('.filter-pill[data-filter="all"]').classList.add('active');
        }
    }

    applyFilters();
}

// 11. SEARCH HANDLING
function setupSearch() {
    const searchInput = document.getElementById('search-input');
    const clearBtn = document.getElementById('clear-search-btn');
    const shortcutHint = document.querySelector('.search-shortcut');
    
    if (!searchInput) return;

    const handleSearchInput = debounce((e) => {
        state.activeFilters.search = e.target.value.trim();
        applyFilters();
    }, CONFIG.searchDebounce);

    searchInput.addEventListener('input', (e) => {
        const val = e.target.value;
        if (val.length > 0) {
            clearBtn.classList.remove('hidden');
            if (shortcutHint) shortcutHint.style.display = 'none';
        } else {
            clearBtn.classList.add('hidden');
            if (shortcutHint) shortcutHint.style.display = 'block';
        }
        handleSearchInput(e);
    });

    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        state.activeFilters.search = '';
        clearBtn.classList.add('hidden');
        if (shortcutHint) shortcutHint.style.display = 'block';
        searchInput.focus();
        applyFilters();
    });
}

// 12. MODAL FUNCTIONALITY
async function openModal(plotId) {
    const index = state.filteredPlots.findIndex(p => p.id === parseInt(plotId));
    if (index === -1) return;
    
    state.currentModalIndex = index;
    const plot = state.filteredPlots[index];

    document.getElementById('modal-plot-number').textContent = `#${plot.id}`;
    document.getElementById('modal-plot-name').textContent = plot.name;
    
    const badge = document.getElementById('modal-difficulty-badge');
    badge.textContent = plot.difficulty;
    badge.className = `difficulty-badge diff-badge-${plot.difficulty.toLowerCase()}`;
    
    // FIX 2 — Removed opacity hack that caused invisible images
    const img = document.getElementById('modal-image');
    img.src = `${CONFIG.figuresDir}${plot.id}.png`;
    img.alt = plot.name;

    const tagsHtml = plot.tags.map(tag => `<span class="tag-pill">${sanitizeHTML(tag)}</span>`).join('');
    document.getElementById('modal-tags').innerHTML = tagsHtml;

    document.getElementById('modal-counter').textContent = `${index + 1} / ${state.filteredPlots.length}`;
    
    // Disable prev/next logic securely
    const prevBtn = document.getElementById('prev-plot-btn');
    const nextBtn = document.getElementById('next-plot-btn');
    prevBtn.disabled = index === 0 || state.filteredPlots.length <= 1;
    nextBtn.disabled = index === state.filteredPlots.length - 1 || state.filteredPlots.length <= 1;

    // FIX 9 — Lazy load code exactly as requested
    const codeEl = document.getElementById('modal-code');
    codeEl.textContent = 'Loading code...';
    
    if (!plot.code) {
        try {
            const res = await fetch(CONFIG.codeSnippetsDir + plot.id + '.txt');
            if (!res.ok) throw new Error();
            plot.code = await res.text();
        } catch {
            plot.code = '# Code file not found. Run splitter.py to generate code snippets.';
        }
    }
    codeEl.textContent = plot.code;

    // FIX 1 — Highlight.js timing
    setTimeout(() => {
        if (codeEl) {
            delete codeEl.dataset.highlighted;
            window.hljs && hljs.highlightElement(codeEl);
        }
    }, 0);

    const overlay = document.getElementById('modal-overlay');
    overlay.classList.remove('hidden');
    requestAnimationFrame(() => {
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        document.getElementById('modal-close-btn').focus();
    });

    // FIX 6 — Lucide icons in modal
    const modalEl = document.getElementById('modal');
    if (modalEl && window.lucide) {
        lucide.createIcons({ attrs: { 'stroke-width': 2 } });
    }
}

function closeModal() {
    const overlay = document.getElementById('modal-overlay');
    if (!overlay) return;
    overlay.classList.remove('active');
    setTimeout(() => {
        overlay.classList.add('hidden');
        document.body.style.overflow = '';
        state.currentModalIndex = -1;
    }, 250);
}

function navigateModal(direction) {
    if (state.currentModalIndex === -1) return;
    
    const newIndex = direction === 'prev' ? state.currentModalIndex - 1 : state.currentModalIndex + 1;
    if (newIndex >= 0 && newIndex < state.filteredPlots.length) {
        openModal(state.filteredPlots[newIndex].id);
    }
}

// 13. KEYBOARD SHORTCUTS & FOCUS TRAP
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        const overlay = document.getElementById('modal-overlay');
        const isModalOpen = overlay && overlay.classList.contains('active');
        const searchInput = document.getElementById('search-input');
        
        if (e.key === 'Escape') {
            if (isModalOpen) closeModal();
        }
        
        if (isModalOpen) {
            if (e.key === 'ArrowLeft') navigateModal('prev');
            if (e.key === 'ArrowRight') navigateModal('next');
            
            // Focus trap
            if (e.key === 'Tab') {
                const focusableElements = document.getElementById('modal').querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];
                
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        }
        
        if (!isModalOpen) {
            if (e.key === '/' || (e.key === 'k' && (e.metaKey || e.ctrlKey))) {
                if (searchInput && document.activeElement !== searchInput) {
                    e.preventDefault();
                    searchInput.focus();
                }
            }
        }
    });
}

// 14. THEME TOGGLE
function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    
    document.body.classList.add('theme-transitioning');
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('matplotgallery-theme', state.theme);
    
    updateThemeIcon();
    
    setTimeout(() => {
        document.body.classList.remove('theme-transitioning');
    }, 350);
}

function updateThemeIcon() {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;
    const iconName = state.theme === 'dark' ? 'moon' : 'sun';
    btn.innerHTML = `<i data-lucide="${iconName}"></i>`;
    lucide.createIcons();
}

// 15 & 16. SCROLL HANDLING
function setupScroll() {
    const progressBar = document.getElementById('scroll-progress');
    const scrollTopBtn = document.getElementById('scroll-top-btn');
    const navbar = document.getElementById('navbar');
    
    const handleScroll = throttle(() => {
        const winScroll = window.scrollY;
        const height = document.documentElement.scrollHeight - window.innerHeight;
        
        if (height > 0) {
            const scrolled = (winScroll / height) * 100;
            if (progressBar) progressBar.style.width = scrolled + '%';
        }
        
        if (scrollTopBtn) {
            if (winScroll > CONFIG.scrollTopThreshold) {
                scrollTopBtn.classList.remove('hidden');
            } else {
                scrollTopBtn.classList.add('hidden');
            }
        }
        
        if (navbar) {
            if (winScroll > 10) navbar.classList.add('scrolled');
            else navbar.classList.remove('scrolled');
        }
    }, 100);

    window.addEventListener('scroll', handleScroll);
    
    if (scrollTopBtn) {
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
}

// 17 & 18. COPY CODE & TOAST
// FIX 7 — Copy to clipboard fallback
async function copyCode(text) {
    try {
        await navigator.clipboard.writeText(text);
        showCopySuccess();
    } catch (err) {
        try {
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            showCopySuccess();
        } catch (fallbackErr) {
            showToast('Could not copy code. Please select and copy manually.', 'error');
        }
    }
}

function showCopySuccess() {
    const copyBtn = document.getElementById('copy-code-btn');
    if (copyBtn) {
        copyBtn.classList.add('copied');
        copyBtn.innerHTML = '<i data-lucide="check"></i> Copied!';
        lucide.createIcons();
        showToast('Code copied to clipboard!', 'success');
        
        setTimeout(() => {
            copyBtn.classList.remove('copied');
            copyBtn.innerHTML = '<i data-lucide="copy"></i> Copy Code';
            lucide.createIcons();
        }, 2000);
    }
}

function setupCopyCode() {
    const copyBtn = document.getElementById('copy-code-btn');
    if (!copyBtn) return;
    
    copyBtn.addEventListener('click', () => {
        const codeText = document.getElementById('modal-code').textContent;
        copyCode(codeText);
    });
}

const navSearchBtn = document.getElementById('nav-search-btn');
if (navSearchBtn) {
    navSearchBtn.addEventListener('click', () => {
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.focus();
    });
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.innerHTML = type === 'success' 
        ? `<i data-lucide="check-circle"></i> ${sanitizeHTML(message)}`
        : `<i data-lucide="alert-circle"></i> ${sanitizeHTML(message)}`;
        
    lucide.createIcons();
    toast.classList.remove('hidden');
    void toast.offsetWidth; // Force reflow
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.classList.add('hidden'), 250);
    }, CONFIG.toastDuration);
}

// SETUP ALL EVENT LISTENERS
function setupEventListeners() {
    setupSearch();
    setupKeyboardShortcuts();
    setupScroll();
    setupCopyCode();
    
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            state.sortOrder = e.target.value;
            applyFilters();
        });
    }
    
    const resetBtn = document.getElementById('reset-filters-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            const searchInput = document.getElementById('search-input');
            const clearBtn = document.getElementById('clear-search-btn');
            
            if (searchInput) searchInput.value = '';
            if (clearBtn) clearBtn.classList.add('hidden');
            
            document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            const allPill = document.querySelector('.filter-pill[data-filter="all"]');
            if (allPill) allPill.classList.add('active');
            
            if (sortSelect) sortSelect.value = 'default';
            
            state.activeFilters.search = '';
            state.activeFilters.difficulty = 'all';
            state.activeFilters.tags = [];
            state.sortOrder = 'default';
            
            applyFilters();
        });
    }
    
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
    
    const modalCloseBtn = document.getElementById('modal-close-btn');
    if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);
    
    // FIX 10 — Modal closes when clicking overlay background
    const overlay = document.getElementById('modal-overlay');
    if (overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
    }
    
    const prevBtn = document.getElementById('prev-plot-btn');
    if (prevBtn) prevBtn.addEventListener('click', () => navigateModal('prev'));
    
    const nextBtn = document.getElementById('next-plot-btn');
    if (nextBtn) nextBtn.addEventListener('click', () => navigateModal('next'));

    document.addEventListener('click', async (e) => {
        if (e.target.id === 'pwa-install-btn') {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                deferredPrompt = null;
                document.getElementById('install-banner').style.display = 'none';
            }
        }
        if (e.target.id === 'pwa-dismiss-btn') {
            document.getElementById('install-banner').style.display = 'none';
        }
    });
}
