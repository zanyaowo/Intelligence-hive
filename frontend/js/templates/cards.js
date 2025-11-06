// Card Template Generators

const CardTemplates = {
    /**
     * Create statistic card
     * @param {string} title - Card title
     * @param {string|number} value - Display value
     * @param {string} color - Color theme (blue, red, orange, green, purple)
     * @param {string} clickHandler - Optional click handler (Alpine.js @click expression)
     * @returns {string} Card HTML
     */
    statCard(title, value, color, clickHandler = null) {
        const colors = {
            blue: 'border-blue-500',
            red: 'border-red-500',
            orange: 'border-orange-500',
            green: 'border-green-500',
            purple: 'border-purple-500',
            cyan: 'border-cyan-500',
            yellow: 'border-yellow-500',
            indigo: 'border-indigo-500',
            pink: 'border-pink-500'
        };

        const clickableClass = clickHandler ? 'cursor-pointer hover:bg-gray-700 transition-colors' : '';
        const clickAttr = clickHandler ? `@click="${clickHandler}"` : '';

        return `
            <div class="bg-gray-800 rounded-lg shadow p-6 border-l-4 ${colors[color] || colors.blue} ${clickableClass}" ${clickAttr}>
                <p class="text-sm text-gray-300 mb-1">${title}</p>
                <p class="text-3xl font-bold text-white">${value}</p>
                ${clickHandler ? '<p class="text-xs text-gray-400 mt-2">點擊查看詳情 →</p>' : ''}
            </div>
        `;
    },

    /**
     * Create info row for detail views
     * @param {string} label - Label text
     * @param {string} value - Value text
     * @param {boolean} fullWidth - Whether to span full width
     * @returns {string} Info row HTML
     */
    infoRow(label, value, fullWidth = false) {
        return `
            <div class="${fullWidth ? 'md:col-span-2' : ''}">
                <div class="text-sm text-gray-600">${label}</div>
                <div class="text-gray-900 font-medium mt-1 ${fullWidth ? 'truncate' : ''}">${value || '-'}</div>
            </div>
        `;
    }
};

window.CardTemplates = CardTemplates;
