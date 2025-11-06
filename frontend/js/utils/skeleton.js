// Loading Skeleton Generators

const SkeletonLoader = {
    /**
     * Create loading skeleton HTML
     * @param {string} type - Skeleton type (card, table, chart)
     * @returns {string} Skeleton HTML
     */
    create(type = 'card') {
        switch (type) {
            case 'card':
                return `
                    <div class="animate-pulse">
                        <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div class="h-8 bg-gray-200 rounded w-1/2"></div>
                    </div>
                `;
            case 'table':
                return `
                    <div class="animate-pulse space-y-2">
                        ${Array(5).fill(0).map(() => `
                            <div class="h-12 bg-gray-200 rounded"></div>
                        `).join('')}
                    </div>
                `;
            case 'chart':
                return `
                    <div class="animate-pulse flex items-center justify-center h-64">
                        <div class="w-48 h-48 bg-gray-200 rounded-full"></div>
                    </div>
                `;
            default:
                return `
                    <div class="animate-pulse">
                        <div class="h-4 bg-gray-200 rounded mb-2"></div>
                        <div class="h-4 bg-gray-200 rounded w-5/6"></div>
                    </div>
                `;
        }
    }
};

window.SkeletonLoader = SkeletonLoader;
