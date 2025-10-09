// ---------------------------- External Imports ----------------------------
// Import React library for JSX/TSX syntax
import React from 'react';

// Import ReactDOM to render React components into the DOM
import ReactDOM from 'react-dom/client';

// Import Redux Provider to connect React app with Redux store
import { Provider } from 'react-redux';

// ---------------------------- Internal Imports ----------------------------
// Import the root App component
import App from './App.tsx';

// Import Tailwind CSS for styling
import '../tailwind.css';

// Import the Redux store
import { store } from './store/store.ts';

// ---------------------------- Render App ----------------------------
/**
 * Input:
 *   1. rootElement: HTML element with id 'root'
 *   2. App component
 *   3. Redux store
 * Process:
 *   1. Get the root HTML element where the app will be mounted
 *   2. Create a React DOM root using ReactDOM.createRoot
 *   3. Render the App component wrapped in:
 *       a. React.StrictMode for development checks
 *       b. Redux Provider for store access
 * Output:
 *   1. React application mounted in the DOM
 */
const rootElement = document.getElementById('root') as HTMLElement; // Step 1: Get root HTML element

// Step 2: Create a React DOM root using ReactDOM.createRoot
ReactDOM.createRoot(rootElement).render(
  // Step 3: Render the application
  <React.StrictMode>
    {/* Step 3b: Wrap App with Redux Provider */}
    <Provider store={store}>
      {/* Step 3c: Render the root App component */}
      <App />
    </Provider>
  </React.StrictMode>
);
