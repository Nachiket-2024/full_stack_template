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
// Get the root HTML element where the React app will be mounted
const rootElement = document.getElementById('root') as HTMLElement;

// Create a React DOM root and render the App inside it
ReactDOM.createRoot(rootElement).render(
  // Wrap in StrictMode to catch potential problems during development
  <React.StrictMode>
    {/* Wrap the App with Provider so Redux store is accessible to all components */}
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
);
