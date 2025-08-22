// Import configureStore from Redux Toolkit
import { configureStore, createSlice } from '@reduxjs/toolkit'
// Import PayloadAction as type-only (fixes TypeScript verbatimModuleSyntax error)
import type { PayloadAction } from '@reduxjs/toolkit'

// Define the type for the counter state
type CounterState = { value: number }

// Initial state
const initialState: CounterState = { value: 0 }

// Create a slice for the counter
const counterSlice = createSlice({
    name: 'counter',
    initialState,
    reducers: {
        increment: (state) => {
            state.value += 1
        },
        decrement: (state) => {
            state.value -= 1
        },
        reset: (state) => {
            state.value = 0
        },
        setValue: (state, action: PayloadAction<number>) => {
            state.value = action.payload
        },
    },
})

// Export actions for use in components
export const { increment, decrement, reset, setValue } = counterSlice.actions

// Create Redux store with the counter slice
export const store = configureStore({
    reducer: {
        counter: counterSlice.reducer,
    },
})

// Infer RootState and AppDispatch types from the store
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
