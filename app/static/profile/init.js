import { initNavigation } from './navigation.js';
import { initMenu } from './menu.js';
import { initHistory } from './history.js';

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initMenu();
    initHistory();
});