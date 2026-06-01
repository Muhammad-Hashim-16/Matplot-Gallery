/**
 * MatplotGallery — Smart Search Engine
 * 
 * Implements fuzzy matching, partial matching, multi-word search,
 * typo tolerance, ranked results, and in-memory analytics.
 */

(function() {
    // 7. Search Analytics (Cache)
    const searchHistory = new Map();

    // 8. Performance Cache
    // Caches the normalized versions of plot strings to avoid re-computing during tight loops
    let normalizedCache = null;

    // 4. Text Normalization
    function normalize(text) {
        if (!text) return '';
        return String(text)
            .toLowerCase()
            .replace(/[^a-z0-9\s]/g, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    // 3. Fuzzy Matching (Levenshtein)
    // Uses dynamic programming to compute the minimum edit distance
    function levenshtein(a, b) {
        if (a.length === 0) return b.length;
        if (b.length === 0) return a.length;

        const matrix = [];

        // Increment along the first column of each row
        for (let i = 0; i <= b.length; i++) {
            matrix[i] = [i];
        }

        // Increment each column in the first row
        for (let j = 0; j <= a.length; j++) {
            matrix[0][j] = j;
        }

        // Fill in the rest of the matrix
        for (let i = 1; i <= b.length; i++) {
            for (let j = 1; j <= a.length; j++) {
                if (b.charAt(i - 1) === a.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1, // substitution
                        Math.min(matrix[i][j - 1] + 1, // insertion
                        matrix[i - 1][j] + 1) // deletion
                    );
                }
            }
        }

        return matrix[b.length][a.length];
    }

    // Fuzzy match rule: distance <= floor(length/4), minimum length 4
    function isFuzzyMatch(queryWord, targetWord) {
        if (queryWord.length < 4) return false;
        const dist = levenshtein(queryWord, targetWord);
        return dist <= Math.floor(queryWord.length / 4);
    }

    // 2. Scoring System
    // Returns a numeric score. 0 means no match.
    function scorePlot(plot, queryWords, rawQuery) {
        let totalScore = 0;
        
        const normName = plot._normName;
        const normTags = plot._normTags;
        const normDiff = plot._normDiff;
        const plotIdStr = plot.id.toString();
        const normRawQuery = normalize(rawQuery);
        
        // Bonus: +50 if query matches the full plot name exactly after normalization
        if (normName === normRawQuery) {
            totalScore += 50;
        }
        
        // Bonus: +30 if query is at the START of the plot name (prefix match)
        if (normName.startsWith(normRawQuery)) {
            totalScore += 30;
        }

        const nameWords = plot._nameWords;

        // Multi-word search — each word is searched independently, all must match
        for (const qWord of queryWords) {
            let wordScore = 0;
            
            // Single character query: only exact prefix matches, no fuzzy
            if (qWord.length === 1) {
                if (normName.startsWith(qWord) || 
                    nameWords.some(nw => nw.startsWith(qWord)) ||
                    normTags.some(t => t.startsWith(qWord)) || 
                    normDiff.startsWith(qWord) || 
                    plotIdStr.startsWith(qWord)) {
                    wordScore += 50; 
                }
                
                // If ANY word scores 0, return 0 total (all words must match)
                if (wordScore === 0) return 0; 
                totalScore += wordScore;
                continue;
            }

            // Check plot number (as string): +90 points if query matches exactly or partially
            if (plotIdStr === qWord || plotIdStr.includes(qWord)) {
                wordScore += 90;
            }
            
            // Check difficulty (case-insensitive): +70 points if matches
            if (normDiff === qWord) {
                wordScore += 70;
            }

            // Check each tag (case-insensitive): +80 points if exact match, +50 if partial
            for (const t of normTags) {
                if (t === qWord) {
                    wordScore += 80;
                } else if (t.includes(qWord)) {
                    wordScore += 50;
                }
            }

            // Check plot name (case-insensitive contains): +100 exact, +60 partial, +40 fuzzy
            for (const nw of nameWords) {
                if (nw === qWord) {
                    wordScore += 100;
                } else if (nw.includes(qWord)) {
                    wordScore += 60;
                } else if (isFuzzyMatch(qWord, nw)) {
                    wordScore += 40;
                }
            }
            
            // If ANY word scores 0, return 0 total (all words must match)
            if (wordScore === 0) return 0;
            
            totalScore += wordScore;
        }

        return totalScore;
    }

    // HTML escape utility to prevent XSS in highlights
    function escapeHtml(unsafe) {
        return (unsafe || '').toString()
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }

    // EXPOSE GLOBAL API
    window.MatplotSearch = {
        
        // 1. MAIN FILTER FUNCTION
        filter: function(plots, query) {
            // Edge Case: Empty query or only spaces
            if (!query || query.trim() === '') return plots;
            
            // Edge Case: Very long query (over 100 chars): truncate to 100 chars
            let safeQuery = query.substring(0, 100);
            
            // Edge Case: Special characters: strip them, search the clean version
            const normQuery = normalize(safeQuery);
            if (!normQuery) return plots; // if query was purely special chars

            // Analytics tracking
            searchHistory.set(normQuery, (searchHistory.get(normQuery) || 0) + 1);

            // 8. Performance caching
            if (!normalizedCache || normalizedCache.length !== plots.length) {
                normalizedCache = plots.map(p => ({
                    ...p,
                    _normName: normalize(p.name),
                    _nameWords: normalize(p.name).split(' ').filter(w => w.length > 0),
                    _normTags: p.tags.map(t => normalize(t)),
                    _normDiff: normalize(p.difficulty)
                }));
            }

            const queryWords = normQuery.split(' ').filter(w => w.length > 0);
            
            const scoredPlots = [];
            
            for (let i = 0; i < plots.length; i++) {
                const score = scorePlot(normalizedCache[i], queryWords, safeQuery);
                if (score > 0) {
                    scoredPlots.push({ plot: plots[i], score });
                }
            }

            // 5. Ranked results — better matches appear first
            scoredPlots.sort((a, b) => b.score - a.score);
            return scoredPlots.map(sp => sp.plot);
        },

        // 5. SEARCH SUGGESTIONS
        getSuggestions: function(plots, query, maxSuggestions = 5) {
            if (!query || query.trim() === '') return [];
            const safeQuery = normalize(query.substring(0, 100));
            if (!safeQuery) return [];

            const suggestions = new Set();
            const dict = new Set();

            plots.forEach(p => {
                dict.add(p.name);
                dict.add(p.difficulty);
                p.tags.forEach(t => dict.add(t));
            });

            // Filter suggestions that START WITH the query first
            for (const item of dict) {
                if (normalize(item).startsWith(safeQuery)) {
                    suggestions.add(item);
                }
            }

            // Then add suggestions that CONTAIN the query
            if (suggestions.size < maxSuggestions) {
                for (const item of dict) {
                    if (normalize(item).includes(safeQuery)) {
                        suggestions.add(item);
                    }
                    if (suggestions.size >= maxSuggestions) break;
                }
            }

            return Array.from(suggestions).slice(0, maxSuggestions);
        },

        // 6. HIGHLIGHT MATCHES
        getHighlightedText: function(text, query) {
            if (!query || query.trim() === '') return escapeHtml(text);
            const normQueryWords = normalize(query).split(' ').filter(w => w.length > 0);
            if (normQueryWords.length === 0) return escapeHtml(text);

            let resultText = escapeHtml(text);
            
            // Escape query words for RegExp construction
            const escapedWords = normQueryWords.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
            const pattern = new RegExp(`(${escapedWords.join('|')})`, 'gi');
            
            return resultText.replace(pattern, '<mark>$1</mark>');
        },

        // 7. SEARCH ANALYTICS
        getTopSearches: function() {
            return Array.from(searchHistory.entries())
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(entry => entry[0]);
        }
    };
})();

// TEST CASE DOCUMENTATION:
// "scater" should find scatter plots (fuzzy match)
// "3d" should find all 3D plots
// "beginner bar" should find beginner bar charts
// "42" should find plot number 42
// "violin stat" should find violin and statistical plots
