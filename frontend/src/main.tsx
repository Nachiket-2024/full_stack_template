// ---------------------------- External Imports ----------------------------
// Import React core
import React from 'react';

// Import ReactDOM to render React components
import ReactDOM from 'react-dom/client';

// Import Redux Provider for global store access
import { Provider } from 'react-redux';

// Import ChakraProvider and defaultSystem from Chakra UI for theming/styling
import { ChakraProvider, defaultSystem } from '@chakra-ui/react';

// ---------------------------- Internal Imports ----------------------------
// Import the root App component
import App from './App.tsx';

// Import the Redux store
import { store } from './store/store.ts';

// ---------------------------- Render App ----------------------------
/**
 * Input:
 *   1. rootElement: HTML element with id 'root'
 *   2. App component
 *   3. Redux store
 *   4. ChakraProvider with defaultSystem for Chakra UI styling
 * Process:
 *   1. Get the root HTML element where the app will be mounted
 *   2. Create a ReactDOM root using ReactDOM.createRoot
 *   3. Render the App component wrapped in:
 *       a. React.StrictMode for development checks
 *       b. Redux Provider for store access
 *       c. ChakraProvider with defaultSystem for Chakra UI
 * Output:
 *   1. React application mounted in the DOM with Redux and Chakra UI
 */
const rootElement = document.getElementById('root') as HTMLElement; // Step 1

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    {/* Step 3b: Wrap with Redux Provider */}
    <Provider store={store}>
      {/* Step 3c: Wrap with ChakraProvider using defaultSystem */}
      <ChakraProvider value={defaultSystem}>
        {/* Step 3d: Render the root App component */}
        <App />
      </ChakraProvider>
    </Provider>
  </React.StrictMode>
);