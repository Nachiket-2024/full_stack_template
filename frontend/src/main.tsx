// Import React (needed to use JSX/TSX)
import React from 'react';

// Import ReactDOM to render our app into the HTML <div id="root">
import ReactDOM from 'react-dom/client';

// Import Redux provider (to connect React with Redux store)
import { Provider } from 'react-redux';

// Import the root App component
import App from './App.tsx';

// Import tailwind CSS
import '../tailwind.css';

// Import Redux store
import { store } from './store/store.ts';

// Get the root HTML element with id="root" from index.html
const rootElement = document.getElementById('root') as HTMLElement;

// Create a React DOM root and render the App inside it
ReactDOM.createRoot(rootElement).render(
  // StrictMode helps catch potential problems in development
  <React.StrictMode>
    {/* Wrap the App with Provider so Redux store is available to all components */}
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
);
