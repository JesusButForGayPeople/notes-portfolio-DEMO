---
layout: page
title: Search Results
permalink: /search/
---

<div id="search-results-page">
    <div id="search-results-container">
        <div id="search-loading" style="display: none;">
            <p>Searching...</p>
        </div>
        <div id="search-results-list"></div>
        <div id="no-results" style="display: none;">
            <p>No results found. Try different keywords.</p>
        </div>
        <div id="search-debug" style="display: none; margin-top: 2rem; padding: 1rem; background: rgba(255,0,0,0.1); border: 1px solid #ff0000;">
            <h4>Debug Information:</h4>
            <div id="debug-content"></div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const resultsContainer = document.getElementById('search-results-list');
    const loadingDiv = document.getElementById('search-loading');
    const noResultsDiv = document.getElementById('no-results');
    const debugDiv = document.getElementById('search-debug');
    const debugContent = document.getElementById('debug-content');
    const pageTitle = document.querySelector('.page-title');
    
    // Show debug info in development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        debugDiv.style.display = 'block';
    }
    
    // Get search query from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const initialQuery = urlParams.get('q');
    
    if (initialQuery) {
        // Update the main content area title to include the search term
        pageTitle.textContent = `Search Results for "${initialQuery}"`;
        performSearch(initialQuery);
    }
    
    function performSearch(query) {
        if (!query.trim()) {
            resultsContainer.innerHTML = '';
            noResultsDiv.style.display = 'none';
            loadingDiv.style.display = 'none';
            pageTitle.textContent = 'Search Results';
            return;
        }
        
        loadingDiv.style.display = 'block';
        noResultsDiv.style.display = 'none';
        resultsContainer.innerHTML = '';
        
        // Update the main content area title
        pageTitle.textContent = `Search Results for "${query}"`;
        
        // Debug info
        debugContent.innerHTML = `Attempting to fetch search.json from: ${window.location.origin}/search.json`;
        
        // Load search index and perform client-side search
        fetch('/search.json')
            .then(response => {
                debugContent.innerHTML += `<br>Response status: ${response.status}`;
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(searchIndex => {
                debugContent.innerHTML += `<br>Search index loaded with ${searchIndex.length} items`;
                loadingDiv.style.display = 'none';
                
                const results = searchInIndex(searchIndex, query);
                debugContent.innerHTML += `<br>Found ${results.length} results for query: "${query}"`;
                
                if (results.length > 0) {
                    displayResults(results, query);
                } else {
                    noResultsDiv.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Search error:', error);
                debugContent.innerHTML += `<br>Error: ${error.message}`;
                loadingDiv.style.display = 'none';
                noResultsDiv.style.display = 'block';
            });
    }
    
    function searchInIndex(searchIndex, query) {
        const queryLower = query.toLowerCase();
        const terms = queryLower.trim().split(/\s+/).filter(term => term.length > 0);
        
        const results = searchIndex.filter(item => {
            // Check if any term matches in title, content, or excerpt
            return terms.some(term => {
                const titleMatch = item.title && item.title.toLowerCase().includes(term);
                const contentMatch = item.content && item.content.toLowerCase().includes(term);
                const excerptMatch = item.excerpt && item.excerpt.toLowerCase().includes(term);
                return titleMatch || contentMatch || excerptMatch;
            });
        });

        // Sort by relevance (title matches first, then content matches)
        results.sort((a, b) => {
            const aTitleMatches = terms.filter(term => 
                a.title && a.title.toLowerCase().includes(term)
            ).length;
            const bTitleMatches = terms.filter(term => 
                b.title && b.title.toLowerCase().includes(term)
            ).length;
            
            const aContentMatches = terms.filter(term => 
                a.content && a.content.toLowerCase().includes(term)
            ).length;
            const bContentMatches = terms.filter(term => 
                b.content && b.content.toLowerCase().includes(term)
            ).length;
            
            // Prioritize title matches, then content matches
            const aScore = aTitleMatches * 2 + aContentMatches;
            const bScore = bTitleMatches * 2 + bContentMatches;
            
            return bScore - aScore;
        });

        return results;
    }
    
    function generateDynamicExcerpt(content, searchTerms) {
        if (!content || searchTerms.length === 0) {
            return content ? content.substring(0, 200) + "..." : "";
        }
        
        const contentLower = content.toLowerCase();
        let bestPosition = 0;
        let bestScore = 0;
        
        // Find the best position that contains the most search terms
        searchTerms.forEach(term => {
            const termLower = term.toLowerCase();
            const pos = contentLower.indexOf(termLower);
            if (pos !== -1) {
                // Calculate a score based on how many terms are near this position
                let score = 0;
                searchTerms.forEach(otherTerm => {
                    const otherPos = contentLower.indexOf(otherTerm.toLowerCase(), Math.max(pos - 100, 0));
                    if (otherPos !== -1 && Math.abs(otherPos - pos) < 200) {
                        score += 1;
                    }
                });
                
                if (score > bestScore) {
                    bestScore = score;
                    bestPosition = pos;
                }
            }
        });
        
        // Extract context around the best position
        const startPos = Math.max(bestPosition - 100, 0);
        const endPos = Math.min(bestPosition + 200, content.length);
        
        let excerpt = content.substring(startPos, endPos).trim();
        
        // Add ellipsis if we're not at the beginning
        if (startPos > 0) {
            excerpt = "..." + excerpt;
        }
        
        // Add ellipsis if we're not at the end
        if (endPos < content.length) {
            excerpt = excerpt + "...";
        }
        
        // Ensure the excerpt isn't too long
        if (excerpt.length > 300) {
            excerpt = excerpt.substring(0, 297) + "...";
        }
        
        return excerpt;
    }
    
    function displayResults(results, query) {
        const terms = query.trim().split(/\s+/).filter(term => term.length > 0);
        
        const resultsHtml = results.map(result => {
            const highlightedTitle = highlightText(result.title, query);
            const dynamicExcerpt = generateDynamicExcerpt(result.content, terms);
            const highlightedExcerpt = highlightText(dynamicExcerpt, query);
            
            return `
                <div class="search-result-item">
                    <h3 class="search-result-title">
                        <a href="${result.url}">${highlightedTitle}</a>
                    </h3>
                    <div class="search-result-meta">
                        <span class="search-result-type">${result.type}</span>
                        ${result.date ? `<span class="search-result-date">${result.date}</span>` : ''}
                    </div>
                    <div class="search-result-excerpt">${highlightedExcerpt}</div>
                </div>
            `;
        }).join('');
        
        resultsContainer.innerHTML = resultsHtml;
    }
    
    function highlightText(text, query) {
        if (!query || !text) return text;
        
        // Split query into individual terms for better highlighting
        const terms = query.trim().split(/\s+/).filter(term => term.length > 0);
        
        let highlightedText = text;
        
        terms.forEach(term => {
            // Escape special regex characters
            const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const regex = new RegExp(`(${escapedTerm})`, 'gi');
            highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
        });
        
        return highlightedText;
    }
    
});
</script>

<style>
.search-result-item {
    margin-bottom: 2rem;
    padding: 1rem;
    border: 1px solid #57702f;
    border-radius: 4px;
    background: rgba(24, 44, 0, 0.1);
}

.search-result-title {
    margin: 0 0 0.5rem 0;
}

.search-result-title a {
    color: #a6e22e;
    text-decoration: none;
}

.search-result-title a:hover {
    text-decoration: underline;
}

.search-result-meta {
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    color: #8a9a5a;
}

.search-result-type {
    background: #57702f;
    color: #a6e22e;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    margin-right: 0.5rem;
}

.search-result-date {
    color: #8a9a5a;
}

.search-result-excerpt {
    color: #8a9a5a;
    line-height: 1.5;
}

mark {
    background: #8aa513;
    color: #1a2d00;
    padding: 0.1rem 0.2rem;
    border-radius: 2px;
}

#search-loading, #no-results {
    text-align: center;
    color: #8a9a5a;
    padding: 2rem;
}

#search-debug {
    font-family: monospace;
    font-size: 0.8rem;
    color: #ff0000;
}
</style> 