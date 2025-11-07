// Clipboard Utility Functions

const ClipboardUtils = {
    /**
     * Copy data to clipboard
     * @param {*} data - Data to copy (array or object)
     * @returns {Promise<boolean>} Success status
     */
    async copy(data) {
        try {
            const text = Array.isArray(data) ? data.join('\n') : JSON.stringify(data, null, 2);
            await navigator.clipboard.writeText(text);
            window.AppStore.showSuccess('已成功複製到剪貼板');
            return true;
        } catch (err) {
            console.error('Copy failed:', err);
            window.AppStore.showError('複製失敗，請重試');
            return false;
        }
    }
};

window.ClipboardUtils = ClipboardUtils;
