---
name: zustand-state-management
description: Production-tested setup for Zustand state management in React applications with TypeScript. Use when setting up global state in React, migrating from Redux or Context API, implementing state persistence with localStorage, configuring TypeScript with Zustand, using slices pattern for modular stores, adding devtools middleware for debugging, handling Next.js SSR hydration, or encountering hydration errors, TypeScript inference issues, or persist middleware problems.
license: MIT
---

# Zustand State Management

**Version**: zustand@5.0.8+ | React 18+ | TypeScript 5+

## Quick Start

```bash
npm install zustand
```

```typescript
import { create } from 'zustand'

interface BearStore {
  bears: number
  increase: (by: number) => void
  reset: () => void
}

// CRITICAL: Notice double parentheses create<T>()() — required for TypeScript + middleware
const useBearStore = create<BearStore>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
  reset: () => set({ bears: 0 }),
}))

// Use in component — only re-renders when bears changes
function BearCounter() {
  const bears = useBearStore((state) => state.bears)
  return <h1>{bears} around here...</h1>
}
```

## The 5 Documented Issues (Prevent These)

### Issue #1: Next.js Hydration Mismatch
**Error**: `"Text content does not match server-rendered HTML"` or `"Hydration failed"`

```typescript
const useStore = create<StoreWithHydration>()(
  persist(
    (set) => ({
      count: 0,
      _hasHydrated: false,
      setHasHydrated: (hydrated) => set({ _hasHydrated: hydrated }),
    }),
    {
      name: 'my-store',
      onRehydrateStorage: () => (state) => { state?.setHasHydrated(true) },
    },
  ),
)

function MyComponent() {
  const hasHydrated = useStore((state) => state._hasHydrated)
  if (!hasHydrated) return <div>Loading...</div>
  return <ActualContent />
}
```

### Issue #2: TypeScript Double Parentheses Missing
```typescript
// ❌ WRONG — breaks middleware type inference
const useStore = create<MyStore>((set) => ({ ... }))

// ✅ CORRECT — always use double parentheses in TypeScript
const useStore = create<MyStore>()((set) => ({ ... }))
```

### Issue #3: Persist Middleware Import Error
```typescript
// ✅ Correct imports for v5
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
```

### Issue #4: Infinite Render Loop
```typescript
import { shallow } from 'zustand/shallow'

// ❌ WRONG — creates new object every render
const { bears, fishes } = useStore((state) => ({ bears: state.bears, fishes: state.fishes }))

// ✅ CORRECT Option 1 — select primitives separately
const bears = useStore((state) => state.bears)
const fishes = useStore((state) => state.fishes)

// ✅ CORRECT Option 2 — use shallow for multiple values
const { bears, fishes } = useStore(
  (state) => ({ bears: state.bears, fishes: state.fishes }),
  shallow,
)
```

### Issue #5: Slices Pattern Type Inference
```typescript
import { create, StateCreator } from 'zustand'

interface BearSlice { bears: number; addBear: () => void }
interface FishSlice { fishes: number; addFish: () => void }

const createBearSlice: StateCreator<BearSlice & FishSlice, [], [], BearSlice> = (set) => ({
  bears: 0,
  addBear: () => set((state) => ({ bears: state.bears + 1 })),
})

const createFishSlice: StateCreator<BearSlice & FishSlice, [], [], FishSlice> = (set) => ({
  fishes: 0,
  addFish: () => set((state) => ({ fishes: state.fishes + 1 })),
})

const useStore = create<BearSlice & FishSlice>()((...a) => ({
  ...createBearSlice(...a),
  ...createFishSlice(...a),
}))
```

## Persist Middleware (localStorage)

```typescript
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  language: string
  setTheme: (theme: UserPreferences['theme']) => void
}

const usePreferencesStore = create<UserPreferences>()(
  persist(
    (set) => ({
      theme: 'system',
      language: 'en',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'user-preferences',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ theme: state.theme, language: state.language }),
    },
  ),
)
```

## Devtools Middleware (Redux DevTools)

```typescript
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

const useStore = create<CounterStore>()(
  devtools(
    (set) => ({
      count: 0,
      increment: () => set(
        (state) => ({ count: state.count + 1 }),
        undefined,
        'counter/increment',  // action name shown in DevTools
      ),
    }),
    { name: 'CounterStore' },
  ),
)
```

## Combining Middlewares

```typescript
// devtools wraps persist — shows persist actions in DevTools
const useStore = create<MyStore>()(
  devtools(
    persist(
      (set) => ({ /* store definition */ }),
      { name: 'my-storage' },
    ),
    { name: 'MyStore' },
  ),
)
```

## Common Patterns

```typescript
// Async actions with loading state
const useAsyncStore = create<AsyncStore>()((set) => ({
  data: null, isLoading: false, error: null,
  fetchData: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch('/api/data')
      set({ data: await response.json(), isLoading: false })
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
    }
  },
}))

// Resettable store
const initialState = { count: 0, name: '' }
const useStore = create<ResettableStore>()((set) => ({
  ...initialState,
  increment: () => set((state) => ({ count: state.count + 1 })),
  reset: () => set(initialState),
}))
```

## Rules

✅ Always use `create<T>()()` double parentheses in TypeScript  
✅ Use selector functions: `useStore(state => state.bears)` — not `useStore().bears`  
✅ Use `shallow` when selecting multiple values as object  
✅ Use unique storage names for persist middleware  
✅ Handle Next.js hydration with `_hasHydrated` flag pattern  
✅ Use `set` with updater functions for derived state: `set(state => ({ count: state.count + 1 }))`  

❌ Never mutate state directly  
❌ Never create new objects in selectors without `shallow`  
❌ Never use same storage name for multiple stores  
❌ Never use Zustand for server state — use TanStack Query instead  
